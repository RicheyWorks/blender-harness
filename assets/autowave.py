# SPDX-License-Identifier: MIT
"""Keep >= 100 READY rows in QUEUE.md (standing order, 2026-10-12). Hidden loop:
every 60 s count READY; below the floor, generate the next procedural wave (rotating crafting items, island props, ark parts,
creatures, biome flora variants), build it headless (blender -b, hidden), append QUEUE rows, post on the team link.
Team requests come first: any NEED addressed to the Blender team is logged to art/bus/requests.jsonl for a human/agent to claim.
Usage: python -m assets.autowave --loop [--floor=100] [--hours=6]    |   GROUPS/SPECS read art/bus/autowave_current.json"""
import json, os, random, subprocess, sys, time
from collections import Counter

ART = r"C:\Users\730ri\projects\bot-team\art"
STATE = os.path.join(ART, "bus", "autowave.json"); CUR = os.path.join(ART, "bus", "autowave_current.json")
ROT = ["crafting", "island", "ark", "creatures", "flora"]
BLENDER = r"C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)

def b(s, c, m=0): return [list(s), list(c), m]
def S(asset, mats, boxes, glow=()): return {"asset": asset, "materials": list(mats), "glow": list(glow), "parts": [{"name": "", "boxes": boxes}]}
METALS = [("Copper", "C8703A"), ("Iron", "C9B49C"), ("Gold", "F2C230"), ("Crystal", "A070FF"), ("Starmetal", "7FE3FF"), ("Heartstone", "FF8A3D"), ("Wood", "8C5A2A"), ("Stone", "7D7B84")]
DARK = "34343A"

def crafting(k, r):
    shapes = {
        "Gear": lambda: [b((0.3, 0.06, 0.3), (0, 0, 0.15), 0)] + [b((0.08, 0.06, 0.08), (0.17 * dx, 0, 0.15 + 0.17 * dz), 0) for dx, dz in ((1, 0), (-1, 0), (0, 1), (0, -1))] + [b((0.08, 0.07, 0.08), (0, 0, 0.15), 1)],
        "Plate": lambda: [b((0.4, 0.3, 0.04), (0, 0, 0.02), 0), b((0.36, 0.26, 0.01), (0, 0, 0.045), 1)],
        "Rod": lambda: [b((0.04, 0.04, 0.5), (0, 0, 0.25), 0), b((0.06, 0.06, 0.04), (0, 0, 0.02), 1)],
        "Rivets": lambda: [b((0.05, 0.05, 0.03), (x, y, 0.015), 0) for x in (-0.06, 0, 0.06) for y in (-0.04, 0.04)],
        "Hinge": lambda: [b((0.12, 0.02, 0.16), (-0.06, 0, 0.08), 0), b((0.12, 0.02, 0.16), (0.06, 0.01, 0.08), 0), b((0.03, 0.03, 0.17), (0, 0, 0.085), 1)],
        "Chain": lambda: [b((0.06, 0.02, 0.1), (0, 0, 0.05 + 0.08 * i), i % 2) for i in range(5)],
        "Spring": lambda: [b((0.12, 0.12, 0.02), (0, 0, 0.02 + 0.04 * i), i % 2) for i in range(6)],
        "Frame": lambda: [b((0.5, 0.05, 0.05), (0, 0, z), 0) for z in (0.025, 0.475)] + [b((0.05, 0.05, 0.5), (x, 0, 0.25), 0) for x in (-0.225, 0.225)] + [b((0.4, 0.02, 0.4), (0, 0, 0.25), 1)],
    }
    out = []
    for sh, f in shapes.items():
        for m, c in METALS:
            if m == "Stone" or (m == "Wood" and sh in ("Rivets", "Spring", "Chain")): continue
            out.append(S("Item_Part_%s_%s" % (sh, m), (c, DARK, c), f(), [0] if m in ("Crystal", "Starmetal", "Heartstone") else []))
    return out

