"""Finish rows whose .blend saved but READY was blocked by a stale dirty flag: open each .blend, judge + turntable + save + READY."""
import bpy, sys, os, json
R = r"C:\Users\730ri\projects\blender-harness"; sys.path.insert(0, R); os.chdir(R)
from bharness.local import LocalBridge
from bharness.context import Context
from bharness.plugins.queue import QueuePlugin
names = sys.argv[sys.argv.index("--") + 1:]
for n in names:
    bpy.ops.wm.open_mainfile(filepath=os.path.join(r"C:\Users\730ri\projects\bot-team\art\Prop", n + ".blend"))
    ctx = Context(bridge=LocalBridge()); q = QueuePlugin(ctx)
    try: r = q.ready(n, turntable=4)
    except Exception as e: r = {"error": repr(e)[:300]}
    print(json.dumps({"asset": n, "ready": r.get("ready", r.get("status")), "res": str(r)[:300]}), flush=True)
