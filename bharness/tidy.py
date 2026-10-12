# SPDX-License-Identifier: MIT
"""Post-job tidy for the GUI Blender (9876): close extra windows (render views, preferences, popups), keeping the main one.
Never saves, never discards: it only closes secondary windows. Skips while the watcher is shipping (it owns Blender then)."""
import json, sys
from bharness.context import Context
from bharness.plugins.bridge import run
from bharness.plugins.queue import QueuePlugin

CODE = r'''
import bpy
wm = bpy.context.window_manager; closed = 0
for w in list(wm.windows)[1:]:
    try:
        with bpy.context.temp_override(window=w): bpy.ops.wm.window_close()
        closed += 1
    except Exception: pass
result = {"closed": closed, "windows": len(wm.windows)}
'''

def main():
    ctx = Context(); busy = QueuePlugin(ctx).watcher_busy()
    if busy: print(json.dumps({"tidy": "skipped", "watcher_shipping": busy})); return 0
    try: print(json.dumps({"tidy": run(ctx.bridge, CODE, timeout=20)}))
    except Exception as e: print(json.dumps({"tidy": "bridge unavailable", "why": repr(e)[:200]}))
    return 0

if __name__ == "__main__":
    sys.exit(main())
