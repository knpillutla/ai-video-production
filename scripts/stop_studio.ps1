<#
.SYNOPSIS
    Stop the running AI Video Producer Studio Core API and Agent workers.

.DESCRIPTION
    Identifies and terminates any active Uvicorn / Studio server processes
    listening on the designated port (default 8000).

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

# 1. Locate listening connections on target port
$Connections = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
$TerminatedCount = 0

if ($Connections) {
    $ProcessIds = $Connections.OwningProcess | Select-Object -Unique
    foreach ($ProcId in $ProcessIds) {
        if ($ProcId -and $ProcId -gt 0) {
            $TargetProcess = Get-Process -Id $ProcId -ErrorAction SilentlyContinue
            if ($TargetProcess) {
                $ProcName = $TargetProcess.ProcessName
                Write-Host "[*] Terminating process PID $ProcId ($ProcName) on port $Port..." -ForegroundColor Yellow
                Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
                $TerminatedCount++
            }
        }
    }
} else {
    # Fallback search for python process listening via netstat
    $NetstatLines = (netstat -ano | Select-String ":$Port\s+.*LISTENING")
    foreach ($Line in $NetstatLines) {
        $Parts = ($Line.Line.Trim() -split '\s+')
        $ProcId = [int]$Parts[-1]
        if ($ProcId -gt 0) {
            Write-Host "[*] Terminating listening PID $ProcId via netstat..." -ForegroundColor Yellow
            Stop-Process -Id $ProcId -Force -ErrorAction SilentlyContinue
            $TerminatedCount++
        }
    }
}

# 2. Also clean up any lingering uvicorn reload child processes running src.api.main:app
$OrphanProcs = Get-CimInstance Win32_Process | Where-Object {
    $_.CommandLine -like "*uvicorn*src.api.main:app*" -or
    ($_.CommandLine -like "*src.api.main*" -and $_.Name -like "python*")
}

foreach ($Orphan in $OrphanProcs) {
    Write-Host "[*] Stopping Studio process PID $($Orphan.ProcessId)..." -ForegroundColor Yellow
    Stop-Process -Id $Orphan.ProcessId -Force -ErrorAction SilentlyContinue
    $TerminatedCount++
}

Start-Sleep -Milliseconds 500

# 3. Verify port is freed
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
