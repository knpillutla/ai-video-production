"""Unit & Integration tests for Declarative Model Selection and Video Adapters."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.config.artifact_models import get_artifact_profile, get_scenario_config
from src.providers.dance.fal_video_factory import resolve_video_motion_adapter
from src.providers.dance.fal_h3_max_turbo import FalH3MaxTurboAdapter
from src.providers.dance.fal_seedance import FalSeedanceAdapter
from src.providers.dance.fal_kling import FalKlingAdapter


def test_model_selection_config_loading():
    """Verify that model_selection_config.json loads correctly across profiles."""
    dev_prof = get_artifact_profile("development")
    assert dev_prof.profile_name == "development"
    assert dev_prof.motion_video.provider == "Fal.ai"
    assert "H3 Max" in dev_prof.motion_video.model

    prod_prof = get_artifact_profile("production")
    assert prod_prof.profile_name == "production"
    assert prod_prof.motion_video.provider == "Fal.ai"
    assert "Seedance 2.5" in prod_prof.motion_video.model


def test_resolve_video_motion_adapter_dev_profile():
    """Verify that development profile (--dev) dynamically resolves to FalH3MaxTurboAdapter."""
    adapter = resolve_video_motion_adapter(profile="development")
    assert isinstance(adapter, FalH3MaxTurboAdapter)
    assert "h3-max" in adapter.endpoint


def test_resolve_video_motion_adapter_prod_profile():
    """Verify that production profile (--live) dynamically resolves to FalSeedanceAdapter."""
    adapter = resolve_video_motion_adapter(profile="production")
    assert isinstance(adapter, FalSeedanceAdapter)
    assert "seedance-2.5" in adapter.endpoint


def test_resolve_video_motion_adapter_overrides():
    """Verify manual model override dynamically instantiates proper adapter."""
    kling_adapter = resolve_video_motion_adapter(model_override="Kling 1.5 Pro")
    assert isinstance(kling_adapter, FalKlingAdapter)

    seedance_adapter = resolve_video_motion_adapter(model_override="ByteDance Seedance 2.5")
    assert isinstance(seedance_adapter, FalSeedanceAdapter)

    turbo_adapter = resolve_video_motion_adapter(model_override="H3 Max Turbo")
    assert isinstance(turbo_adapter, FalH3MaxTurboAdapter)

    from src.providers.dance.fal_hunyuan import FalHunyuanAdapter
    hunyuan_adapter = resolve_video_motion_adapter(model_override="Tencent Hunyuan Video v1.5")
    assert isinstance(hunyuan_adapter, FalHunyuanAdapter)


@pytest.mark.asyncio
async def test_fal_h3_max_turbo_mock_fallback(tmp_path: Path):
    """Verify FalH3MaxTurboAdapter local fallback operates without paid API calls."""
    adapter = FalH3MaxTurboAdapter()
    out_video = tmp_path / "turbo_scene.mp4"
    dummy_img = tmp_path / "scene_00.jpg"
    dummy_img.write_bytes(b"dummy image data")

    with patch("src.providers.dance.fal_h3_max_turbo.is_mock_mode", return_value=True), \
         patch("src.scripts.local_pan_zoom.render_steadycam_clip", return_value=out_video):
        url, path = await adapter.generate_video(
            image_url=str(dummy_img),
            motion_prompt="Smooth slow forward tracking shot",
            output_path=out_video,
            duration=5,
            force_live=False,
        )
        assert path == out_video
        assert "file://" in url


@pytest.mark.asyncio
async def test_fal_seedance_mock_fallback(tmp_path: Path):
    """Verify FalSeedanceAdapter local fallback operates without paid API calls."""
    adapter = FalSeedanceAdapter()
    out_video = tmp_path / "seedance_scene.mp4"
    dummy_img = tmp_path / "scene_00.jpg"
    dummy_img.write_bytes(b"dummy image data")

    with patch("src.providers.dance.fal_seedance.is_mock_mode", return_value=True), \
         patch("src.scripts.local_pan_zoom.render_steadycam_clip", return_value=out_video):
        url, path = await adapter.generate_video(
            image_url=str(dummy_img),
            motion_prompt="Leisurely walking cadence steadycam glide",
            output_path=out_video,
            duration=10,
            force_live=False,
        )
        assert path == out_video
        assert "file://" in url


@pytest.mark.asyncio
async def test_artifact_caching_idempotency(tmp_path: Path):
    """Verify that existing video artifacts on disk are reused immediately without re-rendering."""
    cached_video = tmp_path / "cached_scene.mp4"
    cached_video.write_bytes(b"0" * 60_000)  # > 50KB to simulate existing render

    adapter = FalSeedanceAdapter()
    url, path = await adapter.generate_video(
        image_url="dummy_img.jpg",
        motion_prompt="Test motion",
        output_path=cached_video,
        duration=10,
        force_live=True,  # Even with force_live=True, cache hit should return early
    )
    assert path == cached_video
    assert url == f"file://{cached_video}"
