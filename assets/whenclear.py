# SPDX-License-Identifier: MIT
"""Wait (up to --max minutes) until no QUEUE.md row is SHIPPING, then run assets.chain with the rest of the args.
Usage: python -m assets.whenclear [--max=60] <module> <group>..."""
import json, sys, time
from bharness.context import Context
from bharness.plugins.queue import QueuePlugin, state

def main(a=sys.argv[1:]):
    mx = next((float(x.split("=")[1]) for x in a if x.startswith("--max=")), 60.0); a = [x for x in a if not x.startswith("--max=")]
    q = QueuePlugin(Context()); t0 = time.time()
    while True:
        busy = [r["asset"] for r in q.rows() if state(r["status"]) == "SHIPPING"]
        if not busy: break
        if time.time() - t0 > mx * 60: print(json.dumps({"gave_up": busy}), flush=True); return 1
        time.sleep(30)
    print(json.dumps({"clear_after_s": round(time.time() - t0)}), flush=True)
    from assets import chain
    return chain.main(a)

if __name__ == "__main__":
    sys.exit(main())
