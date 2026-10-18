"""50-Production Character Archetype Rotation Engine.

Guarantees 100% fresh cast on every production across 50 runs,
only cycling back to character #1 after 50 unique productions.
Bypasses static asset cache locks so every video looks fresh.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Any

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.services.character_archetype_catalog import (
    ArchetypeSpec,
    TELUGU_FEMALE_ARCHETYPES,
    TELUGU_MALE_ARCHETYPES,
)

ROTATION_CYCLE_LIMIT = 50


def get_rotation_state_file(user_id: str, network: str | None = None) -> Path:
    """Return the JSON file path storing the persistent production rotation counter."""
    clean_u = str(user_id).replace("@", "-").replace(".", "-")
    clean_net = str(network or "default_network").lower()
    net_dir = storage_service.get_network_path(clean_u, clean_net)
    net_dir.mkdir(parents=True, exist_ok=True)
    return net_dir / "character_rotation.json"


def get_and_increment_production_slot(
    user_id: str,
    network: str | None = None,
    episode_number: int | None = None,
) -> int:
    """Resolve the 0-49 slot index for the production, cycling every 50 runs."""
    state_file = get_rotation_state_file(user_id, network)
    current_index = 0
    if state_file.is_file():
        try:
            data = json.loads(state_file.read_text(encoding="utf-8"))
            current_index = int(data.get("production_counter", 0))
        except Exception:
            current_index = 0

    if episode_number and episode_number > 0:
        slot = (episode_number - 1) % ROTATION_CYCLE_LIMIT
        next_counter = max(current_index, episode_number)
    else:
        slot = current_index % ROTATION_CYCLE_LIMIT
        next_counter = current_index + 1

    try:
        state_file.write_text(
            json.dumps({"production_counter": next_counter, "last_slot": slot}, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"character_rotation_state_write_failed: {e}")

    logger.info(f"character_rotation_slot_assigned: slot={slot + 1}/{ROTATION_CYCLE_LIMIT} (counter={next_counter})")
    return slot


def resolve_cast_archetypes(
    slot: int,
    culture: str = "te",
    language: str = "te",
) -> tuple[ArchetypeSpec, ArchetypeSpec]:
    """Return the exact (Female, Male) ArchetypeSpec dynamically created or retrieved for this language."""
    from src.services.dynamic_character_service import get_or_create_language_archetypes_sync

    fem_list, male_list = get_or_create_language_archetypes_sync(language=language, culture=culture)
    norm_fem_slot = slot % len(fem_list)
    norm_male_slot = slot % len(male_list)
    return fem_list[norm_fem_slot], male_list[norm_male_slot]


def build_fresh_cast_prompt_directive(
    slot: int,
    fem: ArchetypeSpec,
    male: ArchetypeSpec,
    setting: str = "",
) -> str:
    """Generate unambiguous Gemini prompt instructions mandating the exact fresh cast and attractive weather-appropriate attire."""
    is_snow_cold = any(k in (setting or "").lower() for k in ("snow", "alps", "mountain", "winter", "glacier", "blizzard", "cold", "frost", "ice"))
    if is_snow_cold:
        wardrobe_directive = (
            f"3. ATTRACTIVE & STYLISH WEATHER-AUTHENTIC WINTER WARDROBE (Rule 12 & Climate Fidelity):\n"
            f"   - Setting is high-altitude snow / alpine winter. Both characters MUST wear fully covering, weather-authentic, yet HIGHLY ATTRACTIVE and form-flattering luxury winter fashion:\n"
            f"   - Female Lead ({fem.name}): Breathtakingly beautiful, cute, charming, and stylish. Dressed in an impeccably tailored, form-flattering luxury wool/cashmere overcoat in {fem.palette} (belted to flatter her graceful slim waist and natural curves), fine-knit cashmere turtleneck with modest high neckline, tailored thermal wool trousers, and polished leather alpine boots. Curated accessories across all zones: delicate gold/pearl hairpins in styled hair, sparkling earrings, delicate pendant necklace, slim luxury dress watch, dainty rings on hands, and silver ankle chain anklet. STRICT PROHIBITION against thin fabrics, sleeveless tops, bare midriffs, or open-toe shoes in snow!\n"
            f"   - Male Lead ({male.name}): Strikingly handsome in a sharp, tailored heavy wool overcoat in {male.palette} over an unadorned fitted cashmere/cable crewneck sweater, fitted charcoal wool trousers, waterproof leather boots, and classic chronograph watch strapped securely to his left wrist.\n"
            f"   - Aesthetic Realism: Characters must look beautifully dressed, cozy, warm, and authentically protected against the snow.\n"
        )
    else:
        wardrobe_directive = (
            f"3. CONTEXT-MATCHING ATTRACTIVE DESIGNER FASHION (BEAUTIFUL, COLORFUL, ELEGANT WITH DESIGNS - Rule 12):\n"
            f"   - Female Lead ({fem.name}): Breathtakingly beautiful, cute, charming, and stylish. Wearing a context-matching, vibrant and colorful designer dress in {fem.palette} (rich jewel tones, vivid pastels, delicate floral embroidery, or fine lace/zari threadwork designs) tailored to flatter her graceful slim waist and natural curves. She MUST ALWAYS wear complete curated accessories across all 4 zones in every outfit: (1) HAIR: fresh fragrant blossoms or delicate pearl/gold barrette pins; (2) NECKLINE & EARS: sparkling earrings and delicate pendant chain on a modest neckline; (3) HANDS & WRISTS: slim dress watch, delicate gold/silver bangles, and dainty rings; (4) LEGS & ANKLES: dainty silver/gold ankle chain (anklet / payal) with elegant sandals or heels to look cute, charming, and stylish.\n"
            f"   - STRICT MODESTY (FAMILY-FRIENDLY & ZERO NUDITY): Tasteful, fully modest and elegant necklines (boat neck, modest round neck, mandarin collar), completely covered torso and midriff, non-revealing, graceful silhouette. STRICTLY PROHIBIT deep cleavage, plunging necklines, bare midriffs, sheer fabrics, or sexualized/provocative cuts.\n"
            f"   - Male Lead ({male.name}): Strikingly handsome, stylish, and elegant in attractive context-matched tailored attire in {male.palette} (crisp tailored shirt or structured layer, tailored trousers, leather footwear) with chronograph watch strapped securely to his left wrist. Modest gentleman styling (zero bare chest, zero nudity).\n"
        )

    return (
        f"MANDATORY 30-PRODUCTION FRESH CAST ROTATION (Slot {slot + 1}/{ROTATION_CYCLE_LIMIT}):\n"
        f"To ensure every video looks completely fresh, you MUST feature this exact couple with their unique features and curated wardrobe palette:\n"
        f"1. FEMALE LEAD PROTAGONIST:\n"
        f"   - Name: '{fem.name}' (Age: {fem.age})\n"
        f"   - Beauty & Charm: Strikingly beautiful, radiant, cute, with natural feminine grace\n"
        f"   - Facial Features: {fem.face}\n"
        f"   - Hair & Skin: {fem.hair}, {fem.skin}\n"
        f"   - Curated Color Palette: {fem.palette} (STRICTLY PROHIBIT default emerald-green unless specified here)\n"
        f"   - Physicality: Mid-20s, graceful SLIM build with balanced natural curves, slender waist\n"
        f"2. MALE LEAD PROTAGONIST:\n"
        f"   - Name: '{male.name}' (Age: {male.age})\n"
        f"   - Charm & Frame: Strikingly handsome, confident, lean-athletic fit build\n"
        f"   - Facial Features: {male.face}\n"
        f"   - Hair & Skin: {male.hair}, {male.skin}\n"
        f"   - Curated Color Palette: {male.palette} (STRICTLY PROHIBIT default navy unless specified here)\n"
        f"   - Physicality: Mid-20s, MEDIUM BUILT, athletic frame, precision chronograph watch strapped securely to left wrist\n"
        f"{wardrobe_directive}"
        f"4. STRICT SCRIPT CONTINUITY:\n"
        f"   - You MUST name them '{fem.name}' and '{male.name}' in character metadata and across ALL scene visual prompts.\n"
        f"   - Visual prompts across all scenes must explicitly depict their unique facial structures ({fem.face} / {male.face}) and their assigned color palette ({fem.palette} / {male.palette}).\n\n"
    )


__all__ = [
    "ROTATION_CYCLE_LIMIT",
    "get_and_increment_production_slot",
    "resolve_cast_archetypes",
    "build_fresh_cast_prompt_directive",
]
