import os, sys, subprocess, time, glob, json
R = r"C:\Users\730ri\projects\blender-harness"; os.chdir(R); J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs")
BL = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"; ART = r"C:\Users\730ri\projects\bot-team\art"
def wl(k, t): subprocess.call([sys.executable, os.path.join(J, "wl.py"), k, t])
def alive(pid): return str(pid) in subprocess.run(["tasklist", "/FI", "PID eq %d" % pid], capture_output=True, text=True).stdout
while alive(int(sys.argv[1])): time.sleep(10)
subprocess.call([sys.executable, os.path.join(J, "lod1run.py")], stdout=open(os.path.join(J, "lod1run.log"), "w"), stderr=subprocess.STDOUT)
sys.path.insert(0, R); from assets.bbisle_thin import SPECS
wl("DOING", "thin-prop turntables: re-rendering %d Fence/Sign/Banner/Arch/Scarecrow models at 45-deg offset angles" % len(SPECS))
with open(os.path.join(J, "thin.log"), "w") as f:
    subprocess.call([BL, "-b", "--factory-startup", "--python", "assets/headless.py", "--", R, "assets.bbisle_thin", "bbisle_thin", "--batch=10", "--turntable=4", "--no-send"], stdout=f, stderr=subprocess.STDOUT)
fresh = [s["asset"] for s in SPECS if any(time.time() - os.path.getmtime(p) < 3600 for p in glob.glob(os.path.join(ART, "promo", s["asset"], "turn_*.png")))]
wl("DONE", "thin-prop turntables: %d/%d re-rendered (4 frames each = %d PNGs) at 45/135/225/315 deg, framed on true extent; fix in bharness/plugins/render.py auto-detects thin props (min footprint < 25%% of max)" % (len(fresh), len(SPECS), 4 * len(fresh)))
print("END", len(fresh), len(SPECS))
