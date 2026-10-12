# SPDX-License-Identifier: MIT
"""Dragon Warrior realm: Shard Tyrant (rebuilt), the party (Hero, Sage, Scout), and the cave battle kit, as specs.
Front = -Y. Heights in metres. Blocky but layered: every part is bevelled boxes, 3 flat colours per asset."""
import random

def B(size, centre, m):
    return [list(size), list(centre), m]

def mirror(boxes):
    return [[s, [-c[0], c[1], c[2]], m] for s, c, m in boxes]

# ------------------------------------------------------------------ Shard Tyrant: gold armour, purple crest, silver sword
GOLD, PURPLE, SILVER = 0, 1, 2

def tyrant_leg(x):
    s = 1 if x > 0 else -1
    bx = [
        # boot: sole, foot, toe cap, heel, ankle cuff
        B((0.30, 0.48, 0.05), (x, -0.06, 0.025), PURPLE),
        B((0.28, 0.40, 0.13), (x, -0.04, 0.115), GOLD),
        B((0.24, 0.12, 0.10), (x, -0.30, 0.09), SILVER),
        B((0.22, 0.10, 0.16), (x, 0.17, 0.13), GOLD),
        B((0.30, 0.30, 0.10), (x, 0.0, 0.24), PURPLE),
        # greave (shin plate) with a raised front ridge, knee cop
        B((0.24, 0.24, 0.40), (x, 0.0, 0.49), GOLD),
        B((0.10, 0.05, 0.36), (x, -0.135, 0.49), SILVER),
        B((0.26, 0.12, 0.16), (x, -0.10, 0.74), SILVER),
        B((0.08, 0.05, 0.06), (x, -0.17, 0.74), PURPLE),
        # thigh (cuisse) under the skirt
        B((0.25, 0.25, 0.30), (x, 0.0, 0.92), SILVER),
        B((0.27, 0.27, 0.06), (x, 0.0, 0.80), GOLD),
    ]
    return {"name": "_LegL" if x < 0 else "_LegR", "pivot": [x, 0, 1.05], "boxes": bx}

def tyrant_arm(x):
    s = 1 if x > 0 else -1
    bx = [
        B((0.34, 0.44, 0.20), (x + 0.03 * s, 0, 1.70), GOLD),          # pauldron
        B((0.36, 0.46, 0.05), (x + 0.03 * s, 0, 1.585), PURPLE),       # pauldron trim
        B((0.26, 0.36, 0.08), (x + 0.06 * s, 0, 1.83), GOLD),          # pauldron top step
        B((0.18, 0.18, 0.30), (x, 0, 1.40), SILVER),                    # upper arm
        B((0.21, 0.21, 0.08), (x, 0, 1.24), GOLD),                      # elbow
        B((0.23, 0.23, 0.24), (x, 0, 1.09), GOLD),                      # gauntlet
        B((0.25, 0.25, 0.05), (x, 0, 1.20), PURPLE),                    # gauntlet cuff
        B((0.20, 0.22, 0.14), (x, -0.02, 0.92), SILVER),               # fist
        B((0.04, 0.16, 0.04), (x + 0.11 * s, -0.04, 0.95), GOLD),      # knuckle ridge
    ]
    return {"name": "_ArmL" if x < 0 else "_ArmR", "pivot": [x, 0, 1.70], "boxes": bx}

