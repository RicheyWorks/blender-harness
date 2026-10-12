# SPDX-License-Identifier: MIT
"""Wave 3: things that make the world look full. More plants (growing/_Harvested/item), more tree species by stage,
more animals, town buildings + street props, and Dragon Warrior realm towns/landmarks. No catalog.py import here."""
from assets import flora2 as F
from assets.flora2 import b, h

TF, GF, DS, TU, SW, OC, JG, MC, SF = F.TF, F.GF, F.DS, F.TU, F.SW, F.OC, F.JG, F.MC, F.SF
PLANTS = [
 ("Foxglove", "Bloom", TF, "4B7B3A", "C040A0", "Heart Tonic: +1 max heart temp (toxic raw)"), ("Bluebell", "Bloom", TF, "3C7C30", "4060E0", "Dye blue; Fairy Lure"),
 ("Poppy", "Bloom", GF, "4B974B", "E02818", "Dye red; Sleep Dart coating"), ("Sunflower", "Bloom", GF, "4B974B", "F8C818", "Seeds: Trail Mix +stamina"),
 ("Clover", "Herb", GF, "3C9C30", "F4F6FB", "Lucky Tea: +drop luck"), ("Dandelion", "Herb", GF, "59A040", "F8D818", "Dandelion Wine: heal 2"),
 ("Thistle", "Bloom", GF, "6B8C5A", "A070E0", "Prickly Ward: thorns armor buff"), ("Wild Garlic".replace(" ", ""), "Herb", TF, "3C9C30", "F4F6FB", "Garlic Roast: undead resist"),
 ("Sorrel", "Herb", SW, "4B974B", "C04030", "Sour Soup: cure nausea"), ("Cattail", "Aqua", SW, "6B8C2F", "6B4A2A", "Torch fiber; Flour alt"),
 ("Water Lily".replace(" ", ""), "Aqua", SW, "2C8C18", "F8D8E8", "Calm Lotus Tea: mana regen"), ("Bladderwort", "Aqua", SW, "59A040", "F8D818", "Bug Bait"),
 ("Sea Holly".replace(" ", ""), "Bloom", OC, "8CA0B0", "6080C0", "Salt Ward: rust resist"), ("Coral Fan".replace(" ", ""), "Xeno", OC, "E05050", "F29BC0", "Reef Charm: swim speed"),
 ("Aloe Bloom".replace(" ", ""), "Cactus", DS, "6B9C7A", "F87818", "Burn Gel: cure burn"), ("Prickly Pear".replace(" ", ""), "Cactus", DS, "4B974B", "C02060", "Pear Juice: hydrate"),
 ("Agave", "Cactus", DS, "6B9C8A", "E8C890", "Agave Syrup: sweeten any dish"), ("Desert Sage".replace(" ", ""), "Herb", DS, "9CB0A0", "A070E0", "Smudge: repel spirits"),
 ("Cloudberry", "Berry", TU, "4B7B3A", "F8A818", "Cloud Jam: heal 4"), ("Lingonberry", "Berry", TU, "2C5C3A", "D82020", "Lingon Sauce: meat x2 heal"),
 ("Snow Lotus".replace(" ", ""), "Bloom", TU, "8C9C80", "F4F6FB", "Frost Elixir: freeze resist"), ("Ice Moss".replace(" ", ""), "Moss", TU, "A8D8E8", "F4F6FB", "Chill Gel: heat resist"),
 ("Orchid", "Bloom", JG, "2C8C18", "E070D0", "Perfume: animals calm"), ("Cacao", "Berry", JG, "2C6B3A", "8C5A2A", "Cocoa: +stamina regen"),
 ("Vanilla Vine".replace(" ", ""), "Vine", JG, "2C8C18", "F4E8C0", "Vanilla: any dessert +1 heart"), ("Pitcher Plant".replace(" ", ""), "Xeno", JG, "59A040", "C02060", "Digest Acid: dissolve vines"),
 ("Rafflesia", "Bloom", JG, "4B6B3A", "C03020", "Stink Bomb: scatter foes"), ("Banana Flower".replace(" ", ""), "Bloom", JG, "2C8C18", "8C2050", "Fritters: heal 3"),
 ("Cave Lichen".replace(" ", ""), "Moss", MC, "8C9C80", "C8C080", "Lichen Bread: heal 1, never spoils"), ("Crystal Fern".replace(" ", ""), "Fern", MC, "6080C0", "A8D8E8", "Shard Tonic: mining speed"),
 ("Iron Root".replace(" ", ""), "Root", MC, "4B6B3A", "707070", "Iron Broth: +defense"), ("Lamp Shroom".replace(" ", ""), "Shroom", MC, "E8E0C0", "FFD040", "Lamp Oil (glows)"),
 ("Bellcap", "Shroom", TF, "F0E6D0", "C04030", "Toad Stew: jump +"), ("Oyster Shroom".replace(" ", ""), "Shroom", TF, "E4DDCF", "B0A890", "Shroom Skewer: heal 2"),
 ("Starfruit Vine".replace(" ", ""), "Vine", SF, "3A4C8C", "FFE25A", "Starfruit: full stamina (glows)"), ("Comet Fern".replace(" ", ""), "Fern", SF, "5C6CA0", "7FE3FF", "Comet Dust: speed (glows)"),
 ("Void Bloom".replace(" ", ""), "Bloom", SF, "2A1840", "D7B8FF", "Void Ink: stealth (glows)"), ("Moonroot", "Root", SF, "3A4C8C", "D7B8FF", "Moon Mash: night vision"),
 ("Halo Moss".replace(" ", ""), "Moss", SF, "5C389E", "FFE25A", "Halo Paint (glows)"), ("Dreamcap", "Shroom", SF, "D7B8FF", "F29BC0", "Dream Draught: see hidden paths (glows)"),
]
GLOW3 = {"LampShroom", "StarfruitVine", "CometFern", "VoidBloom", "HaloMoss", "Dreamcap", "CoralFan"}
TREES3 = {"Maple": ("7A5232", "D8501C", "round"), "Cherry": ("6B4A3A", "F2A8C8", "round"), "Willow": ("6B5A3A", "6CA040", "droop"),
          "Spruce": ("5A3A22", "2C5C3A", "conifer"), "Cedar": ("6B4A2A", "3A6B4A", "conifer"), "Baobab": ("A08060", "6B8C2F", "round"),
          "Joshua": ("8C7A5A", "6B8C5A", "round"), "Mangrove": ("5A4A3A", "3C7C30", "droop"), "Cypress": ("6B5A4A", "3A6B3A", "conifer"),
          "Coconut": ("A08050", "4AA44F", "palm"), "Ironwood": ("4A4A4A", "4B6B3A", "round"), "Moonbark": ("B8C0E0", "5C6CA0", "droop")}
