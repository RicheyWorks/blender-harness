"""Run every suite in parallel; judge each from its exit code AND its last `n/m` line.

  python -m harness.run_all [-j 3] [--live] [--raise-floors] [--no-ledger]
Marks: ok | FAIL (exit != 0) | FAIL* (exit 0 but a FAIL line or n < m) | SHORT (m < floor) | EMPTY (no n/m line).
Last line: ok_suites/total_suites. Exit 0 only when every suite is ok. Live suites need --live (real Blender)."""
import concurrent.futures as cf, json, os, re, subprocess, sys
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)   # Windows: never flash a console
from harness.ledger import record

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "harness", "suites.json")


def run(s):
    p = subprocess.run([sys.executable, "-m", s["module"]] + s.get("args", []), cwd=ROOT, capture_output=True, creationflags=NOWIN,
                       text=True, timeout=s.get("timeout", 900), env=dict(os.environ, PYTHONPATH=ROOT))
    lines = p.stdout.strip().splitlines()
    m = re.match(r"^(\d+)/(\d+)$", lines[-1].strip()) if lines else None
    got, total = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
    if not m: mark = "EMPTY"
    elif p.returncode: mark = "FAIL"
    elif got < total or any(l.startswith("FAIL") for l in lines): mark = "FAIL*"
    elif total < s["floor"]: mark = "SHORT"
    else: mark = "ok"
    return dict(name=s["name"], floor=s["floor"], got=got, total=total, rc=p.returncode, mark=mark,
                fails=[l for l in lines if l.startswith("FAIL")][:10], tail=lines[-2:] + p.stderr.strip().splitlines()[-3:])


def main(a=sys.argv[1:]):
    j = int(a[a.index("-j") + 1]) if "-j" in a else 3
    spec = json.load(open(SPEC))
    suites = [s for s in spec["suites"] if "--live" in a or not s.get("live")]
    with cf.ThreadPoolExecutor(j) as ex:
        res = list(ex.map(run, suites))
    for r in res:
        print("%-6s %-9s %d/%d (floor %d)%s" % (r["mark"], r["name"], r["got"], r["total"], r["floor"],
              "".join("\n         " + f for f in r["fails"]) if r["mark"] != "ok" else ""))
        if r["mark"] in ("FAIL", "EMPTY") and not r["fails"]:
            print("         " + " | ".join(r["tail"]))
    ok = sum(r["mark"] == "ok" for r in res)
    if "--raise-floors" in a and ok == len(res):
        for s in spec["suites"]:
            for r in res:
                if r["name"] == s["name"]: s["floor"] = max(s["floor"], r["total"])
        json.dump(spec, open(SPEC, "w"), indent=1)
    if "--no-ledger" not in a:
        record("runs", "live" if "--live" in a else "standin", {"ok": ok, "of": len(res), "suites": res})
    print("%d/%d" % (ok, len(res)))
    return 0 if ok == len(res) else 1


if __name__ == "__main__":
    sys.exit(main())
