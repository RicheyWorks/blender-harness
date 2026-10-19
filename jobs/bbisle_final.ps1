$ErrorActionPreference="Continue"; Set-Location C:\Users\730ri\projects\blender-harness
$B="C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"; $J="$env:LOCALAPPDATA\Daedalus\jobs"
function WaitClear { while(@(gcim Win32_Process -Filter "Name='blender.exe'" | ? { $_.CommandLine -match ' -b ' }).Count){ Start-Sleep 5 } }
foreach($n in 2..4){ WaitClear; $env:BBISLE_BATCH="$n"; $p=Start-Process $B -ArgumentList "-b","--factory-startup","--python","`"$PWD\assets\headless.py`"","--","`"$PWD`"","assets.bbisle","bbisle","--batch=10","--turntable=4","--no-send" -WindowStyle Hidden -RedirectStandardOutput "$J\bbisle$n.log" -PassThru; $p.WaitForExit() }
WaitClear
$p=Start-Process $B -ArgumentList "-b","--factory-startup","--python","`"$PWD\assets\flagship.py`"","--","C:\Users\730ri\projects\bot-team\art","C:\Users\730ri\projects\bot-team\art\flagship\contest_island.png" -WindowStyle Hidden -RedirectStandardOutput "$J\flagship.log" -PassThru; $p.WaitForExit()
"done $(Get-Date)" | Set-Content "$J\bbisle_final.done"
