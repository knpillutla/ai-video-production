"""Unit tests for Autonomous Character LoRA Synthesizer & 3D Turnaround Training.

Guarantees 100% offline deterministic test execution ($0.00 spend) per Workspace Rule 8.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
from PIL import Image

from src.services.character_lora_synthesizer import (
    _build_hero_prompt,
    _decouple_and_crop_frames,
    synthesize_turnaround_dataset,
    ensure_character_lora,
)
from src.services.core_lora_service import CharacterLoraProfile, core_lora_service


def test_hero_prompt_rule12_compliance():
    """Verify master hero prompt adheres to Rule 12 (age 24, fit build, modest attire)."""
    p_fem = _build_hero_prompt(name="Kavitha", gender="female", language="te", culture="south_indian")
    assert "24-year-old" in p_fem
    assert "South Indian" in p_fem
    assert "balanced naturally fit build" in p_fem
    assert "modest high-neck" in p_fem
    assert "clean neutral light-grey studio backdrop" in p_fem

    p_male = _build_hero_prompt(name="Naresh", gender="male", language="te", culture="south_indian")
    assert "24-year-old" in p_male
    assert "handsome" in p_male
    assert "tailored dark crewneck shirt" in p_male


def test_decouple_and_crop_frames(tmp_path: Path):
    """Verify raw turnaround frames are cropped and paired with descriptive caption files."""
    raw_dir = tmp_path / "raw_frames"
    raw_dir.mkdir(parents=True)
    out_dir = tmp_path / "dataset"

    # Create 3 dummy raw frames
    for idx in range(1, 4):
        img = Image.new("RGB", (1080, 1080), color=(100 + idx * 30, 120, 140))
        img.save(raw_dir / f"turnaround_{idx:02d}.jpg")

    _decouple_and_crop_frames(raw_dir, out_dir, trigger_word="KAVITHA_TRIGGER", is_female=True)

    crops = sorted(out_dir.glob("crop_*.jpg"))
    captions = sorted(out_dir.glob("crop_*.txt"))
    assert len(crops) == 3
    assert len(captions) == 3

    # Verify 1:1 square crop resolution
    with Image.open(crops[0]) as im:
        assert im.size == (1024, 1024)

    # Verify caption decoupling content
    cap_text = captions[0].read_text(encoding="utf-8")
    assert "KAVITHA_TRIGGER woman" in cap_text
    assert "neutral studio background" in cap_text


@pytest.mark.asyncio
async def test_ensure_character_lora_cache_hit(tmp_path: Path, monkeypatch):
    """Verify existing registered LoRA returns immediately without training ($0.00 spend)."""
    user_id = "test_user_cache"
    net = "test_network_cache"

    profile = CharacterLoraProfile(
        name="Kavitha", gender="female", lora_url="https://fal.media/files/kavitha_cached.safetensors",
        trigger_word="KAVITHA_TRIGGER", scale=0.85, base_model="z-image",
    )
    core_lora_service.register_character_lora(user_id=user_id, network=net, character_key="kavitha", profile=profile)

    res = await ensure_character_lora(
        user_id=user_id, network=net, character_name="Kavitha", gender="female", language="te",
    )
    assert res["path"] == "https://fal.media/files/kavitha_cached.safetensors"
    assert res["trigger_word"] == "KAVITHA_TRIGGER"


@pytest.mark.asyncio
async def test_ensure_character_lora_mock_turnaround_synthesis(tmp_path: Path, monkeypatch):
    """Verify complete end-to-end turnaround synthesis and registration under mock mode."""
    user_id = "test_user_synth"
    net = "test_network_synth"

    # Run synthesize in mock mode (generates mock hero face, local turnaround fallback, dataset crops, and registers mock LoRA)
    res = await ensure_character_lora(
        user_id=user_id, network=net, character_name="Ananya", gender="female", language="te", steps=100, num_frames=3,
    )

    assert res["character_name"] == "Ananya"
    assert "ANANYA_TRIGGER" in res["trigger_word"]
    assert "mock_lora" in res["path"] or "safetensors" in res["path"]

    # Verify it is formally listed in core_lora_service network catalog
    network_loras = core_lora_service.list_character_loras(user_id=user_id, network=net)
    assert any(p.name == "Ananya" for p in network_loras)
