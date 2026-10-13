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
dx, dy = hi.x - lo.x, hi.y - lo.y
thin = min(dx, dy) < 0.25 * max(dx, dy, hi.z - lo.z, 1e-3)   # fences/signs/banners: a 0/90/180/270 set shows them edge-on
if thin: rad = max(max(dx, dy, hi.z - lo.z) * 1.2, 0.1)   # frame on the real extent, not the diagonal
saved = (sc.camera, r.filepath, r.image_settings.file_format, r.resolution_x, r.resolution_y, r.resolution_percentage, r.film_transparent)
cd = bpy.data.cameras.new("BH_TT_Cam"); cam = bpy.data.objects.new("BH_TT_Cam", cd)
ld = bpy.data.lights.new("BH_TT_Sun", "SUN"); ld.energy = 3; sun = bpy.data.objects.new("BH_TT_Sun", ld)
sun.rotation_euler = (0.8, 0.2, 0.6)
fd = bpy.data.lights.new("BH_TT_Fill", "SUN"); fd.energy = 1.0; fd.color = (0.75, 0.82, 1.0); fill = bpy.data.objects.new("BH_TT_Fill", fd)
fill.rotation_euler = (1.1, 0.0, -2.2)
rd = bpy.data.lights.new("BH_TT_Rim", "SUN"); rd.energy = 2.0; rim = bpy.data.objects.new("BH_TT_Rim", rd)
rim.rotation_euler = (-0.9, 0.0, 3.0)
for o in (cam, sun, fill, rim): sc.collection.objects.link(o)
oldworld = sc.world; tw = bpy.data.worlds.new("BH_TT_World"); tw.use_nodes = True
bgc = %(bg)r
if bgc:
    tw.node_tree.nodes["Background"].inputs[0].default_value = tuple((int(bgc[k:k+2], 16) / 255.0) ** 2.2 for k in (0, 2, 4)) + (1.0,)
tw.node_tree.nodes["Background"].inputs[1].default_value = 0.6
sc.world = tw
out = []
try:
    sc.camera = cam; r.image_settings.file_format = "PNG"; r.film_transparent = not bgc
    r.resolution_x, r.resolution_y, r.resolution_percentage = %(size)d, %(size)d, 100
    os.makedirs(%(folder)r, exist_ok=True)
    for i in range(%(n)d):
        a = 2 * math.pi * i / %(n)d - math.pi / 2 + (math.pi / 4 if thin else 0.0)   # frame 0 = front (-Y); thin props offset 45 deg so no frame is edge-on
        cam.location = mid + Vector((math.cos(a), math.sin(a), 0.55)) * rad * 1.6
        cam.rotation_euler = (mid - cam.location).to_track_quat("-Z", "Y").to_euler()
        r.filepath = os.path.join(%(folder)r, "turn_%%02d.png" %% i)
        bpy.ops.render.render(write_still=True); out.append(r.filepath)
finally:
    (sc.camera, r.filepath, r.image_settings.file_format, r.resolution_x, r.resolution_y,
     r.resolution_percentage, r.film_transparent) = saved
    bpy.data.objects.remove(cam); bpy.data.cameras.remove(cd)
    for o, d in ((sun, ld), (fill, fd), (rim, rd)):
        bpy.data.objects.remove(o); bpy.data.lights.remove(d)
    sc.world = oldworld; bpy.data.worlds.remove(tw)
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

    def turntable(self, name, n=8, size=768, folder=None, bg="E9E4DA"):
        folder = folder or self.promo_dir(name)
        return run(self.ctx.bridge, TURNTABLE % {"name": name, "n": int(n), "size": int(size), "folder": folder, "bg": bg},
                   timeout=600)

    def actions(self):
        return [
            Action("shot", self.shot, Risk.READ, "viewport screenshot (optionally saved to path)", ["path?"]),
            Action("turntable", self.turntable, Risk.FILE, "N renders around the asset into art\\promo\\<Asset>\\",
                   ["name", "n?", "size?"]),
        ]
