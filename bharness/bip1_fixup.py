# SPDX-License-Identifier: MIT
"""BIP 1 prop-packet fixup (blender-team; buffffff 49985 buf-bip1-props-reexport-20261019, after unreal-epic-boss survey 49855).
A deterministic post-process pass over the BIP 1 *prop* library packets (Daedalus2 tools/islands/blenderboss/bip_split.py output).
Terrain packets are never read for writing and never touched. Numpy only; no Blender needed (bip1_readback.py re-reads in Blender).
What it does, packet by packet, driven by one versioned JSON (bharness/data/bip1_fixup_map.v<N>.json, built once by `map`):
  1 materials  every source material is fingerprinted by value (colour, roughness, metal, emissive, alpha, sidedness) and mapped to
               one shared M_BB_* material; colours are merged only within the map's ΔE76 radius of a kept centre (greedy cover by
               usage), so no colour moves visibly. Shared names reuse the imported terrain set (M_BB_Grass, ...) when the value
               matches; the rest are M_BB_<Family>_<NN> after the nearest bharness.palette colour. No .NNN, # or invalid characters.
  2 names      mesh/node names are made UE-safe ([A-Za-z0-9_], 'Cube.001' -> 'Cube_001') and unique across the whole prop library.
  3 collision  authored UCX_<Mesh>_<NN> children (rule 49583: authored, no auto hulls): the mesh's connected parts are each fitted
               with the smaller of an axis box or a PCA box, tiny bits dropped, then the closest pieces merged until at most
               max_pieces convex boxes remain. Rules (in the JSON) skip walk-through decor and list creatures / crew mobs for a
               physics asset instead of guessing UCX.
CLI:
  python -m bharness.bip1_fixup map   --packets <dir> [--terrain <dir>] --out bharness/data/bip1_fixup_map.v1.json
  python -m bharness.bip1_fixup apply --manifest flagship.bip.json --packets <dir> --map <map.json> --archive <dir>
      R1 prop packets are moved (never deleted) into --archive first and re-read from there, so a re-run is byte-identical."""
import argparse, colorsys, hashlib, json, os, re, shutil, struct, sys
import numpy as np

SCHEMA = "bb-bip1-fixup-map/1"
_CT = {5121: np.uint8, 5123: np.uint16, 5125: np.uint32, 5126: np.float32}
_NC = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4}
SAFE = re.compile(r"^[A-Za-z0-9_]+$")
DEFAULT_RULES = {
    "max_pieces": 8, "min_piece_m": 0.05, "min_thickness_m": 0.02, "weld_m": 1e-4,
    "skip": [
        {"why": "physics_asset", "match": r"^Mob_", "note": "creature / crew-mob body parts: use a physics asset, not UCX"},
        {"why": "decor", "match": r"^Prop_(Herb|Bloom)_", "note": "walk-through plants"},
        {"why": "decor", "match": r"^Prop_Tree_.*_Top", "note": "tree canopy: the trunk mesh blocks"},
        {"why": "decor", "max_extent_below_m": 0.3, "note": "tiny decor"}]}


# ---------- glb io ----------
def read_glb(path):
    d = open(path, "rb").read()
    if d[:4] != b"glTF" or struct.unpack("<I", d[4:8])[0] != 2 or struct.unpack("<I", d[8:12])[0] != len(d):
        raise ValueError("not a glb 2.0: " + path)
    n, k = struct.unpack("<II", d[12:20]); g = json.loads(d[20:20 + n]); o = 20 + n; b = b""
    if o + 8 <= len(d):
        bl, bk = struct.unpack("<II", d[o:o + 8]); b = d[o + 8:o + 8 + bl]
    return g, b


def pack_glb(g, b):
    js = json.dumps(g, separators=(",", ":")).encode("utf-8"); js += b" " * ((4 - len(js) % 4) % 4); b += b"\0" * ((4 - len(b) % 4) % 4)
    return struct.pack("<4sII", b"glTF", 2, 28 + len(js) + len(b)) + struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(b), 0x004E4942) + b


