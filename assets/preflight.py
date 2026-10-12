# SPDX-License-Identifier: MIT
"""Preflight: the art watcher imports from art\\<Prefix>\\<asset>.blend (not art\\glb). Every Blender-team READY row must have it.
python -m assets.preflight [--fix-block]  -> lists our READY rows missing the .blend; --fix-block sets them BLOCKED (missing source .blend)."""
import json, os, sys
ART = r"C:\Users\730ri\projects\bot-team\art"; Q = os.path.join(ART, "QUEUE.md")
def blend_path(asset, art=ART): return os.path.join(art, asset.split("_")[0], asset + ".blend")
def has_blend(asset, art=ART): return os.path.exists(blend_path(asset, art))
def main(a=sys.argv[1:]):
    t = open(Q, encoding="utf-8").read(); L = t.split("\n"); miss = []
    for i, l in enumerate(L):
        c = l.split("|")
        if len(c) > 6 and c[1].strip().isdigit() and c[5].strip() == "READY" and "Blender team" in c[6] and not has_blend(c[2].strip()):
            miss.append((c[1].strip(), c[2].strip()))
            if "--fix-block" in a: c[5] = " BLOCKED: missing source .blend (preflight) "; L[i] = "|".join(c)
    if "--fix-block" in a and miss and open(Q, encoding="utf-8").read() == t:
        open(Q, "w", encoding="utf-8").write("\n".join(L))
    print(json.dumps({"missing": len(miss), "rows": miss[:50]})); return 1 if miss else 0
if __name__ == "__main__": sys.exit(main())
