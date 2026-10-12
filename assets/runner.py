# SPDX-License-Identifier: MIT
"""Batch builder: specs -> judged, rendered, saved assets; scenes composed from them; tracker regenerated.

  python -m assets.runner build <module> [Asset ...] [--force] [--no-turntable]
        module: a python module with SPECS (e.g. assets.realm, assets.toolspecs)
  python -m assets.runner scene assets.realm      compose + render its SCENE
Each asset: guard (watcher not SHIPPING, no unsaved work) -> new file -> build -> judge -> glb export + self-check ->
turntable -> save art\\<Kind>\\<Asset>.blend. Rows: if the asset has a QUEUE.md row it is claimed and flipped READY
by the queue plugin's rules; otherwise it is saved only. Existing .blend files are skipped unless --force."""
import importlib, json, os, sys, time
from bharness.context import Context
from bharness.build import code, validate
from bharness.plugins.bridge import run
from bharness.plugins.queue import QueuePlugin, state, kind_of, Blocked
from bharness.plugins.judge import judge, passed
from bharness.plugins.probe import asset as probe
from bharness.plugins.render import RenderPlugin
from bharness.plugins.export import export_glb


def reset_own(ctx, name):
    """Drop a half-built untitled file only if it is ours (holds just this asset's collection)."""
    s = run(ctx.bridge, "import bpy\nresult={'file':bpy.data.filepath,'cols':[c.name for c in bpy.data.collections]}")
    if s["file"] == "" and s["cols"] in ([name], []):
        run(ctx.bridge, "import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\nresult=1")


def build_one(ctx, spec, force=False, turntable=8):
    q, rp = QueuePlugin(ctx), RenderPlugin(ctx)
    n = validate(spec)["asset"]
    rec = {"asset": n}
    rows = {r["asset"]: r for r in q.rows()}
    r = rows.get(n)
    if os.path.exists(q.blend_path(n)) and not force:
        rec["skipped"] = "exists"; return rec
    if r and state(r["status"]) not in ("TODO", "REJECTED") and r["status"].strip() != "DOING (%s)" % ctx.who:
        rec["skipped"] = r["status"]; return rec
    if r and state(r["status"]) in ("TODO", "REJECTED"):
        q.claim(n)
    q.open(n)
    try:
        rec["parts"] = run(ctx.bridge, code(spec))
    except Exception:
        reset_own(ctx, n); raise
    cs = judge(n, probe(ctx.bridge, n))
    rec["tris"] = sum(p["tris"] for p in rec["parts"])
    rec["fails"] = [c["check"] + " " + str(c["detail"]) for c in cs if not c["ok"]]
    rec["size"] = next((c["detail"] for c in cs if c["check"] == "size (info)"), "")
    if rec["fails"]:
        reset_own(ctx, n); return rec
    g = export_glb(ctx, n)
    rec["glb"] = g["path"]; rec["glb_fails"] = [c["check"] for c in g["checks"] if not c["ok"]]
    if rec["glb_fails"]:
        reset_own(ctx, n); return rec
    if r:
        res = q.ready(n, turntable=turntable)
        rec["status"] = q.row(n)["status"]; rec["turntable"] = (res.get("turntable") or [None])[1:2]
    else:
        if turntable:
            rec["turntable"] = rp.turntable(n, n=turntable)[1:2]
        rec["blend"] = q.save(n)["file"]; rec["status"] = "saved (no queue row)"
    return rec


