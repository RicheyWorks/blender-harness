# SPDX-License-Identifier: MIT
"""Ecosystem specs, generated from the catalog: every Flora / Fauna / Other-Worlds plant and animal gets a body plan.

GROUPS (build order): livestock+predators, crops, trees, then the rest of the fauna, then the rest of the flora.
Plans are parametric so one function covers a family (quadrupeds, birds, insects, fish, trees by stage...).
Colours: per-species where it matters, otherwise biome-flavoured defaults. Front = -Y."""
import hashlib
from assets.catalog import ASSETS, BIOMES

def b(s, c, m): return [list(s), list(c), m]
A, B2, C = 0, 1, 2   # material slots: main, secondary, accent/eyes

# ------------------------------------------------------------------ colours
SPECIES = {  # main, secondary, accent
 "Cow": ("F2F3F3", "202024", "F29BC0"), "Sheep": ("F4F6FB", "34343A", "E8C090"), "Pig": ("F29BC0", "E07FA6", "202024"),
 "Chicken": ("F4F6FB", "D82800", "F2C230"), "Goat": ("E4DDCF", "7A5230", "202024"), "Horse": ("7A5230", "34343A", "F4F6FB"),
 "Fox": ("F87818", "F4F6FB", "202024"), "Wolf": ("9C9C9C", "E4DDCF", "202024"), "Hawk": ("7A5230", "E4DDCF", "F2C230"),
 "Scorpion": ("C87800", "7A5230", "202024"), "SandSnake": ("E2D08C", "C87800", "202024"), "PolarBear": ("F4F6FB", "E4DDCF", "202024"),
 "SnowFox": ("F4F6FB", "C9D4E0", "202024"), "Crocodile": ("4B6B2F", "9C9C5C", "F2C230"), "Heron": ("C9D4E0", "F4F6FB", "F2C230"),
 "Shark": ("7C8C9C", "F4F6FB", "202024"), "Octopus": ("D85A5A", "F29BC0", "202024"), "Jaguar": ("F2C230", "34343A", "202024"),
 "Python": ("6B8C2F", "C8B040", "202024"), "Bat": ("3C3C3C", "8C34C8", "D82800"), "CaveSpider": ("34343A", "8C34C8", "D82800"),
 "Eagle": ("5A3A22", "F4F6FB", "F2C230"), "VoidStalker": ("2A1840", "A070FF", "7FE3FF"),
 "Rabbit": ("C8A070", "F4F6FB", "202024"), "Deer": ("A0683A", "F4F6FB", "202024"), "Squirrel": ("C8703A", "F4F6FB", "202024"),
 "Mouse": ("9C9C9C", "F29BC0", "202024"), "Pheasant": ("A0581C", "2C8C18", "D82800"), "Lizard": ("8CC040", "E2D08C", "202024"),
 "Jerboa": ("E2D08C", "F4F6FB", "202024"), "Hare": ("E4DDCF", "F4F6FB", "202024"), "Caribou": ("7A5230", "E4DDCF", "F4F6FB"),
 "Frog": ("59D940", "F2C230", "202024"), "Newt": ("F87818", "34343A", "202024"), "Crab": ("D82800", "F87818", "202024"),
 "Shrimp": ("F87850", "F4B0A0", "202024"), "Monkey": ("7A5230", "E8C090", "202024"), "Tapir": ("34343A", "F4F6FB", "202024"),
 "MountainGoat": ("F4F6FB", "C9D4E0", "202024"), "Marmot": ("A0683A", "E4DDCF", "202024"), "Glimmerling": ("D7B8FF", "7FE3FF", "202024"),
 "Robin": ("7A5230", "F87818", "202024"), "Owl": ("A0683A", "E4DDCF", "F2C230"), "Sparrow": ("A0683A", "E4DDCF", "202024"),
 "Vulture": ("34343A", "F29BC0", "F4F6FB"), "SnowyOwl": ("F4F6FB", "C9D4E0", "F2C230"), "Duck": ("2C8C18", "A0683A", "F2C230"),
 "Gull": ("F4F6FB", "9C9C9C", "F2C230"), "Parrot": ("D82800", "0058F8", "F2C230"), "Toucan": ("202024", "F4F6FB", "F87818"),
 "Starling_Comet": ("2A1840", "7FE3FF", "F2C230"), "Bee": ("F2C230", "202024", "F4F6FB"), "Butterfly": ("F87818", "202024", "F4F6FB"),
 "Ladybird": ("D82800", "202024", "F4F6FB"), "Grasshopper": ("8CC040", "4B974B", "202024"), "Beetle": ("2C4C8C", "34343A", "7FE3FF"),
 "Dragonfly": ("1FB5B0", "A8D8E8", "202024"), "Firefly": ("34343A", "FFE25A", "202024"), "Ant": ("7A2818", "34343A", "202024"),
 "MorphoButterfly": ("0D69AC", "202024", "7FE3FF"), "Glowworm": ("E2D08C", "7FE3FF", "202024"), "Lumamoth": ("D7B8FF", "7FE3FF", "202024"),
 "Trout": ("9C9C5C", "F29BC0", "202024"), "Carp": ("F2C230", "F87818", "202024"), "Char": ("7C8C9C", "F87818", "202024"),
 "Catfish": ("6B5A3A", "E4DDCF", "202024"), "Clownfish": ("F87818", "F4F6FB", "202024"), "Tuna": ("2C4C8C", "C9D4E0", "202024"),
 "Pufferfish": ("E2D08C", "F4F6FB", "202024"), "Piranha": ("9C9C9C", "D82800", "202024"), "Blindfish": ("F4E0E0", "F29BC0", "C9D4E0"),
 "Nebulafish": ("5C389E", "7FE3FF", "F4F6FB"), "Fish_Carp": ("F2C230", "F87818", "202024"), "Bird_Sparrow": ("A0683A", "E4DDCF", "202024"),
}
TREES = {"Oak": ("7A5232", "4AA44F", "round"), "Birch": ("F2F3F3", "8CC040", "round"), "Maple": ("7A5232", "F87818", "round"),
         "Willow": ("6B5A3A", "8CC040", "droop"), "Palm": ("A0683A", "4B974B", "palm"), "Joshua": ("8C7A5A", "6B8C2F", "spiky"),
         "Spruce": ("5A3A22", "2C6B3A", "conifer"), "Pine": ("6B4A2A", "3A7A3A", "conifer"), "Cypress": ("6B5A3A", "4B6B2F", "conifer"),
         "Mangrove": ("6B5A3A", "4B974B", "round"), "Kelp": ("6B8C2F", "4B974B", "kelp"), "Kapok": ("8C7A5A", "2C8C18", "round"),
         "Banana": ("8CC040", "59D940", "palm"), "Bamboo": ("8CC040", "59D940", "bamboo"), "Larch": ("6B4A2A", "C8B040", "conifer"),
         "StarWillow": ("3A2A5C", "6A4CC8", "droop")}
