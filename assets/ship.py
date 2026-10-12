# SPDX-License-Identifier: MIT
"""Ship over the Unreal team's team link, one asset at a time (that's the pacing): send asset.ready, then wait for
that asset's asset.shipped / asset.rejected / asset.blocked before the next one. Unreal and Blender are never
asked to do two things at once (the watcher exports from Blender, so we never build while it ships).

  python -m assets.ship backlog [--limit N]   every built asset not yet SHIPPED (exports a missing .glb first)
  python -m assets.ship one <Asset>
Results: art\\bus\\shipments.jsonl (one line per attempt) and jobs\\<Asset>.json last_result."""
import glob, json, os, sys, time
from bharness.context import Context
from bharness.bus import Bus
from bharness import handoff
from bharness.plugins.queue import QueuePlugin, state
from bharness.plugins.export import export_glb
from bharness.plugins.bridge import run

KINDS = ("Tool", "Wpn", "Item", "Prop", "Mob", "Bld", "Veh", "Sky")
FINAL = ("asset.shipped", "asset.rejected")


def log(ctx, rec):
    p = os.path.join(ctx.art, "bus", "shipments.jsonl"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")


def ship_one(ctx, bus, asset, timeout=120, gap=1.0):
    try: handoff.job(asset, ctx.art)
    except FileNotFoundError: pass
    t0 = time.time(); mid = bus.send("asset.ready", {"asset": asset})
    rec = {"asset": asset, "ready_id": mid, "at": handoff.now(), "result": "timeout"}
    blocked = None
    while time.time() - t0 < timeout:
        for m in bus.wait(min(25, max(1, timeout - (time.time() - t0)))):
            b = m.get("body") or {}
            if b.get("asset") != asset: continue
            if m["type"] in FINAL:
                rec.update(result=m["type"].split(".")[1], detail=b.get("result") or b.get("why") or b.get("detail"), id=m["id"],
                           seconds=round(time.time() - t0, 1))
                handoff.fold({"asset": asset, "event": rec["result"], "at": m.get("ts"), "why": b.get("why"), "result": b.get("result")}, ctx.art)
                log(ctx, rec); time.sleep(gap); return rec
            if m["type"] in ("asset.blocked", "asset.waiting"): blocked = b.get("why") or m["type"]
            if m["type"] == "asset.added":   # Unreal queued it (e.g. waiting for Play mode to end): don't block the build line
                rec.update(result="queued", id=m["id"], seconds=round(time.time() - t0, 1)); log(ctx, rec); time.sleep(gap); return rec
        if mid is None and bus.health().get("ok"):   # broker came back: our queued ready was replayed
            mid = "replayed"
    if blocked: rec.update(result="blocked", detail=blocked)
    log(ctx, rec); return rec


def shipped_set(ctx):
    q = QueuePlugin(ctx)
    return {r["asset"] for r in q.rows() if state(r["status"]) == "SHIPPED"}


def ensure_glb(ctx, asset):
    gl = os.path.join(ctx.art, "glb", asset + ".glb")
    if os.path.exists(gl): return None
    q = QueuePlugin(ctx); q.open(asset)
    g = export_glb(ctx, asset)
    run(ctx.bridge, "import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\nresult=1")
    return [c["check"] for c in g["checks"] if not c["ok"]]


def backlog(ctx, limit=None):
    done = shipped_set(ctx); bus = Bus(ctx.art); out = {"shipped": 0, "rejected": [], "other": []}
    names = sorted(os.path.splitext(os.path.basename(p))[0] for k in KINDS for p in glob.glob(os.path.join(ctx.art, k, "*.blend")))
    names = [n for n in names if n not in done and not n.startswith("Prop_PipelineCheck")]
    for i, n in enumerate(names[:limit] if limit else names):
        fails = ensure_glb(ctx, n)
        if fails:
            out["other"].append((n, "glb " + ",".join(fails))); continue
        r = ship_one(ctx, bus, n)
        print(json.dumps(r), flush=True)
        if r["result"] == "shipped": out["shipped"] += 1
        elif r["result"] == "rejected": out["rejected"].append((n, r.get("detail")))
        else: out["other"].append((n, r["result"]))
    handoff.status("shipping-backlog-done", "", "%d shipped" % out["shipped"], art=ctx.art)
    return out


def main(a=sys.argv[1:]):
    ctx = Context()
    if a[0] == "one": print(json.dumps(ship_one(ctx, Bus(ctx.art), a[1])))
    else:
        lim = int(a[a.index("--limit") + 1]) if "--limit" in a else None
        print(json.dumps({"backlog": backlog(ctx, lim)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