def accessor(g, b, i):
    a = g["accessors"][i]; bv = g["bufferViews"][a["bufferView"]]; dt = np.dtype(_CT[a["componentType"]]).newbyteorder("<"); nc = _NC[a["type"]]
    arr = np.frombuffer(b, dtype=dt, count=a["count"] * nc, offset=bv.get("byteOffset", 0) + a.get("byteOffset", 0))
    return arr.reshape(a["count"], nc) if nc > 1 else arr


def sha(b):
    return hashlib.sha256(b).hexdigest()


# ---------- materials ----------
def fingerprint(m):
    p = m.get("pbrMetallicRoughness", {})
    v = {"base": [round(float(x), 5) for x in p.get("baseColorFactor", [1, 1, 1, 1])], "rough": round(float(p.get("roughnessFactor", 1)), 4),
         "metal": round(float(p.get("metallicFactor", 1)), 4), "emissive": [round(float(x), 4) for x in m.get("emissiveFactor", [0, 0, 0])],
         "emissive_strength": round(float(m.get("extensions", {}).get("KHR_materials_emissive_strength", {}).get("emissiveStrength", 1.0)), 4),
         "alpha": m.get("alphaMode", "OPAQUE"), "double": bool(m.get("doubleSided", False))}
    return json.dumps(v, sort_keys=True, separators=(",", ":")), v


def lab(rgb):
    x = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]]) @ np.asarray(rgb, float) / np.array([0.9505, 1.0, 1.089])
    f = np.where(x > 0.008856, np.cbrt(np.maximum(x, 0)), 7.787 * x + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def lin_to_hex(c):
    s = [(x * 12.92 if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055) for x in c[:3]]
    return "%02X%02X%02X" % tuple(int(round(255 * min(1, max(0, v)))) for v in s)


def hex_to_lin(h):
    s = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in s]


def _palette():
    try:
        from bharness import palette as P
    except ImportError:
        import palette as P
    return {k: lab(hex_to_lin(v)) for k, v in sorted(P.PALETTE.items())}


def family(rgb, pal):
    L = lab(rgb); k = min(pal, key=lambda n: (float(np.linalg.norm(pal[n] - L)), n))
    return "".join(w.capitalize() for w in k.split("_"))


def build_map(packet_files, terrain_files=(), radius=8.0, rules=None, version=1):
    """-> map dict. Deterministic in the packet contents (files are read in sorted order)."""
    use, names, val = {}, {}, {}
    for f in sorted(packet_files):
        g, _ = read_glb(f); fps = [fingerprint(m) for m in g.get("materials", [])]
        for i, (fp, v) in enumerate(fps):
            val[fp] = v; names.setdefault(fp, set()).add(g["materials"][i].get("name", ""))
        for me in g["meshes"]:
            for pr in me["primitives"]:
                if pr.get("material") is not None:
                    use[fps[pr["material"]][0]] = use.get(fps[pr["material"]][0], 0) + 1
    terrain = {}
    for f in sorted(terrain_files):
        g, _ = read_glb(f)
        for m in g.get("materials", []):
            fp, v = fingerprint(m); terrain.setdefault(m["name"], v)
    pal = _palette(); groups = {}
    for fp, v in val.items():
        cls = json.dumps({k: v[k] for k in v if k != "base"} | {"a": v["base"][3]}, sort_keys=True)
        groups.setdefault(cls, []).append(fp)
    centres, assign = [], {}
    for cls in sorted(groups):
        fps = sorted(groups[cls]); L = {fp: lab(val[fp]["base"][:3]) for fp in fps}; left = set(fps)
        while left:
            best = max(fps, key=lambda c: (sum(use.get(x, 0) + 1 for x in left if np.linalg.norm(L[x] - L[c]) <= radius), use.get(c, 0), c))
            cov = sorted(x for x in left if np.linalg.norm(L[x] - L[best]) <= radius)
            centres.append(best)
            for x in cov:
                assign[x] = best; left.discard(x)
    shared, fam_n, taken = {}, {}, set()
    for c in sorted(centres, key=lambda c: (-sum(use.get(x, 0) for x in assign if assign[x] == c), c)):
        v = val[c]; nm = None
        for tn, tv in sorted(terrain.items()):
            if tv["rough"] == v["rough"] and tv["emissive"] == v["emissive"] == [0, 0, 0] and tv["alpha"] == v["alpha"] and np.linalg.norm(lab(tv["base"][:3]) - lab(v["base"][:3])) <= 2.0 and tn not in taken:
                nm = tn; break
        if nm is None:
            fam = ("Glow" if any(v["emissive"]) else "") + ("Glass" if v["alpha"] == "BLEND" else "") + family(v["base"][:3], pal)
            fam_n[fam] = fam_n.get(fam, 0) + 1; nm = "M_BB_%s_%02d" % (fam, fam_n[fam])
        taken.add(nm); shared[c] = nm
    mats = []
    for c in sorted(shared, key=lambda c: shared[c]):
        v = val[c]
        mats.append({"name": shared[c], "hex": lin_to_hex(v["base"]), "value": v, "uses": sum(use.get(x, 0) for x in assign if assign[x] == c),
                     "merged_values": sum(1 for x in assign if assign[x] == c),
                     "max_delta_e": round(max(float(np.linalg.norm(lab(val[x]["base"][:3]) - lab(v["base"][:3]))) for x in assign if assign[x] == c), 3)})
    table = [{"fingerprint": fp, "to": shared[assign[fp]], "source_names": sorted(names[fp]), "uses": use.get(fp, 0)} for fp in sorted(val)]
    return {"schema": SCHEMA, "version": version, "radius_delta_e76": radius, "rules": rules or DEFAULT_RULES,
            "source": {"packets": len(packet_files), "material_names": len(set().union(*names.values())) if names else 0, "material_values": len(val)},
            "materials": mats, "map": table}


