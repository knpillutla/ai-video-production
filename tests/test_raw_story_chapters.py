"""Tests for documentary raw story chapters (subtitles & narration) and screenplay multi-shot expansion."""
import json
from pathlib import Path

from src.studios.documentary_studio.doc_story_service import generate_sovereign_21_chapters, build_raw_documentary_story


def test_raw_story_structure_and_chapters():
    """Verify that raw_gemini_story.json contains the chapters array with subtitles and narration."""
    story = build_raw_documentary_story("Norway", channel_id="euro_discovery")
    assert story.get("title"), "Story must have a title"
    assert story.get("destination_entity") == "Norway"
    assert isinstance(story.get("chapters"), list), "Story must have a chapters array"
    assert len(story["chapters"]) == 21, "Story must contain all 21 sovereign chapters"

    for ch in story["chapters"]:
        assert "chapter_index" in ch
        assert "chapter_title" in ch and len(ch["chapter_title"]) > 0
        assert "chapter_subtitle" in ch
        assert "narration" in ch and len(ch["narration"]) > 0


def test_doc_country_facts_injection():
    """Verify that story chapters narrate specific country facts (capital, area, population, arts, music)."""
    chapters = generate_sovereign_21_chapters("Norway")
    assert len(chapters) == 21

    # Chapter 2: Capital & Governance
    ch2 = chapters[1]
    assert "Oslo" in ch2["narration"], "Chapter 2 must narrate the capital city name (Oslo)"
    assert "Storting" in ch2["narration"], "Chapter 2 must narrate the parliament (Storting)"

    # Chapter 3: Geography & Topography
    ch3 = chapters[2]
    assert "385,207" in ch3["narration"], "Chapter 3 must narrate the area in km² (385,207)"
    assert "fjord" in ch3["narration"].lower()

    # Chapter 6: People & Demographics
    ch6 = chapters[5]
    assert "5.55 million" in ch6["narration"], "Chapter 6 must narrate the population (5.55 million)"

    # Chapter 16: Arts & Craftsmanship
    ch16 = chapters[15]
    assert "Edvard Munch" in ch16["narration"] or "Rosemaling" in ch16["narration"]

    # Chapter 17: Music & Cultural Soul
    ch17 = chapters[16]
    assert "Edvard Grieg" in ch17["narration"] or "Hardanger fiddle" in ch17["narration"]


def test_doc_country_facts_injection_ireland():
    """Verify that story chapters narrate specific country facts for Ireland (Dublin, Killarney, Trinity, 70,273 km²)."""
    chapters = generate_sovereign_21_chapters("Ireland")
    assert len(chapters) == 21

    # Chapter 2: Capital & Governance
    ch2 = chapters[1]
    assert "Dublin" in ch2["narration"], "Chapter 2 must narrate the capital city name (Dublin)"
    assert "Oireachtas" in ch2["narration"], "Chapter 2 must narrate the parliament (Oireachtas)"

    # Chapter 3: Geography & Topography
    ch3 = chapters[2]
    assert "70,273" in ch3["narration"], "Chapter 3 must narrate the area in km² (70,273)"

    # Chapter 6: People & Demographics
    ch6 = chapters[5]
    assert "5.15 million" in ch6["narration"], "Chapter 6 must narrate the population (5.15 million)"

    # Chapter 8: Universities
    ch8 = chapters[7]
    assert "Trinity College Dublin" in ch8["narration"]

    # Chapter 18: National Parks
    ch18 = chapters[17]
    assert "Killarney National Park" in ch18["narration"]


def test_screenplay_expands_chapters_with_shots_and_movements():
    """Verify that chapter timeline expansion generates valid scenes with camera movements and prompts."""
    from src.studios.documentary_studio.doc_chapter_cadence_service import flatten_chapters_to_timeline

    sample_doc = {
        "chapters": [
            {
                "chapter_index": 1,
                "chapter_title": "1. SOVEREIGN IDENTITY",
                "shots": [
                    {"visual_prompt": "Wide 4K panoramic fjord vista", "motion_prompt": "dollyin", "duration_seconds": 6.0},
                    {"visual_prompt": "Historic fortress architecture", "motion_prompt": "pan-right", "duration_seconds": 6.0},
                ],
            }
        ]
    }
    flattened, ch_map = flatten_chapters_to_timeline(sample_doc)
    assert len(flattened) == 2, "Should flatten 2 sub-shots across timeline"
    assert flattened[0]["is_chapter_head"] is True
    assert flattened[1]["is_chapter_head"] is False
    assert flattened[0]["duration_seconds"] == 6.0


def test_doc_encyclopedia_35_chapters():
    """Verify that doc/encyclopedia generates the complete 35-chapter Sovereign Almanac."""
    story = build_raw_documentary_story("Ireland", genre="doc/encyclopedia")
    assert story.get("total_chapters") == 35, "Encyclopedia must have 35 chapters"
    assert len(story["chapters"]) == 35
    assert "Encyclopedia" in story["title"] or "Almanac" in story["title"]

    keys = [ch["chapter_key"] for ch in story["chapters"]]
    assert "ancient_history" in keys
    assert "inland_waterways" in keys
    assert "language_heritage" in keys
    assert "science_inventions" in keys
    assert "healthcare_longevity" in keys
    assert "currency_wealth_fund" in keys
    assert "national_sports" in keys
    assert "global_diaspora" in keys


def test_doc_country_facts_croatia_specific_names():
    """Verify Croatia story chapters narrate specific names (Zagreb, Hrvatski Sabor, 5 universities, Plitvice)."""
    story = build_raw_documentary_story("Croatia", channel_id="euro_discovery")
    assert story.get("destination_entity") == "Croatia"
    assert story.get("capital") == "Zagreb"

    chapters = story["chapters"]
    assert len(chapters) == 21

    # Chapter 2: Capital & Governance
    ch2 = chapters[1]
    assert "Zagreb" in ch2["narration"], "Ch 2 must narrate Zagreb"
    assert "Hrvatski Sabor" in ch2["narration"], "Ch 2 must narrate parliament Hrvatski Sabor"

    # Chapter 5: Monuments
    ch5 = chapters[4]
    assert "Diocletian" in ch5["narration"]
    assert "Dubrovnik" in ch5["narration"]

    # Chapter 7: Major Cities
    ch7 = chapters[6]
    assert "Split" in ch7["narration"]
    assert "Rijeka" in ch7["narration"]
    assert "Osijek" in ch7["narration"]

    # Chapter 8: Universities (Must list top universities)
    ch8 = chapters[7]
    assert "University of Zagreb" in ch8["narration"]
    assert "University of Split" in ch8["narration"]
    assert "University of Rijeka" in ch8["narration"]

    # Chapter 18: National Parks
    ch18 = chapters[17]
    assert "Plitvice Lakes National Park" in ch18["narration"]

