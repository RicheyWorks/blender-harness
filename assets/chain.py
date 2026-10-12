# SPDX-License-Identifier: MIT
"""Run several build groups with --ship, then the shipping backlog, in one job (one asset at a time throughout).
  python -m assets.chain assets.worldspecs blocks gatherables armor town vehicles sky realm_rest --backlog"""
import json, sys
from assets import runner
def main(a=sys.argv[1:]):
    mod, groups = a[0], [g for g in a[1:] if not g.startswith("--")]
    for g in groups:
        print(json.dumps({"group": g}), flush=True)
        runner.main(["build", mod, "--group=" + g, "--ship"])
    if "--backlog" in a:
        from assets import ship
        from bharness.context import Context
        print(json.dumps({"backlog": ship.backlog(Context())}), flush=True)
    return 0
if __name__ == "__main__":
    sys.exit(main())
