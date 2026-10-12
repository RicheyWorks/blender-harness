# SPDX-License-Identifier: MIT
"""Wave 4: the gather -> cook -> mine -> smelt -> refine -> craft loop. Ore nodes per game tier (BlockColors.java hexes),
nuggets and bar stacks (Item_Bar_* already exist), cooking and smelting stations (lit/unlit variants), the missing crafted tools,
and modular Ark parts in three build tiers. No catalog.py import here (catalog imports entries())."""
from assets.flora2 import b

STONE, DEEP = "7D7B84", "4A4F5C"
ORES = [  # (tier, hex, host rock, depth note, rarity)  colours from daedalus-core BlockColors / BLENDER-TEAM-BRIEF
    ("Coal", "34343A", STONE, "-2..-22", "common"), ("Copper", "C8703A", STONE, "-6..-28", "common"),
    ("Iron", "C9B49C", STONE, "-14..-38", "uncommon"), ("Gold", "F2C230", DEEP, "-26..-46", "rare"),
    ("Crystal", "A070FF", DEEP, "deep cave geodes", "rare"), ("Heartstone", "FF8A3D", DEEP, "island heart", "epic"),
    ("Starmetal", "7FE3FF", "2A1840", "LEGENDARY islands, meteor crater", "legendary")]
GLOWY = {"Crystal", "Heartstone", "Starmetal"}
WOOD, DARK, IRON, FIRE = "8C5A2A", "34343A", "707070", "F87818"

def node(c, size, depleted):
    s = {"Small": 0.7, "Large": 1.2}[size]
    bx = [b((s, s * 0.9, s * 0.55), (0, 0, s * 0.275), 0), b((s * 0.7, s * 0.6, s * 0.4), (s * 0.1, -s * 0.05, s * 0.7), 0),
          b((s * 0.4, s * 0.4, s * 0.3), (-s * 0.15, s * 0.1, s * 0.98), 0)]
    if not depleted:
        for i, (x, y, z) in enumerate(((0.36, -0.2, 0.3), (-0.3, -0.38, 0.5), (0.2, 0.3, 0.8), (-0.42, 0.1, 0.25), (0.05, -0.42, 0.75), (0.4, 0.25, 0.55))):
            k = s * (0.18 if i % 2 else 0.24); bx.append(b((k, k, k), (x * s, y * s, z * s), 1))
    else:
        bx += [b((s * 0.12, s * 0.12, s * 0.06), (x * s, y * s, z * s), 2) for x, y, z in ((0.3, -0.3, 0.55), (-0.2, 0.35, 0.3))]
    return bx

def nugget():
    return [b((0.10, 0.08, 0.07), (0, 0, 0.035), 0), b((0.07, 0.06, 0.06), (0.05, 0.03, 0.08), 0), b((0.05, 0.05, 0.04), (-0.04, -0.03, 0.07), 1)]
def barstack():
    out = []
    for z in range(3):
        for i in range(3 - z):
            out.append(b((0.28, 0.12, 0.08), (0, -0.14 + 0.14 * i + 0.07 * z, 0.04 + 0.085 * z), 0 if (i + z) % 2 else 1))
    return out

