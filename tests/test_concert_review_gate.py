"""Targeted unit tests for concert review gates (Rule 8 offline deterministic)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch
import pytest

from src.studios.concert_studio.concert_review_gate import (
    prompt_audio_timeline_review,
    prompt_broadcast_cuts_review,
    prompt_script_review,
    prompt_visual_plates_review,
)


def test_review_gates_auto_confirm():
    assert prompt_script_review("Title", "Title Loc", "Radha", "te", "mic", "Beach", "Lyrics", auto_confirm=True) is True
    assert prompt_audio_timeline_review(Path("test.mp3"), 60.0, [], auto_confirm=True) is True
    assert prompt_visual_plates_review(Path("scenes"), [Path("scene_01.jpg")], auto_confirm=True) is True
    assert prompt_broadcast_cuts_review([], "wav2lip", auto_confirm=True) is True


def test_review_gates_interactive_accept():
    with patch("builtins.input", return_value="y"):
        assert prompt_script_review("Title", "Title Loc", "Radha", "te", "mic", "Beach", "Lyrics", auto_confirm=False) is True
    with patch("builtins.input", return_value="yes"):
        assert prompt_audio_timeline_review(Path("test.mp3"), 60.0, [{"cut_index": 1, "start_time": 0.0, "end_time": 4.5}], auto_confirm=False) is True
    with patch("builtins.input", return_value=""):
        assert prompt_visual_plates_review(Path("scenes"), [Path("scene_01.jpg")], auto_confirm=False) is True
    with patch("builtins.input", return_value="Y"):
        assert prompt_broadcast_cuts_review([{"cut_index": 1, "is_singing": True}], "wav2lip", auto_confirm=False) is True


def test_review_gates_interactive_pause():
    with patch("builtins.input", return_value="n"):
        assert prompt_script_review("Title", "Title Loc", "Radha", "te", "mic", "Beach", "Lyrics", auto_confirm=False) is False
    with patch("builtins.input", return_value="no"):
        assert prompt_audio_timeline_review(Path("test.mp3"), 60.0, [], auto_confirm=False) is False
    with patch("builtins.input", return_value="q"):
        assert prompt_visual_plates_review(Path("scenes"), [], auto_confirm=False) is False
    with patch("builtins.input", return_value="quit"):
        assert prompt_broadcast_cuts_review([], "wav2lip", auto_confirm=False) is False


def test_review_gate_displays_llm_info(capsys):
    prompt_script_review("Title", "Title Loc", "Radha", "te", "mic", "Beach", "Lyrics", llm_provider="openai", llm_model="chatgpt-4o-latest", auto_confirm=True)
    out = capsys.readouterr().out
    assert "Script LLM: OPENAI (chatgpt-4o-latest)" in out
