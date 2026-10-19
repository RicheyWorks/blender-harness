import bpy, sys, os
src, blend, glb = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
for o in bpy.data.objects:
    if o.type == "MESH" and o.data: o.data.name = o.name
os.makedirs(os.path.dirname(blend), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.export_scene.gltf(filepath=glb, export_apply=True)
print("OBJS", [o.name for o in bpy.data.objects], sum(len(p.vertices)-2 for o in bpy.data.objects if o.type=="MESH" for p in o.data.polygons))
