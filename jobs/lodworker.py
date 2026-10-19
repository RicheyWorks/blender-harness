"""Real-work filler until 06:00 PT: LOD1 for catalog glbs that have none yet, 40 per cycle, hidden Blender, one job at a time.
Pauses while our editor turn runs or free RAM < 1.5 GB. Writes DOING/DONE lines with real counts to worklog (the poster posts them)."""
import os, sys, subprocess, time, json
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); G = r"C:\Users\730ri\projects\bot-team\art\glb"
BL = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"; END = time.mktime(time.strptime(time.strftime("%Y-%m-%d ") + "06:00:00", "%Y-%m-%d %H:%M:%S"))
if END < time.time() - 3600: END += 86400
def wl(k, t): subprocess.call([sys.executable, os.path.join(J, "wl.py"), k, t])
def free_mb():
    o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"], capture_output=True, text=True, creationflags=0x08000000).stdout
    return int("".join(c for c in o if c.isdigit()) or 0) // 1024
def turn_active():
    try: t = open(os.path.join(J, "bb_next.log"), encoding="utf-8").read()
    except Exception: return False
    return t.count("TRIGGER") > t.count("exit turns")
SKIP = ("Prop_Island_", "_LOD1")
tot = 0
while time.time() < END:
    if turn_active() or free_mb() < 1500: time.sleep(30); continue
    failed = set(open(os.path.join(J, "lodfail.txt")).read().split()) if os.path.exists(os.path.join(J, "lodfail.txt")) else set()
    have = set(os.listdir(G)); todo = sorted(f[:-4] for f in have if f.endswith(".glb") and not any(s in f for s in SKIP) and f[:-4] + "_LOD1.glb" not in have and f[:-4] not in failed)
    if not todo: wl("DONE", "catalog LOD1 complete: no glb left without _LOD1"); break
    batch = todo[:120]
    wl("DOING", "catalog LOD1: batch of %d (%s .. %s), %d catalog glbs still without LOD1" % (len(batch), batch[0], batch[-1], len(todo)))
    try: out = subprocess.run([BL, "-b", "--factory-startup", "--python", os.path.join(J, "lodglb.py"), "--", G] + batch, capture_output=True, text=True, timeout=900, creationflags=0x08000000).stdout
    except subprocess.TimeoutExpired: out = ""
    rs = [json.loads(l[8:]) for l in out.splitlines() if l.startswith("LODJSON ")]
    ok = [r for r in rs if "error" not in r]; f0 = sum(r["faces"] for r in ok); f1 = sum(r["lod1"] for r in ok); tot += len(ok)
    bad = [r["asset"] for r in rs if "error" in r]
    for n in batch:   # never retry forever: mark failures with an empty marker so the queue moves on
        if not os.path.exists(os.path.join(G, n + "_LOD1.glb")): open(os.path.join(J, "lodfail.txt"), "a").write(n + "\n")
    open(os.path.join(J, "lodworker.jsonl"), "a").write(json.dumps({"at": time.strftime("%H:%M:%S"), "ok": len(ok), "bad": bad}) + "\n")
    wl("DONE", "catalog LOD1 batch: %d/%d built, faces %d -> %d (%.0f%%)%s; %d total this session, %d left" % (len(ok), len(batch), f0, f1, 100.0 * f1 / max(f0, 1), (", failed: " + ", ".join(bad[:4])) if bad else "", tot, len(todo) - len(ok)))
    if not ok: time.sleep(600)
    time.sleep(420)
