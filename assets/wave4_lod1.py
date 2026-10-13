# SPDX-License-Identifier: MIT
"""LOD1 for wave-4 crafting stations + ark parts: same specs as assets/wave4.py, each part keeps its largest boxes
(<= 60%, tiny parts < 4% of extent dropped; see bbisle_lod1.lod1). Output <Asset>_LOD1."""
from assets.wave4 import GROUPS as W
from assets.bbisle_lod1 import lod1
def L(specs): return [dict(s, asset=s["asset"] + "_LOD1", parts=[dict(p, boxes=lod1(p["boxes"])) for p in s["parts"]]) for s in specs]
GROUPS = {k + "_lod1": L(W[k]) for k in ("stations", "ark_parts", "ore_nodes", "tools", "metal_items")}
SPECS = [x for g in GROUPS.values() for x in g]; ORDER = list(GROUPS); SIZE = {k: "varies" for k in GROUPS}
