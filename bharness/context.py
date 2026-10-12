# SPDX-License-Identifier: MIT
"""Shared context and the standard harness wiring. Projects add their own plugins with build(extra=[...])."""
import json, os, time
from .client import Bridge
from .contract import Registry, Gateway, Risk

DEFAULT_ART = os.path.join(os.path.expanduser("~"), "projects", "bot-team", "art")
LOG = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "Daedalus", "jobs", "bharness.jsonl")


class Context:
    def __init__(self, art=None, who="Blender Boss", bridge=None, log_path=LOG):
        self.art = art or os.environ.get("BHARNESS_ART", DEFAULT_ART)
        self.who, self.log_path = who, log_path
        self.bridge = bridge or Bridge(log=self.log)

    def log(self, d):
        try:
            os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(dict(d, at=time.strftime("%Y-%m-%dT%H:%M:%S")), default=str) + "\n")
        except OSError:
            pass


def build(ctx=None, ceiling=Risk.SCENE, extra=()):
    from .plugins import bridge, probe, judge, render, queue
    ctx = ctx or Context()
    reg = Registry()
    for cls in (bridge.BridgePlugin, probe.ProbePlugin, judge.JudgePlugin, render.RenderPlugin, queue.QueuePlugin) + tuple(extra):
        reg.add(cls(ctx))
    return ctx, Gateway(reg, ceiling=ceiling, log=ctx.log)
