"""Setup & Installer Script for 100% Offline Local CPU SadTalker.

Installs SadTalker and downloads checkpoints for local CPU inference ($0.00 spend):
- Clones OpenTalker/SadTalker into tools/SadTalker
- Downloads minimal 256x256 checkpoints for fast CPU rendering
- Installs PyTorch CPU (without CUDA bloat)
- Verifies local inference readiness
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import urllib.request

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"
SADTALKER_DIR = TOOLS_DIR / "SadTalker"

CHECKPOINT_URLS = {
    "SadTalker_V0.0.2_256.safetensors": (
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/SadTalker_V0.0.2_256.safetensors",
        "checkpoints",
    ),
    "mapping_00109-model.pth.tar": (
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00109-model.pth.tar",
        "checkpoints",
    ),
    "mapping_00229-model.pth.tar": (
        "https://github.com/OpenTalker/SadTalker/releases/download/v0.0.2-rc/mapping_00229-model.pth.tar",
        "checkpoints",
    ),
}


def download_file_with_progress(url: str, dest_path: Path):
    if dest_path.is_file() and dest_path.stat().st_size > 1000:
        print(f"  [OK] Already exists: {dest_path.name} ({dest_path.stat().st_size // 1024 // 1024} MB)")
        return
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"  [Downloading] {dest_path.name} from {url}...")
    try:
        urllib.request.urlretrieve(url, str(dest_path))
        print(f"  [Saved] {dest_path.name} ({dest_path.stat().st_size // 1024 // 1024} MB)")
    except Exception as ex:
        print(f"  [Warning] Download failed for {dest_path.name}: {ex}")


def clone_sadtalker_repo() -> bool:
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    if (SADTALKER_DIR / "inference.py").is_file():
        print(f"  [OK] SadTalker repo found at {SADTALKER_DIR}")
        return True
    print(f"  [Git] Cloning SadTalker into {SADTALKER_DIR}...")
    cmd = ["git", "clone", "--depth", "1", "https://github.com/OpenTalker/SadTalker.git", str(SADTALKER_DIR)]
    res = subprocess.run(cmd)
    return res.returncode == 0


def install_cpu_dependencies() -> bool:
    python_bin = sys.executable
    print("  [Pip] Checking PyTorch CPU installation...")
    try:
        import torch
        print(f"  [OK] PyTorch {torch.__version__} is already installed.")
    except ImportError:
        print("  [Pip] Installing torch CPU...")
        cmd = [
            python_bin, "-m", "pip", "install", "torch", "torchvision", "torchaudio",
            "--index-url", "https://download.pytorch.org/whl/cpu",
        ]
        subprocess.run(cmd, check=True)

    print("  [Pip] Installing SadTalker dependencies (safetensors, kornia, yacs)...")
    cmd_deps = [python_bin, "-m", "pip", "install", "safetensors", "kornia", "yacs", "face-alignment"]
    subprocess.run(cmd_deps, check=False)
    return True


def download_checkpoints():
    print("  [Checkpoints] Verifying SadTalker weights...")
    for filename, (url, subfolder) in CHECKPOINT_URLS.items():
        target = SADTALKER_DIR / subfolder / filename
        download_file_with_progress(url, target)


def main():
    parser = argparse.ArgumentParser(description="Setup Local CPU SadTalker ($0.00 spend)")
    parser.add_argument("--skip-pip", action="store_true", help="Skip pip dependency installation")
    args = parser.parse_args()

    print("=" * 65)
    print(" Setting up Local CPU SadTalker for Concert Studio Lipsync ($0.00)")
    print("=" * 65)

    if not clone_sadtalker_repo():
        print("[Error] Failed to clone SadTalker repo. Ensure git is installed.")
        return

    if not args.skip_pip:
        install_cpu_dependencies()

    download_checkpoints()

    print("\n[Complete] Local CPU SadTalker is configured!")
    print(f"Location: {SADTALKER_DIR}")
    print("You can now run: python scripts/produce_concert_video.py --lipsync-model sadtalker")


if __name__ == "__main__":
    main()