FLOWER = {"Bluebell": "4AA8FF", "Foxglove": "C060C0", "Sunflower": "F5CD30", "Poppy": "D82800", "DesertRose": "F29BC0",
          "Edelweiss": "F4F6FB", "Lotus": "F29BC0", "WaterLily": "F4F6FB", "SeaAnemone": "F87850", "Orchid": "C080F0",
          "Hibiscus": "FF4D4D", "Gentian": "0058F8", "NovaBloom": "7FE3FF"}
CROP = {"Wheat": ("C8B040", "E2D08C"), "Carrot": ("4B974B", "F87818"), "Potato": ("4B974B", "C8A070"), "Pumpkin": ("4B974B", "F87818"),
        "Melon": ("4B974B", "59A040"), "Tomato": ("4B974B", "D82800"), "Corn": ("6B8C2F", "F5CD30"), "Rice": ("8CC040", "E4DDCF"),
        "Cotton": ("4B974B", "F4F6FB"), "Starbean": ("5C389E", "7FE3FF")}

def h(n, k):  # stable 0..1 per name
    return int(hashlib.md5((n + str(k)).encode()).hexdigest()[:6], 16) / 0xFFFFFF

# ------------------------------------------------------------------ fauna plans
def quad(L=1.0, H=1.0, head=0.32, legs=0.40, tail=True, horns=False, ears="up", wool=False, low=False, neck=False):
    """A blocky four-legged animal. L = body length, H = shoulder height scale."""
    lh = legs * H * (0.45 if low else 1)
    bw, bh = 0.36 * L * (1.25 if wool else 1), 0.34 * L * (1.2 if wool else 1)
    bz = lh + bh / 2
    parts = [{"name": "_Body", "pivot": [0, 0, bz], "boxes": [b((bw, L, bh), (0, 0, bz), A), b((bw * 0.9, L * 0.4, bh * 0.4), (0, -L * 0.1, bz - bh * 0.45), B2)]}]
    hy, hz = -L / 2 - head * 0.35, bz + bh * (0.55 if neck else 0.25)
    hb = [b((head, head, head), (0, hy, hz), A), b((head * 0.6, head * 0.45, head * 0.5), (0, hy - head * 0.6, hz - head * 0.15), B2),
          b((head * 0.18, 0.03, head * 0.18), (-head * 0.25, hy - head * 0.5, hz + head * 0.15), C),
          b((head * 0.18, 0.03, head * 0.18), (head * 0.25, hy - head * 0.5, hz + head * 0.15), C)]
    if ears == "up":
        hb += [b((head * 0.2, head * 0.15, head * 0.4), (s * head * 0.3, hy, hz + head * 0.65), A) for s in (-1, 1)]
    elif ears == "long":
        hb += [b((head * 0.18, head * 0.12, head * 0.9), (s * head * 0.22, hy + 0.02, hz + head * 0.9), A) for s in (-1, 1)]
    elif ears == "side":
        hb += [b((head * 0.35, head * 0.15, head * 0.15), (s * head * 0.62, hy, hz + head * 0.2), A) for s in (-1, 1)]
    if horns:
        hb += [b((0.04, 0.04, head * 0.5), (s * head * 0.3, hy + 0.02, hz + head * 0.7), C if horns == "c" else B2) for s in (-1, 1)]
    if wool:   # fleece tufts on the back, sides and crown
        parts[0]["boxes"] += [b((bw * 0.45, L * 0.3, bh * 0.25), (sx * bw * 0.22, y * L, bz + bh * 0.55), A) for sx in (-1, 1) for y in (-0.3, 0.05, 0.32)]
        parts[0]["boxes"] += [b((bw * 0.2, L * 0.35, bh * 0.4), (sx * bw * 0.55, y * L, bz), A) for sx in (-1, 1) for y in (-0.18, 0.2)]
        hb.append(b((head * 0.9, head * 0.6, head * 0.35), (0, hy + head * 0.12, hz + head * 0.6), A))
    if neck:
        parts[0]["boxes"].append(b((head * 0.7, head * 0.7, bh), (0, -L / 2 + 0.02, bz + bh * 0.4), A))
    parts.append({"name": "_Head", "pivot": [0, -L / 2, hz], "boxes": hb})
    if tail:
        parts.append({"name": "_Tail", "pivot": [0, L / 2, bz + bh * 0.2], "boxes": [b((0.08, L * 0.25, 0.08), (0, L / 2 + L * 0.12, bz + bh * 0.25), B2)]})
    for n, x, y in (("_LegFL", -1, -1), ("_LegFR", 1, -1), ("_LegBL", -1, 1), ("_LegBR", 1, 1)):
        lx, ly = x * bw * 0.32, y * L * 0.36
        parts.append({"name": n, "pivot": [lx, ly, lh], "boxes": [b((0.11 * L ** 0.5, 0.11 * L ** 0.5, lh), (lx, ly, lh / 2), A),
                      b((0.12 * L ** 0.5, 0.14 * L ** 0.5, 0.05), (lx, ly - 0.01, 0.025), B2)]})
    return parts

