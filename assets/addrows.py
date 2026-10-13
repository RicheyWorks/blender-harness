# SPDX-License-Identifier: MIT
"""Append QUEUE.md rows for a spec module ourselves (Buffffff, 2026-10-12): exact table format, one clearly marked block,
re-read/compare before writing, only assets whose .glb exists and that have no row yet. Status READY (built + judged + saved).
Usage: python -m assets.addrows <module> <label>"""
import importlib, json, os, sys
from bharness.context import Context
from bharness.plugins.queue import QueuePlugin, parse, kind_of
from assets.preflight import has_blend

def main(a=sys.argv[1:]):
    mod = importlib.import_module(a[0]); label = a[1]
    ctx = Context(); q = QueuePlugin(ctx)
    for _ in range(5):
        before = q.read(); rows = parse(before)[0]; have = {r["asset"] for r in rows}
        nxt = max(int(r["cells"][0]) for r in rows if r["cells"][0].isdigit()) + 1 if rows else 1
        last = rows[-1]["line"]
        new = []; nob = []
        for grp in getattr(mod, "ORDER", list(mod.GROUPS)):
            for s in mod.GROUPS[grp]:
                n = s["asset"]
                if n in have or not os.path.exists(os.path.join(ctx.art, "glb", n + ".glb")): continue
                if not has_blend(n, ctx.art): nob.append(n); continue   # preflight: watcher source must exist
                k = KIND.get(n.split("_")[0], "prop"); size = getattr(mod, "SIZE", {}).get(grp, "")
                new.append([nxt, n, k, size]); nxt += 1
        if not new: print(json.dumps({"added": 0})); return 0
        # the block lives INSIDE the table (parse() ends the table at the first non-| line); each Notes cell carries the block marker
        new = ["| %d | %s | %s | %s | READY | [%s block %d/%d] added by the Blender team; glb in art\\glb |" % (r[0], r[1], r[2], r[3], label, i + 1, len(new))
               for i, r in enumerate(new)]
        lines = before.split("\n"); lines[last + 1:last + 1] = new; after = "\n".join(lines)
        if q.read() != before: continue
        tmp = q.path + ".bh.tmp"
        with open(tmp, "w", encoding="utf-8", newline="") as f: f.write(after)
        __import__('bharness.plugins.queue', fromlist=['replace_retry']).replace_retry(tmp, q.path)
        names = [l.split("|")[2].strip() for l in new]
        print(json.dumps({"added": len(new), "no_blend": nob[:20], "first": new[0], "last": new[-1], "names": names})); return 0
    print(json.dumps({"error": "QUEUE.md kept changing"})); return 1

KIND = {"Prop": "prop", "Item": "item", "Tool": "tool", "Veh": "vehicle", "Mob": "mob", "Bld": "building", "Wpn": "weapon"}

if __name__ == "__main__":
    sys.exit(main())
