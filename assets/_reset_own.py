"""One-off: drop an untitled scene only if it is exactly our own half-built asset (named in argv)."""
import sys
from bharness.context import Context
from bharness.plugins.bridge import run
b = Context().bridge
n = sys.argv[1]
s = run(b, "import bpy\nresult={'file':bpy.data.filepath,'dirty':bpy.data.is_dirty,'cols':[c.name for c in bpy.data.collections],'objs':[o.name for o in bpy.data.objects]}")
print(s)
if s["file"] == "" and s["cols"] == [n] and set(s["objs"]) <= {n}:
    print("reset:", run(b, "import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\nresult=bpy.data.is_dirty"))
else:
    print("not ours; left alone")
