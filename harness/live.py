"""Live suite: the real Blender on 127.0.0.1:9876, a THROWAWAY asset in a THROWAWAY art folder.

  python -m harness.live
Never touches the real board (only reads it to see that the watcher isn't SHIPPING), refuses to start if Blender
has unsaved work, and reopens the file Blender had open before (Blender is left clean, as it was found)."""
import base64, json, os, socket, sys, tempfile, time
from harness.check import Checks
from harness.fakes import QUEUE
from harness.ledger import record
from bharness.client import Bridge
from bharness.context import Context, DEFAULT_ART
from bharness.plugins.bridge import run, FILESTATE
from bharness.plugins.probe import asset as probe
from bharness.plugins.judge import judge, passed, first_failure
from bharness.plugins.queue import QueuePlugin, parse, state
from bharness.plugins.render import RenderPlugin

A = "Prop_BHTest"
t = Checks()
art = tempfile.mkdtemp(prefix="bh-live-art-")
open(os.path.join(art, "QUEUE.md"), "w", newline="").write(QUEUE)
ctx = Context(art=art)
b = ctx.bridge
q = QueuePlugin(ctx)

if not t("Blender answers ping", b.up()):
    t.done()
fs0 = run(b, FILESTATE)
if not t("Blender has no unsaved work (else we stop: never discard it)", not fs0["dirty"], fs0):
    t.done()
real = os.path.join(DEFAULT_ART, "QUEUE.md")
busy = [r["asset"] for r in parse(open(real, encoding="utf-8").read())[0] if state(r["status"]) == "SHIPPING"] if os.path.exists(real) else []
if not t("the art-queue watcher is not shipping (Blender is free)", not busy, busy):
    t.done()
try:
    q.claim(A)
    t("claim in the throwaway queue", q.row(A)["status"] == "DOING (Blender Boss)")
    q.open(A)
    fs = run(b, FILESTATE)
    t("new empty file opened (no modal, EXEC_DEFAULT)", fs["file"] == "" and not fs["dirty"], fs)
    BUILD = r'''
import bpy, bmesh
col = bpy.data.collections[%r]
me = bpy.data.meshes.new("%s_Body"); bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
bmesh.ops.bevel(bm, geom=[e for e in bm.edges], offset=0.05, segments=1, affect="EDGES")
for v in bm.verts: v.co.z += 0.5
bm.to_mesh(me); bm.free()
ob = bpy.data.objects.new("%s_Body", me); col.objects.link(ob)
m = bpy.data.materials.new("BH_Wood"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.55, 0.35, 0.18, 1)
ob.data.materials.append(m)
result = ob.name
''' % (A, A, A)
    t("build a bevelled 1 m crate through execute_code", run(b, BUILD) == A + "_Body")
    p = probe(b, A)
    cs = judge(A, p)
    t("the crate passes every brief rule", passed(cs), [c for c in cs if not c["ok"]])
    t("triangles measured after modifiers", 0 < sum(o["tris"] for o in p["objects"]) <= 3000, p["objects"][0]["tris"])
    run(b, "import bpy\nbpy.data.objects['%s_Body'].scale=(2,1,1)\nresult=1" % A)
    t("judge catches unapplied scale live", first_failure(judge(A, probe(b, A))) == "scale applied")
    run(b, "import bpy\nbpy.data.objects['%s_Body'].scale=(1,1,1)\nresult=1" % A)
    run(b, "import bpy\nbpy.data.objects['%s_Body'].location.z=0.4\nresult=1" % A)
    t("judge catches a floating asset live", first_failure(judge(A, probe(b, A))) == "stands on z=0 (bottom-centre origin)")
    run(b, "import bpy\nbpy.data.objects['%s_Body'].location.z=0\nresult=1" % A)
    shot = os.path.join(art, "shot.png")
    s = RenderPlugin(ctx).shot(shot)
    t("viewport screenshot saved as a real PNG", open(shot, "rb").read(4) == b"\x89PNG", s)
    r = b.py("def (")
    t("syntax error -> status error with message", r["status"] == "error" and "SyntaxError" in r["message"])
    r = b.py("1/0")
    t("runtime error -> status error", r["status"] == "error" and "ZeroDivision" in r["message"])
    t("bridge alive after errors", b.up())
    try:
        Bridge(timeout=1).py("import time; time.sleep(3)")
        t("a 1 s client timeout on a 3 s job times out", False)
    except socket.timeout:
        t("a 1 s client timeout on a 3 s job times out", True)
    t0 = time.time(); up = b.up()
    t("bridge answers again after the job finishes (it is not cancelled)", up, "%.1fs" % (time.time() - t0))
    t0 = time.time()
    res = q.ready(A, turntable=4)
    t("ready: judged, turntable, saved, row READY", res["ready"] and q.row(A)["status"] == "READY", res.get("failed"))
    frames = res.get("turntable") or []
    t("4 turntable frames in promo\\%s, real PNGs" % A,
      len(frames) == 4 and all(open(f, "rb").read(4) == b"\x89PNG" for f in frames), frames)
    t("turntable took %.1fs, under 60s" % (time.time() - t0), time.time() - t0 < 60)
    blend = os.path.join(art, "Prop", A + ".blend")
    t(".blend saved at art\\Prop\\%s.blend" % A, os.path.exists(blend) and open(blend, "rb").read(7) == b"BLENDER")
    fs = run(b, FILESTATE)
    t("Blender is clean after save; turntable left nothing behind",
      not fs["dirty"] and not run(b, "import bpy\nresult=[o.name for o in bpy.data.objects if o.name.startswith('BH_TT')]"), fs)
    t("feed.jsonl got claim + ready", [json.loads(l)["event"] for l in open(os.path.join(art, "feed.jsonl"))] == ["doing", "ready"])
    caps = run(b, "import bpy, addon_utils\nresult={'blender': bpy.app.version_string, 'engine': bpy.context.scene.render.engine,"
                  "'types': len(dir(bpy.types)), 'ops': {c: len(dir(getattr(bpy.ops, c))) for c in dir(bpy.ops)},"
                  "'addons': sorted(bpy.context.preferences.addons.keys())}")
    record("capabilities", "live", {"blender": caps["blender"], "types": caps["types"], "op_categories": len(caps["ops"]),
                                    "operators": sum(caps["ops"].values()), "addons": caps["addons"]})
    t("capabilities ledger recorded", caps["types"] > 1000, caps["types"])
finally:
    if fs0["file"]:
        run(b, "import bpy\nbpy.ops.wm.open_mainfile('EXEC_DEFAULT', filepath=%r, load_ui=False)\nresult=1" % fs0["file"])
    fs = run(b, FILESTATE)
    t("Blender reopened the file it had before, clean", fs["file"] == fs0["file"] and not fs["dirty"], fs)
t.done()
