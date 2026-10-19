# Flagship island (blender-team)
- `Prop_Island_Flagship_BlenderBoss.glb`: the 14.5 MB source (QUEUE HOLD 2963/4481 after the Oct 13 05:54 GPU crash). Do not import it whole.
- `packets/`: the 67 BIP 1 import packets made from it by Daedalus2 `tools/islands/blenderboss/bip_split.py`; manifest `data/islands/blenderboss/flagship.bip.json` (Daedalus2 main). The same files are in bot-team `art/packets/flagship/`. Frozen: they do not change unless the manifest changes.
- `layout.json`, `contest_island*.png`, `BlenderBoss_Island.md`: the layout, renders and notes from bot-team `art/flagship/`. The 75 MB `.blend` is not in git (over GitHub's 50 MB guidance); flagship.py regenerates it.
