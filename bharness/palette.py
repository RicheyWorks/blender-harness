# SPDX-License-Identifier: MIT
"""The game's colours as one library: Daedalus block colours (BlockColors.java), the brief's ore colours, and the
realm's 8-bit palette. Specs name colours ("wood", "iron") or give hex; resolve() turns either into hex."""
import re

BLOCKS = {"stone": "7D7B84", "dirt": "7A5230", "wood": "9A6B3F", "glass": "A8D8E8", "grass": "6CC046", "sand": "E2D08C",
          "water": "2F80D8", "log": "7A5232", "leaves": "4AA44F", "blossom": "F29BC0", "gravel": "9B9387", "cloud": "F4F6FB",
          "road": "4A4D57", "paving": "E4DDCF", "brick_red": "C4281C", "brick_blue": "0D69AC", "brick_yellow": "F5CD30",
          "brick_green": "4B974B", "brick_white": "F2F3F3", "spawn": "1FB5B0", "portal": "D7B8FF"}
ORES = {"coal": "34343A", "copper": "C8703A", "iron": "C9B49C", "gold": "F2C230", "crystal": "A070FF", "starmetal": "7FE3FF",
        "slime": "59D940", "ghost": "5C389E"}
MISC = {"grip": "5A3A22", "steel": "C9D4E0", "dark": "4A4D57", "rope": "D8C79A", "cloth": "E8DCC4", "leaf": "4AA44F",
        "red": "D82800", "white": "F8F8F8", "black": "202024", "blue": "0058F8", "purple": "8C34C8", "orange": "F87818"}
PALETTE = dict(BLOCKS, **ORES, **MISC)
GLOW = {"crystal", "starmetal", "portal"}
HEX = re.compile(r"^#?[0-9A-Fa-f]{6}$")


def resolve(c):
    """'iron' / '#C9B49C' / 'C9B49C' -> 'C9B49C'. Unknown names raise KeyError (a typo is a bug, not black)."""
    if HEX.match(c):
        return c.lstrip("#").upper()
    return PALETTE[c.lower()]


def linear(h):
    """sRGB hex -> linear RGBA, what Blender's colour sockets expect."""
    h = resolve(h)
    return tuple(round((int(h[k:k + 2], 16) / 255.0) ** 2.2, 5) for k in (0, 2, 4)) + (1.0,)
