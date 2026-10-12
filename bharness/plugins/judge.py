# SPDX-License-Identifier: MIT
"""The brief's rules (Daedalus2 docs/BLENDER-TEAM-BRIEF.md), checked before a row goes READY.

judge() is pure: probe data in, checks out, so it is unit-tested without Blender."""
import re
from ..contract import Plugin, Action, Risk
from .probe import asset

BUDGET = {"Prop": 3000, "Item": 3000, "Tool": 3000, "Wpn": 3000, "Mob": 6000, "Veh": 12000, "Bld": 15000, "Sky": 15000}
NAME = re.compile(r"^(Prop|Item|Tool|Wpn|Mob|Veh|Bld|Sky)_[A-Za-z0-9]+(_[A-Za-z0-9]+)*$")


def judge(name, p):
    c = []

    def add(k, ok, d=""):
        c.append({"check": k, "ok": bool(ok), "detail": d})

    add("name is Kind_Name, no spaces", NAME.match(name), name)
    add("one collection named like the asset", p.get("collection"))
    objs = p.get("objects", [])
    add("has meshes", len(objs) > 0, "%d" % len(objs))
    kind = name.split("_")[0]
    tris, cap = sum(o["tris"] for o in objs), BUDGET.get(kind, 3000)
    add("triangle budget", tris <= cap, "%d / %d" % (tris, cap))
    bad = [o["name"] for o in objs if any(abs(s - 1) > 1e-4 for s in o["scale"])]
    add("scale applied", not bad, ", ".join(bad))
    bad = [o["name"] for o in objs if not 1 <= o["slots"] <= 3 or o.get("empty_slots")]
    add("1-3 filled material slots", not bad, ", ".join(bad))
    bad = [o["name"] for o in objs if o["images"]]
    add("flat colours, no image textures", not bad, ", ".join(bad))
    bad = [o["name"] for o in objs if " " in o["name"]]
    add("object names have no spaces", not bad, ", ".join(bad))
    if objs:
        lo = [min(o["min"][i] for o in objs) for i in range(3)]
        hi = [max(o["max"][i] for o in objs) for i in range(3)]
        add("stands on z=0 (bottom-centre origin)", abs(lo[2]) < 0.01, "min z %.3f" % lo[2])
        add("centred on x/y", abs(lo[0] + hi[0]) / 2 < 0.05 and abs(lo[1] + hi[1]) / 2 < 0.05,
            "centre %.3f, %.3f" % ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2))
        add("size (info)", True, "%.2f x %.2f x %.2f m" % tuple(hi[i] - lo[i] for i in range(3)))
    return c


def passed(checks):
    return all(c["ok"] for c in checks)


def first_failure(checks):
    return next((c["check"] for c in checks if not c["ok"]), None)


class JudgePlugin(Plugin):
    name = "judge"

    def actions(self):
        return [Action("asset", lambda name: judge(name, asset(self.ctx.bridge, name)), Risk.READ,
                       "check the open scene's asset against the brief", ["name"])]