def stations():
    S = {}
    pot = [b((0.9, 0.9, 0.12), (0, 0, 0.06), 2)] + [b((0.12, 0.12, 0.5), (x, y, 0.3), 2) for x in (-0.38, 0.38) for y in (-0.38, 0.38)] + \
          [b((0.7, 0.7, 0.5), (0, 0, 0.75), 0), b((0.8, 0.8, 0.08), (0, 0, 1.02), 0), b((0.6, 0.6, 0.06), (0, 0, 0.99), 1)]
    S["Prop_CookingPot"] = (("34343A", "A8C060", "707070"), pot, [])
    S["Prop_CookingPot_Lit"] = (("34343A", "A8C060", FIRE), pot + [b((0.4, 0.4, 0.2), (0, 0, 0.22), 2), b((0.2, 0.2, 0.2), (0.05, 0, 0.38), 2)], [2])
    S["Prop_Campfire_Spit"] = ((WOOD, DARK, FIRE), [b((0.9, 0.18, 0.12), (0, 0, 0.06), 0), b((0.18, 0.9, 0.12), (0, 0, 0.12), 0), b((0.4, 0.4, 0.3), (0, 0, 0.25), 2)] +
                              [b((0.08, 0.08, 1.0), (x, 0, 0.5), 0) for x in (-0.6, 0.6)] + [b((1.4, 0.06, 0.06), (0, 0, 0.95), 1), b((0.3, 0.2, 0.2), (0, 0, 0.85), 0)], [2])
    S["Prop_Stove_Stone"] = ((STONE, DARK, FIRE), [b((1.2, 0.9, 0.9), (0, 0, 0.45), 0), b((0.6, 0.06, 0.4), (0, -0.46, 0.35), 1), b((0.5, 0.04, 0.3), (0, -0.47, 0.35), 2),
                             b((0.3, 0.3, 1.0), (0.35, 0.25, 1.4), 0), b((1.0, 0.7, 0.06), (0, 0, 0.93), 1)], [2])
    S["Prop_PrepTable"] = ((WOOD, "E4DDCF", "4B974B"), [b((1.6, 0.8, 0.1), (0, 0, 0.85), 0)] + [b((0.1, 0.1, 0.8), (x, y, 0.4), 0) for x in (-0.7, 0.7) for y in (-0.32, 0.32)] +
                           [b((0.5, 0.35, 0.04), (-0.3, 0, 0.92), 1), b((0.2, 0.2, 0.15), (0.4, 0.1, 0.97), 2), b((0.15, 0.15, 0.1), (0.15, -0.15, 0.95), 2)], [])
    S["Prop_BrewingStill"] = ((("C8703A"), "A8D8E8", WOOD), [b((0.6, 0.6, 0.7), (0, 0, 0.35), 0), b((0.3, 0.3, 0.3), (0, 0, 0.85), 0), b((0.6, 0.08, 0.08), (0.35, 0, 0.95), 0),
                             b((0.08, 0.08, 0.5), (0.65, 0, 0.7), 0), b((0.3, 0.3, 0.35), (0.7, 0, 0.18), 1), b((1.6, 0.8, 0.06), (0.3, 0, 0.03), 2)], [])
    smelter = [b((1.4, 1.4, 1.0), (0, 0, 0.5), 0), b((1.1, 1.1, 0.8), (0, 0, 1.4), 0), b((0.8, 0.8, 0.6), (0, 0, 2.1), 0), b((0.4, 0.4, 0.6), (0, 0, 2.7), 2),
               b((0.6, 0.06, 0.5), (0, -0.71, 0.45), 2), b((0.3, 0.6, 0.12), (0, -0.95, 0.2), 1)]
    S["Prop_Smelter"] = ((STONE, IRON, DARK), smelter, [])
    S["Prop_Smelter_Lit"] = ((STONE, IRON, FIRE), smelter, [2])
    forge = [b((1.6, 1.0, 0.8), (0, 0, 0.4), 0), b((1.2, 0.7, 0.1), (0, 0, 0.85), 2), b((0.5, 0.5, 1.6), (0, 0.3, 1.6), 0), b((0.7, 0.7, 0.2), (0, 0.3, 2.5), 1),
             b((0.5, 0.25, 0.25), (0.95, 0, 0.6), 1)]
    S["Prop_Forge"] = ((STONE, IRON, DARK), forge, [])
    S["Prop_Forge_Lit"] = ((STONE, IRON, FIRE), forge, [2])
    S["Prop_Bellows"] = ((WOOD, "8C5A3A", IRON), [b((0.7, 0.4, 0.12), (0, 0, 0.3), 0), b((0.6, 0.38, 0.2), (0, 0, 0.45), 1), b((0.7, 0.4, 0.12), (0, 0, 0.6), 0),
                        b((0.3, 0.08, 0.08), (0.5, 0, 0.45), 2), b((0.08, 0.3, 0.04), (-0.45, 0, 0.62), 0)], [])
    S["Prop_Crucible"] = ((DARK, FIRE, IRON), [b((0.45, 0.45, 0.4), (0, 0, 0.2), 0), b((0.5, 0.5, 0.06), (0, 0, 0.42), 0), b((0.36, 0.36, 0.04), (0, 0, 0.41), 1),
                         b((0.6, 0.06, 0.06), (0, 0, 0.3), 2)], [1])
    S["Prop_IngotMold"] = ((IRON, DARK, "C9B49C"), [b((0.9, 0.4, 0.1), (0, 0, 0.05), 0)] + [b((0.22, 0.28, 0.03), (x, 0, 0.11), 1) for x in (-0.28, 0, 0.28)] +
                          [b((0.2, 0.26, 0.04), (0.28, 0, 0.12), 2)], [])
    S["Prop_QuenchTrough"] = ((WOOD, "2F80D8", IRON), [b((1.4, 0.6, 0.5), (0, 0, 0.25), 0), b((1.3, 0.5, 0.04), (0, 0, 0.47), 1), b((1.44, 0.04, 0.06), (0, -0.3, 0.3), 2), b((1.44, 0.04, 0.06), (0, 0.3, 0.3), 2)], [])
    S["Prop_RareRefinery"] = ((DEEP, "7FE3FF", "A070FF"), [b((1.6, 1.6, 0.3), (0, 0, 0.15), 0), b((1.0, 1.0, 1.2), (0, 0, 0.9), 0), b((0.5, 0.5, 0.5), (0, 0, 1.75), 1),
                             b((0.12, 0.12, 1.4), (0.65, 0.65, 1.0), 2), b((0.12, 0.12, 1.4), (-0.65, -0.65, 1.0), 2), b((0.8, 0.06, 0.6), (0, -0.52, 0.7), 1)], [1])
    S["Prop_Anvil_Starmetal"] = ((("2A1840"), "7FE3FF", IRON), [b((0.5, 0.4, 0.15), (0, 0, 0.075), 0), b((0.25, 0.2, 0.4), (0, 0, 0.35), 0), b((0.8, 0.3, 0.18), (0, 0, 0.64), 1), b((0.25, 0.15, 0.1), (0.5, 0, 0.66), 1)], [1])
    S["Prop_StorageCrate_Ore"] = ((WOOD, DARK, "C8703A"), [b((1.0, 0.8, 0.6), (0, 0, 0.3), 0), b((1.04, 0.84, 0.06), (0, 0, 0.6), 1)] + [b((0.2, 0.2, 0.15), (x, y, 0.68), 2) for x, y in ((-0.25, 0), (0.1, 0.15), (0.3, -0.15))], [])
    return S