def _material_def(entry):
    v = entry["value"]
    m = {"name": entry["name"], "doubleSided": v["double"], "pbrMetallicRoughness": {"baseColorFactor": v["base"], "metallicFactor": v["metal"], "roughnessFactor": v["rough"]}}
    if any(v["emissive"]):
        m["emissiveFactor"] = v["emissive"]
        if v["emissive_strength"] != 1.0:
            m["extensions"] = {"KHR_materials_emissive_strength": {"emissiveStrength": v["emissive_strength"]}}
    if v["alpha"] != "OPAQUE":
        m["alphaMode"] = v["alpha"]
    return m


# ---------- names ----------
def safe_name(n):
    s = re.sub(r"[^A-Za-z0-9_]", "_", n)
    return s if s and not s[0].isdigit() else "M_" + s


def rename_table(all_names):
    """source names (list, library order) -> unique UE-safe names. Names already safe keep priority."""
    out, used = {}, set()
    for n in all_names:
        if SAFE.match(n):
            out[n] = n; used.add(n)
    for n in all_names:
        if n in out:
            continue
        s = safe_name(n); t, i = s, 1
        while t in used:
            t = "%s_%d" % (s, i); i += 1
        out[n] = t; used.add(t)
    return out


# ---------- collision ----------
def skip_reason(name, extent, rules):
    for r in rules["skip"]:
        if "match" in r and re.search(r["match"], name):
            return r["why"]
        if "max_extent_below_m" in r and float(max(extent)) < r["max_extent_below_m"]:
            return r["why"]
    return None


def components(pos, tris, weld):
    key = np.round(pos / weld).astype(np.int64); _, vid = np.unique(key, axis=0, return_inverse=True); vid = vid.reshape(-1)
    parent = np.arange(vid.max() + 1)

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for t in tris:
        a, b, c = find(vid[t[0]]), find(vid[t[1]]), find(vid[t[2]])
        r = min(a, b, c); parent[a] = parent[b] = parent[c] = r
    roots = np.array([find(v) for v in vid]); groups = {}
    for t in tris:
        groups.setdefault(int(roots[t[0]]), set()).update(int(i) for i in t)
    return [pos[sorted(v)] for _, v in sorted(groups.items())]


def fit_box(pts, min_t):
    """smaller of the axis box and the PCA box -> (centre, axes 3x3 rows, half sizes)."""
    lo, hi = pts.min(0), pts.max(0); best = ((lo + hi) / 2, np.eye(3), np.maximum((hi - lo) / 2, min_t / 2))
    if len(pts) >= 4:
        c = pts.mean(0); w, V = np.linalg.eigh(np.cov((pts - c).T)); R = V.T[::-1]
        R = np.where(np.abs(R) < 1e-12, 0, R)
        R = np.array([r * (1 if r[np.argmax(np.abs(r))] > 0 else -1) for r in R]); R[2] = np.cross(R[0], R[1])
        q = (pts - c) @ R.T; ql, qh = q.min(0), q.max(0); h = np.maximum((qh - ql) / 2, min_t / 2)
        if np.prod(h) < np.prod(best[2]) * 0.9:
            best = (c + ((ql + qh) / 2) @ R, R, h)
    return best


