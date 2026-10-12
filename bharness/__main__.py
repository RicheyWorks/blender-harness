# SPDX-License-Identifier: MIT
"""CLI over the gateway.

  python -m bharness list                         every action, with its risk
  python -m bharness call <plugin.action> [k=v ...] [--allow READ|SCENE|FILE]
  python -m bharness judge <Asset>                brief checks on the open scene (exit 1 on a failure)
Values are JSON when they parse (n=8, turntable=4), strings otherwise. Default ceiling: SCENE."""
import json, sys
from .context import build
from .contract import Risk


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    ceiling = Risk.SCENE
    if "--allow" in a:
        i = a.index("--allow"); ceiling = Risk[a[i + 1].upper()]; del a[i:i + 2]
    ctx, gw = build(ceiling=ceiling)
    cmd = a[0] if a else "list"
    if cmd == "list":
        for d in gw.discover():
            print("%-18s %-6s %s" % (d["id"], d["risk"], d["doc"]))
        return 0
    if cmd == "judge":
        cs = gw.invoke("judge.asset", name=a[1])
        for c in cs:
            print("%s %s  %s" % ("PASS" if c["ok"] else "FAIL", c["check"], c["detail"]))
        n = sum(c["ok"] for c in cs); print("%d/%d" % (n, len(cs)))
        return 0 if n == len(cs) else 1
    if cmd == "call":
        kw = {}
        for kv in a[2:]:
            k, v = kv.split("=", 1)
            try: kw[k] = json.loads(v)
            except ValueError: kw[k] = v
        print(json.dumps(gw.invoke(a[1], **kw), indent=1, default=str)[:20000])
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main())
