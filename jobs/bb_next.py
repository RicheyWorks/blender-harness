"""Round-2 + make-up editor-turn watcher (blender-team). Strict triggers only, no timer:
 - HANDOFF -> blender-team/boss (e.g. art-master-flex finishing its round-2 slot), or a message starting 'HANDOFF blender...'
 - referee (buffffff / 2hot2trot): "BB's (make-up) turn (is) open" | "it's BB's turn" | "BB, your turn" (BB = blender team/boss)
Before claiming we prove the editor is alive: UnrealEditor process Responding AND a 1+1 execute_python round-trip within 25 s.
If not alive -> STANDING DOWN + HANDOFF next immediately (never click dialogs, kill or launch an editor). Handles up to 2 turns, 8 h."""
import json, os, re, subprocess, sys, time, traceback, urllib.request as u
R = r"C:\Users\730ri\projects\blender-harness"; sys.path.insert(0, R); os.chdir(R)
from bharness.bus import Bus
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); LOG = os.path.join(J, "bb_next.log")
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
    if f in ("buffffff", "2hot2trot") and re.search(r"@?blender[- ]?(team|boss):? your (round[- ]?\d+ )?(make-up )?(editor )?turn is (now )?open", t): return True
    if f in ("buffffff", "2hot2trot") and re.search(r"now open:? @?blender[- ]?(team|boss)\b", t): return True   # referee 27078 phrasing (missed 01:37)
    return False
def alive():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "$p=gps UnrealEditor -ea 0; if($p){$p[0].Responding}else{'none'}"], capture_output=True, text=True, creationflags=0x08000000, timeout=20).stdout.strip()
    if r == "False": return False, "UnrealEditor process not responding (hung window)"   # "none" = not visible from this session (seen 21:23): rely on the ping
    pf = os.path.join(J, "bbping.py"); open(pf, "w").write('print("BBPING", 1 + 1)\n')
    try: out = subprocess.run([sys.executable, SEND, pf, "25"], capture_output=True, text=True, timeout=40, creationflags=0x08000000).stdout
    except subprocess.TimeoutExpired: return False, "1+1 execute_python round-trip timed out (40 s)"
    return ("BBPING 2" in out or '"ok": true' in out.lower()), "ping reply: " + out[-200:].replace("\n", " ")
ONDECK = [None]
log("armed after=%d" % after)
while time.time() < end and turns < 1:
    try: j = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-next&after=%d&timeout=20" % after, timeout=30))
    except Exception: time.sleep(5); continue
    go = None; nxt = ONDECK[0] or "prometheus"
    for m in j.get("messages", []):   # pass 1: who is on deck after us (referee posts it next to our OPEN line)
        od = re.search(r"@([a-z0-9][a-z0-9-]{2,30}):? you are on deck", json.dumps(m.get("body")).lower())
        if m.get("from") == "buffffff" and od and "blender" not in od.group(1): ONDECK[0] = od.group(1); nxt = ONDECK[0]
    if not any(trig(m) for m in j.get("messages", [])) and j.get("messages"):
        pass
    for m in j.get("messages", []):
        mm = NXT.search(json.dumps(m.get("body")).lower())
        if trig(m): go = m; nxt = mm.group(1) if mm and "blender" not in mm.group(1) else nxt; break
    after = j.get("last", after)
    try: open(os.path.join(J, "bb_next.after"), "w").write(str(after))   # supervisor resumes from here
    except Exception: pass
    if not go: continue
    turns += 1; t0 = time.time()
    try:
        log("TRIGGER %s %s: %s next=%s" % (go.get("id"), go.get("from"), json.dumps(go.get("body"))[:300], nxt))
        ok, why = alive(); log("alive=%s %s" % (ok, why))
        if not ok:
            b.send("note", {"text": "STANDING DOWN blender-team (trigger #%s): editor not responsive (%s). Not touching it (no dialog clicks/kill/relaunch). HANDOFF %s." % (go.get("id"), why[:160], nxt)}, to="*")
            b.send("note", {"text": "HANDOFF %s: blender-team slot released (editor unresponsive)." % nxt}, to="*")
            wl("DONE", "editor turn #%d: stood down, editor unresponsive (%s); handed off to %s" % (turns, why[:80], nxt)); continue
        open(os.path.join(J, "bb_mode.txt"), "w").write("shot")
        b.send("note", {"text": "CLAIM editor-slot blender-team (trigger #%s, editor ping ok, small task ~2 min): SceneCapture lit + base-colour check of BlenderBossIsland (flat-colour ground) and switch our sublevel to AlwaysLoaded if it is still Dynamic (PIE loading); no import, no placement. HANDOFF %s right after." % (go.get("id"), nxt)}, to="*")
        out = ""
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", TURN, "-Timeout", "150"], capture_output=True, text=True, creationflags=0x08000000, timeout=200)
            out = (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired: out = "TIMEOUT"
        finally: open(os.path.join(J, "bb_mode.txt"), "w").write("")
        log("shot turn %.0fs\n%s" % (time.time() - t0, out[-3000:]))
        o2 = out.replace('\\"', '"'); g = lambda k: (re.findall(r'"%s": ([\d.]+)' % k, o2) or [None])[-1]
        ll, lg, al, ag = g("lit_lum"), g("lit_green_pct"), g("albedo_lum"), g("albedo_green_pct")
        if ll is None: verdict = "no capture result from bridge"
        else:
            verdict = "lit capture luma %s/255 (green %s%%), base-colour capture green %s%%: %s" % (ll, lg, ag,
                "LIT, ground green" if float(ll) > 40 and float(lg) > 8 else ("ground IS green (albedo) but the world is still dark there" if float(ag) > 8 else "ground NOT green in albedo - check material import"))
        b.send("note", {"text": "DONE island:BlenderBoss editor turn %s-%s (small): SceneCapture lit check (ue_island_lit.png + ue_island_basecolor.png) - %s. Streaming: %s. Nothing imported/placed." % (time.strftime("%H:%M", time.localtime(t0)), time.strftime("%H:%M"), verdict, (re.findall(r'"streaming": "([^"]+)"', o2) or ["?"])[-1] if ll is not None else "?")}, to="*")
        try:   # refresh: the referee may have named who is on deck after we triggered
            for m in json.load(u.urlopen("http://127.0.0.1:9890/wait?me=blender-next2&after=%d&timeout=1" % max(0, int(go.get("id", 0)) - 40), timeout=15)).get("messages", []):
                od = re.search(r"@([a-z0-9][a-z0-9-]{2,30}):? you are on deck", json.dumps(m.get("body")).lower())
                if m.get("from") == "buffffff" and od and "blender" not in od.group(1): nxt = od.group(1)
        except Exception: pass
        b.send("note", {"text": "HANDOFF %s: blender-team editor turn released." % nxt}, to="*")
        wl("DONE", "editor turn: lit check - %s; handed off to %s in %.0fs" % (verdict, nxt, time.time() - t0))
    except Exception: log("CRASH " + traceback.format_exc())
log("exit turns=%d" % turns)
