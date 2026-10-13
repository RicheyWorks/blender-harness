# SPDX-License-Identifier: MIT
"""Re-render turntables for thin BBIsle families (fences/signs/banners/arches/scarecrows) after the render.py 45-deg fix.
Same seeds as bbisle.py, so meshes are identical; only the promo turntables change."""
from assets.bbisle import items
THIN = ("Fence", "Sign", "Banner", "Arch", "Scarecrow")
SPECS = [s for s in items(0, 500) if s["asset"].split("_")[2] in THIN]
GROUPS = {"bbisle_thin": SPECS}; ORDER = ["bbisle_thin"]; SIZE = {"bbisle_thin": "0.5-5 m"}
