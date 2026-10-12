# SPDX-License-Identifier: MIT
"""Rig batch: skinned GLB + clips for rigged Mob_/Prop_ assets (from the rig pilot). Run headless: blender -b --factory-startup --python pilots/pilots_blender.py -- <art>
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
    empty(); src = os.path.join(ART, asset.split("_")[0], asset + ".blend")
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
    clips = {"Idle": 48, "Open": 24, "Close": 24} if asset.startswith("Prop_") else CLIPS
    for clip, n in clips.items():
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
                elif clip == "Open":
                    a = min(1, (f - 1) / (n * 0.5)); key(pb, f, rot=((-1.6 * a if lo == "lid" else 0), 0, 0))
                elif clip == "Close":
                    a = 1 - min(1, (f - 1) / (n * 0.5)); key(pb, f, rot=((-1.6 * a if lo == "lid" else 0), 0, 0))
                else:   # Hit: knocked back, recovers
                    a = max(0, 1 - (f - 1) / n) * (1 if f > 1 else 0)
                    key(pb, f, loc=(0, 0.12 * a if lo == "root" else 0, 0), rot=((0.35 * a if lo in ("body", "head") else 0), 0, 0))
        tr = arm.animation_data.nla_tracks.new(); tr.name = clip; tr.strips.new(clip, 1, act); arm.animation_data.action = None
    p = d("rig", asset + "_Rig.glb")
    size = export(p, export_animations=True, export_animation_mode="NLA_TRACKS", export_skins=True, export_force_sampling=True)
    return {"glb": p, "bytes": size, "bones": ["root"] + bones, "clips": clips, "tris": sum(len(f.vertices) - 2 for f in me.data.polygons), "skin": "rigid, 1 bone per moving part"}


NAMES = sys.argv[sys.argv.index("--") + 2:]
for a in NAMES:
    try:
        res["rig_" + a] = rig(a)
    except Exception as e: res["rig_" + a] = {"error": repr(e)[:300]}
json.dump(res, open(d("rig", "rig_batch.json"), "w"), indent=1); print("RIGS", json.dumps(res)[:3000])
