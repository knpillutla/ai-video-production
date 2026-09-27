"""Cross-platform script to gracefully stop the CineAI Studio Web UI and uvicorn server."""

import os
import platform
import subprocess
import sys


def stop_server(port: int = 8000):
    print("=" * 60)
    print("      🛑 STOPPING CINEAI STUDIO WEB SERVER")
    print("=" * 60)
    system = platform.system().lower()
    stopped = False

    if system == "windows":
        try:
            # Find PID listening on port
            cmd = f"netstat -ano | findstr :{port}"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            pids = set()
            for line in res.stdout.strip().split("\n"):
                if "LISTENING" in line:
                    parts = line.strip().split()
                    if len(parts) >= 5:
                        pids.add(parts[-1])
            for pid in pids:
                if pid and pid != "0":
                    print(f" * Terminating listening process PID {pid} on port {port}...")
                    subprocess.run(f"taskkill /F /PID {pid}", shell=True, capture_output=True)
                    stopped = True
        except Exception as e:
            print(f"Error finding process: {e}")
    else:
        try:
            cmd = f"lsof -ti:{port} | xargs kill -9 2>/dev/null"
            subprocess.run(cmd, shell=True)
            stopped = True
        except Exception:
            pass

    if stopped:
        print(f"\n[OK] CineAI Studio Web UI on port {port} has been stopped.\n")
    else:
        print(f"\n[INFO] No active server found listening on port {port}.\n")


if __name__ == "__main__":
    target_port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8000
    stop_server(target_port)
