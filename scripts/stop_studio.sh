#!/usr/bin/env bash
# ==============================================================================
# AI Video Producer Studio - Stop Services & Workers
# ==============================================================================

PORT=8000

# Parse optional arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --port|-p)
      PORT="$2"
      shift 2
      ;;
    *)
      if [[ "$1" =~ ^[0-9]+$ ]]; then
        PORT="$1"
        shift
      else
        echo "Usage: $0 [--port <8000>]"
        exit 1
      fi
      ;;
  esac
done

echo "========================================================================"
echo "             STOPPING AI VIDEO PRODUCER STUDIO SERVICES                 "
echo "========================================================================"

STOPPED=0

# 1. Try finding PIDs via lsof (Linux/macOS)
if command -v lsof &>/dev/null; then
  PIDS=$(lsof -ti tcp:"${PORT}" 2>/dev/null || true)
  if [ -n "${PIDS}" ]; then
    for PID in ${PIDS}; do
      echo "[*] Terminating process PID ${PID} on port ${PORT}..."
      kill -9 "${PID}" 2>/dev/null || true
      STOPPED=$((STOPPED + 1))
    done
  fi
fi

# 2. Try finding PIDs via fuser (Linux)
if command -v fuser &>/dev/null; then
  fuser -k -n tcp "${PORT}" 2>/dev/null && STOPPED=$((STOPPED + 1)) || true
fi

# 3. Try finding PIDs via netstat on Windows Git Bash
if command -v netstat &>/dev/null; then
  WIN_PIDS=$(netstat -ano 2>/dev/null | grep ":${PORT} " | grep -i "LISTENING" | awk '{print $NF}' | sort -u || true)
  for WPID in ${WIN_PIDS}; do
    if [[ "${WPID}" =~ ^[0-9]+$ ]] && [ "${WPID}" -gt 0 ]; then
      echo "[*] Terminating listening Windows PID ${WPID} on port ${PORT}..."
      taskkill //F //PID "${WPID}" 2>/dev/null || kill -9 "${WPID}" 2>/dev/null || true
      STOPPED=$((STOPPED + 1))
    fi
  done
fi

# 4. Search for uvicorn processes running src.api.main:app
if command -v pgrep &>/dev/null; then
  UV_PIDS=$(pgrep -f "src.api.main:app" 2>/dev/null || true)
  if [ -n "${UV_PIDS}" ]; then
    for UPID in ${UV_PIDS}; do
      echo "[*] Stopping Studio process PID ${UPID}..."
      kill -9 "${UPID}" 2>/dev/null || true
      STOPPED=$((STOPPED + 1))
    done
  fi
fi

sleep 0.5

if [ "${STOPPED}" -gt 0 ]; then
  echo "[v] Studio services stopped successfully. Port ${PORT} is now free."
else
  echo "[i] No active Studio processes found on port ${PORT}."
fi
echo "========================================================================"
echo ""
