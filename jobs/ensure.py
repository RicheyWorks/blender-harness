"""Supervisor (run every 2 min by Task Scheduler 'BB_Ensure', independent of any shell session): restarts the make-up
watcher and the real-progress poster if they died. Watcher is NOT restarted once it has fired (TRIGGER/exit in its log)."""
import os, sys, subprocess, json, time, urllib.request as u
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); PY = sys.executable.replace("pythonw.exe", "python.exe")
def log(s): open(os.path.join(J, "ensure.log"), "a").write(time.strftime("%H:%M:%S ") + s + "\n")
procs = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | % CommandLine"], capture_output=True, text=True, creationflags=0x08000000).stdout
def start(args, out):
    subprocess.Popen(["cmd", "/c", " ".join([PY] + args) + " > " + out + " 2>&1"], creationflags=0x08000000 | 0x00000008 | 0x00000200, cwd=J)
end = os.path.join(J, "supervise_until.txt")
if os.path.exists(end) and time.time() > float(open(end).read()): sys.exit(0)
wlog = os.path.join(J, "bb_next.log"); fired = os.path.exists(wlog) and ("TRIGGER" in open(wlog, encoding="utf-8").read())
if "bb_next.py" not in procs and not fired:
    try: last = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=bb-ensure&after=999999999&timeout=1", timeout=10)).get("last")
    except Exception: last = None
    st = os.path.join(J, "bb_next.after")
    a = int(open(st).read()) if os.path.exists(st) else (last or 0)
    start([os.path.join(J, "bb_next.py"), str(a)], os.path.join(J, "bb_next.out")); log("restarted bb_next after=%s" % a)
if "poster.py" not in procs:
    start([os.path.join(J, "poster.py"), "3"], os.path.join(J, "poster.out")); log("restarted poster")
if "lodworker.py" not in procs:
    start([os.path.join(J, "lodworker.py")], os.path.join(J, "lodworker.out")); log("restarted lodworker")