def bird(S=0.3, flight=True, long_legs=False, beak=0.08):
    lh = (0.30 if long_legs else 0.08) * S / 0.3
    bz = lh + S * 0.4
    parts = [{"name": "_Body", "pivot": [0, 0, bz], "boxes": [b((S * 0.8, S * 1.2, S * 0.8), (0, 0, bz), A), b((S * 0.6, S * 0.5, S * 0.5), (0, -S * 0.3, bz - S * 0.2), B2),
              b((S * 0.4, S * 0.5, S * 0.12), (0, S * 0.75, bz + S * 0.1), A)] + [b((0.03, 0.03, lh), (s * S * 0.18, 0, lh / 2), C) for s in (-1, 1)]},
             {"name": "_Head", "pivot": [0, -S * 0.5, bz + S * 0.4], "boxes": [b((S * 0.55, S * 0.55, S * 0.55), (0, -S * 0.55, bz + S * 0.55), A),
              b((S * 0.2, beak * 1.5, S * 0.14), (0, -S * 0.9 - beak * 0.5, bz + S * 0.5), C),
              b((S * 0.1, 0.02, S * 0.1), (-S * 0.17, -S * 0.83, bz + S * 0.65), B2), b((S * 0.1, 0.02, S * 0.1), (S * 0.17, -S * 0.83, bz + S * 0.65), B2)]}]
    parts[0]["boxes"] += [b((S * 0.7, S * 0.35, S * 0.08), (0, S * 1.05, bz + S * 0.18), B2), b((S * 0.5, S * 0.06, S * 0.45), (0, -S * 0.61, bz - S * 0.05), C if long_legs else B2)]
    parts[1]["boxes"].append(b((S * 0.14, S * 0.3, S * 0.2), (0, -S * 0.45, bz + S * 0.9), B2))
    for n, s in (("_WingL", -1), ("_WingR", 1)):
        parts.append({"name": n, "pivot": [s * S * 0.4, 0, bz + S * 0.2], "boxes": [b((S * 0.12, S * 0.5, S * 0.08), (s * S * (1.05 if flight else 0.48), S * 0.15, bz + S * 0.22), A), b((S * (0.7 if flight else 0.15), S * 0.9, S * 0.1), (s * S * (0.75 if flight else 0.45), 0.02, bz + S * 0.25), B2)]})
    return parts

