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

# =============================================================== the whole ecosystem, per biome
BIOMES = {
 "Temperate forest": dict(trees=["Oak", "Birch", "Maple"], shrubs=["Hazel", "Fern"], flowers=["Bluebell", "Foxglove"],
     grasses=["MeadowGrass"], herbs=["Sage"], mushrooms=["Toadstool", "Porcini"], fruit=["Apple"],
     prey=["Rabbit", "Deer", "Squirrel"], predators=["Fox", "Wolf"], birds=["Robin", "Owl"], insects=["Bee", "Butterfly"], fish=["Trout"]),
 "Grassland / farm": dict(trees=["Willow"], shrubs=["Hedge"], flowers=["Sunflower", "Poppy"], grasses=["TallGrass", "Hay"],
     herbs=["Mint"], mushrooms=[], fruit=["Strawberry"], prey=["Mouse", "Pheasant"], predators=["Hawk"], birds=["Sparrow"],
     insects=["Ladybird", "Grasshopper"], fish=["Carp"], livestock=["Cow", "Sheep", "Pig", "Chicken", "Goat", "Horse"]),
 "Desert": dict(trees=["Palm", "Joshua"], shrubs=["Saguaro", "Tumbleweed"], flowers=["DesertRose"], grasses=["DuneGrass"],
     herbs=["Aloe"], mushrooms=[], fruit=["Date", "PricklyPear"], prey=["Lizard", "Jerboa"], predators=["Scorpion", "SandSnake"],
     birds=["Vulture"], insects=["Beetle"], fish=[]),
 "Tundra": dict(trees=["Spruce", "Pine"], shrubs=["Juniper"], flowers=["Edelweiss"], grasses=["Tussock"], herbs=["Lichen"],
     mushrooms=["Frostcap"], fruit=["Cloudberry"], prey=["Hare", "Caribou"], predators=["PolarBear", "SnowFox"],
     birds=["SnowyOwl"], insects=[], fish=["Char"]),
 "Swamp / wetland": dict(trees=["Cypress", "Mangrove"], shrubs=["Reed", "Cattail"], flowers=["Lotus", "WaterLily"],
     grasses=["Sedge"], herbs=["Bogmyrtle"], mushrooms=["Glowcap"], fruit=["Cranberry"], prey=["Frog", "Newt"],
     predators=["Crocodile", "Heron"], birds=["Duck"], insects=["Dragonfly", "Firefly"], fish=["Catfish"]),
 "Ocean / reef": dict(trees=["Kelp"], shrubs=["Coral_Brain", "Coral_Fan"], flowers=["SeaAnemone"], grasses=["Seagrass"],
     herbs=["SeaSalt"], mushrooms=[], fruit=["Coconut"], prey=["Crab", "Shrimp"], predators=["Shark", "Octopus"],
     birds=["Gull"], insects=[], fish=["Clownfish", "Tuna", "Pufferfish"]),
 "Jungle": dict(trees=["Kapok", "Banana", "Bamboo"], shrubs=["Monstera"], flowers=["Orchid", "Hibiscus"], grasses=["Vine"],
     herbs=["Ginger"], mushrooms=["Bracket"], fruit=["Mango", "Cocoa"], prey=["Monkey", "Tapir"], predators=["Jaguar", "Python"],
     birds=["Parrot", "Toucan"], insects=["Ant", "MorphoButterfly"], fish=["Piranha"]),
 "Mountain / caves": dict(trees=["Larch"], shrubs=["Heather"], flowers=["Gentian"], grasses=["Moss"], herbs=["Thyme"],
     mushrooms=["CaveShroom", "Glowshroom"], fruit=["Bilberry"], prey=["MountainGoat", "Marmot"], predators=["Bat", "CaveSpider", "Eagle"],
     birds=["Eagle"], insects=["Glowworm"], fish=["Blindfish"]),
 "Starfall (other world)": dict(trees=["StarWillow"], shrubs=["CrystalShrub2"], flowers=["NovaBloom"], grasses=["Shimmergrass"],
     herbs=["Stardust"], mushrooms=["Voidcap"], fruit=["Moonfruit"], prey=["Glimmerling"], predators=["VoidStalker"],
     birds=["Starling_Comet"], insects=["Lumamoth"], fish=["Nebulafish"]),
}
STAGES = ["Sapling", "Young", "Mature"]
for biome, b in BIOMES.items():
    W2 = biome
    other = "other world" in biome
    cat_f = "Other Worlds" if other else "Flora"
    cat_a = "Other Worlds" if other else "Fauna"
    for t in b["trees"]:
        for i, st in enumerate(STAGES):
            add("Prop_Tree_%s_%s" % (t, st), cat_f, "Forestry: tree grows %s -> next stage; chop with Tool_Axe" % st,
                "drops: Item_Log_%s x%d, Item_Seed_%s" % (t, (i + 1) * 2, t) if st != "Sapling" else "plant: Item_Seed_%s" % t,
                st, "_Top (sways)" if st == "Mature" else "", 3 if st == "Mature" else 4, world=W2)
        add("Item_Log_" + t, "Gatherables", "Crafting: planks, fuel", "from Prop_Tree_%s_* + Tool_Axe" % t, prio=3, world=W2)
        add("Item_Seed_" + t, "Gatherables", "Forestry: plant a sapling", "from Prop_Tree_%s_Mature" % t, prio=4, world=W2)
    for kind, mech in (("shrubs", "Gathering: berries/sticks"), ("flowers", "Dye + bees + decor"), ("grasses", "Ground cover; seeds")):
        for n in b[kind]:
            add("Prop_%s_%s" % ({"shrubs": "Shrub", "flowers": "Flower", "grasses": "Grass"}[kind], n), cat_f, mech,
                "drops: " + {"shrubs": "Item_Stick", "flowers": "Item_Dye_" + n, "grasses": "Item_Seed"}[kind], prio=4, world=W2)
    for n in b["herbs"]:
        add("Prop_Herb_" + n, cat_f, "Zelda-style gathering for potions", "drops: Item_Herb_" + n, prio=3, world=W2)
        add("Item_Herb_" + n, "Gatherables", "Brewing ingredient (Prop_BrewingStand)", "from Prop_Herb_" + n, prio=3, world=W2)
    for n in b["mushrooms"]:
        add("Prop_Mushroom_" + n, cat_f, "Gathering; food; brewing", "drops: Item_Mushroom_" + n, prio=4, world=W2)
        add("Item_Mushroom_" + n, "Gatherables", "Food / brewing", "from Prop_Mushroom_" + n, prio=4, world=W2)
    for n in b["fruit"]:
        add("Item_Fruit_" + n, "Gatherables", "Food; cooking", "from its plant", prio=3, world=W2)
    food = {"prey": "eats: plants/insects; eaten by predators", "predators": "eats: prey; drops monster parts",
            "birds": "eats: insects/seeds", "insects": "pollinates flowers; eaten by birds", "fish": "eats: plankton/insects; Tool_FishingRod",
            "livestock": "eats: Item_Hay; farmed"}
    for kind, note in food.items():
        for n in b.get(kind, []):
            drops = {"prey": "Item_Meat, Item_Hide", "predators": "Item_Fang, Item_Hide", "birds": "Item_Feather",
                     "insects": "Item_Honey" if n == "Bee" else "collectible (Tool_BugNet)", "fish": "Item_Fish_" + n,
                     "livestock": {"Cow": "Item_Milk, Item_Meat, Item_Hide", "Sheep": "Item_Wool", "Pig": "Item_Meat",
                                   "Chicken": "Item_Egg, Item_Feather", "Goat": "Item_Milk", "Horse": "rideable"}.get(n, "")}[kind]
            parts = {"birds": "_Body _Head _WingL _WingR", "insects": "_Body _WingL _WingR", "fish": "_Body _Tail"}.get(kind, "_Body _Head _LegFL _LegFR _LegBL _LegBR")
            name = "Mob_" + n
            if any(a["name"] == name for a in R):
                continue
            add(name, cat_a, "%s (%s)" % (kind.capitalize(), biome), "drops: " + drops, parts=parts,
                prio=3 if kind in ("livestock", "predators") else 4, notes=note, world=W2)