TYRANT = {"asset": "Mob_Realm_ShardTyrant", "materials": ["F8B800", "8C34C8", "steel"], "glow": [], "parts": [
    {"name": "_Body", "pivot": [0, 0, 1.05], "boxes": [
        B((0.74, 0.44, 0.22), (0, 0, 1.08), PURPLE),           # skirt (fauld)
        B((0.20, 0.06, 0.24), (0, -0.25, 1.02), GOLD),          # tasset front
        B((0.66, 0.40, 0.08), (0, 0, 1.22), GOLD),              # belt
        B((0.12, 0.05, 0.08), (0, -0.22, 1.22), SILVER),        # buckle
        B((0.70, 0.42, 0.42), (0, 0, 1.47), GOLD),              # cuirass
        B((0.54, 0.06, 0.34), (0, -0.23, 1.50), SILVER),        # chest plate
        B((0.14, 0.05, 0.14), (0, -0.27, 1.53), PURPLE),        # crystal gem
        B((0.58, 0.40, 0.08), (0, 0, 1.70), GOLD),              # gorget
        B((0.50, 0.08, 0.40), (0, 0.24, 1.48), PURPLE)]},       # back cape plate
    {"name": "_Head", "pivot": [0, 0, 1.74], "boxes": [
        B((0.42, 0.42, 0.36), (0, 0, 1.93), GOLD),              # helm
        B((0.36, 0.06, 0.06), (0, -0.215, 1.94), PURPLE),       # visor slit
        B((0.44, 0.08, 0.07), (0, -0.21, 2.01), SILVER),        # brow ridge
        B((0.10, 0.06, 0.16), (0, -0.215, 1.83), SILVER),       # nose/mouth guard
        B((0.07, 0.30, 0.20), (-0.215, -0.02, 1.86), SILVER),   # cheek L
        B((0.07, 0.30, 0.20), (0.215, -0.02, 1.86), SILVER),
        B((0.10, 0.44, 0.10), (0, 0, 2.15), GOLD),              # crest base
        B((0.08, 0.40, 0.14), (0, 0.02, 2.25), PURPLE),         # crest
        B((0.08, 0.24, 0.12), (0, 0.20, 2.17), PURPLE),         # plume tail
        B((0.08, 0.14, 0.10), (0, 0.30, 2.07), PURPLE),
        B((0.06, 0.12, 0.18), (-0.24, 0.02, 2.06), SILVER),     # horns
        B((0.06, 0.12, 0.18), (0.24, 0.02, 2.06), SILVER)]},
    tyrant_arm(-0.47), tyrant_arm(0.47), tyrant_leg(-0.20), tyrant_leg(0.20),
    {"name": "_Shield", "pivot": [-0.62, -0.12, 1.00], "boxes": [   # purple oval, gold rim, crystal boss
        B((0.08, 0.06, 1.00), (-0.66, -0.28, 1.05), PURPLE),
        B((0.08, 0.06, 0.88), (-0.66, -0.28, 1.05), PURPLE),
        B((0.44, 0.06, 0.80), (-0.66, -0.25, 1.05), PURPLE),
        B((0.56, 0.05, 0.58), (-0.66, -0.25, 1.05), PURPLE),
        B((0.32, 0.06, 0.94), (-0.66, -0.26, 1.05), PURPLE),
        B((0.60, 0.04, 0.06), (-0.66, -0.29, 1.05), GOLD),
        B((0.06, 0.04, 0.92), (-0.66, -0.29, 1.05), GOLD),
        B((0.16, 0.06, 0.16), (-0.66, -0.31, 1.05), SILVER),
        B((0.36, 0.03, 0.05), (-0.66, -0.285, 1.44), GOLD),
        B((0.36, 0.03, 0.05), (-0.66, -0.285, 0.66), GOLD)]},
    {"name": "_Sword", "pivot": [0.47, -0.02, 0.92], "boxes": [
        B((0.07, 0.07, 0.07), (0.47, -0.02, 0.80), GOLD),               # pommel
        B((0.06, 0.06, 0.20), (0.47, -0.02, 0.92), PURPLE),             # grip
        B((0.36, 0.09, 0.07), (0.47, -0.02, 1.05), GOLD),               # guard
        B((0.07, 0.10, 0.10), (0.30, -0.02, 1.08), GOLD),
        B((0.07, 0.10, 0.10), (0.64, -0.02, 1.08), GOLD),
        B((0.11, 0.04, 0.86), (0.47, -0.02, 1.52), SILVER),             # blade
        B((0.03, 0.05, 0.80), (0.47, -0.02, 1.50), GOLD),               # fuller
        B((0.07, 0.04, 0.08), (0.47, -0.02, 1.99), SILVER),             # tip steps
        B((0.03, 0.04, 0.06), (0.47, -0.02, 2.06), SILVER)]},
]}

