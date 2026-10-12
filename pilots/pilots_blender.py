# SPDX-License-Identifier: MIT
"""Unreal feature pilots, Blender side. Run headless: blender -b --factory-startup --python pilots/pilots_blender.py -- <art>
Writes art/pilots/{rig,lumen,vfx,sequencer}/... and art/pilots/pilots.json. Never touches the source .blend files (it opens, builds, and exports; it never saves over them)."""
import bpy, json, math, os, sys
ART = sys.argv[sys.argv.index("--") + 1]
OUT = os.path.join(ART, "pilots"); res = {}
def d(*p):
    f = os.path.join(OUT, *p); os.makedirs(os.path.dirname(f), exist_ok=True); return f
def empty():
    bpy.ops.wm.read_homefile(use_empty=True)
def export(path, **kw):
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_apply=True, export_yup=True, **kw)
    return os.path.getsize(path)
def mat(name, rgb, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (*rgb, 1); p.inputs["Roughness"].default_value = 0.8
    if emit: p.inputs["Emission Color"].default_value = (*rgb, 1); p.inputs["Emission Strength"].default_value = emit
    return m
def box(name, s, c, m):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c); o = bpy.context.object; o.scale = s; o.name = name; o.data.name = name
    bpy.ops.object.transform_apply(scale=True); o.data.materials.append(m); return o

