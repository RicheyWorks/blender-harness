# SPDX-License-Identifier: MIT
"""Raw bridge access: status, scene info, Python, and the 'is there unsaved work?' guard every writer uses."""
from ..contract import Plugin, Action, Risk


def unwrap(reply):
    if reply.get("status") != "ok":
        raise RuntimeError("bridge: " + str(reply.get("message")))
    return reply["result"]


def run(bridge, code, timeout=None):
    """Execute code in Blender; return its `result` variable."""
    return unwrap(bridge.py(code, timeout=timeout))["result"]


FILESTATE = "import bpy\nresult={'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty}"


class BridgePlugin(Plugin):
    name = "bridge"

    def actions(self):
        b = self.ctx.bridge
        return [
            Action("ping", lambda: unwrap(b.call("ping", timeout=5)), Risk.READ, "Blender version, open file, add-on"),
            Action("scene", lambda: unwrap(b.call("get_scene_info")), Risk.READ, "objects in the current scene"),
            Action("object", lambda name: unwrap(b.call("get_object_info", name=name)), Risk.READ, "one object", ["name"]),
            Action("filestate", lambda: run(b, FILESTATE), Risk.READ, "open file and whether it has unsaved work"),
            Action("python", lambda code, timeout=None: unwrap(b.py(code, timeout=timeout)), Risk.SCENE,
                   "run Python in Blender (stdout + result)", ["code"]),
        ]
