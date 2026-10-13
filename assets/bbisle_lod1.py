# SPDX-License-Identifier: MIT
"""LOD1 for the 500 Prop_BBIsle_* models: same seeded structure, keep the largest boxes (by volume) up to 60%,
always dropping parts whose longest side is < 4% of the model's extent. Output Prop_BBIsle_<Family>_<nn>_LOD1.
python: GROUPS for headless.py; batch via env BBISLE_BATCH (0-based, 120 per batch)."""
import os, math
from assets.bbisle import items as _items
def lod1(boxes, keep=0.6, tiny=0.04):
    ext = max(max(abs(c[i]) + s[i] / 2 for s, c, *_ in boxes) for i in range(3)) * 2 or 1.0
    big = [x for x in boxes if max(x[0]) >= tiny * ext] or boxes[:1]
    big.sort(key=lambda x: -(x[0][0] * x[0][1] * x[0][2]))
    return big[:max(1, math.ceil(len(boxes) * keep))]
def items(lo, hi):
    out = []
    for it in _items(lo, hi):
        it = dict(it, asset=it["asset"] + "_LOD1"); it["parts"] = [dict(p, boxes=lod1(p["boxes"])) for p in it["parts"]]; out.append(it)
    return out
B = int(os.environ.get("BBISLE_BATCH", "0"))
GROUPS = {"bbisle_lod1": items(B * 120, min(500, B * 120 + 120))}
SPECS = GROUPS["bbisle_lod1"]; ORDER = ["bbisle_lod1"]; SIZE = {"bbisle_lod1": "0.5-5 m"}
