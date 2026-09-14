<#
.SYNOPSIS
    Stop the running AI Video Producer Studio Core API and Agent workers.

.DESCRIPTION
    Identifies and terminates any active Uvicorn / Studio server processes
    and child reloader worker processes listening on the designated port
    (default 8000) or tracked in logs/studio.pid.

.PARAMETER Port
    Port the studio server is bound to (default: 8000).

.EXAMPLE
    .\scripts\stop_studio.ps1
    .\scripts\stop_studio.ps1 -Port 8080
#>

[CmdletBinding()]
param(
    [int]$Port = 8000
)

$ErrorActionPreference = "SilentlyContinue"

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "             STOPPING AI VIDEO PRODUCER STUDIO SERVICES                 " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan

$TerminatedCount = 0

function Stop-ProcessTree([int]$TargetPid) {
    if (-not $TargetPid -or $TargetPid -le 0) { return }
    # Use taskkill /T to terminate entire process tree including Uvicorn reload workers
    cmd /c "taskkill /F /PID $TargetPid /T" 2>$null | Out-Null
    $Children = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.ParentProcessId -eq $TargetPid }
    foreach ($Child in $Children) {
        Stop-Process -Id $Child.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Stop-Process -Id $TargetPid -Force -ErrorAction SilentlyContinue
}

# 1. Check tracked PID file
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$PidFile = Join-Path $ProjectRoot "logs\studio.pid"
if (Test-Path $PidFile) {
    try {
        $SavedPid = (Get-Content $PidFile -ErrorAction SilentlyContinue).Trim()
        if ($SavedPid) {
            $PidInt = [int]$SavedPid
            Write-Host "[*] Terminating recorded Studio PID $PidInt (and child workers)..." -ForegroundColor Yellow
            Stop-ProcessTree -TargetPid $PidInt
            $TerminatedCount++
        }
    } catch {}
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
}

# 2. Locate listening connections on target port
$Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($Connections) {
    $ProcessIds = $Connections.OwningProcess | Select-Object -Unique
    foreach ($ProcId in $ProcessIds) {
        if ($ProcId -and $ProcId -gt 0) {
            Write-Host "[*] Terminating listening process tree for PID $ProcId on port $Port..." -ForegroundColor Yellow
            Stop-ProcessTree -TargetPid $ProcId
            $TerminatedCount++
        }
    }
} else {
    $NetstatLines = (netstat -ano | Select-String ":$Port\s+.*LISTENING")
    foreach ($Line in $NetstatLines) {
        $Parts = ($Line.Line.Trim() -split '\s+')
        $ProcId = [int]$Parts[-1]
        if ($ProcId -gt 0) {
            Write-Host "[*] Terminating listening PID $ProcId via netstat..." -ForegroundColor Yellow
            Stop-ProcessTree -TargetPid $ProcId
            $TerminatedCount++
        }
    }
}

# 3. Clean up any lingering uvicorn reload processes running src.api.main:app
$OrphanProcs = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*uvicorn*src.api.main:app*" -or
    ($_.CommandLine -like "*src.api.main*" -and $_.Name -like "python*")
}

foreach ($Orphan in $OrphanProcs) {
    Write-Host "[*] Stopping lingering Studio worker PID $($Orphan.ProcessId)..." -ForegroundColor Yellow
    Stop-Process -Id $Orphan.ProcessId -Force -ErrorAction SilentlyContinue
    $TerminatedCount++
}

Start-Sleep -Milliseconds 600

# 4. Verify port is freed
$StillListening = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($StillListening) {
    Write-Warning "[!] Warning: Port $Port still appears to have active connections."
} else {
    if ($TerminatedCount -gt 0) {
        Write-Host "[v] Studio services stopped successfully. Port $Port is now free." -ForegroundColor Green
    } else {
        Write-Host "[i] No active Studio processes found on port $Port." -ForegroundColor Gray
    }
}
Write-Host "========================================================================`n" -ForegroundColor Cyan
