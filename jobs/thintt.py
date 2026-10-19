"""Turntable-only re-render for thin BBIsle props (no rebuild, no re-ship): open each art\\Prop\\<asset>.blend and run the
patched render.py turntable (45-deg offset for thin props). blender -b --factory-startup --python thintt.py"""
import bpy, sys, os, json, time
R = r"C:\Users\730ri\projects\blender-harness"; sys.path.insert(0, R); os.chdir(R)
from assets.bbisle_thin import SPECS
from bharness.plugins import render as RP
ART = r"C:\Users\730ri\projects\bot-team\art"; ok = 0; bad = []
for s in SPECS:
    n = s["asset"]; f = os.path.join(ART, "Prop", n + ".blend")
    try:
        bpy.ops.wm.open_mainfile(filepath=f)
        g = {}; exec(RP.TURNTABLE % {"name": n, "n": 4, "size": 768, "folder": os.path.join(ART, "promo", n), "bg": "E9E4DA"}, g)
        ok += 1; print(json.dumps({"asset": n, "frames": len(g.get("result", []))}), flush=True)
    except Exception as e: bad.append(n); print(json.dumps({"asset": n, "error": repr(e)[:200]}), flush=True)
print("TT_END", ok, len(SPECS), bad[:10], flush=True)
