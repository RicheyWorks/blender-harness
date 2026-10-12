"""Blender Boss Island flagship (contest). blender -b --factory-startup --python assets/flagship.py -- <art> <out_png>"""
import bpy, bmesh, sys, os, math, random, re, json
from mathutils import Vector, noise
a = sys.argv[sys.argv.index("--")+1:]; ART, PNG = a[0], a[1]
os.makedirs(os.path.join(ART, "flagship"), exist_ok=True); GLB = os.path.join(ART, "glb"); NAME = "Prop_Island_Flagship_BlenderBoss"
R = 120.0  # radius m: double the 60 m planned island radius (240 m across)
random.seed(1337)
bpy.ops.wm.read_factory_settings(use_empty=True); sc = bpy.context.scene
root = bpy.data.collections.new(NAME); sc.collection.children.link(root)
def h(x, y):
    d = math.hypot(x, y) / R
    base = max(0.0, 1 - d**2.2) * 14
    n = noise.fractal(Vector((x/45, y/45, 0.3)), 0.6, 2.0, 5) * 5
    ridge = max(0, 1 - math.hypot(x+35, y-30)/40) * 18   # quarry hill NW
    t = base + n*max(0, 1-d) + ridge
    t = round(t/3.0)*3.0*0.15 + t*0.85                # terraced tiers
    return t if d < 0.96 else t*(1-(d-0.96)/0.04)-3*(d-0.96)/0.04 if d < 1 else -3
# terrain
bm = bmesh.new(); N = 120; step = 2*R*1.08/N; vs = {}
for i in range(N+1):
    for j in range(N+1):
        x, y = -R*1.08+i*step, -R*1.08+j*step
        vs[i, j] = bm.verts.new((x, y, h(x, y)))
for i in range(N):
    for j in range(N):
        bm.faces.new((vs[i, j], vs[i+1, j], vs[i+1, j+1], vs[i, j+1]))
# underside rock cone (floating island)
ring = [v for v in bm.verts if math.hypot(v.co.x, v.co.y) > R*1.0]
for v in ring: v.co.z = min(v.co.z, -4 - (math.hypot(v.co.x, v.co.y)-R)*0) - (R*1.08-math.hypot(v.co.x,v.co.y))*0
bmesh.ops.delete(bm, geom=[v for v in bm.verts if math.hypot(v.co.x, v.co.y) > R*1.005], context='VERTS')
me = bpy.data.meshes.new(NAME+"_Terrain"); bm.to_mesh(me); bm.free()
ter = bpy.data.objects.new(NAME+"_Terrain", me); root.objects.link(ter)
col = me.color_attributes.new("Col", "BYTE_COLOR", "CORNER")
for poly in me.polygons:
    z = sum(me.vertices[k].co.z for k in poly.vertices)/len(poly.vertices)
    c = (0.80,0.72,0.50,1) if z < 1.5 else (0.20,0.50,0.12,1) if z < 13 else (0.45,0.42,0.38,1)
    if z < -0.5: c = (0.30,0.24,0.20,1)
    for li in poly.loop_indices: col.data[li].color = c
m = bpy.data.materials.new("M_BB_Terrain"); m.use_nodes = True
vc = m.node_tree.nodes.new("ShaderNodeVertexColor"); vc.layer_name = "Col"
m.node_tree.links.new(vc.outputs[0], m.node_tree.nodes["Principled BSDF"].inputs[0]); me.materials.append(m)
for p in me.polygons: p.use_smooth = True
# underside: inverted cone
bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=R*1.0, depth=80, location=(0, 0, -42.5)); cone = bpy.context.object
cone.rotation_euler.x = math.pi; cone.name = NAME+"_Underside"; rm = bpy.data.materials.new("M_BB_Rock"); rm.diffuse_color = (0.30,0.24,0.20,1)
rm.use_nodes = True; rm.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.30,0.24,0.20,1); cone.data.materials.append(rm)
for c in cone.users_collection: c.objects.unlink(cone)
root.objects.link(cone)
# catalog
names = sorted(f[:-4] for f in os.listdir(GLB) if f.endswith(".glb"))
def pick(rx, n): return [x for x in names if re.match(rx, x) and "_Harvested" not in x and "_Depleted" not in x][:n]
proto = {}
def load(an):
    if an in proto: return proto[an]
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(GLB, an+".glb"))
    objs = [o for o in bpy.data.objects if o not in before]
    for o in objs:
        for c in list(o.users_collection): c.objects.unlink(o)
    proto[an] = [o for o in objs if o.parent is None and o.type in ("MESH","EMPTY")] or objs; proto[an+"__all"] = objs
    return proto[an]
placed = []
def put(an, x, y, s=1.0, rot=None, zoff=0.0, tag=""):
    z = h(x, y) + zoff
    for src in load(an):
        o = src.copy(); o.location = (x, y, z); o.rotation_euler.z = random.uniform(0, 6.283) if rot is None else rot
        o.scale = (s, s, s); root.objects.link(o); o["catalog"] = an; o["zone"] = tag
        for ch in src.children_recursive:
            c2 = ch.copy(); c2.parent = o; root.objects.link(c2)
    placed.append((an, tag))
