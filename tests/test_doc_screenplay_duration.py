"""Unit test for documentary screenplay duration calibration and auto duration (-1) handling.

Offline deterministic test verifying $0.00 spend and pure mathematical derivation
of total production video duration from narration word counts and visual padding.
"""
import pytest
from src.studios.documentary_studio.doc_screenplay_duration import calibrate_screenplay_durations


def test_calibrate_screenplay_durations_auto():
    # 20 words at 2.0 words/sec = 10.0s narration + 3.0s padding = 13.0s per chapter
    mock_screenplay = {
        "title": "Germany: Architectural & Modern Odyssey",
        "chapters": [
            {
                "chapter_index": 1,
                "title": "The Brandenburg Gate",
                "narration_text": "Standing majestically in Berlin, the Brandenburg Gate embodies centuries of tumultuous European history, architectural neoclassical grandeur, and national unity today.",
                # 20 words
            },
            {
                "chapter_index": 2,
                "title": "Heidelberg Castle",
                "narration_text": "Perched above the tranquil Neckar River, Heidelberg Castle reigns as a magnificent Renaissance fortress of weathered sandstone and romantic legend.",
                # 19 words
            },
        ],
    }

    calibrated, total_dur = calibrate_screenplay_durations(
        mock_screenplay,
        speech_words_per_sec=2.0,
        default_visual_padding=3.0,
        is_auto_duration=True,
    )

    # Chapter 1: 20 words / 2.0 = 10.0s narration + 3.0s padding = 13.0s
    ch1 = calibrated["chapters"][0]
    assert ch1["estimated_narration_seconds"] == 10.0
    assert ch1["visual_padding_seconds"] == 3.0
    assert ch1["duration_seconds"] == 13.0

    # Chapter 2: 20 words / 2.0 = 10.0s narration + 3.0s padding = 13.0s
    ch2 = calibrated["chapters"][1]
    assert ch2["estimated_narration_seconds"] == 10.0
    assert ch2["visual_padding_seconds"] == 3.0
    assert ch2["duration_seconds"] == 13.0

    # Root fields
    assert calibrated["total_duration_seconds"] == 26.0
    assert calibrated["estimated_narration_duration_seconds"] == 20.0
    assert calibrated["total_words_count"] == 40
    assert total_dur == 26.0


def test_calibrate_screenplay_durations_custom_clamps_minimum():
    # If custom duration provided was smaller than the narration requires,
    # it must safely expand so narration isn't truncated
    mock_screenplay = {
        "title": "Compact Test",
        "scenes": [
            {
                "narration_text": "One two three four five six seven eight nine ten.",  # 10 words -> 5.0s + 3.0s = 8.0s needed
                "duration_seconds": 4.0,  # smaller than needed 8.0s
            }
        ],
    }

    calibrated, total_dur = calibrate_screenplay_durations(
        mock_screenplay,
        speech_words_per_sec=2.0,
        default_visual_padding=3.0,
        is_auto_duration=False,
    )

    sc = calibrated["scenes"][0]
    assert sc["estimated_narration_seconds"] == 5.0
    assert sc["duration_seconds"] == 8.0  # expanded to fit speech + padding
    assert total_dur == 8.0
