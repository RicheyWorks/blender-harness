# SPDX-License-Identifier: MIT
"""The mechanics-to-assets map: every asset Daedalus needs, as data. The tracker and the builder read this.

Row: (name, category, world, mechanic, ingredients/drops, tier, moving parts, priority, notes)
Priority 1 = needed now (digging is live) ... 5 = later. Tri budget comes from the Kind (brief)."""

TIERS = [("Copper", "C8703A", "copper ore x3 + stick"), ("Iron", "C9B49C", "iron ore x3 + stick"),
         ("Gold", "F2C230", "gold ore x3 + stick"), ("Crystal", "A070FF", "crystal x3 + stick"),
         ("Starmetal", "7FE3FF", "starmetal x3 + shield core")]
W = "Shattered islands (all)"
R = []


def add(name, cat, mech, drops="", tier="", parts="", prio=3, notes="", world=W):
    R.append(dict(name=name, category=cat, world=world, mechanic=mech, drops=drops, tier=tier, parts=parts,
                  priority=prio, notes=notes))


# ---------------------------------------------------------------- Tools (digging, building, farming, utility)
add("Tool_Pickaxe", "Tools", "Digging: break stone/ore cubes", "stone x3 + stick", "Stone", prio=1)
for t, _, d in TIERS:
    add("Tool_Pickaxe_" + t, "Tools", "Digging: faster, harder ores", d, t, prio=1 if t in ("Iron", "Gold", "Starmetal") else 2)
add("Tool_Shovel", "Tools", "Digging: dirt, sand, gravel", "stone x1 + stick", "Stone", prio=1)
add("Tool_Axe", "Tools", "Chopping logs and trees", "stone x3 + stick", "Stone", prio=1)
add("Tool_Hoe", "Tools", "Farming: till grass into soil", "stone x2 + stick", "Stone", prio=2)
add("Tool_Hammer", "Tools", "Building: break/place blocks, repair", "stone x4 + stick", "Stone", prio=2)
for base, mech in (("Shovel", "Digging: dirt, sand, gravel"), ("Axe", "Chopping logs and trees"),
                   ("Hoe", "Farming: till soil, bigger area"), ("Hammer", "Building: repair, faster break")):
    for t, _, d in TIERS:
        add("Tool_%s_%s" % (base, t), "Tools", mech, d, t, prio=2 if t in ("Copper", "Iron") else 3)
for n, mech, d in [("WateringCan", "Farming: water crops", "copper x3"), ("Sickle", "Farming: harvest crops", "iron x2 + stick"),
                   ("SeedBag", "Farming: plant seeds", "cloth x2"), ("FishingRod", "Fishing in island pools", "stick x3 + string"),
                   ("BugNet", "Catching critters (Animal Crossing feel)", "stick x2 + string x3"),
                   ("Trowel", "Building: smooth/shape blocks", "iron x1 + stick"),
                   ("BlockPlacer", "Building: place cubes at range", "starmetal x2 + crystal"),
                   ("PaintBrush", "Building: recolour cubes", "stick + dye"), ("Lantern", "Light while exploring caves", "iron x2 + glass"),
                   ("GrappleHook", "Traversal: swing between islands", "iron x4 + string x4"),
                   ("Wrench", "Fix vehicles and Ark parts", "iron x3"), ("Bucket", "Carry water/sand", "iron x3"),
                   ("Torch", "Placeable light", "stick + coal")]:
    add("Tool_" + n, "Tools", mech, d, prio=2 if n in ("WateringCan", "Sickle", "SeedBag", "Torch", "Lantern") else 3)

# ---------------------------------------------------------------- Weapons (Zelda II swords, Halo guns)
add("Wpn_Sword", "Weapons", "Melee combat (Zelda II thrust/slash)", "iron x2 + stick", "Iron", prio=1)
for t, _, d in TIERS:
    add("Wpn_Sword_" + t, "Weapons", "Melee combat, more damage", d, t, prio=2)
add("Wpn_Blaster", "Weapons", "Ranged combat (Halo rifle)", "iron x4 + crystal", "Iron", prio=1)
add("Wpn_Blaster_Pistol", "Weapons", "Ranged sidearm", "iron x2 + crystal", "Iron", prio=2)
add("Wpn_Blaster_Plasma", "Weapons", "Charged plasma shots", "starmetal x3 + crystal x2", "Starmetal", prio=3)
add("Wpn_Bow", "Weapons", "Quiet ranged, arrows", "stick x3 + string x3", "Wood", prio=3)
add("Wpn_Spear", "Weapons", "Reach melee, throwable", "iron x1 + stick x2", "Iron", prio=3)
for t, c in (("Wood", "9A6B3F"), ("Iron", "C9B49C"), ("Starmetal", "7FE3FF")):
    add("Wpn_Shield_" + t, "Weapons", "Block attacks (Zelda II shield)", t.lower() + " x4", t, prio=2 if t == "Wood" else 3)

