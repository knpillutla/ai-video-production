"""Cross-platform script to start the CineAI Studio Web UI and FastAPI server."""

import os
import sys
import time
import webbrowser
from pathlib import Path
import uvicorn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main():
    host = os.getenv("STUDIO_HOST", "127.0.0.1")
    port = int(os.getenv("STUDIO_PORT", "8000"))
    url = f"http://{host}:{port}/ui"

    print("=" * 70)
    print("      🎬 CINEAI STUDIO - AUTONOMOUS VIDEO PRODUCER WEB UI")
    print("=" * 70)
    print(f" * Project Root:  {PROJECT_ROOT}")
    print(f" * Web UI URL:    {url}")
    print(f" * API Docs:      http://{host}:{port}/docs")
    print(f" * Real-Time Log: http://{host}:{port}/api/logs/stream")
    print("=" * 70)

    # Optional auto-launch browser
    if "--no-browser" not in sys.argv:
        def open_browser():
            time.sleep(1.2)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        import threading
        threading.Thread(target=open_browser, daemon=True).start()

    print(f"\n[STARTING] Serving CineAI Studio at {url} (Press CTRL+C to stop)...\n")
    uvicorn.run(
        "src.api.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