TIERS = [("Copper", "C8703A"), ("Iron", "C9B49C"), ("Gold", "F2C230"), ("Crystal", "A070FF"), ("Starmetal", "7FE3FF")]
def sickle(): return [b((0.04, 0.04, 0.32), (0, 0, 0.16), 0), b((0.06, 0.06, 0.05), (0, 0, 0.34), 1), b((0.05, 0.03, 0.1), (0.02, 0, 0.4), 2), b((0.08, 0.03, 0.05), (0.08, 0, 0.47), 2),
                      b((0.12, 0.03, 0.05), (0.18, 0, 0.51), 2), b((0.06, 0.03, 0.05), (0.28, 0, 0.49), 2), b((0.04, 0.03, 0.06), (0.32, 0, 0.44), 2)]
TOOLS = {
    "Tool_Tongs": ((IRON, DARK, IRON), [b((0.03, 0.03, 0.55), (x, 0, 0.3), 0) for x in (-0.03, 0.03)] + [b((0.1, 0.04, 0.04), (0, 0, 0.3), 1), b((0.08, 0.04, 0.06), (0, 0, 0.6), 2)]),
    "Tool_Prospector": ((DARK, "7FE3FF", "C8703A"), [b((0.05, 0.05, 0.4), (0, 0, 0.2), 0), b((0.2, 0.06, 0.14), (0, 0, 0.47), 2), b((0.3, 0.3, 0.03), (0, -0.12, 0.62), 1), b((0.06, 0.06, 0.08), (0, 0, 0.55), 1)]),
    "Tool_Ladle": ((WOOD, IRON, DARK), [b((0.04, 0.04, 0.5), (0, 0, 0.25), 0), b((0.16, 0.16, 0.08), (0, -0.05, 0.54), 1)]),
    "Tool_Chisel": ((WOOD, IRON, DARK), [b((0.05, 0.05, 0.15), (0, 0, 0.075), 0), b((0.03, 0.03, 0.12), (0, 0, 0.21), 1), b((0.04, 0.01, 0.04), (0, 0, 0.29), 1)]),
}
ARK_TIERS = [("Wood", "8C5A2A", "6B4A2A", "C8A070"), ("Iron", "707070", "4A4A4A", "C9B49C"), ("Starmetal", "2A1840", "7FE3FF", "C0C0C0")]
def ark_parts():
    P = {  # modular on a 2 m grid, origin bottom-centre, -Y = bow
        "Hull_Bow": [b((3.0, 1.0, 1.4), (0, 0.5, 0.7), 0), b((2.2, 0.8, 1.2), (0, -0.4, 0.8), 0), b((1.2, 0.8, 1.0), (0, -1.2, 0.9), 0), b((0.4, 0.6, 0.8), (0, -1.8, 1.0), 1)],
        "Hull_Mid": [b((3.0, 2.0, 1.4), (0, 0, 0.7), 0), b((3.1, 2.0, 0.12), (0, 0, 1.4), 1), b((3.1, 0.12, 0.3), (0, -0.95, 0.7), 1)],
        "Hull_Stern": [b((3.0, 2.0, 1.4), (0, 0, 0.7), 0), b((3.0, 0.3, 2.2), (0, 0.85, 1.1), 0), b((1.0, 0.1, 0.6), (0, 1.02, 1.6), 2)],
        "Deck": [b((3.0, 2.0, 0.12), (0, 0, 0.06), 2)] + [b((0.04, 2.0, 0.02), (x, 0, 0.13), 1) for x in (-1.0, -0.33, 0.33, 1.0)],
        "Railing": [b((0.1, 0.1, 0.9), (0, y, 0.45), 0) for y in (-0.95, 0, 0.95)] + [b((0.08, 2.0, 0.08), (0, 0, 0.9), 1)],
        "Mast": [b((0.25, 0.25, 6.0), (0, 0, 3.0), 0), b((2.8, 0.15, 0.15), (0, 0, 5.2), 0), b((0.5, 0.5, 0.3), (0, 0, 6.1), 1)],
        "Sail": [b((2.6, 0.08, 3.6), (0, 0, 1.8), 2), b((2.7, 0.12, 0.12), (0, 0, 3.6), 0), b((2.7, 0.12, 0.12), (0, 0, 0.0 + 0.06), 0)],
        "Rudder": [b((0.15, 1.0, 1.6), (0, 0, 0.8), 0), b((0.2, 0.2, 0.6), (0, -0.5, 1.9), 1)],
        "Helm": [b((0.2, 0.2, 1.0), (0, 0, 0.5), 0), b((0.9, 0.08, 0.9), (0, -0.1, 1.2), 1)] + [b((0.06, 0.06, 1.1), (0, -0.12, 1.2), 0)],
        "Cabin": [b((2.4, 2.0, 2.0), (0, 0, 1.0), 0), b((2.8, 2.4, 0.2), (0, 0, 2.1), 1), b((0.8, 0.1, 1.5), (0, -1.02, 0.75), 2), b((0.5, 0.1, 0.5), (0.8, -1.02, 1.3), 2)],
        "Balloon": [b((2.6, 4.0, 2.0), (0, 0, 3.0), 2), b((3.0, 3.2, 1.6), (0, 0, 3.0), 2), b((0.08, 0.08, 2.0), (1.0, 0, 1.0), 0), b((0.08, 0.08, 2.0), (-1.0, 0, 1.0), 0)],
        "Propeller": [b((0.4, 0.5, 0.4), (0, 0.25, 0.2), 0), b((0.15, 0.2, 0.15), (0, -0.05, 0.2), 1), b((1.6, 0.06, 0.2), (0, -0.16, 0.2), 1), b((0.2, 0.06, 1.6), (0, -0.16, 0.2), 1)],
        "Engine": [b((1.6, 1.2, 1.0), (0, 0, 0.5), 0), b((0.6, 0.6, 0.8), (-0.4, 0, 1.4), 1), b((0.3, 1.3, 0.3), (0.5, 0, 0.8), 1), b((0.5, 0.06, 0.5), (0, -0.62, 0.5), 2)],
        "Anchor": [b((0.12, 0.12, 1.2), (0, 0, 0.7), 0), b((0.8, 0.12, 0.12), (0, 0, 0.12), 0), b((0.15, 0.12, 0.3), (0.38, 0, 0.25), 0), b((0.15, 0.12, 0.3), (-0.38, 0, 0.25), 0), b((0.4, 0.12, 0.1), (0, 0, 1.2), 1)],
        "Wing_L": [b((3.0, 1.2, 0.15), (-1.6, 0, 0.5), 0), b((1.6, 0.8, 0.12), (-3.4, 0.2, 0.5), 2), b((0.2, 0.2, 1.0), (-0.1, 0, 0.5), 1)],
        "Wing_R": [b((3.0, 1.2, 0.15), (1.6, 0, 0.5), 0), b((1.6, 0.8, 0.12), (3.4, 0.2, 0.5), 2), b((0.2, 0.2, 1.0), (0.1, 0, 0.5), 1)],
        "ShieldCore_Housing": [b((1.2, 1.2, 0.3), (0, 0, 0.15), 0), b((0.8, 0.8, 0.8), (0, 0, 0.7), 1), b((0.5, 0.5, 0.5), (0, 0, 0.7), 2), b((1.0, 1.0, 0.15), (0, 0, 1.15), 0)],
        "DockClamp": [b((1.0, 0.6, 0.3), (0, 0, 0.15), 0), b((0.2, 0.6, 1.0), (-0.4, 0, 0.8), 1), b((0.2, 0.6, 1.0), (0.4, 0, 0.8), 1), b((0.9, 0.3, 0.15), (0, 0, 1.2), 0)],
        "Lantern_Post": [b((0.12, 0.12, 2.0), (0, 0, 1.0), 0), b((0.4, 0.4, 0.4), (0, 0, 2.1), 2), b((0.5, 0.5, 0.08), (0, 0, 2.34), 1)],
    }
    return P
