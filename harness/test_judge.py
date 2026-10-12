"""The brief's rules, pure (no Blender)."""
from harness.check import Checks
from harness.fakes import crate
from bharness.plugins.judge import judge, passed, first_failure

t = Checks()
ok = judge("Prop_BHTest", crate())
t("a good crate passes", passed(ok), [c for c in ok if not c["ok"]])
cases = [
    ("bad name (space)", "Prop BHTest", crate(), "name is Kind_Name, no spaces"),
    ("bad kind", "Thing_X", crate("Thing_X"), "name is Kind_Name, no spaces"),
    ("over prop budget", "Prop_BHTest", crate(tris=3001), "triangle budget"),
    ("unapplied scale", "Prop_BHTest", crate(scale=(2, 1, 1)), "scale applied"),
    ("no material slot", "Prop_BHTest", crate(slots=0), "1-3 filled material slots"),
    ("four slots", "Prop_BHTest", crate(slots=4), "1-3 filled material slots"),
    ("image texture", "Prop_BHTest", crate(images=True), "flat colours, no image textures"),
    ("floating", "Prop_BHTest", crate(zmin=0.3), "stands on z=0 (bottom-centre origin)"),
]
for label, name, p, want in cases:
    cs = judge(name, p)
    t("rejects: " + label, first_failure(cs) == want, first_failure(cs))
t("mob budget is 6000", passed(judge("Mob_X", crate("Mob_X", tris=6000))) and not passed(judge("Mob_X", crate("Mob_X", tris=6001))))
t("vehicle budget is 12000", passed(judge("Veh_X", crate("Veh_X", tris=12000))))
t("building budget is 15000", passed(judge("Bld_X", crate("Bld_X", tris=15000))))
t("no collection fails", not passed(judge("Prop_X", {"collection": False, "objects": []})))
t("empty asset fails (zero meshes is not a pass)", first_failure(judge("Prop_X", {"collection": True, "objects": []})) == "has meshes")
p = crate(); p["objects"][0]["min"][0] = 0.0; p["objects"][0]["max"][0] = 1.0
t("off-centre fails", first_failure(judge("Prop_BHTest", p)) == "centred on x/y")
t.done()
