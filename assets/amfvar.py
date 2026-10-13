# SPDX-License-Identifier: MIT
"""AMF request 2026-10-12: water bowl + hay bale variants V2-V4 (6 assets)."""
def b(s, c, m=0): return [list(s), list(c), m]
def bowl(v):
    r = [0.28, 0.36, 0.46][v-2]; h = [0.10, 0.12, 0.16][v-2]
    o = [b((r, r, h), (0, 0, h/2), 0), b((r*0.82, r*0.82, 0.02), (0, 0, h-0.005), 1)]
    if v >= 3: o.append(b((r*1.1, r*1.1, 0.03), (0, 0, 0.015), 2))          # rubber base ring
    if v == 4: o += [b((0.05, 0.12, 0.2), (r/2+0.02, 0, 0.1), 2), b((0.08, 0.08, 0.06), (r/2+0.02, 0, 0.23), 0)]   # refill tank nozzle
    return o
def hay(v):
    w, d, h = [(1.0, 0.5, 0.45), (1.2, 0.6, 0.6), (1.4, 1.4, 1.2)][v-2]
    o = [b((w, d, h), (0, 0, h/2), 0)]
    for x in ((-w/3, w/3) if v < 4 else (-w/3, 0, w/3)): o.append(b((0.04, d*1.02, h*1.02), (x, 0, h/2), 1))   # twine
    if v >= 3: o.append(b((w*0.9, d*0.9, 0.06), (0, 0, h+0.03), 2))         # loose straw top
    return o
BOWL = [("8CA0B4", "2F80D8", "34343A"), ("C8703A", "2F80D8", "4A4F5C"), ("F4F6FB", "4FC3F7", "E05050")]
HAY = [("D8B860", "8C5A2A", "E8D890"), ("C8A850", "6B4A2A", "E0C878"), ("B89840", "4A3A2A", "D8C070")]
GROUPS = {"amfvar": [{"asset": "Prop_PetWaterBowl_V%d" % v, "materials": list(BOWL[v-2]), "glow": [], "parts": [{"name": "", "boxes": bowl(v)}]} for v in (2, 3, 4)] +
                    [{"asset": "Prop_HayBale_V%d" % v, "materials": list(HAY[v-2]), "glow": [], "parts": [{"name": "", "boxes": hay(v)}]} for v in (2, 3, 4)]}
SPECS = GROUPS["amfvar"]; ORDER = ["amfvar"]; SIZE = {"amfvar": "0.3-1.4 m"}
