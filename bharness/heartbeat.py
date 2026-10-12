# SPDX-License-Identifier: MIT
"""Hidden heartbeat on the team link (swarm rules, 2026-10-12): every 5 min a short note with queue counts.
Usage: python -m bharness.heartbeat [--minutes=240] [--every=300]"""
import json, sys, time
from collections import Counter
from bharness.context import Context
from bharness.bus import Bus
from bharness.plugins.queue import QueuePlugin, state

def main(a=sys.argv[1:]):
    opt = dict(x[2:].split("=") for x in a if x.startswith("--") and "=" in x)
    mins, every = float(opt.get("minutes", 240)), float(opt.get("every", 300))
    ctx = Context(); bus = Bus(ctx.art); q = QueuePlugin(ctx); end = time.time() + mins * 60
    while time.time() < end:
        c = Counter(state(r["status"]) for r in q.rows())
        txt = "HEARTBEAT blender-team: DOING wave builds headless (no editor). Queue %s. Self-ship: off until our editor turn." % \
              " ".join("%s %d" % (k, v) for k, v in sorted(c.items()))
        try: bus.send("note", {"asset": "-", "tag": "HEARTBEAT", "text": txt})
        except Exception as e: print(json.dumps({"error": repr(e)[:200]}), flush=True)
        time.sleep(every)
    return 0

if __name__ == "__main__":
    sys.exit(main())
