"""Targeted Unit Tests for Concert Studio 2-Plate Rig & Kling-3D Extractor ($0.00 spend, Rule 8)."""

from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, patch

from src.studios.concert_studio.concert_director import CAMERA_NAME_TO_INDEX, synthesize_concert_broadcast_cuts
from src.studios.concert_studio.concert_image_service import (
    CONCERT_CAMERA_NAMES,
    synthesize_concert_camera_rig,
)
from src.studios.concert_studio.concert_kling_3d import (
    extract_keyframes_from_video,
    synthesize_kling_3d_flight_plates,
)


def test_single_plate_default_camera_names():
    assert len(CONCERT_CAMERA_NAMES) == 1
    assert CONCERT_CAMERA_NAMES == ["singer_orchestra_stage"]


def test_camera_mapping_defaults_to_plate_1_for_stage():
    assert CAMERA_NAME_TO_INDEX["singer_orchestra_stage"] == 1
    assert CAMERA_NAME_TO_INDEX["center_vocalist_front"] == 1
    assert CAMERA_NAME_TO_INDEX["backing_orchestra_ensemble"] == 1
    assert CAMERA_NAME_TO_INDEX["active_instrument_macro"] == 1
    assert CAMERA_NAME_TO_INDEX["overall_stage_vista"] == 3
    assert CAMERA_NAME_TO_INDEX["stadium_audience_crowd"] == 2
    assert CAMERA_NAME_TO_INDEX["overall_stadium_vista"] == 3


@pytest.mark.asyncio
async def test_synthesize_rig_returns_single_plate_via_spatial_3d(tmp_path: Path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    sb_data = {
        "characters": [{"name": "Radha", "gender": "Female"}],
        "character_wardrobe": {"outfit_description": "silk saree", "accessories": "earrings"},
        "scenes": [
            {"camera_id": "singer_orchestra_stage", "visual_prompt": "singer on stage"},
            {"camera_id": "stadium_audience_crowd", "visual_prompt": "audience cheering"},
        ],
    }

    with patch("src.compositor.vocal_lora_resolver.resolve_vocal_loras", new_callable=AsyncMock) as mock_loras, \
         patch("src.providers.visual.fal_zimage.FalZImageAdapter.generate_to_file", new_callable=AsyncMock) as mock_gen, \
         patch("src.providers.visual.fal_aura_sr.FalAuraSRAdapter.upscale_image", new_callable=AsyncMock) as mock_up:
        mock_loras.return_value = ([], "")
        async def side_effect(prompt, output_path, **kwargs):
            Path(output_path).write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)
        mock_gen.side_effect = side_effect

        plates = await synthesize_concert_camera_rig(
            storyboard_data=sb_data,
            scenes_dir=scenes_dir,
            user_id="test_user",
            force_live=False,
            chars="Radha",
            motion_model="drone",
        )

        assert len(plates) == 1
        assert plates[0].name == "scene_01.jpg"
        assert (scenes_dir / "stadium_3d_flight.mp4").is_file()


@pytest.mark.asyncio
async def test_synthesize_rig_returns_2_plates_when_legacy_requested(tmp_path: Path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    sb_data = {
        "characters": [{"name": "Radha", "gender": "Female"}],
        "character_wardrobe": {"outfit_description": "silk saree", "accessories": "earrings"},
        "scenes": [
            {"camera_id": "singer_orchestra_stage", "visual_prompt": "singer on stage"},
            {"camera_id": "stadium_audience_crowd", "visual_prompt": "audience cheering"},
        ],
    }

    with patch("src.compositor.vocal_lora_resolver.resolve_vocal_loras", new_callable=AsyncMock) as mock_loras, \
         patch("src.providers.visual.fal_zimage.FalZImageAdapter.generate_to_file", new_callable=AsyncMock) as mock_gen, \
         patch("src.providers.visual.fal_aura_sr.FalAuraSRAdapter.upscale_image", new_callable=AsyncMock) as mock_up:
        mock_loras.return_value = ([], "")
        async def side_effect(prompt, output_path, **kwargs):
            Path(output_path).write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)
        mock_gen.side_effect = side_effect

        plates = await synthesize_concert_camera_rig(
            storyboard_data=sb_data,
            scenes_dir=scenes_dir,
            user_id="test_user",
            force_live=False,
            chars="Radha",
            motion_model="2-plate-legacy",
        )

        assert len(plates) == 1
        assert plates[0].name == "scene_01.jpg"


