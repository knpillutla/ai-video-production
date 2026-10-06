"""Targeted local mock unit tests for Universal Lighting Director & Photorealism Engine.

Tests:
1. Default daytime (5400K-5600K) photorealism when no time-of-day is specified.
2. Strict user intent priority when sunrise, sunset, evening, or night is requested.
3. Prompt integration in build_base_directorial_prompt and build_travel_prompt.
Runs 100% locally with zero paid API calls ($0.00 spend).
"""
import pytest
from src.studios.lighting_director import (
    detect_lighting_directive,
    format_universal_lighting_guardrails,
)
from src.studios.base_directorial_prompt import build_base_directorial_prompt
from src.studios.travel_studio.travel_prompt import build_travel_prompt


def test_default_daytime_when_prompt_has_no_time_of_day():
    """Prompts without lighting keywords must default strictly to 5500K natural daytime."""
    kelvin, tod_key, desc = detect_lighting_directive("Hyderabad Charminar aerial drone flight")
    assert kelvin == 5500
    assert tod_key == "daytime_natural"
    assert "daytime sunlight" in desc.lower()


def test_empty_prompt_defaults_to_daytime():
    """Empty or None prompt must default to daytime unless archetype explicitly overrides."""
    kelvin, tod_key, desc = detect_lighting_directive(None, archetype="cities")
    assert kelvin == 5500
    assert tod_key == "daytime_natural"


def test_user_intent_sunrise_honored():
    """Explicit sunrise/dawn in prompt must be honored with ~3800K warm morning light."""
    kelvin, tod_key, desc = detect_lighting_directive("Varanasi sacred river ghats at sunrise dawn")
    assert kelvin == 3800
    assert tod_key == "sunrise_dawn"
    assert "sunrise" in desc.lower()


def test_user_intent_sunset_honored():
    """Explicit sunset/golden hour in prompt must be honored with ~3000K golden illumination."""
    kelvin, tod_key, desc = detect_lighting_directive("Golconda Fort granite walls during sunset golden hour")
    assert kelvin == 3000
    assert tod_key == "sunset_golden_hour"
    assert "sunset" in desc.lower()


def test_user_intent_evening_honored():
    """Explicit evening/twilight in prompt must be honored with ~3800K twilight illumination."""
    kelvin, tod_key, desc = detect_lighting_directive("Tokyo skyline during evening twilight")
    assert kelvin == 3800
    assert tod_key == "evening_twilight"
    assert "twilight" in desc.lower()


def test_user_intent_night_honored():
    """Explicit night/midnight/starlight in prompt must be honored with ~2200K starlit illumination."""
    kelvin, tod_key, desc = detect_lighting_directive("Desert sand dunes under midnight starlit sky with Milky Way")
    assert kelvin == 2200
    assert tod_key == "night_starlight"
    assert "midnight" in desc.lower()


def test_base_directorial_prompt_contains_photorealism_and_daytime():
    """build_base_directorial_prompt must inject 4K/8K photorealism and daytime lighting guardrails."""
    prompt = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="Metropolises & Skylines",
        custom_prompt="4K drone flight over Bangalore technology corridor",
        duration_seconds=12.0,
        num_shots=2,
    )
    assert "UNIVERSAL PHOTOREALISM & LIGHTING DIRECTIVE" in prompt
    assert "Hasselblad H6D-100c" in prompt
    assert "DAYTIME_NATURAL" in prompt
    assert "5500K" in prompt
    assert '"color_temp_kelvin": 5500' in prompt


def test_travel_prompt_cities_defaults_to_daytime():
    """build_travel_prompt for cities without night specified must NOT force evening urban glow."""
    prompt = build_travel_prompt(
        custom_prompt="Hyderabad HITEC city skyline",
        duration_seconds=10.0,
        num_shots=2,
        archetype="cities",
    )
    assert "evening urban glow" not in prompt
    assert "DAYTIME_NATURAL" in prompt
    assert '"color_temp_kelvin": 5500' in prompt


def test_travel_prompt_honors_explicit_night():
    """build_travel_prompt must honor explicit night if requested in custom_prompt."""
    prompt = build_travel_prompt(
        custom_prompt="Hyderabad HITEC city skyline at night with illuminated bridges",
        duration_seconds=10.0,
        num_shots=2,
        archetype="cities",
    )
    assert "NIGHT_STARLIGHT" in prompt
    assert '"color_temp_kelvin": 2200' in prompt


def test_travel_prompt_autonomous_curation_directives():
    """build_travel_prompt must direct Gemini to autonomously curate landmarks and cities without hardcoding."""
    prompt = build_travel_prompt(
        custom_prompt="Hyderabad",
        duration_seconds=120.0,
        num_shots=3,
        archetype="cities",
    )
    assert "COMPREHENSIVE LANDMARK, ARCHITECTURE & CULTURAL CURATION" in prompt
    assert "AUTONOMOUS CITY & DESTINATION SELECTION" in prompt
    assert "Monumental Heritage" in prompt
    assert "Modern Architectural Skylines" in prompt
    assert "Famous Roads, Boulevards & Waterfronts" in prompt
    assert "Historic Quarters & Boutique Districts" in prompt

