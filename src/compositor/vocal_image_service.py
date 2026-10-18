"""Reusable Vocal Music Video Scene Image Synthesis Service.

Synthesizes single or multi-scene 4K images with character identity consistency,
supporting fresh characters per song by default, and persistent network LoRAs when --loras is set.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import AssetType, CommercialLicenseType, rights_ledger
from src.core.telemetry import logger
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
    script_loras = storyboard_data.get("loras") or storyboard_data.get("character_loras") or []
    effective_explicit = explicit_loras or script_loras
    loras = (
        resolve_effective_loras(user_id=str(user_id or "default_user"), network=network, explicit_loras=effective_explicit)
        if (use_loras or count > 1 or effective_explicit)
        else (effective_explicit or [])
    )
    trigger_words = " ".join(l.get("trigger_word", "") for l in loras if l.get("trigger_word")).strip()

    scenes_list = storyboard_data.get("scenes") or []
    prompts_model = storyboard_data.get("prompts_by_model") or {}
    base_prompt = prompts_model.get("z_image") or prompts_model.get("flux_dev") or ""

    resolved_paths: list[Path] = []
    z_adapter = FalZImageAdapter()
    flux_adapter = FalFluxLoraAdapter()
    song_seed = abs(hash(str(episode_id or scenes_dir.parent.name))) % 100000

    for idx in range(1, count + 1):
        scene_path = scenes_dir / f"scene_{idx:02d}.jpg"
        if scene_path.is_file() and scene_path.stat().st_size > 1000:
            logger.info(f"vocal_scene_cached: reusing existing scene {scene_path.name} ({scene_path.stat().st_size} bytes)")
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
        # Sanitize any accidental negative constraint tokens from prompt
        if "negative constraints:" in effective_prompt:
            effective_prompt = effective_prompt.split("negative constraints:")[0].strip(", ")

        scene_seed = (song_seed + idx * 7919) % 1000000
        logger.info(f"generating_vocal_scene_{idx:02d}: prompt={effective_prompt[:80]}... (loras={len(loras)}, seed={scene_seed})")
        if loras:
            primary_lora = loras[0]["path"]
            scale = float(loras[0].get("scale", 1.0))
            await flux_adapter.generate_with_lora(
                prompt=effective_prompt, lora_url=primary_lora, output_path=scene_path,
                lora_scale=scale, aspect_ratio="16:9", seed=scene_seed,
            )
            provider_name, model_name = "Fal.ai/Flux", "flux-lora"
        else:
            await z_adapter.generate_to_file(
                prompt=effective_prompt, output_path=scene_path, aspect_ratio="16:9", force_live=force_live, seed=scene_seed,
            )
            provider_name, model_name = "Fal.ai", "z-image-turbo"

        if episode_id and scene_path.is_file():
            rights_ledger.record_asset(
                episode_id, AssetType.IMAGE, str(scene_path), provider_name, model_name,
                CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, f"SCENE-{idx}-{episode_id}", True,
            )
        resolved_paths.append(scene_path)

    return resolved_paths


__all__ = ["synthesize_vocal_scenes"]
