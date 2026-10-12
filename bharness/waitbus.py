"""Wait (<= N s, check every 30 s) for the Unreal team: art\BUS.json, a change in NOTES\Blender-team-handoff.md, or new feed lines."""
import os, sys, time, json
from bharness.context import DEFAULT_ART as A
N = float(sys.argv[1]) if len(sys.argv) > 1 else 720
notes = os.path.join(A, "NOTES", "Blender-team-handoff.md"); feed = os.path.join(A, "feed.jsonl")
m0, f0, t0 = os.path.getmtime(notes), os.path.getsize(feed), time.time()
while time.time() - t0 < N:
    hit = []
    if os.path.exists(os.path.join(A, "BUS.json")): hit.append("BUS.json: " + open(os.path.join(A, "BUS.json")).read())
    if os.path.getmtime(notes) != m0: hit.append("NOTES changed:\n" + open(notes, encoding="utf-8-sig").read().rsplit("\n---", 2)[-2][-3000:] + "\n[tail]\n" + open(notes, encoding="utf-8-sig").read()[-1500:])
    if os.path.getsize(feed) != f0:
        with open(feed, encoding="utf-8") as f: f.seek(f0); print("FEED:\n" + f.read()[-3000:], flush=True); f0 = f.tell()
    print(time.strftime("%H:%M:%S"), "hit" if hit else "nothing", flush=True)
    if hit:
        print("\n".join(hit), flush=True); sys.exit(0)
    time.sleep(30)
print("TIMEOUT nothing arrived", flush=True)

