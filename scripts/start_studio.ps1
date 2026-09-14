<#
.SYNOPSIS
    Start the AI Video Producer Studio Core API, Swarm Agents, and Web UI in the background.

.DESCRIPTION
    Launches the FastAPI ASGI application via Uvicorn in the background by default,
    which initializes all background agents, task queue workers, and serves the Web Studio UI.
    All stdout/stderr logs are routed to logs/studio_server.log and logs/studio_server_err.log.

.PARAMETER Port
    Port to bind the web server to (default: 8000).

.PARAMETER Host
    Host address to bind the web server to (default: 127.0.0.1).

.PARAMETER NoReload
    Disable hot-reloading on code modifications.

.PARAMETER Open
    Automatically launch default browser to the Web Studio UI.

.PARAMETER Foreground
    Run the server in the foreground console instead of background.

.EXAMPLE
    .\scripts\start_studio.ps1
    .\scripts\start_studio.ps1 -Open
    .\scripts\start_studio.ps1 -Foreground
#>

[CmdletBinding()]
param(
    [int]$Port = 8000,
    [string]$BindHost = "127.0.0.1",
    [switch]$NoReload,
    [switch]$Open,
    [switch]$Foreground
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

# 4. Endpoints Info
$BaseUrl = "http://${BindHost}:${Port}"
Write-Host "`n ACTIVE STUDIO SERVICES & ENDPOINTS:" -ForegroundColor Green
Write-Host "  - Web Studio Dashboard UI:  ${BaseUrl}/ui" -ForegroundColor White
Write-Host "  - OpenAPI Interactive Docs:  ${BaseUrl}/docs" -ForegroundColor White
Write-Host "  - Health Check & Telemetry:  ${BaseUrl}/health" -ForegroundColor White
Write-Host "  - Static & Media Storage:    ${BaseUrl}/storage" -ForegroundColor White
Write-Host "  - Multi-Agent Task Workers:  [ACTIVE] Listening on background queue" -ForegroundColor White
Write-Host "========================================================================`n" -ForegroundColor Cyan

# 5. Check if port is already listening and active
$PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if ($PortInUse) {
    try {
        $Health = Invoke-RestMethod -Uri "${BaseUrl}/health" -TimeoutSec 2 -ErrorAction Stop
        if ($Health.service -eq "video-studio-api") {
            Write-Host "[i] Studio API server is ALREADY ACTIVE and running in background on ${BaseUrl}!" -ForegroundColor Green
            Write-Host "    Open UI in browser: ${BaseUrl}/ui" -ForegroundColor White
            if ($Open) { Start-Process "${BaseUrl}/ui" }
            exit 0
        }
    } catch {}
    Write-Warning "[!] Port $Port is occupied by another process. Stop it with .\scripts\stop_studio.ps1 or choose another port with -Port."
    exit 1
}

# 6. Ensure logs directory exists
$LogDir = Join-Path $ProjectRoot "logs"
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
$StdOutLog = Join-Path $LogDir "studio_server.log"
$StdErrLog = Join-Path $LogDir "studio_server_err.log"
$PidFile = Join-Path $LogDir "studio.pid"

# 7. Assemble Uvicorn arguments
$UvicornArgs = @(
    "-m", "uvicorn", "src.api.main:app",
    "--host", $BindHost,
    "--port", "$Port"
)

if (-not $NoReload) {
    $UvicornArgs += "--reload"
}

# 8. Foreground option
if ($Foreground) {
    Write-Host "[i] Starting ASGI server in FOREGROUND on ${BaseUrl} (Press Ctrl+C to stop)...`n" -ForegroundColor Yellow
    if ($Open) { Start-Process "${BaseUrl}/ui" }
    & $PythonExe $UvicornArgs
    exit $LASTEXITCODE
}

# 9. Background Execution (DEFAULT)
Write-Host "[*] Launching Studio API server & background agent workers in BACKGROUND..." -ForegroundColor Yellow

$Proc = Start-Process -FilePath $PythonExe `
    -ArgumentList $UvicornArgs `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -PassThru `
    -WindowStyle Hidden

if (-not $Proc) {
    Write-Error "[!] Failed to launch background Studio process."
    exit 1
}

$Proc.Id | Out-File -FilePath $PidFile -Encoding ASCII -Force

# 10. Wait for server readiness
Write-Host "[*] Waiting for Studio server initialization on ${BaseUrl}..." -NoNewline -ForegroundColor Gray
$Healthy = $false
$Attempts = 0
$MaxAttempts = 20

while ($Attempts -lt $MaxAttempts) {
    Start-Sleep -Milliseconds 500
    Write-Host "." -NoNewline -ForegroundColor Gray
    try {
        $Health = Invoke-RestMethod -Uri "${BaseUrl}/health" -TimeoutSec 1 -ErrorAction Stop
        if ($Health.status -eq "ok" -or $Health.service -eq "video-studio-api") {
            $Healthy = $true
            break
        }
    } catch {
        if ($Proc.HasExited) {
            Write-Host "`n"
            Write-Error "[!] Studio process exited prematurely with exit code $($Proc.ExitCode). Check log: $StdErrLog"
            exit 1
        }
    }
    $Attempts++
}

Write-Host ""

if ($Healthy) {
    Write-Host "`n[v] Studio services & background workers started successfully in the BACKGROUND!" -ForegroundColor Green
    Write-Host "    PID:          $($Proc.Id)" -ForegroundColor White
    Write-Host "    Web UI:       ${BaseUrl}/ui" -ForegroundColor White
    Write-Host "    API Docs:     ${BaseUrl}/docs" -ForegroundColor White
    Write-Host "    Output Log:   $StdOutLog" -ForegroundColor Gray
    Write-Host "    Error Log:    $StdErrLog" -ForegroundColor Gray
    Write-Host "    To stop:      .\scripts\stop_studio.ps1`n" -ForegroundColor Yellow

    if ($Open) {
        Start-Process "${BaseUrl}/ui"
    }
} else {
    Write-Warning "[!] Studio background process started (PID $($Proc.Id)), but health check timed out."
    Write-Warning "    Inspect log for details: $StdErrLog"
}
