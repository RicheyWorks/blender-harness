# SPDX-License-Identifier: MIT
"""Compute-lock gate for the team link: wait until no OTHER bot holds an unexpired lock of a given name.
The lock is advisory (bus messages type lock/unlock, body.name); a holder is a bot whose latest lock has no later
unlock from the same bot and whose ts + ttl is still in the future. Our own lock never blocks us. An unlock that names a
body.lock_id only releases that lock (a stale or foreign id is ignored).
  python -m bharness.lockgate [N] [--attempts N] [--interval S] [--me blender-team] [--name compute] [--log <log.jsonl>]
      wait only. Exit 0 = free (prints "free"), 3 = still held after N checks (prints the holders and their lock ids).
  python -m bharness.lockgate --acquire [--ttl S] [--note TEXT] [--settle S] [--tries N] ...
      wait, post our lock, re-read after --settle seconds and confirm we are the SOLE holder; if another bot locked inside
      that window, release only ours (by id), back off (interval x 1..2, jittered) and retry. Prints "lock <id>" (exit 0)
      or "still held {...}" (exit 3). (Added after the 06:42 race: blender-team 50309 vs unreal-epic-boss 50310.)
  python -m bharness.lockgate --release ID
      unlock ONLY if our live lock is ID (body.lock_id = ID, reply_to = ID). Prints "unlock <id>", or "skip: ..." when the
      lock is not ours / already released / expired: we never unlock a lock we do not hold. Exit 0 either way."""
import argparse, datetime, json, random, sys, time, urllib.request

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
            lid = (e.get("body") or {}).get("lock_id")
            if lid is None or (e.get("from") in held and held[e["from"]][2] == lid):
                held.pop(e.get("from"), None)
    live = {k: v[2] for k, v in held.items() if (now - v[0]).total_seconds() < v[1]}
    return live if me is None else {k: v for k, v in live.items() if k != me}


def mine(lines, now, me="blender-team", name="compute"):
    """Our own live lock id, or None."""
    return active(lines, now, None, name).get(me)


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


BUS = "http://127.0.0.1:9890/send"


def bus_post(msg, url=BUS):
    """POST one team-link message; returns its id."""
    req = urllib.request.Request(url, data=json.dumps(msg).encode(), headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode()).get("id")


def release(read, post, lock_id, me="blender-team", name="compute", now=datetime.datetime.now):
    """Unlock only our own live lock `lock_id`. -> (unlock message id, None) or (None, reason)."""
    cur = mine(read(), now(), me, name)
    if cur is None:
        return None, "no live %s lock held by %s" % (name, me)
    if cur != lock_id:
        return None, "our live lock is %s, not %s" % (cur, lock_id)
    return post({"from": me, "to": "*", "type": "unlock", "reply_to": lock_id, "body": {"name": name, "lock_id": lock_id, "forced": False}}), None


def acquire(read, post, me="blender-team", name="compute", ttl=900, note="", attempts=40, interval=10.0, settle=3.0, tries=5,
            now=datetime.datetime.now, sleep=time.sleep, rand=random.random, log=print):
    """Wait until free, lock, then confirm we are the sole holder. On contention release ours (by id), back off, retry.
    -> (lock id, {}) or (None, holders)."""
    holders = {}
    for t in range(max(1, tries)):
        ok, holders = wait_free(read, attempts, interval, me, name, now, sleep, log)
        if not ok:
            return None, holders
        lid = post({"from": me, "to": "*", "type": "lock", "reply_to": None, "body": {"name": name, "note": note, "ttl": ttl}})
        sleep(settle)
        lines = read(); holders = active(lines, now(), me, name)
        if not holders and mine(lines, now(), me, name) == lid:
            return lid, {}
        if not holders:                                # our lock is not visible yet: give it one more settle
            sleep(settle); lines = read(); holders = active(lines, now(), me, name)
            if not holders:
                return lid, {}
        log("contention on %s: %s locked inside the window; releasing our %s and backing off" % (name, holders, lid))
        release(read, post, lid, me, name, now)
        sleep(interval * (1 + rand()))
    return None, holders


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("n", nargs="?", type=int, help="attempts (legacy positional)")
    ap.add_argument("--attempts", type=int, default=40); ap.add_argument("--interval", type=float, default=10.0)
    ap.add_argument("--me", default="blender-team"); ap.add_argument("--name", default="compute"); ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--acquire", action="store_true"); ap.add_argument("--release", type=int, metavar="LOCK_ID")
    ap.add_argument("--ttl", type=float, default=900); ap.add_argument("--note", default=""); ap.add_argument("--settle", type=float, default=3.0)
    ap.add_argument("--tries", type=int, default=5); ap.add_argument("--bus", default=BUS)
    o = ap.parse_args(argv)
    read = lambda: tail(o.log); post = lambda m: bus_post(m, o.bus)
    if o.release is not None:
        uid, why = release(read, post, o.release, o.me, o.name)
        print("unlock %s" % uid if uid is not None else "skip: %s" % why, flush=True)
        return 0
    if o.acquire:
        lid, a = acquire(read, post, o.me, o.name, o.ttl, o.note, o.n if o.n is not None else o.attempts, o.interval, o.settle, o.tries)
        print("lock %s" % lid if lid is not None else "still held %s" % a, flush=True)
        return 0 if lid is not None else 3
    ok, a = wait_free(lambda: tail(o.log), o.n if o.n is not None else o.attempts, o.interval, o.me, o.name)
    print("free" if ok else "still held %s" % a, flush=True)
    return 0 if ok else 3


if __name__ == "__main__":
    sys.exit(main())
