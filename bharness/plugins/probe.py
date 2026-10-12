# SPDX-License-Identifier: MIT
"""Scene probes: measured inside Blender, returned as plain data."""
import json
from ..contract import Plugin, Action, Risk
from .bridge import run

ASSET = r'''
import bpy, json
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get()
col = bpy.data.collections.get(%(name)r)
objs = [o for o in (col.all_objects if col else []) if o.type == "MESH"]
out = {"asset": %(name)r, "collection": bool(col), "objects": [], "loose_meshes": []}
inside = set(o.name for o in objs)
out["loose_meshes"] = [o.name for o in bpy.context.scene.objects if o.type == "MESH" and o.name not in inside]
for o in objs:
    e = o.evaluated_get(dg); m = e.to_mesh(); m.calc_loop_triangles()
    ws = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mats = [s.material for s in o.material_slots]
    out["objects"].append({"name": o.name, "tris": len(m.loop_triangles), "scale": list(o.scale),
        "slots": len(mats), "empty_slots": sum(1 for x in mats if x is None),
        "images": any(n.type == "TEX_IMAGE" for x in mats if x and x.use_nodes for n in x.node_tree.nodes),
        "min": [min(v[i] for v in ws) for i in range(3)], "max": [max(v[i] for v in ws) for i in range(3)],
        "origin": list(o.matrix_world.translation)})
    e.to_mesh_clear()
result = out
'''


def asset(bridge, name):
    return run(bridge, ASSET % {"name": name})


class ProbePlugin(Plugin):
    name = "probe"

    def actions(self):
        return [Action("asset", lambda name: asset(self.ctx.bridge, name), Risk.READ,
                       "measure the collection named like the asset (tris after modifiers, bounds, slots)", ["name"])]
