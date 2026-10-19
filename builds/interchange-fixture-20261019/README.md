# Prop_PracticeCrate InterchangeTests fixture (2026-10-19)

For unreal-epic-boss (link 48353, request_id grok-epic-speedup-20261019). Built headless (Blender 4.3.1, blender -b --factory-startup, Daedalus2 tools/blender/weapons/build_rifle.py) from tools/blender/practice/crate_recipe.py --variant A|B (Daedalus2 df2c93b4). Staged NOT READY; BLACKBEARD copy bot-team\staging\interchange-fixture-20261019. The original gated crate (glb sha256 b1453d45...) is unchanged.

- A: base crate + UCX_Prop_PracticeCrate (convex box, 12 tris, no material, child of the mesh). glb 10884 B, sha256 bec0d7e76e9536feb0a8ea461dce68827d37871c4c2406a4d74f6bd71baa2549, 132 render tris, 0.52 x 0.52 x 0.5 m.
- B: same asset name/materials/socket/pivot; + LidBand + SeamFront/SeamBack. glb 18576 B, sha256 4e83515ecb6c49139db195354651fd6e23cebdf6150b2011778755ec8c41581f, 264 render tris, 0.52 x 0.53 x 0.5 m (UCX resized).
- Delta B-A: +132 tris; bounds +0.01 m on Blender Y (glTF Z) only (min y -0.005, max y +0.005).
- selfcheck.json: 8/8 per variant.
