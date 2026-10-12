"""Stand-ins: a fake Blender bridge in-process, and a fake TCP bridge for the client suite."""
import json, os, socket, threading, time

QUEUE = """# Art queue (test)

| # | Asset | Kind | Size | Status | Notes |
|---|---|---|---|---|---|
| 1 | Prop_BHTest | prop | 1 m | TODO | throwaway test crate |
| 2 | Prop_Other | prop | 1 m | DOING (Someone Else) | |
| 3 | Prop_Shipping | prop | 1 m | READY | |
| 4 | Prop_Rej | prop | 1 m | REJECTED: triangle budget | |
| 5 | Prop_Blk | prop | 1 m | BLOCKED: Unreal in Play | |
"""


def crate(name="Prop_BHTest", tris=24, scale=(1, 1, 1), slots=1, images=False, zmin=0.0):
    return {"asset": name, "collection": True, "loose_meshes": [], "objects": [
        {"name": name + "_Body", "tris": tris, "scale": list(scale), "slots": slots, "empty_slots": 0,
         "images": images, "min": [-0.5, -0.5, zmin], "max": [0.5, 0.5, zmin + 1.0], "origin": [0, 0, 0]}]}


class FakeBridge:
    """Answers the harness's own code snippets the way Blender would. Records every call."""

    def __init__(self, file="", dirty=False, assets=None):
        self.file, self.dirty, self.assets, self.calls = file, dirty, assets or {}, []

    def ok(self, res):
        return {"id": 1, "status": "ok", "result": res}

    def call(self, type_, timeout=None, **p):
        self.calls.append((type_, p))
        if type_ == "ping":
            return self.ok({"blender": "4.3.1", "file": self.file, "background": False, "addon": "1.0.2"})
        if type_ == "get_scene_info":
            return self.ok({"objects": []})
        if type_ == "get_object_info":
            return {"id": 1, "status": "error", "message": "no object " + p.get("name", "")}
        if type_ == "viewport_screenshot":
            return self.ok({"image_png_base64": "iVBORw0KGgo=", "width": 4, "height": 4})
        if type_ == "execute_code":
            return self.code(p["code"])
        return {"id": 1, "status": "error", "message": "unknown command"}

    def py(self, code, timeout=None):
        return self.call("execute_code", code=code)

    def code(self, c):
        r = lambda v: self.ok({"stdout": "", "result": v})
        if "INVOKE_DEFAULT" in c:
            return {"id": 1, "status": "error", "message": "fake: a modal would open (INVOKE_DEFAULT)"}
        if "result={'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty}" in c and "save_as_mainfile" not in c:
            return r({"file": self.file, "dirty": self.dirty})
        if "save_as_mainfile" in c:
            path = c.split("filepath=")[1].split(", check_existing")[0].strip("'\"").replace("\\\\", "\\")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "wb").write(b"BLENDER-fake")
            self.file, self.dirty = path, False
            return r({"file": path, "dirty": False})
        if "open_mainfile" in c or "read_homefile" in c:
            self.dirty = False
            return r(self.file)
        if "col = bpy.data.collections.get(" in c:
            name = c.split("bpy.data.collections.get(")[1].split(")")[0].strip("'\"")
            return r(self.assets.get(name, {"asset": name, "collection": False, "objects": [], "loose_meshes": []}))
        if "BH_TT_Cam" in c:
            folder = c.split("os.makedirs(")[1].split(", exist_ok")[0].strip("'\"").replace("\\\\", "\\")
            n = int(c.split("for i in range(")[-1].split(")")[0])
            os.makedirs(folder, exist_ok=True)
            out = []
            for i in range(n):
                f = os.path.join(folder, "turn_%02d.png" % i); open(f, "wb").write(b"\x89PNG"); out.append(f)
            return r(out)
        if "result = 1+1" in c:
            return r(2)
        return r(None)


class FakeTCP:
    """A tiny TCP bridge: `ping` ok, `boom` error, `slow` sleeps, `big` returns ~3 MB."""

    def __init__(self):
        self.s = socket.socket(); self.s.bind(("127.0.0.1", 0)); self.s.listen(8)
        self.port = self.s.getsockname()[1]
        threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            try:
                c, _ = self.s.accept()
            except OSError:
                return
            threading.Thread(target=self.one, args=(c,), daemon=True).start()

    def one(self, c):
        buf = b""
        while not buf.endswith(b"\n"):
            d = c.recv(65536)
            if not d:
                break
            buf += d
        req = json.loads(buf)
        t = req["type"]
        if t == "slow":
            time.sleep(2)
        if t == "garbage":
            c.sendall(b"not json\n"); c.close(); return
        resp = {"id": req["id"], "status": "ok", "result": {"echo": req["params"]}}
        if t == "boom":
            resp = {"id": req["id"], "status": "error", "message": "ValueError: boom"}
        if t == "big":
            resp["result"] = "x" * 3_000_000
        c.sendall(json.dumps(resp).encode() + b"\n"); c.close()
