import os, sys, subprocess, time, json
R = r"C:\Users\730ri\projects\blender-harness"; os.chdir(R); sys.path.insert(0, R)
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); BL = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
GLB = r"C:\Users\730ri\projects\bot-team\art\glb"
def wl(k, t): subprocess.call([sys.executable, os.path.join(J, "wl.py"), k, t])
def free_mb():
    o = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory"], capture_output=True, text=True, creationflags=0x08000000).stdout
    return int("".join(c for c in o if c.isdigit()) or 0) // 1024
def turn_active():
    try: t = open(os.path.join(J, "bb_makeup3.log"), encoding="utf-8").read()
    except Exception: return False
    return "TRIGGER" in t and "exit turns" not in t
from assets import wave4 as W, wave4_lod1 as L
res = {}
for g, src in (("ore_nodes_lod1", "ore_nodes"), ("tools_lod1", "tools"), ("metal_items_lod1", "metal_items")):
    while turn_active() or free_mb() < 1200:   # never compete with the editor for RAM
        time.sleep(20)
    wl("DOING", "LOD1 %s: building %d models hidden (free RAM %d MB)" % (src, len(L.GROUPS[g]), free_mb()))
    with open(os.path.join(J, "w4_%s.log" % g), "w") as f:
        subprocess.call([BL, "-b", "--factory-startup", "--python", "assets/headless.py", "--", R, "assets.wave4_lod1", g, "--batch=10", "--turntable=0", "--no-send"], stdout=f, stderr=subprocess.STDOUT)
    b0 = sum(len(p["boxes"]) for s in W.GROUPS[src] for p in s["parts"]); b1 = sum(len(p["boxes"]) for s in L.GROUPS[g] for p in s["parts"])
    n = sum(os.path.exists(os.path.join(GLB, s["asset"] + ".glb")) for s in L.GROUPS[g])
    wl("DONE", "LOD1 %s: %d/%d glbs; boxes %d -> %d (%.0f%%), ~%d -> ~%d tris" % (src, n, len(L.GROUPS[g]), b0, b1, 100.0 * b1 / max(b0, 1), 12 * b0, 12 * b1))
