"""LoRA Resolution and Training Engine for Vocal Music Videos.

Ensures strict character-LoRA matching, prevents cross-character and cross-gender
contamination, and orchestrates on-demand LoRA synthesis when --loras is requested.
"""

from __future__ import annotations

import re
from typing import Any

from src.core.telemetry import logger
from src.services.network_lora_service import resolve_effective_loras


async def resolve_vocal_loras(
    storyboard_data: dict[str, Any],
    char_names: list[str],
    chars: str | list[str] | None,
    explicit_loras: list[dict[str, Any]] | None,
    user_id: str | None,
    network: str | None,
    use_loras: bool,
    force_live: bool,
    lora_model: str | None = None,
    dataset_model: str | None = None,
) -> tuple[list[dict[str, Any]], str]:
    """Resolve active LoRAs with strict character, gender, and base-model compatibility guards."""
    script_loras = storyboard_data.get("loras") or storyboard_data.get("character_loras") or []
    effective_explicit = explicit_loras or script_loras
    eff_base = str(
        lora_model
        or storyboard_data.get("lora_model")
        or ("z-image" if str(storyboard_data.get("model", "")).lower() == "z-image" else "flux")
    ).lower().strip()

    if any(k in eff_base for k in ("ultra", "flux-ultra", "flux ultra", "flux_ultra", "flux-pro-ultra")):
        return [], ""

    # Detect character gender context to prevent male/female LoRA conflicts
    vocal_g = str(storyboard_data.get("vocal_gender") or "").lower()
    chars_list = storyboard_data.get("characters") or []
    char_g = str((chars_list[0] if chars_list else {}).get("gender") or "").lower()
    is_male = "male" in char_g or "male" in vocal_g
    is_female = "female" in char_g or "female" in vocal_g
    is_duet = ("duet" in vocal_g) or (is_male and is_female) or len(chars_list) > 1

    found_loras = resolve_effective_loras(
        user_id=str(user_id or "default_user"),
        network=network,
        explicit_loras=effective_explicit,
    )

    loras: list[dict[str, Any]] = []
    if found_loras:
        if char_names:
            # Strict match: LoRA character_name or trigger_word must match requested name
            matched = [
                l for l in found_loras
                if any(
                    cn.lower() in str(l.get("character_name", "")).lower()
                    or cn.lower() in str(l.get("trigger_word", "")).lower()
                    for cn in char_names
                )
            ]
            # Strict match: LoRAs must match requested base_model (do NOT fall back to incompatible base models)
            model_matched = [l for l in matched if str(l.get("base_model", "")).lower() in (eff_base, eff_base.replace("-", ""))]
            loras = model_matched
        elif use_loras or bool(chars):
            # When no char_names specified, filter found_loras by gender compatibility and base_model
            gender_compatible = [
                l for l in found_loras
                if not (is_female and not is_duet and "male" == str(l.get("gender", "")).lower())
                and not (is_male and not is_duet and "female" == str(l.get("gender", "")).lower())
            ]
            model_matched = [l for l in gender_compatible if str(l.get("base_model", "")).lower() in (eff_base, eff_base.replace("-", ""))]
            loras = model_matched

    # Training is ONLY invoked if --loras was explicitly passed on CLI and no match found
    if use_loras and not loras and network:
        try:
            from src.services.character_lora_synthesizer import ensure_character_lora
            lead_name = char_names[0] if char_names else (chars_list[0].get("name", "Lead") if chars_list else "Lead")
            lead_gender = chars_list[0].get("gender", "female") if chars_list else ("female" if is_female else "male")
            auto_lora = await ensure_character_lora(
                user_id=str(user_id or "default_user"),
                network=network,
                character_name=lead_name,
                gender=lead_gender,
                language=storyboard_data.get("language", "te"),
                culture=storyboard_data.get("culture", "south_indian"),
                force_live=force_live,
                base_model=eff_base,
                dataset_model=dataset_model or storyboard_data.get("dataset_model", "z-image"),
            )
            if auto_lora and auto_lora.get("path"):
                loras = [auto_lora]
        except Exception as lora_ex:
            logger.warning(f"auto_character_lora_failed: {lora_ex}, falling back to prompt anchors")

    trigger_words = " ".join(l.get("trigger_word", "") for l in loras if l.get("trigger_word")).strip()
    return loras, trigger_words


__all__ = ["resolve_vocal_loras"]
