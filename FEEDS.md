# Blender team feeds for the Unreal team (2026-10-12)

| Feed | What the Blender team provides | Status |
|---|---|---|
| Landscape | `assets/heightmap.py`: 16-bit 1009x1009 heightmaps per biome, terraced in 1 m steps (blocky world), with `heightmaps.json` (relief, step, Unreal Z scale). Output in `art/landscape/`. No Blender or editor needed. | Live: 9 biomes |
| Foliage | Flora props are instancing-ready: origin at the base centre, one mesh, 1 to 3 flat materials, small tri counts (herbs and flowers 300 to 700 tris), no per-instance data. A growing / `_Harvested` pair per species, so the game can swap meshes on harvest. | Live (flora wave 2) |
| Physics | Simple collision hulls `UCX_<Asset>_NN` (axis-aligned boxes from the blocky parts, 1 to 4 per asset). This is **opt-in after the Unreal team confirms** that its glTF import keeps UCX meshes (the FBX path does; the glTF path may not). Until then, Unreal auto-generates simple collision. | Proposed |
| AI | Nothing to build on the Blender side. Assets keep navmesh-friendly sizes: walkable tops at whole 1 m steps, doors and gaps at least 1 m wide and 2 m tall, mobs at most 1.2 m wide unless they are bosses. | Rule |

Resource rules (RAM is tight, about 6 GB free): the Blender team never launches an Unreal editor. It runs one Blender job at a time, hidden (blender-job.ps1 uses ShowWindow=0), in background mode where possible.