def box_corners(b):
    c, R, h = b
    return np.array([c + (sx * h[0]) * R[0] + (sy * h[1]) * R[1] + (sz * h[2]) * R[2] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)])


def ucx_boxes(pos, tris, rules):
    comps = components(pos, tris, rules["weld_m"]); mt = rules["min_thickness_m"]
    pieces = [(p, fit_box(p, mt)) for p in comps]
    big = [x for x in pieces if float(np.max(x[0].max(0) - x[0].min(0))) >= rules["min_piece_m"]] or pieces
    big = [(p, b, float(np.prod(b[2]))) for p, b in big]
    while len(big) > rules["max_pieces"]:
        best = None
        for i in range(len(big)):
            for j in range(i + 1, len(big)):
                lo = np.minimum(big[i][0].min(0), big[j][0].min(0)); hi = np.maximum(big[i][0].max(0), big[j][0].max(0))
                cost = float(np.prod(np.maximum(hi - lo, mt))) / 8 - big[i][2] - big[j][2]
                if best is None or cost < best[0]:
                    best = (cost, i, j)
        _, i, j = best; p = np.vstack([big[i][0], big[j][0]]); b = fit_box(p, mt)
        big = [x for k, x in enumerate(big) if k not in (i, j)] + [(p, b, float(np.prod(b[2])))]
    return [b for _, b, _ in sorted(big, key=lambda x: tuple(np.round(x[1][0], 6)))]


BOX_TRIS = np.array([[0, 1, 3], [0, 3, 2], [4, 6, 7], [4, 7, 5], [0, 4, 5], [0, 5, 1], [2, 3, 7], [2, 7, 6], [0, 2, 6], [0, 6, 4], [1, 5, 7], [1, 7, 3]], np.uint16)


def _fix_winding(v, t):
    c = v.mean(0); out = []
    for a, b, d in t:
        n = np.cross(v[b] - v[a], v[d] - v[a])
        out.append((a, b, d) if np.dot(n, v[a] - c) > 0 else (a, d, b))
    return np.array(out, np.uint16)


