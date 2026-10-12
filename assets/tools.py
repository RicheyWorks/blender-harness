# SPDX-License-Identifier: MIT
"""Daedalus priority-1 tools, built from bevelled boxes (BLENDER-TEAM-BRIEF.md).

  python -m assets.tools [Asset ...] [--dry]
For each asset: claim its QUEUE.md row (if it has one) -> open/new file -> build -> judge -> turntable (8) ->
save art\\<Kind>\\<Asset>.blend -> READY. Assets without a row are built, judged, rendered and saved, never flipped.
Upright tools stand on z=0, centred on x/y, front face toward -Y. One object per asset, 1-3 flat materials."""
import sys, json
from bharness.context import Context
from bharness.plugins.bridge import run
from bharness.plugins.queue import QueuePlugin, state, QueueError
from bharness.plugins.judge import judge, passed
from bharness.plugins.probe import asset as probe
from bharness.plugins.render import RenderPlugin

WOOD, GRIP, STONE = "9A6B3F", "5A3A22", "7D7B84"
STEEL, DARK, GOLD, CYAN = "C9D4E0", "4A4D57", "F2C230", "7FE3FF"

def pickaxe(head, glow=False):
    # (size xyz, centre xyz, material index)
    b = [((0.06, 0.06, 0.80), (0, 0, 0.40), 0),        # shaft
         ((0.075, 0.075, 0.18), (0, 0, 0.09), 1),      # grip wrap
         ((0.085, 0.085, 0.05), (0, 0, 0.02), 1),      # pommel
         ((0.13, 0.11, 0.12), (0, 0, 0.83), 2),        # head socket
         ((0.16, 0.08, 0.075), (0.14, 0, 0.845), 2),   # right arm
         ((0.16, 0.08, 0.075), (-0.14, 0, 0.845), 2),  # left arm
         ((0.09, 0.06, 0.06), (0.255, 0, 0.815), 2),   # right tip (droops)
         ((0.09, 0.06, 0.06), (-0.255, 0, 0.815), 2),
         ((0.04, 0.045, 0.045), (0.31, 0, 0.79), 2),   # points
         ((0.04, 0.045, 0.045), (-0.31, 0, 0.79), 2)]
    return b, [WOOD, GRIP, head], glow

BUILDS = {
    "Tool_Pickaxe": pickaxe(STONE),
    "Tool_Pickaxe_Iron": pickaxe("C9B49C"),
    "Tool_Pickaxe_Gold": pickaxe(GOLD),
    "Tool_Pickaxe_Starmetal": pickaxe(CYAN, glow=True),
    "Tool_Shovel": ([((0.06, 0.06, 0.62), (0, 0, 0.62), 0),   # shaft 0.31..0.93
                     ((0.07, 0.07, 0.16), (0, 0, 0.86), 1),
                     ((0.22, 0.06, 0.05), (0, 0, 0.955), 1),  # T grip
                     ((0.10, 0.07, 0.08), (0, 0, 0.30), 2),   # collar
                     ((0.24, 0.035, 0.22), (0, 0, 0.15), 2),  # blade
                     ((0.16, 0.035, 0.06), (0, 0, 0.03), 2),  # blade tip
                     ((0.26, 0.05, 0.03), (0, 0, 0.265), 2)], # step
                    [WOOD, GRIP, STEEL], False),
    "Tool_Axe": ([((0.06, 0.06, 0.80), (0, 0, 0.40), 0),
                  ((0.075, 0.075, 0.18), (0, 0, 0.09), 1),
                  ((0.085, 0.085, 0.05), (0, 0, 0.02), 1),
                  ((0.12, 0.10, 0.14), (0, 0, 0.73), 2),      # eye
                  ((0.12, 0.05, 0.14), (0.11, 0, 0.73), 2),   # cheek
                  ((0.06, 0.035, 0.26), (0.19, 0, 0.72), 2),  # bit (edge)
                  ((0.07, 0.07, 0.07), (-0.08, 0, 0.73), 2)], # poll
                 [WOOD, GRIP, STEEL], False),
    "Wpn_Sword": ([((0.05, 0.05, 0.05), (0, 0, 0.025), 2),    # pommel
                   ((0.045, 0.045, 0.17), (0, 0, 0.135), 1),  # grip
                   ((0.30, 0.07, 0.05), (0, 0, 0.245), 2),    # guard
                   ((0.06, 0.08, 0.06), (0.17, 0, 0.255), 2), # guard ends
                   ((0.06, 0.08, 0.06), (-0.17, 0, 0.255), 2),
                   ((0.08, 0.025, 0.72), (0, 0, 0.63), 0),    # blade
                   ((0.05, 0.025, 0.06), (0, 0, 1.02), 0),    # tip step
                   ((0.02, 0.02, 0.04), (0, 0, 1.07), 0)],    # point -> 1.09 m
                  [STEEL, GRIP, GOLD], False),
    "Wpn_Blaster": ([((0.10, 0.36, 0.14), (0, 0.0, 0.22), 0),      # body (length along Y, muzzle -Y)
                     ((0.05, 0.22, 0.05), (0, -0.28, 0.24), 0),    # barrel
                     ((0.07, 0.05, 0.07), (0, -0.40, 0.24), 2),    # muzzle glow
                     ((0.08, 0.16, 0.10), (0, 0.25, 0.20), 1),     # stock
                     ((0.06, 0.06, 0.15), (0, 0.10, 0.075), 1),    # grip
                     ((0.06, 0.08, 0.14), (0, -0.06, 0.09), 1),    # magazine
                     ((0.04, 0.12, 0.05), (0, 0.0, 0.315), 1),     # scope
                     ((0.11, 0.18, 0.02), (0, -0.05, 0.16), 2)],   # cyan strip
                    [DARK, "4B974B", CYAN], True),
}

