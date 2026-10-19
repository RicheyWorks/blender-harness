import json, os, re, subprocess, sys, time, urllib.request as u
sys.path.insert(0, r"C:\Users\730ri\projects\blender-harness"); os.chdir(r"C:\Users\730ri\projects\blender-harness")
from bharness.bus import Bus
LOG = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs", "bb_turn.log")
def log(s): open(LOG, "a", encoding="utf-8").write(time.strftime("%H:%M:%S ") + s + "\n")
b = Bus(r"C:\Users\730ri\projects\bot-team\art"); after = int(sys.argv[1]); end = time.time() + 4 * 3600; go = None
log("watching link for art-master-flex HANDOFF / referee call for blender-team, after %d" % after)
while time.time() < end and not go:
    try: j = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-turnwatch&after=%d&timeout=20" % after, timeout=30))
    except Exception: time.sleep(10); continue
    for m in j.get("messages", []):
        t = json.dumps(m.get("body")).lower(); f = m.get("from")
        if f == "art-master-flex" and "handoff" in t: go = m
        if f == "buffffff" and re.search(r"blender[- ]?(boss|team)[^.;]{0,30}\b(go|now|your turn|is up|you are up)\b", t) and "not " not in t[:80]: go = m
    after = j.get("last", after)
if not go: log("no turn within 4 h"); sys.exit(0)
log("trigger %s %s %s" % (go.get("id"), go.get("from"), json.dumps(go.get("body"))[:200]))
b.send("claim", {"text": "CLAIM editor-slot blender-team (after %s %s, 10 min): bb_turn.ps1 only = import base + missing glbs, place BlenderBoss Island (1003 placements incl. water chain) in own sublevel /Game/BlenderBoss/Maps/BlenderBossIsland, save own sublevel, no Play, tidy panels." % (go.get("from"), go.get("id"))})
b.send("note", {"asset": "-", "text": "DOING editor-slot blender-team: placing BlenderBoss Island."})
t0 = time.time()
r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", r"C:\Users\730ri\projects\Daedalus2\tools\islands\blenderboss\bb_turn.ps1", "-Timeout", "540"],
                   capture_output=True, text=True, creationflags=0x08000000, timeout=660)
out = (r.stdout or "") + (r.stderr or ""); log("exit %s %.0fs\n%s" % (r.returncode, time.time() - t0, out[-3000:]))
res = re.findall(r"placed=\d+/\d+[^\n\"]*", out); summ = res[-1] if res else ("exit %s" % r.returncode)
ok = "PASS" in summ
b.send("note", {"asset": "-", "text": "%s island:BlenderBoss editor turn (%.0f s): %s. Own sublevel saved, Play not used, panels tidied." % ("DONE" if ok else "BLOCKED", time.time() - t0, summ[:200])})
b.send("note", {"asset": "-", "text": "HANDOFF editor-slot blender-team -> 2hot2trot (next in the turn ledger)."})
log("posted ok=%s" % ok)
