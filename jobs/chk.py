import json, urllib.request as u, re, os, time
J = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs"); st = os.path.join(J, "chk.after")
a = int(open(st).read()) if os.path.exists(st) else 26559
j = json.load(u.urlopen("http://127.0.0.1:9890/wait?me=bb-chk&after=%d&timeout=1" % a, timeout=20))
for m in j["messages"]:
    t = json.dumps(m["body"]); tl = t.lower()
    if m["from"] == "blender-team": continue
    if re.search(r"\bneed\b|blender|request|@blender|asset\.error", tl) and "referee idle" not in tl and "referee scores" not in tl:
        print(m["id"], m["from"], m.get("type"), t[:260])
open(st, "w").write(str(j.get("last", a)))
q = open(r"C:\Users\730ri\projects\bot-team\art\QUEUE.md", encoding="utf-8").read()
print("READY", len(re.findall(r"\| READY \|", q)), "TODO", len(re.findall(r"\| TODO \|", q)), [l[:110] for l in q.splitlines() if "| TODO |" in l][:6])
print("worklog:", open(os.path.join(J, "worklog.jsonl"), encoding="utf-8").read().splitlines()[-2:])
print("next:", open(os.path.join(J, "bb_next.log")).read()[-300:] if os.path.exists(os.path.join(J, "bb_next.log")) else "-")