CODE = r'''
import bpy, bmesh
name, boxes, cols, glow = %r, %r, %r, %r
col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in list(bpy.data.objects):
    if o.type in ("MESH", "LIGHT", "CAMERA") and o.name != "BH_keep": bpy.data.objects.remove(o)
main = bmesh.new()
for (sx, sy, sz), (cx, cy, cz), mi in boxes:
    t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0)
    for v in t.verts: v.co.x = v.co.x*sx + cx; v.co.y = v.co.y*sy + cy; v.co.z = v.co.z*sz + cz
    bmesh.ops.bevel(t, geom=list(t.edges), offset=min(sx, sy, sz)*0.12, segments=1, affect="EDGES")
    for f in t.faces: f.material_index = mi
    m = bpy.data.meshes.new("tmp"); t.to_mesh(m); t.free(); main.from_mesh(m); bpy.data.meshes.remove(m)
xs = [v.co.x for v in main.verts]; ys = [v.co.y for v in main.verts]; zs = [v.co.z for v in main.verts]
off = ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, min(zs))
for v in main.verts: v.co.x -= off[0]; v.co.y -= off[1]; v.co.z -= off[2]
me = bpy.data.meshes.new(name); main.to_mesh(me); main.free()
ob = bpy.data.objects.new(name, me); col.objects.link(ob)
for i, h in enumerate(cols):
    mname = "%%s_M%%d" %% (name, i)
    mat = bpy.data.materials.get(mname) or bpy.data.materials.new(mname); mat.use_nodes = True
    rgb = tuple((int(h[k:k+2], 16)/255.0) ** 2.2 for k in (0, 2, 4)) + (1.0,)
    p = mat.node_tree.nodes["Principled BSDF"]; p.inputs["Base Color"].default_value = rgb
    p.inputs["Roughness"].default_value = 0.6; mat.diffuse_color = rgb
    if glow and i == len(cols) - 1:
        p.inputs["Emission Color"].default_value = rgb; p.inputs["Emission Strength"].default_value = 2.0
    ob.data.materials.append(mat)
result = {"tris": sum(len(f.vertices) - 2 for f in me.polygons), "dims": list(ob.dimensions)}
'''


def main(a=sys.argv[1:]):
    names = [x for x in a if not x.startswith("--")] or list(BUILDS)
    ctx = Context(); q = QueuePlugin(ctx); rp = RenderPlugin(ctx)
    rows = {r["asset"]: r for r in q.rows()}
    out = []
    for n in names:
        r = rows.get(n)
        rec = {"asset": n, "row": bool(r)}
        try:
            if r and r["status"].strip() != "DOING (%s)" % ctx.who:
                if state(r["status"]) not in ("TODO", "REJECTED"):
                    rec["skipped"] = r["status"]; out.append(rec); print(json.dumps(rec)); continue
                q.claim(n)
            q.open(n)
            try:
                rec["build"] = run(ctx.bridge, CODE % ((n,) + BUILDS[n]))
            except Exception:
                # the file is the one q.open just made for us: drop our half-built scene so Blender is clean again
                run(ctx.bridge, "import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\nresult=1")
                raise
            cs = judge(n, probe(ctx.bridge, n))
            rec["fails"] = [c["check"] + " " + c["detail"] for c in cs if not c["ok"]]
            rec["size"] = next(c["detail"] for c in cs if c["check"] == "size (info)")
            if rec["fails"]:
                print(json.dumps(rec)); out.append(rec); continue
            if r:
                res = q.ready(n, turntable=8)
                rec["status"] = q.row(n)["status"]; rec["turntable"] = res["turntable"]; rec["blend"] = res["blend"]
            else:
                rec["turntable"] = rp.turntable(n, n=8); rec["blend"] = q.save(n)["file"]; rec["status"] = "saved, no QUEUE row"
        except QueueError as e:
            rec["error"] = repr(e)
        print(json.dumps(rec)); out.append(rec)
    return 0 if all(not x.get("fails") and not x.get("error") for x in out) else 1


if __name__ == "__main__":
    sys.exit(main())
