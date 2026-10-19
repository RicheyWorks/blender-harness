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
