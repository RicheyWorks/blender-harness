# SPDX-License-Identifier: MIT
"""The art board (bot-team\\art\\QUEUE.md), from the Blender side.

Rules followed exactly (BRIEF.md + asset_pipeline/artqueue.py):
* only the Status and Notes cells of one row are rewritten; every other byte is kept;
* read -> compute -> re-read -> compare -> write (atomic replace), so a watcher or bot editing at the same
  moment is never overwritten;
* the same table parser as the watcher, so both sides see the same rows.

Transitions this harness may make (anything else is refused):
    TODO            -> DOING (<who>)        claim
    REJECTED: ...   -> DOING (<who>)        claim, to fix it
    DOING (<who>)   -> READY                ready, only after the judge passes and the .blend is saved
    BLOCKED: ...    -> READY                retry, after the editor-side cause is cleared (not a Blender fault)
BLOCKED is distinct from REJECTED: REJECTED = the asset broke a rule (Blender team fixes it);
BLOCKED = editor state stopped it (e.g. Unreal in Play, a dialog, a locked file). The watcher only acts on READY,
so a BLOCKED row is inert until someone retries it.

Coordination with the watcher (it shares the one Blender):
* never touch SHIPPING / SHIPPED / WAITING rows, nor another bot's DOING row;
* do no Blender file work while any row is SHIPPING (the watcher has Blender);
* never discard unsaved Blender work: opening or saving refuses if the open file has unsaved changes and is not
  this asset's own file.
"""
import datetime, json, os, re, time
from ..contract import Plugin, Action, Risk
from .bridge import run, FILESTATE
from .judge import judge, passed, first_failure
from .probe import asset as probe_asset

KINDS = ("Tool", "Item", "Mob", "Veh", "Bld", "Prop", "Sky", "Wpn")


def parse(text):
    """Identical to asset_pipeline.artqueue.parse."""
    lines = text.split("\n")
    header, rows = None, []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s.startswith("|"):
            if header is not None and rows:
                break
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if header is None:
            low = [c.lower() for c in cells]
            if "asset" in low and "status" in low:
                header = {"asset": low.index("asset"), "status": low.index("status"),
                          "notes": low.index("notes") if "notes" in low else None, "width": len(cells)}
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        if len(cells) < header["width"]:
            cells += [""] * (header["width"] - len(cells))
        rows.append({"line": i, "cells": cells, "asset": cells[header["asset"]], "status": cells[header["status"]],
                     "notes": cells[header["notes"]] if header["notes"] is not None else ""})
    return rows, header


def state(status):
    m = re.match(r"\s*([A-Za-z]+)", status or "")
    return m.group(1).upper() if m else ""


def set_row(text, asset, status, notes=None):
    """Identical to asset_pipeline.artqueue.set_row: one row's Status (and Notes), the rest byte for byte."""
    rows, header = parse(text)
    lines = text.split("\n")
    for r in rows:
        if r["asset"] == asset:
            cells = list(r["cells"])
            cells[header["status"]] = status.replace("|", "/")
            if notes is not None and header["notes"] is not None:
                cells[header["notes"]] = notes.replace("|", "/").replace("\n", " ")
            lines[r["line"]] = "| " + " | ".join(cells) + " |"
            return "\n".join(lines)
    raise KeyError(asset)


def kind_of(asset):
    k = asset.split("_", 1)[0]
    return k if k in KINDS else None


class QueueError(Exception):
    pass


class Blocked(QueueError):
    """Editor state, not the asset: retry later."""