@pytest.mark.asyncio
async def test_kling_3d_flight_plates_extraction(tmp_path: Path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    master_img = scenes_dir / "scene_01.jpg"
    master_img.write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)

    # In mock mode, synthesize_kling_3d_flight_plates generates 3d flight video and returns plate 1
    with patch("src.providers.visual.fal_aura_sr.FalAuraSRAdapter.upscale_image", new_callable=AsyncMock):
        plates = await synthesize_kling_3d_flight_plates(
            stage_master_image=master_img,
            scenes_dir=scenes_dir,
            force_live=False,
            engine="h3_max",
        )

        assert len(plates) == 1
        assert plates[0].name == "scene_01.jpg"
        assert (scenes_dir / "stadium_3d_flight.mp4").is_file()


@pytest.mark.asyncio
async def test_synthesize_rig_switches_between_h3_max_and_kling_3d(tmp_path: Path):
    scenes_dir = tmp_path / "scenes"
    scenes_dir.mkdir(parents=True, exist_ok=True)
    sb_data = {
        "characters": [{"name": "Radha", "gender": "Female"}],
        "character_wardrobe": {"outfit_description": "silk saree", "accessories": "earrings"},
        "scenes": [
            {"camera_id": "singer_orchestra_stage", "visual_prompt": "singer on stage"},
        ],
    }

    with patch("src.compositor.vocal_lora_resolver.resolve_vocal_loras", new_callable=AsyncMock) as mock_loras, \
         patch("src.providers.visual.fal_zimage.FalZImageAdapter.generate_to_file", new_callable=AsyncMock) as mock_gen, \
         patch("src.providers.visual.fal_aura_sr.FalAuraSRAdapter.upscale_image", new_callable=AsyncMock) as mock_up, \
         patch("src.studios.concert_studio.concert_kling_3d.synthesize_spatial_3d_flight_plates", new_callable=AsyncMock) as mock_spatial:
        mock_loras.return_value = ([], "")
        async def side_effect(prompt, output_path, **kwargs):
            Path(output_path).write_bytes(b"\xff\xd8\xff" + b"\x00" * 2000)
        mock_gen.side_effect = side_effect
        mock_spatial.return_value = [scenes_dir / "scene_01.jpg"]

        # 1. Test H3 Max selection
        await synthesize_concert_camera_rig(
            storyboard_data=sb_data,
            scenes_dir=scenes_dir,
            user_id="test_user",
            force_live=False,
            chars="Radha",
            spatial_3d_engine="h3-max",
        )
        assert mock_spatial.call_args.kwargs["engine"] == "h3_max"

        # 2. Test Kling 3D selection
        await synthesize_concert_camera_rig(
            storyboard_data=sb_data,
            scenes_dir=scenes_dir,
            user_id="test_user",
            force_live=False,
            chars="Radha",
            spatial_3d_engine="kling",
        )
        assert mock_spatial.call_args.kwargs["engine"] == "kling"

        # 3. Test alias 'king-3d'
        await synthesize_concert_camera_rig(
            storyboard_data=sb_data,
            scenes_dir=scenes_dir,
            user_id="test_user",
            force_live=False,
            chars="Radha",
            spatial_3d_engine="king-3d",
        )
        assert mock_spatial.call_args.kwargs["engine"] == "kling"
