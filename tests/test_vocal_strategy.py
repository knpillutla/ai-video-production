"""Offline Unit Tests for Vocal Song & Lyrical Video Strategy."""

import json
from pathlib import Path
import pytest
from src.compositor.genre_strategies import resolve_strategy
from src.compositor.vocal_compositor import (
    build_vocal_subtitles,
    probe_audio_duration,
)


def test_vocal_strategy_properties():
    """Verify VocalStrategy configuration and protocol adherence."""
    strategy = resolve_strategy("vocal")
    assert strategy.genre_id == "vocal"
    assert strategy.default_fps == 30
    assert strategy.audio_mode == "song"
    assert strategy.lipsync_mode == "none"
    assert strategy.enable_voice_over is False
    assert strategy.enable_bgm is True


def test_vocal_prompt_and_schema_telugu():
    """Verify Gemini prompt and schema for Telugu romantic duet."""
    strategy = resolve_strategy("vocal")
    prompt = strategy.build_gemini_prompt(
        title="Prema Sandram",
        duration_seconds=90,
        language="te",
        music_style="soft romantic melody",
        similar_to="Inkem Inkem Inkem Kaavaale",
        country="India",
        culture="telangana",
        gender="duet",
    )
    assert "Inkem Inkem" in prompt
    assert "telangana" in prompt.lower()
    assert "graceful SLIM build" in prompt
    assert "MEDIUM BUILT" in prompt
    assert "z_image" in prompt

    schema = strategy.build_gemini_schema()
    assert schema["type"] == "OBJECT"
    assert "prompts_by_model" in schema["properties"]
    assert "lyrics_segments" in schema["properties"]
    assert "animation_timeline" in schema["properties"]
    assert "zero outfit distortion" in prompt.lower()
    assert "animation_timeline" in prompt


def test_vocal_fx_filter_complex_compilation(tmp_path: Path):
    """Verify single-pass FFmpeg filter complex compilation with timeline cues."""
    from src.compositor.vocal_fx import compile_vocal_filter_complex
    cues = [
        {"start_time": 0.0, "end_time": 10.0, "camera_motion": "slow_zoom_in", "effect_type": "golden_light_leak"},
        {"start_time": 10.0, "end_time": 25.0, "camera_motion": "pan_left_to_right", "effect_type": "floating_petals_up"},
    ]
    sub_file = tmp_path / "sub.ass"
    sub_file.write_text("[Script Info]\nTitle: Test\n", encoding="utf-8")
    extra_args, filter_str = compile_vocal_filter_complex(cues, total_duration=30.0, sub_path=sub_file, fps=30)
    assert len(extra_args) >= 4  # -stream_loop -1 -i ...
    assert ("scale=3840:2160" in filter_str or "zoompan" in filter_str)
    assert "colorkey=" in filter_str
    assert "fx_alpha" in filter_str
    assert "format=auto" in filter_str
    assert "subtitles=" in filter_str
    assert "loudnorm=" in filter_str


def test_build_vocal_subtitles_center_alignment(tmp_path: Path):
    """Verify that subtitles are generated with center alignment (Alignment=5) and modern font."""
    sb_data = {
        "title_localized": "కరిగే వెన్నెలే",
        "lyrics_segments": [
            {"start": 0.0, "end": 4.5, "text": "కరిగే వెన్నెలే నాతో మాట్లాడే వేళ"},
            {"start": 4.5, "end": 9.0, "text": "తీరని కోరికే ప్రాణమైన రాగాల తీరం"},
        ],
    }
    out_ass = tmp_path / "test_lyrics.ass"
    res_path, fonts_dir = build_vocal_subtitles(sb_data, language="te", out_ass_path=out_ass, total_duration=10.0)
    assert res_path.is_file()
    assert fonts_dir.is_dir()
    content = res_path.read_text(encoding="utf-8")
    assert ("Mandali" in content or "Noto Sans Telugu" in content or "Nirmala UI" in content or "Arial" in content or "Gidugu" in content)
    assert ",5,80,80," in content  # Alignment=5 (center)
    assert "కరిగే వెన్నెలే" in content


def test_probe_audio_duration_missing_fallback(tmp_path: Path):
    """Verify probe_audio_duration returns sensible fallback on missing file."""
    fake_path = tmp_path / "non_existent.wav"
    assert probe_audio_duration(fake_path) == 60.0


