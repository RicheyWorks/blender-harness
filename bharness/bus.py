# SPDX-License-Identifier: MIT
"""Blender team client for the Blender team <-> Unreal team message bus (BUS-SCHEMA.md).

Transport: the Unreal team's team link broker, 127.0.0.1:9890 (ADR-053, Daedalus2/docs/TEAMLINK.md); override
with art\\BUS.json {"url": ...} or the env var DAEDALUS_BUS. If it's not reachable, the same messages go to the file bus: art\\bus\\outbox-blender.jsonl,
which we write, and art\\feed.jsonl, which we read. That way no message is lost while the server is down, and on reconnect
the outbox is replayed (ids make this idempotent).

  python -m bharness.bus health | ping | note <text> | ready <Asset> | wait [s]"""
import datetime, json, os, sys, threading, time, urllib.request, urllib.error, uuid
from bharness.context import DEFAULT_ART

V = 1
ME, THEM = "blender-team", "unreal-team"
PORT = 9890   # the Unreal team's team link broker (ADR-053, Daedalus2/docs/TEAMLINK.md)
TYPES = {"note", "ping", "pong", "ack", "asset.ready", "status",                                     # Blender team sends
         "asset.shipping", "asset.shipped", "asset.rejected", "asset.blocked", "asset.waiting"}       # Unreal team sends


def now(): return datetime.datetime.now().isoformat(timespec="seconds")


def endpoint(art=DEFAULT_ART):
    if os.environ.get("DAEDALUS_BUS"): return os.environ["DAEDALUS_BUS"].rstrip("/")
    try: return json.load(open(os.path.join(art, "BUS.json"), encoding="utf-8"))["url"].rstrip("/")
    except (OSError, ValueError, KeyError): return "http://127.0.0.1:%d" % PORT


def envelope(type_, body=None, to=THEM, reply_to=None):
    if type_ not in TYPES: raise ValueError("unknown type %r" % type_)
    return {"from": ME, "to": to, "type": type_, "body": body or {}, "reply_to": reply_to}


class Bus:
    """Team link client (POST /send, GET /wait long-poll, POST /ack, /heartbeat, /pending, /health).
    Broker down: messages queue in art\\bus\\outbox-blender.jsonl and replay on the next call; inbound falls back to feed.jsonl."""
    def __init__(self, art=DEFAULT_ART, url=None, timeout=5.0):
        self.art, self.url, self.timeout = art, url or endpoint(art), timeout
        self.dir = os.path.join(art, "bus"); os.makedirs(self.dir, exist_ok=True)
        self.state_p = os.path.join(self.dir, "blender-client.json")
        try: self.state = json.load(open(self.state_p, encoding="utf-8"))
        except (OSError, ValueError): self.state = {}
        self.state.setdefault("after", 0); self.state.setdefault("feed_pos", 0); self.state.setdefault("outbox", [])

    def _save(self):
        tmp = self.state_p + ".tmp"; json.dump(self.state, open(tmp, "w", encoding="utf-8")); os.replace(tmp, self.state_p)

    def _http(self, method, path, obj=None, timeout=None):
        req = urllib.request.Request(self.url + path, method=method, data=json.dumps(obj).encode() if obj is not None else None,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout or self.timeout) as r: return json.loads(r.read() or b"null")

    def health(self):
        try: return dict(self._http("GET", "/health") or {}, transport="teamlink", url=self.url)
        except (OSError, ValueError, urllib.error.URLError) as e: return {"ok": False, "transport": "file", "why": repr(e)[:200], "url": self.url}

    def heartbeat(self, status=""):
        try: return self._http("POST", "/heartbeat", {"me": ME, "status": status})
        except (OSError, ValueError, urllib.error.URLError): return None

    def send(self, type_, body=None, to=THEM, reply_to=None):
        m = envelope(type_, body, to, reply_to)
        self.state["outbox"].append(m); self._save()
        with open(os.path.join(self.dir, "outbox-blender.jsonl"), "a", encoding="utf-8") as f: f.write(json.dumps(dict(m, at=now())) + "\n")
        ids = self.flush()
        return ids[-1] if ids and not self.state["outbox"] else None

    def flush(self):
        ids = []
        while self.state["outbox"]:
            try: r = self._http("POST", "/send", self.state["outbox"][0])
            except (OSError, ValueError, urllib.error.URLError): break
            ids.append(r["id"]); self.state["outbox"].pop(0); self._save()
        return ids

    def ack(self, mid):
        try: return self._http("POST", "/ack", {"me": ME, "id": mid})
        except (OSError, ValueError, urllib.error.URLError): return None

    def wait(self, timeout=25.0):
        """Long-poll the broker for messages to blender-team after our cursor; ack each non-ack message."""
        try:
            r = self._http("GET", "/wait?me=%s&after=%d&timeout=%s" % (ME, self.state["after"], min(timeout, 55)), timeout=timeout + 5)
        except (OSError, ValueError, urllib.error.URLError):
            return self._feed_fallback()
        self.flush()
        msgs = r["messages"]; self.state["after"] = r["last"]; self._save()
        for m in msgs:
            if m["type"] not in ("ack", "pong"): self.ack(m["id"])
        return msgs

    def ping(self, timeout=20.0):
        t0 = time.time(); mid = self.send("ping")
        while mid and time.time() - t0 < timeout:
            for m in self.wait(max(1.0, timeout - (time.time() - t0))):
                if m["type"] == "pong" and m.get("reply_to") == mid: return {"ping": mid, "pong": True, "ms": round((time.time() - t0) * 1000)}
        return {"ping": mid, "pong": False}

    def _feed_fallback(self):
        p = os.path.join(self.art, "feed.jsonl"); out = []
        try:
            with open(p, encoding="utf-8") as f:
                f.seek(self.state["feed_pos"]); data = f.read(); self.state["feed_pos"] = f.tell()
        except OSError:
            return []
        for line in data.splitlines():
            try: e = json.loads(line)
            except ValueError: continue
            t = "asset." + str(e.get("event"))
            if t in TYPES: out.append({"id": None, "ts": e.get("at"), "from": THEM, "to": "*", "type": t,
                                       "body": {k: v for k, v in e.items() if k not in ("event", "at")}, "reply_to": None, "via": "feed"})
        self._save(); return out


