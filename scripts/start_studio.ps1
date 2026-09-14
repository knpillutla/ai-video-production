<#
.SYNOPSIS
    Start the AI Video Producer Studio Core API, Swarm Agents, and Web UI.

.DESCRIPTION
    Launches the FastAPI ASGI application via Uvicorn, which initializes all background
    agents, task queue workers, and serves the interactive Web Studio UI.

.PARAMETER Port
    Port to bind the web server to (default: 8000).

.PARAMETER Host
    Host address to bind the web server to (default: 127.0.0.1).

.PARAMETER NoReload
    Disable hot-reloading on code modifications.

.PARAMETER Open
    Automatically launch default browser to the Web Studio UI.

.EXAMPLE
    .\scripts\start_studio.ps1
    .\scripts\start_studio.ps1 -Port 8080 -Open
#>

[CmdletBinding()]
param(
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1",
    [switch]$NoReload,
    [switch]$Open
)

$ErrorActionPreference = "Stop"

# 1. Resolve Project Root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

# 2. Locate Virtual Environment Python
$PythonExe = $null
$CandidateVenvs = @(
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe"),
    (Join-Path $ProjectRoot "venv\Scripts\python.exe")
)

foreach ($cand in $CandidateVenvs) {
    if (Test-Path $cand) {
        $PythonExe = $cand
        break
    }
}

if (-not $PythonExe) {
    $SysPython = (Get-Command python -ErrorAction SilentlyContinue)
    if ($SysPython) {
        $PythonExe = $SysPython.Source
    } else {
        Write-Error "[!] Error: Python executable not found. Please create or activate a virtual environment."
        exit 1
    }
}

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "       AI VIDEO PRODUCER STUDIO - MULTI-AGENT RUNTIME & WEB UI          " -ForegroundColor Cyan
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host " Python Runtime: $PythonExe" -ForegroundColor Gray
Write-Host " Project Root:   $ProjectRoot" -ForegroundColor Gray

# 3. Verify Dependencies
$UvicornCheck = & $PythonExe -c "import fastapi, uvicorn; print('OK')" 2>$null
if ($UvicornCheck -ne "OK") {
    Write-Warning "[!] Warning: fastapi or uvicorn missing. Installing dependencies from requirements.txt..."
    & $PythonExe -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
}

# 4. Display Active Endpoints
$BaseUrl = "http://${BindHost}:${Port}"
Write-Host "`n ACTIVE STUDIO SERVICES & ENDPOINTS:" -ForegroundColor Green
Write-Host "  - Web Studio Dashboard UI:  ${BaseUrl}/ui" -ForegroundColor White
Write-Host "  - OpenAPI Interactive Docs:  ${BaseUrl}/docs" -ForegroundColor White
Write-Host "  - Health Check & Telemetry:  ${BaseUrl}/health" -ForegroundColor White
Write-Host "  - Static & Media Storage:    ${BaseUrl}/storage" -ForegroundColor White
Write-Host "  - Multi-Agent Task Workers:  [ACTIVE] Listening on background queue" -ForegroundColor White
Write-Host "========================================================================`n" -ForegroundColor Cyan

# 5. Optionally Open Browser
if ($Open) {
    Start-Process "${BaseUrl}/ui"
}

# Check if port is already listening
$PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if ($PortInUse) {
    try {
        $Health = Invoke-RestMethod -Uri "${BaseUrl}/health" -TimeoutSec 2 -ErrorAction Stop
        if ($Health.service -eq "video-studio-api") {
            Write-Host "[i] Studio API server is ALREADY ACTIVE and running on ${BaseUrl}!" -ForegroundColor Green
            Write-Host "    Open UI in browser: ${BaseUrl}/ui" -ForegroundColor White
            exit 0
        }
    } catch {}
    Write-Warning "[!] Port $Port is occupied by another process. Please specify a different port with -Port <number> (e.g. .\scripts\start_studio.ps1 -Port 8001)."
}

# 6. Launch Uvicorn Server
$UvicornArgs = @(
    "-m", "uvicorn", "src.api.main:app",
    "--host", $BindHost,
    "--port", $Port
)

if (-not $NoReload) {
    $UvicornArgs += "--reload"
}

Write-Host "[i] Starting ASGI server on ${BaseUrl} (Press Ctrl+C to stop)...`n" -ForegroundColor Yellow
& $PythonExe $UvicornArgs
