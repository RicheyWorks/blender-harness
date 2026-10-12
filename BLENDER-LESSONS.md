# Blender lessons: driving Blender through the Claude Blender Bridge

Found live on BLACKBEARD (Blender 4.3.1, add-on 1.0.2), 2026-10-12. Add to it when something new breaks.
Companion to `Daedalus2/docs/AUTOMATION-LESSONS.md` (Unreal and Windows).

## The bridge
1. **Command names differ from the MCP tool names.** On the wire it's `ping` and `execute_code`; the MCP tools are
   called `blender_status` and `execute_python`. An unknown command gets back the list of known ones.
2. `execute_code` returns `{stdout, result}`, where `result` is the code's own `result` variable (made JSON-safe with `repr`).
   Errors come back as `status: error` with a traceback, and the bridge stays up.
3. **One main thread, one job at a time.** Four clients at once all succeed, but they run one after another, and the UI
   freezes while a job runs. The art-queue watcher shares this Blender: never do Blender file work while a row is
   `SHIPPING`.
4. **A client timeout does not cancel anything.** Blender finishes the job; the next call waits for it, and the bridge's
   own limit is 1800 s. Keep calls short, and split big work into steps.
5. Images come back only as base64 PNG (`viewport_screenshot` has no file option; `render_image` takes
   `output_path` and also returns base64). Large replies are fine (2-3 MB tested).
6. `render_image` fails clearly when the scene has no camera.

## Speed (measured)
7. Linking 1,000 objects that share one mesh takes 76 ms; 200 `bpy.ops.mesh.primitive_cube_add` calls take 8.9 s. **Use
   `bpy.data` + `bmesh`, not operators**, in loops.
8. ping/scene info are about 50 ms; viewport shot about 0.4 s; EEVEE render at 50% about 0.5 s on the default scene.

## Never open a modal: outside watchers can't answer Blender's dialogs
9. Blender's dialogs are mostly in-process UI (file browser, "save changes?", popups), so a window watcher sees few
   of them. **Prevent them in Python:** always call operators with `'EXEC_DEFAULT'`, never `INVOKE_DEFAULT`; pass
   `filepath=` (no file browser); `open_mainfile(..., load_ui=False)`; `save_as_mainfile(..., check_existing=False)`.
   The test suite and the mutants enforce this for the queue's file operations.
10. **Check `bpy.data.is_dirty` before opening or creating a file.** If there's unsaved work in another file, stop
    (BLOCKED) and never discard it. An unsaved untitled file counts as unsaved work too.
11. Context-sensitive ops (`view3d.*`, screenshots) need a window; they fail headless (`blender -b`).
12. A `.blend` load drops non-persistent timers and handlers (the add-on's 1.0.2 fix); make new ones `persistent`.

## The board
13. Change only the Status and Notes cells of one row, with read → compute → re-read → compare → atomic replace.
    Never write with `open(path, "w").write(f(read()))`: `open` truncates the file before `read()` runs (this
    bit our own test).
14. `BLOCKED: <why>` = editor state (Unreal in Play, a dialog, a locked file), not the asset. `REJECTED: <check>` =
    the asset broke a rule. The watcher acts only on READY, so a BLOCKED row waits until someone runs `queue.retry`.
15. 2026-10-12: Prop_PipelineCheck was REJECTED "every file mesh became an Unreal static mesh (2 vs 0)" while it
    passes every brief rule on the Blender side; Unreal was in Play (PIE). That's a BLOCKED case on Claude's side.

## Running on the PC
16. Device-link calls die at 60 s. Long jobs go through `blender-job.ps1 -Start` (WMI), then `-Wait` in later calls.
17. The suite convention: `PASS`/`FAIL` lines and `n/m` last. `run_all` marks a suite EMPTY without it.

## Building real assets (2026-10-12, priority-1 tools)
18. `MeshPolygon` has `.vertices`, not `.verts` (that's bmesh). A build that dies halfway leaves an untitled scene with
    changes in Blender, and the never-discard guard then (rightly) blocks the next `open`. `assets/tools.py` now drops
    its own half-built scene on failure; `assets/_reset_own.py` clears one only if it holds nothing but that asset.
19. Only the Status and Notes cells may change, so assets with no QUEUE.md row (Tool_Shovel, Tool_Axe, Wpn_Blaster,
    Wpn_Sword today) are built, judged, rendered and saved but not flipped; someone has to add their rows.
20. Building from bevelled boxes in one bmesh, 1 object and up to 3 slots, gives 300-450 tris per tool, far under 3k.
    Hex colours go in linear (`(c/255)**2.2`); emission on the last slot for glowing heads.
21. READY rows wait while Unreal is in Play: STATUS.md says "Waiting on: Unreal to leave Play mode". Not ours to clear.
22. Batch builds go through `blender-job.ps1 -Start -Run "assets.runner build <specs module>"`: 56 tools took about 2 minutes,
    longer than one 60 s call. Every asset is judged, exported to .glb and self-checked before it is saved.
23. Rendering a composed scene from collection instances (empties) keeps the source assets untouched; exclude the
    source collections from the view layer, and the instances still render.
