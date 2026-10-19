# SPDX-License-Identifier: MIT
"""bharness.lockgate: who holds the advisory compute lock, and waiting for it. n/m line at the end."""
import datetime, io, json, os, sys, tempfile, contextlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bharness import lockgate as G
from harness.check import Checks

NOW = datetime.datetime(2026, 10, 19, 4, 0, 0)


def ev(i, who, typ, ago, ttl=900, name="compute"):
    b = {"name": name}
    if typ == "lock":
        b["ttl"] = ttl
    return json.dumps({"id": i, "ts": (NOW - datetime.timedelta(seconds=ago)).isoformat(timespec="seconds"), "from": who, "to": "*", "type": typ, "body": b})


def unl(i, who, lock_id, ago, name="compute"):
    return json.dumps({"id": i, "ts": (NOW - datetime.timedelta(seconds=ago)).isoformat(timespec="seconds"), "from": who, "to": "*", "type": "unlock",
                       "body": {"name": name, "lock_id": lock_id}, "reply_to": lock_id})


class Bus:
    """In-memory team link: post() appends a message with the next id at NOW. intrude_after_lock = a bot that grabs the lock
    right after our lock lands (the 06:42 race); intruder_leaves_after = it unlocks after that many of our back-offs."""
    def __init__(self, lines):
        self.lines = list(lines); self.posted = []; self.intrude_after_lock = None; self.intruder_leaves_after = None; self.backoffs = 0

    def next_id(self):
        return max([json.loads(l)["id"] for l in self.lines] + [0]) + 1

    def read(self):
        return list(self.lines)

    def post(self, m):
        i = self.next_id(); e = dict(m, id=i, ts=NOW.isoformat(timespec="seconds")); self.lines.append(json.dumps(e)); self.posted.append(e)
        if m["type"] == "lock" and self.intrude_after_lock and not any(json.loads(l)["from"] == self.intrude_after_lock for l in self.lines):
            self.lines.append(ev(self.next_id(), self.intrude_after_lock, "lock", 0))
        if m["type"] == "unlock" and self.intruder_leaves_after is not None:
            self.backoffs += 1
            if self.backoffs >= self.intruder_leaves_after:
                held = G.active(self.lines, NOW).get(self.intrude_after_lock)
                if held:
                    self.lines.append(unl(self.next_id(), self.intrude_after_lock, held, 0))
        return i


