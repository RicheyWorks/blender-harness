"""Gateway / registry / risk ladder / accounting identity."""
from harness.check import Checks
from bharness.contract import Risk, Action, Plugin, Registry, Gateway, PolicyError
from bharness.context import build, Context
from harness.fakes import FakeBridge

t = Checks()

class P(Plugin):
    name = "p"
    def actions(self):
        return [Action("look", lambda: 1, Risk.READ), Action("edit", lambda: 2, Risk.SCENE),
                Action("write", lambda: 3, Risk.FILE), Action("nuke", lambda: 4, Risk.DESTRUCTIVE),
                Action("bad", lambda: 1 / 0, Risk.READ)]

reg = Registry(); reg.add(P(None))
gw = Gateway(reg)
t("default ceiling is SCENE", gw.ceiling == Risk.SCENE)
t("READ action runs", gw.invoke("p.look") == 1)
t("SCENE action runs under SCENE", gw.invoke("p.edit") == 2)
t.raises("FILE action refused under SCENE", PolicyError, lambda: gw.invoke("p.write"))
t.raises("DESTRUCTIVE refused under SCENE", PolicyError, lambda: gw.invoke("p.nuke"))
t.raises("failing action raises", ZeroDivisionError, lambda: gw.invoke("p.bad"))
t.raises("unknown action is a KeyError naming the catalogue", KeyError, lambda: gw.invoke("p.nope"))
t.raises("duplicate plugin rejected", ValueError, lambda: reg.add(P(None)))
acc = gw.accounting()
t("accounting balances when every action has a bucket", acc["balanced"], acc)
t("buckets: driven 2, refused 2, failed 1",
  [len(acc["buckets"].get(k, [])) for k in ("driven", "refused", "failed")] == [2, 2, 1], acc["buckets"])
gw2 = Gateway(reg); gw2.invoke("p.look")
t("an undriven action is UNACCOUNTED", not gw2.accounting()["balanced"] and "UNACCOUNTED" in gw2.accounting()["buckets"])
gw2.ledger["p.ghost"] = "driven"
t("a stray ledger entry unbalances", gw2.accounting()["stray"] == ["p.ghost"])
gw3 = Gateway(reg, ceiling=Risk.FILE)
t("FILE ceiling allows FILE", gw3.invoke("p.write") == 3)
t.raises("FILE ceiling still refuses DESTRUCTIVE", PolicyError, lambda: gw3.invoke("p.nuke"))
logged = []
gw4 = Gateway(reg, log=logged.append); gw4.invoke("p.look")
t("every invoke is logged", logged and logged[0]["outcome"] == "driven")
ctx, g = build(Context(art="/tmp/x", bridge=FakeBridge(), log_path="/tmp/bh-test.jsonl"))
ids = [d["id"] for d in g.discover()]
for core in ("bridge.ping", "bridge.python", "probe.asset", "judge.asset", "render.shot", "render.turntable",
             "queue.claim", "queue.ready", "queue.retry", "queue.block"):
    t("standard wiring has " + core, core in ids)
risks = {d["id"]: d["risk"] for d in g.discover()}
t("every queue write is FILE risk", all(risks[k] == "FILE" for k in ids if k.startswith("queue.") and k not in ("queue.board", "queue.mine")))
t("bridge.python is SCENE risk", risks["bridge.python"] == "SCENE")
t.done()