# ---------- packet pass ----------
def fix_packet(raw, fmap, rules, renames):
    """R1 packet bytes -> (R2 packet bytes, stats). Pure function of its inputs."""
    g, b = read_glb_bytes(raw)
    to = {e["fingerprint"]: e["to"] for e in fmap["map"]}; defs = {e["name"]: e for e in fmap["materials"]}
    src = [fingerprint(m)[0] for m in g.get("materials", [])]; order = []
    for me in g["meshes"]:
        for pr in me["primitives"]:
            if pr.get("material") is not None:
                n = to[src[pr["material"]]]
                if n not in order:
                    order.append(n)
    ix = {n: i for i, n in enumerate(order)}
    for me in g["meshes"]:
        for pr in me["primitives"]:
            if pr.get("material") is not None:
                pr["material"] = ix[to[src[pr["material"]]]]
    g["materials"] = [_material_def(defs[n]) for n in order]
    if not any("extensions" in m for m in g["materials"]):
        g.pop("extensionsUsed", None)
    else:
        g["extensionsUsed"] = ["KHR_materials_emissive_strength"]
    chunks = [b + b"\0" * ((4 - len(b) % 4) % 4)]; blen = len(chunks[0])

    def view(arr, target):
        nonlocal blen
        raw_ = arr.tobytes(); pad = (4 - blen % 4) % 4
        if pad:
            chunks.append(b"\0" * pad); blen += pad
        g["bufferViews"].append({"buffer": 0, "byteOffset": blen, "byteLength": len(raw_), "target": target}); chunks.append(raw_); blen += len(raw_)
        return len(g["bufferViews"]) - 1
    stats = {"ucx": 0, "meshes": 0, "with_ucx": 0, "skipped": {}, "renamed": 0}
    render = list(range(len(g["nodes"])))
    for ni in render:
        nd = g["nodes"][ni]; old = nd["name"]; new = renames[old]; stats["renamed"] += old != new
        nd["name"] = new; g["meshes"][nd["mesh"]]["name"] = new; stats["meshes"] += 1
        prims = g["meshes"][nd["mesh"]]["primitives"]; P, T, off = [], [], 0
        for pr in prims:
            p = accessor(g, b, pr["attributes"]["POSITION"]).astype(np.float64); t = accessor(g, b, pr["indices"]).reshape(-1, 3).astype(np.int64)
            P.append(p); T.append(t + off); off += len(p)
        pos = np.vstack(P); tris = np.vstack(T); why = skip_reason(new, pos.max(0) - pos.min(0), rules)
        if why:
            stats["skipped"].setdefault(why, []).append(new); continue
        kids = []
        for k, bx in enumerate(ucx_boxes(pos, tris, rules)):
            v = box_corners(bx).astype("<f4"); t = _fix_winding(v.astype(np.float64), BOX_TRIS)
            a0 = {"bufferView": view(np.ascontiguousarray(v), 34962), "componentType": 5126, "count": 8, "type": "VEC3",
                  "min": [float(x) for x in v.min(0)], "max": [float(x) for x in v.max(0)]}
            g["accessors"].append(a0); pa = len(g["accessors"]) - 1
            g["accessors"].append({"bufferView": view(np.ascontiguousarray(t.reshape(-1), "<u2"), 34963), "componentType": 5123, "count": 36, "type": "SCALAR"}); ia = len(g["accessors"]) - 1
            nm = "UCX_%s_%02d" % (new, k)
            g["meshes"].append({"name": nm, "primitives": [{"attributes": {"POSITION": pa}, "indices": ia, "mode": 4}]})
            g["nodes"].append({"name": nm, "mesh": len(g["meshes"]) - 1}); kids.append(len(g["nodes"]) - 1)
        nd["children"] = kids; stats["ucx"] += len(kids); stats["with_ucx"] += 1
    g["buffers"] = [{"byteLength": blen}]
    ex = g.setdefault("extras", {}); ex["bip1_fixup"] = {"map_schema": fmap["schema"], "map_version": fmap["version"], "ucx": stats["ucx"]}
    stats["materials"] = len(g["materials"])
    return pack_glb(g, b"".join(chunks)), stats


def read_glb_bytes(d):
    n, _ = struct.unpack("<II", d[12:20]); g = json.loads(d[20:20 + n]); o = 20 + n; b = b""
    if o + 8 <= len(d):
        bl, _ = struct.unpack("<II", d[o:o + 8]); b = d[o + 8:o + 8 + bl]
    return g, b


