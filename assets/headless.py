# SPDX-License-Identifier: MIT
"""Build ahead in a headless Blender, then send asset.ready in batches without blocking.
Run: blender -b --factory-startup --python assets/headless.py -- <repo> <module> [groups...] [--batch=10] [--turntable=4]
Does not touch the GUI Blender (9876) that the watcher uses. Skips only the asset the watcher is shipping.
Results (shipped/rejected) come back over the link and are recorded by assets.collect, not waited on here."""
import json, os, sys, time
a = sys.argv[sys.argv.index("--") + 1:]
sys.path.insert(0, a[0])
from bharness.local import LocalBridge
from bharness.context import Context
from bharness.bus import Bus
from assets import runner
import importlib

def main(a):
    mod = importlib.import_module(a[1]); groups = [g for g in a[2:] if not g.startswith("--")]
    opt = dict(x[2:].split("=") for x in a[2:] if x.startswith("--") and "=" in x)
    batch, tt = int(opt.get("batch", 10)), int(opt.get("turntable", 4))
    ctx = Context(bridge=LocalBridge()); bus = Bus(ctx.art); pend = []; t0 = time.time(); built = 0
    log = open(os.path.join(ctx.art, "bus", "headless.jsonl"), "a", encoding="utf-8")
    def flush():
        ids = [bus.send("asset.ready", {"asset": n, "batch": len(pend)}) for n in pend]
        rec = {"at": time.strftime("%H:%M:%S"), "sent": list(pend), "ids": ids, "built": built, "min": round((time.time() - t0) / 60, 2)}
        log.write(json.dumps(rec) + "\n"); log.flush(); print(json.dumps(rec), flush=True); pend.clear()
    for g in groups:
        for s in (mod.GROUPS[g] if g in mod.GROUPS else []):
            try: rec = runner.build_one(ctx, s, turntable=tt)
            except Exception as e: rec = {"asset": s["asset"], "error": repr(e)[:300]}
            ok = not (rec.get("fails") or rec.get("glb_fails") or rec.get("error") or rec.get("skipped"))
            print(json.dumps({k: rec.get(k) for k in ("asset", "tris", "skipped", "error", "fails")}), flush=True)
            if ok:
                built += 1; pend.append(rec["asset"])
                try:
                    from bharness import handoff; handoff.job(rec["asset"], ctx.art)
                except Exception: pass
                if len(pend) >= batch: flush()
    if pend: flush()
    m = (time.time() - t0) / 60
    print(json.dumps({"done": built, "minutes": round(m, 2), "per_min": round(built / m, 2) if m else None}), flush=True)

main(a)