def scatter(pool, n, cx, cy, rad, tag, s=(0.9, 1.3)):
    for k in range(n):
        ang, rr = random.uniform(0, 6.283), rad*math.sqrt(random.random())
        x, y = cx+rr*math.cos(ang), cy+rr*math.sin(ang)
        if math.hypot(x, y) < R*0.93 and h(x,y) > 1.5: put(pool[k % len(pool)], x, y, random.uniform(*s), tag=tag)
trees = pick(r"Prop_Tree_.*_Mature", 20) or pick(r"Prop_Tree_", 20)
herbs = pick(r"Prop_Herb_", 40); blooms = pick(r"Prop_Bloom_", 30)
ores = pick(r"Prop_OreNode_.*_Large", 10) + pick(r"Prop_OreNode_.*_Small", 10)
stations = [x for x in names if re.search(r"Smelter|Forge|Cook|Anvil|Bench|Kiln|Loom|Furnace|Mill|Still", x) and not x.startswith("Item_")][:12]
mobs = pick(r"Mob_(Meadow|Forest)_(Grazer|Hopper|Crawler)", 18); crew = pick(r"Mob_Crew_", 12)
rocks = pick(r"Prop_Island_(Boulder|Driftwood|Tidepool)", 30); chests = pick(r"Prop_Chest_", 6)
scatter(trees, 140, 35, -25, 70, "orchard-forest", (1.0, 1.6))
scatter(trees, 60, -20, 60, 40, "north-grove", (1.0, 1.5))
for k, hb in enumerate(herbs*3):                                   # spiral herb garden, the Boss's signature
    t = k*0.55; rr = 6 + t*1.1
    if rr < 34: put(hb, -55+rr*math.cos(t)*0.6, -40+rr*math.sin(t)*0.6, 1.2, tag="herb-spiral")
scatter(blooms, 70, -55, -40, 30, "bloom-meadow")
scatter(ores, 40, -35, 30, 26, "quarry-hill", (1.0, 1.8))
for k, st in enumerate(stations):                                  # crafting plaza ring
    t = k/max(1, len(stations))*6.283; put(st, 10+14*math.cos(t), 5+14*math.sin(t), 1.0, rot=t+math.pi, tag="crafting-plaza")
for k, c in enumerate(chests): put(c, 10+4*math.cos(k), 5+4*math.sin(k), 1.0, tag="crafting-plaza")
scatter(mobs, 40, 55, 45, 22, "livestock-pen")
for k, c in enumerate(crew): put(c, 10+7*math.cos(k*0.52), 5+7*math.sin(k*0.52), 1.0, tag="crew")
for k in range(70):                                                # shoreline rocks
    t = random.uniform(0, 6.283); rr = R*random.uniform(0.86, 0.95); put(rocks[k % len(rocks)], rr*math.cos(t), rr*math.sin(t), random.uniform(0.8, 2.0), tag="shore")
# ark dock: pier east + moored ark
wood = bpy.data.materials.new("M_BB_Pier"); wood.diffuse_color = (0.45, 0.30, 0.18, 1)
wood.use_nodes = True; wood.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.45, 0.30, 0.18, 1)
z0 = h(R*0.85, 0) + 0.6
for k in range(14):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(R*0.82+k*2.6, 0, z0)); p = bpy.context.object; p.scale = (2.5, 6, 0.3)
    p.name = "%s_Pier_%02d" % (NAME, k); p.data.materials.append(wood)
    for c in p.users_collection: c.objects.unlink(p)
    root.objects.link(p)
for k, dc in enumerate(pick(r"Veh_ArkPart_DockClamp_", 4)): put(dc, R*0.86+k*8, 4.5, 1.2, rot=0, zoff=z0-h(R*0.86+k*8, 4.5), tag="ark-dock")
if "Veh_Ark" in names: put("Veh_Ark", R*0.82+40, -12, 1.0, rot=math.pi/2, zoff=z0+4-h(R*0.82+40, -12), tag="ark-dock")
# lights/camera/render
sun = bpy.data.objects.new("Sun", bpy.data.lights.new("Sun", "SUN")); sun.data.energy = 5; sun.rotation_euler = (0.9, 0.2, 2.3); sc.collection.objects.link(sun)
w = bpy.data.worlds.new("Sky"); sc.world = w; w.use_nodes = True; w.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.48, 0.90, 1); w.node_tree.nodes["Background"].inputs[1].default_value = 0.9
cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.location = (190, -200, 105); cam.data.lens = 35
d = Vector((30, 0, -8)) - cam.location; cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
sc.render.engine = "BLENDER_EEVEE_NEXT"; sc.render.resolution_x, sc.render.resolution_y = 1920, 1080; sc.render.filepath = PNG
sc.view_settings.view_transform = "AgX"
bpy.ops.render.render(write_still=True)
# export: island collection only
for o in bpy.data.objects: o.select_set(False)
for o in root.all_objects: o.select_set(True)
out = os.path.join(GLB, NAME+".glb")
bpy.ops.export_scene.gltf(filepath=out, use_selection=True, export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ART, "flagship", NAME+".blend"))
from collections import Counter
print(json.dumps({"asset": NAME, "placed": len(placed), "unique": len(set(a for a, _ in placed)), "zones": Counter(t for _, t in placed), "glb": out, "mb": round(os.path.getsize(out)/1e6, 1), "stations": stations}))
