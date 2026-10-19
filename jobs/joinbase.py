import bpy, sys, os
blend, out = sys.argv[sys.argv.index("--")+1:]
bpy.ops.wm.open_mainfile(filepath=blend)
keys = ("_Terrain", "_Underside", "_Pier_", "_Water_")
objs = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("Prop_Island_Flagship_BlenderBoss") and any(k in o.name for k in keys)]
bpy.ops.object.select_all(action="DESELECT")
dup = []
for o in objs:
    c = o.copy(); c.data = o.data.copy(); bpy.context.scene.collection.objects.link(c); dup.append(c)
for c in dup: c.select_set(True)
bpy.context.view_layer.objects.active = dup[0]; bpy.ops.object.join()
j = bpy.context.view_layer.objects.active; j.name = "Prop_Island_BlenderBoss_Base"; j.data.name = j.name
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.ops.object.select_all(action="DESELECT"); j.select_set(True)
bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_apply=True)
print("JOINED", len(objs), len(j.data.polygons), len(j.data.materials))