# ------------------------------------------------------------------ the party: one humanoid, three outfits
def humanoid(name, mats, extra_parts, hood=False, robe=False, h=1.0):
    C, S, M = 0, 1, 2   # clothes, skin, metal/accent
    z = lambda v: v * h
    leg = lambda x: {"name": "_LegL" if x < 0 else "_LegR", "pivot": [x, 0, z(0.72)], "boxes": [
        B((0.18, 0.30, 0.10), (x, -0.04, z(0.05)), M), B((0.17, 0.18, 0.20), (x, 0, z(0.20)), M),
        B((0.15, 0.15, 0.40), (x, 0, z(0.50)), C)]}
    arm = lambda x: {"name": "_ArmL" if x < 0 else "_ArmR", "pivot": [x, 0, z(1.22)], "boxes": [
        B((0.18, 0.22, 0.14), (x, 0, z(1.20)), M if not robe else C), B((0.13, 0.13, 0.30), (x, 0, z(1.02)), C),
        B((0.14, 0.14, 0.12), (x, 0, z(0.82)), S)]}
    body = [B((0.44, 0.26, 0.48), (0, 0, z(1.00)), C), B((0.46, 0.28, 0.06), (0, 0, z(0.80)), M)]
    if robe:
        body += [B((0.50, 0.34, 0.50), (0, 0, z(0.50)), C), B((0.56, 0.38, 0.12), (0, 0, z(0.28)), C)]
    head = [B((0.30, 0.30, 0.30), (0, 0, z(1.43)), S), B((0.20, 0.04, 0.04), (0, -0.155, z(1.46)), M)]
    if hood:
        head += [B((0.36, 0.36, 0.20), (0, 0.02, z(1.55)), C), B((0.36, 0.10, 0.34), (0, 0.15, z(1.42)), C)]
    else:
        head += [B((0.32, 0.32, 0.10), (0, 0.01, z(1.60)), M)]
    parts = [{"name": "_Body", "pivot": [0, 0, z(0.72)], "boxes": body}, {"name": "_Head", "pivot": [0, 0, z(1.28)], "boxes": head},
             arm(-0.30), arm(0.30)] + ([] if robe else [leg(-0.11), leg(0.11)]) + extra_parts
    return {"asset": name, "materials": mats, "parts": parts}

HERO = humanoid("Mob_Realm_Party_Hero", ["0058F8", "E8C090", "steel"], [
    {"name": "_Sword", "pivot": [0.30, -0.05, 0.82], "boxes": [B((0.05, 0.05, 0.16), (0.30, -0.05, 0.82), 0),
        B((0.22, 0.06, 0.05), (0.30, -0.05, 0.92), 2), B((0.07, 0.03, 0.60), (0.30, -0.05, 1.24), 2)]},
    {"name": "_Shield", "pivot": [-0.36, -0.08, 0.95], "boxes": [B((0.06, 0.40, 0.48), (-0.38, -0.02, 0.95), 2),
        B((0.07, 0.30, 0.36), (-0.40, -0.02, 0.95), 0), B((0.08, 0.06, 0.20), (-0.42, -0.02, 0.95), 2)]}])
SAGE = humanoid("Mob_Realm_Party_Sage", ["F2F3F3", "E8C090", "4B974B"], [
    {"name": "_Staff", "pivot": [0.30, -0.05, 0.82], "boxes": [B((0.06, 0.06, 1.50), (0.30, -0.05, 0.75), 2),
        B((0.16, 0.16, 0.16), (0.30, -0.05, 1.56), 2), B((0.08, 0.08, 0.08), (0.30, -0.05, 1.68), 0)]}], robe=True)
SCOUT = humanoid("Mob_Realm_Party_Scout", ["4B974B", "E8C090", "7A5230"], [
    {"name": "_DaggerR", "pivot": [0.30, -0.05, 0.82], "boxes": [B((0.05, 0.05, 0.10), (0.30, -0.06, 0.80), 2),
        B((0.04, 0.03, 0.26), (0.30, -0.06, 0.66), 0)]},
    {"name": "_DaggerL", "pivot": [-0.30, -0.05, 0.82], "boxes": [B((0.05, 0.05, 0.10), (-0.30, -0.06, 0.80), 2),
        B((0.04, 0.03, 0.26), (-0.30, -0.06, 0.66), 0)]}], hood=True, h=0.95)
# skin is the hood colour's partner; the scout's materials: clothes green, skin, leather

# ------------------------------------------------------------------ the cave kit
DARK, MID, WET = 0, 1, 2

