# SPDX-License-Identifier: MIT
"""Thin client for the Claude Blender Bridge: one JSON line out, one JSON line back, a fresh socket per call.

Bridge commands (add-on 1.0.2): ping, get_scene_info, get_object_info, execute_code, viewport_screenshot,
render_image. Note a client timeout does NOT cancel the work: Blender finishes it, and the next call waits."""
import itertools, json, socket, time


class BridgeError(Exception):
    pass


class Bridge:
    def __init__(self, host="127.0.0.1", port=9876, timeout=55.0, log=None):
        self.host, self.port, self.timeout, self.log = host, port, timeout, log
        self._ids = itertools.count(1)

    def call(self, type_, timeout=None, **params):
        rid = next(self._ids)
        msg = json.dumps({"id": rid, "type": type_, "params": params}) + "\n"
        t0 = time.time()
        with socket.create_connection((self.host, self.port), timeout=timeout or self.timeout) as s:
            s.sendall(msg.encode("utf-8"))
            buf = b""
            while not buf.endswith(b"\n"):
                chunk = s.recv(1 << 20)
                if not chunk:
                    break
                buf += chunk
        try:
            reply = json.loads(buf.decode("utf-8"))
        except ValueError:
            raise BridgeError("unparseable reply (%d bytes): %r" % (len(buf), buf[:200]))
        if self.log:
            self.log({"cmd": type_, "ms": int((time.time() - t0) * 1000), "bytes": len(buf),
                      "status": reply.get("status"), "message": reply.get("message")})
        return reply

    def py(self, code, timeout=None):
        return self.call("execute_code", timeout=timeout, code=code)

    def up(self):
        try:
            return self.call("ping", timeout=3).get("status") == "ok"
        except OSError:
            return False