def test_core_asset_and_lora_service_network_resolution(tmp_path: Path):
    """Verify CoreAssetService and CoreLoraService register and resolve network LoRAs."""
    from src.services.core_asset_service import core_asset_service
    from src.services.core_lora_service import CharacterLoraProfile, core_lora_service

    profile = CharacterLoraProfile(
        name="Siri",
        gender="female",
        lora_url="https://fal.media/files/test/siri_flux.safetensors",
        trigger_word="SIRI_TE",
        scale=1.0,
        body_composition="graceful medium-thin build with natural feminine curves",
    )
    core_lora_service.register_character_lora(
        user_id="test_user", network="telugu_melody", character_key="female_lead", profile=profile
    )

    resolved = core_lora_service.resolve_character_loras(user_id="test_user", network="telugu_melody")
    assert len(resolved) == 1
    assert resolved[0]["path"] == "https://fal.media/files/test/siri_flux.safetensors"
    assert resolved[0]["trigger_word"] == "SIRI_TE"

    # Test explicit override takes precedence
    override = [{"path": "https://custom.lora/override.safetensors", "scale": 0.8}]
    res_override = core_lora_service.resolve_character_loras(
        user_id="test_user", network="telugu_melody", explicit_loras=override
    )
    assert res_override == override

    # Test prompt cue injection
    prompt = "A stunning cinematic couple looking at sunset"
    enhanced = core_lora_service.inject_lora_prompt_cues(prompt, resolved)
    assert enhanced.startswith("SIRI_TE, ")


def test_vocal_multi_image_filter_complex_xfade(tmp_path: Path):
    """Verify compile_vocal_filter_complex generates xfade crossfades when image_count > 1."""
    from src.compositor.vocal_fx import compile_vocal_filter_complex

    cues = [{"start_time": 0.0, "end_time": 90.0, "camera_motion": "slow_zoom_in", "effect_type": "golden_light_leak"}]
    sub_file = tmp_path / "sub.ass"
    sub_file.write_text("[Script Info]\nTitle: Test\n", encoding="utf-8")

    extra_args, filter_str = compile_vocal_filter_complex(
        cues, total_duration=90.0, sub_path=sub_file, fps=30, image_count=3
    )
    assert "[v_seg_0]" in filter_str
    assert "[v_seg_1]" in filter_str
    assert "[v_seg_2]" in filter_str
    assert "xfade=transition=fade" in filter_str
    assert "[3:a]loudnorm=" in filter_str


def test_vocal_strategy_location_fidelity():
    """Verify that user-provided setting/location theme (e.g. Swiss Alps) is explicitly forwarded into Gemini prompt."""
    strategy = resolve_strategy("vocal")
    prompt = strategy.build_gemini_prompt(
        title="Soulful Romantic Melody",
        duration_seconds=210,
        language="te",
        theme="romantic melody song in swiss alps",
        art_style="Swiss Alpine Grindelwald 8K Scenic Nature",
        num_images=3,
    )
    assert "romantic melody song in swiss alps" in prompt
    assert "Swiss Alps" in prompt
    assert "SETTING & SCENIC LOCATION FIDELITY" in prompt
    assert "MULTI-SCENE ROTATION (3 SCENES" in prompt


@pytest.mark.asyncio
async def test_synthesize_vocal_scenes_4k_upscale(tmp_path: Path):
    """Verify synthesize_vocal_scenes immediately upscales images to exact 3840x2160 4K UHD."""
    import cv2
    from src.compositor.vocal_image_service import synthesize_vocal_scenes

    sb_data = {
        "prompts_by_model": {"z_image": "Romantic couple in Swiss Alps"},
        "scenes": [{"scene_index": 1, "visual_prompt": "Romantic couple near alpine lake"}],
        "characters": [{"seed": 12345}],
    }
    scenes_dir = tmp_path / "scenes"
    paths = await synthesize_vocal_scenes(storyboard_data=sb_data, scenes_dir=scenes_dir, num_images=1, force_live=False)
    assert len(paths) == 1
    assert paths[0].is_file()

    img = cv2.imread(str(paths[0]))
    assert img is not None
    assert img.shape == (2160, 3840, 3), f"Expected 4K (2160, 3840, 3), got {img.shape}"



