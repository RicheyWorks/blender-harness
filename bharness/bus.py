# SPDX-License-Identifier: MIT
"""Blender team client for the Blender team <-> Unreal team message bus (BUS-SCHEMA.md).

Transport: the Unreal team's local HTTP server (endpoint found in art\\BUS.json {"url": "http://127.0.0.1:<port>"},
or the env var DAEDALUS_BUS). If it's not reachable, the same messages go to the file bus: art\\bus\\outbox-blender.jsonl,
which we write, and art\\feed.jsonl, which we read. That way no message is lost while the server is down, and on reconnect
the outbox is replayed (ids make this idempotent).

  python -m bharness.bus health
  python -m bharness.bus send <type> [asset] [json-body]
  python -m bharness.bus poll [seconds]
  python -m bharness.bus standin [port]     local stand-in server for tests (NOT the Unreal team's server)"""
import datetime, json, os, sys, threading, time, urllib.request, urllib.error, uuid
from bharness.context import DEFAULT_ART

V = 1
TYPES = {"hello", "ready", "status", "note", "ack",                # Blender team -> Unreal team
         "shipping", "shipped", "rejected", "blocked", "waiting"}  # Unreal team -> Blender team


def now(): return datetime.datetime.now().isoformat(timespec="seconds")


def envelope(type_, asset=None, body=None, frm="blender", to="unreal", reply_to=None):
    if type_ not in TYPES: raise ValueError("unknown type %r" % type_)
    return {"v": V, "id": str(uuid.uuid4()), "from": frm, "to": to, "type": type_, "asset": asset, "at": now(),
            "reply_to": reply_to, "body": body or {}}


def endpoint(art=DEFAULT_ART):
    if os.environ.get("DAEDALUS_BUS"): return os.environ["DAEDALUS_BUS"].rstrip("/")
    try: return json.load(open(os.path.join(art, "BUS.json"), encoding="utf-8"))["url"].rstrip("/")
    except (OSError, ValueError, KeyError): return None


