"""Walk robot: drive every catalogued action with arguments from POOLS; account for all of them.

  python -m harness.walk            stand-in (fake Blender), ceiling FILE, temp art folder
  python -m harness.walk --live     live Blender, READ actions only (changes nothing)
discovered == driven + refused + failed + excluded, or the run is UNACCOUNTED and fails."""
import os, shutil, sys, tempfile
from harness.check import Checks
from harness.fakes import QUEUE, FakeBridge, crate
from harness.ledger import record
from bharness.context import build, Context
from bharness.contract import Risk, PolicyError

live = "--live" in sys.argv
POOLS = {"name": "Prop_BHTest", "asset": "Prop_BHTest", "code": "result = 1+1", "reason": "walk", "n": 2}
EXCLUDE = {"bridge.object": "needs an object name that exists; probe.asset covers object reads",
           "queue.open": "replaces the open file; covered by test_queue and the live suite",
           "queue.retry": "needs a BLOCKED row; test_queue drives it",
           "queue.block": "needs a READY row; test_queue drives it",
           "export.glb": "needs a real glTF exporter; the live runner exports and self-checks every asset",
           "export.lod": "needs real Decimate modifiers; the live runner covers it"}
ARGS = {"bridge.python": ["code"], "probe.asset": ["name"], "judge.asset": ["name"], "render.turntable": ["name", "n"],
        "queue.claim": ["asset"], "queue.save": ["asset"], "queue.ready": ["asset"]}
CORE = ("bridge.ping", "bridge.scene", "bridge.filestate", "bridge.python", "probe.asset", "judge.asset",
        "render.shot", "render.turntable", "queue.board", "queue.claim", "queue.ready")

d = tempfile.mkdtemp(prefix="bhwalk-")
open(os.path.join(d, "QUEUE.md"), "w", newline="").write(QUEUE)
if live:
    ctx, gw = build(Context(art=d), ceiling=Risk.READ)
else:
    ctx, gw = build(Context(art=d, bridge=FakeBridge(assets={"Prop_BHTest": crate()}), log_path=os.path.join(d, "l")),
                    ceiling=Risk.FILE)
t = Checks()
cat = gw.discover()
ids = [a["id"] for a in cat]
for c in CORE:
    t("core action present: " + c, c in ids)
order = sorted(ids, key=lambda i: (i != "queue.claim", i))   # claim before ready
for a in order:
    if a in EXCLUDE:
        gw.exclude(a, EXCLUDE[a]); continue
    kw = {k: POOLS[k] for k in ARGS.get(a, [])}
    try:
        gw.invoke(a, **kw)
    except PolicyError:
        pass
    except Exception as e:
        print("     %s failed: %r" % (a, e))
acc = gw.accounting()
t("identity holds (no UNACCOUNTED)", acc["balanced"], acc)
t("no action failed", not acc["buckets"].get("failed"), acc["buckets"].get("failed"))
t("live walk changes nothing (only READ driven)" if live else "stand-in drives every non-excluded action",
  (not acc["buckets"].get("failed")) and (live or len(acc["buckets"].get("driven", [])) == len(ids) - len(EXCLUDE)))
if "--no-ledger" not in sys.argv:
    record("walk", "live" if live else "standin", {"discovered": acc["discovered"],
           "buckets": {k: len(v) for k, v in acc["buckets"].items()}, "rows": acc["buckets"], "excluded_why": EXCLUDE})
shutil.rmtree(d, ignore_errors=True)
t.done()