TREE_BIOME = {"Maple": TF, "Cherry": TF, "Willow": SW, "Spruce": TU, "Cedar": MC, "Baobab": GF, "Joshua": DS, "Mangrove": SW, "Cypress": SW,
              "Coconut": OC, "Ironwood": MC, "Moonbark": SF}
ANIMALS = [  # (name, kind, biome, role)
 ("Deer_Red", "wildlife", TF, "prey: venison, hide"), ("Boar_Wild", "wildlife", TF, "prey: meat, tusk"), ("Badger", "wildlife", TF, "prey: pelt"),
 ("Hedgehog", "wildlife", GF, "critter: quill"), ("Horse_Pony", "livestock", GF, "mount"), ("Donkey", "livestock", GF, "pack animal"),
 ("Goose", "birds", GF, "egg, feather"), ("Duck", "birds", SW, "egg, feather"), ("Heron", "birds", SW, "feather"), ("Frog_Bull", "critter", SW, "frog leg"),
 ("Camel", "livestock", DS, "mount, milk"), ("Jackal", "predator", DS, "fang"), ("Vulture", "birds", DS, "feather"),
 ("Walrus", "wildlife", TU, "tusk, blubber"), ("Lynx", "predator", TU, "pelt"), ("Penguin", "birds", TU, "feather"),
 ("Tapir", "wildlife", JG, "meat"), ("Jaguar", "predator", JG, "pelt, fang"), ("Macaw", "birds", JG, "feather"),
 ("Goat_Mountain", "wildlife", MC, "milk, horn"), ("Mole_Giant", "wildlife", MC, "claw"), ("Bat_Cave", "birds", MC, "wing"),
 ("Fish_Salmon", "fish", OC, "fish"), ("Fish_Tuna", "fish", OC, "fish"), ("Fish_Eel", "fish", SW, "fish"),
 ("Moth_Luna", "insects", SF, "glow dust"), ("Stag_Star", "wildlife", SF, "star antler"), ("Bird_Comet", "birds", SF, "comet feather"),
]
WOOD = "8C5A2A"
TOWN3 = {  # name: (w, d, h, wall, roof, sign)
 "Bld_Bakery": (5, 4.4, 2.8, "F2E6CC", "C87850", True), "Bld_Tavern": (7, 5, 3.4, "E4C8A0", "6B4A2A", True), "Bld_Chapel": (5, 7, 4.2, "E4DDCF", "4A4A6A", False),
 "Bld_Mill": (4.4, 4.4, 4.0, "F2E6CC", "8C2A1C", False), "Bld_Barn_Red": (7, 6, 3.6, "B03020", "4A4A4A", False), "Bld_Stable": (6, 4, 2.6, "C8A070", "6B4A2A", False),
 "Bld_Library": (6, 5, 3.6, "D8C8B0", "2C4C8C", True), "Bld_Tailor": (4.6, 4.2, 2.8, "F0D8E0", "8C2A60", True), "Bld_Fishery": (5, 4, 2.6, "A8C0D0", "2C5C8C", True),
 "Bld_TownHall": (8, 6, 4.0, "E4DDCF", "2C4C8C", True), "Bld_Cottage_Blue": (4.6, 4.2, 2.6, "C0D0E0", "2C4C8C", False), "Bld_Cottage_Green": (4.6, 4.2, 2.6, "D0E0C0", "3C6B30", False),
 "Bld_Cottage_Stone": (5, 4.4, 2.8, "A0A0A0", "6B4A2A", False), "Bld_Watchtower": (3, 3, 6.0, "A0A0A0", "6B4A2A", False), "Bld_Apothecary": (4.6, 4.2, 2.8, "E8F0D8", "3C6B30", True),
 "Bld_Jeweler": (4.4, 4.0, 2.8, "F0E8D0", "8C2AA0", True),
}
def street(n):
    W = WOOD
    P = {
     "Prop_Town_Well": ((("A0A0A0", W, "2F80D8")), [b((1.2, 1.2, 0.7), (0, 0, 0.35), 0), b((0.9, 0.9, 0.05), (0, 0, 0.66), 2), b((0.1, 0.1, 1.4), (-0.55, 0, 1.2), 1), b((0.1, 0.1, 1.4), (0.55, 0, 1.2), 1), b((1.4, 1.4, 0.15), (0, 0, 1.95), 1)]),
     "Prop_Town_Lamppost": (("202024", "34343A", "FFD040"), [b((0.3, 0.3, 0.2), (0, 0, 0.1), 0), b((0.1, 0.1, 2.6), (0, 0, 1.4), 1), b((0.3, 0.3, 0.35), (0, 0, 2.85), 2), b((0.4, 0.4, 0.08), (0, 0, 3.06), 0)]),
     "Prop_Town_MarketStall": ((W, "D82800", "F2E6CC"), [b((2.0, 1.0, 0.9), (0, 0, 0.45), 0)] + [b((0.1, 0.1, 2.2), (x, y, 1.1), 0) for x in (-0.95, 0.95) for y in (-0.45, 0.45)] + [b((2.3, 1.3, 0.12), (0, 0, 2.25), 1), b((0.3, 0.3, 0.3), (-0.5, 0, 1.05), 2), b((0.3, 0.3, 0.3), (0.4, 0.1, 1.05), 1)]),
     "Prop_Town_Fence": ((W, W, "6B4A2A"), [b((0.12, 0.12, 1.0), (x, 0, 0.5), 0) for x in (-0.94, 0, 0.94)] + [b((2.0, 0.06, 0.12), (0, 0, z), 2) for z in (0.4, 0.8)]),
     "Prop_Town_Bench": ((W, "34343A", W), [b((1.6, 0.45, 0.08), (0, 0, 0.45), 0), b((1.6, 0.08, 0.4), (0, 0.2, 0.75), 0)] + [b((0.08, 0.4, 0.45), (x, 0, 0.22), 1) for x in (-0.7, 0.7)]),
     "Prop_Town_Signpost": ((W, "E4DDCF", "202024"), [b((0.12, 0.12, 2.0), (0, 0, 1.0), 0), b((0.9, 0.06, 0.25), (0.35, 0, 1.7), 1), b((0.8, 0.06, 0.25), (-0.3, 0, 1.35), 1)]),
     "Prop_Town_Barrel": ((W, "707070", W), [b((0.6, 0.6, 0.9), (0, 0, 0.45), 0), b((0.64, 0.64, 0.06), (0, 0, 0.2), 1), b((0.64, 0.64, 0.06), (0, 0, 0.7), 1)]),
     "Prop_Town_CrateStack": ((W, "6B4A2A", W), [b((0.7, 0.7, 0.7), (-0.4, 0, 0.35), 0), b((0.7, 0.7, 0.7), (0.4, 0.1, 0.35), 1), b((0.7, 0.7, 0.7), (0, 0.05, 1.05), 0)]),
     "Prop_Town_Haybale": (("E4C860", "C8A040", "8C5A2A"), [b((1.2, 0.8, 0.8), (0, 0, 0.4), 0), b((1.22, 0.06, 0.82), (0, -0.2, 0.4), 2), b((1.22, 0.06, 0.82), (0, 0.2, 0.4), 2)]),
     "Prop_Town_Cart": ((W, "34343A", "6B4A2A"), [b((1.6, 1.0, 0.3), (0, 0, 0.7), 0), b((1.6, 0.06, 0.4), (0, -0.5, 1.05), 0), b((1.6, 0.06, 0.4), (0, 0.5, 1.05), 0)] + [b((0.1, 0.7, 0.7), (x, y, 0.35), 1) for x in (-0.5, 0.5) for y in (-0.56, 0.56)] + [b((1.4, 0.08, 0.08), (1.4, 0, 0.6), 2)]),
     "Prop_Town_Fountain": (("A0A0A0", "2F80D8", "C0C0C0"), [b((3.0, 3.0, 0.5), (0, 0, 0.25), 0), b((2.6, 2.6, 0.06), (0, 0, 0.46), 1), b((0.5, 0.5, 1.4), (0, 0, 1.1), 2), b((1.2, 1.2, 0.2), (0, 0, 1.8), 0), b((0.3, 0.3, 0.5), (0, 0, 2.1), 1)]),
     "Prop_Town_Flowerbox": ((W, "4B974B", "E02818"), [b((1.2, 0.4, 0.3), (0, 0, 0.15), 0), b((1.1, 0.3, 0.12), (0, 0, 0.34), 1)] + [b((0.12, 0.12, 0.12), (x, 0, 0.45), 2) for x in (-0.4, 0, 0.4)]),
     "Prop_Town_Banner": ((W, "0058F8", "F2C230"), [b((0.1, 0.1, 3.0), (0, 0, 1.5), 0), b((0.8, 0.04, 1.2), (0.4, 0, 2.3), 1), b((0.3, 0.05, 0.3), (0.4, -0.01, 2.4), 2)]),
     "Prop_Town_Noticeboard": ((W, "E4DDCF", "D82800"), [b((0.12, 0.12, 1.8), (x, 0, 0.9), 0) for x in (-0.7, 0.7)] + [b((1.6, 0.08, 1.0), (0, 0, 1.4), 0), b((0.4, 0.04, 0.5), (-0.3, -0.05, 1.4), 1), b((0.3, 0.04, 0.4), (0.35, -0.05, 1.5), 2)]),
    }
    return P[n]