def insect(S=0.12, wings=True, legs6=True):
    parts = [{"name": "_Body", "pivot": [0, 0, S * 0.6], "boxes": [b((S * 0.6, S * 0.6, S * 0.5), (0, -S * 0.5, S * 0.6), B2), b((S * 0.8, S * 1.1, S * 0.6), (0, S * 0.35, S * 0.6), A),
             b((S * 0.4, S * 0.4, S * 0.4), (0, -S * 0.95, S * 0.65), B2), b((0.012, 0.012, S * 0.5), (-S * 0.12, -S * 1.1, S * 1.0), B2),
             b((0.012, 0.012, S * 0.5), (S * 0.12, -S * 1.1, S * 1.0), B2)] +
             ([b((S * 1.4, 0.015, 0.015), (0, y, S * 0.25), B2) for y in (-S * 0.4, 0, S * 0.4)] if legs6 else [])}]
    if wings:
        for n, s in (("_WingL", -1), ("_WingR", 1)):
            parts.append({"name": n, "pivot": [s * S * 0.3, 0, S * 0.9], "boxes": [b((S * 1.4, S * 1.0, 0.012), (s * S * 1.0, 0, S * 0.95), A),
                          b((S * 0.6, S * 0.4, 0.014), (s * S * 1.1, S * 0.1, S * 0.96), C)]})
    return parts

def fish(L=0.4, tall=0.5, puff=False):
    H = L * tall * (1.6 if puff else 1)
    return [{"name": "_Body", "pivot": [0, 0, H / 2], "boxes": [b((L * 0.3 * (2 if puff else 1), L, H), (0, 0, H / 2), A), b((L * 0.28, L * 0.5, H * 0.35), (0, -L * 0.05, H * 0.2), B2),
             b((0.02, L * 0.3, H * 0.35), (0, 0, H + H * 0.15), B2), b((L * 0.06, 0.02, L * 0.06), (-L * 0.15 * (2 if puff else 1), -L * 0.35, H * 0.65), C),
             b((L * 0.06, 0.02, L * 0.06), (L * 0.15 * (2 if puff else 1), -L * 0.35, H * 0.65), C)]},
            {"name": "_Tail", "pivot": [0, L / 2, H / 2], "boxes": [b((0.03, L * 0.25, H * 0.9), (0, L / 2 + L * 0.12, H / 2), B2)]}]

def snake(L=1.6):
    segs = [b((0.14, L / 8, 0.12), (0.10 * ((-1) ** i), -L / 2 + i * L / 8 + L / 16, 0.06), A if i % 2 else B2) for i in range(8)]
    return [{"name": "_Body", "pivot": [0, 0, 0.06], "boxes": segs},
            {"name": "_Head", "pivot": [0.1, -L / 2, 0.06], "boxes": [b((0.18, 0.16, 0.12), (0.10, -L / 2 - 0.08, 0.08), A),
             b((0.04, 0.02, 0.04), (0.05, -L / 2 - 0.165, 0.11), C), b((0.04, 0.02, 0.04), (0.15, -L / 2 - 0.165, 0.11), C)]}]

def arthro(S=0.3, tail=False):
    legs = [b((S * 1.6, 0.03, 0.03), (0, y, S * 0.15), B2) for y in (-S * 0.25, 0, S * 0.25)]
    parts = [{"name": "_Body", "pivot": [0, 0, S * 0.3], "boxes": [b((S, S * 0.9, S * 0.35), (0, 0, S * 0.3), A)] + legs +
              [b((0.05, 0.02, 0.05), (s * S * 0.15, -S * 0.46, S * 0.45), C) for s in (-1, 1)]}]
    for n, s in (("_ClawL", -1), ("_ClawR", 1)):
        parts.append({"name": n, "pivot": [s * S * 0.4, -S * 0.4, S * 0.3], "boxes": [b((S * 0.15, S * 0.4, S * 0.12), (s * S * 0.45, -S * 0.65, S * 0.3), A),
                      b((S * 0.25, S * 0.2, S * 0.18), (s * S * 0.5, -S * 0.9, S * 0.3), A)]})
    if tail:
        parts.append({"name": "_Tail", "pivot": [0, S * 0.45, S * 0.3], "boxes": [b((S * 0.15, S * 0.4, S * 0.15), (0, S * 0.65, S * 0.4), A),
                      b((S * 0.15, S * 0.15, S * 0.4), (0, S * 0.85, S * 0.7), A), b((S * 0.1, S * 0.2, S * 0.1), (0, S * 0.75, S * 0.95), C)]})
    return parts

def octo(S=0.6):
    tents = [b((0.08, 0.08, S * 0.5), (S * 0.3 * dx, S * 0.3 * dy, S * 0.25), B2) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7))]
    return [{"name": "_Body", "pivot": [0, 0, S * 0.5], "boxes": [b((S * 0.6, S * 0.6, S * 0.6), (0, 0, S * 0.8), A), b((S * 0.4, S * 0.4, S * 0.2), (0, 0, S * 1.2), A),
             b((S * 0.1, 0.02, S * 0.1), (-S * 0.13, -S * 0.31, S * 0.7), C), b((S * 0.1, 0.02, S * 0.1), (S * 0.13, -S * 0.31, S * 0.7), C)]},
            {"name": "_Tentacles", "pivot": [0, 0, S * 0.5], "boxes": tents}]

