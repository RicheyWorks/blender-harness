# SPDX-License-Identifier: MIT
"""LOD1 for the built Prop_Decor_* models (autowave decor): only those whose glb exists; same lod1() rule. Output <Asset>_LOD1."""
import os, random
from assets.autowave import decor
from assets.bbisle_lod1 import lod1
GLB = r"C:\Users\730ri\projects\bot-team\art\glb"
SPECS = [dict(s, asset=s["asset"] + "_LOD1", parts=[dict(p, boxes=lod1(p["boxes"])) for p in s["parts"]])
         for s in decor(0, random.Random(0)) if os.path.exists(os.path.join(GLB, s["asset"] + ".glb"))]
GROUPS = {"decor_lod1": SPECS}; ORDER = ["decor_lod1"]; SIZE = {"decor_lod1": "0.5-5 m"}
