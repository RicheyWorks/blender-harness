# Blender team <-> Unreal team message bus: schema v1 (proposal from the Blender team)

Transport is the **Unreal team's local HTTP server** (their design). The Blender team adapts to their endpoints;
these names are a proposal until they publish theirs. Discovery: `art\BUS.json` = `{"url": "http://127.0.0.1:<port>"}`
(the server writes it on start), or the env var `DAEDALUS_BUS`.
Fallback, when the server is down: the file bus (`art\bus\outbox-blender.jsonl` out, `art\feed.jsonl` in). The outbox
is replayed on reconnect; `id` makes POST idempotent.

## Envelope
```json
{"v": 1, "id": "uuid4", "from": "blender|unreal", "to": "unreal|blender", "type": "…", "asset": "Kind_Name|null",
 "at": "2026-10-12T12:00:00", "reply_to": "id|null", "body": {}}
```
| type | from | body |
|---|---|---|
| hello | either | `{"client": "blender-harness", "version": "<git sha>"}` |
| ready | blender | the `blender` half of jobs\<Asset>.json: glb path, glb_sha1, tris, meshes, materials, selfcheck |
| status | blender | `{"state": "idle|building|fixing|paused", "group", "progress": "n/m"}` |
| note | either | `{"text": "…"}` (replaces NOTES\*.md for live talk; NOTES stay for the record) |
| ack | either | `{}` with reply_to |
| shipping / shipped / rejected | unreal | the watcher's feed fields: `result`, `dest`, `why`, `detail`, `unreal_tris` |
| blocked / waiting | unreal | `{"why": "Play running | Unreal closed | socket reset | Blender unsaved"}`; auto-retried by the Unreal team |

## Endpoints (proposed)
- `GET  /v1/health` → `{"ok": true, "v": 1}`
- `POST /v1/messages` (envelope) → `{"ok": true, "id": "…"}`; a repeated id → ok, no duplicate
- `GET  /v1/messages?to=blender&since=<id>` → `[envelope…]` oldest first
- (optional) `GET /v1/status` → the board as JSON (what STATUS.md shows)

QUEUE.md stays the record of truth for row status; the bus carries the events in real time.
Blender team client: blender-harness `bharness/bus.py` (`python -m bharness.bus health|send|poll`), tests in
`harness/test_bus.py` against a stand-in server (8/8).