# ---------------------------------------------------------------- crops with growth stages (farmland)
for c in ("Wheat", "Carrot", "Potato", "Pumpkin", "Melon", "Tomato", "Corn", "Rice", "Cotton", "Starbean"):
    for i in range(1, 5):
        add("Prop_Crop_%s_S%d" % (c, i), "Flora", "Farming: crop stage %d/4 on Prop_Farmland" % i,
            "drops: Item_Crop_%s, Item_Seed_%s" % (c, c) if i == 4 else "", "S%d" % i, prio=2 if c in ("Wheat", "Carrot") else 3)
    add("Item_Crop_" + c, "Gatherables", "Food / cooking / trade", "from Prop_Crop_%s_S4" % c, prio=3)
    add("Item_Seed_" + c, "Gatherables", "Farming: plant on Prop_Farmland", "from Prop_Crop_%s_S4" % c, prio=3)

# ---------------------------------------------------------------- Minecraft-complete mechanics
for n, mech, drops in [
    ("CraftingTable", "Crafting 3x3", "Item_Planks x4"), ("BrewingStand", "Brewing potions", "Item_Iron x1 + Item_Crystal"),
    ("EnchantingTable", "Enchanting tools", "Item_Crystal x2 + Item_Starmetal"), ("Grindstone", "Remove enchantments", "stone x2"),
    ("Smoker", "Cook food fast", "Prop_Furnace + Item_Log"), ("Composter", "Compost -> fertiliser", "Item_Planks x7")]:
    add("Prop_" + n, "Stations", "Crafting: " + mech, drops, prio=2 if n == "CraftingTable" else 3)