SCENE_CODE = r'''
import bpy, math, os
place, out_png, res = %r, %r, %r
sc = bpy.context.scene
for name in set(p[0] for p in place):
    lc = bpy.context.view_layer.layer_collection.children.get(name)
    if lc: lc.exclude = True
for i, pl in enumerate(place):
    name, x, y, z, rot = pl[:5]; scl = pl[5] if len(pl) > 5 else 1.0
    e = bpy.data.objects.new("Place_%%02d_%%s" %% (i, name), None)
    e.instance_type = "COLLECTION"; e.instance_collection = bpy.data.collections[name]
    e.location = (x, y, z); e.scale = (scl, scl, scl); e.rotation_euler = (0, 0, math.radians(rot)); sc.collection.objects.link(e)
w = bpy.data.worlds.new("Cave"); w.use_nodes = True; sc.world = w
bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.012, 0.010, 0.025, 1); bg.inputs[1].default_value = 1.0
def light(n, kind, loc, energy, color, size=0.3, rot=None):
    d = bpy.data.lights.new(n, kind); d.energy = energy; d.color = color
    if kind in ("POINT", "SPOT"): d.shadow_soft_size = size
    if kind == "AREA": d.size = size
    o = bpy.data.objects.new(n, d); o.location = loc
    if rot: o.rotation_euler = rot
    sc.collection.objects.link(o); return o
for p in place:
    if p[0] == "Prop_Realm_Cave_Torch":
        light("TorchLight", "POINT", (p[1], p[2] - 0.2, p[3] + 1.6), 120, (1.0, 0.55, 0.2), 0.15)
light("Key", "AREA", (2.5, -3.5, 3.2), 450, (1.0, 0.92, 0.85), 2.5, (math.radians(55), 0, math.radians(35)))
light("Rim", "SPOT", (0, 4.6, 3.4), 900, (0.55, 0.65, 1.0), 0.4, (math.radians(-40), 0, math.radians(180)))
light("Crystal", "POINT", (0, 1.2, 0.4), 40, (0.5, 0.9, 1.0), 0.5)
cd = bpy.data.cameras.new("BattleCam"); cd.lens = 22; cam = bpy.data.objects.new("BattleCam", cd); sc.collection.objects.link(cam)
cam.location = (0.3, -6.4, 2.0)
from mathutils import Vector
cam.rotation_euler = (Vector((0, 2.4, 1.9)) - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
r = sc.render; r.resolution_x, r.resolution_y, r.resolution_percentage = res[0], res[1], 100
r.image_settings.file_format = "PNG"; r.filepath = out_png; r.film_transparent = False
try:
    sc.eevee.use_shadows = True; sc.eevee.use_raytracing = True
except Exception: pass
sc.view_settings.view_transform = "AgX"; sc.view_settings.look = "AgX - Punchy"
bpy.ops.render.render(write_still=True)
result = out_png
'''


def scene(ctx, mod, name="Realm_ShardTyrant_Battle", res=(1600, 900)):
    q = QueuePlugin(ctx)
    busy = q.watcher_busy()
    if busy:
        raise Blocked("watcher shipping " + ", ".join(busy))
    fs = run(ctx.bridge, "import bpy\nresult={'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty}")
    if fs["dirty"]:
        raise Blocked("Blender has unsaved work in %r; never discarded" % fs["file"])
    run(ctx.bridge, "import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\nresult=1")
    specs = {s["asset"]: s for s in mod.SPECS}
    for a in sorted(set(p[0] for p in mod.SCENE)):
        run(ctx.bridge, code(specs[a]))
    folder = os.path.join(ctx.art, "scenes"); os.makedirs(folder, exist_ok=True)
    png = os.path.join(folder, name + ".png")
    run(ctx.bridge, SCENE_CODE % (mod.SCENE, png, list(res)), timeout=900)
    blend = os.path.join(folder, name + ".blend")
    run(ctx.bridge, "import bpy\nbpy.ops.wm.save_as_mainfile('EXEC_DEFAULT', filepath=%r, check_existing=False)\nresult=1" % blend)
    return {"png": png, "blend": blend}


def tracker():
    try:
        from assets import tracker as t
        return t.build()[0]
    except Exception as e:   # the tracker is a report; it never fails a build
        return "tracker not regenerated: %r" % e


def main(a=sys.argv[1:]):
    ctx = Context()
    cmd, mod = a[0], importlib.import_module(a[1])
    names = [x for x in a[2:] if not x.startswith("--")]
    if cmd == "scene":
        print(json.dumps(scene(ctx, mod))); print(json.dumps({"tracker": tracker()})); return 0
    bad = 0
    for s in mod.SPECS:
        if names and s["asset"] not in names:
            continue
        try:
            rec = build_one(ctx, s, force="--force" in a, turntable=0 if "--no-turntable" in a else 8)
        except Exception as e:
            rec = {"asset": s["asset"], "error": repr(e)[:300]}
        bad += bool(rec.get("fails") or rec.get("glb_fails") or rec.get("error"))
        print(json.dumps(rec), flush=True)
    print(json.dumps({"tracker": tracker()}))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