REALM3 = {  # Dragon Warrior: towns and landmarks (blocky, 8-bit palette)
 "Bld_Realm_Town_Rimvale": ("Town", ("F0D090", "D82800", "8C5A2A")), "Bld_Realm_Town_Garinham": ("Town", ("E4C8A0", "0058F8", "8C5A2A")),
 "Bld_Realm_Town_Cantlin": ("Town", ("C0C0C0", "188C10", "6B4A2A")), "Bld_Realm_Inn_Rimvale": ("Inn", ("E4C8A0", "D82800", "8C5A2A")),
 "Bld_Realm_Shop_Weapon": ("Shop", ("F0D090", "707070", "8C5A2A")), "Bld_Realm_Shop_Item": ("Shop", ("F0D090", "188C10", "8C5A2A")),
 "Bld_Realm_Castle_Charlock": ("Castle", ("5C389E", "202024", "D82800")), "Bld_Realm_Castle_Tantegel": ("Castle", ("C0C0C0", "0058F8", "202024")),
}
REALMPROP3 = {
 "Prop_Realm_Shrine": (("C0C0C0", "F2C230", "0058F8"), [b((3, 3, 0.4), (0, 0, 0.2), 0)] + [b((0.4, 0.4, 2.4), (x, y, 1.6), 0) for x in (-1.2, 1.2) for y in (-1.2, 1.2)] + [b((3, 3, 0.3), (0, 0, 2.95), 2), b((0.6, 0.6, 0.6), (0, 0, 0.7), 1)]),
 "Prop_Realm_Bridge": (("8C5A2A", "6B4A2A", "C0C0C0"), [b((2.0, 6.0, 0.3), (0, 0, 0.6), 0)] + [b((0.12, 6.0, 0.12), (x, 0, 1.2), 1) for x in (-0.95, 0.95)] + [b((0.12, 0.12, 0.7), (x, y, 0.95), 1) for x in (-0.95, 0.95) for y in (-2.9, -1, 1, 2.9)]),
 "Prop_Realm_Swamp_Tile": (("6B8C2F", "3C5C2A", "8C2AA0"), [b((1, 1, 0.12), (0, 0, 0.06), 0), b((0.4, 0.3, 0.02), (0.15, -0.1, 0.13), 1), b((0.2, 0.2, 0.02), (-0.25, 0.2, 0.13), 2)]),
 "Prop_Realm_Desert_Tile": (("F0D090", "E4C060", "C0A050"), [b((1, 1, 0.12), (0, 0, 0.06), 0), b((0.5, 0.2, 0.04), (0.1, 0.2, 0.14), 1), b((0.3, 0.15, 0.04), (-0.2, -0.25, 0.14), 2)]),
 "Prop_Realm_Hill_Tile": (("59A040", "3C7C30", "8C5A2A"), [b((1, 1, 0.12), (0, 0, 0.06), 0), b((0.7, 0.7, 0.2), (0, 0, 0.22), 1), b((0.4, 0.4, 0.14), (0, 0, 0.39), 1)]),
 "Prop_Realm_Water_Tile": (("2F80D8", "60A0F0", "F4F6FB"), [b((1, 1, 0.08), (0, 0, 0.04), 0), b((0.4, 0.06, 0.02), (-0.2, 0.1, 0.09), 2), b((0.3, 0.06, 0.02), (0.2, -0.2, 0.09), 2)]),
 "Prop_Realm_Barrier_Tile": (("D82800", "F87818", "F2C230"), [b((1, 1, 0.08), (0, 0, 0.04), 0), b((0.8, 0.8, 0.02), (0, 0, 0.09), 1), b((0.3, 0.3, 0.02), (0, 0, 0.11), 2)]),
 "Prop_Realm_TreasureChest": (("8C5A2A", "F2C230", "202024"), [b((0.8, 0.5, 0.45), (0, 0, 0.225), 0), b((0.84, 0.54, 0.2), (0, 0, 0.55), 0), b((0.86, 0.06, 0.66), (0, 0, 0.33), 1), b((0.1, 0.06, 0.12), (0, -0.28, 0.42), 2)]),
 "Prop_Realm_Throne": (("D82800", "F2C230", "8C5A2A"), [b((1.2, 1.0, 0.5), (0, 0, 0.25), 2), b((0.9, 0.7, 0.2), (0, 0, 0.6), 0), b((0.9, 0.15, 1.6), (0, 0.35, 1.3), 0), b((1.0, 0.18, 0.2), (0, 0.35, 2.15), 1)] + [b((0.12, 0.7, 0.4), (x, 0, 0.9), 1) for x in (-0.5, 0.5)]),
 "Prop_Realm_Stairs": (("A0A0A0", "707070", "202024"), [b((1, 0.33, 0.33 * (i + 1)), (0, -0.33 + 0.33 * i, 0.165 * (i + 1)), i % 2) for i in range(3)]),
 "Prop_Realm_Signboard": (("8C5A2A", "F0D090", "202024"), [b((0.12, 0.12, 1.6), (0, 0, 0.8), 0), b((1.0, 0.08, 0.6), (0, 0, 1.4), 1), b((0.6, 0.02, 0.06), (0, -0.05, 1.45), 2)]),
 "Prop_Realm_Rainbow_Bridge": (("D82800", "F2C230", "0058F8"), [b((2.0, 6.0, 0.3), (0, 0, 0.6), 0), b((2.0, 6.0, 0.06), (0, 0, 0.78), 1), b((2.0, 6.0, 0.06), (0, 0, 0.84), 2)]),
}

