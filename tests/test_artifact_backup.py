"""Targeted offline unit tests for Artifact Backup Service (Single-Shot Regeneration)."""
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from src.services.artifact_backup_service import backup_keyframe, backup_motion_clip


def test_backup_keyframe():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ep_dir = Path(tmp_dir)
        # Create a mock keyframe > 1000 bytes
        kf_path = ep_dir / "keyframe_p2.jpg"
        kf_path.write_bytes(b"A" * 1500)

        backed_up = backup_keyframe(ep_dir, shot_index=2, model_name="FLUX.1-dev")
        assert backed_up is not None
        assert backed_up.is_file()

        backup_dir = ep_dir / "backups" / "images" / "flux.1-dev"
        assert backup_dir.is_dir()
        assert (backup_dir / "keyframe_p2.jpg").is_file()
        assert (backup_dir / "keyframe_p2.jpg").stat().st_size == 1500

        # Check timestamped file is also created
        stamped = list(backup_dir.glob("keyframe_p2_*.jpg"))
        assert len(stamped) >= 1


def test_backup_motion_clip():
    with tempfile.TemporaryDirectory() as tmp_dir:
        ep_dir = Path(tmp_dir)
        # Create a mock motion clip > 1000 bytes
        mc_path = ep_dir / "motion_p3.mp4"
        mc_path.write_bytes(b"M" * 2000)

        # Also mock a nature clip
        nat_path = ep_dir / "motion_nature_p3.mp4"
        nat_path.write_bytes(b"N" * 1200)

        backed_up = backup_motion_clip(ep_dir, shot_index=3, model_name="wan_4k")
        assert backed_up is not None
        assert backed_up.is_file()

        backup_dir = ep_dir / "backups" / "motion" / "wan_4k"
        assert backup_dir.is_dir()
        assert (backup_dir / "motion_p3.mp4").is_file()
        assert (backup_dir / "motion_nature_p3.mp4").is_file()
        assert (backup_dir / "motion_p3.mp4").stat().st_size == 2000