GLOWPART = {"Engine": [2], "ShieldCore_Housing": [2], "Lantern_Post": [2]}

def S(asset, mats, boxes, glow=()): return {"asset": asset, "materials": list(mats), "glow": list(glow), "parts": [{"name": "", "boxes": boxes}]}

def specs():
    g = {"stations": [], "ore_nodes": [], "ark_parts": [], "tools": [], "metal_items": []}
    for n, (m, bx, gl) in stations().items(): g["stations"].append(S(n, m, bx, gl))
    for t, c, rock, _, _ in ORES:
        for size in ("Small", "Large"):
            g["ore_nodes"].append(S("Prop_OreNode_%s_%s" % (t, size), (rock, c, DARK), node(c, size, False), [1] if t in GLOWY else []))
        g["ore_nodes"].append(S("Prop_OreNode_%s_Depleted" % t, (rock, c, DARK), node(c, "Small", True)))
    for part, bx in ark_parts().items():
        for tn, a, bcol, c in ARK_TIERS:
            gl = GLOWPART.get(part, []) if tn == "Starmetal" or part in ("Lantern_Post",) else []
            mats = (a, bcol, "F4F0E0" if part in ("Sail", "Balloon") else c) if part in ("Sail", "Balloon") else (a, bcol, c)
            g["ark_parts"].append(S("Veh_ArkPart_%s_%s" % (part, tn), mats, bx, gl))
    for t, c in TIERS: g["tools"].append(S("Tool_Sickle_" + t, (WOOD, DARK, c), sickle(), [2] if t in ("Crystal", "Starmetal") else []))
    for n, (m, bx) in TOOLS.items(): g["tools"].append(S(n, m, bx, [1] if n == "Tool_Prospector" else []))
    for t, c, *_ in ORES:
        g["metal_items"].append(S("Item_Nugget_" + t, (c, c if t != "Coal" else "4A4A50", DARK), nugget(), [0] if t in GLOWY else []))
    for t, c in [("Copper", "C8703A"), ("Iron", "C9B49C"), ("Gold", "F2C230"), ("Starmetal", "7FE3FF"), ("Heartstone", "FF8A3D")]:
        g["metal_items"].append(S("Item_BarStack_" + t, (c, c, DARK), barstack(), [0] if t in GLOWY else []))
    g["metal_items"].append(S("Item_Bar_Heartstone", ("FF8A3D", "FFB070", DARK), [b((0.28, 0.12, 0.08), (0, 0, 0.04), 0), b((0.24, 0.1, 0.02), (0, 0, 0.09), 1)], [0]))
    return g