# ------------------------------------------------------------------ stand-in server (tests only)
def standin(port=0, folder=None):
    """Tests only: a tiny broker with the team link's HTTP shape; it answers ping with pong and asset.ready with asset.shipped."""
    import tempfile
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import urlparse, parse_qs
    log, cond = [], threading.Condition()
    def put(frm, to, t, body, reply_to=None):
        with cond:
            m = {"id": len(log) + 1, "ts": now(), "from": frm, "to": to, "type": t, "body": body, "reply_to": reply_to}; log.append(m); cond.notify_all(); return m["id"]
    class H(BaseHTTPRequestHandler):
        def log_message(self, *a): pass
        def _j(self, obj):
            b = json.dumps(obj).encode(); self.send_response(200); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def do_GET(self):
            u = urlparse(self.path); q = {k: v[-1] for k, v in parse_qs(u.query).items()}
            if u.path == "/health": return self._j({"ok": True, "last": len(log)})
            if u.path == "/wait":
                me, after, dl = q["me"], int(q.get("after", 0)), time.time() + float(q.get("timeout", 5))
                with cond:
                    while True:
                        got = [m for m in log if m["id"] > after and m["from"] != me and m["to"] in (me, "*")]
                        if got or time.time() > dl: return self._j({"messages": got, "last": len(log)})
                        cond.wait(max(0.01, dl - time.time()))
        def do_POST(self):
            b = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if self.path == "/send":
                mid = put(b["from"], b["to"], b["type"], b.get("body") or {}, b.get("reply_to"))
                if b["type"] == "ping": put(THEM, b["from"], "pong", {}, mid)
                if b["type"] == "asset.ready": put(THEM, "*", "asset.shipped", {"asset": b["body"]["asset"], "result": "SHIPPED (stand-in)"})
                return self._j({"id": mid})
            if self.path in ("/ack", "/heartbeat"): return self._j({"ok": True})
    return ThreadingHTTPServer(("127.0.0.1", port), H)


def main(a=sys.argv[1:]):
    cmd = a[0] if a else "health"
    b = Bus()
    if cmd == "health": print(json.dumps(b.health()))
    elif cmd == "ping": print(json.dumps(b.ping()))
    elif cmd == "note": print(json.dumps({"id": b.send("note", {"text": " ".join(a[1:])})}))
    elif cmd == "ready": print(json.dumps({"id": b.send("asset.ready", {"asset": a[1]})}))
    elif cmd == "wait":
        for m in b.wait(float(a[1]) if len(a) > 1 else 25): print(json.dumps(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
