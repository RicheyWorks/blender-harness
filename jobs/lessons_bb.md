
## blender-team | 2026-10-13 00:55 | Missing .blend shipped a stale mesh (island at 36 tris)
- What happened: QUEUE row 2963, the BlenderBoss island, shipped to Unreal as a 36-tri mesh. The same thing happened to 13 Art Master Flex pets, which got the wrong meshes.
- Root cause: the art-queue watcher imports from art\<Kind>\<Asset>.blend. With no .blend at that path, it exported whatever was in its live Blender scene and shipped that under our asset name.
- Fix or workaround: assets/preflight.py checks that every Blender-team READY row has its .blend and BLOCKs the row if not; addrows skips rows with no .blend. I copied the island .blend to art\Prop\, re-queued it as row 4481 (2963 SUPERSEDED), and rebuilt the 13 pets as .blend files (rows 1367-1379).
- Rule for next time: never mark a row READY with only a glb. Put the .blend at art\<Kind>\<Asset>.blend first, and run preflight before every READY batch.
- Evidence (commit, log, screenshot): blender-harness a031107 (preflight); QUEUE rows 2963 -> 4481; disk-saver's watcher-bug thread on the link; unmerged watcher fix dc79319a (unreal-team).

## blender-team | 2026-10-13 00:56 | Multi-mesh base glb: 323 assets imported, the script picked one stray part
- What happened: the BlenderBoss base reported "base ok", but no terrain showed in Unreal (09:23 PM shot). Only the props appeared.
- Root cause: Prop_Island_BlenderBoss_Base.glb held 323 separate meshes (terrain, underside, pier, water pieces). Unreal imported them as 323 StaticMesh assets, and bb_island_ue's lookup took the first StaticMesh in the folder, which was a single pier block.
- Fix or workaround: flagship.py exports the base as one joined mesh (323 parts, 25,431 faces). The UE lookup is now exact-name only, with a size guard that refuses a base under 100 m (base_cm logged: 25465).
- Rule for next time: anything placed as one actor must be exported as one mesh. Never fall back to "first asset in folder". Log and gate on the mesh bounds.
- Evidence (commit, log, screenshot): Daedalus2 9fcca073, blender-harness 35b9a90; round-3 turn 23:05 PT placed 1003/1003 with base_cm 25465; shots\blenderboss\ue_island.png before/after.

## blender-team | 2026-10-13 00:57 | Vertex colours are ignored on glb import: white ground
- What happened: after the base fix, the island ground showed in Unreal but pure white (round-3 shot 23:08 PT).
- Root cause: M_BB_Terrain coloured the terrain only through a vertex-colour attribute ("Col") wired into Base Color. glTF carries COLOR_0, but the Unreal import does not wire vertex colour into the generated material.
- Fix or workaround: replaced the vertex colours with 5 flat material slots (grass, rock, sand, dirt, shore water) assigned per face by height, slope and zone. Re-imported and re-placed the base on the round-4 turn (00:02 PT).
- Rule for next time: Unreal-bound assets carry colour in material baseColorFactor slots, not vertex colours. Check that each glb has no COLOR_0 and every material has a baseColorFactor (all 500 BBIsle props passed this check).
- Evidence (commit, log, screenshot): blender-harness c826624, Daedalus2 1d45f827; art\flagship\contest_island_v4.png (Blender render, green ground); round-4 DONE on the link 00:03 PT.

## blender-team | 2026-10-13 00:58 | __main__ guard: the bridge exec ran nothing
- What happened: our 7:14 PM editor turn sent bb_island_ue.py over the 9877 bridge and got "ok" back, but nothing was imported or placed.
- Root cause: the bridge runs the file in-process with exec, so __name__ is not "__main__". The run() call under the guard never fired.
- Fix or workaround: the script ends with RESULT = run(); print(json.dumps(RESULT)), with no guard. ue_send then gets real counts back.
- Rule for next time: bridge scripts call their entry point at module level and print a JSON result. Treat a reply with no result JSON as a failure, not a success.
- Evidence (commit, log, screenshot): Daedalus2 8dc36c6b; 7:14 PM turn and correction post on the link; same lesson in the buffffff seed list.

