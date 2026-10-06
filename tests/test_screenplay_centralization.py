"""Targeted unit tests for centralized base screenplay engine, tier contract, and zero fallback policy."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest

from src.studios.base_screenplay_engine import execute_directorial_screenplay
from src.studios.screenplay_models import (
    AmbientScenePrompt,
    AmbientStoryboard,
    RelaxSceneDirective,
    RelaxScreenplay,
    relax_to_ambient_storyboard,
)
from src.studios.base_directorial_prompt import build_base_directorial_prompt


def test_screenplay_models_tier_contract():
    """Verify tier and motion metadata fields exist on RelaxScreenplay and AmbientStoryboard."""
    scene = RelaxSceneDirective(
        scene_index=1,
        location_hub="Charminar",
        visual_prompt="Historic 16:9 aerial vista",
        motion_prompt="Stationary locked frame",
        domain="landscape_solid",
        motion_type="ken_burns",
        camera_movement="slow_drone_forward",
        motion_rationale="Rigid masonry preservation",
        duration_seconds=5.0,
    )
    sp = RelaxScreenplay(
        production_id="EP-001",
        title="Hyderabad 4K",
        story_topic="Heritage tour",
        genre="travel/scenic",
        tier="balanced",
        scenes=[scene],
    )
    assert sp.tier == "balanced"
    assert sp.scenes[0].motion_type == "ken_burns"
    assert sp.scenes[0].camera_movement == "slow_drone_forward"

    # Test conversion to AmbientStoryboard
    sb = relax_to_ambient_storyboard(sp)
    assert sb.tier == "balanced"
    assert len(sb.scenes) == 1
    assert sb.scenes[0].motion_type == "ken_burns"
    assert sb.scenes[0].camera_movement == "slow_drone_forward"
    assert sb.scenes[0].motion_rationale == "Rigid masonry preservation"


def test_base_directorial_prompt_contains_tier_in_schema():
    """Verify build_base_directorial_prompt mandates tier in the JSON schema instruction."""
    prompt = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="travel",
        custom_prompt="Hyderabad",
        duration_seconds=15.0,
        num_shots=3,
        tier="balanced",
    )
    assert '"tier": "balanced"' in prompt
    assert "- Motion & Quality Tier: balanced" in prompt


@pytest.mark.asyncio
async def test_execute_directorial_screenplay_success(tmp_path: Path):
    """Verify execute_directorial_screenplay writes raw JSON artifact and validates RelaxScreenplay."""
    mock_payload = {
        "production_id": "EP-001",
        "title": "Hyderabad 4K Drone Showcase",
        "story_topic": "Panoramic aerial tour",
        "genre": "travel/scenic",
        "sub_genre": "cities",
        "primary_archetype": "cities",
        "tier": "balanced",
        "total_duration_seconds": 15.0,
        "scenes": [
            {
                "scene_index": 1,
                "location_hub": "Charminar",
                "shot_type": "wide_panoramic_picturesque",
                "camera_rig": "slow_drone_forward",
                "visual_prompt": "Photorealistic 4K Charminar aerial view at 5500K",
                "motion_prompt": "Rigid locked frame, cloudless sky",
                "domain": "landscape_solid",
                "motion_type": "ken_burns",
                "camera_movement": "slow_drone_forward",
                "motion_rationale": "Zero drift for heritage architecture",
                "duration_seconds": 5.0,
            }
        ]
    }
    raw_path = tmp_path / "raw_gemini_screenplay.json"

    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json = lambda: {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(mock_payload)}]
                }
            }
        ]
    }

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp

    with patch("src.core.config.settings.llm.google_api_key", "test_mock_key"), \
         patch("src.providers.base.HTTPClientPool.get_client", return_value=mock_client):
        sp = await execute_directorial_screenplay(
            sys_prompt="test prompt",
            raw_output_path=raw_path,
            tier="balanced",
            genre="travel/scenic",
        )

    assert sp.production_id == "EP-001"
    assert sp.tier == "balanced"
    assert sp.scenes[0].motion_type == "ken_burns"
    assert raw_path.exists()
    assert "Hyderabad 4K Drone Showcase" in raw_path.read_text("utf-8")


@pytest.mark.asyncio
async def test_execute_directorial_screenplay_zero_fallback_on_api_error(tmp_path: Path):
    """Verify zero-fallback policy: HTTP 402 or other failure strictly halts with RuntimeError."""
    mock_resp = AsyncMock()
    mock_resp.status_code = 402
    mock_resp.text = '{"error": {"message": "Prepayment credits depleted", "status": "RESOURCE_EXHAUSTED"}}'

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_resp

    with patch("src.core.config.settings.llm.google_api_key", "test_mock_key"), \
         patch("src.providers.base.HTTPClientPool.get_client", return_value=mock_client):
        with pytest.raises(RuntimeError, match="Production halted: Screenplay formulation failed: Gemini API error"):
            await execute_directorial_screenplay(
                sys_prompt="test prompt",
                raw_output_path=tmp_path / "raw.json",
                tier="balanced",
            )


@pytest.mark.asyncio
async def test_screenplay_disk_cache_reuse_on_resynthesis(tmp_path: Path):
    """Verify produce_channel_video reuses existing screenplay on disk without calling Gemini."""
    from src.services.channel_production_service import produce_channel_video

    ep_dir = tmp_path / "user-test" / "channels" / "skylinediariesindia4k" / "EP-001"
    ep_dir.mkdir(parents=True, exist_ok=True)
    sp_file = ep_dir / "screenplay.json"
    mock_sp_data = {
        "production_id": "EP-001",
        "title": "Hyderabad 4K Cached Title",
        "story_topic": "Panoramic aerial tour",
        "genre": "travel/scenic",
        "tier": "balanced",
        "total_duration_seconds": 15.0,
        "scenes": [
            {
                "scene_index": 1,
                "location_hub": "Charminar",
                "visual_prompt": "Charminar aerial view",
                "motion_prompt": "Stationary",
                "motion_type": "ken_burns",
                "duration_seconds": 5.0,
            }
        ]
    }
    sp_file.write_text(json.dumps(mock_sp_data), encoding="utf-8")

    # Patch dispatch_studio_director to fail if called
    with patch("src.services.channel_production_service.dispatch_studio_director") as mock_director, \
         patch("src.services.channel_production_service.storage_service.get_user_container_path", return_value=tmp_path / "user-test"), \
         patch("src.services.channel_production_service.BaseChannelPipeline.execute", new_callable=AsyncMock) as mock_pipeline:
        mock_pipeline.return_value = {"success": True, "artifacts": []}

        # Simulate Re-Synthesize call (not script_only, not force_rerun)
        res = await produce_channel_video(
            channel_id="skylinediariesindia4k",
            prompt="",
            duration_seconds=5.0,
            episode_id="EP-001",
            user_id="test@example.com",
            script_only=False,
            photos_only=False,
            motion_only=False,
            force_rerun=False,
            tier="balanced",
        )

        mock_director.assert_not_called()
        assert res["title"] == "Hyderabad 4K Cached Title"
        assert res["duration_seconds"] == 15.0
        assert mock_pipeline.call_count == 1
        # Check that pipeline received the cached screenplay
        call_kwargs = mock_pipeline.call_args.kwargs
        assert call_kwargs["sb"].title == "Hyderabad 4K Cached Title"
        assert call_kwargs["tier"] == "balanced"

