# SPDX-License-Identifier: MIT
"""Tests for bharness.bip1_fixup (BIP 1 prop re-export, buffffff 49985). Synthetic packets, no Blender. Prints ok/FAIL lines and n/m."""
import json, os, shutil, sys, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
from bharness import bip1_fixup as F

R = []


def t(name, cond, info=""):
    R.append(bool(cond)); print(("ok   " if cond else "FAIL ") + name + ("" if cond else "  " + str(info)))


def mat(name, rgb, rough=0.6, em=None, alpha=None):
    m = {"doubleSided": True, "name": name, "pbrMetallicRoughness": {"baseColorFactor": list(rgb) + [1], "metallicFactor": 0, "roughnessFactor": rough}}
    if em:
        m["emissiveFactor"] = em; m["extensions"] = {"KHR_materials_emissive_strength": {"emissiveStrength": 2.0}}
    if alpha:
        m["alphaMode"] = alpha
    return m


def cube(c, h):
    v = np.array([[c[0] + sx * h[0], c[1] + sy * h[1], c[2] + sz * h[2]] for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)], "<f4")
    return v, F.BOX_TRIS.astype("<u2")


def packet(meshes, mats):
    """meshes: [(name, [(verts, idx, mat_ix), ...])] -> glb bytes shaped like bip_split's library packets."""
    g = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": []}], "nodes": [], "meshes": [], "materials": mats, "accessors": [], "bufferViews": [],
         "buffers": [], "extras": {"bip": 1}}
    bin_ = bytearray()

    def view(a, tgt):
        while len(bin_) % 4:
            bin_.append(0)
        g["bufferViews"].append({"buffer": 0, "byteOffset": len(bin_), "byteLength": a.nbytes, "target": tgt}); bin_.extend(a.tobytes()); return len(g["bufferViews"]) - 1
    for name, prims in meshes:
        ps = []
        for v, i, mi in prims:
            g["accessors"].append({"bufferView": view(v, 34962), "componentType": 5126, "count": len(v), "type": "VEC3", "min": v.min(0).tolist(), "max": v.max(0).tolist()})
            g["accessors"].append({"bufferView": view(i.reshape(-1), 34963), "componentType": 5123, "count": i.size, "type": "SCALAR"})
            ps.append({"attributes": {"POSITION": len(g["accessors"]) - 2}, "indices": len(g["accessors"]) - 1, "material": mi, "mode": 4})
        g["meshes"].append({"name": name, "primitives": ps}); g["nodes"].append({"name": name, "mesh": len(g["meshes"]) - 1}); g["scenes"][0]["nodes"].append(len(g["nodes"]) - 1)
    g["buffers"] = [{"byteLength": len(bin_)}]
    return F.pack_glb(g, bytes(bin_))


def two_cubes(name, mi=0, gap=2.0, size=0.5):
    a, i = cube((0, size, 0), (size, size, size)); b, _ = cube((gap, size, 0), (size, size, size))
    return (name, [(np.vstack([a, b]), np.vstack([i, i + 8]).astype("<u2"), mi)])


MATS0 = [mat("BUF_D_#8A5A32", (0.25, 0.11, 0.03)), mat("BUF_D_#8A5A32.001", (0.25, 0.11, 0.03)), mat("Bld_Mill_M0", (0.252, 0.112, 0.031)),
         mat("Glow", (1, 1, 1), em=[1, 0.5, 0.1]), mat("Far", (0.05, 0.4, 0.9))]
P0 = packet([two_cubes("Cube.001", 0), two_cubes("Bld_Mill", 1), two_cubes("Mob_Crew_Smith_ArmL", 2), two_cubes("Prop_Herb_Aloe", 3, 0.2, 0.1),
             two_cubes("Cube_001", 4), ("Prop_Pebble", [cube((0, 0.05, 0), (0.05, 0.05, 0.05)) + (0,)])], MATS0)
P1 = packet([two_cubes("Prop_BBIsle_Crate_00", 1, 0.0, 0.5), ("Prop_Many", [(np.vstack([cube((3 * k, 0.5, 0), (0.5, 0.5, 0.5))[0] for k in range(12)]),
                                                                              np.vstack([F.BOX_TRIS + 8 * k for k in range(12)]).astype("<u2"), 0)])], MATS0[:2])


