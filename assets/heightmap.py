# SPDX-License-Identifier: MIT
"""Landscape feed: 16-bit grayscale heightmaps sized for Unreal Landscape (1009 = 63 quads x 16 sections + 1).
Pure Python + numpy + PIL: no Blender, no editor, light on RAM. One PNG + a .json with the Z scale per biome.
Usage: python -m assets.heightmap <out_folder> [size=1009]"""
import json, os, sys
import numpy as np
from PIL import Image

BIOMES = {  # (seed, relief metres, roughness, plateau terracing steps: blocky world = stepped heights)
    "TemperateForest": (1, 24, 0.55, 24), "Grassland": (2, 10, 0.45, 10), "Desert": (3, 18, 0.5, 12),
    "Tundra": (4, 14, 0.5, 14), "Swamp": (5, 4, 0.4, 4), "Jungle": (6, 30, 0.6, 30), "Mountain": (7, 120, 0.65, 60),
    "OceanFloor": (8, 20, 0.45, 20), "Starfall": (9, 40, 0.7, 20)}

def fbm(n, seed, rough, octaves=7):
    rng = np.random.default_rng(seed); out = np.zeros((n, n)); amp = 1.0; tot = 0
    for o in range(octaves):
        g = 2 ** (o + 2) + 1; grid = rng.random((g, g))
        x = np.linspace(0, g - 1, n); i = np.minimum(x.astype(int), g - 2); f = x - i; f = f * f * (3 - 2 * f)
        a = grid[i][:, i] * (1 - f)[None, :] + grid[i][:, i + 1] * f[None, :]
        c = grid[i + 1][:, i] * (1 - f)[None, :] + grid[i + 1][:, i + 1] * f[None, :]
        out += amp * (a * (1 - f)[:, None] + c * f[:, None]); tot += amp; amp *= rough
    return out / tot

def main(a=sys.argv[1:]):
    folder = a[0]; n = int(a[1]) if len(a) > 1 else 1009; os.makedirs(folder, exist_ok=True); meta = {}
    for name, (seed, relief, rough, steps) in BIOMES.items():
        h = fbm(n, seed, rough); h = (h - h.min()) / (np.ptp(h) or 1)
        h = np.round(h * steps) / steps   # terraced in 1 m blocks (relief/steps metres per step)
        png = os.path.join(folder, "Heightmap_%s.png" % name)
        Image.fromarray((h * 65535).astype(np.uint16)).save(png)
        # Unreal: Z scale % = relief_cm / 512 (a 16-bit landscape spans 512 units at scale 100)
        meta[name] = {"png": os.path.basename(png), "size": n, "relief_m": relief, "step_m": round(relief / steps, 2),
                      "unreal_z_scale": round(relief * 100 / 512 * 100 / 100, 3), "xy_scale_cm": 100}
    json.dump(meta, open(os.path.join(folder, "heightmaps.json"), "w"), indent=1); print(len(meta), "heightmaps ->", folder)

if __name__ == "__main__":
    main()
