"""Character Consistency Engine with LoRA, Clothing, Jewelry, and Visual Anchoring."""

import re
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.domain.creative import Character
from src.domain.repo import repo
from src.mcp.model_selector.cultural_catalog import lookup_costume_stack, lookup_cultural_stack


DEFAULT_BODY_COMPOSITION = "balanced naturally fit medium build, neither too skinny nor chubby"
_BODY_OVERRIDE_PATTERNS = (
    ("skinny", ("skinny", "very thin", "bony")),
    ("chubby", ("chubby", "plus-size", "plus size", "overweight")),
)


def _body_composition_from_user_text(text: str | None) -> str | None:
    """Accept non-default body types only when the user's own brief states one."""
    normalized = (text or "").lower()
    for composition, cues in _BODY_OVERRIDE_PATTERNS:
        if any(cue in normalized for cue in cues):
            return composition
    return None


def _safe_appearance_summary(summary: str | None, body: str) -> str:
    """Keep useful model-provided traits without letting it override body defaults."""
    cleaned = summary or ""
    if body == DEFAULT_BODY_COMPOSITION:
        cleaned = re.sub(r"\b(skinny|very thin|bony|chubby|plus[- ]size|overweight)\b", "", cleaned, flags=re.IGNORECASE)
    return ", ".join(part.strip(" ,") for part in (body, cleaned) if part.strip(" ,"))


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


def build_character_prompt_prefix(
    anchor: CharacterVisualAnchor,
    costume_override: str | None = None,
) -> str:
    """Construct an identity-locking prompt prefix specifying exact facial, clothing, and jewelry traits."""
    costume = costume_override if costume_override is not None else anchor.costume_anchor
    elements = [
        f"Protagonist {anchor.name}",
        anchor.appearance_anchor,
        costume,
        anchor.jewelry_anchor,
    ]
    cleaned = [e.strip() for e in elements if e and e.strip()]
    return ", ".join(cleaned)


def inject_character_consistency(
    visual_prompt: str,
    anchor: CharacterVisualAnchor | None,
    costume_override: str | None = None,
) -> tuple[str, list[dict[str, Any]], int]:
    """Inject persistent character anchors and LoRAs into visual diffusion scene prompts.

    Prioritizes scene-contextual outfits derived from narrative context over static costumes.

    Returns:
        tuple[str, list[dict[str, Any]], int]: (enhanced_prompt, scene_loras, deterministic_seed)
    """
    if not anchor:
        return visual_prompt, [], 42819

    vp_lower = visual_prompt.lower()
    has_scene_outfit = any(k in vp_lower for k in ("wearing", "dressed in", "outfit", "attire", "costume", "garb", "saree", "jacket", "suit"))
    effective_costume = costume_override if costume_override is not None else ("" if has_scene_outfit else anchor.costume_anchor)

    prefix = build_character_prompt_prefix(anchor, costume_override=effective_costume)
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
    language: str = "en",
    age: int | None = None,
    body_composition: str | None = None,
    height: str | None = None,
    role: str | None = None,
    appearance_summary: str | None = None,
    source_text: str | None = None,
) -> CharacterVisualAnchor:
    """Retrieve existing character anchor from universe repo or initialize a culturally authentic anchor."""
    from src.mcp.model_selector.cultural_names import resolve_cultural_character_name

    name = character_name or resolve_cultural_character_name(
        culture=culture, language=language, gender=gender, seed=abs(hash(str(show_id))) % 100
    )
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

    # Initialize character anchor (Mandatory: balanced fit build, neither too skinny nor chubby, mid-20s)
    eff_age = age or 24
    # The storyboard may suggest a body type, but only an explicit user prompt can
    # override the universal healthy medium-build default.
    eff_body = _body_composition_from_user_text(source_text) or DEFAULT_BODY_COMPOSITION
    if appearance_summary:
        appearance = _safe_appearance_summary(appearance_summary, eff_body)
    elif gender.lower() == "female":
        appearance = (
            f"{eff_age}-year-old, mid-20s, {eff_body}, graceful feminine curves with toned midriff, neither too skinny nor chubby, "
            f"breathtakingly beautiful South Asian woman, warm golden-dusky glowing complexion, expressive big dark brown eyes, "
            f"long thick wavy black hair, radiant charming smile"
        )
    else:
        appearance = (
            f"{eff_age}-year-old, mid-20s, {eff_body}, healthy masculine build, neither too skinny nor chubby, "
            f"remarkably handsome South Asian man, warm wheatish skin tone, well-defined sharp jawline, short neatly styled black hair, "
            f"clean trimmed light stubble, confident expressive dark eyes"
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
