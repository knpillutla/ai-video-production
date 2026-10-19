"""Reusable Vocal Music Video Scene Image Synthesis Service.

Synthesizes single or multi-scene 4K images with character identity consistency,
supporting fresh characters per song by default, and persistent network LoRAs when --loras is set.
"""

from __future__ import annotations

from pathlib import Path
import re
from typing import Any

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
from src.providers.visual.fal_aura_sr import FalAuraSRAdapter
from src.providers.visual.fal_flux_lora import FalFluxLoraAdapter
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.services.network_lora_service import resolve_effective_loras


async def synthesize_vocal_scenes(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    num_images: int = 1,
    user_id: str | None = None,
    network: str | None = None,
    force_live: bool = False,
    explicit_loras: list[dict[str, Any]] | None = None,
    episode_id: Any | None = None,
    use_loras: bool = False,
) -> list[Path]:
    """Synthesize or reuse 4K scene images locking character consistency and optional network LoRAs."""
    scenes_dir.mkdir(parents=True, exist_ok=True)
    count = max(1, num_images)
    eff_use_loras = use_loras or (count > 1)
    script_loras = storyboard_data.get("loras") or storyboard_data.get("character_loras") or []
    effective_explicit = explicit_loras or script_loras
    loras = (
        resolve_effective_loras(user_id=str(user_id or "default_user"), network=network, explicit_loras=effective_explicit)
        if (eff_use_loras or effective_explicit)
        else (effective_explicit or [])
    )
    trigger_words = " ".join(l.get("trigger_word", "") for l in loras if l.get("trigger_word")).strip()

    scenes_list = storyboard_data.get("scenes") or []
    prompts_model = storyboard_data.get("prompts_by_model") or {}
    base_prompt = prompts_model.get("z_image") or prompts_model.get("flux_dev") or ""

    resolved_paths: list[Path] = []
    z_adapter = FalZImageAdapter()
    flux_adapter = FalFluxLoraAdapter()
    aura_upscaler = FalAuraSRAdapter()
    import hashlib

    seed_key = str(episode_id or scenes_dir.parent.name)
    seed_hash = int(hashlib.sha256(seed_key.encode("utf-8")).hexdigest()[:8], 16)
    char_seed = int((storyboard_data.get("characters") or [{}])[0].get("seed", 0))
    song_seed = (seed_hash + char_seed * 137) % 900000

    # Build persistent character visual anchor prefix to enforce facial/attire consistency across all scenes
    chars = storyboard_data.get("characters") or []
    char_anchors = []
    for c in chars:
        c_name = c.get("name", "Lead")
        c_age = c.get("age", "")
        c_gender = c.get("gender", "")
        c_comp = c.get("body_composition", "")
        c_hair = c.get("hair_and_facial_features") or c.get("face_and_hair") or ""
        c_outfit = c.get("outfit_description", "")
        desc_parts = []
        if c_age:
            desc_parts.append(f"{c_age}-year-old")
        if c_gender:
            desc_parts.append(c_gender)
        if c_comp:
            desc_parts.append(c_comp)
        if c_hair:
            desc_parts.append(c_hair)
        if c_outfit:
            desc_parts.append(f"wearing {c_outfit}")
        char_anchors.append(f"{c_name} ({', '.join(desc_parts) if desc_parts else c_comp})")

    # If hair/stubble details were omitted from characters array, pull from base_prompt
    facial_hair_hint = ""
    if base_prompt:
        m_fh = re.search(r"(\b(?:curtain fade|stubble|beard|mustache|haircut|hairstyle|wavy hair|braid|bun|curls)\b[^\.,;]*)", base_prompt, re.IGNORECASE)
        if m_fh and not any("stubble" in a.lower() or "hair" in a.lower() for a in char_anchors):
            facial_hair_hint = f" Facial and hair styling: {m_fh.group(1)}."

    anchor_prefix = (
        f"Lead character identity: {'; '.join(char_anchors)}.{facial_hair_hint} Same exact character face, hair, and outfit in every scene. "
        if char_anchors else ""
    )

    # Detect character gender for gender-adaptive broadcast safety tokens
    vocal_g = str(storyboard_data.get("vocal_gender") or "").lower()
    char_g = str((chars[0] if chars else {}).get("gender") or "").lower()
    is_male = "male" in char_g or "male" in vocal_g
    is_female = "female" in char_g or "female" in vocal_g
    is_duet = ("duet" in vocal_g) or (is_male and is_female) or len(chars) > 1

    if is_duet:
        safety_tokens = (
            "generous upper headroom, characters framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, modest high boat neckline for female lead, zero cleavage, "
            "fully visible leads in frame, zero disembodied hands, zero floating limbs, handsome male lead with watch on left wrist, "
            "beautiful female lead in elegant modest designer attire, tasteful modest family-friendly attire, zero nudity, zero bare chest"
        )
    elif is_male:
        safety_tokens = (
            "generous upper headroom, character framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, fully visible lead in frame, zero disembodied hands, zero floating limbs, "
            "natural fit lean-athletic masculine build, defined sharp jawline, neat light facial stubble, stylish haircut, "
            "tailored collared shirt, chronograph watch strapped securely to left wrist, tasteful modest family-friendly attire, "
            "zero bare chest, zero nudity"
        )
    else:
        safety_tokens = (
            "generous upper headroom, character framed with ample headroom showing open sky and scenery, "
            "rule of thirds eye line, safe broadcast framing, modest high boat neckline, zero cleavage, "
            "fully visible lead in frame, zero disembodied hands, zero floating limbs, graceful slender-curvy silhouette, "
            "delicate hair flowers or pins, delicate necklace and sparkling pendant around neck, matching earrings, "
            "slim wrist watch, delicate bangles, dainty ankle chain anklet, cute charming elegant styling, zero nudity"
        )

    for idx in range(1, count + 1):
        scene_path = scenes_dir / f"scene_{idx:02d}.jpg"
        if scene_path.is_file() and scene_path.stat().st_size > 1000:
            logger.info(f"vocal_scene_cached: ensuring 4K for existing scene {scene_path.name}")
            await aura_upscaler.upscale_image(scene_path, scene_path, target_res=(3840, 2160), force_live=force_live)
            resolved_paths.append(scene_path)
            continue

        # Extract prompt directly from script for scene idx
        if idx <= len(scenes_list) and scenes_list[idx - 1].get("visual_prompt"):
            raw_prompt = scenes_list[idx - 1]["visual_prompt"]
        elif idx == 1 and base_prompt:
            raw_prompt = base_prompt
        else:
            raw_prompt = f"{base_prompt}, dynamic scene angle {idx}, distinct pose and setting"

        # Apply LoRA trigger words if active, otherwise use Gemini script prompt directly
        effective_prompt = f"{trigger_words}, {raw_prompt}".strip(", ") if (loras and trigger_words) else raw_prompt
        # Sanitize any accidental negative constraint or Negative: tokens from prompt
        effective_prompt = re.split(r"(?i)\bnegative\s*(?:constraints|prompt)?\s*:", effective_prompt)[0].strip(", ")

        # Derive context-driven facial expressions matching the mood and lyrical theme
        ctx = f"{storyboard_data.get('genre', '')} {storyboard_data.get('song_type', '')} {storyboard_data.get('mood', '')} {storyboard_data.get('suno_tags', '')} {raw_prompt}".lower()
        if any(k in ctx for k in ("mass", "dappu", "teenmaar", "dance", "troupe", "party", "club", "energetic", "celebrat", "jathara")):
            expression_token = "radiant energetic joyful smile, infectious beaming expression, lively confident sparkle in eyes, happy animated laugh"
        elif any(k in ctx for k in ("devotion", "spiritual", "bhajan", "kirtan", "temple", "peace", "prayer")):
            expression_token = "serene peaceful smile, blissful transcendent expression, gentle spiritual warmth, glowing tranquil countenance"
        elif any(k in ctx for k in ("sad", "heartbreak", "melanchol", "sorrow", "tear", "alone", "cry")):
            expression_token = "tender wistful gaze, gentle soulful reflective emotion, poignant heartfelt expression, emotional eyes"
        else:
            expression_token = "warm affectionate tender smile, soft dreamy romantic gaze, heartfelt soulful facial expression, vibrant lively eyes"

        is_mass_or_party = any(k in ctx for k in ("mass", "dappu", "teenmaar", "dance", "troupe", "party", "club"))
        troupe_token = (
            ", vibrant synchronized background troupe of both male and female backup dancers in coordinated festive party attire grooving in soft cinematic bokeh, lively cheering crowd"
            if is_mass_or_party else ""
        )
        is_cutaway = idx <= len(scenes_list) and any(k in f"{scenes_list[idx-1].get('character_pose', '')} {raw_prompt}".lower() for k in ("cutaway", "contextual insert", "percussion close", "troupe only", "drone insert", "scenic insert"))
        eff_anchor = "" if is_cutaway else anchor_prefix
        eff_expr = "" if is_cutaway else f", {expression_token}"
        effective_prompt = f"{eff_anchor}{effective_prompt}{eff_expr}, {safety_tokens}{troupe_token}".strip(", ")

        # Use deterministic shared song seed for character consistency across all scenes in song
        max_attempts = 3 if force_live else 1
        for attempt in range(1, max_attempts + 1):
            scene_seed = (song_seed + idx * 79 + (attempt - 1) * 12345) % 900000
            cur_prompt = effective_prompt
            if attempt > 1:
                cur_prompt = f"{effective_prompt}, anatomically flawless human body, strictly two natural arms, strictly two hands, zero extra hands, zero extra fingers"
            logger.info(f"generating_vocal_scene_{idx:02d} (attempt {attempt}/{max_attempts}): prompt={cur_prompt[:80]}... (seed={scene_seed})")
            if loras:
                primary_lora = loras[0]["path"]
                scale = float(loras[0].get("scale", 1.0))
                await flux_adapter.generate_with_lora(
                    prompt=cur_prompt, lora_url=primary_lora, output_path=scene_path,
                    lora_scale=scale, aspect_ratio="16:9", seed=scene_seed,
                )
                provider_name, model_name = "Fal.ai/Flux", "flux-lora"
            else:
                await z_adapter.generate_to_file(
                    prompt=cur_prompt, output_path=scene_path, aspect_ratio="16:9", force_live=force_live, seed=scene_seed,
                )
                provider_name, model_name = "Fal.ai", "z-image-turbo"

            # Automated multimodal hallucination and anatomical audit
            from src.compositor.image_hallucination_auditor import audit_image_anatomy
            audit = await audit_image_anatomy(scene_path, prompt_context=cur_prompt, force_live=force_live)
            if not audit.is_valid:
                logger.warning(
                    f"hallucination_detected_in_scene_{idx:02d} (attempt {attempt}/{max_attempts}): "
                    f"{audit.reason}. Defects: {audit.defects}. Deleting and regenerating..."
                )
                scene_path.unlink(missing_ok=True)
                if attempt < max_attempts:
                    continue
                logger.error(f"scene_{idx:02d}_max_regeneration_attempts_reached: proceeding with best effort")
            break

        if scene_path.is_file():
            logger.info(f"upscaling_vocal_scene_{idx:02d}_to_4k: target=(3840, 2160)")
            await aura_upscaler.upscale_image(scene_path, scene_path, target_res=(3840, 2160), force_live=force_live)

        if episode_id and scene_path.is_file():
            rights_ledger.record_asset(
                episode_id, AssetType.IMAGE, str(scene_path), provider_name, model_name,
                CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"SCENE-{idx}-{episode_id}", True,
            )
        resolved_paths.append(scene_path)

    return resolved_paths


__all__ = ["synthesize_vocal_scenes"]
