"""Deterministic offline test for walking tour production pipeline."""

from pathlib import Path
from unittest.mock import patch
import pytest

from scripts.produce_walking_tour import (
    WALKING_PRESETS,
    build_custom_walking_prompts,
    produce_walking_tour,
)


def test_walking_presets_structure():
    assert "swiss_alps" in WALKING_PRESETS
    assert "portugal_coastal" in WALKING_PRESETS
    assert "kyoto_bamboo" in WALKING_PRESETS
    for name, prompts in WALKING_PRESETS.items():
        assert len(prompts) == 10
        for p in prompts:
            assert "First-person POV" in p
            assert len(p) > 30


def test_build_custom_walking_prompts():
    prompts = build_custom_walking_prompts("Venice Grand Canal", num_shots=5)
    assert len(prompts) == 5
    assert all("Venice Grand Canal" in p for p in prompts)
    assert all("First-person POV" in p for p in prompts)


@pytest.mark.asyncio
async def test_produce_walking_tour_offline_mock(tmp_path: Path):
    out_dir = tmp_path / "test_tour"

    # Mock image generation and drone rendering to guarantee $0.00 spend and fast execution
    async def fake_generate_to_file(self, prompt, output_path, **kwargs):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x" * 15000)
        return f"file://{p}", p

    def fake_drone_render(image_path, output_path, **kwargs):
        p = Path(output_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"dummy_mp4_bytes_12345")
        return p

    def fake_subprocess_run(cmd, *args, **kwargs):
        # Emulate successful ffmpeg run by creating the master output file
        target_path = Path(cmd[-1])
        target_path.write_bytes(b"master_video_content")
        class FakeResult:
            returncode = 0
        return FakeResult()

    with patch("src.providers.visual.fal_zimage.FalZImageAdapter.generate_to_file", side_effect=fake_generate_to_file, autospec=True):
        with patch("scripts.produce_walking_tour.render_perspective_drone_clip_sync", side_effect=fake_drone_render):
            with patch("scripts.produce_walking_tour.subprocess.run", side_effect=fake_subprocess_run):
                master = await produce_walking_tour(
                    preset_name="swiss_alps",
                    num_shots=2,
                    duration_per_shot=3.0,
                    output_dir=out_dir,
                    force_live=False,
                    with_audio=False,
                )
                assert master.exists()
                assert (out_dir / "keyframes" / "shot_01.jpg").exists()
                assert (out_dir / "keyframes" / "shot_02.jpg").exists()
                assert (out_dir / "clips" / "clip_01.mp4").exists()
                assert (out_dir / "clips" / "clip_02.mp4").exists()
                assert (out_dir / "concat_list.txt").exists()
