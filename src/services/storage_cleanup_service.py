"""Robust Storage Cleanup Service for Windows and Linux.

Provides guaranteed folder deletion that bypasses Windows file watcher locks,
read-only permission traps, and tidies empty parent production directories.
"""

from __future__ import annotations

import gc
import os
import shutil
import stat
import subprocess
import time
from pathlib import Path
from src.core.telemetry import logger


def _remove_readonly(func, path, exc_info):
    """Clear the read-only bit and retry removal."""
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception as e:
        logger.debug(f"readonly_unprotect_failed for {path}: {e}")


def robust_remove_directory(path: Path | str, max_retries: int = 3) -> bool:
    """Robustly delete a directory tree on Windows or Linux.
    
    Retries across transient file watcher locks and falls back to native OS deletion
    if Python's shutil.rmtree leaves an empty directory behind.
    """
    target = Path(path).resolve()
    if not target.exists():
        return True

    # Attempt 1: Standard rmtree with readonly un-protect handler
    for attempt in range(1, max_retries + 1):
        try:
            gc.collect()
            shutil.rmtree(target, onerror=_remove_readonly)
        except Exception as ex:
            logger.debug(f"rmtree_attempt_{attempt}_failed: {target} -> {ex}")

        if not target.exists():
            return True

        # Brief backoff allowing Windows file watchers to release handles
        time.sleep(0.12 * attempt)

    # Attempt 2: Direct rmdir if only the folder shell remains
    if target.is_dir():
        try:
            target.rmdir()
            if not target.exists():
                return True
        except Exception:
            pass

    # Attempt 3: OS-level native purge fallback on Windows
    if os.name == "nt" and target.exists():
        try:
            cmd = f'cmd.exe /c rd /s /q "{target}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
            if res.returncode == 0 and not target.exists():
                logger.info(f"native_rd_purged_directory: {target}")
                return True
        except Exception as e_cmd:
            logger.warning(f"native_rd_failed: {target} -> {e_cmd}")

    return not target.exists()


PROTECTED_DIR_NAMES = {
    "networks",
    "channels",
    "productions",
    "documentary",
    "relaxation",
    "audio_vault",
    "storage",
}


def cleanup_empty_parent_production(parent_dir: Path | str, user_container: Path | str) -> bool:
    """Prune empty parent production directory after episode deletion."""
    try:
        p_dir = Path(parent_dir).resolve()
        u_cont = Path(user_container).resolve()

        # Safety: must be strictly inside the user container and not a protected structural dir
        if not str(p_dir).startswith(str(u_cont)):
            return False
        if p_dir == u_cont or p_dir.name.lower() in PROTECTED_DIR_NAMES:
            return False

        # Only prune if directory exists, is a dir, and is completely empty
        if p_dir.is_dir() and not any(p_dir.iterdir()):
            p_dir.rmdir()
            logger.info(f"pruned_empty_production_directory: {p_dir}")
            return True
    except Exception as e:
        logger.debug(f"cleanup_empty_parent_production_skipped: {e}")
    return False
