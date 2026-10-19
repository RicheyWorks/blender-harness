"""Round-2 + make-up editor-turn watcher (blender-team). Strict triggers only, no timer:
 - HANDOFF -> blender-team/boss (e.g. art-master-flex finishing its round-2 slot), or a message starting 'HANDOFF blender...'
 - referee (buffffff / 2hot2trot): "BB's (make-up) turn (is) open" | "it's BB's turn" | "BB, your turn" (BB = blender team/boss)
Before claiming we prove the editor is alive: UnrealEditor process Responding AND a 1+1 execute_python round-trip within 25 s.
If not alive -> STANDING DOWN + HANDOFF next immediately (never click dialogs, kill or launch an editor). Handles up to 2 turns, 8 h."""
import json, os, re, subprocess, sys, time, traceback, urllib.request as u
R = r"C:\Users\730ri\projects\blender-harness"; sys.path.insert(0, R); os.chdir(R)
from bharness.bus import Bus
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); LOG = os.path.join(J, "bb_round2.log")
SEND = r"C:\Users\730ri\projects\Daedalus2-pcg-ecology\engines\unreal\pcg-ecology\ue_send.py"
TURN = r"C:\Users\730ri\projects\Daedalus2\tools\islands\blenderboss\bb_turn.ps1"
TIDY = r"C:\Users\730ri\projects\studio-screen-connector\tidy.ps1"
def log(s): open(LOG, "a", encoding="utf-8").write(time.strftime("%H:%M:%S ") + s + "\n")
def wl(k, t): subprocess.call([sys.executable, os.path.join(J, "wl.py"), k, t])
b = Bus(r"C:\Users\730ri\projects\bot-team\art"); after = int(sys.argv[1]); end = time.time() + 8 * 3600; turns = 0
BB = r"blender[- ]?(team|boss)|\bbb\b"
NXT = re.compile(r"next[: ]+(?:is )?@?([a-z0-9][a-z0-9-]{2,30})")
def trig(m):
    f = m.get("from"); t = json.dumps(m.get("body")).lower()
    if f == "blender-team": return False
    if re.search(r"handoff\W{0,8}(->|to)\W{0,4}(" + BB + ")", t) or re.match(r'"?\W*(\{"text": ")?handoff\W{1,4}(' + BB + ")", t): return True
    if f in ("buffffff", "2hot2trot") and re.search(r"(" + BB + r")('s)? (round[- ]?2 |make-up )?turn (is )?(now )?open|it'?s (now )?(" + BB + r")'?s? turn|(" + BB + r"),? (it'?s )?your turn", t): return True
    return False
def alive():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "$p=gps UnrealEditor -ea 0; if($p){$p[0].Responding}else{'none'}"], capture_output=True, text=True, creationflags=0x08000000, timeout=20).stdout.strip()
    if r != "True": return False, "UnrealEditor process: %s" % (r or "none")
    pf = os.path.join(J, "bbping.py"); open(pf, "w").write('print("BBPING", 1 + 1)\n')
    try: out = subprocess.run([sys.executable, SEND, pf, "25"], capture_output=True, text=True, timeout=40, creationflags=0x08000000).stdout
    except subprocess.TimeoutExpired: return False, "1+1 execute_python round-trip timed out (40 s)"
    return ("BBPING 2" in out or '"ok": true' in out.lower()), "ping reply: " + out[-200:].replace("\n", " ")
log("armed after=%d" % after)
while time.time() < end and turns < 2:
    try: j = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-round2&after=%d&timeout=20" % after, timeout=30))
    except Exception: time.sleep(5); continue
    go = None; nxt = "prometheus"
    for m in j.get("messages", []):
        mm = NXT.search(json.dumps(m.get("body")).lower())
        if trig(m): go = m; nxt = mm.group(1) if mm and "blender" not in mm.group(1) else nxt; break
    after = j.get("last", after)
    if not go: continue
    turns += 1; t0 = time.time()
    try:
        log("TRIGGER %s %s: %s next=%s" % (go.get("id"), go.get("from"), json.dumps(go.get("body"))[:300], nxt))
        ok, why = alive(); log("alive=%s %s" % (ok, why))
        if not ok:
            b.send("note", {"text": "STANDING DOWN blender-team (trigger #%s): editor not responsive (%s). Not touching it (no dialog clicks/kill/relaunch). HANDOFF %s." % (go.get("id"), why[:160], nxt)}, to="*")
            b.send("note", {"text": "HANDOFF %s: blender-team slot released (editor unresponsive)." % nxt}, to="*")
            wl("DONE", "editor turn #%d: stood down, editor unresponsive (%s); handed off to %s" % (turns, why[:80], nxt)); continue
        b.send("note", {"text": "CLAIM editor-slot blender-team (trigger #%s, editor ping ok, 10 min hard stop): BlenderBoss Island import + place 1003 at -6000000,6000000,0 in /Game/BlenderBoss/Maps/BlenderBossIsland, save sublevel + DaedalusWorld, Play off, tidy, HANDOFF %s." % (go.get("id"), nxt)}, to="*")
        budget = 540 - (time.time() - t0); os.environ["BB_IMPORT_S"] = str(int(max(60, budget - 300))); out, rc = "", None
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", TURN, "-Timeout", str(int(budget - 30))], capture_output=True, text=True, creationflags=0x08000000, timeout=budget, env=os.environ)
            out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
        except subprocess.TimeoutExpired as e:
            out = "TIMEOUT"; subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", TIDY, "-Once"], creationflags=0x08000000, timeout=20)
        log("rc %s %.0fs\n%s" % (rc, time.time() - t0, out[-5000:]))
        m = re.findall(r'"placed": (\d+), "want": (\d+)', out); imp = re.findall(r'"imported": (\d+)', out); good = '"ok": true' in out
        summ = ("placed %s/%s, imported %s" % (m[-1][0], m[-1][1], imp[-1] if imp else "?")) if m else "no result from bridge (partial/timeout)"
        b.send("note", {"text": "%s island:BlenderBoss editor turn %s-%s: %s. Play off, tidy run%s." % ("DONE" if good else "PARTIAL", time.strftime("%H:%M", time.localtime(t0)), time.strftime("%H:%M"), summ, ", sublevel + DaedalusWorld saved" if m else "")}, to="*")
        b.send("note", {"text": "HANDOFF %s: blender-team editor turn released." % nxt}, to="*")
        wl("DONE", "editor turn #%d: %s; handed off to %s in %.0fs" % (turns, summ, nxt, time.time() - t0))
    except Exception: log("CRASH " + traceback.format_exc())
log("exit turns=%d" % turns)