PLAN = {  # name -> callable producing parts
 "Cow": lambda: quad(1.5, 1.2, 0.42, 0.55, horns="c", ears="side"), "Sheep": lambda: quad(1.1, 1.0, 0.30, 0.40, wool=True, ears="side"),
 "Pig": lambda: quad(1.1, 0.8, 0.36, 0.30, ears="side"), "Goat": lambda: quad(1.0, 1.1, 0.30, 0.50, horns=True),
 "Horse": lambda: quad(1.7, 1.6, 0.38, 0.85, neck=True), "Chicken": lambda: bird(0.32, False),
 "Fox": lambda: quad(0.9, 0.9, 0.28, 0.32), "Wolf": lambda: quad(1.1, 1.0, 0.30, 0.42), "Hawk": lambda: bird(0.35), "Eagle": lambda: bird(0.45),
 "Scorpion": lambda: arthro(0.35, tail=True), "SandSnake": lambda: snake(1.4), "Python": lambda: snake(2.4),
 "PolarBear": lambda: quad(1.8, 1.3, 0.46, 0.55, ears="side"), "SnowFox": lambda: quad(0.8, 0.8, 0.26, 0.28),
 "Crocodile": lambda: quad(2.2, 0.8, 0.40, 0.25, low=True, ears=None), "Heron": lambda: bird(0.40, long_legs=True, beak=0.16),
 "Shark": lambda: fish(2.2, 0.35), "Octopus": lambda: octo(0.7), "Jaguar": lambda: quad(1.4, 1.0, 0.34, 0.45),
 "Bat": lambda: bird(0.22, beak=0.02), "CaveSpider": lambda: arthro(0.45), "VoidStalker": lambda: quad(1.5, 1.4, 0.36, 0.70),
 "Rabbit": lambda: quad(0.45, 0.5, 0.22, 0.14, ears="long"), "Hare": lambda: quad(0.55, 0.6, 0.24, 0.18, ears="long"),
 "Deer": lambda: quad(1.3, 1.4, 0.32, 0.75, horns=True, neck=True), "Caribou": lambda: quad(1.6, 1.5, 0.36, 0.80, horns="c", neck=True),
 "Squirrel": lambda: quad(0.30, 0.4, 0.16, 0.10), "Mouse": lambda: quad(0.20, 0.3, 0.12, 0.06, ears="side"),
 "Pheasant": lambda: bird(0.30, False), "Lizard": lambda: quad(0.5, 0.4, 0.14, 0.08, low=True, ears=None),
 "Jerboa": lambda: quad(0.25, 0.4, 0.14, 0.12, ears="long"), "Frog": lambda: quad(0.25, 0.3, 0.18, 0.08, low=True, ears=None, tail=False),
 "Newt": lambda: quad(0.25, 0.25, 0.10, 0.05, low=True, ears=None), "Crab": lambda: arthro(0.30), "Shrimp": lambda: fish(0.20, 0.4),
 "Monkey": lambda: quad(0.6, 0.9, 0.24, 0.35, ears="side"), "Tapir": lambda: quad(1.4, 1.0, 0.34, 0.45, ears="side"),
 "MountainGoat": lambda: quad(1.1, 1.1, 0.30, 0.50, horns="c"), "Marmot": lambda: quad(0.45, 0.45, 0.20, 0.10, ears="side"),
 "Glimmerling": lambda: quad(0.4, 0.5, 0.24, 0.15, ears="long"),
 "Bee": lambda: insect(0.10), "Butterfly": lambda: insect(0.12, legs6=False), "Ladybird": lambda: insect(0.08), "Grasshopper": lambda: insect(0.12),
 "Beetle": lambda: insect(0.12, wings=False), "Dragonfly": lambda: insect(0.14), "Firefly": lambda: insect(0.08), "Ant": lambda: insect(0.06, wings=False),
 "MorphoButterfly": lambda: insect(0.16, legs6=False), "Glowworm": lambda: insect(0.08, wings=False), "Lumamoth": lambda: insect(0.18, legs6=False),
 "Pufferfish": lambda: fish(0.35, 0.6, puff=True), "Tuna": lambda: fish(1.2, 0.35),
}
GLOWY = {"Firefly", "Glowworm", "Lumamoth", "Glimmerling", "VoidStalker", "Nebulafish", "Starling_Comet", "Blindfish"}

def fauna(a):
    n = a["name"][4:]
    cols = SPECIES.get(n)
    kind = a["mechanic"].split(" (")[0].lower()
    if not cols:
        hh = h(n, 1)
        cols = ("%02X%02X%02X" % (int(120 + 100 * hh), int(90 + 80 * h(n, 2)), int(60 + 60 * h(n, 3))), "E4DDCF", "202024")
    if n in PLAN:
        parts = PLAN[n]()
    elif kind == "fish" or n.startswith("Fish_"):
        parts = fish(0.4 + 0.3 * h(n, 4))
    elif kind == "birds" or n.startswith("Bird_"):
        parts = bird(0.25 + 0.15 * h(n, 4))
    elif kind == "insects" or kind.startswith("critter"):
        parts = insect(0.12)
    else:
        parts = quad(0.6 + 0.8 * h(n, 4), 0.8 + 0.5 * h(n, 5))
    glow = [1] if n in GLOWY else []
    return {"asset": a["name"], "materials": list(cols), "glow": glow, "parts": parts}

