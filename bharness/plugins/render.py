# SPDX-License-Identifier: MIT
"""Viewport shots and turntable renders (for the advertising team: art\\promo\\<Asset>\\).

The turntable builds a temporary camera + light, renders N angles around the asset's collection, and removes
everything it added, restoring the scene camera and render settings, so the file's content is unchanged."""
import base64, os
from ..contract import Plugin, Action, Risk
from .bridge import unwrap, run

TURNTABLE = r'''
import bpy, math, os
from mathutils import Vector
sc = bpy.context.scene; r = sc.render
col = bpy.data.collections[%(name)r]
pts = [o.matrix_world @ Vector(c) for o in col.all_objects if o.type == "MESH" for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
mid = (lo + hi) / 2; rad = max((hi - lo).length, 0.1)
saved = (sc.camera, r.filepath, r.image_settings.file_format, r.resolution_x, r.resolution_y, r.resolution_percentage, r.film_transparent)
cd = bpy.data.cameras.new("BH_TT_Cam"); cam = bpy.data.objects.new("BH_TT_Cam", cd)
ld = bpy.data.lights.new("BH_TT_Sun", "SUN"); ld.energy = 3; sun = bpy.data.objects.new("BH_TT_Sun", ld)
sun.rotation_euler = (0.8, 0.2, 0.6)
sc.collection.objects.link(cam); sc.collection.objects.link(sun)
out = []
try:
    sc.camera = cam; r.image_settings.file_format = "PNG"; r.film_transparent = True
    r.resolution_x, r.resolution_y, r.resolution_percentage = %(size)d, %(size)d, 100
    os.makedirs(%(folder)r, exist_ok=True)
    for i in range(%(n)d):
        a = 2 * math.pi * i / %(n)d - math.pi / 2   # frame 0 looks at the front (-Y)
        cam.location = mid + Vector((math.cos(a), math.sin(a), 0.55)) * rad * 1.6
        cam.rotation_euler = (mid - cam.location).to_track_quat("-Z", "Y").to_euler()
        r.filepath = os.path.join(%(folder)r, "turn_%%02d.png" %% i)
        bpy.ops.render.render(write_still=True); out.append(r.filepath)
finally:
    (sc.camera, r.filepath, r.image_settings.file_format, r.resolution_x, r.resolution_y,
     r.resolution_percentage, r.film_transparent) = saved
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd)
    bpy.data.objects.remove(sun); bpy.data.lights.remove(ld)
result = out
'''


class RenderPlugin(Plugin):
    name = "render"

    def promo_dir(self, name):
        return os.path.join(self.ctx.art, "promo", name)

    def shot(self, path=None):
        res = unwrap(self.ctx.bridge.call("viewport_screenshot"))
        if path:
            with open(path, "wb") as f:
                f.write(base64.b64decode(res["image_png_base64"]))
        return {"width": res["width"], "height": res["height"], "path": path}

    def turntable(self, name, n=8, size=768, folder=None):
        folder = folder or self.promo_dir(name)
        return run(self.ctx.bridge, TURNTABLE % {"name": name, "n": int(n), "size": int(size), "folder": folder},
                   timeout=600)

    def actions(self):
        return [
            Action("shot", self.shot, Risk.READ, "viewport screenshot (optionally saved to path)", ["path?"]),
            Action("turntable", self.turntable, Risk.FILE, "N renders around the asset into art\\promo\\<Asset>\\",
                   ["name", "n?", "size?"]),
        ]
