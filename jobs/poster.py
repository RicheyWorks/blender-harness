"""Real-progress poster (not a heartbeat): every 10 min posts the newest REAL work lines from worklog.jsonl
(written by our job scripts with numbers) plus the live tail of any running headless Blender job log. Posts nothing fake:
if there is no new work line and no running job, it posts nothing and logs 'idle' locally so the agent can see it."""
import json, os, re, sys, time, glob
sys.path.insert(0, r"C:\\Users\\730ri\\projects\\blender-harness"); os.chdir(r"C:\\Users\\730ri\\projects\\blender-harness")
from bharness.bus import Bus
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); WL = os.path.join(J, "worklog.jsonl"); ME = os.path.join(J, "poster.log")
b = Bus(r"C:\\Users\\730ri\\projects\\bot-team\\art"); pos = os.path.getsize(WL) if os.path.exists(WL) else 0
end = time.time() + float(sys.argv[1] if len(sys.argv) > 1 else 6) * 3600; EVERY = 540
def log(s): open(ME, "a", encoding="utf-8").write(time.strftime("%H:%M:%S ") + s + "\n")
def running_job():
    logs = sorted(glob.glob(os.path.join(J, "*.log")), key=os.path.getmtime)[-6:]
    for p in reversed(logs):
        if time.time() - os.path.getmtime(p) < 90 and os.path.basename(p) not in ("poster.log", "heartbeat.log", "bb_makeup.log"):
            tail = open(p, encoding="utf-8", errors="ignore").read()[-6000:]
            n = len(re.findall(r'^\{"asset": "', tail, re.M)); last = re.findall(r'"asset": "([^"]+)"', tail)
            return "%s: %d assets built in the last chunk, latest %s" % (os.path.basename(p)[:-4], n, last[-1] if last else "-")
log("armed")
while time.time() < end:
    lines = []
    if os.path.exists(WL) and os.path.getsize(WL) > pos:
        with open(WL, encoding="utf-8") as f: f.seek(pos); lines = [json.loads(l) for l in f if l.strip()]; pos = f.tell()
    job = running_job()
    if lines or job:
        done = [l["text"] for l in lines if l.get("kind") == "DONE"]; doing = [l["text"] for l in lines if l.get("kind") != "DONE"]
        txt = ("DONE blender-team: " + " | ".join(done[-3:])) if done else ("DOING blender-team: " + (" | ".join(doing[-2:]) or ""))
        if job and not done: txt += (" | " if doing else "") + "running " + job
        b.send("note", {"text": txt[:600]}, to="*"); log("posted " + txt[:200])
    else: log("idle: no new work line and no running job; nothing posted")
    time.sleep(EVERY)
