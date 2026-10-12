"""Palette, spec builder, glb reader/self-check (no Blender)."""
import json, os, struct, tempfile
from harness.check import Checks
from bharness.palette import resolve, linear, PALETTE
from bharness.build import validate, code, tris_estimate, SpecError
from bharness import glb

t = Checks()
t("palette: names resolve to the game's hex", resolve("wood") == "9A6B3F" and resolve("starmetal") == "7FE3FF")
t("palette: hex passes through, # stripped, upper-cased", resolve("#c9b49c") == "C9B49C")
t.raises("palette: an unknown colour is an error, not black", KeyError, lambda: resolve("wodo"))
t("palette: linear(white) = 1, linear(black) = 0", linear("FFFFFF")[:3] == (1.0, 1.0, 1.0) and linear("000000")[:3] == (0, 0, 0))
t("palette: linear is gamma 2.2", abs(linear("808080")[0] - (128 / 255) ** 2.2) < 1e-4)
t("palette has every brief ore colour", all(k in PALETTE for k in ("coal", "copper", "iron", "gold", "crystal", "starmetal")))
box = [[0.1, 0.1, 0.1], [0, 0, 0.05], 0]
ok = {"asset": "Tool_X", "materials": ["wood"], "parts": [{"name": "", "boxes": [box]}]}
t("a minimal spec validates", validate(ok)["materials"] == ["9A6B3F"])
bad = [("no asset", dict(ok, asset="")), ("no materials", dict(ok, materials=[])), ("4 materials", dict(ok, materials=["wood"] * 4)),
       ("no parts", dict(ok, parts=[])), ("empty part", dict(ok, parts=[{"name": "", "boxes": []}])),
       ("duplicate part", dict(ok, parts=[{"name": "_A", "boxes": [box]}, {"name": "_A", "boxes": [box]}])),
       ("space in part name", dict(ok, parts=[{"name": "_A B", "boxes": [box]}])),
       ("zero-size box", dict(ok, parts=[{"name": "", "boxes": [[[0, 1, 1], [0, 0, 0], 0]]}])),
       ("material index out of range", dict(ok, parts=[{"name": "", "boxes": [[[1, 1, 1], [0, 0, 0], 1]]}]))]
for label, s in bad:
    t.raises("spec rejected: " + label, SpecError, lambda s=s: validate(s))
t("glow defaults to glowing palette names", validate(dict(ok, materials=["wood", "starmetal"]))["glow"] == [1])
t("tris estimate: 44 per bevelled box, 12 unbevelled",
  tris_estimate(ok) == 44 and tris_estimate(dict(ok, parts=[{"name": "", "boxes": [box, box], "bevel": 0}])) == 24)
c = code(ok)
t("generated code compiles", compile(c, "<spec>", "exec") is not None)
t("generated code carries linear colours, not hex", "9A6B3F" not in c and str(round((0x9A / 255) ** 2.2, 5)) in c)
t("generated code never opens a modal", "INVOKE_DEFAULT" not in c and "bpy.ops" not in c)
from assets.realm import SPECS as RS
from assets.toolspecs import SPECS as TS
t("every realm spec validates", all(validate(s) for s in RS))
t("every tool/weapon spec validates (%d)" % len(TS), all(validate(s) for s in TS) and len(TS) >= 40)
from bharness.plugins.judge import BUDGET
over = [s["asset"] for s in RS + TS if tris_estimate(s) > BUDGET[s["asset"].split("_")[0]]]
t("every spec is inside its triangle budget before Blender", not over, over)


def fake_glb(path, tris=12, dims=(1, 1, 1), name="Tool_X", mats=1, scale=None):
    node = {"name": name, "mesh": 0}
    if scale: node["scale"] = scale
    doc = {"asset": {"version": "2.0"}, "nodes": [node], "materials": [{"name": "m%d" % i} for i in range(mats)],
           "meshes": [{"name": name, "primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "material": i} for i in range(mats)]}],
           "accessors": [{"count": 8, "min": [0, 0, 0], "max": list(dims)}, {"count": tris * 3 // mats}]}
    js = json.dumps(doc).encode(); js += b" " * (-len(js) % 4)
    with open(path, "wb") as f:
        f.write(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js)) + struct.pack("<I4s", len(js), b"JSON") + js)
    return path


d = tempfile.mkdtemp()
probe = {"objects": [{"name": "Tool_X", "tris": 12, "min": [0, 0, 0], "max": [1, 1, 1]}]}
s = glb.summarize(glb.read_json(fake_glb(os.path.join(d, "a.glb"))))
t("glb: reads meshes, nodes, triangles", s["meshes"][0]["triangles"] == 12 and len(s["nodes"]) == 1)
t("glb: a faithful file passes the self-check", all(c["ok"] for c in glb.check(probe, s)), glb.check(probe, s))
lost = glb.summarize(glb.read_json(fake_glb(os.path.join(d, "b.glb"), tris=10)))
t("glb: lost triangles fail", not next(c for c in glb.check(probe, lost) if c["check"].startswith("triangles"))["ok"])
big = glb.summarize(glb.read_json(fake_glb(os.path.join(d, "c.glb"), dims=(2, 1, 1))))
t("glb: a size change fails", not next(c for c in glb.check(probe, big) if c["check"].startswith("sizes"))["ok"])
sc = glb.summarize(glb.read_json(fake_glb(os.path.join(d, "d.glb"), scale=[2, 1, 1])))
t("glb: a baked node scale fails", not next(c for c in glb.check(probe, sc) if c["check"].startswith("no node scale"))["ok"])
ren = glb.summarize(glb.read_json(fake_glb(os.path.join(d, "e.glb"), name="Other")))
t("glb: a renamed node fails", not next(c for c in glb.check(probe, ren) if c["check"].startswith("node names"))["ok"])
open(os.path.join(d, "x.glb"), "wb").write(b"nope" * 4)
t.raises("glb: bad magic is rejected", ValueError, lambda: glb.read_json(os.path.join(d, "x.glb")))
t.done()
