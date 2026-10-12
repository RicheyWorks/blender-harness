# SPDX-License-Identifier: MIT
"""Self-ship (Richey's permission, 2026-10-12): import the Blender team's saved READY .glb files into the Unreal editor that is
ALREADY open, through its bridge on 9877. It never launches an editor and never stops a Play session.
Collision rules with the Unreal team's watcher:
  * a note on the team link before (exact rows) and after (results);
  * each row goes READY -> 'SHIPPING (Blender team)' (atomic, re-read compare write) before import, so the watcher skips it;
  * -> 'SHIPPED (tris, size)' in the watcher's own format only when Unreal's import matches the saved .glb, else back to READY;
  * row 619-style stuck rows (SHIPPING by the watcher) are never touched.
Uses the Unreal team's asset_pipeline as a read-only library (sides.UNREAL_IMPORT, wire.call): no edits to their code.
Usage: python -m bharness.selfship [--max=20] [--dry]"""
import json, os, sys, time
from bharness.context import Context
from bharness.bus import Bus
from bharness import glb as G
from bharness.plugins.queue import QueuePlugin, state, kind_of

AP = r"C:\Users\730ri\projects\Daedalus2\connectors\claude-asset-pipeline"
sys.path.insert(0, AP)
from asset_pipeline import sides, wire   # noqa: E402  (read-only use)

PLAYING = "import unreal\nresult = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_game_world() is not None\n"
LOG = os.path.join(Context().art, "bus", "selfship.jsonl")

def log(rec):
    with open(LOG, "a", encoding="utf-8") as f: f.write(json.dumps(rec) + "\n")

def editor_state():
    if not wire.reachable(wire.UNREAL): return "no editor bridge on 9877 (we never launch one)"
    try:
        if wire.call(wire.UNREAL, "execute_python", side="Unreal", timeout=20, code=PLAYING)["result"]:
            return "Unreal is in Play mode (never stopped by us)"
    except Exception as e:
        return "Unreal busy (%s)" % type(e).__name__
    return ""

def ship(ctx, q, asset):
    gl = os.path.join(ctx.art, "glb", asset + ".glb"); s = G.summarize(G.read_json(gl))
    ft = sum(m["triangles"] for m in s["meshes"]); fdim = max(max(m["dims"]) for m in s["meshes"])
    dest = "/Game/Daedalus/Art/%s/%s" % (kind_of(asset), asset)
    q._write(asset, lambda r: state(r["status"]) == "READY", "SHIPPING (Blender team)")
    t0 = time.time()
    try:
        made = wire.call(wire.UNREAL, "execute_python", side="Unreal", timeout=300,
                         code=sides.script(sides.UNREAL_IMPORT, path=gl, dest=dest, save=True))["result"]
        ut = sum(m["triangles"] for m in made["meshes"]); nm = len(made["meshes"])
        ok = nm == len(s["meshes"]) and ut == ft
        why = "" if ok else "Unreal %d meshes/%d tris vs file %d/%d" % (nm, ut, len(s["meshes"]), ft)
    except Exception as e:
        ok, why, made = False, "import error: " + repr(e)[:200], {}
    if ok:
        q._write(asset, lambda r: r["status"].startswith("SHIPPING (Blender team)"), "SHIPPED (%d tris, %.2f m)" % (ft, fdim), "self-shipped by the Blender team")
    else:
        q._write(asset, lambda r: r["status"].startswith("SHIPPING (Blender team)"), "READY", "self-ship failed: " + why)
    rec = {"asset": asset, "ok": ok, "why": why, "dest": dest, "tris": ft, "s": round(time.time() - t0, 1), "at": time.strftime("%H:%M:%S")}
    log(rec); return rec

def main(a=sys.argv[1:]):
    mx = next((int(x.split("=")[1]) for x in a if x.startswith("--max=")), 20)
    ctx = Context(); q = QueuePlugin(ctx); bus = Bus(ctx.art)
    rows = [r["asset"] for r in q.rows() if state(r["status"]) == "READY"
            and os.path.exists(os.path.join(ctx.art, "glb", r["asset"] + ".glb"))][:mx]
    why = editor_state()
    if why or not rows:
        print(json.dumps({"selfship": "not now", "why": why or "no READY rows"})); return 0
    if "--dry" in a: print(json.dumps({"would_ship": rows})); return 0
    bus.send("note", {"asset": "-", "selfship": "start", "rows": rows,
                      "text": "Blender team SELF-SHIP starting (Richey's permission): importing these %d READY rows into the open editor via 9877, "
                              "each marked 'SHIPPING (Blender team)' first so your watcher skips them: %s" % (len(rows), ", ".join(rows))})
    out = []
    for n in rows:
        if editor_state(): break   # Play started or editor went away: stop at once
        out.append(ship(ctx, q, n))
    good = [r["asset"] for r in out if r["ok"]]; bad = [(r["asset"], r["why"]) for r in out if not r["ok"]]
    bus.send("note", {"asset": "-", "selfship": "done", "shipped": good, "failed": bad,
                      "text": "Blender team SELF-SHIP done: %d shipped under /Game/Daedalus/Art/<Kind>/<Asset>, %d failed (rows back to READY): %s"
                              % (len(good), len(bad), json.dumps(bad)[:600])})
    hook = os.environ.get("DAEDALUS_POST_JOB_HOOK", r"C:\Users\730ri\projects\bot-team\hooks\post-job.ps1")
    if os.path.exists(hook):   # 2Hot2Trot's UI cleanup (Content Browser / Message Log) when published
        import subprocess
        subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", hook, "-Job", "selfship"],
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), timeout=120)
    print(json.dumps({"shipped": len(good), "failed": bad})); return 0



def loop(minutes=120, grace=60, batch=20):
    """Hidden watchdog: when the editor is free (not playing) and the watcher hasn't reduced READY within `grace` s, self-ship a batch."""
    ctx = Context(); q = QueuePlugin(ctx); end = time.time() + minutes * 60
    ready = lambda: sum(state(r["status"]) == "READY" for r in q.rows())
    while time.time() < end:
        if editor_state(): time.sleep(15); continue
        n0 = ready(); time.sleep(grace)
        if ready() < n0: continue          # the watcher is draining: let it
        main(["--max=%d" % batch])
    return 0


if __name__ == "__main__":
    sys.exit(loop() if "--loop" in sys.argv else main())
