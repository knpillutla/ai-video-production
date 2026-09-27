@echo off
title Stop CineAI Studio Web UI
cd /d "%~dp0\.."
echo ========================================================================
echo       STOPPING CINEAI STUDIO WEB SERVER (PORT 8000)
echo ========================================================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do (
    echo Stopping process PID: %%a ...
    taskkill /F /PID %%a
)
echo.
echo [OK] Done.
pause