# ---------------------------------------------------------------- 1. rig + clips
CLIPS = {"Idle": 48, "Walk": 32, "Attack": 24, "Hit": 16}
def rig(asset):
    empty(); src = os.path.join(ART, "Mob", asset + ".blend")
    with bpy.data.libraries.load(src, link=False) as (a, b): b.objects = a.objects
    parts = [o for o in b.objects if o and o.type == "MESH"]
    for o in parts: bpy.context.scene.collection.objects.link(o)
    bpy.ops.object.armature_add(location=(0, 0, 0)); arm = bpy.context.object; arm.name = asset + "_Rig"; arm.data.name = asset + "_Skel"
    bpy.ops.object.mode_set(mode="EDIT"); eb = arm.data.edit_bones; eb.remove(eb[0])
    root = eb.new("root"); root.head, root.tail = (0, 0, 0), (0, 0.2, 0)
    names = []
    for o in parts:
        suf = o.name[len(asset):].strip("_") or "Body"; bn = suf
        if bn == "root": bn = "Body"
        lo = [v.co for v in o.data.vertices]; mn = [min(v[i] for v in lo) for i in range(3)]; mx = [max(v[i] for v in lo) for i in range(3)]
        pv = list(o.location) if any(o.location) else [(mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2, mn[2]]
        bb = eb.new(bn); bb.head = pv; bb.tail = (pv[0], pv[1], pv[2] + max(0.1, (mx[2] - mn[2]) / 2)); bb.parent = root
        names.append((o, bn))
    bpy.ops.object.mode_set(mode="OBJECT")
    for o, bn in names:   # rigid skin: each part's vertices weighted 1.0 to its own bone
        o.vertex_groups.new(name=bn).add(range(len(o.data.vertices)), 1.0, "REPLACE")
    bpy.ops.object.select_all(action="DESELECT")
    for o, _ in names: o.select_set(True)
    bpy.context.view_layer.objects.active = names[0][0]; bpy.ops.object.join(); me = bpy.context.object
    me.name = asset; me.data.name = asset
    md = me.modifiers.new("Armature", "ARMATURE"); md.object = arm; me.parent = arm
    bones = [bn for _, bn in names]
    def key(pb, f, loc=None, rot=None):
        if loc is not None: pb.location = loc; pb.keyframe_insert("location", frame=f)
        if rot is not None: pb.rotation_mode = "XYZ"; pb.rotation_euler = rot; pb.keyframe_insert("rotation_euler", frame=f)
    arm.animation_data_create()
    for clip, n in CLIPS.items():
        act = bpy.data.actions.new(clip); arm.animation_data.action = act
        for bn in ["root"] + bones:
            pb = arm.pose.bones[bn]; lo = bn.lower()
            for f in (1, n // 4 + 1, n // 2 + 1, 3 * n // 4 + 1, n + 1):
                t = (f - 1) / n * 2 * math.pi; s = math.sin(t)
                if clip == "Idle":
                    key(pb, f, loc=(0, 0, 0.02 * s if lo in ("root", "body") else 0), rot=(0, 0, 0))
                elif clip == "Walk":
                    sw = 0.5 * s * (-1 if lo.endswith("r") else 1)
                    key(pb, f, loc=(0, 0, abs(0.03 * s) if lo == "root" else 0), rot=((sw if ("leg" in lo or "arm" in lo) else 0), 0, 0))
                elif clip == "Attack":
                    a = math.sin(min(1, (f - 1) / (n * 0.5)) * math.pi)
                    key(pb, f, loc=(0, -0.15 * a if lo in ("root", "body") else 0, 0), rot=((-1.4 * a if lo in ("armr", "head") else 0), 0, 0))
                else:   # Hit: knocked back, recovers
                    a = max(0, 1 - (f - 1) / n) * (1 if f > 1 else 0)
                    key(pb, f, loc=(0, 0.12 * a if lo == "root" else 0, 0), rot=((0.35 * a if lo in ("body", "head") else 0), 0, 0))
        tr = arm.animation_data.nla_tracks.new(); tr.name = clip; tr.strips.new(clip, 1, act); arm.animation_data.action = None
    p = d("rig", asset + "_Rig.glb")
    size = export(p, export_animations=True, export_animation_mode="NLA_TRACKS", export_skins=True, export_force_sampling=True)
    return {"glb": p, "bytes": size, "bones": ["root"] + bones, "clips": CLIPS, "tris": sum(len(f.vertices) - 2 for f in me.data.polygons), "skin": "rigid, 1 bone per moving part"}

for a in ("Mob_BlightSlime", "Mob_StoneKnight"):
    try: res["rig_" + a] = rig(a)
    except Exception as e: res["rig_" + a] = {"error": repr(e)[:300]}

# ---------------------------------------------------------------- 2. Lumen emissive + slot convention
empty()
mb, ma, me_ = mat("M_Base", (0.30, 0.22, 0.14)), mat("M_Accent", (0.55, 0.57, 0.62)), mat("M_Emissive", (1.0, 0.75, 0.30), emit=8.0)
for n, s, c, m in (("Prop_Pilot_LumenLamp", (0.3, 0.3, 0.1), (0, 0, 0.05), mb),):
    o = box(n, s, c, m)
parts = [box("p1", (0.08, 0.08, 1.2), (0, 0, 0.7), ma), box("p2", (0.3, 0.3, 0.3), (0, 0, 1.45), me_), box("p3", (0.4, 0.4, 0.06), (0, 0, 1.63), ma)]
for x in parts: x.select_set(True)
o.select_set(True); bpy.context.view_layer.objects.active = o; bpy.ops.object.join()
p = d("lumen", "Prop_Pilot_LumenLamp.glb"); res["lumen"] = {"glb": p, "bytes": export(p), "slots": ["M_Base", "M_Accent", "M_Emissive"],
    "convention": "slot names M_Base/M_Accent/M_Emissive; M_Emissive = emission colour = base colour, strength 8 (KHR_materials_emissive_strength)"}

# ---------------------------------------------------------------- 3. Niagara VFX meshes
empty(); fx = mat("M_FX_Additive", (1, 1, 1), emit=4.0)
bpy.ops.mesh.primitive_plane_add(size=1); q = bpy.context.object; q.name = q.data.name = "FX_Quad"; q.rotation_euler = (math.pi / 2, 0, 0); q.data.materials.append(fx)
bpy.ops.mesh.primitive_circle_add(vertices=16, radius=0.5, fill_type="NOTHING", location=(2, 0, 0)); r = bpy.context.object; r.name = r.data.name = "FX_Ring"
bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.mesh.extrude_region_shrink_fatten(TRANSFORM_OT_shrink_fatten={"value": -0.1}); bpy.ops.object.mode_set(mode="OBJECT"); r.data.materials.append(fx)
bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.5, radius2=0.0, depth=0.6, end_fill_type="NOTHING", location=(4, 0, 0.3)); c = bpy.context.object; c.name = c.data.name = "FX_Cone"; c.data.materials.append(fx)
bpy.ops.mesh.primitive_cube_add(size=0.1, location=(6, 0, 0.05)); k = bpy.context.object; k.name = k.data.name = "FX_Shard"; k.data.materials.append(fx)
res["vfx"] = {}
for o in (q, r, c, k):
    bpy.ops.object.select_all(action="DESELECT"); o.select_set(True); o.location = (0, 0, o.location.z)
    p = d("vfx", o.name + ".glb"); res["vfx"][o.name] = {"glb": p, "bytes": export(p, use_selection=True), "tris": sum(len(f.vertices) - 2 for f in o.data.polygons)}

# ---------------------------------------------------------------- 4. Sequencer: camera + animated prop, 5 s at 24 fps
empty(); sc = bpy.context.scene; sc.render.fps = 24; sc.frame_start, sc.frame_end = 1, 120
cm = bpy.data.cameras.new("CAM_Pilot_Orbit"); cm.lens = 35; cam = bpy.data.objects.new("CAM_Pilot_Orbit", cm); sc.collection.objects.link(cam)
tgt = box("Prop_Pilot_SeqCube", (1, 1, 1), (0, 0, 0.5), mat("M_Base", (0.35, 0.75, 0.25)))
cam.animation_data_create(); keys = []
for f in range(1, 121, 10):
    a = (f - 1) / 120 * 2 * math.pi; cam.location = (6 * math.sin(a), -6 * math.cos(a), 2.5)
    dvec = (-cam.location.x, -cam.location.y, 0.5 - 2.5); cam.rotation_mode = "XYZ"
    cam.rotation_euler = (math.atan2(math.hypot(dvec[0], dvec[1]), -dvec[2]), 0, math.atan2(dvec[1], dvec[0]) + math.pi / 2)
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f)
    tgt.location.z = 0.5 + 0.5 * math.sin(a); tgt.keyframe_insert("location", frame=f)
    keys.append({"frame": f, "cam_loc_m": [round(v, 3) for v in cam.location], "cam_rot_deg": [round(math.degrees(v), 2) for v in cam.rotation_euler], "lens_mm": 35})
cam.animation_data.action.name = "CAM_Pilot_Orbit_Move"; tgt.animation_data.action.name = "Prop_Pilot_SeqCube_Bob"
p = d("sequencer", "Seq_Pilot_Orbit.glb")
res["sequencer"] = {"glb": p, "bytes": export(p, export_cameras=True, export_animations=True, export_force_sampling=True), "fps": 24, "frames": 120}
jp = d("sequencer", "Seq_Pilot_Orbit.camera.json"); json.dump({"fps": 24, "frames": [1, 120], "units": "m, Blender Z-up", "keys": keys}, open(jp, "w"), indent=1)
res["sequencer"]["camera_json"] = jp
json.dump(res, open(d("pilots.json"), "w"), indent=1); print("PILOTS", json.dumps(res)[:2000])