## blender-team | 2026-10-13 00:59 | BB_MODE env var never reached the editor process
- What happened: round 4 (00:02 PT) was meant to re-place only the base (BB_MODE=base). The script re-placed all 1003 models instead (new 1003, kept 0).
- Root cause: the env var was set in our PowerShell, and ue_send only sends the script text. The code runs inside the already-running UnrealEditor process, whose environment we never touch.
- Fix or workaround: the watcher writes the mode to %LOCALAPPDATA%\Daedalus\jobs\bb_mode.txt before sending and clears it afterwards, and bb_island_ue reads that file.
- Rule for next time: pass parameters to bridge scripts through a file or the script text itself, never through the sender's environment. Echo the mode in the result JSON so a wrong mode is visible.
- Evidence (commit, log, screenshot): Daedalus2 3d61fc41; r4turn.log result {"new": 1003, "kept": 0}.

## blender-team | 2026-10-13 01:00 | "Add Level" dialog blocked the job and the next team
- What happened: in our 22:21 make-up turn the bridge job was still "running" after 508 s, and an "Add Level" window stayed open after tidy. The next team's turn (prometheus) started with our job still in the editor.
- Root cause (most likely): open_sublevel called add_level_to_world on BlenderBossIsland while it was already streamed into DaedalusWorld, which opens a modal dialog. A modal blocks the editor's Python tick, so the job never finishes.
- Fix or workaround: only add the sublevel when it is not already in world.get_streaming_levels(); if that check fails, skip the re-add. The next turns (23:05, 00:02) finished in about 3 minutes with no dialogs.
- Rule for next time: never call an editor op that can raise a modal without checking state first. When a job overruns, post BLOCKED with the job id and leave the editor alone during the next team's turn.
- Evidence (commit, log, screenshot): Daedalus2 9631805d; link msgs 24212 (CLAIM), 24240/24241 (PARTIAL + HANDOFF), our BLOCKED post at 22:31; job job-1791868891380-17 state "running".

## blender-team | 2026-10-13 01:01 | Frozen editor after a GPU crash: no CLAIM without a live ping
- What happened: the 8:22 PM make-up turn timed out with no bridge reply. Prometheus lost its turn the same way, and we scored 0.
- Root cause: since 7:17:55 PM the editor (pid 12904) showed a modal "GPU Crashed or D3D Device Removed" dialog. The process and the 9877 socket still looked alive, but no Python ran.
- Fix or workaround: before CLAIM the watcher checks that the UnrealEditor window responds (unless it isn't visible from our session) and runs a 1+1 execute_python round-trip with a 25 s timeout ("BBPING 2"). If that fails it posts STANDING DOWN plus HANDOFF right away, and never clicks the dialog, kills or relaunches the editor. The editor was later relaunched with -d3d11 by its owner.
- Rule for next time: a socket that answers is not proof the editor is alive. Prove it with a real Python round-trip before claiming, and stand down at once if it fails.
- Evidence (commit, log, screenshot): jobs\bb_makeup3.py / bb_next.py alive(); bb_makeup3.log "alive=True ping reply: BBPING 2" (22:21:30); the 8:22 PM finding post on the link.

## blender-team | 2026-10-13 01:02 | Watcher false trigger on "skip", then a crash on bus type "claim"
- What happened: at 8:15 PM our turn watcher fired on someone else's message, then died, so no CLAIM was posted.
- Root cause: (1) the trigger regex matched loose words like "skip" (msg 23529) instead of a real handoff. (2) the watcher then called bus.send("claim", ...), but "claim" is not a valid bus message type; Bus raises ValueError, and the unhandled exception killed the process.
- Fix or workaround: strict triggers only. One is "HANDOFF -> blender-team" (or a message starting "HANDOFF blender..."). The other is a referee line from buffffff or 2hot2trot saying our turn is open. We never trigger on our own messages. CLAIM/DONE/HANDOFF go as type "note" to "*". The turn body sits in try/except with logging. A Task Scheduler supervisor (BB_Ensure, every 2 min) restarts the watcher if it dies, and never after it has fired.
- Rule for next time: test trigger regexes against the last ~200 real link messages before arming; ours matched only the real 7:11 PM "turn open" line. Send only valid bus types. A watcher must log and survive any exception.
- Evidence (commit, log, screenshot): link msg 23529 (false trigger); bharness.bus TYPES (no "claim"); jobs\bb_round2.py / bb_next.py / ensure.py; trigger test run 21:19 PT (198 msgs, 1 true hit).
