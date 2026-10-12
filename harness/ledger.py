"""ledgers/<name>.json = {"entries": {key: {..., "at": epoch}}}. A number a tool can compute is never typed by hand."""
import json, os, time
ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ledgers")


def record(name, key, entry):
    os.makedirs(ROOT, exist_ok=True)
    p = os.path.join(ROOT, name + ".json")
    data = {"entries": {}}
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    data["entries"][key] = dict(entry, at=int(time.time()))
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=1, sort_keys=True); f.write("\n")
