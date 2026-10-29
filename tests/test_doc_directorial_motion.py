"""Targeted unit tests for Pass 2 Gemini Directorial Motion & Audio Cadence Service.

Runs 100% locally and offline ($0.00 API expenditure) per Rule 8.
"""
import pytest
from src.studios.documentary_studio.doc_directorial_motion_service import (
    build_pass2_directorial_prompt,
    _fallback_pass2_allocation,
    execute_pass2_directorial_motion,
)


def test_build_pass2_directorial_prompt():
    raw_sp = {
        "title": "Fiji: Sovereign Archipelago",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "ISLAND GEOGRAPHY",
                "origin_coords": [-18.1416, 178.4419],
                "shots": [
                    {"shot_index": 1, "shot_type": "wide", "visual_prompt": "Aerial view of Suva harbor", "origin_coords": [-18.1416, 178.4419]},
                    {"shot_index": 2, "shot_type": "medium", "visual_prompt": "Local market with traders", "origin_coords": [-18.1416, 178.4419]},
                ],
            }
        ],
    }
    chapter_durs = {1: 16.50}
    prompt = build_pass2_directorial_prompt(raw_sp, chapter_durs, execution_mode="prod")

    assert "Fiji: Sovereign Archipelago" in prompt
    assert "16.50 seconds" in prompt
    assert "[-18.1416, 178.4419]" in prompt
    assert "local_drone" in prompt
    assert "kling_v3_4k" in prompt
    assert "movements" in prompt


def test_fallback_pass2_allocation_zero_drift():
    raw_sp = {
        "title": "Fiji Dossier",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "CHAPTER 1",
                "origin_coords": [-18.1416, 178.4419],
                "shots": [
                    {"shot_index": 1, "visual_prompt": "Vista 1", "motion_type": "ken_burns"},
                    {"shot_index": 2, "visual_prompt": "Living market", "motion_type": "ai_diffusion"},
                ],
            },
            {
                "chapter_index": 2,
                "chapter_title": "CHAPTER 2",
                "origin_coords": [-17.8, 177.4],
                "shots": [
                    {"shot_index": 1, "visual_prompt": "Coral reef", "motion_type": "ken_burns"},
                    {"shot_index": 2, "visual_prompt": "Coast road", "motion_type": "ken_burns"},
                ],
            },
        ],
    }
    chapter_durs = {1: 15.35, 2: 12.80}
    res = _fallback_pass2_allocation(raw_sp, chapter_durs, execution_mode="prod")

    # Audio duration + 3.0s visual padding per chapter
    expected_ch1_dur = 15.35 + 3.0
    expected_ch2_dur = 12.80 + 3.0
    assert res["total_duration_seconds"] == round(expected_ch1_dur + expected_ch2_dur, 2)

    ch1 = res["chapters"][0]
    assert ch1["visual_padding_seconds"] == 3.0
    assert ch1["chapter_total_duration"] == round(expected_ch1_dur, 2)
    assert len(ch1["shots"]) == 3  # Mandated 3-shot coverage (Aerial, Top View, Detail)
    ch1_durs = [s["duration_seconds"] for s in ch1["shots"]]
    assert round(sum(ch1_durs), 2) == round(expected_ch1_dur, 2)
    assert ch1["shots"][0]["shot_type"] == "wide_aerial_panoramic"
    assert "movements" in ch1["shots"][0]["model_configs"]["local_drone"]
    assert ch1["shots"][1]["shot_type"] == "top_view_orbital"
    assert ch1["shots"][2]["shot_type"] == "ground_tactile_detail"

    ch2 = res["chapters"][1]
    assert ch2["visual_padding_seconds"] == 3.0
    assert ch2["chapter_total_duration"] == round(expected_ch2_dur, 2)
    assert len(ch2["shots"]) == 3
    ch2_durs = [s["duration_seconds"] for s in ch2["shots"]]
    assert round(sum(ch2_durs), 2) == round(expected_ch2_dur, 2)


@pytest.mark.asyncio
async def test_execute_pass2_directorial_motion_offline_fallback(tmp_path):
    out_file = tmp_path / "raw_gemini_screenplay.json"
    raw_sp = {
        "title": "Offline Test",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "FOUNDATIONS",
                "shots": [{"shot_index": 1, "visual_prompt": "Castle view"}],
            }
        ],
    }
    chapter_durs = {1: 10.0}

    # Runs offline with allow_fallback=True ($0.00 cost)
    res = await execute_pass2_directorial_motion(
        screenplay_data=raw_sp,
        chapter_durations=chapter_durs,
        raw_output_path=out_file,
        allow_fallback=True,
    )
    assert res is not None
    assert out_file.is_file()
    assert res["chapters"][0]["chapter_audio_duration"] == 10.0
    assert res["chapters"][0]["visual_padding_seconds"] == 3.0
    assert res["chapters"][0]["chapter_total_duration"] == 13.0
    # 3 distinct angles generated per chapter
    assert len(res["chapters"][0]["shots"]) == 3
    shot_durs = [s["duration_seconds"] for s in res["chapters"][0]["shots"]]
    assert round(sum(shot_durs), 2) == 13.0

