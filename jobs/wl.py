import json, os, sys, time
p = os.path.join(os.environ["LOCALAPPDATA"], "Daedalus", "jobs", "worklog.jsonl")
open(p, "a", encoding="utf-8").write(json.dumps({"at": time.strftime("%H:%M:%S"), "kind": sys.argv[1], "text": " ".join(sys.argv[2:])}) + "\n")
