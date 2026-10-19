# Restoring the blender-team asset binaries

The large `.blend` and `.glb` catalog files are not in git. They are attached as zip assets to GitHub releases of this repo. Each release has a manifest here: `assets-<date>.md` (readable) and `assets-<date>.json` (for scripts). Each manifest lists every file's path, size and SHA256, which zip holds it, and the zips' own SHA256.

## Download
    gh release download assets-2026-10-18 --repo RicheyWorks/blender-harness --dir <download dir>
Or download the zips from https://github.com/RicheyWorks/blender-harness/releases/tag/assets-2026-10-18.

## Check the zips
PowerShell: `Get-FileHash <zip> -Algorithm SHA256`. Compare the result with the `zips` table.

## Restore
Unzip every zip into the art root, `C:\Users\730ri\projects\bot-team\art` on BLACKBEARD. The paths inside the zips are relative to it, for example `Prop/Prop_Lantern.blend` and `glb/Prop_Lantern.glb`.

    Expand-Archive <zip> -DestinationPath C:\Users\730ri\projects\bot-team\art     # add -Force only to overwrite on purpose

Restore into a scratch folder first if the art folders are live: the art watcher imports from `art\<Kind>` and `art\glb`.

## Verify the restored files
    python -c "import json,hashlib,os,sys; m=json.load(open('releases/assets-2026-10-18.json')); r=sys.argv[1]; bad=[f['path'] for f in m['files'] if hashlib.sha256(open(os.path.join(r,f['path']),'rb').read()).hexdigest()!=f['sha256']]; print(len(m['files'])-len(bad),'/',len(m['files']),'match'); print(bad[:10])" <art root>
