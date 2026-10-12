"""The suite output convention (shared with the Unreal connector harness):
one `PASS <label>` / `FAIL <label>  <detail>` line per check, `n/m` as the LAST line, exit 0 only if n == m."""
import sys, traceback


class Checks:
    def __init__(self):
        self.n = self.m = 0

    def __call__(self, label, ok, detail=""):
        self.m += 1
        if ok:
            self.n += 1
        print(("PASS %s" % label) if ok else ("FAIL %s  %s" % (label, detail)), flush=True)
        return ok

    def raises(self, label, exc, fn):
        try:
            fn()
        except exc as e:
            return self(label, True)
        except Exception as e:
            return self(label, False, "raised %r" % e)
        return self(label, False, "did not raise")

    def done(self):
        print("%d/%d" % (self.n, self.m), flush=True)
        sys.exit(0 if self.n == self.m and self.m > 0 else 1)