def stalactite(x, y, length, w, rng, m=MID):
    """Layered taper hanging from z=0 down to -length, slightly kinked so no two look alike."""
    out, z, cw, k = [], 0.0, w, 0
    steps = max(3, int(length / 0.18))
    seg = length / steps
    dx = dy = 0.0
    for i in range(steps):
        out.append(B((cw, cw * rng.uniform(0.8, 1.1), seg + 0.02), (x + dx, y + dy, z - seg / 2), m if i % 2 else DARK))
        z -= seg; cw *= 0.80; dx += rng.uniform(-0.02, 0.02); dy += rng.uniform(-0.02, 0.02)
    return out

def ceiling(seed=13):
    rng = random.Random(seed)
    slabs = []
    for i in range(7):                                  # layered rock ceiling: 3 depths of overlapping slabs
        for j, y in enumerate((-1.0, 0.6, 2.2)):
            w = rng.uniform(1.0, 1.5); d = rng.uniform(1.4, 1.8); t = rng.uniform(0.35, 0.65)
            slabs.append(B((w, d, t), (-3.6 + i * 1.2 + rng.uniform(-0.15, 0.15), y, 4.0 + t / 2 + j * 0.15 - rng.uniform(0, 0.2)), DARK if (i + j) % 2 else MID))
    tites = []
    for _ in range(14):
        x, y = rng.uniform(-3.6, 3.6), rng.uniform(-1.3, 2.6)
        L = rng.choice([0.5, 0.8, 1.1, 1.5, 0.35])
        for s, c, m in stalactite(0, 0, L, rng.uniform(0.18, 0.34), rng):
            tites.append([s, [c[0] + x, c[1] + y, c[2] + 4.05], m])
    drips = [B((0.04, 0.04, 0.06), (b[1][0], b[1][1], b[1][2] - b[0][2] / 2 - 0.05), WET) for b in tites[::9]]
    return {"asset": "Prop_Realm_Cave_Ceiling", "materials": ["4A4652", "6E6878", "7FE3FF"], "glow": [2], "parts": [
        {"name": "", "boxes": slabs, "bevel": 0.10}, {"name": "_Stalactites", "boxes": tites + drips, "bevel": 0}]}

def floor(seed=7):
    rng = random.Random(seed)
    tiles = []
    for i in range(8):                          # irregular flagstones, uneven heights (8 x 5 m)
        for j in range(5):
            h = rng.uniform(0.10, 0.22)
            tiles.append(B((0.98 + rng.uniform(-0.06, 0.04), 0.98 + rng.uniform(-0.06, 0.04), h),
                           (-3.5 + i, -1.5 + j + 0.5, h / 2), MID if (i * 3 + j) % 4 else DARK))
    rocks = []
    for _ in range(12):                         # rocks: two stacked boxes
        x, y = rng.uniform(-3.8, 3.8), rng.uniform(-1.4, 3.3)
        s = rng.uniform(0.18, 0.40)
        rocks += [B((s, s * 0.9, s * 0.6), (x, y, 0.22 + s * 0.3), DARK), B((s * 0.6, s * 0.6, s * 0.4), (x + 0.03, y - 0.02, 0.22 + s * 0.8), MID)]
    pebbles = [B((p, p, p * 0.6), (rng.uniform(-3.9, 3.9), rng.uniform(-1.4, 3.4), 0.23), rng.choice([DARK, MID]))
               for p in [rng.uniform(0.05, 0.10) for _ in range(28)]]
    puddles = [B((rng.uniform(0.5, 1.0), rng.uniform(0.3, 0.6), 0.02), (x, y, 0.225), WET) for x, y in ((-2.2, -0.6), (1.6, 0.4), (-0.4, 2.4), (2.9, 2.6))]
    return {"asset": "Prop_Realm_Cave_Floor", "materials": ["3E3A44", "6E6878", "1E4E86"], "parts": [
        {"name": "", "boxes": tiles, "bevel": 0.08}, {"name": "_Rocks", "boxes": rocks, "bevel": 0},
        {"name": "_Pebbles", "boxes": pebbles + puddles, "bevel": 0}]}

