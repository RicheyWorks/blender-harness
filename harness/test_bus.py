# SPDX-License-Identifier: MIT
"""Team link client against a stand-in broker (same HTTP shape) and the file fallback. n/m line at the end."""
import json, os, sys, tempfile, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bharness import bus
from harness.check import Checks

def main():
    c = Checks(); art = tempfile.mkdtemp()
    srv = bus.standin(0); port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
    b = bus.Bus(art, url="http://127.0.0.1:%d" % port)
    c("health", b.health().get("ok") is True)
    c("ping -> pong", b.ping(5)["pong"] is True)
    mid = b.send("asset.ready", {"asset": "Tool_Test"})
    c("send returns broker id", isinstance(mid, int))
    got = b.wait(3)
    c("asset.shipped arrives", any(m["type"] == "asset.shipped" and m["body"]["asset"] == "Tool_Test" for m in got), json.dumps(got)[:200])
    c("cursor: no repeats", b.wait(0.5) == [])
    c.raises("unknown type refused", ValueError, lambda: bus.envelope("explode"))
    srv.shutdown(); srv.server_close()
    b2 = bus.Bus(art, url="http://127.0.0.1:%d" % port, timeout=0.5)
    c("broker down: queued", b2.send("note", {"text": "x"}) is None and len(b2.state["outbox"]) == 1)
    open(os.path.join(art, "feed.jsonl"), "w").write(json.dumps({"at": "x", "asset": "A", "event": "rejected", "why": "w"}) + "\n")
    got = b2.wait(0.5)
    c("file fallback reads feed", got and got[0]["type"] == "asset.rejected" and got[0]["body"]["why"] == "w")
    srv2 = bus.standin(port); threading.Thread(target=srv2.serve_forever, daemon=True).start()
    b2.timeout = 3; c("replay on reconnect", len(b2.flush()) == 1 and b2.state["outbox"] == [])
    srv2.shutdown()
    c.done()

if __name__ == "__main__":
    main()
