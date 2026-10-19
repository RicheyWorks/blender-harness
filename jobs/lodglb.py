"""Generic LOD1 from catalog glbs (no spec needed): per asset, split into loose parts, drop the smallest parts (by bbox volume)
until ~60% of faces remain (never parts > 4% of the extent... largest always kept); meshes still > 2000 tris get a 0.5 collapse decimate.
blender -b --factory-startup --python lodglb.py -- <glb_dir> <name> [<name> ...]   -> <name>_LOD1.glb, prints JSON per asset."""
import bpy, sys, os, json
a = sys.argv[sys.argv.index("--") + 1:]; G = a[0]
for n in a[1:]:
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=os.path.join(G, n + ".glb"))
        ms = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        t0 = sum(len(o.data.polygons) for o in ms)
        for o in ms:
            bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); bpy.context.view_layer.objects.active = o
            bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.remove_doubles(threshold=0.0005); bpy.ops.mesh.separate(type="LOOSE"); bpy.ops.object.mode_set(mode="OBJECT")
        parts = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        vol = lambda o: max(o.dimensions.x, 1e-4) * max(o.dimensions.y, 1e-4) * max(o.dimensions.z, 1e-4)
        parts.sort(key=vol, reverse=True); keep, f = [], 0
        for o in parts:
            if keep and f >= 0.6 * t0: bpy.data.objects.remove(o); continue
            keep.append(o); f += len(o.data.polygons)
        for o in keep:
            for p in o.data.polygons: p.use_smooth = False   # merged verts: keep the flat voxel look
            if len(o.data.polygons) > 2000:
                d = o.modifiers.new("lod", "DECIMATE"); d.ratio = 0.5
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.export_scene.gltf(filepath=os.path.join(G, n + "_LOD1.glb"), use_selection=True, export_apply=True)
        t1 = sum(len(o.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.polygons) for o in keep)
        print("LODJSON " + json.dumps({"asset": n, "faces": t0, "lod1": t1, "parts": len(parts), "kept": len(keep)}), flush=True)
    except Exception as e:
        print("LODJSON " + json.dumps({"asset": n, "error": repr(e)[:200]}), flush=True)

