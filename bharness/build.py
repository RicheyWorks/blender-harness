# SPDX-License-Identifier: MIT
"""Data-driven builder: a spec (plain dict / JSON) -> Blender Python that builds the asset. Reusable for any project.

spec = {
  "asset": "Tool_Hoe_Iron",
  "materials": ["wood", "grip", "iron"],         # 1-3 palette names or hex; index = box material
  "glow": [2],                                    # optional: material indexes that emit
  "bevel": 0.12,                                  # optional: bevel as a fraction of the box's smallest side
  "parts": [                                      # one object per part; moving parts get their own pivot
     {"name": "",  "boxes": [[[sx,sy,sz],[cx,cy,cz],mat], ...]},              # "" -> object named like the asset
     {"name": "_ArmL", "pivot": [x,y,z], "boxes": [...]},                    # origin at the pivot (a joint)
  ]}
The whole asset is shifted so it stands on z=0 centred on x/y (brief: bottom-centre origin). Pivots are given in
spec coordinates and shifted the same way. Front = -Y."""
import json
from .palette import resolve, linear, GLOW


class SpecError(ValueError):
    pass


def validate(spec):
    """Raise SpecError for anything the brief or Blender would reject; return the normalised spec."""
    s = dict(spec)
    if not s.get("asset"):
        raise SpecError("spec has no asset name")
    mats = s.get("materials") or []
    if not 1 <= len(mats) <= 3:
        raise SpecError("%s: needs 1-3 materials, has %d" % (s["asset"], len(mats)))
    s["materials"] = [resolve(m) for m in mats]
    parts = s.get("parts") or []
    if not parts:
        raise SpecError(s["asset"] + ": no parts")
    names = set()
    for p in parts:
        n = p.get("name", "")
        if n in names:
            raise SpecError("%s: duplicate part %r" % (s["asset"], n))
        names.add(n)
        if " " in n:
            raise SpecError("%s: part name %r has a space" % (s["asset"], n))
        if not p.get("boxes"):
            raise SpecError("%s%s: no boxes" % (s["asset"], n))
        for b in p["boxes"]:
            (size, centre, mi) = b
            if min(size) <= 0:
                raise SpecError("%s%s: box with a non-positive size %r" % (s["asset"], n, size))
            if not 0 <= mi < len(mats):
                raise SpecError("%s%s: material index %d out of range" % (s["asset"], n, mi))
    if "glow" not in s:
        s["glow"] = [i for i, m in enumerate(mats) if isinstance(m, str) and m.lower() in GLOW]
    return s


def tris_estimate(spec):
    """A bevelled box (segments=1) has 26 faces -> 44 triangles. Lets catalogs check budgets before Blender."""
    return sum((44 if p.get("bevel", spec.get("bevel", 0.12)) > 0 else 12) * len(p["boxes"]) for p in spec["parts"])


CODE = r'''
import bpy, bmesh, json
spec = json.loads(%r)
name = spec["asset"]
col = bpy.data.collections.get(name) or bpy.data.collections.new(name)
if col.name not in [c.name for c in bpy.context.scene.collection.children]:
    bpy.context.scene.collection.children.link(col)
for o in list(col.all_objects):
    bpy.data.objects.remove(o)
mats = []
for i, rgb in enumerate(spec["lin"]):
    mname = "%%s_M%%d" %% (name, i)
    m = bpy.data.materials.get(mname) or bpy.data.materials.new(mname)
    m.use_nodes = True; m.diffuse_color = rgb
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = rgb; p.inputs["Roughness"].default_value = 0.6
    if i in spec["glow"]:
        p.inputs["Emission Color"].default_value = rgb; p.inputs["Emission Strength"].default_value = 2.0
    mats.append(m)
built = []
for part in spec["parts"]:
    bm = bmesh.new()
    for (sx, sy, sz), (cx, cy, cz), mi in part["boxes"]:
        t = bmesh.new(); bmesh.ops.create_cube(t, size=1.0)
        for v in t.verts:
            v.co.x = v.co.x * sx + cx; v.co.y = v.co.y * sy + cy; v.co.z = v.co.z * sz + cz
        bev = part.get("bevel", spec["bevel"])
        if bev > 0:
            bmesh.ops.bevel(t, geom=list(t.edges), offset=min(sx, sy, sz) * bev, segments=1, affect="EDGES")
        for f in t.faces:
            f.material_index = mi
        me = bpy.data.meshes.new("tmp"); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
    built.append((part, bm))
vs = [v.co for _, bm in built for v in bm.verts]
off = ((min(v.x for v in vs) + max(v.x for v in vs)) / 2, (min(v.y for v in vs) + max(v.y for v in vs)) / 2, min(v.z for v in vs))
out = []
for part, bm in built:
    piv = part.get("pivot") or [off[0], off[1], off[2]]
    for v in bm.verts:
        v.co.x -= piv[0]; v.co.y -= piv[1]; v.co.z -= piv[2]
    oname = name + part.get("name", "")
    me = bpy.data.meshes.new(oname); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(oname, me); col.objects.link(ob)
    ob.location = (piv[0] - off[0], piv[1] - off[1], piv[2] - off[2])
    for m in mats:
        ob.data.materials.append(m)
    out.append({"name": oname, "tris": sum(len(f.vertices) - 2 for f in me.polygons), "location": list(ob.location)})
result = out
'''


def code(spec):
    s = validate(spec)
    payload = {"asset": s["asset"], "parts": s["parts"], "glow": s["glow"], "bevel": s.get("bevel", 0.12),
               "lin": [linear(m) for m in s["materials"]]}
    return CODE % json.dumps(payload)