def island(k, r):
    out = []
    kinds = ["Boulder", "RockCluster", "Stump", "Log", "Driftwood", "RuinPillar", "RuinWall", "CrystalSpire", "Mushroomring", "Cairn", "Geyser", "Tidepool"]
    pal = {"Boulder": ("7D7B84", "4A4F5C", "59A040"), "RockCluster": ("7D7B84", "A0A0A0", "4A4F5C"), "Stump": ("6B4A2A", "C8A070", "59A040"),
           "Log": ("6B4A2A", "C8A070", "59A040"), "Driftwood": ("C8B8A0", "A09080", "E4DDCF"), "RuinPillar": ("D8D0C0", "A09080", "59A040"),
           "RuinWall": ("C0B8A8", "8C8478", "59A040"), "CrystalSpire": ("A070FF", "7FE3FF", "4A4F5C"), "Mushroomring": ("F0E6D0", "D82800", "59A040"),
           "Cairn": ("A0A0A0", "7D7B84", "59A040"), "Geyser": ("7D7B84", "A8D8E8", "F4F6FB"), "Tidepool": ("A0A0A0", "2F80D8", "E05050")}
    for kind in kinds:
        for v in range(5):
            rr = random.Random("%s%d%d" % (kind, k, v)); s = 0.6 + rr.random() * 1.6; bx = []
            for i in range(4 + rr.randint(0, 4)):
                w = s * (0.3 + rr.random() * 0.5); hgt = s * (0.2 + rr.random() * (1.5 if kind in ("RuinPillar", "CrystalSpire", "Geyser") else 0.6))
                bx.append(b((w, w * (0.6 + rr.random() * 0.6), hgt), ((rr.random() - 0.5) * s, (rr.random() - 0.5) * s, hgt / 2), i % 3 if i else 0))
            out.append(S("Prop_Island_%s_K%dV%d" % (kind, k, v), pal[kind], bx, [1] if kind in ("CrystalSpire",) else []))
    return out

