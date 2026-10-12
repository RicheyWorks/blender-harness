# SPDX-License-Identifier: MIT
"""Fixed-scale lineup renders: every built ecosystem asset of one biome, side by side on one ground line, one
orthographic camera, so a 6 cm ant and a 4 m tree are drawn at their true relative sizes (turntables re-frame each asset,
so they cannot show scale). Assets are linked from their saved .blend files (nothing is rebuilt), the lineup is saved
to art\\scenes\\Lineup_<Biome>.blend so Blender is never left with unsaved work, and placements are printed as JSON so
labels can be drawn afterwards.

  python -m assets.lineup                 every biome
  python -m assets.lineup Desert Tundra   some biomes"""
import json, os, re, sys
from bharness.context import Context
from bharness.plugins.queue import QueuePlugin, Blocked
from assets.runner import run
from assets.catalog import ASSETS
from assets import ecospecs

CODE = r'''
import bpy, math
from mathutils import Vector
items, out_png, px_per_m = %r, %r, %r
bpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)
sc = bpy.context.scene
placed, x = [], 0.0
for name, path in items:
    with bpy.data.libraries.load(path, link=True) as (src, dst):
        dst.collections = [name] if name in src.collections else []
    if not dst.collections: continue
    col = dst.collections[0]
    pts = [o.matrix_world @ Vector(c) for o in col.all_objects if o.type == "MESH" for c in o.bound_box]
    lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
    w = hi.x - lo.x; gap = max(0.15, 0.25 * w)
    e = bpy.data.objects.new("L_" + name, None); e.instance_type = "COLLECTION"; e.instance_collection = col
    e.location = (x + gap / 2 - lo.x, 0, 0); sc.collection.objects.link(e)
    placed.append({"asset": name, "x0": x, "x1": x + w + gap, "h": hi.z, "w": w}); x += w + gap
W = x; H = max(p["h"] for p in placed) * 1.12 + 0.3
g = bpy.data.meshes.new("Ground"); import bmesh; bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1); bm.to_mesh(g); bm.free()
go = bpy.data.objects.new("Ground", g); go.scale = (W + 2, 4, 0.02); go.location = (W / 2, 1.5, -0.011); sc.collection.objects.link(go)
gm = bpy.data.materials.new("GroundMat"); gm.use_nodes = True; gm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.55, 0.52, 0.47, 1); g.materials.append(gm)
w = bpy.data.worlds.new("Lineup"); w.use_nodes = True; sc.world = w; w.node_tree.nodes["Background"].inputs[0].default_value = (0.80, 0.77, 0.71, 1)
def light(n, kind, rot, energy):
    d = bpy.data.lights.new(n, kind); d.energy = energy; o = bpy.data.objects.new(n, d); o.rotation_euler = rot; sc.collection.objects.link(o)
light("Sun", "SUN", (math.radians(50), 0, math.radians(25)), 3.5); light("Fill", "SUN", (math.radians(70), 0, math.radians(-140)), 1.2)
cd = bpy.data.cameras.new("Cam"); cd.type = "ORTHO"; cam = bpy.data.objects.new("Cam", cd); sc.collection.objects.link(cam)
tilt = 0.0   # pure front: an ortho camera tilt pushed the tops of tall trees out of frame
cd.ortho_scale = max(W, H)
cam.rotation_euler = (math.radians(90) - tilt, 0, 0); cam.location = (W / 2, -40, H / 2 + 40 * math.tan(tilt))
sc.camera = cam
r = sc.render; r.resolution_x = int(W * px_per_m); r.resolution_y = int(H * px_per_m); r.resolution_percentage = 100
if r.resolution_x > 6000:
    k = 6000 / r.resolution_x; r.resolution_x = 6000; r.resolution_y = int(r.resolution_y * k)
r.image_settings.file_format = "PNG"; r.filepath = out_png
sc.view_settings.view_transform = "AgX"
try: sc.eevee.use_shadows = True
except Exception: pass
bpy.ops.render.render(write_still=True)
result = {"W": W, "H": H, "res": [r.resolution_x, r.resolution_y], "placed": placed}
'''


def biomes():
    world = {a["name"]: a["world"] for a in ASSETS}
    out = {}
    for s in ecospecs.SPECS:
        out.setdefault(world[s["asset"]], []).append(s["asset"])
    return out


def slug(b): return re.sub(r"[^A-Za-z0-9]+", "_", b.split(" (")[0]).strip("_")


def main(a=sys.argv[1:]):
    ctx = Context(); q = QueuePlugin(ctx)
    if q.watcher_busy(): raise Blocked("watcher shipping")
    fs = run(ctx.bridge, "import bpy\nresult={'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty}")
    if fs["dirty"]: raise Blocked("Blender has unsaved work in %r; never discarded" % fs["file"])
    folder = os.path.join(ctx.art, "scenes"); os.makedirs(folder, exist_ok=True)
    for b, names in biomes().items():
        if a and slug(b) not in a and b not in a: continue
        # fauna first (small to large), then flora (small to large) so the eye reads both scales
        items = []
        for n in names:
            p = os.path.join(ctx.art, n.split("_")[0], n + ".blend")
            if os.path.exists(p): items.append((n, p))
        items.sort(key=lambda t: (not t[0].startswith("Mob_"), t[0]))
        chunks = [items[i:i + 24] for i in range(0, len(items), 24)]   # long biomes split into several strips
        for k, part in enumerate(chunks):
            png = os.path.join(folder, "Lineup_%s%s.png" % (slug(b), "_%d" % (k + 1) if len(chunks) > 1 else ""))
            res = run(ctx.bridge, CODE % (part, png, 140.0), timeout=900)
            run(ctx.bridge, "import bpy\nbpy.ops.wm.save_as_mainfile('EXEC_DEFAULT', filepath=%r, check_existing=False)\nresult=1" % png.replace(".png", ".blend"))
            res.update({"biome": b, "png": png})
            json.dump(res, open(png.replace(".png", ".json"), "w"))
            print(json.dumps(res), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
