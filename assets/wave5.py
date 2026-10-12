# SPDX-License-Identifier: MIT
"""Wave 5: board #4 storage chests (moving _Lid, hinge pivot at the back) and #16 NPC Ark crew (humanoids with
_Body/_Head/_ArmL/_ArmR/_LegL/_LegR, role props on the body/head). Rigs and clips come from pilots/rig_batch.py."""
from assets.flora2 import b

def P(name, pivot, boxes): return {"name": name, "pivot": list(pivot), "boxes": boxes}
CHESTS = {"Wood": ("8C5A2A", "6B4A2A", "707070", 1.0), "Iron": ("707070", "4A4A4A", "C9B49C", 1.0), "Gold": ("8C5A2A", "F2C230", "F8F0C0", 1.0),
          "Starmetal": ("2A1840", "7FE3FF", "C0C0C0", 1.0), "Large_Wood": ("8C5A2A", "6B4A2A", "707070", 1.5), "Ark_Locker": ("4A4F5C", "C8703A", "7FE3FF", 1.2)}
def chest(n, c):
    a, bnd, lock, s = c; W, D, H = 0.9 * s, 0.6 * s, 0.45 * s
    base = [b((W, D, H), (0, 0, H / 2), 0), b((W + 0.02, 0.05, H * 0.9), (0, -D / 2, H / 2), 1), b((0.05, D + 0.02, H * 0.9), (-W / 2 + 0.1, 0, H / 2), 1),
            b((0.05, D + 0.02, H * 0.9), (W / 2 - 0.1, 0, H / 2), 1), b((0.12, 0.04, 0.12), (0, -D / 2 - 0.02, H - 0.06), 2)]
    lid = [b((W + 0.02, D + 0.02, 0.12 * s), (0, 0, H + 0.06 * s), 0), b((W * 0.9, D * 0.9, 0.08 * s), (0, 0, H + 0.16 * s), 0),
           b((0.05, D + 0.04, 0.2 * s), (-W / 2 + 0.1, 0, H + 0.1 * s), 1), b((0.05, D + 0.04, 0.2 * s), (W / 2 - 0.1, 0, H + 0.1 * s), 1),
           b((0.1, 0.04, 0.08), (0, -D / 2 - 0.02, H + 0.02), 2)]
    return {"asset": "Prop_Chest_" + n, "materials": [a, bnd, lock], "glow": [2] if n in ("Starmetal", "Ark_Locker") else [],
            "parts": [P("_Base", (0, 0, 0), base), P("_Lid", (0, D / 2, H), lid)]}

# crew: (role, skin, outfit, accent, extra body boxes, extra head boxes)
SK = ["E8B890", "C88860", "8C5A3A", "F0D0B0"]
def human(role, skin, cloth, acc, body_x=(), head_x=(), h=1.8):
    k = h / 1.8; L, T, A = 0.85 * k, 0.6 * k, 0.62 * k
    body = [b((0.46 * k, 0.26 * k, T), (0, 0, L + T / 2), 1), b((0.48 * k, 0.28 * k, 0.08 * k), (0, 0, L + 0.06 * k), 2)] + list(body_x)
    head = [b((0.32 * k, 0.3 * k, 0.32 * k), (0, 0, L + T + 0.18 * k), 0), b((0.05 * k, 0.02, 0.05 * k), (-0.08 * k, -0.16 * k, L + T + 0.2 * k), 2),
            b((0.05 * k, 0.02, 0.05 * k), (0.08 * k, -0.16 * k, L + T + 0.2 * k), 2)] + list(head_x)
    arm = lambda s: [b((0.13 * k, 0.14 * k, A), (s * 0.3 * k, 0, L + T - A / 2), 1), b((0.12 * k, 0.12 * k, 0.1 * k), (s * 0.3 * k, 0, L + T - A - 0.05 * k), 0)]
    leg = lambda s: [b((0.17 * k, 0.18 * k, L - 0.08 * k), (s * 0.12 * k, 0, (L - 0.08 * k) / 2 + 0.08 * k), 1), b((0.18 * k, 0.24 * k, 0.08 * k), (s * 0.12 * k, -0.03 * k, 0.04 * k), 2)]
    top = L + T
    return {"asset": "Mob_Crew_" + role, "materials": [skin, cloth, acc], "glow": [],
            "parts": [P("_Body", (0, 0, L), body), P("_Head", (0, 0, top), head), P("_ArmL", (-0.3 * k, 0, top - 0.05), arm(-1)), P("_ArmR", (0.3 * k, 0, top - 0.05), arm(1)),
                      P("_LegL", (-0.12 * k, 0, L), leg(-1)), P("_LegR", (0.12 * k, 0, L), leg(1))]}
