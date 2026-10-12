# SPDX-License-Identifier: MIT
"""Read a .glb's JSON chunk without any 3D library (mirrors Daedalus2 asset_pipeline/glb.py) and check it against
what Blender measured, so an export is proven before the pipeline ever sees it."""
import json, struct

TRIANGLES = 4


def read_json(path):
    with open(path, "rb") as f:
        head = f.read(12)
        if len(head) < 12:
            raise ValueError("%s is not a GLB: too short" % path)
        magic, version, _ = struct.unpack("<4sII", head)
        if magic != b"glTF":
            raise ValueError("%s is not a GLB: bad magic" % path)
        if version != 2:
            raise ValueError("%s is glTF version %d, want 2" % (path, version))
        clen, ctype = struct.unpack("<I4s", f.read(8))
        if ctype != b"JSON":
            raise ValueError("%s: first chunk is not JSON" % path)
        return json.loads(f.read(clen).decode("utf-8"))


def summarize(doc):
    acc = doc.get("accessors", [])
    mats = [m.get("name", "material_%d" % i) for i, m in enumerate(doc.get("materials", []))]
    meshes = []
    for i, mesh in enumerate(doc.get("meshes", [])):
        tris, used, lo, hi = 0, [], None, None
        for prim in mesh.get("primitives", []):
            if prim.get("mode", TRIANGLES) == TRIANGLES:
                tris += acc[prim["indices"]]["count"] // 3 if "indices" in prim else acc[prim["attributes"]["POSITION"]]["count"] // 3
            if "material" in prim and mats[prim["material"]] not in used:
                used.append(mats[prim["material"]])
            pos = acc[prim["attributes"]["POSITION"]]
            if "min" in pos:
                lo = pos["min"] if lo is None else [min(a, b) for a, b in zip(lo, pos["min"])]
                hi = pos["max"] if hi is None else [max(a, b) for a, b in zip(hi, pos["max"])]
        ext = [h - l for l, h in zip(lo, hi)] if lo else [0, 0, 0]
        meshes.append({"name": mesh.get("name", "mesh_%d" % i), "triangles": tris, "materials": used,
                       "dims": sorted((round(e, 4) for e in ext), reverse=True)})
    nodes = [{"name": n.get("name"), "mesh": n["mesh"], "scale": n.get("scale", [1, 1, 1])}
             for n in doc.get("nodes", []) if "mesh" in n]
    return {"meshes": meshes, "nodes": nodes, "materials": mats}


def check(probe, summ, tol=0.01):
    """[{check, ok, detail}]: the file holds exactly what Blender measured (the pipeline's first judge checks)."""
    c = []
    add = lambda k, ok, d="": c.append({"check": k, "ok": bool(ok), "detail": d})
    objs = probe["objects"]
    add("every Blender object reached the file", len(objs) == len(summ["nodes"]) and objs, "Blender %d, file %d" % (len(objs), len(summ["nodes"])))
    bt, ft = sum(o["tris"] for o in objs), sum(m["triangles"] for m in summ["meshes"])
    add("triangles: Blender = file", bt == ft, "Blender %d, file %d" % (bt, ft))
    add("1-3 materials per mesh in the file", all(1 <= len(m["materials"]) <= 3 for m in summ["meshes"]),
        [len(m["materials"]) for m in summ["meshes"]])
    add("no node scale baked in", all(all(abs(s - 1) < 1e-4 for s in n["scale"]) for n in summ["nodes"]))
    bd = sorted(sorted((round(o["max"][i] - o["min"][i], 4) for i in range(3)), reverse=True) for o in objs)
    fd = sorted(m["dims"] for m in summ["meshes"])
    add("sizes: Blender = file", len(bd) == len(fd) and all(all(abs(a - b) <= tol + 0.01 * max(a, b) for a, b in zip(x, y)) for x, y in zip(bd, fd)),
        "Blender %s, file %s" % (bd, fd))
    names = sorted(o["name"] for o in objs)
    add("node names = Blender names", sorted(n["name"] for n in summ["nodes"]) == names)
    return c