class Bus:
    def __init__(self, art=DEFAULT_ART, url=None, timeout=3.0):
        self.art, self.url, self.timeout = art, url or endpoint(art), timeout
        self.dir = os.path.join(art, "bus"); os.makedirs(self.dir, exist_ok=True)
        self.state_p = os.path.join(self.dir, "blender-client.json")
        try: self.state = json.load(open(self.state_p, encoding="utf-8"))
        except (OSError, ValueError): self.state = {"since": None, "feed_pos": 0, "unsent": []}

    def _save(self):
        tmp = self.state_p + ".tmp"; json.dump(self.state, open(tmp, "w", encoding="utf-8")); os.replace(tmp, self.state_p)

    def _http(self, method, path, obj=None):
        req = urllib.request.Request(self.url + path, method=method, data=json.dumps(obj).encode() if obj is not None else None,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r: return json.loads(r.read() or b"null")

    def health(self):
        if not self.url: return {"ok": False, "transport": "file", "why": "no art\\BUS.json / DAEDALUS_BUS"}
        try: return dict(self._http("GET", "/v1/health") or {}, transport="http", url=self.url)
        except (OSError, ValueError, urllib.error.URLError) as e: return {"ok": False, "transport": "file", "why": repr(e)[:200], "url": self.url}

    def send(self, type_, asset=None, body=None, reply_to=None):
        m = envelope(type_, asset, body, reply_to=reply_to)
        with open(os.path.join(self.dir, "outbox-blender.jsonl"), "a", encoding="utf-8") as f: f.write(json.dumps(m) + "\n")
        self.state["unsent"].append(m["id"]); self._save()
        self.flush()
        return m

    def flush(self):
        """Replay outbox messages the server hasn't acked (POST is idempotent on id)."""
        if not self.state["unsent"] or not self.url: return 0
        msgs = {}
        for line in open(os.path.join(self.dir, "outbox-blender.jsonl"), encoding="utf-8"):
            try: m = json.loads(line); msgs[m["id"]] = m
            except ValueError: pass
        sent = 0
        for i in list(self.state["unsent"]):
            try:
                r = self._http("POST", "/v1/messages", msgs[i]) if i in msgs else {"ok": True}
                if r and r.get("ok"): self.state["unsent"].remove(i); sent += 1
            except (OSError, ValueError, urllib.error.URLError):
                break
        self._save(); return sent

    def poll(self, seconds=0, every=2):
        """Messages for the Blender team: HTTP if up (GET /v1/messages?to=blender&since=<id>), else feed.jsonl."""
        t0 = time.time()
        while True:
            out = self._poll_once()
            if out or time.time() - t0 >= seconds: return out
            time.sleep(every)

    def _poll_once(self):
        if self.url:
            try:
                q = "/v1/messages?to=blender" + ("&since=" + self.state["since"] if self.state["since"] else "")
                msgs = self._http("GET", q) or []
                if msgs: self.state["since"] = msgs[-1]["id"]; self._save()
                self.flush()
                return msgs
            except (OSError, ValueError, urllib.error.URLError):
                pass
        # file fallback: translate watcher feed events into envelopes
        p = os.path.join(self.art, "feed.jsonl"); out = []
        try:
            with open(p, encoding="utf-8") as f:
                f.seek(self.state["feed_pos"]); data = f.read(); self.state["feed_pos"] = f.tell()
        except OSError:
            return []
        for line in data.splitlines():
            try: e = json.loads(line)
            except ValueError: continue
            t = e.get("event")
            if t in TYPES:
                m = envelope(t, e.get("asset"), {k: v for k, v in e.items() if k not in ("asset", "event", "at")}, frm="unreal", to="blender")
                m["at"] = e.get("at"); out.append(m)
        self._save(); return out


# ------------------------------------------------------------------ stand-in server (tests only)
def standin(port=8790):
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    log, seen, lock = [], set(), threading.Lock()

    class H(BaseHTTPRequestHandler):
        def _j(self, code, obj):
            b = json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith("/v1/health"): return self._j(200, {"ok": True, "v": V, "server": "standin"})
            if self.path.startswith("/v1/messages"):
                from urllib.parse import urlparse, parse_qs
                q = parse_qs(urlparse(self.path).query); to = q.get("to", [None])[0]; since = q.get("since", [None])[0]
                with lock:
                    ids = [m["id"] for m in log]; start = ids.index(since) + 1 if since in ids else 0
                    return self._j(200, [m for m in log[start:] if to in (None, m["to"])])
            self._j(404, {"ok": False})
        def do_POST(self):
            m = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if m.get("v") != V or m.get("type") not in TYPES or not m.get("id"): return self._j(400, {"ok": False, "why": "bad envelope"})
            with lock:
                if m["id"] not in seen:
                    seen.add(m["id"]); log.append(m)
                    if m["type"] == "ready":   # the stand-in plays the Unreal team: answer every ready with shipped
                        r = envelope("shipped", m["asset"], {"result": "SHIPPED (stand-in)", "tris": m["body"].get("tris")}, frm="unreal", to="blender", reply_to=m["id"])
                        seen.add(r["id"]); log.append(r)
            self._j(200, {"ok": True, "id": m["id"]})
    srv = ThreadingHTTPServer(("127.0.0.1", port), H)
    return srv


def main(a=sys.argv[1:]):
    cmd = a[0] if a else "health"
    if cmd == "standin":
        s = standin(int(a[1]) if len(a) > 1 else 8790); print("standin on", s.server_address, flush=True); s.serve_forever()
    b = Bus()
    if cmd == "health": print(json.dumps(b.health()))
    elif cmd == "send": print(json.dumps(b.send(a[1], a[2] if len(a) > 2 else None, json.loads(a[3]) if len(a) > 3 else None)))
    elif cmd == "poll":
        for m in b.poll(float(a[1]) if len(a) > 1 else 0): print(json.dumps(m))
    return 0


if __name__ == "__main__":
    sys.exit(main())
