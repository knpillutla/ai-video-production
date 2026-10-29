"""Targeted unit tests for documentary chapter cadence and multi-shot flattener.

Verifies deterministic duration sizing, 0ms audio-visual drift, and
hierarchical chapter-to-shot unrolling without external API calls ($0.00).
"""
import pytest
from src.studios.documentary_studio.doc_chapter_cadence_service import (
    compute_chapter_shot_durations,
    flatten_chapters_to_timeline,
    is_ai_diffusion_shot,
)


def test_is_ai_diffusion_shot():
    assert is_ai_diffusion_shot({"motion_type": "ai_diffusion", "recommended_model": "h3_max"}) is True
    assert is_ai_diffusion_shot({"motion_type": "ken_burns", "recommended_model": "local_drone"}) is False
    assert is_ai_diffusion_shot({"recommended_model": "kling_v3_4k"}) is True


def test_compute_chapter_shot_durations_hybrid():
    # 3 shots: 1 diffusion (5s), 2 Ken Burns
    shots = [
        {"shot_type": "wide", "motion_type": "ken_burns"},
        {"shot_type": "medium", "motion_type": "ai_diffusion", "recommended_model": "h3_max"},
        {"shot_type": "detail", "motion_type": "ken_burns"},
    ]
    audio_dur = 14.54
    durs = compute_chapter_shot_durations(shots, audio_dur)

    assert len(durs) == 3
    # Diffusion shot gets locked to 5.0s
    assert durs[1] == 5.0
    # Remaining time = 9.54s split between shot 0 and shot 2
    assert round(sum(durs), 2) == 14.54
    assert durs[0] > 4.0
    assert durs[2] > 4.0


def test_compute_chapter_shot_durations_all_ken_burns():
    shots = [
        {"shot_type": "wide", "motion_type": "ken_burns"},
        {"shot_type": "detail", "motion_type": "ken_burns"},
    ]
    audio_dur = 13.50
    durs = compute_chapter_shot_durations(shots, audio_dur)

    assert len(durs) == 2
    assert round(sum(durs), 2) == 13.50
    assert durs[0] == 6.75
    assert durs[1] == 6.75


def test_flatten_chapters_to_timeline():
    raw_data = {
        "title": "New Zealand Country Profile",
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "SOVEREIGN FOUNDATIONS",
                "chapter_subtitle": "Pacific Bastion",
                "fact_badge": "🇳🇿 CAPITAL: WELLINGTON",
                "chapter_stats": "Area: 268,021 km²",
                "narration_text": "In the southwestern Pacific lies an isolated archipelago of monumental majesty.",
                "duration_seconds": 15.0,
                "shots": [
                    {
                        "shot_index": 1,
                        "visual_prompt": "Aerial view of Mount Cook",
                        "motion_type": "ken_burns",
                        "recommended_model": "local_drone",
                    },
                    {
                        "shot_index": 2,
                        "visual_prompt": "Wellington waterfront with pedestrians",
                        "motion_type": "ai_diffusion",
                        "recommended_model": "h3_max",
                    },
                ],
            },
            {
                "chapter_index": 2,
                "chapter_title": "ALPINE GEOGRAPHY",
                "fact_badge": "🏔️ MOUNT COOK 3,724M",
                "narration_text": "Crowned by thirty distinct peaks exceeding three thousand meters.",
                "duration_seconds": 12.0,
                "shots": [
                    {
                        "shot_index": 1,
                        "visual_prompt": "Glacial valley of Franz Josef",
                        "motion_type": "ken_burns",
                        "recommended_model": "local_drone",
                    }
                ],
            },
        ],
    }

    flattened, chapter_map = flatten_chapters_to_timeline(raw_data)

    # Chapter 1 had 2 shots, Chapter 2 had 1 shot -> 3 total timeline shots
    assert len(flattened) == 3

    # Shot 1: Chapter 1 Head
    assert flattened[0]["is_chapter_head"] is True
    assert flattened[0]["chapter_title"] == "SOVEREIGN FOUNDATIONS"
    assert flattened[0]["fact_badge"] == "🇳🇿 CAPITAL: WELLINGTON"
    assert flattened[0]["timeline_index"] == 1

    # Shot 2: Chapter 1 Sub-Shot (No dossier card repeat)
    assert flattened[1]["is_chapter_head"] is False
    assert flattened[1]["chapter_title"] is None
    assert flattened[1]["fact_badge"] is None
    assert flattened[1]["timeline_index"] == 2

    # Shot 3: Chapter 2 Head
    assert flattened[2]["is_chapter_head"] is True
    assert flattened[2]["chapter_title"] == "ALPINE GEOGRAPHY"
    assert flattened[2]["fact_badge"] == "🏔️ MOUNT COOK 3,724M"
    assert flattened[2]["timeline_index"] == 3

    # Chapter map should only map head shots (index 0 and index 2)
    assert 0 in chapter_map
    assert 1 not in chapter_map
    assert 2 in chapter_map


def test_flatten_chapters_with_scenes_key_preserves_all_10_shots():
    raw_data = {
        "title": "Fiji Country Dossier",
        "scenes": [
            {
                "chapter_title": f"CHAPTER {i+1}",
                "narration_text": f"Chapter {i+1} narration",
                "shots": [
                    {"visual_prompt": f"Wide shot {i+1}A", "location_hub": f"Location {i+1}A"},
                    {"visual_prompt": f"Detail shot {i+1}B", "location_hub": f"Location {i+1}B"},
                ],
            }
            for i in range(5)
        ],
    }
    flattened, chapter_map = flatten_chapters_to_timeline(raw_data)
    assert len(flattened) == 10
    head_count = sum(1 for s in flattened if s["is_chapter_head"])
    sub_count = sum(1 for s in flattened if not s["is_chapter_head"])
    assert head_count == 5
    assert sub_count == 5