for n, mech in [("Chest", "Storage"), ("Chest_Large", "Storage x2"), ("Barrel_Storage", "Storage"), ("Bed", "Sleep / set spawn"),
                ("Door_Wood", "Doors"), ("Door_Iron", "Locked doors"), ("Trapdoor", "Hatches"), ("Ladder_Wood", "Climbing"),
                ("Farmland", "Tilled soil (Tool_Hoe)"), ("Farmland_Wet", "Watered soil (Tool_WateringCan)"), ("Torch_Wall", "Light"),
                ("Sign", "Labels"), ("Fence_Gate", "Pens for livestock"), ("Scaffold", "Building"), ("Glass_Pane", "Windows")]:
    add("Prop_" + n, "Blocks", mech, "", prio=3)
for n, mech in [("Rail", "Rails"), ("Rail_Powered", "Powered rails"), ("Lever", "Signal source"), ("Button", "Signal pulse"),
                ("PressurePlate", "Step signal"), ("Wire", "Starwire (redstone-like) signal"), ("Lamp_Signal", "Signal lamp"),
                ("Piston", "Push blocks"), ("Hopper", "Item transfer"), ("Dispenser", "Fire items"), ("Repeater", "Signal delay"),
                ("Observer", "Detect change"), ("Conveyor", "Move items")]:
    add("Prop_" + n, "Blocks", "Machines: " + mech, "Item_Iron + Item_Starwire" if n != "Rail" else "Item_Iron x6 + Item_Stick", prio=4,
        parts="_Arm" if n in ("Piston", "Lever") else "")
add("Veh_Minecart", "Vehicles", "Ride rails", "Item_Iron x5", parts="_Body _WheelL _WheelR", prio=3)
add("Veh_Boat", "Vehicles", "Cross island pools", "Item_Planks x5", parts="_Body _OarL _OarR", prio=3)
add("Veh_Glider", "Vehicles", "Glide between islands (Zelda paraglider)", "Item_Cloth x4 + Item_Stick x2", prio=3)

# ---------------------------------------------------------------- Zelda-style gatherables (recipe links)
for n, src in [("Fang", "predators"), ("Hide", "prey/predators"), ("Feather", "birds"), ("Honey", "Mob_Bee"), ("Meat", "prey/livestock"),
               ("Milk", "Mob_Cow/Mob_Goat"), ("Egg", "Mob_Chicken"), ("Wool", "Mob_Sheep"), ("Hay", "Prop_Grass_Hay"),
               ("SlimeGel", "Mob_BlightSlime"), ("WispDust", "Mob_DustWisp"), ("ShardbackPlate", "Mob_Shardback"),
               ("KnightCrest", "Mob_StoneKnight"), ("Planks", "Item_Log_* at Prop_CraftingTable"), ("Starwire", "Item_Starmetal + Item_Copper"),
               ("Dye", "flowers"), ("Potion_Heal", "Item_Herb_Sage + Item_Mushroom_Toadstool at Prop_BrewingStand"),
               ("Potion_Stamina", "Item_Herb_Mint + Item_Honey at Prop_BrewingStand"), ("Potion_Shield", "Item_Crystal + Item_WispDust at Prop_BrewingStand"),
               ("Gem_Ruby", "cave ore"), ("Gem_Sapphire", "cave ore"), ("Gem_Emerald", "cave ore"), ("Gem_Amber", "Prop_Tree_Kapok_Mature"),
               ("Bar_Copper", "Item_Copper at Prop_Furnace"), ("Bar_Iron", "Item_Iron at Prop_Furnace"), ("Bar_Gold", "Item_Gold at Prop_Furnace"),
               ("Bar_Starmetal", "Item_Starmetal at Prop_Starforge"), ("Cooked_Meat", "Item_Meat at Prop_Smoker"), ("Bread", "Item_Crop_Wheat x3")]:
    if not any(a["name"] == "Item_" + n for a in R):
        add("Item_" + n, "Gatherables", "Crafting / cooking / brewing ingredient", "from: " + src, prio=3)

