import pytest
from src.studios.documentary_studio.doc_directorial_motion_service import flatten_chapters_to_scenes


def test_flatten_chapters_sequential_order():
    """Verify that shots are extracted sequentially from Chapter 1 Shot 1 downwards."""
    chapters = [
        {
            "chapter_index": 1,
            "chapter_title": "Chapter 1",
            "shots": [
                {"shot_index": 1, "duration_seconds": 15.0, "visual_prompt": "Ch1 S1"},
                {"shot_index": 2, "duration_seconds": 16.0, "visual_prompt": "Ch1 S2"},
                {"shot_index": 3, "duration_seconds": 15.0, "visual_prompt": "Ch1 S3"},
            ]
        },
        {
            "chapter_index": 2,
            "chapter_title": "Chapter 2",
            "shots": [
                {"shot_index": 1, "duration_seconds": 17.0, "visual_prompt": "Ch2 S1"},
                {"shot_index": 2, "duration_seconds": 17.0, "visual_prompt": "Ch2 S2"},
                {"shot_index": 3, "duration_seconds": 15.0, "visual_prompt": "Ch2 S3"},
            ]
        }
    ]

    # Full duration: all 6 shots
    scenes = flatten_chapters_to_scenes(chapters, target_duration=-1)
    assert len(scenes) == 6
    assert scenes[0]["chapter_index"] == 1 and scenes[0]["shot_index"] == 1
    assert scenes[1]["chapter_index"] == 1 and scenes[1]["shot_index"] == 2
    assert scenes[2]["chapter_index"] == 1 and scenes[2]["shot_index"] == 3
    assert scenes[3]["chapter_index"] == 2 and scenes[3]["shot_index"] == 1
    assert scenes[4]["chapter_index"] == 2 and scenes[4]["shot_index"] == 2
    assert scenes[5]["chapter_index"] == 2 and scenes[5]["shot_index"] == 3


def test_flatten_chapters_duration_fitting():
    """Verify that shots accumulate starting from Shot 1 in Chapter 1 to fit target duration."""
    chapters = [
        {
            "chapter_index": 1,
            "chapter_title": "Chapter 1",
            "shots": [
                {"shot_index": 1, "duration_seconds": 15.0, "visual_prompt": "Ch1 S1"},
                {"shot_index": 2, "duration_seconds": 16.0, "visual_prompt": "Ch1 S2"},
                {"shot_index": 3, "duration_seconds": 15.0, "visual_prompt": "Ch1 S3"},
            ]
        },
        {
            "chapter_index": 2,
            "chapter_title": "Chapter 2",
            "shots": [
                {"shot_index": 1, "duration_seconds": 17.0, "visual_prompt": "Ch2 S1"},
                {"shot_index": 2, "duration_seconds": 17.0, "visual_prompt": "Ch2 S2"},
            ]
        }
    ]

    # Target duration 60.0s:
    # Ch1 S1 (15) + Ch1 S2 (16 = 31) + Ch1 S3 (15 = 46 <= 60); next shot (17) would be 63 > 60 -> 3 shots
    scenes_60 = flatten_chapters_to_scenes(chapters, target_duration=60.0)
    assert len(scenes_60) == 3
    assert sum(s["duration_seconds"] for s in scenes_60) == 46.0
    assert scenes_60[0]["visual_prompt"] == "Ch1 S1"
    assert scenes_60[1]["visual_prompt"] == "Ch1 S2"
    assert scenes_60[2]["visual_prompt"] == "Ch1 S3"


def test_flatten_chapters_num_shots_limit():
    """Verify that num_shots takes the first N shots from the beginning."""
    chapters = [
        {
            "chapter_index": 1,
            "chapter_title": "Chapter 1",
            "shots": [
                {"shot_index": 1, "duration_seconds": 15.0, "visual_prompt": "Ch1 S1"},
                {"shot_index": 2, "duration_seconds": 16.0, "visual_prompt": "Ch1 S2"},
            ]
        },
        {
            "chapter_index": 2,
            "chapter_title": "Chapter 2",
            "shots": [
                {"shot_index": 1, "duration_seconds": 17.0, "visual_prompt": "Ch2 S1"},
            ]
        }
    ]

    scenes = flatten_chapters_to_scenes(chapters, num_shots=2)
    assert len(scenes) == 2
    assert scenes[0]["visual_prompt"] == "Ch1 S1"
    assert scenes[1]["visual_prompt"] == "Ch1 S2"
