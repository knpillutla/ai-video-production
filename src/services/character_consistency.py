"""Character Consistency Engine with LoRA, Clothing, Jewelry, and Visual Anchoring."""

from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.domain.creative import Character
from src.domain.repo import repo
from src.mcp.model_selector.cultural_catalog import lookup_costume_stack, lookup_cultural_stack


class CharacterVisualAnchor(BaseModel):
    """Complete visual identity specification locking character consistency across all scenes."""

    character_id: str
    name: str
    gender: str = "female"
    age_bracket: str = "20s"
    ethnicity: str = "south_asian"
    culture: str = "indian_south"
    appearance_anchor: str = ""
    costume_anchor: str = ""
    jewelry_anchor: str = ""
    seed: int = 42819
    loras: list[dict[str, Any]] = Field(default_factory=list)
    reference_image_path: str | None = None


def build_character_prompt_prefix(anchor: CharacterVisualAnchor) -> str:
    """Construct an identity-locking prompt prefix specifying exact facial, clothing, and jewelry traits."""
    elements = [
        f"Protagonist {anchor.name}",
        anchor.appearance_anchor,
        anchor.costume_anchor,
        anchor.jewelry_anchor,
    ]
    cleaned = [e.strip() for e in elements if e and e.strip()]
    return ", ".join(cleaned)


def inject_character_consistency(
    visual_prompt: str,
    anchor: CharacterVisualAnchor | None,
) -> tuple[str, list[dict[str, Any]], int]:
    """Inject persistent character anchors and LoRAs into visual diffusion scene prompts.

    Returns:
        tuple[str, list[dict[str, Any]], int]: (enhanced_prompt, scene_loras, deterministic_seed)
    """
    if not anchor:
        return visual_prompt, [], 42819

    prefix = build_character_prompt_prefix(anchor)
    enhanced = f"{prefix}, {visual_prompt}"
    logger.info(
        f"character_consistency_injected: char={anchor.name}, loras={len(anchor.loras)}, "
        f"seed={anchor.seed}"
    )
    return enhanced, anchor.loras, anchor.seed


def get_or_create_character_anchor(
    user_id: UUID,
    show_id: UUID,
    character_name: str | None = None,
    culture: str = "indian_south",
    costume_style: str = "indian_traditional",
    gender: str = "female",
) -> CharacterVisualAnchor:
    """Retrieve existing character anchor from universe repo or initialize a culturally authentic anchor."""
    name = character_name or ("Ananya" if gender.lower() == "female" else "Ravi")
    existing_chars = repo.list_characters(user_id, show_id)
    match = next((c for c in existing_chars if c.name.lower() == name.lower()), None)

    costume_info = lookup_costume_stack(costume_style, gender=gender)
    cult_info = lookup_cultural_stack(culture)

    loras: list[dict[str, Any]] = []
    if "recommended_lora" in costume_info:
        loras.append(costume_info["recommended_lora"])
    if "jewelry_lora" in costume_info:
        loras.append(costume_info["jewelry_lora"])

    if match:
        return CharacterVisualAnchor(
            character_id=str(match.id),
            name=match.name,
            gender=match.gender,
            age_bracket=match.age_bracket,
            ethnicity=match.ethnicity,
            culture=match.culture,
            appearance_anchor=match.appearance_anchor or cult_info["visual_diffusion"]["prompt_anchors"],
            costume_anchor=match.costume_anchor or costume_info.get("prompt_enhancer", ""),
            seed=match.seed,
            loras=loras,
            reference_image_path=match.face_embedding_path,
        )

    # Initialize new culturally authentic character anchor
    if gender.lower() == "female":
        appearance = (
            "24-year-old South Asian woman, warm golden-dusky glowing complexion, expressive almond dark brown eyes, "
            "sharp jawline, long thick silky black hair braided with neat jasmine flowers, radiant warm smile"
        )
    else:
        appearance = (
            "28-year-old South Asian man, warm wheatish skin tone, well-defined jawline, short neatly styled black hair, "
            "clean trimmed light stubble, confident expressive dark eyes"
        )

    char_entity = Character(
        id=uuid4(),
        user_id=user_id,
        show_id=show_id,
        name=name,
        gender=gender,
        age_bracket="20s",
        ethnicity="south_asian" if "indian" in culture else "global",
        culture=culture,
        appearance_anchor=appearance,
        costume_anchor=costume_info.get("prompt_enhancer", ""),
        seed=42819 + (abs(hash(name)) % 5000),
    )
    repo.save_character(char_entity)
    logger.info(f"character_anchor_created: name={name}, culture={culture}, show_id={show_id}")

    return CharacterVisualAnchor(
        character_id=str(char_entity.id),
        name=char_entity.name,
        gender=char_entity.gender,
        age_bracket=char_entity.age_bracket,
        ethnicity=char_entity.ethnicity,
        culture=char_entity.culture,
        appearance_anchor=char_entity.appearance_anchor,
        costume_anchor=char_entity.costume_anchor,
        seed=char_entity.seed,
        loras=loras,
    )


__all__ = [
    "CharacterVisualAnchor",
    "build_character_prompt_prefix",
    "inject_character_consistency",
    "get_or_create_character_anchor",
]
