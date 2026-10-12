# SPDX-License-Identifier: MIT
"""Blender team side of the real-time Blender team <-> Unreal team handoff (spec: HANDOFF-SPEC.md).

Files only. It never touches Unreal, artqueue.py, ship.py or the watcher.
  art\\jobs\\<Asset>.json      per-asset contract: Blender team writes "blender", Unreal team adds "unreal"
  art\\STATUS-blender.json     Blender team heartbeat: state, current group, n/m, last event
  art\\feed.jsonl              read only: the watcher's events (shipped / rejected / waiting / resumed)
  art\\NOTES\\*.md             read: replies from the Unreal team (anything after our last '---')
  QUEUE.md row block           written ONLY with --apply and only inside the agreed fenced block

  python -m bharness.handoff job <Asset>        write/refresh art\\jobs\\<Asset>.json from the .blend/.glb
  python -m bharness.handoff status <state> [group] [n/m]
  python -m bharness.handoff watch [seconds]    tail feed + NOTES; fold results into jobs\\*.json; print new events
  python -m bharness.handoff rows [--apply]     the fenced READY row block (dry run prints it)
  python -m bharness.handoff board              one-screen summary: rows, jobs, waiting-on, replies"""
import datetime, glob, hashlib, json, os, re, sys, time
from bharness.context import DEFAULT_ART
from bharness import glb as G

SPEC = 1
BEGIN, END = "<!-- blender-team rows: begin -->", "<!-- blender-team rows: end -->"
ROW0 = 200


def now(): return datetime.datetime.now().isoformat(timespec="seconds")
def _w(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f: json.dump(obj, f, indent=2)
    os.replace(tmp, path)   # atomic: the other side never reads half a file
def _r(path, default=None):
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError): return default


def kind(asset): return asset.split("_")[0]


def _selfcheck(s, built):
    """File-side facts the Unreal team re-checks: mesh nodes, no node scale, tris > 0, 1-3 materials per mesh.
    If the build record is given, its Blender-vs-file glb_fails must be empty too."""
    fails = []
    if not s["meshes"]: fails.append("no meshes")
    fails += ["node %s scaled" % n["name"] for n in s["nodes"] if any(abs(x - 1) > 1e-4 for x in n["scale"])]
    fails += ["mesh %s: no triangles" % m["name"] for m in s["meshes"] if not m["triangles"]]
    fails += ["mesh %s: %d materials" % (m["name"], len(m["materials"])) for m in s["meshes"] if not 1 <= len(m["materials"]) <= 3]
    fails += list((built or {}).get("glb_fails") or [])
    return {"ok": not fails, "fails": fails, "checked_at": now()}


def job(asset, art=DEFAULT_ART, built=None):
    """Write art\\jobs\\<asset>.json. The 'blender' half comes from the saved .glb (re-read, not trusted from memory)."""
    blend = os.path.join(art, kind(asset), asset + ".blend"); gl = os.path.join(art, "glb", asset + ".glb")
    if not os.path.exists(gl):
        raise FileNotFoundError(gl)
    s = G.summarize(G.read_json(gl))
    path = os.path.join(art, "jobs", asset + ".json")
    j = _r(path, {}) or {}
    j.update({"spec": SPEC, "asset": asset, "kind": kind(asset)})
    j["blender"] = {
        "blend": blend, "glb": gl, "glb_sha1": hashlib.sha1(open(gl, "rb").read()).hexdigest(),
        "tris": sum(m["triangles"] for m in s["meshes"]), "meshes": [{"name": m["name"], "tris": m["triangles"], "materials": m["materials"], "dims_m": m["dims"]} for m in s["meshes"]],
        "materials": s["materials"], "built_by": "Blender team", "built_at": now(),
        "selfcheck": _selfcheck(s, built),
        "turntable": os.path.join(art, "promo", asset)}
    j.setdefault("unreal", None)   # the Unreal team fills: shipped_at, unreal_path, unreal_tris, result
    _w(path, j)
    return path


def status(state, group="", progress="", note="", art=DEFAULT_ART):
    _w(os.path.join(art, "STATUS-blender.json"), {"spec": SPEC, "team": "Blender team", "state": state, "group": group,
       "progress": progress, "note": note, "at": now()})


def feed(art=DEFAULT_ART, since=0):
    p = os.path.join(art, "feed.jsonl")
    try:
        with open(p, encoding="utf-8") as f:
            f.seek(since); data = f.read(); pos = f.tell()
    except OSError:
        return [], since
    out = []
    for line in data.splitlines():
        try: out.append(json.loads(line))
        except ValueError: pass
    return out, pos


