"""Targeted unit tests for Master 4K Duration and Audio Fade-Out Export.

Tests:
1. assemble_4k_master enforces target_duration_sec on video (-t) and audio (-af afade).
2. assemble_dual_masters invalidates cache on target duration mismatch.
Runs 100% locally with offline mocks ($0.00 spend).
"""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.services.broadcast_export_service import assemble_4k_master, assemble_dual_masters


def test_assemble_4k_master_respects_target_duration(tmp_path):
    """assemble_4k_master must cap output at target_duration_sec and apply audio fade-out."""
    clip1 = tmp_path / "c1.mp4"
    clip2 = tmp_path / "c2.mp4"
    clip3 = tmp_path / "c3.mp4"
    audio = tmp_path / "music_suno_240s.mp3"
    out = tmp_path / "master_4k_ambient.mp4"

    for c in [clip1, clip2, clip3, audio]:
        c.write_bytes(b"dummy_media_bytes" * 100)

    with patch("src.services.broadcast_export_service.get_media_duration", return_value=5.0), \
         patch("src.services.broadcast_export_service.build_adaptive_resolution_filter", return_value="scale=3840:2160"), \
         patch("subprocess.run") as mock_run:

        mock_run.return_value = MagicMock(returncode=0)

        assemble_4k_master(
            seamless_clips=[clip1, clip2, clip3],
            audio_path=audio,
            out_master=out,
            target_duration_sec=120.0,
        )

        assert mock_run.called
        cmd = mock_run.call_args[0][0]
        # Must have -t 120.00
        assert "-t" in cmd
        t_idx = cmd.index("-t")
        assert cmd[t_idx + 1] == "120.00"

        # Must have audio fade-out ending at 120.00 (st=117.00:d=3.00)
        assert "-af" in cmd
        af_idx = cmd.index("-af")
        assert "afade=t=out:st=117.00:d=3.00" in cmd[af_idx + 1]


def test_assemble_dual_masters_rebuilds_on_duration_mismatch(tmp_path):
    """assemble_dual_masters must invalidate cached master if existing duration differs from target."""
    clip1 = tmp_path / "c1.mp4"
    audio = tmp_path / "music.mp3"
    master = tmp_path / "master_4k_ambient.mp4"

    clip1.write_bytes(b"clip" * 100)
    audio.write_bytes(b"audio" * 100)
    # Existing cached master of 240s
    master.write_bytes(b"master" * 1000)

    with patch("src.services.broadcast_export_service.build_seamless_forward_cineloop", return_value=clip1), \
         patch("src.services.broadcast_export_service.get_media_duration", return_value=240.0), \
         patch("src.services.broadcast_export_service.assemble_4k_master") as mock_asm:

        # User requests 120s preview
        assemble_dual_masters(
            video_clips=[clip1],
            audio_path=audio,
            ep_dir=tmp_path,
            target_duration_sec=120.0,
        )

        # Must trigger rebuild because cached is 240s and target is 120s
        assert mock_asm.called
        assert mock_asm.call_args[1]["target_duration_sec"] == 120.0