def S(asset, mats, boxes, glow=()): return {"asset": asset, "materials": list(mats), "glow": list(glow), "parts": [{"name": "", "boxes": boxes}]}

def entries():
    out = []
    def add(n, cat, world, mech, drops="", prio=3, notes=""):
        out.append(dict(name=n, category=cat, world=world, mechanic=mech, drops=drops, tier="", parts="", priority=prio, notes=notes))
    for n, k, bi, c1, c2, use in PLANTS:
        cat = "Other Worlds" if bi == SF else "Flora"
        add("Prop_%s_%s" % (k, n), cat, bi, "Gathering: harvest -> Item_%s_%s (regrows)" % (k, n), "Item_%s_%s x1-3" % (k, n), notes="Recipe: " + use)
        add("Prop_%s_%s_Harvested" % (k, n), cat, bi, "Gathering: picked state, regrows in 3 days", prio=4)
        add("Item_%s_%s" % (k, n), "Gatherables", bi, "Ingredient (Zelda-style cooking/alchemy)", "from Prop_%s_%s" % (k, n), notes="Recipe: " + use)
    for sp in TREES3:
        for st in ("Sapling", "Young", "Mature"):
            add("Prop_Tree_%s_%s" % (sp, st), "Flora", TREE_BIOME[sp], "Tree growth stage %s; chop -> logs" % st, "Item_Log x%d" % {"Sapling": 0, "Young": 2, "Mature": 5}[st])
    for n, kind, bi, role in ANIMALS:
        add("Mob_" + n, "Fauna", bi, "%s (%s)" % (kind.capitalize(), role), role.split(": ")[-1])
    for n in TOWN3: add(n, "Town", "Shattered islands (all)", "Town building (visible skyline)")
    for n in street.__defaults__ or []: pass
    for n in STREET: add(n, "Town", "Shattered islands (all)", "Street dressing prop")
    for n in REALM3: add(n, "Dragon Warrior", "Dragon Warrior realm", "Realm %s" % REALM3[n][0])
    for n in REALMPROP3: add(n, "Dragon Warrior", "Dragon Warrior realm", "Realm landmark / overworld tile")
    return out