# ------------------------------------------------------------------ flora plans
def canopy(style, trunk_h, size, rng_name):
    out = []
    if style in ("round", "droop"):
        for i, (w, z) in enumerate(((1.0, 0), (1.2, 0.35), (0.9, 0.7), (0.5, 0.95))):
            out.append(b((size * w, size * w * (0.9 + 0.2 * h(rng_name, i)), size * 0.38), (size * 0.05 * (h(rng_name, i + 9) - 0.5), 0, trunk_h + size * z), B2))
        if style == "droop":
            out += [b((size * 0.12, size * 0.12, size * 0.6), (size * 0.5 * dx, size * 0.5 * dy, trunk_h - size * 0.15), B2) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, -0.7))]
    elif style == "conifer":
        for i, w in enumerate((1.0, 0.8, 0.6, 0.4, 0.2)):
            out.append(b((size * w, size * w, size * 0.32), (0, 0, trunk_h * 0.45 + i * size * 0.3), B2))
    elif style == "palm":   # 8 arched fronds: a rising inner segment and a drooping outer one, plus a crown
        import math
        for k in range(8):
            a = 2 * math.pi * k / 8 + 0.2; ca, sa = math.cos(a), math.sin(a); L = size * 0.55
            ex, ey = (abs(ca) * L + 0.06, abs(sa) * L + 0.06)
            out.append(b((ex if abs(ca) > 0.5 else 0.14 * size + 0.04, ey if abs(sa) > 0.5 else 0.14 * size + 0.04, 0.06), (ca * L * 0.5, sa * L * 0.5, trunk_h + 0.08), B2))
            out.append(b((max(abs(ca) * L * 0.8, 0.1 * size), max(abs(sa) * L * 0.8, 0.1 * size), 0.06), (ca * L * 1.25, sa * L * 1.25, trunk_h - 0.12 * size), B2))
            out.append(b((0.08 * size + 0.03, 0.08 * size + 0.03, 0.14 * size), (ca * L * 1.75, sa * L * 1.75, trunk_h - 0.28 * size), B2))
        out.append(b((size * 0.28, size * 0.28, size * 0.22), (0, 0, trunk_h + 0.06), B2))
        out += [b((0.1 * size + 0.04,) * 3, (dx * size * 0.12, dy * size * 0.12, trunk_h - 0.06), C) for dx, dy in ((1, 0), (-1, 0.3), (0, -1))]
    elif style == "spiky":
        out += [b((size * 0.15, size * 0.15, size * 0.4), (size * 0.3 * dx, size * 0.3 * dy, trunk_h + size * 0.1), B2) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
    elif style == "kelp":   # three swaying stalks with broad alternating blades and gas bladders
        for j, (sx, sy, f) in enumerate(((0, 0, 1.0), (size * 0.25, size * 0.15, 0.75), (-size * 0.2, -size * 0.1, 0.6))):
            if j: out.append(b((0.05 + 0.03 * size, 0.05 + 0.03 * size, trunk_h * f), (sx, sy, trunk_h * f / 2), A))
            for i in range(5):
                z = trunk_h * f * (0.18 + 0.17 * i); sd = (-1) ** (i + j)
                out.append(b((size * 0.32, 0.05, size * 0.22), (sx + sd * size * 0.17, sy, z), B2))
                out.append(b((0.06 + 0.04 * size,) * 3, (sx + sd * 0.04, sy, z - size * 0.13), C))
    elif style == "bamboo":
        out += [b((size * 0.3, 0.04, 0.05), (size * 0.15 * (-1) ** i, 0, trunk_h * (0.4 + 0.15 * i)), B2) for i in range(4)]
    return out

def tree(a):
    name = a["name"]; sp, stage = name.split("_")[2], name.split("_")[3]
    trunk, leaf, style = TREES.get(sp, ("7A5232", "4AA44F", "round"))
    sc = {"Sapling": 0.25, "Young": 0.55, "Mature": 1.0}[stage]
    th = (3.0 if style in ("palm", "bamboo") else 2.2 if style != "kelp" else 2.8) * sc
    tw = max(0.06, 0.32 * sc * (0.5 if style in ("bamboo", "kelp") else 1))
    boxes = [b((tw, tw, th), (0, 0, th / 2), A)]
    if style == "bamboo":
        boxes += [b((tw * 1.2, tw * 1.2, 0.04), (0, 0, th * f), A) for f in (0.25, 0.5, 0.75)] + [b((tw, tw, th * 0.8), (tw * 1.6, tw, th * 0.4), A)]
    if stage == "Mature" and style in ("round", "droop", "conifer"):
        boxes += [b((tw * 1.6, tw * 0.5, 0.12), (0, 0, 0.06), A), b((tw * 0.5, tw * 1.6, 0.12), (0, 0, 0.06), A)]   # roots
    leaves = canopy(style, th, 1.8 * sc + 0.2, name)
    parts = [{"name": "", "boxes": boxes}]
    if leaves:
        parts.append({"name": "_Top", "pivot": [0, 0, th * 0.8], "boxes": leaves})
    accent = "D82800" if sp in ("Oak", "Apple") else "F29BC0" if sp == "Kapok" else "7FE3FF" if sp == "StarWillow" else "6B8C2F" if sp == "Kelp" else "6B4A2A" if style == "palm" else "F2C230"
    if sp == "StarWillow":   # glow lives only in small hanging star-lights, so the canopy keeps its violet
        parts[-1]["boxes"] += [b((0.08 + 0.06 * sc,) * 3, (0.9 * sc * dx, 0.9 * sc * dy, th - 0.45 * sc), C) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, -0.7))]
    if stage == "Mature" and style == "round":
        parts[-1]["boxes"] += [b((0.12, 0.12, 0.12), (0.5 * (h(name, k) - 0.5) * 2.0, -0.95 * sc, th + 0.3 + 0.5 * h(name, k + 3)), C) for k in range(3)]
    return {"asset": name, "materials": [trunk, leaf, accent], "glow": [2] if sp == "StarWillow" else [], "parts": parts}

