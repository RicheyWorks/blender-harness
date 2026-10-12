# SPDX-License-Identifier: MIT
"""Bus client against the stand-in server and the file fallback. n/m line at the end."""
import json, os, sys, tempfile, threading
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bharness import bus
from harness.check import Checks

def main():
    c = Checks()
    art = tempfile.mkdtemp()
    srv = bus.standin(0); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    b = bus.Bus(art, url="http://127.0.0.1:%d" % port)
    c("health over http", b.health().get("ok") is True)
    m = b.send("ready", "Tool_Test", {"tris": 44})
    c("send acked (nothing unsent)", b.state["unsent"] == [])
    got = b.poll()
    c("reply arrives", any(x["type"] == "shipped" and x["reply_to"] == m["id"] for x in got), json.dumps(got)[:200])
    c("since cursor: no repeats", b.poll() == [])
    try: bus.envelope("explode"); ok = False
    except ValueError: ok = True
    c("unknown type refused", ok)
    srv.shutdown(); srv.server_close()
    b2 = bus.Bus(art, url="http://127.0.0.1:%d" % port, timeout=0.5)
    b2.send("status", None, {"state": "paused"})
    c("server down: message kept in outbox", len(b2.state["unsent"]) == 1)
    open(os.path.join(art, "feed.jsonl"), "w").write(json.dumps({"at": "x", "asset": "A", "event": "rejected", "why": "w"}) + "\n")
    got = b2.poll()
    c("file fallback reads feed", got and got[0]["type"] == "rejected" and got[0]["body"]["why"] == "w")
    srv2 = bus.standin(port); threading.Thread(target=srv2.serve_forever, daemon=True).start()
    b2.timeout = 3; c("replay on reconnect", b2.flush() == 1 and b2.state["unsent"] == [])
    srv2.shutdown()
    c.done()

if __name__ == "__main__":
    sys.exit(main())