STREET = ["Prop_Town_Well", "Prop_Town_Lamppost", "Prop_Town_MarketStall", "Prop_Town_Fence", "Prop_Town_Bench", "Prop_Town_Signpost",
          "Prop_Town_Barrel", "Prop_Town_CrateStack", "Prop_Town_Haybale", "Prop_Town_Cart", "Prop_Town_Fountain", "Prop_Town_Flowerbox",
          "Prop_Town_Banner", "Prop_Town_Noticeboard"]

def specs():
    from assets import ecospecs as E, worldspecs as W
    E.TREES.update(TREES3)
    g = {"town": [], "realm": [], "trees": [], "animals": [], "plants": [], "plant_items": [], "plant_harvested": []}
    for n, (w, d, hh, wall, roof, sign) in TOWN3.items():
        bx = W.roofhouse(w, d, hh, 0, 1, 2, sign=sign or None)
        if n == "Bld_Watchtower": bx = [b((3, 3, 6), (0, 0, 3), 0), b((3.6, 3.6, 0.3), (0, 0, 6.15), 2)] + [b((0.5, 0.5, 0.6), (x, y, 6.6), 0) for x in (-1.5, 1.5) for y in (-1.5, 1.5)] + [b((1, 0.1, 1.9), (0, -1.54, 0.95), 2)]
        if n == "Bld_Mill": bx += [b((0.3, 0.3, 0.3), (0, -2.4, 3.2), 2), b((0.3, 0.1, 5.0), (0, -2.6, 3.2), 2), b((5.0, 0.1, 0.3), (0, -2.6, 3.2), 2)]
        if n == "Bld_Chapel": bx += [b((1.2, 1.2, 3.0), (0, 3.0, 5.5), 0), b((0.2, 0.2, 1.0), (0, 3.0, 7.5), 2), b((0.6, 0.2, 0.2), (0, 3.0, 7.6), 2)]
        g["town"].append(S(n, (wall, roof, WOOD), bx))
    for n in STREET:
        m, bx = street(n); g["town"].append(S(n, m, bx, glow=[2] if n == "Prop_Town_Lamppost" else []))
    for n, (k, cols) in REALM3.items():
        sp = W.realm_bld("Bld_Realm_" + k); sp["asset"] = n; sp["materials"] = list(cols); g["realm"].append(sp)
    for n, (m, bx) in REALMPROP3.items(): g["realm"].append(S(n, m, bx))
    for sp in TREES3:
        for st in ("Sapling", "Young", "Mature"):
            g["trees"].append(E.tree({"name": "Prop_Tree_%s_%s" % (sp, st)}))
    for n, kind, bi, role in ANIMALS:
        g["animals"].append(E.fauna({"name": "Mob_" + n, "mechanic": "%s (%s)" % (kind.capitalize(), role)}))
    for n, k, bi, c1, c2, use in PLANTS:
        gl = [1] if n in GLOW3 else []; stem = F.SOIL.get(k, "6B4A2A"); mats = [c1, c2, stem]
        g["plants"].append({"asset": "Prop_%s_%s" % (k, n), "materials": mats, "glow": gl, "parts": [{"name": "", "boxes": F.plant(n, k, False)}]})
        g["plant_harvested"].append({"asset": "Prop_%s_%s_Harvested" % (k, n), "materials": mats, "glow": [], "parts": [{"name": "", "boxes": F.plant(n, k, True)}]})
        g["plant_items"].append({"asset": "Item_%s_%s" % (k, n), "materials": [c1, c2, stem if k not in ("Herb", "Fern", "Moss") else "D8C79A"], "glow": gl, "parts": [{"name": "", "boxes": F.item(n, k)}]})
    return g

_G = None
def __getattr__(name):   # lazy (PEP 562): catalog.py imports entries() from here before ecospecs/worldspecs can load
    global _G
    if name in ("GROUPS", "SPECS"):
        if _G is None: _G = specs()
        return _G if name == "GROUPS" else [x for v in _G.values() for x in v]
    raise AttributeError(name)