def wall(seed=3):
    rng = random.Random(seed)
    cols = []
    for i in range(16):                        # rock columns of varied height and depth: a jagged backdrop
        w = 0.5 + rng.uniform(0, 0.25); h = rng.uniform(3.2, 4.6); d = rng.uniform(0.6, 1.2)
        x = -3.9 + i * 0.52
        cols.append(B((w, d, h), (x, rng.uniform(-0.2, 0.2), h / 2), DARK if i % 3 else MID))
        cols.append(B((w * 0.7, d * 0.6, rng.uniform(0.4, 0.9)), (x + 0.05, -d / 2 - 0.1, rng.uniform(0.3, 2.8)), MID))
    veins = [B((0.10, 0.05, 0.10), (rng.uniform(-3.5, 3.5), -0.65, rng.uniform(0.6, 3.2)), WET) for _ in range(8)]
    return {"asset": "Prop_Realm_Cave_Wall", "materials": ["3A3640", "5E5868", "A070FF"], "glow": [2], "parts": [
        {"name": "", "boxes": cols, "bevel": 0.08}, {"name": "_Crystals", "boxes": veins, "bevel": 0}]}

def stalagmite(seed=5):
    rng = random.Random(seed)
    bx = []
    for k, (x, y, L) in enumerate(((0, 0, 1.4), (0.35, 0.15, 0.8), (-0.3, -0.1, 0.6))):
        for s, c, m in stalactite(0, 0, L, 0.42 - 0.08 * k, rng):
            bx.append([s, [c[0] + x, c[1] + y, -c[2]], m])     # flipped: grows up from z=0
    return {"asset": "Prop_Realm_Cave_Stalagmite", "materials": ["3E3A44", "6E6878", "7FE3FF"], "parts": [{"name": "", "boxes": bx}]}

TORCH = {"asset": "Prop_Realm_Cave_Torch", "materials": ["5A3A22", "7C7C7C", "F87818"], "glow": [2], "parts": [
    {"name": "", "boxes": [B((0.14, 0.14, 0.04), (0, 0, 0.02), 1), B((0.06, 0.06, 1.30), (0, 0, 0.69), 0),
                           B((0.18, 0.18, 0.10), (0, 0, 1.38), 1), B((0.22, 0.22, 0.04), (0, 0, 1.44), 1)]},
    {"name": "_Flame", "pivot": [0, 0, 1.46], "boxes": [B((0.16, 0.16, 0.16), (0, 0, 1.54), 2), B((0.10, 0.10, 0.14), (0.01, 0, 1.68), 2),
                                                       B((0.05, 0.05, 0.10), (0, 0.01, 1.79), 2)], "bevel": 0.2}]}

SPECS = [TYRANT, HERO, SAGE, SCOUT, ceiling(), floor(), wall(), stalagmite(), TORCH]

# where each goes in the composed battle scene (x, y, z, rotation about Z in degrees)
SCENE = [("Prop_Realm_Cave_Floor", 0, 1.0, 0, 0), ("Prop_Realm_Cave_Floor", 0, 5.6, 0.05, 180), ("Prop_Realm_Cave_Wall", 0, 5.4, 0, 0),
         ("Prop_Realm_Cave_Wall", -4.6, 2.6, 0, 80), ("Prop_Realm_Cave_Wall", 4.6, 2.6, 0, -80),
         ("Prop_Realm_Cave_Ceiling", 0, 1.2, 3.3, 0), ("Prop_Realm_Cave_Ceiling", 0.4, 4.2, 3.6, 180),
         ("Prop_Realm_Cave_Stalagmite", -2.9, 3.4, 0.2, 0), ("Prop_Realm_Cave_Stalagmite", 3.1, 3.0, 0.2, 40),
         ("Prop_Realm_Cave_Stalagmite", -3.6, -0.6, 0.2, 120, 0.7),
         ("Prop_Realm_Cave_Torch", -1.9, 4.2, 0.2, 0), ("Prop_Realm_Cave_Torch", 2.1, 4.2, 0.2, 0),
         ("Mob_Realm_ShardTyrant", 0.1, 2.6, 0.2, -8, 1.35),
         ("Mob_Realm_Party_Hero", -0.9, -1.5, 0.2, 165), ("Mob_Realm_Party_Sage", -2.3, -1.2, 0.2, 155), ("Mob_Realm_Party_Scout", 1.7, -1.3, 0.2, 200)]
