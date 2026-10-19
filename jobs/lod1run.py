import os, sys, subprocess, json, time
R = r"C:\Users\730ri\projects\blender-harness"; os.chdir(R); sys.path.insert(0, R)
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); BL = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
def wl(k, t): subprocess.call([sys.executable, os.path.join(J, "wl.py"), k, t])
from assets import bbisle_lod1 as L, bbisle as B0
t0 = 0; t1 = 0; nb0 = nb1 = 0
for b in range(5):
    os.environ["BBISLE_BATCH"] = str(b)
    import importlib; importlib.reload(B0); importlib.reload(L)
    for a, c in zip(B0.SPECS, L.SPECS): nb0 += len(a["parts"][0]["boxes"]); nb1 += len(c["parts"][0]["boxes"])
    wl("DOING", "LOD1 batch %d/5 building (%d models)" % (b + 1, len(L.SPECS)))
    with open(os.path.join(J, "lod1_b%d.log" % b), "w") as f:
        subprocess.call([BL, "-b", "--factory-startup", "--python", "assets/headless.py", "--", R, "assets.bbisle_lod1", "bbisle_lod1", "--batch=10", "--turntable=0", "--no-send"], stdout=f, stderr=subprocess.STDOUT, env=dict(os.environ))
glbs = [x for x in os.listdir(r"C:\Users\730ri\projects\bot-team\art\glb") if x.startswith("Prop_BBIsle_") and x.endswith("_LOD1.glb")]
wl("DONE", "LOD1 for Prop_BBIsle_*: %d/500 glbs built; parts %d -> %d (%.0f%%), tris ~%d -> ~%d (12/box)" % (len(glbs), nb0, nb1, 100.0 * nb1 / nb0, nb0 * 12, nb1 * 12))
print("END", len(glbs), nb0, nb1)
