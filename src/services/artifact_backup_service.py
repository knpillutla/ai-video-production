"""Artifact Backup Service for Single-Shot Regeneration.

Backs up existing keyframe images and motion clips into dedicated model-named
backup subdirectories before re-creating them.
"""
from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Optional
from src.core.telemetry import logger


def backup_keyframe(ep_dir: Path, shot_index: int, model_name: Optional[str] = None) -> Optional[Path]:
    """Back up existing keyframe_p{shot_index}.jpg into backups/images/{model_name}/."""
    src_kf = ep_dir / f"keyframe_p{shot_index}.jpg"
    if not (src_kf.is_file() and src_kf.stat().st_size > 1000):
        return None

    safe_model = (model_name or "original").strip().lower().replace(" ", "_").replace("/", "_")
    backup_dir = ep_dir / "backups" / "images" / safe_model
    backup_dir.mkdir(parents=True, exist_ok=True)

    dest_named = backup_dir / f"keyframe_p{shot_index}.jpg"
    dest_stamped = backup_dir / f"keyframe_p{shot_index}_{int(time.time())}.jpg"
    shutil.copy2(src_kf, dest_named)
    shutil.copy2(src_kf, dest_stamped)
    logger.info(f"keyframe_backed_up: shot={shot_index} model={safe_model} dest={dest_named}")
    return dest_named


def backup_motion_clip(ep_dir: Path, shot_index: int, model_name: Optional[str] = None) -> Optional[Path]:
    """Back up existing motion_p{shot_index}.mp4 into backups/motion/{model_name}/."""
    src_clip = ep_dir / f"motion_p{shot_index}.mp4"
    if not (src_clip.is_file() and src_clip.stat().st_size > 1000):
        return None

    safe_model = (model_name or "original").strip().lower().replace(" ", "_").replace("/", "_")
    backup_dir = ep_dir / "backups" / "motion" / safe_model
    backup_dir.mkdir(parents=True, exist_ok=True)

    dest_named = backup_dir / f"motion_p{shot_index}.mp4"
    dest_stamped = backup_dir / f"motion_p{shot_index}_{int(time.time())}.mp4"
    shutil.copy2(src_clip, dest_named)
    shutil.copy2(src_clip, dest_stamped)

    src_nat = ep_dir / f"motion_nature_p{shot_index}.mp4"
    if src_nat.is_file() and src_nat.stat().st_size > 1000:
        shutil.copy2(src_nat, backup_dir / f"motion_nature_p{shot_index}.mp4")

    logger.info(f"motion_clip_backed_up: shot={shot_index} model={safe_model} dest={dest_named}")
    return dest_named