def fold(ev, art=DEFAULT_ART):
    """Copy a watcher result into jobs\\<asset>.json 'last_result' (the Unreal half stays theirs to write)."""
    if ev.get("event") not in ("shipped", "rejected", "blocked"): return False
    path = os.path.join(art, "jobs", ev["asset"] + ".json")
    j = _r(path)
    if j is None: return False
    j["last_result"] = {k: ev.get(k) for k in ("at", "event", "why", "detail", "result", "dest") if ev.get(k) is not None}
    rep = _r(os.path.join(art, "reports", ev["asset"] + ".json"))
    if rep and rep.get("unreal", {}).get("meshes"):
        j["last_result"]["unreal_tris"] = [m["triangles"] for m in rep["unreal"]["meshes"]]
    _w(path, j); return True


def replies(art=DEFAULT_ART):
    """Text written below our last '---' in NOTES\\*.md that isn't ours: the Unreal team's replies."""
    out = {}
    for p in glob.glob(os.path.join(art, "NOTES", "*.md")):
        if "proposed-rows" in p: continue
        t = open(p, encoding="utf-8-sig").read()
        tail = t.rsplit("\n---", 1)[-1].strip() if "\n---" in t else ""
        if tail and not tail.startswith("**From the Blender team"):
            out[os.path.basename(p)] = tail
    return out


def rows(art=DEFAULT_ART, apply=False, names=None):
    """The fenced block of READY rows at the bottom of QUEUE.md. Only judged + glb-self-checked assets (have a jobs json
    with selfcheck ok) that have no row yet. Writes only with apply=True; read-compute-reread-compare-write."""
    from bharness.plugins.queue import parse
    q = os.path.join(art, "QUEUE.md")
    txt = open(q, encoding="utf-8").read()
    head = txt.split(BEGIN)[0].rstrip("\n")
    have = {r["asset"] for r in parse(head)[0]}
    lines, n = [BEGIN], ROW0
    for p in sorted(glob.glob(os.path.join(art, "jobs", "*.json"))):
        j = _r(p) or {}
        a = j.get("asset")
        if not a or a in have or (names and a not in names): continue
        if not j.get("blender", {}).get("selfcheck", {}).get("ok", False): continue
        m = j["blender"]["meshes"]; d = max((max(x["dims_m"]) for x in m), default=0)
        lines.append("| %d | %s | %s | %.2f m | READY | Blender team batch row; %d tris; jobs\\%s.json |" % (n, a, kind(a).lower(), d, j["blender"]["tris"], a))
        n += 1
    lines.append(END)
    block = "\n".join(lines)
    if apply:
        again = open(q, encoding="utf-8").read()
        if again != txt: raise RuntimeError("QUEUE.md changed while computing; rerun")
        with open(q, "w", encoding="utf-8", newline="\n") as f: f.write(head + "\n\n" + block + "\n")
    return block, n - ROW0


def board(art=DEFAULT_ART):
    st = open(os.path.join(art, "STATUS.md"), encoding="utf-8").read().split("## Last events")[0].strip()
    jobs = glob.glob(os.path.join(art, "jobs", "*.json"))
    me = _r(os.path.join(art, "STATUS-blender.json"), {})
    rep = replies(art)
    return "%s\n\nBlender team: %s %s %s (%s)\njobs: %d\nreplies: %s" % (st, me.get("state"), me.get("group", ""), me.get("progress", ""),
           me.get("at"), len(jobs), json.dumps({k: v[:300] for k, v in rep.items()}, indent=1) if rep else "none")


def watch(seconds=50, art=DEFAULT_ART, every=5):
    state = _r(os.path.join(art, "jobs", ".watch.json"), {"pos": 0, "replies": {}})
    t0 = time.time(); out = []
    while True:
        evs, state["pos"] = feed(art, state["pos"])
        for e in evs:
            fold(e, art); out.append({"feed": e})
        for k, v in replies(art).items():
            hsh = hashlib.sha1(v.encode()).hexdigest()
            if state["replies"].get(k) != hsh:
                state["replies"][k] = hsh; out.append({"reply": k, "text": v[:2000]})
        if out or time.time() - t0 > seconds: break
        time.sleep(every)
    _w(os.path.join(art, "jobs", ".watch.json"), state)
    return out


def main(a=sys.argv[1:]):
    cmd = a[0] if a else "board"
    if cmd == "job":
        for x in a[1:]: print(job(x))
    elif cmd == "status": status(*(a[1:4] + [""] * (3 - len(a[1:4])))); print("ok")
    elif cmd == "watch":
        for e in watch(float(a[1]) if len(a) > 1 else 50): print(json.dumps(e))
    elif cmd == "rows":
        block, n = rows(apply="--apply" in a, names=[x for x in a[1:] if not x.startswith("--")] or None); print(block); print("%d rows%s" % (n, " written" if "--apply" in a else " (dry run)"))
    else: print(board())
    return 0


if __name__ == "__main__":
    sys.exit(main())
