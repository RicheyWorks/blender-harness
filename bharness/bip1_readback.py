# SPDX-License-Identifier: MIT
"""Headless Blender re-read of BIP 1 R2 prop packets (bip1_fixup output): every packet is imported with Blender's own glTF
importer into an empty scene and checked against the manifest: object names == glTF node names (Blender renames clashes to .NNN,
so any suffix means a duplicate), UE-safe names, UCX_<Mesh>_NN children per prop == manifest ucx, materials == shared M_BB_ set,
UCX objects material-free, render tris == manifest. Optional --sheet renders sample props with their UCX as red wire.
  blender -b --factory-startup --python bharness/bip1_readback.py -- --manifest flagship.bip.json --packets <dir> --out report.json [--sheet sheet.png --props A,B,..]"""
import argparse, json, math, os, re, sys
import bpy

SAFE = re.compile(r"^[A-Za-z0-9_]+$")


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def tris(o):
    me = o.data; me.calc_loop_triangles(); return len(me.loop_triangles)


def check_packet(path, rows, prow):
    clear(); bpy.ops.import_scene.gltf(filepath=path)
    objs = [o for o in bpy.data.objects if o.type == "MESH"]; fails = []
    import struct
    d = open(path, "rb").read(); n = struct.unpack("<I", d[12:16])[0]; g = json.loads(d[20:20 + n]); want = {nd["name"] for nd in g["nodes"]}
    names = {o.name for o in objs}
    if names != want:
        fails.append("object names differ from glTF nodes (%d extra, %d missing)" % (len(names - want), len(want - names)))
    if any(not SAFE.match(x) for x in names):
        fails.append("unsafe names")
    ucx = 0; render_tris = 0
    for o in objs:
        if o.name.startswith("UCX_"):
            ucx += 1
            if o.parent is None or o.name.rsplit("_", 1)[0] != "UCX_" + o.parent.name:
                fails.append(o.name + ": not a UCX child of its mesh")
            if any(s.material for s in o.material_slots):
                fails.append(o.name + ": UCX has a material")
            continue
        render_tris += tris(o); r = rows.get(o.name)
        if r is None:
            fails.append(o.name + ": not in manifest props"); continue
        k = sum(1 for c in o.children if c.name.startswith("UCX_"))
        if k != r["ucx"]:
            fails.append("%s: ucx %d != manifest %d" % (o.name, k, r["ucx"]))
    mats = sorted({s.material.name for o in objs for s in o.material_slots if s.material})
    if not all(re.match(r"^M_BB_[A-Za-z0-9_]+$", m) for m in mats):
        fails.append("non-shared material names: %s" % [m for m in mats if not re.match(r"^M_BB_[A-Za-z0-9_]+$", m)][:5])
    if len(mats) != prow["materials"]:
        fails.append("materials %d != manifest %d" % (len(mats), prow["materials"]))
    if ucx != prow["ucx"]:
        fails.append("packet ucx %d != manifest %d" % (ucx, prow["ucx"]))
    if render_tris != prow["tris"]:
        fails.append("render tris %d != manifest %d" % (render_tris, prow["tris"]))
    return {"packet": prow["id"], "objects": len(objs), "ucx": ucx, "materials": len(mats), "render_tris": render_tris, "fails": fails}, mats


def sheet(o, M, rows):
    clear(); by = {}
    for nm in o.props.split(","):
        by.setdefault(rows[nm]["packet"], []).append(nm)
    placed = []; x = 0.0
    for pk, nms in sorted(by.items()):
        before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(o.packets, pk + ".glb")); new = [ob for ob in bpy.data.objects if ob not in before]
        for ob in new:
            root = ob if not ob.name.startswith("UCX_") else ob.parent
            if root is None or root.name not in nms:
                bpy.data.objects.remove(ob, do_unlink=True)
    red = bpy.data.materials.new("UCXWire"); red.diffuse_color = (1, 0.05, 0.05, 1)
    roots = sorted([ob for ob in bpy.data.objects if ob.type == "MESH" and not ob.name.startswith("UCX_")], key=lambda ob: o.props.split(",").index(ob.name))
    cols = 4; cell = []
    for ob in roots:
        bb = [ob.matrix_world @ __import__("mathutils").Vector(c) for c in ob.bound_box]; cell.append(max(max(v[i] for v in bb) - min(v[i] for v in bb) for i in range(3)))
    for i, ob in enumerate(roots):
        s = 1.0 / max(cell[i], 1e-3); ob.scale = (s, s, s); ob.location = ((i % cols) * 1.6, -(i // cols) * 1.6 * 0 , -(i // cols) * 1.6)
        for c in ob.children:
            if c.name.startswith("UCX_"):
                c.data.materials.clear(); c.data.materials.append(red); w = c.modifiers.new("w", "WIREFRAME"); w.thickness = 0.02 / s
    sc = bpy.context.scene; sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.color_type = "MATERIAL"; sc.display.shading.light = "STUDIO"
    sc.render.resolution_x, sc.render.resolution_y = 1600, 400 * math.ceil(len(roots) / cols) + 0
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.type = "ORTHO"; rows_n = math.ceil(len(roots) / cols); cam.data.ortho_scale = cols * 1.6
    cx, cz = (cols - 1) * 0.8, -(rows_n - 1) * 0.8
    cam.location = (cx + 6, -12 , cz + 0.5 + 5); d = __import__("mathutils").Vector((cx, 0, cz + 0.5)) - cam.location
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler(); cam.data.clip_end = 100
    sc.render.filepath = o.sheet; bpy.ops.render.render(write_still=True)


def main():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", required=True); ap.add_argument("--packets", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--sheet"); ap.add_argument("--props", default=""); o = ap.parse_args(a)
    M = json.load(open(o.manifest, encoding="utf-8")); rows = {p["name"]: p for p in M["props"]}; rep = []; allm = set()
    for p in M["packets"]:
        if p["kind"] != "props":
            continue
        r, mats = check_packet(os.path.join(o.packets, p["file"]), rows, p); rep.append(r); allm |= set(mats)
        print("readback %s objects %d ucx %d materials %d %s" % (p["id"], r["objects"], r["ucx"], r["materials"], "OK" if not r["fails"] else "FAIL " + "; ".join(r["fails"][:3])))
    out = {"packets": len(rep), "passed": sum(1 for r in rep if not r["fails"]), "ucx": sum(r["ucx"] for r in rep), "shared_materials": len(allm),
           "render_meshes": sum(r["objects"] - r["ucx"] for r in rep), "blender": bpy.app.version_string, "rows": rep}
    json.dump(out, open(o.out, "w"), indent=1); print("READBACK %d/%d ucx %d materials %d" % (out["passed"], out["packets"], out["ucx"], out["shared_materials"]))
    if o.sheet:
        sheet(o, M, rows)


main()
