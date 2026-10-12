"""QUEUE.md rules, transitions, BLOCKED vs REJECTED, watcher coordination, never-discard guard (no Blender)."""
import os, shutil, sys, tempfile, json
from harness.check import Checks
from harness.fakes import QUEUE, FakeBridge, crate
from bharness.context import Context
from bharness.plugins.queue import QueuePlugin, QueueError, Blocked, parse, set_row, state

t = Checks()
here = os.path.dirname(os.path.abspath(__file__))
ref = os.path.join(here, "..", "..", "Daedalus2", "connectors", "claude-asset-pipeline")


def fresh(**fb):
    d = tempfile.mkdtemp(prefix="bhq-")
    open(os.path.join(d, "QUEUE.md"), "w", newline="").write(QUEUE)
    br = FakeBridge(assets={"Prop_BHTest": crate()}, **fb)
    return d, br, QueuePlugin(Context(art=d, bridge=br, log_path=os.path.join(d, "log.jsonl")))


def other_lines_same(before, after, asset):
    rb, _ = parse(before)
    line = next(r["line"] for r in rb if r["asset"] == asset)
    a, b = before.split("\n"), after.split("\n")
    return len(a) == len(b) and all(x == y for i, (x, y) in enumerate(zip(a, b)) if i != line)


d, br, q = fresh()
t("parses 5 rows", len(q.rows()) == 5)
t("BLOCKED is its own state", state("BLOCKED: Unreal in Play") == "BLOCKED" and state("REJECTED: x") == "REJECTED")
before = q.read()
q.claim("Prop_BHTest")
after = q.read()
t("claim: TODO -> DOING (Blender Boss)", q.row("Prop_BHTest")["status"] == "DOING (Blender Boss)")
t("claim changes only that row, byte for byte", other_lines_same(before, after, "Prop_BHTest"))
cells_b = parse(before)[0][0]["cells"]; cells_a = parse(after)[0][0]["cells"]
t("claim changes only Status (Notes kept)", [c for i, c in enumerate(cells_a) if i != 4] == [c for i, c in enumerate(cells_b) if i != 4])
t.raises("claim refuses someone else's DOING", QueueError, lambda: q.claim("Prop_Other"))
t.raises("claim refuses READY", QueueError, lambda: q.claim("Prop_Shipping"))
t.raises("claim refuses BLOCKED (not a Blender fault)", QueueError, lambda: q.claim("Prop_Blk"))
q.claim("Prop_Rej")
t("claim takes a REJECTED row to fix it", q.row("Prop_Rej")["status"] == "DOING (Blender Boss)")
t("mine lists our rows", sorted(q.mine()) == ["Prop_BHTest", "Prop_Rej"])
t.raises("ready refuses a row that isn't ours", QueueError, lambda: q.ready("Prop_Other"))
r = q.ready("Prop_Rej")
t("ready refuses when the judge fails, row unchanged", not r["ready"] and q.row("Prop_Rej")["status"] == "DOING (Blender Boss)", r.get("failed"))
r = q.ready("Prop_BHTest", turntable=4)
t("ready: judged, saved, READY", r["ready"] and q.row("Prop_BHTest")["status"] == "READY", r)
t(".blend saved at art\\Prop\\Prop_BHTest.blend", os.path.exists(os.path.join(d, "Prop", "Prop_BHTest.blend")))
t("turntable wrote 4 frames to promo\\Prop_BHTest", len(os.listdir(os.path.join(d, "promo", "Prop_BHTest"))) == 4)
t("READY notes carry tris and size", "24 tris" in q.row("Prop_BHTest")["notes"], q.row("Prop_BHTest")["notes"])
try:
    q.open("Prop_BHTest"); t("open the asset's saved .blend (EXEC, no modal)", True)
except Exception as e:
    t("open the asset's saved .blend (EXEC, no modal)", False, repr(e))
codes = [p["code"] for k, p in br.calls if k == "execute_code"]
t("no operator is ever invoked with INVOKE_DEFAULT (no modals)", not any("INVOKE_DEFAULT" in c for c in codes))
t("every file operator runs EXEC_DEFAULT", all("EXEC_DEFAULT" in c for c in codes if "mainfile" in c or "homefile" in c))
feed = [json.loads(l) for l in open(os.path.join(d, "feed.jsonl"))]
t("feed has a line per transition", [e["event"] for e in feed] == ["doing", "doing", "ready"], [e["event"] for e in feed])
q.block("Prop_BHTest", "Unreal in Play")
t("block: READY -> BLOCKED: reason", q.row("Prop_BHTest")["status"] == "BLOCKED: Unreal in Play")
t.raises("block refuses another bot's DOING", QueueError, lambda: q.block("Prop_Other", "x"))
q.retry("Prop_Blk")
t("retry: BLOCKED -> READY", q.row("Prop_Blk")["status"] == "READY")
t.raises("retry refuses a REJECTED row", QueueError, lambda: q.retry("Prop_Rej"))
t("board groups BLOCKED apart from REJECTED", "BLOCKED" in q.board() and "REJECTED" not in q.board().get("BLOCKED", []))

# watcher coordination
d, br, q = fresh()
q.claim("Prop_BHTest")
txt = set_row(q.read(), "Prop_Shipping", "SHIPPING"); open(q.path, "w", newline="").write(txt)
t.raises("no Blender work while the watcher is SHIPPING", Blocked, lambda: q.ready("Prop_BHTest"))
t("row stays DOING while blocked", q.row("Prop_BHTest")["status"] == "DOING (Blender Boss)")

# never discard unsaved work
d, br, q = fresh(file=r"C:\other\Elsewhere.blend", dirty=True)
q.claim("Prop_BHTest")
t.raises("open refuses over unsaved work in another file", Blocked, lambda: q.open("Prop_BHTest"))
t.raises("ready refuses over unsaved work in another file", Blocked, lambda: q.ready("Prop_BHTest"))
t("no file operator ran while dirty", not any("mainfile" in p.get("code", "") or "homefile" in p.get("code", "") for k, p in br.calls))
d, br, q = fresh(file="", dirty=True)
t.raises("open refuses over an unsaved untitled file", Blocked, lambda: q.open("Prop_BHTest"))

# concurrent edit: someone writes between our read and our write
d, br, q = fresh()
real = q.read; n = {"i": 0}
def racing():
    n["i"] += 1
    if n["i"] == 2:   # our re-read: another bot changed a different row meanwhile
        txt = set_row(real(), "Prop_Other", "READY"); open(q.path, "w", newline="").write(txt)
    return real()
q.read = racing
q.claim("Prop_BHTest")
q.read = real
t("a concurrent edit to another row survives our write", q.row("Prop_Other")["status"] == "READY" and q.row("Prop_BHTest")["status"].startswith("DOING"))

# same parser as the watcher
if os.path.isdir(ref):
    sys.path.insert(0, ref)
    from asset_pipeline import artqueue as aq
    t("parse == watcher's parse", aq.parse(QUEUE) == parse(QUEUE))
    t("set_row == watcher's set_row", aq.set_row(QUEUE, "Prop_BHTest", "READY", "n") == set_row(QUEUE, "Prop_BHTest", "READY", "n"))
else:
    t("parse matches the watcher's documented format (watcher source not on this machine)", parse(QUEUE)[1]["status"] == 4)
t.done()