# =============================================================== Dragon Warrior realm (realm_13; ADR-036/037/052)
# Source: Daedalus2 daedalus-core/.../world/retro/RetroMonster.java, RetroItem.java, RetroTile.java (+ Richey's bestiary
# and battle screenshots). Blocky 3D takes on the 8-bit sprites; colours are the sprites' body/accent.
DW = "Dragon Warrior realm"
SHAPE_PARTS = {0: "_Body _Eyes (squash/bounce)", 1: "_Body _Tail (floats)", 2: "_Body _Head _Spikes _LegFL _LegFR _LegBL _LegBR",
               3: "_Cap _Stem _FeetL _FeetR", 4: "_Body _Head _ArmL _ArmR _LegL _LegR _Shield _Sword", 5: "_Body _WingL _WingR",
               6: "_Box _Lid (snaps)", 7: "_Orb _Eye"}
for n, shape, body, acc, drop, rar in [
    ("BlightSlime", 0, "58D840", "188C10", "Item_Realm_Herb", "common"), ("BogSlime", 0, "8C34C8", "4C1478", "Item_Realm_Antidote", "uncommon"),
    ("LuckyDrip", 0, "F8B800", "C87800", "Item_Realm_MightSeed", "rare"), ("DustWisp", 1, "BCBCBC", "8C34C8", "Item_Realm_Tonic", "common"),
    ("EmberWisp", 1, "F87818", "D82800", "Item_Realm_Tonic", "uncommon"), ("Shardback", 2, "9C9C9C", "3CE0E0", "Item_Realm_Herb", "common"),
    ("Glassback", 2, "F0F0FC", "F878C8", "Item_Realm_StarShard", "uncommon"), ("Puffcap", 3, "D82800", "F0D090", "Item_Realm_Herb", "common"),
    ("Shadecap", 3, "8C34C8", "9C9C9C", "Item_Realm_LifeSeed", "uncommon"), ("Gloomwing", 5, "3C3C3C", "D82800", "Item_Realm_Torch", "common"),
    ("StareOrb", 7, "F8F8F8", "0058F8", "Item_Realm_Tonic", "uncommon"), ("Gnashbox", 6, "A0581C", "F8B800", "Item_Realm_StarShard", "rare"),
    ("MossKnight", 4, "2C8C18", "80D010", "Item_Realm_ChainMail", "uncommon"), ("StoneKnight", 4, "7C7C7C", "D82800", "Item_Realm_IronAxe", "rare"),
    ("ShardTyrant", 4, "F8B800", "8C34C8", "Item_Realm_StarShard", "legendary boss")]:
    notes = "#%s body, #%s accent; %s; RetroMonster shape %d" % (body, acc, rar, shape)
    if n == "ShardTyrant":
        notes += "; boss: gold armoured knight, purple crest, visor slit, purple oval shield, silver sword (battle screen, cave)"
    add("Mob_Realm_" + n, "Dragon Warrior", "Realm foe (turn-based battle, EXP/gold)", "drops: " + drop, rar,
        SHAPE_PARTS[shape] if n != "ShardTyrant" else "_Body _Head _Crest _ArmL _ArmR _LegL _LegR, Mob_Realm_ShardTyrant_Shield, Mob_Realm_ShardTyrant_Sword",
        prio=2 if n == "ShardTyrant" else 3, notes=notes, world=DW)
