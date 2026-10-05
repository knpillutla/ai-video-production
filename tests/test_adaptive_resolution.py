import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.services.ambient_export_service import probe_clip_geometry, build_adaptive_resolution_filter


def test_probe_clip_geometry():
    fake_clip = Path('fake_clip.mp4')
    mock_res = MagicMock()
    mock_res.stderr = 'Stream #0:0: Video: h264, yuv420p, 3840x2160, 24 fps'
    with patch('subprocess.run', return_value=mock_res):
        w, h = probe_clip_geometry(fake_clip)
        assert (w, h) == (3840, 2160)


def test_build_adaptive_resolution_filter_native_4k():
    fake_clip = Path('fake_clip.mp4')
    with patch('src.services.ambient_export_service.probe_clip_geometry', return_value=(3840, 2160)):
        filt = build_adaptive_resolution_filter(fake_clip, 3840, 2160)
        assert filt == 'setsar=1'


def test_build_adaptive_resolution_filter_1080p():
    fake_clip = Path('fake_clip.mp4')
    with patch('src.services.ambient_export_service.probe_clip_geometry', return_value=(1920, 1080)):
        filt = build_adaptive_resolution_filter(fake_clip, 3840, 2160)
        assert 'scale=3840:2160:flags=lanczos,setsar=1' in filt
        assert 'pad=' not in filt


def test_build_adaptive_resolution_filter_720p():
    fake_clip = Path('fake_clip.mp4')
    with patch('src.services.ambient_export_service.probe_clip_geometry', return_value=(1280, 720)):
        filt = build_adaptive_resolution_filter(fake_clip, 3840, 2160)
        assert 'scale=3840:2160:flags=lanczos,setsar=1' in filt
        assert 'pad=' not in filt


def test_build_adaptive_resolution_filter_square_cropped():
    fake_clip = Path('fake_clip.mp4')
    with patch('src.services.ambient_export_service.probe_clip_geometry', return_value=(1024, 1024)):
        filt = build_adaptive_resolution_filter(fake_clip, 3840, 2160)
        assert 'pad=3840:2160' in filt