def apply(manifest_path, pdir, map_path, archive):
    M = json.load(open(manifest_path, encoding="utf-8")); fmap = json.load(open(map_path, encoding="utf-8")); rules = fmap["rules"]
    props = [p for p in M["packets"] if p["kind"] == "props"]; fx = M.get("props_fixup")
    r1 = fx["r1"] if fx else {p["file"]: p["sha256"] for p in props}
    os.makedirs(archive, exist_ok=True); src = {}
    for p in props:                                   # archive R1 (move, never delete), then always read R1 from the archive
        a = os.path.join(archive, p["file"]); live = os.path.join(pdir, p["file"])
        if not os.path.exists(a):
            if sha(open(live, "rb").read()) != r1[p["file"]]:
                raise SystemExit("refusing: %s is neither archived nor the R1 sha" % p["file"])
            shutil.move(live, a)
        d = open(a, "rb").read()
        if sha(d) != r1[p["file"]]:
            raise SystemExit("refusing: archived %s does not match its R1 sha" % p["file"])
        src[p["file"]] = d
    lib = [nd["name"] for p in props for nd in read_glb_bytes(src[p["file"]])[0]["nodes"]]
    if len(lib) != len(set(lib)):
        raise SystemExit("source node names are not unique")
    ren = rename_table(lib); outstats = {}
    if len(set(ren.values())) != len(lib):
        raise SystemExit("renamed library names are not unique")
    for p in props:
        out, st = fix_packet(src[p["file"]], fmap, rules, ren); tmp = os.path.join(pdir, p["file"] + ".tmp")
        open(tmp, "wb").write(out); os.replace(tmp, os.path.join(pdir, p["file"]))
        p.update(sha256=sha(out), bytes=len(out), materials=st["materials"], ucx=st["ucx"], revision="R2"); outstats[p["file"]] = st
    skip = {}
    for st in outstats.values():
        for k, v in st["skipped"].items():
            skip.setdefault(k, []).extend(v)
    skipped = {n: k for k, v in skip.items() for n in v}
    ucx_of = {}
    for p in props:
        g, _ = read_glb(os.path.join(pdir, p["file"]))
        for nd in g["nodes"]:
            if not nd["name"].startswith("UCX_"):
                ucx_of[nd["name"]] = len(nd.get("children", []))
    for pr in M["props"]:
        pr.setdefault("src_mesh_name", pr["name"]); old = pr["name"] if pr["name"] in ren else pr["src_mesh_name"]
        pr["name"] = ren[old]; pr["ucx"] = ucx_of[pr["name"]]; pr["collision"] = "UCX" if pr["ucx"] else "none:" + skipped[pr["name"]]
    for pl in M["placements"]:
        pl["prop"] = ren.get(pl["prop"], pl["prop"])
    t = M["totals"]; t["bytes"] = sum(p["bytes"] for p in M["packets"]); t["max_packet_bytes"] = max(p["bytes"] for p in M["packets"])
    shared = sorted({m["name"] for p in props for m in read_glb(os.path.join(pdir, p["file"]))[0]["materials"]})
    t["prop_ucx"] = sum(st["ucx"] for st in outstats.values()); t["prop_materials_shared"] = len(shared)
    M["manifest_version"] = max(2, M.get("manifest_version", 1) + (0 if fx else 1))
    M["props_fixup"] = {"tool": "blender-harness bharness/bip1_fixup.py", "map": os.path.basename(map_path), "map_version": fmap["version"],
                        "map_sha256": sha(open(map_path, "rb").read()), "archive": "art/packets/flagship_archive/props_r1 (bot-team)", "r1": r1,
                        "ucx": t["prop_ucx"], "materials_shared": shared, "skipped_collision": {k: sorted(v) for k, v in sorted(skip.items())},
                        "renamed": {k: v for k, v in sorted(ren.items()) if k != v}, "request": "buffffff 49985 buf-bip1-props-reexport-20261019"}
    s = json.dumps(M, indent=1) + "\n"; open(manifest_path, "w", encoding="utf-8", newline="\n").write(s)
    return M


def main(argv=None):
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="cmd", required=True)
    a = sp.add_parser("map"); a.add_argument("--packets", required=True); a.add_argument("--terrain"); a.add_argument("--out", required=True)
    a.add_argument("--radius", type=float, default=8.0); a.add_argument("--version", type=int, default=1)
    b = sp.add_parser("apply"); b.add_argument("--manifest", required=True); b.add_argument("--packets", required=True); b.add_argument("--map", required=True); b.add_argument("--archive", required=True)
    o = ap.parse_args(argv)
    if o.cmd == "map":
        pf = [os.path.join(o.packets, f) for f in os.listdir(o.packets) if re.match(r"flagship_props_\d+\.glb$", f)]
        tf = [os.path.join(o.terrain, f) for f in os.listdir(o.terrain) if re.match(r"flagship_terrain_\w+\.glb$", f)] if o.terrain else []
        m = build_map(pf, tf, o.radius, version=o.version); open(o.out, "w", encoding="utf-8", newline="\n").write(json.dumps(m, indent=1) + "\n")
        print(json.dumps({"material_names": m["source"]["material_names"], "values": m["source"]["material_values"], "shared": len(m["materials"]),
                          "max_delta_e": max(x["max_delta_e"] for x in m["materials"])}))
    else:
        M = apply(o.manifest, o.packets, o.map, o.archive); t = M["totals"]
        print(json.dumps({"prop_packets": sum(1 for p in M["packets"] if p["kind"] == "props"), "ucx": t["prop_ucx"], "materials": t["prop_materials_shared"],
                          "skipped": {k: len(v) for k, v in M["props_fixup"]["skipped_collision"].items()}}))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    main()
