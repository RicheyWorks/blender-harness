"""bharness: a modular, reusable harness over the Claude Blender Bridge (127.0.0.1:9876).

Gateway -> Registry -> Plugins (bridge, probe, judge, render, queue). See README.md."""
from .client import Bridge, BridgeError
from .contract import Risk, Action, Plugin, Registry, Gateway, PolicyError
__version__ = "0.1.0"