def crop(a):
    c, st = a["name"].split("_")[2], int(a["name"].split("_")[3][1])
    leaf, fruit = CROP.get(c, ("4B974B", "F2C230"))
    soil = [b((0.98, 0.98, 0.12), (0, 0, 0.06), A)]
    plants = []
    for i, (x, y) in enumerate(((-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25))):
        hgt = 0.08 + 0.14 * st
        plants.append(b((0.06, 0.06, hgt), (x, y, 0.12 + hgt / 2), B2))
        if st >= 2:
            plants.append(b((0.18, 0.04, 0.04), (x, y, 0.12 + hgt * 0.6), B2))
        if st == 4:
            fs = 0.30 if c in ("Pumpkin", "Melon") else 0.12
            plants.append(b((fs, fs, fs), (x, y - (0.12 if c in ("Pumpkin", "Melon") else 0), 0.12 + (fs / 2 if c in ("Pumpkin", "Melon", "Potato", "Carrot") else hgt)), C))
    return {"asset": a["name"], "materials": ["5A3A22", leaf, fruit], "glow": [2] if c == "Starbean" else [], "parts": [
        {"name": "", "boxes": soil}, {"name": "_Plants", "pivot": [0, 0, 0.12], "boxes": plants}]}

def small_plant(a):
    n = a["name"]; kind, sp = n.split("_")[1], "_".join(n.split("_")[2:])
    if kind == "Flower":
        col = FLOWER.get(sp, "F29BC0")
        bx = [b((0.04, 0.04, 0.30), (0, 0, 0.15), A), b((0.14, 0.04, 0.03), (0.06, 0, 0.12), A), b((0.16, 0.16, 0.05), (0, 0, 0.32), B2),
              b((0.06, 0.06, 0.06), (0, 0, 0.36), C), b((0.04, 0.04, 0.22), (0.12, 0.08, 0.11), A), b((0.10, 0.10, 0.04), (0.12, 0.08, 0.24), B2)]
        return {"asset": n, "materials": ["4B974B", col, "F2C230"], "glow": [1] if sp == "NovaBloom" else [], "parts": [{"name": "", "boxes": bx}]}
    if kind == "Grass":
        bx = [b((0.04, 0.03, 0.15 + 0.25 * h(n, k)), ((h(n, k + 5) - 0.5) * 0.5, (h(n, k + 9) - 0.5) * 0.5, (0.15 + 0.25 * h(n, k)) / 2), A if k % 2 else B2) for k in range(9)]
        g = {"Hay": ("C8B040", "E2D08C"), "DuneGrass": ("C8B040", "8CC040"), "Seagrass": ("2C8C18", "4B974B"), "Moss": ("4B974B", "2C6B3A"),
             "Shimmergrass": ("7FE3FF", "A070FF"), "Vine": ("2C8C18", "59D940")}.get(sp, ("6CC046", "4AA44F"))
        return {"asset": n, "materials": list(g) + ["F4F6FB"], "glow": [0] if sp == "Shimmergrass" else [], "parts": [{"name": "", "boxes": bx}]}
    if kind == "Mushroom":
        capc = {"Toadstool": "D82800", "Porcini": "8C5A2A", "Frostcap": "A8D8E8", "Glowcap": "7FE3FF", "Bracket": "C87800",
                "CaveShroom": "9C9C9C", "Glowshroom": "59D940", "Voidcap": "5C389E"}.get(sp, "C87800")
        bx = [b((0.10, 0.10, 0.16), (0, 0, 0.08), A), b((0.30, 0.30, 0.08), (0, 0, 0.19), B2), b((0.20, 0.20, 0.06), (0, 0, 0.25), B2),
              b((0.05, 0.05, 0.02), (0.07, -0.08, 0.235), C), b((0.06, 0.06, 0.10), (0.14, 0.10, 0.05), A), b((0.14, 0.14, 0.05), (0.14, 0.10, 0.12), B2)]
        return {"asset": n, "materials": ["F0E6D0", capc, "F4F6FB"], "glow": [1] if "Glow" in sp or sp == "Voidcap" else [], "parts": [{"name": "", "boxes": bx}]}
    if kind in ("Shrub", "Herb"):
        leaf = {"Saguaro": "4B974B", "Tumbleweed": "C8A070", "Reed": "8CC040", "Cattail": "6B8C2F", "Coral_Brain": "F29BC0", "Coral_Fan": "C060C0",
                "Lichen": "9CB070", "SeaSalt": "F4F6FB", "Stardust": "7FE3FF", "CrystalShrub2": "A070FF", "Heather": "C080C0"}.get(sp, "4AA44F")
        s = 0.6 if kind == "Shrub" else 0.3
        if sp == "Saguaro":
            bx = [b((0.30, 0.30, 1.6), (0, 0, 0.8), B2), b((0.16, 0.16, 0.5), (0.3, 0, 0.9), B2), b((0.2, 0.16, 0.16), (0.2, 0, 0.7), B2),
                  b((0.16, 0.16, 0.4), (-0.3, 0, 1.1), B2), b((0.2, 0.16, 0.16), (-0.2, 0, 0.95), B2), b((0.08, 0.08, 0.08), (0, 0, 1.64), C)]
        elif sp in ("Reed", "Cattail", "Bamboo"):
            bx = [b((0.04, 0.04, 0.9 + 0.3 * h(n, k)), ((h(n, k) - 0.5) * 0.4, (h(n, k + 3) - 0.5) * 0.4, (0.9 + 0.3 * h(n, k)) / 2), B2) for k in range(6)]
            if sp == "Cattail":
                bx += [b((0.07, 0.07, 0.16), (k[1][0], k[1][1], k[0][2] + 0.05), C) for k in bx[:4]]
        else:
            bx = [b((s * 0.2, s * 0.2, s * 0.3), (0, 0, s * 0.15), A)] + [
                b((s * (0.7 - 0.15 * i), s * (0.7 - 0.15 * i) * (0.85 + 0.3 * h(n, i)), s * 0.35), ((h(n, i) - 0.5) * s * 0.2, (h(n, i + 4) - 0.5) * s * 0.2, s * (0.35 + 0.3 * i)), B2) for i in range(3)]
            if kind == "Herb":
                bx += [b((0.05, 0.05, 0.05), (s * 0.2, -s * 0.25, s * 0.8), C)]
        return {"asset": n, "materials": ["6B4A2A", leaf, "F4F6FB"], "glow": [1] if sp in ("Stardust", "CrystalShrub2") else [], "parts": [{"name": "", "boxes": bx}]}
    return None

