# SPDX-License-Identifier: MIT
"""LocalBridge: the bridge interface, executed in-process inside a headless Blender (blender -b).
Lets the same builders run without the GUI Blender on 9876, which the Unreal team's watcher uses for shipping."""
import io, contextlib, traceback

class LocalBridge:
    headless = True
    def py(self, code, timeout=None):
        import bpy
        ns = {"bpy": bpy, "__name__": "__bharness__"}; out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                exec(compile(code, "<bharness>", "exec"), ns)
        except Exception:
            return {"status": "error", "message": traceback.format_exc()[-1500:]}
        return {"status": "ok", "result": {"result": ns.get("result"), "stdout": out.getvalue()}}
    def call(self, cmd, **params):
        if cmd == "ping": return {"status": "ok", "result": {"pong": True, "headless": True}}
        return {"status": "error", "message": "%s is not available in headless Blender" % cmd}
    def close(self): pass
