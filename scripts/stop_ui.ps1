# PowerShell script to stop the CineAI Studio Web UI server
param(
    [int]$Port = 8000
)

Write-Host "========================================================================" -ForegroundColor Yellow
Write-Host "      🛑 STOPPING CINEAI STUDIO WEB SERVER (PORT $Port)                 " -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Yellow

$conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
if ($conn) {
    $procIds = $conn.OwningProcess | Select-Object -Unique
    foreach ($procId in $procIds) {
        Write-Host " * Stopping server process PID: $procId..." -ForegroundColor Gray
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Milliseconds 500
    Write-Host "`n[OK] CineAI Studio server on port $Port stopped successfully.`n" -ForegroundColor Green
} else {
    Write-Host "`n[INFO] No active process was found listening on port $Port.`n" -ForegroundColor Gray
}
