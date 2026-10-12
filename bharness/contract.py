# SPDX-License-Identifier: MIT
"""The harness contract (CSRBT / FlowersForever shape): Gateway -> Registry -> Plugins.

* A plugin declares its actions, and each action's risk. The caller never claims a risk.
* The gateway enforces a policy ceiling (default SCENE: may read and edit the open scene, may not write files).
* Accounting (ComputerPets rule): every catalogued action ends a run in exactly one bucket;
  discovered == driven + failed + refused + excluded. Anything else is UNACCOUNTED, a harness bug.
"""
import enum, time, json, traceback


class Risk(enum.IntEnum):
    READ = 0      # observe only
    SCENE = 1     # change the open Blender scene (undoable, nothing on disk)
    FILE = 2      # write files: .blend, renders, QUEUE.md
    DESTRUCTIVE = 3  # could lose work: revert, open over another file. Never allowed by default.


class Action:
    def __init__(self, name, fn, risk, doc="", args=()):
        self.name, self.fn, self.risk, self.doc, self.args = name, fn, Risk(risk), doc, tuple(args)

    def describe(self):
        return {"name": self.name, "risk": self.risk.name, "doc": self.doc, "args": list(self.args)}


class Plugin:
    """Subclass, set `name`, and return Actions from actions()."""
    name = "plugin"

    def __init__(self, ctx):
        self.ctx = ctx  # shared Context: bridge, config, log

    def actions(self):
        return []


class PolicyError(Exception):
    pass


class Registry:
    def __init__(self):
        self.plugins = {}

    def add(self, plugin):
        if plugin.name in self.plugins:
            raise ValueError("duplicate plugin " + plugin.name)
        self.plugins[plugin.name] = plugin
        return plugin

    def catalog(self):
        return {"%s.%s" % (p.name, a.name): a for p in self.plugins.values() for a in p.actions()}


class Gateway:
    def __init__(self, registry, ceiling=Risk.SCENE, log=None):
        self.registry, self.ceiling, self.log = registry, Risk(ceiling), log or (lambda d: None)
        self.ledger = {}  # action id -> bucket

    def discover(self):
        return [dict(id=k, **a.describe()) for k, a in sorted(self.registry.catalog().items())]

    def invoke(self, action_id, **kw):
        cat = self.registry.catalog()
        if action_id not in cat:
            raise KeyError("unknown action %s; have %s" % (action_id, ", ".join(sorted(cat))))
        a = cat[action_id]
        if a.risk > self.ceiling:
            self.ledger[action_id] = "refused"
            self.log({"t": time.time(), "action": action_id, "outcome": "refused", "risk": a.risk.name})
            raise PolicyError("%s needs %s; gateway ceiling is %s" % (action_id, a.risk.name, self.ceiling.name))
        t0 = time.time()
        try:
            out = a.fn(**kw)
        except Exception as e:
            self.ledger[action_id] = "failed"
            self.log({"t": t0, "action": action_id, "outcome": "failed", "error": repr(e)})
            raise
        self.ledger[action_id] = "driven"
        self.log({"t": t0, "action": action_id, "outcome": "driven", "ms": int((time.time() - t0) * 1000)})
        return out

    def exclude(self, action_id, why):
        self.ledger[action_id] = "excluded: " + why

    def accounting(self):
        cat = set(self.registry.catalog())
        buckets = {}
        for k in cat:
            b = self.ledger.get(k, "UNACCOUNTED").split(":")[0]
            buckets.setdefault(b, []).append(k)
        stray = sorted(set(self.ledger) - cat)
        return {"discovered": len(cat), "buckets": {b: sorted(v) for b, v in buckets.items()},
                "balanced": "UNACCOUNTED" not in buckets and not stray, "stray": stray}
