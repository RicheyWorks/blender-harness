# Blender team <-> Unreal team handoff spec (v1)

Owner of this file: the Blender team (blender-harness/HANDOFF-SPEC.md, copied to art\NOTES\HANDOFF-SPEC.md).
The Unreal team: reply in art\NOTES\Blender-team-handoff.md and I'll change the spec to match. Nothing here
edits artqueue.py, ship.py, the watcher or Unreal; the Unreal-side items are requests.

## Files (all in C:\Users\730ri\projects\bot-team\art\)
| File | Writer | Reader | Purpose |
|---|---|---|---|
| QUEUE.md | both (rules of BRIEF.md) | both | The board. |
| QUEUE.md fenced block `<!-- blender-team rows: begin -->`...`end` | Blender team (**only once the Unreal team agrees**) | watcher | Batch rows #200+, status READY, only self-checked assets. |
| jobs\<Asset>.json | Blender team writes `blender`; Unreal team writes `unreal` | both | One contract per asset (below). |
| STATUS-blender.json | Blender team | watcher, lead bot | Heartbeat: `state` idle/building/fixing/paused, `group`, `progress` n/m, `at`. |
| STATUS.md, feed.jsonl, reports\ | Unreal team (watcher) | Blender team | Unchanged. The Blender team folds feed results into jobs\*.json `last_result`. |
| NOTES\<Asset>.md, NOTES\Blender-team-handoff.md | both | both | Talk. Each message ends with a `---` line; the reply goes below it. |

## jobs\<Asset>.json
```json
{"spec": 1, "asset": "Tool_Pickaxe", "kind": "Tool",
 "blender": {"blend": "...\\Tool\\Tool_Pickaxe.blend", "glb": "...\\glb\\Tool_Pickaxe.glb", "glb_sha1": "…",
             "tris": 440, "meshes": [{"name": "Tool_Pickaxe", "tris": 440, "materials": ["…_M0"], "dims_m": [0.895, 0.66, 0.11]}],
             "materials": ["…"], "built_by": "Blender team", "built_at": "2026-10-12T11:55:00",
             "selfcheck": {"ok": true, "fails": [], "checked_at": "…"}, "turntable": "...\\promo\\Tool_Pickaxe"},
 "unreal": {"shipped_at": "…", "unreal_path": "/Game/…", "unreal_tris": [422], "result": "SHIPPED|REJECTED: …|BLOCKED: …"},
 "last_result": {"at": "…", "event": "rejected", "why": "…", "detail": "…", "unreal_tris": [422]}}
```
The `blender` half is written when the row goes READY, from the saved .glb (re-read, not from memory). The watcher can
ship that exact .glb (`glb_sha1`) instead of re-exporting from Blender, so Blender doesn't have to be open or idle.

## Status meanings (requested)
- `REJECTED: <check>` means the **art** must change. Only the Blender team acts on it.
- `BLOCKED: <reason>` means the **editor** is the problem: Play running, Unreal closed or busy, socket reset, Blender has
  unsaved work. The watcher sets the row back to READY by itself when the reason clears. Nobody touches it.

## Requests to the Unreal team
1. A socket reset during the PLAYING check counts as `waiting`, not `watcher-error`.
2. BLOCKED + auto-retry as above.
3. The triangle check allows what Unreal's mesh build removes (Unreal ≤ file and ≥ 95% of it), with both counts written
   to SHIPPED. See NOTES\Tool_Pickaxe.md.
4. Write `unreal` into jobs\<Asset>.json on every attempt.
5. STATUS.md shows one line from STATUS-blender.json.

## Blender team side (built: blender-harness `python -m bharness.handoff`)
`job <Asset>` · `status <state> [group] [n/m]` · `watch [s]` (feed + NOTES replies) · `rows [--apply]` · `board`.
