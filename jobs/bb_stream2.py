import unreal, json
SUB = "/Game/BlenderBoss/Maps/BlenderBossIsland"; PERSIST = "/Game/Daedalus/DaedalusWorld"
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world(); out = {}
ls = unreal.GameplayStatics.get_streaming_level(world, "BlenderBossIsland"); lv = ls.get_loaded_level()
if lv and lv.get_package().is_dirty() if hasattr(lv.get_package(), "is_dirty") else False: out["note"] = "sublevel dirty - skipped"
else:
    out["removed"] = unreal.EditorLevelUtils.remove_level_from_world(lv)
    ls2 = unreal.EditorLevelUtils.add_level_to_world(world, SUB, unreal.LevelStreamingAlwaysLoaded)
    out["after"] = ls2.get_class().get_name() if ls2 else None
    out["saved_world"] = unreal.EditorLoadingAndSavingUtils.save_map(world, PERSIST)
print(json.dumps(out))
