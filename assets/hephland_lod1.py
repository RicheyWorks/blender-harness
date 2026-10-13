# SPDX-License-Identifier: MIT
"""LOD1 for the hephaestus landmarks (hephland.py): largest boxes kept (<= 60%), tiny parts dropped. Output <Asset>_LOD1."""
from assets.hephland import SPECS as H
from assets.bbisle_lod1 import lod1
SPECS = [dict(s, asset=s["asset"] + "_LOD1", parts=[dict(p, boxes=lod1(p["boxes"])) for p in s["parts"]]) for s in H]
GROUPS = {"hephland_lod1": SPECS}; ORDER = ["hephland_lod1"]; SIZE = {"hephland_lod1": "1.5-20 m"}