def main():
    c = Checks()
    c("empty log: free", G.active([], NOW) == {})
    c("lock then unlock: free", G.active([ev(1, "a", "lock", 60), ev(2, "a", "unlock", 30)], NOW) == {})
    c("live lock: held with its id", G.active([ev(1, "a", "lock", 60)], NOW) == {"a": 1})
    c("expired ttl: free", G.active([ev(1, "a", "lock", 1000, ttl=900)], NOW) == {})
    c("own lock never blocks", G.active([ev(1, "blender-team", "lock", 5)], NOW) == {})
    c("other lock names ignored", G.active([ev(1, "a", "lock", 5, name="gpu")], NOW) == {})
    c("unlock by someone else does not free", G.active([ev(1, "a", "lock", 60), ev(2, "b", "unlock", 30)], NOW) == {"a": 1})
    c("re-lock after unlock: held, newest id", G.active([ev(1, "a", "lock", 90), ev(2, "a", "unlock", 80), ev(3, "a", "lock", 10)], NOW) == {"a": 3})
    c("several holders", G.active([ev(1, "a", "lock", 60), ev(2, "b", "lock", 50), ev(3, "c", "lock", 40), ev(4, "b", "unlock", 5)], NOW) == {"a": 1, "c": 3})
    c("junk and non-lock lines skipped", G.active(["not json", "", json.dumps([1]), json.dumps({"type": "note"}), ev(1, "a", "lock", 5)], NOW) == {"a": 1})
    c("bad ts skipped", G.active([json.dumps({"id": 9, "from": "a", "type": "lock", "ts": "nope", "body": {"name": "compute"}})], NOW) == {})
    c("dict lines accepted", G.active([json.loads(ev(1, "a", "lock", 5))], NOW) == {"a": 1})
    state = {"lines": [ev(1, "a", "lock", 5)], "sleeps": 0}
    def sl(s):
        state["sleeps"] += 1
        if state["sleeps"] == 2:
            state["lines"].append(ev(2, "a", "unlock", 1))
    ok, a = G.wait_free(lambda: state["lines"], attempts=10, interval=0, now=lambda: NOW, sleep=sl, log=lambda *_: None)
    c("wait_free returns once released", ok and a == {} and state["sleeps"] == 2, state)
    n = {"s": 0}
    ok, a = G.wait_free(lambda: [ev(1, "a", "lock", 5)], attempts=3, interval=0, now=lambda: NOW, sleep=lambda s: n.__setitem__("s", n["s"] + 1), log=lambda *_: None)
    c("wait_free gives up after attempts, no trailing sleep", not ok and a == {"a": 1} and n["s"] == 2)
    # --- unlock by id, sole-holder acquire, never unlock a lock we do not hold (06:42 race: 50309 vs 50310) ---
    c("unlock naming a stale lock_id does not free the newer lock", G.active([ev(1, "a", "lock", 90), ev(3, "a", "lock", 10), unl(4, "a", 1, 5)], NOW) == {"a": 3})
    c("unlock naming the live lock_id frees it", G.active([ev(3, "a", "lock", 10), unl(4, "a", 3, 5)], NOW) == {})
    c("mine: our live lock id", G.mine([ev(1, "blender-team", "lock", 10)], NOW) == 1 and G.mine([], NOW) is None)
    bus = Bus([]); uid, why = G.release(bus.read, bus.post, 7, now=lambda: NOW)
    c("release with no lock of ours: nothing posted", uid is None and bus.posted == [] and why)
    bus = Bus([ev(5, "unreal-epic-boss", "lock", 5), ev(6, "blender-team", "lock", 60), ev(7, "blender-team", "unlock", 50)])
    uid, why = G.release(bus.read, bus.post, 6, now=lambda: NOW)
    c("release after we already unlocked: skipped, UEB untouched", uid is None and bus.posted == [] and G.active(bus.lines, NOW) == {"unreal-epic-boss": 5})
    bus = Bus([ev(8, "blender-team", "lock", 60)]); uid, why = G.release(bus.read, bus.post, 9, now=lambda: NOW)
    c("release of a foreign/stale id: skipped", uid is None and bus.posted == [] and "not 9" in why)
    bus = Bus([ev(8, "blender-team", "lock", 60)]); uid, _ = G.release(bus.read, bus.post, 8, now=lambda: NOW)
    m = bus.posted[-1]
    c("release of our live lock: unlock carries lock_id + reply_to", uid == 9 and m["type"] == "unlock" and m["body"]["lock_id"] == 8 and m["reply_to"] == 8 and G.mine(bus.lines, NOW) is None)
    bus = Bus([]); lid, h = G.acquire(bus.read, bus.post, note="t", attempts=1, interval=0, settle=0, now=lambda: NOW, sleep=lambda s: None, log=lambda *_: None)
    c("acquire on a free lock: sole holder, one lock posted", lid == 1 and h == {} and [m["type"] for m in bus.posted] == ["lock"])
    bus = Bus([]); bus.intrude_after_lock = "unreal-epic-boss"
    lid, h = G.acquire(bus.read, bus.post, attempts=1, interval=0, settle=0, tries=2, now=lambda: NOW, sleep=lambda s: None, rand=lambda: 0.5, log=lambda *_: None)
    types = [(m["type"], m["body"].get("lock_id")) for m in bus.posted]
    c("race: another bot locks inside the window -> we release ONLY ours (by id) and back off", types[:2] == [("lock", None), ("unlock", 1)] and G.active(bus.lines, NOW).get("unreal-epic-boss") == 2, types)
    c("race: we never take it while they hold it (gives up, holders reported)", lid is None and h == {"unreal-epic-boss": 2})
    bus = Bus([]); bus.intrude_after_lock = "unreal-epic-boss"; bus.intruder_leaves_after = 1
    sl = []; lid, h = G.acquire(bus.read, bus.post, attempts=3, interval=10, settle=0, tries=3, now=lambda: NOW, sleep=sl.append, rand=lambda: 0.5, log=lambda *_: None)
    c("race then free: retry succeeds after a jittered back-off", lid is not None and h == {} and 15.0 in sl and G.mine(bus.lines, NOW) == lid, (lid, sl))
    bus = Bus([ev(1, "hephaestus", "lock", 5)])
    lid, h = G.acquire(bus.read, bus.post, attempts=2, interval=0, settle=0, now=lambda: NOW, sleep=lambda s: None, log=lambda *_: None)
    c("acquire while held: no lock posted, exit-3 path", lid is None and bus.posted == [] and h == {"hephaestus": 1})
    d = tempfile.mkdtemp(); p = os.path.join(d, "log.jsonl")
    with open(p, "w", encoding="utf-8") as f:
        f.write(ev(1, "zz-test-holder", "lock", -10 ** 7, ttl=10 ** 9) + "\n")   # far-future lock: held whatever the real clock says
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = G.main(["1", "--interval", "0", "--log", p])
    c("CLI legacy positional, held -> exit 3", rc == 3 and "still held" in out.getvalue(), out.getvalue())
    with open(p, "a", encoding="utf-8") as f:
        f.write(ev(2, "zz-test-holder", "unlock", 0) + "\n")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        rc = G.main(["--attempts", "1", "--log", p])
    c("CLI free -> exit 0", rc == 0 and out.getvalue().strip() == "free", out.getvalue())
    c("tail keeps the last n lines", len(G.tail(p, 1)) == 1)
    c.done()


if __name__ == "__main__":
    main()
