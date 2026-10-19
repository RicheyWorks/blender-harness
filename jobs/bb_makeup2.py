import json, os, re, shutil, subprocess, sys, time, urllib.request as u
sys.path.insert(0, r"C:\Users\730ri\projects\blender-harness"); os.chdir(r"C:\Users\730ri\projects\blender-harness")
from bharness.bus import Bus
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); LOG = os.path.join(J, "bb_makeup.log")
def log(s): open(LOG, "a", encoding="utf-8").write(time.strftime("%H:%M:%S ") + s + "\n")
b = Bus(r"C:\Users\730ri\projects\bot-team\art"); after = int(sys.argv[1]); end = time.time() + 6 * 3600; go = None; nxt = "prometheus"
BB = r"blender[- ]?(team|boss)"
T_GO = time.mktime(time.strptime(time.strftime("%Y-%m-%d ") + "20:22:30", "%Y-%m-%d %H:%M:%S")); ue_claimed = False
log("armed after=%d timer=20:22:30" % after)
while time.time() < end and not go:
    if time.time() >= T_GO and not ue_claimed:
        go = {"id": "timer-20:22:30", "from": "timer", "body": "no unreal-team CLAIM after 23529"}; break
    try: j = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-makeup2&after=%d&timeout=5" % after, timeout=15))
    except Exception: time.sleep(3); continue
    for m in j.get("messages", []):
        f = m.get("from"); t = json.dumps(m.get("body")).lower(); ty = str(m.get("type", "")).lower()
        if f == "blender-team": continue
        if f == "unreal-team" and (ty == "claim" or "claim editor-slot" in t): ue_claimed = True; log("unreal-team claimed at %s" % m.get("id"))
        if re.search(r"handoff\W{0,8}(->|to)\W{0,4}" + BB, t) or re.match(r'"?\W*handoff\W{1,4}' + BB, t): go = m
        if f in ("buffffff", "2hot2trot") and re.search(BB + r"('s)? (make-up )?turn (is )?(now )?open|it'?s (now )?" + BB + r"'?s? turn|" + BB + r",? (it'?s )?your turn", t): go = m
        if go: break
    after = j.get("last", after)
if not go: log("no turn in 6 h"); sys.exit(0)
import traceback
try:
    t0 = time.time(); log("TRIGGER %s %s: %s | next=%s" % (go.get("id"), go.get("from"), json.dumps(go.get("body"))[:300], nxt))
    b.send("note", {"text": "CLAIM editor-slot blender-team (make-up turn, trigger #%s, 10 min hard stop): BlenderBoss Island import (time-boxed) + place 1003 incl. water chain at -6000000,6000000,0 in /Game/BlenderBoss/Maps/BlenderBossIsland, save sublevel + DaedalusWorld, Play off, tidy, HANDOFF %s." % (go.get("id"), nxt)}, to="*")
    budget = 540 - (time.time() - t0)
    os.environ["BB_IMPORT_S"] = str(int(max(60, budget - 300)))
    out, rc = "", None
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", r"C:\Users\730ri\projects\Daedalus2\tools\islands\blenderboss\bb_turn.ps1", "-Timeout", str(int(budget - 30))],
                           capture_output=True, text=True, creationflags=0x08000000, timeout=budget, env=os.environ)
        out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
    except subprocess.TimeoutExpired as e:
        out = "TIMEOUT " + str((e.stdout or b"")[-2000:]); subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", r"C:\Users\730ri\projects\studio-screen-connector\tidy.ps1", "-Once"], creationflags=0x08000000, timeout=20)
    log("rc %s %.0fs\n%s" % (rc, time.time() - t0, out[-5000:]))
    m = re.findall(r'"placed": (\d+), "want": (\d+)', out); imp = re.findall(r'"imported": (\d+)', out); ok = '"ok": true' in out
    summ = ("placed %s/%s, imported %s, base %s" % (m[-1][0], m[-1][1], imp[-1] if imp else "?", "ok" if '"base": true' in out else "MISSING")) if m else "no result from bridge (partial/timeout)"
    b.send("note", {"text": "%s island:BlenderBoss make-up turn %s-%s: %s. Play off, tidy run%s." % ("DONE" if ok else "PARTIAL", time.strftime("%H:%M", time.localtime(t0)), time.strftime("%H:%M"), summ, ", sublevel + DaedalusWorld saved" if m else "")}, to="*")
    b.send("note", {"text": "HANDOFF %s: blender-team make-up turn released." % nxt}, to="*")
    log("handoff %s at %.0fs; %s" % (nxt, time.time() - t0, summ))
    shot = r"C:\Users\730ri\projects\bot-team\shots\blenderboss\ue_island.png"
    for _ in range(30):
        if os.path.exists(shot): log("shot ok"); break
        time.sleep(2)

except Exception:
    log('CRASH ' + traceback.format_exc())