def ark(k, r):
    from assets.wave4 import ark_parts, GLOWPART
    tiers = [("Copper", "C8703A", "6B4A2A", "E8C890"), ("Gold", "F2C230", "8C5A2A", "F8F0C0"), ("Crystal", "5C389E", "A070FF", "D7B8FF"),
             ("Heartstone", "4A4F5C", "FF8A3D", "FFD0A0"), ("Bone", "E4DDCF", "8C8478", "34343A"), ("Coral", "E05050", "F29BC0", "2F80D8")]
    t = tiers[(k // 5) % len(tiers)], tiers[(k // 5 + 1) % len(tiers)], tiers[(k // 5 + 2) % len(tiers)]
    return [S("Veh_ArkPart_%s_%s" % (p, tn), (a, bc, c), bx, GLOWPART.get(p, [])) for tn, a, bc, c in t for p, bx in ark_parts().items()]

def creatures(k, r):
    from assets import ecospecs as E
    biomes = ["Forest", "Meadow", "Dune", "Frost", "Bog", "Reef", "Canopy", "Crag", "Starfall"]
    kinds = [("wildlife", "Grazer"), ("predator", "Prowler"), ("birds", "Flier"), ("fish", "Swimmer"), ("insects", "Crawler"), ("critter", "Hopper")]
    out = []
    for bi in biomes:
        for kind, word in kinds:
            n = "Mob_%s_%s_K%d" % (bi, word, k)
            out.append(E.fauna({"name": n, "mechanic": "%s (wave %d)" % (kind.capitalize(), k)}))
    return out

def flora(k, r):
    from assets import flora2 as F
    out = []
    for n, kd, bi, c1, c2, use in F.SPECIES[(k * 7) % 50:(k * 7) % 50 + 20]:
        rr = random.Random(n + str(k)); shift = lambda h: "%02X%02X%02X" % tuple(max(0, min(255, int(h[i:i + 2], 16) + rr.randint(-40, 40))) for i in (0, 2, 4))
        mats = [shift(c1), shift(c2), F.SOIL.get(kd, "6B4A2A")]; nn = "%s_V%d" % (n, k)
        out.append({"asset": "Prop_%s_%s" % (kd, nn), "materials": mats, "glow": [], "parts": [{"name": "", "boxes": F.plant(nn, kd, False)}]})
        out.append({"asset": "Prop_%s_%s_Harvested" % (kd, nn), "materials": mats, "glow": [], "parts": [{"name": "", "boxes": F.plant(nn, kd, True)}]})
        out.append({"asset": "Item_%s_%s" % (kd, nn), "materials": mats, "glow": [], "parts": [{"name": "", "boxes": F.item(nn, kd)}]})
    return out

GEN = {"crafting": crafting, "island": island, "ark": ark, "creatures": creatures, "flora": flora}
SIZE = {"crafting": "~0.3-0.5 m", "island": "0.6-2.2 m", "ark": "2 m grid", "creatures": "varies", "flora": "~0.4 m"}

def __getattr__(name):   # GROUPS / SPECS / ORDER for headless.py and addrows.py
    cur = json.load(open(CUR, encoding="utf-8"))
    if name == "GROUPS": return {cur["cat"]: cur["specs"]}
    if name == "SPECS": return cur["specs"]
    if name == "ORDER": return [cur["cat"]]
    if name == "SIZE": return {cur["cat"]: SIZE[cur["cat"]]}
    raise AttributeError(name)

def ready_count():
    sys.path.insert(0, HERE)
    from bharness.plugins.queue import QueuePlugin, state
    from bharness.context import Context
    return Counter(state(r["status"]) for r in QueuePlugin(Context()).rows())["READY"]

def wave(bus, st):
    from bharness.plugins.queue import QueuePlugin
    from bharness.context import Context
    have = {r["asset"] for r in QueuePlugin(Context()).rows()}
    for _ in range(len(ROT)):
        k = st["k"] = st.get("k", 0) + 1; cat = ROT[k % len(ROT)]
        specs = [s for s in GEN[cat](k, None) if s["asset"] not in have and not os.path.exists(os.path.join(ART, "glb", s["asset"] + ".glb"))]
        if specs: break
    json.dump({"k": k, "cat": cat, "specs": specs}, open(CUR, "w", encoding="utf-8")); json.dump(st, open(STATE, "w"))
    bus.send("note", {"asset": "-", "text": "DOING blender-team auto-wave %d (%s, %d assets): READY fell below the floor; building headless now." % (k, cat, len(specs))})
    log = os.path.join(os.environ.get("LOCALAPPDATA", ART), "Daedalus", "jobs", "autowave-build.log")
    with open(log, "w") as f:
        subprocess.run([BLENDER, "-b", "--factory-startup", "--python", os.path.join(HERE, "assets", "headless.py"), "--", HERE, "assets.autowave", cat,
                        "--batch=10", "--turntable=4", "--no-send"], stdout=f, stderr=subprocess.STDOUT, creationflags=NOWIN, timeout=3600)
    from assets import addrows
    import io, contextlib
    out = io.StringIO()
    with contextlib.redirect_stdout(out): addrows.main(["assets.autowave", "auto%d" % k])
    res = json.loads(out.getvalue().strip().splitlines()[-1])
    first = res.get("first", "").split("|")[1].strip() if res.get("first") else "-"; last = res.get("last", "").split("|")[1].strip() if res.get("last") else "-"
    bus.send("note", {"asset": "-", "text": "DONE blender-team auto-wave %d (%s): %d built, QUEUE rows %s-%s appended READY [auto%d block]." % (k, cat, res.get("added", 0), first, last, k)})
    return res

def requests(bus, st):
    """Log NEED/asset requests addressed to the Blender team (served first by the agent; logged here so none are missed)."""
    import urllib.request
    try:
        after = st.get("req_after", 0)
        j = json.load(urllib.request.urlopen("http://127.0.0.1:9890/wait?me=blender-reqscan&after=%d&timeout=1" % after, timeout=5))
        for m in j.get("messages", []):
            t = json.dumps(m.get("body") or {})
            if m.get("from") != "blender-team" and "NEED" in t and ("blender" in t.lower() or m.get("to") == "blender-team"):
                open(os.path.join(ART, "bus", "requests.jsonl"), "a", encoding="utf-8").write(json.dumps(m) + "\n")
        st["req_after"] = j.get("last", after)
    except Exception: pass

def loop(floor=100, hours=6):
    sys.path.insert(0, HERE)
    from bharness.bus import Bus
    bus = Bus(ART); st = json.load(open(STATE)) if os.path.exists(STATE) else {}
    end = time.time() + hours * 3600
    while time.time() < end:
        requests(bus, st); json.dump(st, open(STATE, "w"))
        try:
            n = ready_count()
            if n < floor: print(json.dumps({"ready": n, "wave": wave(bus, st)}), flush=True)
        except Exception as e:
            print(json.dumps({"error": repr(e)[:300]}), flush=True)
        time.sleep(60)
    return 0

if __name__ == "__main__" and "--loop" in sys.argv:
    o = dict(x[2:].split("=") for x in sys.argv if x.startswith("--") and "=" in x)
    sys.exit(loop(int(o.get("floor", 100)), float(o.get("hours", 6))))
