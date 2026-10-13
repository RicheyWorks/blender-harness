# SPDX-License-Identifier: MIT
"""Hephaestus landmark requests (QUEUE rows 1360-1366): asteroid impact site, ark wreck, Team Grok monolith + seed pod.
Box specs, metres, <=3 material slots (slot 2 = emissive glow)."""
import math, random
def b(s, c, m=0): return [list(s), list(c), m]
def rock(r, n, R, z0=0.0, m=0, spread=1.0):
    out = []
    for i in range(n):
        a = r.uniform(0, 6.283); d = r.uniform(0, R * spread); s = r.uniform(0.35, 0.8) * R
        out.append(b((s, s * r.uniform(0.6, 1.1), s * r.uniform(0.5, 0.9)), (d * math.cos(a), d * math.sin(a), z0 + s * 0.3), m))
    return out
def core():
    r = random.Random(1360); bx = rock(r, 14, 3.2, 0.6)
    bx += [b((0.35, 0.35, r.uniform(1.5, 3.2)), (r.uniform(-2, 2), r.uniform(-2, 2), r.uniform(1.5, 3.5)), 2) for _ in range(9)]   # crystal veins
    bx += [b((8, 8, 0.5), (0, 0, 0.0), 1)]                                                                                          # scorched bed
    return bx
def chunk(seed, R):
    r = random.Random(seed); bx = rock(r, 6, R * 1.05, 0.0, 0, 0.45)
    bx += [b((0.12 * R, 0.12 * R, 0.45 * R), (r.uniform(-R/4, R/4), r.uniform(-R/4, R/4), 0.35 * R), 2) for _ in range(2)]
    return bx
def rim():
    r = random.Random(1363); bx = [b((3.0, 1.2, 1.4), (0, 0, 0.7), 0), b((2.2, 1.0, 1.0), (0.3, 0.1, 1.6), 0), b((1.0, 0.9, 0.7), (-1.1, 0.2, 2.0), 1)]
    bx += [b((0.5, 0.4, 0.3), (r.uniform(-1.4, 1.4), r.uniform(-0.6, 0.6), 1.45 + r.uniform(0, 0.8)), 1) for _ in range(5)]
    return bx
def wreck():
    bx = []
    for i in range(10):   # hull broken into tilting segments along 20 m
        x = -9 + i * 2; tilt = 0.25 * math.sin(i * 1.3)
        if i in (4, 5): continue                                      # the break
        bx += [b((1.9, 5.0 - abs(i - 4.5) * 0.25, 3.2), (x, tilt * 2, 1.6 + tilt), 0), b((1.9, 0.3, 1.0), (x, 2.5, 3.4 + tilt), 1)]
    bx += [b((0.4, 7.0, 0.4), (-2, 0, 4.6), 1), b((0.4, 0.4, 6.0), (2.5, -1.0, 3.8), 1), b((2.6, 2.6, 1.4), (9.4, 0, 1.4), 0),
           b((0.8, 0.8, 0.8), (-9.6, 0, 1.6), 2), b((6, 0.25, 0.8), (1, -3.2, 0.5), 1)]   # spar, mast, bow, dead engine glow, torn plate
    return bx
def monolith():
    bx = [b((2.0, 1.0, 6.0), (0, 0, 3.0), 0), b((2.6, 1.6, 0.4), (0, 0, 0.2), 1)]
    for k in range(5): bx.append(b((2.06, 1.06, 0.18), (0, 0, 1.0 + k * 1.05), 2 if k % 2 == 0 else 1))   # carved Turing-coat stripes
    return bx
def seedpod():
    bx = [b((3.2, 3.2, 0.5), (0, 0, 0.25), 1)]
    for k, (w, z) in enumerate(((1.6, 0.9), (2.4, 1.6), (2.8, 2.4), (2.4, 3.1), (1.4, 3.7))): bx.append(b((w, w, 0.8), (0, 0, z), 2 if k == 2 else 0))
    for a in range(6):
        t = a * 1.047; bx.append(b((0.3, 0.3, 2.2), (1.5 * math.cos(t), 1.5 * math.sin(t), 1.4), 1))   # cradle ribs
    return bx
PAL_ROCK = ["3A3530", "1E1A18", "4FE3D0"]
SPECS = [
    {"asset": "Prop_Asteroid_Core", "materials": PAL_ROCK, "glow": [2], "parts": [{"name": "", "boxes": core()}]},
    {"asset": "Prop_Asteroid_Chunk_Small", "materials": PAL_ROCK, "glow": [2], "parts": [{"name": "", "boxes": chunk(1361, 1.5)}]},
    {"asset": "Prop_Asteroid_Chunk_Large", "materials": PAL_ROCK, "glow": [2], "parts": [{"name": "", "boxes": chunk(1362, 4.0)}]},
    {"asset": "Prop_Crater_RimRock", "materials": ["4A4038", "1A1614", "FF6A3D"], "glow": [], "parts": [{"name": "", "boxes": rim()}]},
    {"asset": "Prop_ArkWreck_Hull", "materials": ["6E7378", "3A3F44", "FF8A3D"], "glow": [2], "parts": [{"name": "", "boxes": wreck()}]},
    {"asset": "Prop_Grok_Monolith", "materials": ["16181C", "F4F6FB", "E8772E"], "glow": [2], "parts": [{"name": "", "boxes": monolith()}]},
    {"asset": "Prop_Grok_SeedPod", "materials": ["2A2420", "4A3F36", "FF7A1A"], "glow": [2], "parts": [{"name": "", "boxes": seedpod()}]},
]
GROUPS = {"hephland": SPECS}; ORDER = ["hephland"]; SIZE = {"hephland": "1.5-20 m"}
