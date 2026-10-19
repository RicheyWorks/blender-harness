import unreal, json
SUB = "/Game/BlenderBoss/Maps/BlenderBossIsland"; PERSIST = "/Game/Daedalus/DaedalusWorld"
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
out = {"world": world.get_path_name()}
try:
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if les.is_in_play_in_editor(): les.editor_request_end_play(); out["play"] = "ended"
except Exception as e: out["play_err"] = repr(e)
ls = unreal.GameplayStatics.get_streaming_level(world, "BlenderBossIsland")
out["before"] = ls.get_class().get_name() if ls else None
if ls and "AlwaysLoaded" not in out["before"]:
    nl = unreal.EditorLevelUtils.set_streaming_class_for_level(ls, unreal.LevelStreamingAlwaysLoaded)
    ls2 = unreal.GameplayStatics.get_streaming_level(world, "BlenderBossIsland"); out["after"] = ls2.get_class().get_name() if ls2 else None
    # save ONLY the persistent map (streaming list lives there) + our sublevel
    out["saved_world"] = unreal.EditorLoadingAndSavingUtils.save_map(world, PERSIST)
    lv = ls2.get_loaded_level() if ls2 else None
    if lv:
        try: out["saved_sub"] = unreal.EditorLevelUtils.save_level(lv) if hasattr(unreal.EditorLevelUtils, "save_level") else "n/a"
        except Exception as e: out["saved_sub_err"] = repr(e)
print(json.dumps(out))
