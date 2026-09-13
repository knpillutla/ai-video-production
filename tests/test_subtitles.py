"""Unit tests for Multilingual Subtitle Bundles, WebVTT, and Default English Subtitling."""

import json
from pathlib import Path
import pytest

from src.scripts.local_subtitles import (
    format_timestamp_srt,
    format_timestamp_vtt,
    format_timestamp_ass,
    generate_srt,
    generate_vtt,
    generate_kinetic_ass,
    generate_subtitle_bundle,
)
from src.scripts.local_translator import (
    is_indian_language,
    get_subtitle_bundle_languages,
    translate_dialogue,
)


def test_indian_language_classification():
    assert is_indian_language("te") is True
    assert is_indian_language("te-IN") is True
    assert is_indian_language("hi") is True
    assert is_indian_language("ta") is True
    assert is_indian_language("kn") is True
    assert is_indian_language("ml") is True
    assert is_indian_language("en") is False
    assert is_indian_language("es") is False
    assert is_indian_language("fr") is False


def test_bundle_languages_selection():
    # Indian content -> English + 5 Indian languages
    indian_bundle = get_subtitle_bundle_languages("te")
    assert "en" in indian_bundle
    assert "te" in indian_bundle
    assert "hi" in indian_bundle
    assert "ta" in indian_bundle
    assert "kn" in indian_bundle
    assert "ml" in indian_bundle
    assert len(indian_bundle) >= 6

    # World content -> English + 5 World languages
    world_bundle = get_subtitle_bundle_languages("es")
    assert "en" in world_bundle
    assert "es" in world_bundle
    assert "fr" in world_bundle
    assert "de" in world_bundle
    assert "ja" in world_bundle


def test_dialogue_translation():
    te_text = "వర్క్ ఫ్రమ్ హోమ్ అని చెప్పి రోజుకి 18 గంటలు లాగిన్ లోనే ఉంటే... జీతం ఏమో నెలకి 30 వేలు!"
    # Translate Telugu to English
    en_trans = translate_dialogue(te_text, "te", "en")
    assert "Work From Home" in en_trans
    assert "18 hours" in en_trans

    # Translate Telugu to Hindi
    hi_trans = translate_dialogue(te_text, "te", "hi")
    assert "वर्क फ्रॉम होम" in hi_trans


def test_subtitle_bundle_generation(tmp_path: Path):
    segments = [
        {
            "start": 0.0,
            "end": 3.8,
            "text": "వర్క్ ఫ్రమ్ హోమ్ అని చెప్పి రోజుకి 18 గంటలు లాగిన్ లోనే ఉంటే... జీతం ఏమో నెలకి 30 వేలు!",
        },
        {
            "start": 3.8,
            "end": 8.0,
            "text": "మేనేజర్ కాల్ వచ్చిన ప్రతిసారీ వైఫై కట్ అయిందని అబద్ధం చెప్పే కళ లో మనం డాక్టరేట్ చేసాం.",
        },
    ]

    out_dir = tmp_path / "subtitles"
    result = generate_subtitle_bundle(
        base_segments=segments,
        base_language="te",
        output_dir=out_dir,
        default_subtitle_lang="en",
    )

    # 1. Verify default burned subtitle path is English
    burned_path = result["burned_ass_path"]
    assert burned_path.name == "kinetic_en.ass"
    assert burned_path.exists()

    # 2. Verify English content contains translated text
    en_content = burned_path.read_text(encoding="utf-8")
    assert "Work From Home" in en_content

    # 3. Verify all bundle formats exist (.ass, .srt, .vtt)
    for lang in ["en", "te", "hi", "ta", "kn", "ml"]:
        assert (out_dir / f"kinetic_{lang}.ass").exists()
        assert (out_dir / f"{lang}.srt").exists()
        assert (out_dir / f"{lang}.vtt").exists()

    # 4. Verify manifest.json
    manifest_file = out_dir / "manifest.json"
    assert manifest_file.exists()
    manifest_data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert manifest_data["content_language"] == "te"
    assert manifest_data["default_subtitle_language"] == "en"
    assert manifest_data["is_indian_bundle"] is True
    assert len(manifest_data["tracks"]) >= 6
