# PowerShell script to start the CineAI Studio Web UI and open the browser
param(
    [int]$Port = 8000,
    [string]$HostAddress = "127.0.0.1",
    [switch]$NoBrowser
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "      🎬 CINEAI STUDIO - AUTONOMOUS AI VIDEO PRODUCER WEB UI            " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host " Project Root: $ProjectRoot" -ForegroundColor Gray
Write-Host " UI Address:   http://${HostAddress}:${Port}/ui" -ForegroundColor Green
Write-Host " API Docs:     http://${HostAddress}:${Port}/docs" -ForegroundColor Gray
Write-Host "========================================================================`n" -ForegroundColor Cyan

# Check if port is in use and terminate existing process if needed
$conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if ($conn) {
    $procId = $conn.OwningProcess | Select-Object -First 1
    if ($procId) {
        Write-Host "[!] Port $Port is currently in use by PID $procId. Restarting..." -ForegroundColor Yellow
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Start-Sleep -Milliseconds 600
    }
}

# Auto-launch default browser
if (-not $NoBrowser) {
    Start-Job -ScriptBlock {
        param($url)
        Start-Sleep -Seconds 1
        Start-Process $url
    } -ArgumentList "http://${HostAddress}:${Port}/ui" | Out-Null
}

python -m uvicorn src.api.main:app --host $HostAddress --port $Port --reload
