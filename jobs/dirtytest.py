import bpy
f=r"C:\Users\730ri\projects\bot-team\art\Prop\Prop_Grok_SeedPod.blend"
bpy.ops.wm.open_mainfile(filepath=f); print("A", bpy.data.is_dirty)
r=bpy.ops.wm.save_as_mainfile('EXEC_DEFAULT', filepath=f, check_existing=False); print("B", r, bpy.data.is_dirty)
