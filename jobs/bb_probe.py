import unreal, json
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
ls = unreal.GameplayStatics.get_streaming_level(world, "BlenderBossIsland")
les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
print(json.dumps({"world": world.get_path_name(), "class": ls.get_class().get_name() if ls else None, "loaded": bool(ls and ls.get_loaded_level()), "pie": les.is_in_play_in_editor(),
  "api": [n for n in dir(unreal.EditorLevelUtils) if "stream" in n.lower() or "level" in n.lower()][:20]}))
