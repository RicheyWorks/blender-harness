"""The TCP client against a fake bridge: ok, error, garbage, big reply, timeout, refused."""
import socket
from harness.check import Checks
from harness.fakes import FakeTCP
from bharness.client import Bridge, BridgeError

t = Checks()
f = FakeTCP()
b = Bridge(port=f.port, timeout=5)
r = b.call("ping", x=1)
t("one JSON line out, one back; params echoed", r["status"] == "ok" and r["result"]["echo"] == {"x": 1})
t("py() sends execute_code with code", b.py("result=1")["result"]["echo"] == {"code": "result=1"})
t("errors come back as status=error, not exceptions", b.call("boom")["status"] == "error")
t.raises("garbage reply raises BridgeError", BridgeError, lambda: b.call("garbage"))
t("a 3 MB reply arrives whole", len(b.call("big")["result"]) == 3_000_000)
t.raises("a slow command times out on the client", socket.timeout, lambda: Bridge(port=f.port, timeout=0.5).call("slow"))
t("still answers after a client timeout", b.call("ping")["status"] == "ok")
s = socket.socket(); s.bind(("127.0.0.1", 0)); dead = s.getsockname()[1]; s.close()
t.raises("Blender closed -> ConnectionRefusedError", OSError, lambda: Bridge(port=dead, timeout=1).call("ping"))
t("up() is False when Blender is closed", Bridge(port=dead).up() is False)
t("up() is True when it answers", b.up())
logs = []
Bridge(port=f.port, log=logs.append).call("ping")
t("every call is logged with ms and bytes", logs and {"cmd", "ms", "bytes"} <= set(logs[0]))
t.done()