# ---------------------------------------------------------------- Armor
for t, _, d in [("Leather", "", "hide x5")] + TIERS[1:]:
    add("Item_Helmet_" + t, "Armor", "Armor tier (set_armor_tier)", d, t, "_Head", prio=3)
    add("Item_Chestplate_" + t, "Armor", "Armor tier (set_armor_tier)", d, t, "_Body", prio=3)
add("Item_ShieldCore", "Armor", "Raises armor (add_shield_core)", "drop: Stone Knight", "Shield", prio=2)
add("Item_Overshield", "Armor", "Temporary overshield (give_overshield)", "rare drop", "Gold", prio=2)

# ---------------------------------------------------------------- Stations (crafting)
for n, m in [("Workbench", "Craft tools"), ("Furnace", "Smelt ore into bars"), ("Anvil", "Upgrade tool tiers"),
             ("Loom", "Cloth, string"), ("Cauldron", "Potions/dyes"), ("Starforge", "Starmetal gear")]:
    add("Prop_" + n, "Stations", "Crafting: " + m, "", prio=2 if n in ("Workbench", "Furnace") else 3)

# ---------------------------------------------------------------- Flora
for n, d in [("OakTree", "log x4, sapling"), ("BlossomTree", "log x3, blossom"), ("Bush", "berries"),
             ("Wheat", "wheat, seeds"), ("Carrot", "carrot"), ("Pumpkin", "pumpkin"), ("Flower_Red", "dye red"),
             ("Mushroom", "mushroom"), ("CrystalShrub", "crystal shard")]:
    add("Prop_" + n, "Flora", "Gathering/farming", d, prio=3, parts="_Top (sways)" if "Tree" in n else "")

# ---------------------------------------------------------------- Fauna (foes + critters)
for n, s, p, d in [("BlightSlime", "~0.8 m", "_Body _Head", "slime gel"), ("Shardback", "~1.3 m", "_Body _Head _LegL _LegR", "crystal"),
                   ("DustWisp", "~0.7 m", "_Body", "dust"), ("StoneKnight", "~2.4 m", "_Body _Head _ArmL _ArmR _LegL _LegR", "shield core")]:
    add("Mob_" + n, "Fauna", "Foe (combat) " + s, d, parts=p, prio=2)
for n in ("Butterfly", "Beetle", "Fish_Carp", "Bird_Sparrow"):
    add("Mob_" + n, "Fauna", "Critter (net/rod, museum)", "collectible", parts="_Body _WingL _WingR" if n in ("Butterfly", "Bird_Sparrow") else "_Body", prio=4)

# ---------------------------------------------------------------- Gatherables (ore pickups)
for n, c in [("Coal", "34343A"), ("Copper", "C8703A"), ("Iron", "C9B49C"), ("Gold", "F2C230"), ("Crystal", "A070FF"), ("Starmetal", "7FE3FF")]:
    add("Item_" + n, "Gatherables", "Digging drop / crafting", "from %s ore cube" % n.lower(), n, prio=1, notes="#" + c)
for n in ("Stick", "String", "Cloth", "Seed"):
    add("Item_" + n, "Gatherables", "Crafting ingredient", "", prio=3)

# ---------------------------------------------------------------- Blocks (decor variants beyond the voxel types)
for n in ("Crate", "Barrel", "Ladder", "Door", "Window", "Stairs_Wood"):
    add("Prop_" + n, "Blocks", "Building pieces", "", prio=3)

# ---------------------------------------------------------------- Town (Animal Crossing)
for n, prio in [("Bld_NewsBoard", 2), ("Bld_Shop", 3), ("Bld_Cottage", 3), ("Prop_Bench", 3), ("Prop_Lantern", 3),
                ("Prop_Mailbox", 3), ("Prop_Well", 3), ("Prop_FlowerPot", 3), ("Prop_Fence", 3)]:
    add(n, "Town", "Cosy town", "", prio=prio, world="Town island")

# ---------------------------------------------------------------- Vehicles
add("Veh_Ghost", "Vehicles", "Hover bike", "", parts="_Body _GunL _GunR", prio=2, world="All")
add("Veh_Warthog", "Vehicles", "3-seat buggy", "", parts="_Body _WheelFL _WheelFR _WheelBL _WheelBR _Turret", prio=3, world="All")
add("Veh_Ark", "Vehicles", "Tow islands together", "", parts="_Hull _Sail Veh_Ark_Claw", prio=3, world="The bubble")

# ---------------------------------------------------------------- Sky
for n in ("Sky_MeteorChunk_A", "Sky_MeteorChunk_B", "Sky_MeteorChunk_C", "Sky_ShatteredPlanet"):
    add(n, "Sky", "Backdrop outside the bubble", "", prio=4, world="Outside the bubble")

# ---------------------------------------------------------------- Other Worlds (later biomes)
for n, w in [("Prop_IceSpire", "Frost shard"), ("Prop_LavaRock", "Ember shard"), ("Prop_CoralTree", "Tide shard"),
             ("Prop_RuinPillar", "Old-world ruins")]:
    add(n, "Other Worlds", "Biome dressing", "", prio=5, world=w)

ASSETS = R
