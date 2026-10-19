import os, re, sys, time
sys.path.insert(0, r"C:\Users\730ri\projects\blender-harness"); os.chdir(r"C:\Users\730ri\projects\blender-harness")
from bharness.bus import Bus
import assets.autowave as A
Q = r"C:\Users\730ri\projects\bot-team\art\QUEUE.md"; LOG = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs", "island4481.log")
def log(s): open(LOG, "a").write(time.strftime("%H:%M ") + s + "\n")
def row():
    for l in open(Q, encoding="utf-8"):
        c = l.split("|")
        if len(c) > 6 and c[1].strip() == "4481": return c[5].strip()
def setrow(st):
    t = open(Q, encoding="utf-8").read(); L = t.split("\n")
    for i, l in enumerate(L):
        c = l.split("|")
        if len(c) > 6 and c[1].strip() == "4481": c[5] = " %s " % st; L[i] = "|".join(c)
    if open(Q, encoding="utf-8").read() == t: open(Q, "w", encoding="utf-8").write("\n".join(L)); return True
end = time.time() + 6 * 3600; log("waiting for drain (READY<=150)")
while time.time() < end and A.ready_count() > 150: time.sleep(60)
for _ in range(5):
    if setrow("READY"): break
    time.sleep(2)
log("4481 READY, READY=%d" % A.ready_count())
while time.time() < end and not (row() or "").startswith(("SHIPPED", "BLOCKED")): time.sleep(30)
st = row() or ""; log("4481 -> " + st)
m = re.search(r"\((\d+) tris", st); tris = int(m.group(1)) if m else 0
ok = abs(tris - 445294) <= 0.05 * 445294
b = Bus(r"C:\Users\730ri\projects\bot-team\art")
if ok:
    b.send("note", {"asset": "-", "text": "DONE row 4481 Prop_Island_Flagship_BlenderBoss shipped at %d tris (expected ~445k). @unreal-team @2hot2trot: please replace/delete the bad 36-tri uasset from superseded row 2963 so /Game/Daedalus/Art/Prop/Prop_Island_Flagship_BlenderBoss is the 445k version." % tris})
else:
    b.send("note", {"asset": "-", "text": "BLOCKED row 4481 Prop_Island_Flagship_BlenderBoss: status '%s', expected ~445k tris. Blender team checking." % st[:80]})
log("posted ok=%s tris=%d" % (ok, tris))
