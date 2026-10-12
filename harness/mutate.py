"""Mutation testing: break the harness on purpose; the named suite must go red (killed).

  python -m harness.mutate [-j 4] [--list] [--only N]
Each mutant: copy bharness/ + harness/ to a temp dir, require the `old` anchor exactly once (else inconclusive),
replace it, run only the named suite there. SURVIVED = the suite stayed green = write a new check."""
import concurrent.futures as cf, os, shutil, subprocess, sys, tempfile
from harness.ledger import record

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MUTANTS = [
    ("the risk ceiling is ignored", "bharness/contract.py", "if a.risk > self.ceiling:", "if False:", "harness.test_contract"),
    ("refusals are not ledgered", "bharness/contract.py", 'self.ledger[action_id] = "refused"', "pass", "harness.test_contract"),
    ("accounting ignores UNACCOUNTED", "bharness/contract.py", '"balanced": "UNACCOUNTED" not in buckets and not stray', '"balanced": True', "harness.test_contract"),
    ("queue writes skip the re-read guard", "bharness/plugins/queue.py", "if self.read() != before:", "if False:", "harness.test_queue"),
    ("claim takes any row", "bharness/plugins/queue.py", 'lambda r: state(r["status"]) in ("TODO", "REJECTED")', "lambda r: True", "harness.test_queue"),
    ("the watcher's SHIPPING is ignored", "bharness/plugins/queue.py", "        if busy:\n", "        if False:\n", "harness.test_queue"),
    ("unsaved work is not protected", "bharness/plugins/queue.py", 'if fs["dirty"] and fs["file"] and', 'if False and', "harness.test_queue"),
    ("ready skips the judge", "bharness/plugins/queue.py", "if not passed(checks):", "if False:", "harness.test_queue"),
    ("file ops open modals", "bharness/plugins/queue.py", "open_mainfile('EXEC_DEFAULT'", "open_mainfile('INVOKE_DEFAULT'", "harness.test_queue"),
    ("save opens a file browser", "bharness/plugins/queue.py", "save_as_mainfile('EXEC_DEFAULT'", "save_as_mainfile('INVOKE_DEFAULT'", "harness.test_queue"),
    ("BLOCKED rows can be claimed", "bharness/plugins/queue.py", 'in ("TODO", "REJECTED")', 'in ("TODO", "REJECTED", "BLOCKED")', "harness.test_queue"),
    ("set_row rewrites Notes always", "bharness/plugins/queue.py", "if notes is not None and header", "if header", "harness.test_queue"),
    ("judge ignores the triangle budget", "bharness/plugins/judge.py", "tris <= cap", "True", "harness.test_judge"),
    ("judge passes an empty asset", "bharness/plugins/judge.py", 'add("has meshes", len(objs) > 0', 'add("has meshes", True', "harness.test_judge"),
    ("judge ignores scale", "bharness/plugins/judge.py", "abs(s - 1) > 1e-4", "False", "harness.test_judge"),
    ("client drops params", "bharness/client.py", '"params": params', '"params": {}', "harness.test_client"),
    ("client reads one chunk only", "bharness/client.py", "while not buf.endswith(b\"\\n\"):", "for _ in range(1):", "harness.test_client"),
    ("turntable action is dropped", "bharness/plugins/render.py", 'Action("turntable"', 'Action("turntable_x"', "harness.walk"),
]


def one(i):
    name, rel, old, new, suite = MUTANTS[i]
    d = tempfile.mkdtemp(prefix="bhmut-")
    try:
        for sub in ("bharness", "harness"):
            shutil.copytree(os.path.join(ROOT, sub), os.path.join(d, sub), ignore=shutil.ignore_patterns("__pycache__"))
        p = os.path.join(d, rel); src = open(p, encoding="utf-8").read()
        if src.count(old) != 1:
            return dict(name=name, verdict="inconclusive", detail="anchor found %d times" % src.count(old))
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
        args = ["--no-ledger"] if suite == "harness.walk" else []
        try:
            r = subprocess.run([sys.executable, "-m", suite] + args, cwd=d, capture_output=True, text=True, timeout=300,
                               env=dict(os.environ, PYTHONPATH=d))
        except subprocess.TimeoutExpired:
            return dict(name=name, verdict="killed", detail="timeout")
        fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
        return dict(name=name, verdict="killed" if r.returncode else "SURVIVED",
                    detail=(suite + ": " + (fails[0] if fails else (r.stderr.strip().splitlines() or ["rc=%d" % r.returncode])[-1]))[:200])
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main(a=sys.argv[1:]):
    if "--list" in a:
        for i, m in enumerate(MUTANTS): print(i, m[0], "->", m[4])
        return 0
    idx = [int(a[a.index("--only") + 1])] if "--only" in a else range(len(MUTANTS))
    j = int(a[a.index("-j") + 1]) if "-j" in a else 4
    with cf.ThreadPoolExecutor(j) as ex:
        rows = list(ex.map(one, idx))
    for r in rows:
        print("%s %s  %s" % ("PASS" if r["verdict"] == "killed" else "FAIL", r["name"], r["detail"]))
    k = sum(r["verdict"] == "killed" for r in rows)
    if "--only" not in a:
        record("mutants", "harness", {"mutants": len(rows), "killed": k,
               "survived": sum(r["verdict"] == "SURVIVED" for r in rows),
               "inconclusive": sum(r["verdict"] == "inconclusive" for r in rows), "rows": rows})
    print("%d/%d" % (k, len(rows)))
    return 0 if k == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
