# SPDX-License-Identifier: MIT
# Run a harness job outside the calling shell (WMI), so it outlives 60 s device-link calls and job objects.
#
#   .\blender-job.ps1 -Start                       run_all (stand-in suites)
#   .\blender-job.ps1 -Start -Live                 run_all --live (real Blender, throwaway asset)
#   .\blender-job.ps1 -Start -Run "harness.mutate -j 4"
#   .\blender-job.ps1 -Start -Run "bharness call queue.board"
#   .\blender-job.ps1 -Wait                        up to 50 s; repeat until DONE (exit code + log tail)
#   .\blender-job.ps1 -Status | -Stop
param([switch]$Start, [switch]$Wait, [switch]$Status, [switch]$Stop, [switch]$Live, [string]$Run = "")
$Here = $PSScriptRoot
$Jobs = Join-Path $env:LOCALAPPDATA "Daedalus\jobs"
New-Item -ItemType Directory -Force -Path $Jobs | Out-Null
$Log = Join-Path $Jobs "bharness-job.log"; $Exit = "$Log.exit"; $PidFile = "$Log.pid"

function Alive {
    if (-not (Test-Path $PidFile)) { return $null }
    $p = Get-CimInstance Win32_Process -Filter "ProcessId = $([int](Get-Content $PidFile))" -ErrorAction SilentlyContinue
    if ($p -and $p.CommandLine -match 'bharness-job') { $p } else { $null }
}

if ($Start) {
    if (Alive) { "already running (pid $((Alive).ProcessId)); use -Wait"; exit 1 }
    if (-not $Run) { $Run = "harness.run_all" + $(if ($Live) { " --live" } else { "" }) }
    Remove-Item $Log, $Exit -ErrorAction SilentlyContinue
    $py = (Get-Command python).Source
    # Post-job hook: our Blender tidy, then the shared cleanup script if one is published (2Hot2Trot's hook point)
    $Hook = if ($env:DAEDALUS_POST_JOB_HOOK) { $env:DAEDALUS_POST_JOB_HOOK } else { "C:\Users\730ri\projects\bot-team\hooks\post-job.ps1" }
    $cmd = "cmd /v:on /c title bharness-job & cd /d `"$Here`" & set PYTHONPATH=$Here & `"$py`" -u -m $Run > `"$Log`" 2>&1 & echo !ERRORLEVEL! > `"$Exit`" & `"$py`" -m bharness.tidy >> `"$Log`" 2>&1 & if exist `"$Hook`" powershell -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Hook`" -Job bharness >> `"$Log`" 2>&1"
    # Hidden: ShowWindow=0 (SW_HIDE) so the job console never pops up over Richey's work.
    $si = New-CimInstance -ClassName Win32_ProcessStartup -ClientOnly -Property @{ ShowWindow = [uint16]0 }
    $r = Invoke-CimMethod Win32_Process -MethodName Create -Arguments @{ CommandLine = $cmd; CurrentDirectory = $Here; ProcessStartupInformation = $si }
    $r.ProcessId | Set-Content $PidFile
    "STARTED pid $($r.ProcessId): python -m $Run  (log $Log)"; exit 0
}
if ($Wait) {
    $deadline = (Get-Date).AddSeconds(50)
    while ((Get-Date) -lt $deadline -and -not (Test-Path $Exit)) { Start-Sleep -Milliseconds 500 }
    if (Test-Path $Exit) { "DONE exit $((Get-Content $Exit).Trim())"; Get-Content $Log -Tail 40; exit 0 }
    "RUNNING (call -Wait again)"; Get-Content $Log -Tail 5 -ErrorAction SilentlyContinue; exit 0
}
if ($Status) { if (Alive) { "running pid $((Alive).ProcessId)" } elseif (Test-Path $Exit) { "done, exit $((Get-Content $Exit).Trim())" } else { "idle" }; exit 0 }
if ($Stop) { $p = Alive; if ($p) { Stop-Process -Id $p.ProcessId -Force; "stopped" } else { "not running" }; exit 0 }
Get-Content $PSCommandPath -TotalCount 9 | Select-Object -Skip 1