ORDER = ["ore_nodes", "stations", "ark_parts", "tools", "metal_items"]   # most visible first
SIZE = {"ore_nodes": "0.7-1.2 m", "stations": "~1-3 m", "ark_parts": "2 m grid", "tools": "~0.4-0.6 m", "metal_items": "~0.3 m"}
KIND = {"Prop": "prop", "Item": "item", "Tool": "tool", "Veh": "vehicle"}
MECH = {"ore_nodes": ("Mining", "ore node; mine with pickaxe tier >= ore"), "stations": ("Stations", "cook / smelt / refine station"),
        "ark_parts": ("Vehicles", "modular Ark part (2 m grid)"), "tools": ("Tools", "crafted tool"), "metal_items": ("Gatherables", "smelting material")}

def entries():
    out = []
    for grp in ORDER:
        cat, mech = MECH[grp]
        for s in specs()[grp]:
            out.append(dict(name=s["asset"], category="Gatherables" if cat == "Mining" else cat, world="Shattered islands (all)", mechanic=mech,
                            drops="", tier="", parts="", priority=2, notes="wave 4 (gameplay loop)"))
    return out

_G = None
def __getattr__(name):
    global _G
    if name in ("GROUPS", "SPECS"):
        if _G is None: _G = specs()
        return _G if name == "GROUPS" else [x for v in _G.values() for x in v]
    raise AttributeError(name)