def crew():
    H = lambda *x: list(x)
    return [
        human("Captain", SK[0], "1C3C8C", "F2C230", [b((0.5, 0.3, 0.06), (0, 0, 1.38), 2)], [b((0.42, 0.4, 0.08), (0, 0, 1.67), 1), b((0.3, 0.3, 0.12), (0, 0, 1.75), 1), b((0.08, 0.02, 0.06), (0, -0.2, 1.75), 2)]),
        human("Navigator", SK[1], "2C6B5A", "C8A070", [b((0.06, 0.3, 0.06), (0.26, 0, 1.2), 2)], [b((0.36, 0.34, 0.06), (0, 0, 1.65), 2)]),
        human("Engineer", SK[2], "C8703A", "34343A", [b((0.3, 0.06, 0.4), (0, -0.15, 1.05), 2)], [b((0.3, 0.06, 0.08), (0, -0.16, 1.66), 2)]),
        human("Cook", SK[3], "F4F6FB", "D82800", [b((0.4, 0.04, 0.5), (0, -0.15, 1.0), 1)], [b((0.3, 0.3, 0.25), (0, 0, 1.8), 1)]),
        human("Smith", SK[1], "4A4A4A", "8C5A2A", [b((0.44, 0.04, 0.55), (0, -0.15, 1.05), 2)], [], h=1.9),
        human("Botanist", SK[0], "4B974B", "F2E6CC", [b((0.2, 0.15, 0.2), (0.3, 0.1, 1.0), 2)], [b((0.5, 0.5, 0.04), (0, 0, 1.64), 2), b((0.3, 0.3, 0.1), (0, 0, 1.7), 2)]),
        human("Merchant", SK[2], "8C2A60", "F2C230", [b((0.2, 0.12, 0.2), (-0.28, -0.05, 0.95), 2)], [b((0.34, 0.32, 0.14), (0, 0, 1.68), 1)]),
        human("Medic", SK[3], "F4F6FB", "D82800", [b((0.14, 0.04, 0.04), (0, -0.14, 1.25), 2), b((0.04, 0.04, 0.14), (0, -0.14, 1.25), 2)], []),
        human("Deckhand", SK[0], "6B8CB0", "E4DDCF", [], [b((0.34, 0.32, 0.06), (0, 0, 1.63), 2)], h=1.7),
        human("Lookout", SK[1], "5A6B3A", "C0C0C0", [b((0.05, 0.25, 0.05), (0.27, -0.1, 1.15), 2)], [b((0.34, 0.32, 0.1), (0, 0, 1.65), 1)], h=1.75),
        human("Shipwright", SK[2], "A0522D", "C8A070", [b((0.06, 0.06, 0.3), (0.3, 0.05, 0.9), 2)], [], h=1.85),
        human("Kid", SK[3], "F29BC0", "59D940", [], [b((0.12, 0.12, 0.12), (0.1, 0.05, 1.18), 2)], h=1.2),
    ]
ORDER = ["crew", "chests"]
SIZE = {"crew": "~1.8 m", "chests": "0.9-1.35 m"}
def specs(): return {"crew": crew(), "chests": [chest(n, c) for n, c in CHESTS.items()]}
def entries():
    out = []
    for grp, cat, mech in (("crew", "Fauna", "NPC Ark crew (rigged: Idle/Walk/Attack/Hit clips in art/rig)"), ("chests", "Blocks", "Storage chest; _Lid opens (hinge at back)")):
        for s in specs()[grp]:
            out.append(dict(name=s["asset"], category=cat, world="Shattered islands (all)", mechanic=mech, drops="", tier="",
                            parts=", ".join(p["name"] for p in s["parts"]), priority=2, notes="wave 5 (board #4/#16)"))
    return out
_G = None
def __getattr__(name):
    global _G
    if name in ("GROUPS", "SPECS"):
        if _G is None: _G = specs()
        return _G if name == "GROUPS" else [x for v in _G.values() for x in v]
    raise AttributeError(name)
