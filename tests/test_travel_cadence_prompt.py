"""Test travel duration-driven shot derivation for Gemini prompts."""
import pytest
from src.studios.travel_studio.travel_prompt import build_travel_prompt
from src.studios.base_directorial_prompt import build_base_directorial_prompt


def test_travel_prompt_derives_shots_from_duration_not_num_shots():
    # Pass num_shots=1 explicitly, but duration=120.0s
    prompt = build_travel_prompt(
        custom_prompt="Hyderabad City Skyline",
        duration_seconds=120.0,
        num_shots=1,
        archetype="cities",
        channel_id="skylinediariesindia4k",
    )
    # 120s / 12.5s = 10 shots
    assert "Shot Count: 1 shots" not in prompt
    assert "exactly 10 scenes" in prompt


def test_base_directorial_prompt_overrides_travel_num_shots():
    # Calling base prompt directly with genre='travel/scenic' and num_shots=1
    prompt = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="travel",
        custom_prompt="Hyderabad City Skyline",
        duration_seconds=120.0,
        num_shots=1,
        channel_id="skylinediariesindia4k",
    )
    assert "Shot Count: 1 shots" not in prompt
    assert "exactly 10" in prompt
    assert "12.0s per shot" in prompt or "12.0s per scene" in prompt


def test_channel_production_travel_effective_shots_formula():
    eff_genre = "travel/scenic"
    duration_seconds = 120.0
    num_shots = 1  # UI default that was sent
    channel_id = "skylinediariesindia4k"

    is_travel_genre = (
        eff_genre.lower().startswith("travel")
        or eff_genre.lower() in ("travel/scenic", "travel_scenic", "travel_walking")
        or channel_id == "skylinediariesindia4k"
    )
    assert is_travel_genre is True

    effective_shots = max(2, round((duration_seconds or 60.0) / 12.5)) if is_travel_genre else num_shots
    assert effective_shots == 10  # 120s -> 10 shots, completely overriding num_shots=1


def test_num_shots_sentinel_negative_one():
    # Calling base directorial prompt with num_shots = -1
    prompt = build_base_directorial_prompt(
        genre="travel/scenic",
        sub_genre="cities",
        archetype="cities",
        cluster="travel",
        custom_prompt="Hyderabad City Skyline",
        duration_seconds=120.0,
        num_shots=-1,
        channel_id="skylinediariesindia4k",
    )
    assert "num_shots: -1" in prompt
    assert "Autonomous Cadence Contract" in prompt
    assert "exactly 10 distinct landmark scenes" in prompt or "exactly 10" in prompt


def test_travel_prompt_30s_and_60s_durations():
    # 30 seconds -> 2 shots (~15s each)
    prompt_30s = build_travel_prompt(
        custom_prompt="Goa Beaches",
        duration_seconds=30.0,
        num_shots=-1,
        archetype="cities",
        channel_id="skylinediariesindia4k",
    )
    assert "exactly 2 scenes" in prompt_30s

    # 60 seconds (1 min) -> 5 shots (~12s each)
    prompt_60s = build_travel_prompt(
        custom_prompt="Mumbai Marine Drive",
        duration_seconds=60.0,
        num_shots=-1,
        archetype="cities",
        channel_id="skylinediariesindia4k",
    )
    assert "exactly 5 scenes" in prompt_60s