class QueuePlugin(Plugin):
    name = "queue"

    @property
    def path(self):
        return os.path.join(self.ctx.art, "QUEUE.md")

    def read(self):
        for _ in range(5):
            try:
                with open(self.path, encoding="utf-8", newline="") as f:
                    return f.read()
            except PermissionError:
                time.sleep(0.4)
        raise PermissionError(self.path)

    def rows(self):
        return parse(self.read())[0]

    def row(self, asset):
        for r in self.rows():
            if r["asset"] == asset:
                return r
        raise QueueError("no row for %s in %s" % (asset, self.path))

    def _write(self, asset, expect, status, notes=None):
        """Change one row if, at the moment of writing, its state is still `expect` (a set of states)."""
        for _ in range(5):
            before = self.read()
            r = next((r for r in parse(before)[0] if r["asset"] == asset), None)
            if r is None:
                raise QueueError("no row for " + asset)
            if not expect(r):
                raise QueueError("%s is %r; refusing" % (asset, r["status"]))
            after = set_row(before, asset, status, notes)
            if self.read() != before:
                continue  # someone wrote meanwhile: start over
            tmp = self.path + ".bh.tmp"
            with open(tmp, "w", encoding="utf-8", newline="") as f:
                f.write(after)
            os.replace(tmp, self.path)
            self.event(asset, state(status).lower(), status=status, by=self.ctx.who)
            return status
        raise Blocked("QUEUE.md kept changing under us; try again")

    def event(self, asset, what, **detail):
        line = dict({"at": datetime.datetime.now().isoformat(timespec="seconds"), "asset": asset, "event": what}, **detail)
        with open(os.path.join(self.ctx.art, "feed.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")

    # ---------------------------------------------------------------- read side

    def board(self):
        out = {}
        for r in self.rows():
            out.setdefault(state(r["status"]) or "?", []).append(r["asset"])
        return out

    def mine(self):
        tag = "DOING (%s)" % self.ctx.who
        return [r["asset"] for r in self.rows() if r["status"].strip() == tag]

    def watcher_busy(self):
        return [r["asset"] for r in self.rows() if state(r["status"]) == "SHIPPING"]

    # ---------------------------------------------------------------- transitions

    def claim(self, asset, notes=None):
        if not kind_of(asset):
            raise QueueError("%s: name is not Kind_Name" % asset)
        return self._write(asset, lambda r: state(r["status"]) in ("TODO", "REJECTED"),
                           "DOING (%s)" % self.ctx.who, notes)

    def blend_path(self, asset):
        return os.path.join(self.ctx.art, kind_of(asset), asset + ".blend")

    def guard_blender(self, asset):
        """Raise Blocked unless Blender may be used for this asset now. Returns the file state."""
        busy = self.watcher_busy()
        if busy:
            raise Blocked("the watcher is shipping %s; Blender is in use" % ", ".join(busy))
        fs = run(self.ctx.bridge, FILESTATE)
        own = os.path.normcase(os.path.abspath(self.blend_path(asset)))
        if fs["dirty"] and fs["file"] and os.path.normcase(os.path.abspath(fs["file"])) != own:
            raise Blocked("Blender has unsaved work in %s; save it first (never discarded)" % fs["file"])
        return fs

    def open(self, asset):
        """Open the asset's .blend, or a new empty file if it has none. No modals: EXEC, load_ui=False."""
        fs = self.guard_blender(asset)
        p = self.blend_path(asset)
        if fs["dirty"] and not fs["file"]:
            raise Blocked("Blender has an unsaved untitled file; save it first (never discarded)")
        if os.path.exists(p):
            code = "import bpy\nbpy.ops.wm.open_mainfile('EXEC_DEFAULT', filepath=%r, load_ui=False)\nresult=bpy.data.filepath" % p
        else:
            code = ("import bpy\nbpy.ops.wm.read_homefile('EXEC_DEFAULT', use_empty=True, load_ui=False)\n"
                    "c=bpy.data.collections.new(%r); bpy.context.scene.collection.children.link(c)\nresult=''" % asset)
        return run(self.ctx.bridge, code)

    def save(self, asset):
        """Save the open file as art\\<Kind>\\<Asset>.blend (no file browser)."""
        self.guard_blender(asset)
        p = self.blend_path(asset)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return run(self.ctx.bridge, "import bpy\nbpy.ops.wm.save_as_mainfile('EXEC_DEFAULT', filepath=%r, check_existing=False)\n"
                                    "result={'file': bpy.data.filepath, 'dirty': bpy.data.is_dirty}" % p)

    def ready(self, asset, turntable=0, notes=None):
        """Judge -> (turntable) -> save -> READY. Refuses unless the row is ours and every check passes."""
        tag = "DOING (%s)" % self.ctx.who
        if self.row(asset)["status"].strip() != tag:
            raise QueueError("%s is not %s" % (asset, tag))
        self.guard_blender(asset)
        checks = judge(asset, probe_asset(self.ctx.bridge, asset))
        if not passed(checks):
            return {"ready": False, "failed": first_failure(checks), "checks": checks}
        shots = []
        if turntable:
            from .render import RenderPlugin
            shots = RenderPlugin(self.ctx).turntable(asset, n=turntable)
        saved = self.save(asset)
        if saved["dirty"]:
            raise Blocked("save did not stick: " + str(saved))
        size = next((c["detail"] for c in checks if c["check"] == "size (info)"), "")
        tris = next((c["detail"] for c in checks if c["check"] == "triangle budget"), "")
        status = self._write(asset, lambda r: r["status"].strip() == tag, "READY",
                             notes if notes is not None else "judged ok: %s tris, %s" % (tris.split(" ")[0], size))
        return {"ready": True, "status": status, "blend": saved["file"], "turntable": shots, "checks": checks}

    def retry(self, asset):
        return self._write(asset, lambda r: state(r["status"]) == "BLOCKED", "READY")

    def block(self, asset, reason):
        """Mark a row BLOCKED: <reason> (editor state, not the asset). Only from READY or our own DOING."""
        tag = "DOING (%s)" % self.ctx.who
        return self._write(asset, lambda r: state(r["status"]) == "READY" or r["status"].strip() == tag,
                           "BLOCKED: " + reason)

    def actions(self):
        return [
            Action("board", self.board, Risk.READ, "rows grouped by state"),
            Action("mine", self.mine, Risk.READ, "rows DOING by this harness's name"),
            Action("claim", self.claim, Risk.FILE, "TODO/REJECTED -> DOING (who)", ["asset", "notes?"]),
            Action("open", self.open, Risk.FILE, "open the asset's .blend (refuses over unsaved work)", ["asset"]),
            Action("save", self.save, Risk.FILE, "save as art\\<Kind>\\<Asset>.blend", ["asset"]),
            Action("ready", self.ready, Risk.FILE, "judge, turntable, save, then DOING -> READY", ["asset", "turntable?"]),
            Action("retry", self.retry, Risk.FILE, "BLOCKED -> READY", ["asset"]),
            Action("block", self.block, Risk.FILE, "READY/our DOING -> BLOCKED: reason", ["asset", "reason"]),
        ]