def flora(a):
    n = a["name"]
    if n.startswith("Prop_Tree_"): return tree(a)
    if n.startswith("Prop_Crop_"): return crop(a)
    if n.split("_")[1] in ("Flower", "Grass", "Mushroom", "Shrub", "Herb"): return small_plant(a)
    return None

# ------------------------------------------------------------------ groups, in build order
def _eco(a): return a["category"] in ("Flora", "Fauna", "Other Worlds")
def _spec(a):
    if a["name"].startswith("Mob_"):
        return fauna(a) if "Realm" not in a["name"] else None
    return flora(a)
EXISTING_FOES = {"Mob_BlightSlime", "Mob_Shardback", "Mob_DustWisp", "Mob_StoneKnight"}   # the brief's foes: own pass with Claude's notes
eco = [a for a in ASSETS if _eco(a) and a["name"] not in EXISTING_FOES]
def group(pred): return [s for s in (_spec(a) for a in sorted(eco, key=lambda a: (a["priority"], a["name"])) if pred(a)) if s]
mech = lambda a: a["mechanic"].lower()
GROUPS = {
 "livestock_predators": group(lambda a: a["name"].startswith("Mob_") and (mech(a).startswith("livestock") or mech(a).startswith("predators"))),
 "crops": group(lambda a: a["name"].startswith("Prop_Crop_")),
 "trees": group(lambda a: a["name"].startswith("Prop_Tree_")),
 "fauna_rest": group(lambda a: a["name"].startswith("Mob_") and not (mech(a).startswith("livestock") or mech(a).startswith("predators"))),
 "flora_rest": group(lambda a: a["name"].startswith("Prop_") and not a["name"].startswith(("Prop_Crop_", "Prop_Tree_"))),
}
SPECS = [s for g in GROUPS.values() for s in g]
