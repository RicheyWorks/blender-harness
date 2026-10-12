# SPDX-License-Identifier: MIT
"""glb export of an asset's collection, then a self-check of the file against Blender's own measurements
(the same numbers the Daedalus pipeline's judge compares), and a LOD / triangle report."""
import os, tempfile
from ..contract import Plugin, Action, Risk
from .bridge import run
from .probe import asset as probe
from .. import glb

EXPORT = r'''
import bpy
col = bpy.data.collections[%(name)r]
objs = [o for o in col.all_objects if o.type == "MESH"]
vl = bpy.context.view_layer
was = {o.name: o.select_get() for o in vl.objects}
act = vl.objects.active
for o in vl.objects: o.select_set(False)
for o in objs: o.select_set(True)
try:
    bpy.ops.export_scene.gltf('EXEC_DEFAULT', filepath=%(path)r, export_format="GLB", use_selection=True,
                              export_apply=True, export_yup=True, export_materials="EXPORT", export_animations=False)
finally:
    for o in vl.objects: o.select_set(was.get(o.name, False))
    vl.objects.active = act
result = %(path)r
'''

LOD = r'''
import bpy
col = bpy.data.collections[%(name)r]; dg = bpy.context.evaluated_depsgraph_get()
out = {}
for o in [o for o in col.all_objects if o.type == "MESH"]:
    row = {}
    for r in %(ratios)r:
        m = o.modifiers.new("BH_LOD", "DECIMATE"); m.ratio = r
        dg.update(); e = o.evaluated_get(dg); me = e.to_mesh(); me.calc_loop_triangles()
        row[str(r)] = len(me.loop_triangles); e.to_mesh_clear(); o.modifiers.remove(m)
    out[o.name] = row
dg.update()
result = out
'''


def export_glb(ctx, name, path=None):
    path = path or os.path.join(ctx.art, "glb", name + ".glb")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    run(ctx.bridge, EXPORT % {"name": name, "path": path}, timeout=300)
    summ = glb.summarize(glb.read_json(path))
    return {"path": path, "checks": glb.check(probe(ctx.bridge, name), summ), "file": summ}


def lod_report(ctx, name, ratios=(1.0, 0.5, 0.25)):
    from .judge import BUDGET
    per = run(ctx.bridge, LOD % {"name": name, "ratios": list(ratios)})
    total = {str(r): sum(v[str(r)] for v in per.values()) for r in ratios}
    budget = BUDGET.get(name.split("_")[0], 3000)
    return {"objects": per, "total": total, "budget": budget, "budget_used": round(total["1.0"] / budget, 3)}


class ExportPlugin(Plugin):
    name = "export"

    def actions(self):
        return [Action("glb", lambda name, path=None: export_glb(self.ctx, name, path), Risk.FILE,
                       "export the asset's collection to .glb and self-check it", ["name", "path?"]),
                Action("lod", lambda name: lod_report(self.ctx, name), Risk.SCENE,
                       "triangles per object at LOD ratios 1, 0.5, 0.25 vs the budget", ["name"])]
