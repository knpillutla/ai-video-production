#!/usr/bin/env bash
# ==============================================================================
# AI Video Producer Studio - Multi-Agent Runtime & Web UI Launcher
# ==============================================================================

set -eo pipefail

PORT=8000
HOST="127.0.0.1"
RELOAD="--reload"
OPEN_BROWSER=false

# Parse optional CLI flags
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    --host|-h)
      HOST="$2"
      shift 2
      ;;
    --no-reload)
      RELOAD=""
      shift
      ;;
    --open|-o)
      OPEN_BROWSER=true
      shift
      ;;
    *)
      echo "Unknown argument: $1"
      echo "Usage: $0 [--port <8000>] [--host <127.0.0.1>] [--no-reload] [--open]"
      exit 1
      ;;
  esac
done

# Resolve Project Root (one level above scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${PROJECT_ROOT}"

# Detect Python in virtual environment (support Linux/macOS and Windows Git Bash)
PYTHON_EXE=""
if [[ -f "${PROJECT_ROOT}/.venv/bin/python" ]]; then
  PYTHON_EXE="${PROJECT_ROOT}/.venv/bin/python"
elif [[ -f "${PROJECT_ROOT}/.venv/Scripts/python.exe" ]]; then
  PYTHON_EXE="${PROJECT_ROOT}/.venv/Scripts/python.exe"
elif [[ -f "${PROJECT_ROOT}/venv/bin/python" ]]; then
  PYTHON_EXE="${PROJECT_ROOT}/venv/bin/python"
elif [[ -f "${PROJECT_ROOT}/venv/Scripts/python.exe" ]]; then
  PYTHON_EXE="${PROJECT_ROOT}/venv/Scripts/python.exe"
elif command -v python3 &>/dev/null; then
  PYTHON_EXE="$(command -v python3)"
elif command -v python &>/dev/null; then
  PYTHON_EXE="$(command -v python)"
else
  echo "[!] Error: No Python executable found. Please create or activate a virtual environment."
  exit 1
fi

echo "========================================================================"
echo "       AI VIDEO PRODUCER STUDIO - MULTI-AGENT RUNTIME & WEB UI          "
echo "========================================================================"
echo " Python Runtime: ${PYTHON_EXE}"
echo " Project Root:   ${PROJECT_ROOT}"

# Verify core dependencies
if ! "${PYTHON_EXE}" -c "import fastapi, uvicorn" &>/dev/null; then
  echo "[!] Warning: fastapi or uvicorn missing. Installing from requirements.txt..."
  "${PYTHON_EXE}" -m pip install -r "${PROJECT_ROOT}/requirements.txt"
fi

BASE_URL="http://${HOST}:${PORT}"
echo ""
echo " ACTIVE STUDIO SERVICES & ENDPOINTS:"
echo "  - Web Studio Dashboard UI:  ${BASE_URL}/ui"
echo "  - OpenAPI Interactive Docs:  ${BASE_URL}/docs"
echo "  - Health Check & Telemetry:  ${BASE_URL}/health"
echo "  - Static & Media Storage:    ${BASE_URL}/storage"
echo "  - Multi-Agent Task Workers:  [ACTIVE] Listening on background queue"
echo "========================================================================"
echo ""

# Optionally open browser
if [ "$OPEN_BROWSER" = true ]; then
  if command -v xdg-open &>/dev/null; then
    xdg-open "${BASE_URL}/ui" &>/dev/null &
  elif command -v open &>/dev/null; then
    open "${BASE_URL}/ui" &>/dev/null &
  elif command -v start &>/dev/null; then
    start "${BASE_URL}/ui" &>/dev/null &
  fi
fi

# Check if studio is already running on this port
if command -v curl &>/dev/null; then
  if curl -s -m 2 "${BASE_URL}/health" 2>/dev/null | grep -q "video-studio-api"; then
    echo "[i] Studio API server is ALREADY ACTIVE and running on ${BASE_URL}!"
    echo "    Open UI in browser: ${BASE_URL}/ui"
    exit 0
  fi
fi

echo "[i] Starting ASGI server on ${BASE_URL} (Press Ctrl+C to stop)..."
echo ""

if [ -n "${RELOAD}" ]; then
  exec "${PYTHON_EXE}" -m uvicorn src.api.main:app --host "${HOST}" --port "${PORT}" ${RELOAD}
else
  exec "${PYTHON_EXE}" -m uvicorn src.api.main:app --host "${HOST}" --port "${PORT}"
fi
