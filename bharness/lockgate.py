# SPDX-License-Identifier: MIT
"""Compute-lock gate for the team link: wait until no OTHER bot holds an unexpired lock of a given name.
The lock is advisory (bus messages type lock/unlock, body.name); a holder is a bot whose latest lock has no later
unlock from the same bot and whose ts + ttl is still in the future. Our own lock never blocks us.
  python -m bharness.lockgate [N] [--attempts N] [--interval S] [--me blender-team] [--name compute] [--log <log.jsonl>]
Exit 0 = free (prints "free"), 3 = still held after N checks (prints the holders and their lock ids)."""
import argparse, datetime, json, sys, time

DEFAULT_LOG = r"C:\Users\730ri\projects\bot-team\link\log.jsonl"


def active(lines, now, me="blender-team", name="compute"):
    """lines: iterable of log.jsonl lines (str) or dicts. now: naive local datetime (log ts are local). -> {holder: lock id}."""
    held = {}
    for ln in lines:
        try:
            e = json.loads(ln) if isinstance(ln, str) else ln
        except ValueError:
            continue
        if not isinstance(e, dict) or e.get("type") not in ("lock", "unlock") or (e.get("body") or {}).get("name") != name:
            continue
        if e["type"] == "lock":
            try:
                held[e["from"]] = (datetime.datetime.fromisoformat(e["ts"]), float(e["body"].get("ttl", 900)), e.get("id"))
            except (KeyError, ValueError, TypeError):
                continue
        else:
            held.pop(e.get("from"), None)
    return {k: v[2] for k, v in held.items() if k != me and (now - v[0]).total_seconds() < v[1]}


def tail(path, n=1500):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.readlines()[-n:]


def wait_free(read, attempts=40, interval=10.0, me="blender-team", name="compute", now=datetime.datetime.now, sleep=time.sleep, log=print):
    """read() -> log lines. Returns (True, {}) once free, else (False, holders) after `attempts` checks."""
    a = {}
    for i in range(max(1, attempts)):
        a = active(read(), now(), me, name)
        if not a:
            return True, {}
        if i == 0:
            log("held %s" % a)
        if i < attempts - 1:
            sleep(interval)
    return False, a


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("n", nargs="?", type=int, help="attempts (legacy positional)")
    ap.add_argument("--attempts", type=int, default=40); ap.add_argument("--interval", type=float, default=10.0)
    ap.add_argument("--me", default="blender-team"); ap.add_argument("--name", default="compute"); ap.add_argument("--log", default=DEFAULT_LOG)
    o = ap.parse_args(argv)
    ok, a = wait_free(lambda: tail(o.log), o.n if o.n is not None else o.attempts, o.interval, o.me, o.name)
    print("free" if ok else "still held %s" % a, flush=True)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
