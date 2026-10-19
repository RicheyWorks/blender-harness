import unreal, json
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ls = unreal.GameplayStatics.get_streaming_level(world, "BlenderBossIsland"); lv = ls.get_loaded_level() if ls else None
acts = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
n = sum(1 for a in acts if str(a.get_folder_path()).startswith("BlenderBoss"))
print(json.dumps({"class": ls.get_class().get_name() if ls else None, "loaded": bool(lv), "bb_actors": n, "pie": unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor()}))
