# SPDX-License-Identifier: MIT
"""Flora wave 2: gatherable plants with Zelda-style recipe uses. Each species gives three assets:
  Prop_<Kind>_<Name>            growing (ready to harvest: flowers / berries / caps / fruit showing)
  Prop_<Kind>_<Name>_Harvested  picked state (stubs, leaves only; regrows)
  Item_<Kind>_<Name>            the gathered ingredient
Kinds: Herb, Shroom, Bloom, Berry, Root, Vine, Moss, Fern, Cactus, Aqua, Xeno (other-world).
This module has no imports from catalog.py (catalog.py imports it)."""
import hashlib

def h(n, k): return int(hashlib.md5((n + str(k)).encode()).hexdigest()[:6], 16) / 0xFFFFFF
def b(s, c, m=0): return [list(s), list(c), m]

TF, GF, DS, TU, SW, OC, JG, MC, SF = ("Temperate forest", "Grassland / farm", "Desert", "Tundra", "Swamp / wetland",
                                      "Ocean / reef", "Jungle", "Mountain / caves", "Starfall (other world)")
# (name, kind, biome, leaf/body colour, accent colour, recipe use)
SPECIES = [
 # herbs: medicinal / culinary / magical
 ("Chamomile", "Herb", GF, "6CA040", "F8F0C0", "Calm Tea: +stamina regen (with Item_Honey)"),
 ("Yarrow", "Herb", GF, "6B8C2F", "F4F6FB", "Field Salve: heal 3 hearts (with Item_Cloth)"),
 ("Basil", "Herb", GF, "3C9C30", "59D940", "Hearty Stew: +2 max hearts temp (with Item_Meat, Item_Crop_Tomato)"),
 ("Lavender", "Herb", GF, "6B8C5A", "A070E0", "Sleep Draught: restful bed, full stamina"),
 ("Rosemary", "Herb", TF, "4B6B3A", "8CA0D0", "Roast Herb Meat: heal 5 hearts"),
 ("Valerian", "Herb", TF, "5A8040", "F4D0E0", "Quiet Elixir: sneak (foes notice later)"),
 ("Nettle", "Herb", TF, "3A7A2A", "8CC040", "Nettle Soup: cold resist (with Item_Milk)"),
 ("Wormwood", "Herb", DS, "9CB080", "C8C080", "Antivenom: cure scorpion/snake poison"),
 ("Saltbush", "Herb", DS, "A0A890", "E4DDCF", "Cured Jerky: food that never spoils"),
 ("Arctic Thyme".replace(" ", ""), "Herb", TU, "6B8060", "C080C0", "Warming Tea: cold resist 3 min"),
 ("Angelica", "Herb", TU, "6CA040", "F4F6FB", "Revive Tonic: auto-revive once (with Item_Gem_Ruby)"),
 ("Marshmallow", "Herb", SW, "6B9C50", "F8D8E8", "Soothing Paste: cure burn"),
 ("Watercress", "Herb", SW, "2C8C18", "F4F6FB", "Fresh Salad: heal 2 hearts, fast to cook"),
 ("Lemongrass", "Herb", JG, "8CC040", "C8D860", "Jungle Curry: heat resist (with Item_Crop_Rice)"),
 ("Cinchona", "Herb", JG, "4B7B3A", "D82800", "Fever Bark Tonic: cure swamp fever"),
 ("Edelwort", "Herb", MC, "8C9C80", "F4F6FB", "Climber's Brew: +climb speed"),
 ("Moonpetal", "Herb", SF, "5C6CA0", "D7B8FF", "Star Draught: see in the dark (glows)"),
 ("Voidleaf", "Herb", SF, "3A2A5C", "7FE3FF", "Phase Tonic: brief invulnerability"),
 # mushrooms
 ("Chanterelle", "Shroom", TF, "F0E6D0", "F2A830", "Golden Omelette: +attack (with Item_Egg)"),
 ("Morel", "Shroom", TF, "F0E6D0", "8C6A40", "Forager's Pie: heal 4 hearts"),
 ("Puffball", "Shroom", GF, "F4F0E0", "E4DDCF", "Smoke Bomb ingredient: escape battle"),
 ("Inkcap", "Shroom", SW, "F0E6D0", "34343A", "Item_Dye black; Ink Potion: stealth"),
 ("Bogbell", "Shroom", SW, "D8C8B0", "8CC040", "Swamp Stew: poison resist"),
 ("Ghostcap", "Shroom", MC, "E8E8F4", "A8D8E8", "Spirit Lamp fuel (glows)"),
 ("Embercap", "Shroom", MC, "F0E6D0", "F87818", "Spicy Skewer: cold resist"),
 ("Sporelight", "Shroom", SF, "D7B8FF", "7FE3FF", "Lumen Elixir: light radius (glows)"),
 # flowers
 ("Silent Princess".replace(" ", ""), "Bloom", TF, "4B7B3A", "C0D0FF", "Calming Elixir: rare; quest flower"),
 ("Cornflower", "Bloom", GF, "4B974B", "2C6CF8", "Item_Dye blue; Fleet Tea: +speed"),
 ("Marigold", "Bloom", GF, "4B974B", "F8A818", "Item_Dye orange; Pest-ward for crops"),
 ("Fireweed", "Bloom", TU, "4B7B3A", "E040A0", "Warm Elixir: cold resist"),
 ("Ghost Orchid".replace(" ", ""), "Bloom", SW, "6B8C5A", "F4F6FB", "Night Vision Elixir"),
 ("Bird of Paradise".replace(" ", ""), "Bloom", JG, "2C8C18", "F87818", "Feather charm: glide farther"),
 ("Desert Marigold".replace(" ", ""), "Bloom", DS, "8CA060", "F5CD30", "Sun Tea: heat resist"),
 ("Starbloom", "Bloom", SF, "3A4C8C", "FFE25A", "Wish Elixir: +luck (glows)"),
 # berries (bushes)
 ("Blackberry", "Berry", TF, "3A7A2A", "2A1840", "Bramble Jam: heal 3 hearts (with Item_Honey)"),
 ("Elderberry", "Berry", TF, "4B7B3A", "3C2C5C", "Elder Syrup: cure cold sickness"),
 ("Gooseberry", "Berry", GF, "4B974B", "A8D860", "Tart Pie: +stamina"),
 ("Juniper Berry".replace(" ", ""), "Berry", MC, "3A6B4A", "4A6CB0", "Hunter's Spice: meat dishes x2"),
 ("Crowberry", "Berry", TU, "2C5C3A", "202024", "Tundra Mash: cold resist"),
 ("Goji", "Berry", DS, "8C9C60", "E03020", "Vigor Mix: +max stamina temp"),
 ("Acai", "Berry", JG, "2C8C18", "4A2A6C", "Power Bowl: +attack"),
 ("Glowberry", "Berry", MC, "4B6B3A", "FFD040", "Cave Lantern snack (glows)"),
 # roots
 ("Ginseng", "Root", TF, "4B974B", "E8C890", "Vitality Elixir: +max hearts temp"),
 ("Mandrake", "Root", SW, "4B6B3A", "C8A070", "Scream Potion: stun foes (magical)"),
 ("Turmeric", "Root", JG, "4B974B", "F8A818", "Golden Curry: heal + cure poison"),
 ("Wasabi", "Root", MC, "59D940", "A8D860", "Fire Sushi: +attack (with Fish)"),
 ("Desert Yam".replace(" ", ""), "Root", DS, "8CA060", "C87850", "Baked Yam: heal 3 hearts"),
 # vines
 ("Ivy", "Vine", TF, "2C6B3A", "4B974B", "Climbing Rope recipe (with Item_String)"),
 ("Passionflower", "Vine", JG, "2C8C18", "A070E0", "Passion Fruit Tea: +stamina regen"),
 ("Grapevine", "Vine", GF, "4B7B3A", "6A3C8C", "Grape Juice: heal 2 hearts; Item_Dye purple"),
 ("Glowvine", "Vine", MC, "2C5C3A", "7FE3FF", "Cave light strand (glows)"),
 # mosses
 ("Sphagnum", "Moss", SW, "8CC040", "C8D860", "Bandage moss: heal over time"),
 ("Reindeer Moss".replace(" ", ""), "Moss", TU, "C8C8B0", "E4DDCF", "Animal feed: tame caribou"),
 ("Lumimoss", "Moss", MC, "4B6B3A", "59D940", "Glow paint for signs (glows)"),
 # ferns
 ("Bracken", "Fern", TF, "4B7B3A", "8C6A40", "Thatch roofing; fern bedding"),
 ("Fiddlehead", "Fern", SW, "59A040", "8CC040", "Spring Stir-fry: heal 2 hearts"),
 ("Tree Fern".replace(" ", ""), "Fern", JG, "2C8C18", "6B4A2A", "Fiber for Item_String"),
 ("Silverfern", "Fern", SF, "A8B8D0", "F4F6FB", "Silver Tincture: magic defense"),
 # cacti
 ("Barrel Cactus".replace(" ", ""), "Cactus", DS, "4B974B", "F29BC0", "Cactus Water: hydrate in desert heat"),
 ("Cholla", "Cactus", DS, "8CA060", "F2C230", "Spike trap material"),
 ("Peyotl", "Cactus", DS, "6B8C7A", "F4D0E0", "Vision Brew: reveal hidden doors (magical)"),
 # aquatic
 ("Seagrape", "Aqua", OC, "2C8C18", "59D940", "Brine Snack: heal 1 heart, swim stamina"),
 ("Kelpbloom", "Aqua", OC, "6B8C2F", "F2C230", "Diver's Tea: hold breath longer"),
 ("Duckweed", "Aqua", SW, "8CC040", "59D940", "Fish bait; compost booster"),
 ("Arrowhead", "Aqua", SW, "3C9C30", "F4F6FB", "Tuber starch: Item_Bread alt"),
 ("Sea Lettuce".replace(" ", ""), "Aqua", OC, "59D940", "A8D860", "Ocean Salad: heal 2 hearts"),
 # other-world
 ("Crystalthorn", "Xeno", SF, "5C389E", "A070FF", "Item_Crystal shards on harvest (glows)"),
 ("Gravpod", "Xeno", SF, "3A4C8C", "7FE3FF", "Float Potion: low gravity jump"),
 ("Nebulily", "Xeno", SF, "2A1840", "F29BC0", "Nebula Dye; Star Map ink (glows)"),
 ("Meteor Moss".replace(" ", ""), "Xeno", SF, "6B6470", "F87818", "Heat core for Prop_Starforge"),
]
GLOW = {"Moonpetal", "Voidleaf", "Ghostcap", "Sporelight", "Starbloom", "Glowberry", "Glowvine", "Lumimoss", "Crystalthorn", "Gravpod", "Nebulily", "MeteorMoss"}

