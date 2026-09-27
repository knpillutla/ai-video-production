@echo off
title CineAI Studio Web UI
cd /d "%~dp0\.."
echo ========================================================================
echo       CINEAI STUDIO - AUTONOMOUS AI VIDEO PRODUCER WEB UI
echo ========================================================================
echo Starting server at http://127.0.0.1:8000/ui ...
start http://127.0.0.1:8000/ui
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
pause