def setup(td):
    pk = os.path.join(td, "pk"); os.makedirs(pk)
    files = {"flagship_props_000.glb": P0, "flagship_props_001.glb": P1, "flagship_terrain_00.glb": packet([two_cubes("X_Terrain", 0)], [mat("M_BB_Grass", (0.2, 0.5, 0.12), 0.9)])}
    for f, d in files.items():
        open(os.path.join(pk, f), "wb").write(d)
    pk_rows = [{"id": f[:-4], "file": f, "kind": "terrain" if "terrain" in f else "props", "sha256": F.sha(d), "bytes": len(d), "materials": len(F.read_glb_bytes(d)[0]["materials"])} for f, d in sorted(files.items())]
    props = [{"name": nd["name"], "src_mesh_name": nd["name"], "packet": f[:-4]} for f in ("flagship_props_000.glb", "flagship_props_001.glb") for nd in F.read_glb_bytes(files[f])[0]["nodes"]]
    M = {"bip": 1, "packets": pk_rows, "props": props, "placements": [{"node": p["name"] + ".001", "prop": p["name"], "packet": p["packet"]} for p in props], "totals": {}}
    mj = os.path.join(td, "m.json"); json.dump(M, open(mj, "w")); return pk, mj, files


def main():
    td = tempfile.mkdtemp()
    try:
        pk, mj, files = setup(td)
        pf = [os.path.join(pk, f) for f in files if "props" in f]
        m1 = F.build_map(pf, [os.path.join(pk, "flagship_terrain_00.glb")]); m2 = F.build_map(list(reversed(pf)), [os.path.join(pk, "flagship_terrain_00.glb")])
        t("map is deterministic (file order does not matter)", json.dumps(m1) == json.dumps(m2))
        to = {n: e["to"] for e in m1["map"] for n in e["source_names"]}
        t(".NNN duplicate and hex/# names fold into one shared material", to["BUF_D_#8A5A32"] == to["BUF_D_#8A5A32.001"] == to["Bld_Mill_M0"], to)
        t("a colour far away stays its own material", to["Far"] != to["Bld_Mill_M0"])
        t("emissive is never merged with plain", to["Glow"] != to["Bld_Mill_M0"] and "Glow" in to["Glow"])
        t("shared names are M_BB_ and UE-safe", all(F.SAFE.match(x["name"]) and x["name"].startswith("M_BB_") for x in m1["materials"]))
        t("every merge within the radius", all(x["max_delta_e"] <= m1["radius_delta_e76"] for x in m1["materials"]))
        t("map counts source names", m1["source"]["material_names"] == 5)
        t("versioned schema", m1["schema"] == F.SCHEMA and m1["version"] == 1)
        ren = F.rename_table(["Cube.001", "Cube_001", "A#b", "Ok"])
        t("names made UE-safe, existing safe names keep priority, still unique", ren == {"Cube_001": "Cube_001", "Ok": "Ok", "Cube.001": "Cube_001_1", "A#b": "A_b"}, ren)
        t("fit_box: axis box for an axis cube", np.allclose(F.fit_box(cube((1, 2, 3), (0.5, 0.5, 0.5))[0].astype(float), 0.02)[2], 0.5))
        th = np.radians(30); Rz = np.array([[np.cos(th), -np.sin(th), 0], [np.sin(th), np.cos(th), 0], [0, 0, 1]])
        bar = cube((0, 0, 0), (2, 0.1, 0.1))[0].astype(float) @ Rz.T; bx = F.fit_box(bar, 0.02)
        t("fit_box: PCA box for a rotated bar (tight)", np.prod(bx[2]) < 0.05, bx[2])
        mj_map = os.path.join(td, "map.json"); json.dump(m1, open(mj_map, "w"))
        arch = os.path.join(td, "arch"); terr0 = F.sha(files["flagship_terrain_00.glb"])
        M = F.apply(mj, pk, mj_map, arch)
        t("R1 prop packets archived, not deleted", sorted(os.listdir(arch)) == ["flagship_props_000.glb", "flagship_props_001.glb"] and all(F.sha(open(os.path.join(arch, f), "rb").read()) == F.sha(files[f]) for f in os.listdir(arch)))
        t("terrain packet untouched", F.sha(open(os.path.join(pk, "flagship_terrain_00.glb"), "rb").read()) == terr0 and [p for p in M["packets"] if p["kind"] == "terrain"][0]["sha256"] == terr0)
        g, b = F.read_glb(os.path.join(pk, "flagship_props_000.glb")); names = [n["name"] for n in g["nodes"]]
        t("node names unique and UE-safe", len(names) == len(set(names)) and all(F.SAFE.match(n) for n in names), names)
        t("Cube.001 renamed without colliding with Cube_001", "Cube_001_1" in names and "Cube_001" in names)
        t("materials in the packet are the shared set only", {m["name"] for m in g["materials"]} <= {x["name"] for x in m1["materials"]} and len(g["materials"]) == 3, [m["name"] for m in g["materials"]])
        kids = {n["name"]: [g["nodes"][c]["name"] for c in n.get("children", [])] for n in g["nodes"] if not n["name"].startswith("UCX_")}
        t("UCX_<Mesh>_NN children on blocking props (two parts -> two boxes)", kids["Bld_Mill"] == ["UCX_Bld_Mill_00", "UCX_Bld_Mill_01"], kids)
        t("crew mob skipped for a physics asset", kids["Mob_Crew_Smith_ArmL"] == [] and "Mob_Crew_Smith_ArmL" in M["props_fixup"]["skipped_collision"]["physics_asset"])
        t("herb and tiny pebble skipped as decor", kids["Prop_Herb_Aloe"] == [] and kids["Prop_Pebble"] == [] and {"Prop_Herb_Aloe", "Prop_Pebble"} <= set(M["props_fixup"]["skipped_collision"]["decor"]))
        ucx = [n for n in g["nodes"] if n["name"].startswith("UCX_")]
        t("UCX meshes are 8-vertex boxes without a material", all(len(g["meshes"][n["mesh"]]["primitives"]) == 1 and "material" not in g["meshes"][n["mesh"]]["primitives"][0] and g["accessors"][g["meshes"][n["mesh"]]["primitives"][0]["attributes"]["POSITION"]]["count"] == 8 for n in ucx))
        ok = True
        for n in ucx:
            pr = g["meshes"][n["mesh"]]["primitives"][0]; v = F.accessor(g, b, pr["attributes"]["POSITION"]).astype(float); i = F.accessor(g, b, pr["indices"]).reshape(-1, 3); c = v.mean(0)
            ok &= all(np.dot(np.cross(v[q[1]] - v[q[0]], v[q[2]] - v[q[0]]), v[q[0]] - c) > 0 for q in i)
            a = g["accessors"][pr["attributes"]["POSITION"]]; ok &= np.allclose(v.min(0), a["min"], atol=1e-6) and np.allclose(v.max(0), a["max"], atol=1e-6)
        t("UCX faces wound outward, accessor min/max right", ok)
        mill = [n for n in g["nodes"] if n["name"] == "Bld_Mill"][0]
        P = F.accessor(g, b, g["meshes"][mill["mesh"]]["primitives"][0]["attributes"]["POSITION"]).astype(float)
        boxes = [F.accessor(g, b, g["meshes"][g["nodes"][c]["mesh"]]["primitives"][0]["attributes"]["POSITION"]).astype(float) for c in mill["children"]]
        t("boxes cover every render vertex", all(any(np.all((p >= bb.min(0) - 1e-5) & (p <= bb.max(0) + 1e-5)) for bb in boxes) for p in P))
        g1, _ = F.read_glb(os.path.join(pk, "flagship_props_001.glb")); many = [n for n in g1["nodes"] if n["name"] == "Prop_Many"][0]
        t("many parts merged down to max_pieces", len(many["children"]) == F.DEFAULT_RULES["max_pieces"], len(many["children"]))
        crate = [n for n in g1["nodes"] if n["name"] == "Prop_BBIsle_Crate_00"][0]
        t("overlapping duplicate parts give one box", len(crate["children"]) == 1, len(crate["children"]))
        rows = {p["file"]: p for p in M["packets"]}
        t("manifest shas/bytes/ucx match the new files", all(F.sha(open(os.path.join(pk, f), "rb").read()) == rows[f]["sha256"] and os.path.getsize(os.path.join(pk, f)) == rows[f]["bytes"] for f in files))
        t("manifest version bumped, fixup recorded with R1 shas and map sha", M["manifest_version"] == 2 and M["props_fixup"]["r1"]["flagship_props_000.glb"] == F.sha(P0) and len(M["props_fixup"]["map_sha256"]) == 64)
        t("placements follow the renames", any(p["prop"] == "Cube_001_1" for p in M["placements"]) and not any(p["prop"] == "Cube.001" for p in M["placements"]))
        t("props rows carry collision + ucx", all(("ucx" in p and p["collision"] in ("UCX", "none:decor", "none:physics_asset")) for p in M["props"]))
        first = {f: open(os.path.join(pk, f), "rb").read() for f in files}
        M2 = F.apply(mj, pk, mj_map, arch)
        t("re-run reads R1 from the archive and is byte-identical", all(open(os.path.join(pk, f), "rb").read() == first[f] for f in files) and M2["manifest_version"] == 2)
        open(os.path.join(arch, "flagship_props_000.glb"), "ab").write(b"x")
        try:
            F.apply(mj, pk, mj_map, arch); t("tampered archive refused", False)
        except SystemExit:
            t("tampered archive refused", True)
    finally:
        shutil.rmtree(td, ignore_errors=True)
    print("%d/%d" % (sum(R), len(R)))
    return 0 if all(R) else 1


if __name__ == "__main__":
    sys.exit(main())
