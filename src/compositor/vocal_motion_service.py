"""Selective Video Motion Synthesis for Vocal and Dance Music Videos.

Supports:
1. Autonomous Gemini-directed motion selection (Wan 2.1 by default, Kling 1.6 Pro with --kling).
2. Dual model-specific prompt dispatch (Wan anti-hallucination vs Kling kinetic physics).
3. Universal Artifact Caching, Idempotent Resumption, and deleted-motion rerenders (Rule 3).
"""

from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any

from src.core.telemetry import logger
from src.providers.base import is_mock_mode
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.providers.visual.fal_wan21 import FalWan21Adapter
from src.compliance.rights_ledger import (
    AssetType,
    CommercialLicenseType,
    rights_ledger,
)


async def synthesize_vocal_dance_motion(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    enable_dance: bool = False,
    use_kling: bool = False,
    force_live: bool = False,
    episode_id: Any = None,
) -> dict[int, Path]:
    """Synthesize video motion for scenes selected by Gemini for dynamic choreography."""
    resolved_motions: dict[int, Path] = {}
    if not enable_dance and not use_kling:
        return resolved_motions

    scenes = storyboard_data.get("scenes") or []
    if not scenes:
        return resolved_motions

    motion_scenes = [s for s in scenes if s.get("render_mode") == "motion"]
    # Fallback/Resumption: if user requested --dance/--kling, detect prior motion artifacts or peak intensity
    if not motion_scenes and (enable_dance or use_kling):
        # 1. Discover any scene that previously had a motion or meta file on disk (even if mp4 deleted)
        prior_motion_indices = set()
        for p in scenes_dir.glob("scene_*_motion.*"):
            m = re.search(r"scene_(\d+)_motion", p.name)
            if m:
                prior_motion_indices.add(int(m.group(1)))
        for s in scenes:
            if int(s.get("scene_index", 0)) in prior_motion_indices:
                s["render_mode"] = "motion"
                if s not in motion_scenes:
                    motion_scenes.append(s)

        # 2. If none on disk, check for beat_drop_hook or high choreographic intensity
        if not motion_scenes:
            for s in scenes:
                intens = str(s.get("choreography_intensity", "")).lower()
                if any(k in intens for k in ("beat_drop", "hook", "drop", "climax", "high")):
                    s["render_mode"] = "motion"
                    motion_scenes.append(s)
                    break

        # 3. Final fallback: pick scene 2 (or 1)
        if not motion_scenes:
            pick_idx = 2 if len(scenes) >= 2 else 1
            for s in scenes:
                if s.get("scene_index") == pick_idx:
                    s["render_mode"] = "motion"
                    motion_scenes = [s]
                    break

    api_key = _fal_api_key()
    wan_adapter = FalWan21Adapter(api_key=api_key)
    kling_adapter = FalKlingAdapter(api_key=api_key)

    for sc in motion_scenes:
        idx = int(sc.get("scene_index", 1))
        if idx == 0:
            continue
        motion_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
        meta_path = scenes_dir / f"scene_{idx:02d}_motion.meta.json"
        keyframe_path = scenes_dir / f"scene_{idx:02d}.jpg"

        if not keyframe_path.is_file() or keyframe_path.stat().st_size < 1000:
            logger.warning(f"vocal_motion_missing_keyframe: scene_{idx:02d}.jpg not found on disk, skipping motion")
            continue

        # Check local disk cache and handle model rerender override (e.g. Wan -> Kling)
        is_cached = motion_path.is_file() and motion_path.stat().st_size > 10_000
        if is_cached and meta_path.is_file():
            try:
                m_info = json.loads(meta_path.read_text(encoding="utf-8"))
                prev_model = str(m_info.get("model", "")).lower()
                if use_kling and prev_model == "wan":
                    logger.info(f"rerendering_motion_with_kling: scene_{idx:02d} was rendered with wan, rerendering with Kling 1.6 Pro...")
                    is_cached = False
                elif not use_kling and prev_model == "kling":
                    # User ran without --kling but already has Kling clip, keep it
                    is_cached = True
            except Exception:
                pass

        if is_cached:
            cached_model = prev_model or ("kling-1.6-pro" if use_kling else "wan-2.1-i2v")
            logger.info(f"vocal_motion_cached [model={cached_model}]: reusing existing motion video {motion_path.name} ($0.00 spend)")
            resolved_motions[idx] = motion_path
            continue

        prompts = sc.get("motion_prompts") or {}
        if use_kling:
            prompt = (
                prompts.get("kling")
                or sc.get("dance_motion_prompt")
                or "High-octane mass commercial dance step, sharp kinetic footwork, shirt billowing naturally, confident grin"
            )
            neg_prompt = "blurry face, distorted hands, stiff awkward movement, low resolution, plastic skin"
            model_provider, model_name = "Fal.ai/Kling", "kling-1.6-pro"
            active_adapter = kling_adapter
            logger.info(f"synthesizing_dance_motion_{idx:02d} [model={model_name}]: prompt={prompt[:70]}...")
        else:
            prompt = (
                prompts.get("wan")
                or sc.get("dance_motion_prompt")
                or "Controlled energetic mass dance step, firmly grounded feet, rhythmic torso bounce, strictly two natural legs, strictly two arms, flawless human joints"
            )
            neg_prompt = "extra limbs, extra legs, extra arms, phantom feet, morphing anatomy, distorted body, blurry face, three legs, duplicate limbs"
            model_provider, model_name = "Fal.ai/Wan21", "wan-2.1-i2v"
            active_adapter = wan_adapter
            logger.info(f"synthesizing_dance_motion_{idx:02d} [model={model_name}]: prompt={prompt[:70]}...")

        fal_url = await upload_to_fal(keyframe_path, api_key)
        await active_adapter.generate_video(
            image_url=fal_url,
            motion_prompt=prompt,
            output_path=motion_path,
            duration=5,
            force_live=force_live,
            negative_prompt=neg_prompt,
        )
        logger.info(f"vocal_dance_motion_ok_{idx:02d} [model={model_name}]: {motion_path.name} ({motion_path.stat().st_size} B)")

        meta_data = {
            "model": "kling" if use_kling else "wan",
            "prompt": prompt,
            "negative_prompt": neg_prompt,
            "duration": 5,
            "timestamp": time.time(),
        }
        meta_path.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")

        if episode_id and motion_path.is_file():
            rights_ledger.record_asset(
                episode_id,
                AssetType.VIDEO_MOTION,
                str(motion_path),
                model_provider,
                model_name,
                CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                f"MOTION-{idx}-{episode_id}",
                True,
            )

        resolved_motions[idx] = motion_path

    return resolved_motions


__all__ = ["synthesize_vocal_dance_motion"]