add("Mob_Realm_Wolf", "Dragon Warrior", "Realm foe (overworld screenshot)", "drops: Item_Realm_Herb", "common",
    "_Body _Head _Tail _LegFL _LegFR _LegBL _LegBR", prio=3, world=DW)
for n, role in (("Hero", "party lead: sword + shield"), ("Sage", "party healer/caster: robe + staff"), ("Scout", "party agile: hood + daggers")):
    add("Mob_Realm_Party_" + n, "Dragon Warrior", "Party member (Dragon Warrior / FF1 party)", "", "", "_Body _Head _ArmL _ArmR _LegL _LegR",
        prio=2, notes=role, world=DW)
for t, mech in [("Grass", "plains"), ("Tree", "forest (walkable)"), ("Hill", "hills"), ("Mountain", "impassable grey mountains"),
                ("Water", "sea/lake"), ("Sand", "desert"), ("Bridge", "crossings"), ("Swamp", "poison ground"),
                ("Town", "town tile -> Bld_Realm_Town"), ("Castle", "castle tile -> Bld_Realm_Castle"), ("Cave", "cave mouth"),
                ("Portal", "realm portal"), ("Chest", "treasure chest"), ("StairsDown", "dungeon stairs"), ("Throne", "throne room")]:
    add("Prop_Realm_Tile_" + t, "Dragon Warrior", "Overworld/dungeon tile (RetroTile %s)" % t.upper(), "", "", "", prio=3,
        notes="1 m x 1 m tile block, 8-bit palette", world=DW)
for n, mech, prio in [("Bld_Realm_Town", "Town: shops, inn", 3), ("Bld_Realm_Castle", "Castle: king, throne", 3),
                      ("Bld_Realm_Inn", "Rest to heal", 4), ("Bld_Realm_Shop", "Buy gear", 4),
                      ("Prop_Realm_Mountain", "Overworld mountain massif", 3), ("Prop_Realm_Forest", "Overworld forest clump", 3),
                      ("Prop_Realm_CaveEntrance", "Cave mouth", 3),
                      ("Prop_Realm_Cave_Stalactite", "Cave battle backdrop", 2), ("Prop_Realm_Cave_Stalagmite", "Cave battle backdrop", 3),
                      ("Prop_Realm_Cave_Floor", "Cave battle floor tile", 2), ("Prop_Realm_Cave_Wall", "Cave battle backdrop", 3),
                      ("Prop_Realm_Cave_Ceiling", "Cave battle backdrop: layered rock ceiling + stalactites", 2),
                      ("Prop_Realm_Cave_Torch", "Cave battle lighting", 2)]:
    add(n, "Dragon Warrior", mech, "", "", "", prio=prio, world=DW)
for n, kind, price, power in [("Herb", "use", 10, 25), ("Tonic", "use", 30, 10), ("Antidote", "use", 8, 0), ("Torch", "use", 8, 3),
                              ("Wings", "use", 25, 0), ("MightSeed", "use", 0, 2), ("LifeSeed", "use", 0, 6), ("BronzeKey", "key", 45, 1),
                              ("SilverKey", "key", 0, 2), ("StarKey", "key", 0, 3), ("Club", "weapon", 25, 4), ("CopperSword", "weapon", 110, 9),
                              ("IronAxe", "weapon", 280, 15), ("EmberBlade", "weapon", 0, 22), ("StarBlade", "weapon", 0, 30),
                              ("Clothes", "armor", 15, 2), ("LeatherVest", "armor", 70, 6), ("ChainMail", "armor", 240, 12),
                              ("ShardMail", "armor", 0, 18), ("MeteorMail", "armor", 0, 26), ("StarShard", "treasure", 0, 300)]:
    add("Item_Realm_" + n, "Dragon Warrior", "Realm %s (RetroItem; price %d, power %d)" % (kind, price, power),
        "dropped by realm foes / shops", kind, prio=3 if kind in ("weapon", "armor") else 4, world=DW)

from assets.flora2 import entries as _flora2   # flora wave 2: gatherable plants (growing, harvested, item)
R.extend(_flora2())
from assets.wave3 import entries as _wave3   # wave 3: fuller world (plants, trees, animals, town, realm)
_have = {r["name"] for r in R}
R.extend(x for x in _wave3() if x["name"] not in _have)

ASSETS = R
