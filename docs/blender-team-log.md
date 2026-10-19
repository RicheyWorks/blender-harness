# Blender team (Blender Boss): status and pilot log
Repo: RicheyWorks/blender-harness (BLACKBEARD and origin in sync, HEAD 67ee763). Team link: 127.0.0.1:9890. Never launches Unreal. Jobs are hidden and run one at a time.

## Unreal feature pilots (Blender side, sent 2026-10-12 about 1:25 PM PT)
All output is in `bot-team\art\pilots\`. It was built headless with `blender -b --factory-startup` (pilots/pilots_blender.py), and the GLBs were checked with our glb reader.
| Pilot | Files | Blender-side check | Link msg | Unreal result |
|---|---|---|---|---|
| Rig + clips | rig/Mob_BlightSlime_Rig.glb (3 joints), rig/Mob_StoneKnight_Rig.glb (7 joints) | 1 skin, animations Idle/Walk/Attack/Hit | 4542 | pending |
| Lumen emissive and slots | lumen/Prop_Pilot_LumenLamp.glb | M_Base/M_Accent/M_Emissive; emissive + KHR_materials_emissive_strength present | 4544 | pending |
| Niagara VFX | vfx/FX_Quad, FX_Ring, FX_Cone, FX_Shard .glb; T_FX_Smoke/Spark/BlightPop_4x4.png | 2 to 32 tris, additive emissive material; 512 px 4x4 flipbooks | 4546 | pending |
| Sequencer | sequencer/Seq_Pilot_Orbit.glb + .camera.json | 1 camera, 2 animations (camera orbit, cube bob), 120 f at 24 fps | 4548 | pending |

## Open items
- [ ] QUEUE.md row 619 Prop_Herb_Chamomile stuck in SHIPPING since about 1:00 PM PT (asked 4521, 4570). It no longer blocks Blender team builds (headless). It does block the Unreal team draining 187 READY.
- [x] Reply to Codex (pootscoot) on saved-glb.patch: confirmed the producer contract, said ownership (1) to (4) belongs to the Unreal team, and flagged Chamomile as evidence of the stranded-SHIPPING risk (4538).
- [x] Mesh-data names now equal object/node names, so there is no more .001 in GLBs (67ee763).
- [x] Jobs hidden (c900b6c). Feeds: landscape heightmaps and FEEDS.md (068bef7).
- [ ] Hero size-check fix (Unreal team side), then re-send Mob_Realm_Party_Hero.
- [ ] UCX collision: waiting for the Unreal team to confirm that glTF import keeps UCX meshes (4523).

## Speed-up (2026-10-12, 1:25 to 1:32 PM PT), HEAD 0be8509
- Checked first: the Unreal team's watcher uses the GUI Blender on 9876. It opens `<Kind>\<Asset>.blend` and exports. So the Blender team now builds in a separate hidden `blender -b` (assets/headless.py with LocalBridge) and skips only the asset that is SHIPPING.
- Throughput, before: about 6.9 assets/min with waits for each ship result. While row 619 was stuck: 0/min (all builds paused). After: **185 assets in 2.07 min, about 89 assets/min**, with 0 errors.
- asset.ready now goes out in bursts of 10, with no waiting for each result. Batch shipping proposed to the Unreal team (link msg 4570: asset.ready.batch, ship_saved path, long-poll).
- Post-job hook: blender-job.ps1 runs `bharness.tidy` (closes extra Blender windows; skipped while the watcher ships), then `bot-team\hooks\post-job.ps1` or $DAEDALUS_POST_JOB_HOOK if 2Hot2Trot publishes one.
- Queue: 565 SHIPPED, 187 READY waiting on the Unreal team, 1 SHIPPING (619, stuck), 2 REJECTED (99 superseded test crate; 391 Hero, false size check on their side). The catalog is fully built: 755 GLBs. Every GLB has been sent.
- [x] Flora wave 2 complete: 210 of 210 built and sent.

## Wave 3 and self-ship (2026-10-12, 1:40 to 1:52 PM PT), HEAD 6eff70e
- Wave 3 (assets/wave3.py), 234 assets, all built headless: 30 town (16 buildings, 14 street props), 36 trees (12 species x 3 stages), 20 Dragon Warrior (towns, inn, shops, 2 castles, shrine, bridges, overworld tiles, chest, throne), 28 animals, 40 plants x growing/harvested/item. The second run went at 97 assets/min; asset.ready was sent in bursts of 10. Catalog total: 974. Contact sheets: /workspace/wave3_sheet_1.png and _2.png (box).
- Self-ship tool: bharness/selfship.py. It imports our READY .glb into the editor that is ALREADY open, via 9877, using the Unreal team's sides.UNREAL_IMPORT as a read-only library, to /Game/Daedalus/Art/<Kind>/<Asset>.
  - Row flow: READY -> "SHIPPING (Blender team)" -> SHIPPED (tris, size) only if Unreal matches the glb, otherwise back to READY.
  - It posts link notes before (exact rows) and after (results). It never launches an editor, never stops Play, and never touches row 619.
  - Watchdog (hidden, `bharness.selfship --loop`, 120 min): fires only if the editor is not in Play AND the watcher hasn't reduced READY within 60 s. Then it runs the UI-cleanup hook if 2Hot2Trot publishes one.
- Self-ship result so far: **0 shipped, none attempted**. The open editor (pid 53716, DaedalusRealm) has been in Play mode since 1:25 PM PT, and Unreal can't save assets during Play. Neither the watcher nor we can ship until Play ends. Asked on the link who owns the Play session (msg 8988).
- Queue: 565 SHIPPED, 187 READY, 1 SHIPPING (619), 2 REJECTED. The wave 3 asset.ready messages are on the link, but no rows have been added yet (the Unreal team's side is idle).
- Incident: a second headless run briefly overlapped the first. It skipped existing files and exited on its own; there was no damage and only one job was left running. RAM free stayed at about 3.9 GB.

## Wave 4: gameplay loop (2026-10-12, 2:15 to 2:25 PM PT), HEAD 1d9e9d6
- Read Buffffff's broadcasts on the link (10019 gameplay loop, 10021 basics checklist) and the board BOARD/game-basics.md. Checked the catalog for duplicates: Item_Bar_* (Copper, Iron, Gold, Starmetal), Prop_Furnace/Anvil/Cauldron and the tiered tools already existed, so they were not rebuilt.
- Built 117 assets headless at 91 assets/min (assets/wave4.py), using the ore hexes from daedalus-core BlockColors.java:
  - 21 ore nodes: Coal, Copper, Iron, Gold, Crystal, Heartstone, Starmetal, each Small, Large and Depleted.
  - 17 stations: cooking pot (plus lit), campfire spit, stone stove, prep table, brewing still, smelter (plus lit), forge (plus lit), bellows, crucible, ingot mould, quench trough, rare-metal refinery, starmetal anvil, ore crate.
  - 57 modular Ark parts: 19 modules (hull bow/mid/stern, deck, railing, mast, sail, rudder, helm, cabin, balloon, propeller, engine, anchor, wings L/R, shield-core housing, dock clamp, lantern post) in Wood, Iron and Starmetal, on a 2 m grid.
  - 9 tools: sickle in 5 tiers, tongs, prospector, ladle, chisel.
  - 13 metal items: 7 nuggets, 5 bar stacks, 1 Heartstone bar.
- QUEUE.md rows 1054 to 1170 were appended by us (Buffffff's instruction): status READY, Notes tagged `[wave4 block n/117]`, written with a re-read/compare before writing. The block sits INSIDE the table, because the parser ends the table at the first non-`|` line. Re-parsed afterwards: all 117 rows are visible. No asset.ready was sent, so the link adds no duplicate rows. The row list was posted on the link (10869, 10870).
- The 42 BLOCKED rows (link 10873): 18 WinError 10061 (Unreal bridge refused; editor closed or restarting), 2 WinError 10054 (connection reset; editor busy), 21 "'bool' object is not subscriptable", 1 "'meshes'". All are on the watcher/Unreal side, with a 60 s retry; the assets are fine. The bool/meshes errors look like a bridge reply that is not a dict (editor startup or Play), so a guard in artqueue is suggested.
- Swarm rules: CLAIM posted for board items #4 (chest), #5 (DONE), #8 (DONE), #13 (DONE) and #16 (NPC crew models, next). Hidden heartbeat every 5 min (bharness.heartbeat, 4 h).
- Self-ship watchdog STOPPED. It only checked "not in Play"; the editor now runs 20-min turns rotated by 2Hot2Trot. NEED posted (10872): how is the turn published, and where is tidy.ps1? It restarts once we can read our turn.
- Contact sheet: /workspace/wave4_sheet.png.

## Wave 5: board #4 chests + #16 ark crew (2026-10-12, 2:23 to 2:28 PM PT), HEAD 4d3de8f
- 12 crew: Mob_Crew_Captain, Navigator, Engineer, Cook, Smith, Botanist, Merchant, Medic, Deckhand, Lookout, Shipwright, Kid. Parts _Body/_Head/_ArmL/_ArmR/_LegL/_LegR with role props; 616 to 748 tris.
- 6 chests: Prop_Chest_Wood, Iron, Gold, Starmetal, Large_Wood, Ark_Locker. Parts _Base + _Lid (hinge pivot at the back); 440 tris.
- Rigged skinned GLBs (pilots/rig_batch.py, headless): art/pilots/rig/<A>_Rig.glb. Crew: 7 joints, clips Idle/Walk/Attack/Hit. Chests: 3 joints, clips Idle/Open/Close. All 18 verified in the GLB.
- QUEUE rows 1171 to 1188 appended (READY, [wave5 block]). DONE + HANDOFF posted (link 11064).
- The Blender team announced on the link that it takes requests from all three teams, first-come-first-served with round-robin (11056). No NEED addressed to the Blender team yet.
- Editor turns: 2hot2trot published the protocol (link 10357: claim 'editor-slot <task>', 20-min turns, 'release' to hand off; the Unreal team holds the slot). Self-ship is not needed right now: the watcher is draining at about 2 assets/s since Play was stopped. If it stalls, we claim a slot.
- The Unreal team confirmed the Hero false-REJECT is fixed and re-queued (11001).

## 2026-10-12 14:35 PT: autowave + 20 tasks
- autowave.py deployed (commit 4fca984), running hidden via WMI pid 61548 (--loop --floor=100 --hours=6).
- auto1: 60 Prop_Island_* rows 1189-1248, all SHIPPED. Watcher drains about 2/s, so READY stays near 0 and refill runs nonstop.
- Posted CLAIM 1/20..20/20 on the link; DONE 14/20 posted.

## 2026-10-12 ~14:45 PT: post-crash check (D3D12 DXGI_ERROR_INVALID_CALL, link msg 12417)
- Checked QUEUE rows 1054+ against C:\Unreal\DaedalusRealm\Content\Daedalus\Art: 476 SHIPPED. auto1-auto6 present (multi-part assets as _M#/_Part uassets).
- Reset 8 to READY (SHIPPED but no uasset): 1367-1374 (pet items/mobs).
- Scan: no NaN or huge bounds, no row over 50k tris (auto rows max 352), largest glb 0.67 MB, one embedded texture (Creature_CaneCorso). The crash isn't from our assets.
- Autowave alive (cmd pid 61548), waves auto1-auto8 done; READY now builds up while the editor is down.

## 2026-10-12 ~15:15 PT: island contest entry
- Registered on the link: CLAIM island:BlenderBoss.
- assets/flagship.py builds Prop_Island_Flagship_BlenderBoss (240 m, 502 placed catalog items, 183 unique), headless and hidden, about 30 s.
- glb in art\glb (6.2 MB), .blend + lore/herb/survival doc in art\flagship. QUEUE row 2963 READY, placed after the team requests.
- Hero shot at /workspace/contest_island.png.

## 2026-10-12 ~15:30 PT: island polish
- Mob_Crew_Cook removed from stations; now an NPC working Prop_CookingPot_Lit on the plaza. Stations exclude Mob_/Item_/BBIsle/Decor.
- Polar terrain mesh, 256 segments: smooth circular rim. Camera reframed, whole ark in frame. Rendered alone (no other Blender job running). /workspace/contest_island.png.
- New unique island-only models: bbkit.py (25 structural families) + bbisle.py, batch 0 = 120 Prop_BBIsle_* built, 0 fails. 120/500. All placed on the island (623 placed, 304 unique).
- autowave: new "decor" category (25 bbkit families x 12 styles, seeded per style so the shapes differ), creature/flora/island recolour waves capped, waves max 60.

## 2026-10-12 ~15:42 PT: island unique 500/500
- Prop_BBIsle_* batches 1-4 built (380, 0 fails), 500/500 total. A BLACKBEARD disconnect killed batch 2 partway, so the rest ran in a detached hidden ps1 that waits until no other headless Blender is running.
- Zoned placement with spacing: farm by the livestock pen, village ring around the plaza, monuments along an outer ring (gap 3.5-6 m). Island: 1003 placed, 684 unique, glb 15 MB.
- Final hero shot: /workspace/contest_island.png.

## 2026-10-12 ~15:45 PT: island requeue + watcher bug check
- Row 2963 marked SUPERSEDED (it had shipped as 36 tris / 2.20 m, wrong). New row 4481 READY: v2 island glb, 1003 placed, 445,294 tris.
- Checked 231 shipped rows (191 autowave across all categories + 40 Prop_Island_*) against art\glb triangle counts: all match, uasset hashes all distinct. Only the multi-object island row was affected.
- Posted BLOCKED + evidence to @2hot2trot / @unreal-team on the link (watcher owner).

## 2026-10-12 ~16:30 PT: island 4481 fix path
- Posted CORRECTION on the link: the 2963 bad import was our missing art\Prop\<asset>.blend, not a watcher bug.
- Preflight added (assets/preflight.py; addrows skips rows with no .blend), commit a031107. Current READY rows missing a .blend: 0.
- Island .blend copied to art\Prop (74 MB). Watcher not draining yet at 16:30 (READY 1869); buffffff asked unreal-team to merge ceo/watcher-glb-asis.
- Hidden island4481.py (pid 14428): when READY<=150, sets 4481 READY, waits for SHIPPED, checks ~445k tris, posts DONE + 2963 replace ask, or BLOCKED. Log: %LOCALAPPDATA%\Daedalus\jobs\island4481.log.

## 2026-10-12 ~17:55 PT: island turn-in (BLACKBEARD offline)
- Water chain coded into flagship.py (spring, rain catchment, cistern, aqueduct, channels to herb spiral/orchard/meadow, waterwheel, 4 troughs, well). Also exports Base glb + layout.json. NOT rendered/built yet: BLACKBEARD offline.
- Daedalus2 main: 1233056 (builder + manifest), 95b330d (docs/islands/BlenderBoss.md + tools/islands/blenderboss/bb_island_ue.py + bb_turn.ps1). Hero PNG not pushed (binary).
- SendToAgent to Buffffff: not available to this subagent; draft handed to parent.

## 2026-10-12 18:45-19:30 PT
- Heartbeat restarted (pid 39852, 12 h / 5 min). 13 AMF pet assets were stale scene exports (Cairn/Hopper); rebuilt from NOTES\amf\t20 into art\<Kind>\*.blend + glb and re-queued READY (rows 1367-1379). HANDOFF to AMF.
- Water chain built; layout.json + hero pushed to Daedalus2 a6788b55; bb_turn.ps1 paths fixed e5430f2a; 500 BBIsle rows queued 5796-6295.
- Editor turn 19:14-19:24 FAILED: bb_island_ue.py ran run() only under __main__ (ue_send runs in-process), so nothing was placed. BLACKBEARD then dropped 19:15-19:24. Posted HANDOFF to 2hot2trot + CORRECTION + NEED make-up turn. Fixed 8dc36c6b.
- Duplicate risk: hidden turn-watcher triggered at 19:14:15 on referee msg 23107 and may have posted a 2nd CLAIM before I killed it.
- AMF: RedPanda re-sent; Prop_PetWaterBowl_V2-4 + Prop_HayBale_V2-4 built (0 fails), rows 6296-6301 READY; HANDOFF posted.

## 2026-10-12 ~20:15 PT: make-up turn prep
- Dry check OK: layout 1003 placements / 685 unique, 404 already in UE, 281 to import, 0 missing glb; base glb now one joined mesh (193 parts, 24,651 faces); ue_send + tidy paths exist.
- bb_island_ue.py 42b5b858: ends Play first, chunked imports time-boxed to 200 s, mesh cache, save_all_dirty_levels, HighResShot to bot-team\shots\blenderboss\ue_island.png.
- Turn watcher bb_makeup.py armed 19:59 (pid 48460, after msg 23266, 6 h). Not triggered by 20:11.
- 2hot2trot NEED (23509): the Blender GUI connector on 9876 is down. Not reopened (RAM); asked Richey.

## 2026-10-12 20:15-20:50 PT: make-up turn
- First watcher's trigger matched a 'skip' in referee msg 23529 (unreal-team's turn). Process then died because Bus.send("claim") is not a valid type (ValueError). Fixed: type "note"; triggers = HANDOFF to blender-team, explicit referee "blender-team turn open", or 20:22:30 timer (primary) with no unreal-team CLAIM.
- 20:22:30 timer fired. CLAIM 23557, bb_turn ran 510 s, the bridge never returned. Tidy ran. HANDOFF prometheus 23600 at 20:31. Referee: scored 0, nothing saved.
- Root cause: the editor (pid 12904) has had a modal 'GPU Crashed or D3D Device Removed' dialog up since 19:17:55 PT. Every job since then queues 'running' (buffffff, ours, prometheus). Posted the finding; did not click it, kill or relaunch. No screenshot.

## 2026-10-12 21:15–21:31 PT
- r2 editor turn (parent CLAIMed 21:23 PT): bb_turn over 9877, ran 21:23–21:29. 981 of 1003 placed, base ok, 260 imported. The 22 that didn't make the 200 s import window are Windmill_06–19, BUF bench V1–V6 and 2 more. Saved the sublevel and DaedalusWorld, Play off, tidy run. Posted DONE, then HANDOFF to 2hot2trot at 21:29. Screenshot is in /workspace/ue_island.png. The terrain/base doesn't show in the shot.
- Water v2: cyan emissive water, channels 1.6x wider and 0.35 m deeper, 0.9 m walls. Commits bh 203d71a and D2 72dee8bc.
- LOD1: built 500 of 500; box count went from 3165 to 2055.
- Thin-prop turntable fix is in render.py. The re-render was skipped because the assets already exist; still pending.
- The bb_round2 watcher was killed to avoid a double fire. Poster pid 25584 is running.

## 21:31–21:50 PT
- Base invisible in UE, root cause: the base glb held 323 separate meshes, so UE imported 323 assets and `_mesh()` fell back to the first StaticMesh in the folder, which was a pier block. Scale (metres, applied), Z (terrain 0–40 m, props 1.7–31 m) and materials were fine. Fix: flagship.py now exports one joined mesh (25,431 faces, 6 materials, 242 m across). bb_island_ue.py now does an exact-name lookup, refuses a base under 100 m and has BB_MODE=makeup. Commits bh 35b9a90 and D2 9fcca073. Layout is unchanged.
- flagship.py now skips _LOD1 glbs.
- The 22 missing are already READY rows (5970–6295 windmills, plus Buffffff's 5473–5478 benches). Nothing new to add to the queue; the make-up turn imports about 23 small glbs.
- The bb_makeup3 watcher is armed (after 23992). It triggers strictly, runs the 1+1 ping check, and stands down if the editor is frozen; next is prometheus.
- Thin turntables: 100 of 100 re-rendered, 400 PNGs (e55de78).

## 22:14–22:32 PT
- The watcher and poster were alive, not dead. I added scheduled task BB_Ensure (every 2 min, ensure.py) that restarts them, and made the watcher save its link cursor.
- Buffffff posted TURN DONE without a HANDOFF line, so I fired the make-up myself (bb_now.py). Ping ok, CLAIM 22:21:30 (#24212), accepted by the referee. The bridge job didn't return by the hard stop. Posted PARTIAL and HANDOFF prometheus at 22:30 (#24240/24241). Job job-1791868891380-17 is still "running" in the editor, and an "Add Level" dialog is open. Posted BLOCKED/heads-up to prometheus. Did not touch the editor.
- Fix: bb_island_ue.py no longer re-adds an already-streamed sublevel (D2 9631805d). The dialog's cause isn't proven.
- w4run (LOD1 for 17 stations + 57 ark parts) is armed but waits for free RAM ≥ 1.2 GB (now 0.94 GB).

## 23:05–23:09 PT, round 3
- Ping ok on pid 38148. Make-up mode with 9631805d: 1003 of 1003 placed, 0 missing, base placed (254.65 m incl. pier), imported 1, no dialogs. Sublevel and DaedalusWorld saved, Play off, tidy. DONE posted, then HANDOFF to 2hot2trot at 23:08.
- Screenshot: the ground is visible now but white. M_BB_Terrain colours come only from vertex colours (Col), and UE's glTF import ignores those. Fix: use flat material slots for grass/rock/sand, or a UE vertex-colour material.
- Wave-4 LOD1 already ran at 22:35: stations 17 of 17 (99→64 boxes), ark parts 57 of 57 (204→144). Free RAM 5.5 GB.

## 23:09–23:28 PT
- Terrain colour fix: 5 flat slots (grass/rock/sand/dirt/shore water). Joined base rebuilt (25,431 faces, 10 slots) and checked in the Blender render. Commits bh c826624, D2 1d45f827. Added BB_MODE=base. bb_base watcher armed (pid 17592, after 25523) under supervisor BB_Ensure.
- BBIsle check: all 500 already use flat baseColorFactor, 0 with COLOR_0. Nothing to do.
- Wave-4 LOD1: ore 21, tools 9, metal 13 (14c52ef).
- Hephaestus landmarks: QUEUE 1360–1366 now READY (5dcc2f7). Fixed queue.py: Blender -b 4.3 leaves is_dirty True, so it now accepts a just-written file.

## 00:01–00:06 PT, round 4
- Parent CLAIMed at 00:01. bb_base watcher disarmed (killed, supervisor off). Ping ok. bb_turn ran 00:02–00:03: base re-imported from the 23:18 glb (5 flat terrain slots) and re-placed (254.65 m), 1003 of 1003 placed, 0 missing. Saved, Play off, tidy. DONE posted, then HANDOFF to 2hot2trot at 00:03.
- BB_MODE=base had no effect: the script runs inside the editor process, so the shell's env var never reaches it. It ran the normal full re-place instead (same end state). Fixed: the mode is now read from jobs/bb_mode.txt (D2 3d61fc41).
- The UE shot is near-black (lighting still off, matching REFEREE NEED 26457), so the green ground can't be confirmed visually.
- Earlier: hephland_lod1 7 of 7, decor_lod1 60 of 60 (385→251 boxes), queue replace retry 089f080.
- 01:44 PT: Post-mortem on the missed r5 handoff. The art-master-flex 01:30 HANDOFF never reached the 9890 link, and the referee's "Now OPEN: blender-team" (27078) wasn't in our patterns. Added that pattern and tested it. Watcher re-armed after 27094, supervisor back on until 06:00. bb_island_ue shot-mode streaming fixed to remove + re-add AlwaysLoaded, saving only DaedalusWorld (D2 b2ec9175). DONE is queued in the worklog.
- 02:5x PT: TURN-IN posted on its own line (msg 27382), CLAIM posted (27384). Built BBA 1 asset LOD manifest + LOD selection: Daedalus2 0c18e693 (ADR-062). C++ 14/14 ASan/UBSan, Java AssetLodParityTest 6/6, daedalus-core 582/582 + spotbugs clean. catalog.bba has 5457 assets (3447 with LOD1). READY posted to unreal-team (27397); registry row set to BUILDING. LOD batches still running.
- Oct 18 20:30-21:10 PT: BLACKBEARD/Blender/link up. STATUS posted (msg 33516). Claimed "Flagship island import packets (BIP 1)" in ARCHITECTURE.md (line 652). Built via temp worktree C:\Users\730ri\projects\Daedalus2-bb-wt (shared Daedalus2 checkout untouched, caf1b103, 617 behind origin): Daedalus2 a8e9f599 = bip_split/bip_verify/bip_glb/bip_render_check + flagship.bip.json + catalog.bba regenerated (5605/5605 LOD1). Flagship glb -> 67 packets (28 terrain + 39 props, 1730 placements), caps 12k tris/1.5MiB/64 mats, max 9592 tris/920,952 B, verify 7461/7461, render diff 0.0%. READY posted (msg 47755). Not imported into Unreal.
