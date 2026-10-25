"""Selective Performance Motion and Beat-Synchronized Lipsync for Virtual Artist Videos.

Coordinates:
1. Natural performance motion synthesis (Wan 2.1 / Kling 1.6 Pro) tailored for
   singer mannerisms (subtle rhythm sway, hair flutter, instrument strumming, expressive eyes).
2. Beat-synchronized vocal lipsync (FalLatentSyncAdapter) matching mouth movement to Suno vocal stems.
3. Universal Artifact Caching, Idempotent Resumption, and Rights Ledger registration (Rules 3, 11).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.compliance.rights_ledger import (
    AssetType,
    CommercialLicenseType,
    rights_ledger,
)
from src.core.telemetry import logger
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.fal_storage import _fal_api_key, upload_to_fal
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
from src.providers.visual.fal_wan21 import FalWan21Adapter


async def synthesize_virtual_artist_motion(
    storyboard_data: dict[str, Any],
    scenes_dir: Path,
    audio_path: Path,
    use_kling: bool = False,
    force_live: bool = False,
    episode_id: Any = None,
    enable_lipsync: bool = True,
) -> dict[int, Path]:
    """Synthesize natural performance motion clips and apply beat-synchronized lipsync."""
    resolved_motions: dict[int, Path] = {}
    scenes = storyboard_data.get("scenes") or []
    if not scenes:
        return resolved_motions

    api_key = _fal_api_key()
    wan_adapter = FalWan21Adapter(api_key=api_key)
    kling_adapter = FalKlingAdapter(api_key=api_key)
    latentsync_adapter = FalLatentSyncAdapter(api_key=api_key)

    cum_time = 0.0
    first_sing_time = min((float(seg.get("start", 0)) for seg in (storyboard_data.get("lyrics_segments") or [])), default=0.0)

    for sc in scenes:
        idx = int(sc.get("scene_index", 1))
        sc_dur = float(sc.get("duration_seconds", 5.0))
        pose = str(sc.get("character_pose", "")).lower()
        is_cutaway = "cutaway" in pose or "orchestra" in pose or "instrument" in pose or "audience" in pose

        # Scene 00 is strictly reserved as static title card intro slide: NEVER motion, NEVER lipsync
        if idx == 0:
            logger.info("virtual_artist_motion: scene_00 is strictly reserved as static intro slide, skipping motion/lipsync")
            cum_time += sc_dur
            continue

        keyframe_path = scenes_dir / f"scene_{idx:02d}.jpg"
        if not keyframe_path.is_file() or keyframe_path.stat().st_size < 1000:
            cum_time += sc_dur
            continue

        raw_motion_path = scenes_dir / f"scene_{idx:02d}_motion.mp4"
        lipsync_path = scenes_dir / f"scene_{idx:02d}_lipsync.mp4"
        meta_path = scenes_dir / f"scene_{idx:02d}_motion.meta.json"

        has_broadcast = bool(storyboard_data.get("broadcast_timeline"))
        target_final = raw_motion_path if has_broadcast else (lipsync_path if (enable_lipsync and not is_cutaway) else raw_motion_path)
        if target_final.is_file() and target_final.stat().st_size > 10_000:
            model_tag = "kling-1.6-pro" if use_kling else "wan-2.1-i2v"
            logger.info(f"virtual_artist_motion_cached [model={model_tag}]: reusing {target_final.name} ($0.00 spend)")
            resolved_motions[idx] = target_final
            cum_time += sc_dur
            continue

        # Step A: Synthesize Base Performance Motion Video
        if not (raw_motion_path.is_file() and raw_motion_path.stat().st_size > 10_000):
            prompts = sc.get("motion_prompts") or {}
            cam_id = sc.get("camera_id", "")
            if "instrument" in cam_id or idx == 2:
                default_prompt = "Extreme macro close-up of musician's fingers moving swiftly up and down the guitar fretboard, fretting chords with rhythmic precision, picking vibrating strings, warm stage spotlight glinting off brass frets"
            elif "profile" in cam_id or idx == 3:
                default_prompt = "Cinematic concert camera slowly arcs 35 degrees around singer on elevated stage, stage spotlights sweeping in atmospheric haze, maintaining exact stage gown and lighting"
            elif "close_up" in cam_id or idx == 4:
                default_prompt = "Intimate portrait framing of singer: passionate vocal delivery, emotive singing eyes, subtle rhythm sway, hair flutter, breathing articulation"
            elif "crane" in cam_id or "orchestra" in cam_id or idx == 6:
                default_prompt = "Cinematic concert stage: live backing band performing on elevated riser, drummer energetically striking cymbals in rhythm, bassist swaying with the groove, rhythm guitarist strumming chords, stage spotlights sweeping through atmospheric haze"
            else:
                default_prompt = "Gentle singer performance: expressive pitch-inflected hand gestures rising with high vocal melody, breathing, subtle head tilt, natural hands, strictly two legs"

            if use_kling:
                prompt = prompts.get("kling") or default_prompt
                neg_prompt = "two hands rigidly clutching mic, stiff frozen hands, blurry face, distorted hands, stiff awkward movement, high-energy dance, extra limbs"
                adapter = kling_adapter
                model_provider, model_name = "Fal.ai/Kling", "kling-1.6-pro"
            else:
                prompt = prompts.get("wan") or default_prompt
                neg_prompt = "two hands rigidly clutching mic, rigid mic grip, frozen hands, extra limbs, phantom arms, dancing, jumping, morphing face, distorted anatomy"
                adapter = wan_adapter
                model_provider, model_name = "Fal.ai/Wan21", "wan-2.1-i2v"

            logger.info(f"synthesizing_virtual_artist_motion_{idx:02d} [model={model_name}]: {prompt[:60]}...")
            fal_url = await upload_to_fal(keyframe_path, api_key)
            await adapter.generate_video(
                image_url=fal_url,
                motion_prompt=prompt,
                output_path=raw_motion_path,
                duration=5,
                force_live=force_live,
                negative_prompt=neg_prompt,
            )
            meta_data = {
                "model": "kling" if use_kling else "wan",
                "prompt": prompt,
                "timestamp": str(Path(__file__).stat().st_mtime),
            }
            meta_path.write_text(json.dumps(meta_data, indent=2), encoding="utf-8")

        # Step B: Apply Beat-Synchronized Vocal Lipsync for singing scenes (skip if broadcast cuts will handle it, or cutaways/intro)
        is_intro = (cum_time + min(sc_dur, 5.0)) <= (first_sing_time + 0.5)
        if not has_broadcast and enable_lipsync and not is_cutaway and not is_intro and audio_path.is_file():
            try:
                from src.compositor.virtual_artist_broadcast_service import slice_cut_audio
                sliced_audio = scenes_dir / f"scene_{idx:02d}_audio.mp3"
                slice_dur = min(sc_dur, 5.0)
                slice_cut_audio(audio_path, cum_time, slice_dur, sliced_audio)
                target_audio = sliced_audio if sliced_audio.is_file() else audio_path

                logger.info(f"applying_latentsync_lipsync_{idx:02d} [{cum_time:.1f}s-{cum_time+slice_dur:.1f}s]: {raw_motion_path.name} -> {lipsync_path.name}")
                synced_v = await latentsync_adapter.lipsync_video(
                    video_url=str(raw_motion_path),
                    audio_path=target_audio,
                    output_path=lipsync_path,
                    force_live=force_live,
                )
                if synced_v and synced_v.is_file() and synced_v.stat().st_size > 10_000:
                    resolved_motions[idx] = synced_v
                    if episode_id:
                        rights_ledger.record_asset(
                            episode_id, AssetType.VIDEO_MOTION, str(synced_v),
                            "Fal.ai/LatentSync", "latentsync",
                            CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                            f"LIPSYNC-{idx}-{episode_id}", True,
                        )
                    cum_time += sc_dur
                    continue
            except Exception as e:
                logger.warning(f"latentsync_failed_fallback_to_raw_{idx:02d}: {e}")
        cum_time += sc_dur

        # Fallback to raw performance motion
        if raw_motion_path.is_file():
            resolved_motions[idx] = raw_motion_path
            if episode_id:
                rights_ledger.record_asset(
                    episode_id, AssetType.VIDEO_MOTION, str(raw_motion_path),
                    "Fal.ai/Kling" if use_kling else "Fal.ai/Wan21",
                    "kling-1.6-pro" if use_kling else "wan-2.1-i2v",
                    CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP,
                    f"PERF-MOTION-{idx}-{episode_id}", True,
                )

    return resolved_motions


__all__ = ["synthesize_virtual_artist_motion"]
