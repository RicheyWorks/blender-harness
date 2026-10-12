# blender-harness

A modular, reusable harness over the [Claude Blender Bridge](https://github.com/RicheyWorks/claude-blender-connector)
(TCP 127.0.0.1:9876), so a bot can operate Blender safely and hand assets to the
[Daedalus2 asset pipeline](https://github.com/RicheyWorks/Daedalus2/tree/main/connectors/claude-asset-pipeline).
Python 3.10+ standard library only.

Shape (the same as the CSRBT / FlowersForever / ComputerPets harnesses and the Unreal connector's harness):

```text
CLI / bot / test runner
        │
Gateway   risk ceiling (READ < SCENE < FILE < DESTRUCTIVE), log, accounting identity
        │
Registry  plugins: bridge · probe · judge · render · queue   (+ your project's own)
        │
Bridge client ── 127.0.0.1:9876 ── Blender
```

| Path | What it is |
|---|---|
| `bharness/client.py` | the bridge client (one JSON line each way) |
| `bharness/contract.py` | Risk, Action, Plugin, Registry, Gateway, accounting |
| `bharness/context.py` | shared context + `build()` wiring; pass `extra=[MyPlugin]` for project plugins |
| `bharness/plugins/bridge.py` | ping, scene, object, filestate, python |
| `bharness/plugins/probe.py` | measures an asset's collection inside Blender |
| `bharness/plugins/judge.py` | the Daedalus brief's rules (pure function, unit-tested) |
| `bharness/plugins/render.py` | viewport shot; turntable renders → `art\promo\<Asset>\` (for advertising) |
| `bharness/plugins/queue.py` | the art board: claim, open, save, ready, retry, block |
| `harness/` | suites (`n/m` last line), `run_all`, `walk`, `mutate`, `ledger`, stand-ins |
| `ledgers/` | runs, walk, mutants, capabilities (written by the tools, never by hand) |
| `blender-job.ps1` | run any of it as a WMI job: `-Start`, then `-Wait` |
| `BLENDER-LESSONS.md` | what breaks, found live |

## Use

```powershell
python -m bharness list
python -m bharness judge Prop_Lantern                      # brief checks on the open scene; n/m last
python -m bharness call queue.board
python -m bharness call queue.claim asset=Prop_Lantern --allow FILE
python -m bharness call queue.ready asset=Prop_Lantern turntable=8 --allow FILE
python -m bharness call queue.retry asset=Prop_Lantern --allow FILE   # BLOCKED -> READY
```
The art folder defaults to `%USERPROFILE%\projects\bot-team\art`; override it with `BHARNESS_ART`. The name the
harness uses on the board is `Blender Boss` (`Context(who=...)`).

### The hand-off (Blender team → Claude/Unreal → advertising)
`claim` (TODO/REJECTED → `DOING (Blender Boss)`) → build → `ready`: judge against the brief → optional turntable
to `promo\<Asset>\` → save `<Kind>\<Asset>.blend` → `READY` with tris and size in Notes, plus a `feed.jsonl` line
for the lead bot. The watcher ships it into Unreal. `REJECTED: <check>` means fix the asset and `claim` again;
`BLOCKED: <why>` means the editor got in the way (not the asset), so `retry` once it's clear.

Safety: only the Status and Notes cells are ever written, with a re-read guard. Nothing runs while the watcher is
SHIPPING. Unsaved Blender work is never discarded. File operators always run `EXEC_DEFAULT`, so no modal opens.

## Tests

```powershell
python -m harness.run_all              # stand-in suites: contract, judge, queue, client, walk
python -m harness.run_all --live       # + the live suite: real Blender, throwaway Prop_BHTest in a temp art folder
python -m harness.mutate -j 4          # every mutant must be killed
python -m harness.walk --live          # READ-only walk of every action against the open Blender
```