def entries():
    out = []
    for n, k, bi, c1, c2, use in SPECIES:
        cat = "Other Worlds" if bi == SF else "Flora"
        out.append(dict(name="Prop_%s_%s" % (k, n), category=cat, world=bi, mechanic="Gathering: harvest -> Item_%s_%s (regrows)" % (k, n),
                        drops="Item_%s_%s x1-3" % (k, n), tier="", parts="", priority=3, notes="Recipe: " + use))
        out.append(dict(name="Prop_%s_%s_Harvested" % (k, n), category=cat, world=bi, mechanic="Gathering: picked state, regrows in 3 days",
                        drops="", tier="", parts="", priority=4, notes="swap target after harvest"))
        out.append(dict(name="Item_%s_%s" % (k, n), category="Gatherables", world=bi, mechanic="Ingredient (Zelda-style cooking/alchemy)",
                        drops="from Prop_%s_%s" % (k, n), tier="", parts="", priority=3, notes="Recipe: " + use))
    return out

# ------------------------------------------------------------------ shapes (main=0 leaf/body, 1 accent/fruit, 2 stem/soil)
def soil(): return [b((0.40, 0.40, 0.04), (0, 0, 0.02), 2)]
def plant(n, k, harvested):
    r = lambda i: h(n, i)
    bx = soil()
    if k == "Herb":
        for i in range(5):
            x, y, ht = (r(i) - 0.5) * 0.24, (r(i + 9) - 0.5) * 0.24, 0.16 + 0.14 * r(i + 3)
            ht = ht * (0.35 if harvested else 1)
            bx += [b((0.03, 0.03, ht), (x, y, 0.04 + ht / 2), 0), b((0.10, 0.03, 0.05), (x + 0.03, y, 0.04 + ht * 0.6), 0)]
            if not harvested: bx.append(b((0.06, 0.06, 0.05), (x, y, 0.04 + ht + 0.02), 1))
    elif k == "Shroom":
        for i, (x, y, s) in enumerate(((0, 0, 1.0), (0.12, 0.08, 0.7), (-0.1, 0.1, 0.55))):
            if harvested: bx.append(b((0.06 * s, 0.06 * s, 0.03), (x, y, 0.055), 0)); continue
            bx += [b((0.07 * s, 0.07 * s, 0.14 * s), (x, y, 0.04 + 0.07 * s), 0), b((0.22 * s, 0.22 * s, 0.07 * s), (x, y, 0.04 + 0.16 * s), 1), b((0.14 * s, 0.14 * s, 0.04 * s), (x, y, 0.04 + 0.21 * s), 1)]
    elif k == "Bloom":
        for i in range(3):
            x, y = (r(i) - 0.5) * 0.2, (r(i + 4) - 0.5) * 0.2; ht = 0.32 + 0.1 * r(i + 7)
            bx += [b((0.03, 0.03, ht * (0.5 if harvested else 1)), (x, y, 0.04 + ht * (0.25 if harvested else 0.5)), 0), b((0.12, 0.03, 0.04), (x + 0.04, y, 0.12), 0)]
            if not harvested: bx += [b((0.14, 0.14, 0.04), (x, y, 0.06 + ht), 1), b((0.05, 0.05, 0.05), (x, y, 0.09 + ht), 2)]
    elif k == "Berry":
        bx += [b((0.08, 0.08, 0.16), (0, 0, 0.12), 2), b((0.50, 0.46, 0.22), (0, 0, 0.3), 0), b((0.40, 0.38, 0.18), (0.02, 0, 0.48), 0), b((0.22, 0.22, 0.1), (0, 0, 0.6), 0)]
        if not harvested: bx += [b((0.06, 0.06, 0.06), ((r(i) - 0.5) * 0.48, -0.24 + 0.48 * (i % 2), 0.25 + 0.3 * r(i + 5)), 1) for i in range(8)]
    elif k == "Root":
        bx += [b((0.04, 0.04, 0.2 * (0.4 if harvested else 1)), (x, 0, 0.04 + 0.1 * (0.4 if harvested else 1)), 0) for x in (-0.05, 0.05)]
        if not harvested: bx += [b((0.14, 0.03, 0.10), (s * 0.07, 0, 0.26), 0) for s in (-1, 1)] + [b((0.12, 0.10, 0.06), (0, -0.02, 0.05), 1)]
        else: bx.append(b((0.12, 0.10, 0.03), (0, 0, 0.0 + 0.055), 2))
    elif k == "Vine":
        bx += [b((0.06, 0.06, 0.9), (0, 0.12, 0.45), 2), b((0.4, 0.06, 0.06), (0, 0.12, 0.88), 2)]
        for i in range(7):
            z = 0.12 + 0.11 * i; sd = (-1) ** i
            bx.append(b((0.12, 0.04, 0.08), (sd * 0.07, 0.08, z), 0))
            if not harvested and i % 2: bx.append(b((0.07, 0.07, 0.07), (sd * 0.12, 0.05, z - 0.04), 1))
    elif k == "Moss":
        for i in range(6):
            s = 0.12 + 0.1 * r(i); bx.append(b((s, s, 0.04 + (0 if harvested else 0.04 * r(i + 2))), ((r(i + 3) - 0.5) * 0.3, (r(i + 6) - 0.5) * 0.3, 0.06), 0 if i % 2 else 1))
    elif k == "Fern":
        for i in range(6):
            import math
            a = 2 * math.pi * i / 6; L = 0.22 * (0.4 if harvested else 1)
            bx.append(b((max(0.04, abs(math.cos(a)) * L), max(0.04, abs(math.sin(a)) * L), 0.03), (math.cos(a) * L * 0.6, math.sin(a) * L * 0.6, 0.12 + 0.05 * (i % 2)), 0))
        bx.append(b((0.06, 0.06, 0.12), (0, 0, 0.1), 2))
        if not harvested: bx += [b((0.04, 0.04, 0.12), (0.04 * s, 0.02, 0.24), 1) for s in (-1, 1)]
    elif k == "Cactus":
        bx += [b((0.24, 0.24, 0.30 if harvested else 0.42), (0, 0, 0.2 if harvested else 0.25), 0), b((0.18, 0.18, 0.06), (0, 0, 0.38 if harvested else 0.49), 0)]
        bx += [b((0.02, 0.02, 0.05), (0.13 * dx, 0.13 * dy, 0.3), 2) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
        if not harvested: bx += [b((0.08, 0.08, 0.05), (0, 0, 0.545), 1), b((0.1, 0.1, 0.16), (0.17, 0, 0.3), 0)]
    elif k == "Aqua":
        bx = [b((0.5, 0.5, 0.02), (0, 0, 0.01), 2)]
        bx += [b((0.16, 0.14, 0.02), ((r(i) - 0.5) * 0.3, (r(i + 2) - 0.5) * 0.3, 0.03), 0) for i in range(4)]
        bx += [b((0.03, 0.03, 0.3 * (0.4 if harvested else 1)), (0.1, 0.05, 0.02 + 0.15 * (0.4 if harvested else 1)), 0)]
        if not harvested: bx += [b((0.08, 0.08, 0.08), (0.1, 0.05, 0.36), 1), b((0.1, 0.1, 0.04), (-0.08, 0.02, 0.05), 1)]
    else:  # Xeno: crystal stalks around a pod
        for i in range(5):
            ht = (0.15 + 0.25 * r(i)) * (0.4 if harvested else 1)
            bx.append(b((0.06, 0.06, ht), ((r(i + 4) - 0.5) * 0.28, (r(i + 8) - 0.5) * 0.28, 0.04 + ht / 2), 0 if i % 2 else 1))
        if not harvested: bx.append(b((0.12, 0.12, 0.12), (0, 0, 0.12), 1))
    return bx

def item(n, k):
    if k in ("Herb", "Fern", "Moss"):
        return [b((0.04, 0.04, 0.16), (0, 0, 0.08), 2), b((0.14, 0.03, 0.08), (-0.05, 0, 0.18), 0), b((0.14, 0.03, 0.08), (0.05, 0, 0.23), 0), b((0.10, 0.03, 0.07), (0, 0, 0.29), 0),
                b((0.07, 0.07, 0.05), (0, 0, 0.35), 1), b((0.08, 0.08, 0.03), (0, 0, 0.08), 1)]
    if k == "Shroom":
        return [b((0.07, 0.07, 0.12), (0, 0, 0.06), 0), b((0.22, 0.22, 0.07), (0, 0, 0.15), 1), b((0.14, 0.14, 0.04), (0, 0, 0.2), 1), b((0.04, 0.02, 0.03), (0.05, -0.11, 0.16), 0)]
    if k == "Bloom":
        return [b((0.03, 0.03, 0.26), (0, 0, 0.13), 0), b((0.10, 0.03, 0.04), (0.04, 0, 0.1), 0), b((0.16, 0.16, 0.04), (0, 0, 0.28), 1), b((0.06, 0.06, 0.05), (0, 0, 0.31), 2)]
    if k in ("Berry", "Aqua", "Vine"):
        return [b((0.08, 0.08, 0.08), (x, y, 0.04 + z), 1) for x, y, z in ((0, 0, 0), (0.07, 0.02, 0), (-0.04, 0.06, 0), (0.02, 0.03, 0.07))] + [b((0.12, 0.03, 0.02), (0, 0.02, 0.16), 0)]
    if k == "Root":
        return [b((0.20, 0.10, 0.08), (0, 0, 0.04), 1), b((0.12, 0.08, 0.06), (0.12, 0, 0.04), 1), b((0.03, 0.03, 0.12), (-0.06, 0, 0.13), 0), b((0.03, 0.03, 0.1), (-0.02, 0, 0.12), 0)]
    if k == "Cactus":
        return [b((0.14, 0.14, 0.12), (0, 0, 0.06), 0), b((0.10, 0.10, 0.06), (0, 0, 0.15), 1), b((0.02, 0.02, 0.04), (0.08, 0, 0.08), 2)]
    return [b((0.06, 0.06, 0.18), (-0.03, 0, 0.09), 0), b((0.05, 0.05, 0.24), (0.04, 0.02, 0.12), 1), b((0.04, 0.04, 0.14), (0, -0.04, 0.07), 0)]

SOIL = {"Aqua": "2F80D8", "Cactus": "E2D08C", "Xeno": "2A1840"}
def specs():
    out = {"growing": [], "harvested": [], "items": []}
    for n, k, bi, c1, c2, use in SPECIES:
        g = [1] if n in GLOW else []
        stem = SOIL.get(k, "6B4A2A")
        mats = [c1, c2, stem]
        out["growing"].append({"asset": "Prop_%s_%s" % (k, n), "materials": mats, "glow": g, "parts": [{"name": "", "boxes": plant(n, k, False)}]})
        out["harvested"].append({"asset": "Prop_%s_%s_Harvested" % (k, n), "materials": mats, "glow": [], "parts": [{"name": "", "boxes": plant(n, k, True)}]})
        im = [c1, c2, stem if k not in ("Herb", "Fern", "Moss") else "D8C79A"]
        out["items"].append({"asset": "Item_%s_%s" % (k, n), "materials": im, "glow": g, "parts": [{"name": "", "boxes": item(n, k)}]})
    return out
GROUPS = specs()
SPECS = [s for v in GROUPS.values() for s in v]
