"""Live stress test of the 9876 bridge. Works in a throwaway scene and deletes it; never saves."""
import json, time, sys, os, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bharness import Bridge
b = Bridge(timeout=55)
R = []
def t(name, fn):
    t0 = time.time()
    try: r = fn(); ok = True
    except Exception as e: r = repr(e); ok = False
    s = json.dumps(r, default=str)
    R.append((name, ok, int((time.time()-t0)*1000), s[:300]))
    print("%-28s %-5s %6dms %s" % (name, ok, R[-1][2], s[:300]), flush=True)
    return r
t("status", lambda: b.call("ping"))
t("scene_info", lambda: b.call("get_scene_info"))
t("guard: file clean?", lambda: b.py("import bpy\nresult=bpy.data.is_dirty"))
if R[-1][3].find('"result": false')<0: print("ABORT: Blender has unsaved work"); sys.exit(2)
t("make stress scene", lambda: b.py("import bpy\nsc=bpy.data.scenes.new('BH_Stress')\nbpy.context.window.scene=sc\ncam=bpy.data.objects.new('BH_Cam',bpy.data.cameras.new('BH_Cam'));sc.collection.objects.link(cam);cam.location=(16,-40,25);cam.rotation_euler=(1.1,0,0);sc.camera=cam\nresult=sc.name"))
t("py return value", lambda: b.py("result = 6*7"))
t("py print capture", lambda: b.py("print('hello from blender')"))
t("py syntax error", lambda: b.py("def ("))
t("py runtime error", lambda: b.py("1/0"))
t("alive after errors", lambda: b.call("ping"))
t("1000 cubes (bmesh-free)", lambda: b.py("import bpy\nsc=bpy.context.scene\nme=bpy.data.meshes.new('BHc')\nimport bmesh\nbm=bmesh.new();bmesh.ops.create_cube(bm,size=1);bm.to_mesh(me);bm.free()\nfor i in range(1000):\n o=bpy.data.objects.new('BH_%d'%i,me);o.location=(i%32,i//32,0);sc.collection.objects.link(o)\nresult=len(sc.objects)"))
t("200 ops.mesh_add", lambda: b.py("import bpy\nfor i in range(200): bpy.ops.mesh.primitive_cube_add(location=(i,-5,0))\nresult=len(bpy.context.scene.objects)"))
t("scene_info large", lambda: b.call("get_scene_info"))
t("big return 2MB", lambda: len(json.dumps(b.py("result='x'*2_000_000"))))
t("sleep 20s", lambda: b.py("import time;time.sleep(20);result='woke'"))
t("short timeout 3s on 10s", lambda: Bridge(timeout=3).py("import time;time.sleep(10)"))
t("alive after timeout", lambda: b.call("ping"))
t("viewport_screenshot", lambda: str(b.call("viewport_screenshot", filepath=r"C:\Users\730ri\AppData\Local\Temp\bh_shot.png"))[:300])
t("render_image eevee", lambda: str(b.call("render_image", output_path=r"C:\Users\730ri\AppData\Local\Temp\bh_render.png", resolution_percentage=50))[:300])
import concurrent.futures as cf
t("4 concurrent clients", lambda: list(cf.ThreadPoolExecutor(4).map(lambda i: b.py("import time;time.sleep(1);result=%d"%i)["result"]["result"], range(4))))
t("revert file (discard test)", lambda: b.py("import bpy\nbpy.ops.wm.revert_mainfile()\nresult=bpy.data.is_dirty"))
#t("cleanup", lambda: b.py("import bpy\nsc=bpy.data.scenes['BH_Stress']\nfor o in list(sc.objects): bpy.data.objects.remove(o)\nfor m in [m for m in bpy.data.meshes if m.users==0]: bpy.data.meshes.remove(m)\nbpy.context.window.scene=[s for s in bpy.data.scenes if s.name!='BH_Stress'][0]\nbpy.data.scenes.remove(sc)\nresult=[s.name for s in bpy.data.scenes]"))
t("final status", lambda: b.call("ping"))
