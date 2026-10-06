"""Studio 4K Single-Pass Master Producer.

Enforces Universal Artifact Caching, Resilient Idempotency, FAL Request State Persistence,
Velvet Anti-Fatigue Acoustic Mastering, AI Video Diffusion (Wan/Kling/Hunyuan), and 4K UHD rendering.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.services.binaural_spatial_audio import apply_binaural_spatial_mastering
from src.services.broadcast_export_service import (
    assemble_4k_master,
    assemble_dual_masters,
    export_metadata_packages,
    handle_long_play_export,
    handle_short_export,
)
from src.services.motion_tier_router import resolve_scene_motion_model
from src.services.soundtrack_service import soundtrack_service
from src.services.topic_memory import topic_memory
from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.screenplay_models import AmbientScenePrompt, AmbientStoryboard


def _resolve_scene_negative_prompt(scene: Any, default_camera: str = "locked_tripod") -> str:
    neg = getattr(scene, "motion_negative_prompt", None)
    base_neg = neg.strip() if (neg and isinstance(neg, str)) else ""
    cam = getattr(scene, "camera_rig", "") or default_camera
    extra_tokens = []
    if cam == "locked_tripod":
        extra_tokens.append("camera movement, camera pan, panning, tilt, zoom, zoom in, zoom out, forward camera movement, camera flythrough, walking tour, walking cadence, dolly, tracking shot, handheld camera, camera shake, jitter, violent wind, rapid shaking, fast motion, sudden lighting shift, flickering light, jumping foliage, jumping branches, discontinuous water flow, abrupt mist displacement, temporal jump, loop seam, morphing landscape, changing environment, hallucinating objects, appearing trees, appearing foliage, shifting rocks, altering cliff structures, structural drift, changing perspective, sunny sky, rainbow, sunlight shifts, altering colors")
    p_text = f"{getattr(scene, 'visual_prompt', '')} {getattr(scene, 'motion_prompt', '')}".lower()
    if "rain" in p_text or "monsoon" in p_text:
        extra_tokens.append("dry weather, bright sunshine, clear blue sky, cloudless, arid, parched")
    else:
        extra_tokens.append("clouds, cloudy, overcast sky, overcast, cumulus, stratus, cirrus, storm clouds, dark clouds, moving clouds, timelapse clouds, rapid clouds, rolling clouds, cloud morphing, rapid cloud shadows, sky flickering")
    if "waterfall" in p_text or "cascade" in p_text:
        extra_tokens.append("frozen ice, motionless water, stagnant pond, reverse water flow")
    extra_tokens.append("fast moving clouds, timelapse, time-lapse, rapid clouds, rolling storm clouds, accelerated sky, swirling clouds, cloud morphing, rapid cloud shadows, high-speed wind, storm winds, flickering sky")
    extra_tokens.append("gelatinous water, melting foam, static frozen water, boiling water artifacts, rubbery water, unnatural foam blobs, zero static vertical streaks, artifacts")
    parts = [p for p in [base_neg, ", ".join(extra_tokens)] if p]
    return ", ".join(parts)


class StudioProducer:
    """Produces 4K broadcast-grade relaxing video masters with acoustic mastering & AI video diffusion."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/studio_productions")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.fal_key = os.getenv("FAL_KEY", "")

    async def produce(
        self,
        sb: AmbientStoryboard,
        episode_id: Optional[str] = None,
        tier: str = "balanced",
        motion_model: str = "auto",
        image_model: str = "flux_dev",
        long_play_hours: Optional[float] = None,
        fade_to_black_hours: Optional[float] = None,
        generate_short: bool = False,
        photos_only: bool = False,
        motion_only: bool = False,
        audio_only: bool = False,
        master_only: bool = False,
        no_bgm: bool = False,
        enable_voiceover: bool = False,
        allow_fallback: bool = False,
        force_rerun: bool = False,
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_{sb.primary_archetype[:20]}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        if not sb or not getattr(sb, "scenes", None) or len(sb.scenes) == 0:
            raise RuntimeError(
                "Production halted: Screenplay script is the mandatory foundation for all production. "
                "No script or scenes found; stopping."
            )

        # Stage 1: Pre-Flight Deduplication & Autonomous Creative Auto-Pivot Gate
        if not episode_id:
            is_dup, conflict = await topic_memory.is_duplicate_topic(sb.title, genre=f"nature_{sb.cluster}")
            if is_dup and conflict:
                logger.warning(f"decision_duplicate_detected: '{sb.title}' matches {conflict.get('episode_id')}. Auto-pivoting...")
                sb.title = f"{sb.title} ~ Golden Twilight Edition"
                for s in sb.scenes:
                    s.visual_prompt = f"{s.visual_prompt} Bathed in warm golden twilight and serene evening tranquility."
            else:
                logger.info(f"decision_deduplication_clean: '{sb.title}' is unique. Proceeding without conflict.")

        # Stage 2: Keyframe Image Gate (Concurrent Idempotent Batch via visual_batch_service)
        def _resolve_scene_image_prompt(s: AmbientScenePrompt) -> str:
            raw_prompt = ""
            m_target = (image_model or "flux_dev").lower()
            if getattr(s, "image_model_configs", None) and isinstance(s.image_model_configs, dict):
                keys = ["flux_dev", "flux", "flux_pro", "zimage"] if "dev" in m_target else (["flux_pro", "flux_1_1_pro_ultra", "flux_dev", "zimage"] if "pro" in m_target or "ultra" in m_target else ["zimage", "flux_dev", "flux_pro"])
                for k in keys:
                    if k in s.image_model_configs:
                        cfg = s.image_model_configs[k]
                        if isinstance(cfg, dict) and cfg.get("prompt"):
                            raw_prompt = str(cfg["prompt"]).strip()
                            break
            if not raw_prompt:
                raw_prompt = s.visual_prompt.strip()
            return raw_prompt

        keyframe_tasks = [
            (
                _resolve_scene_image_prompt(s),
                ep_dir / f"keyframe_p{idx}.jpg",
                ep_dir / f"fal_req_p{idx}.json",
                idx,
            )
            for idx, s in enumerate(sb.scenes, 1)
        ]
        kf_force_rerun = force_rerun and photos_only
        image_results = await visual_batch_service.render_keyframes_batch(
            tasks=keyframe_tasks,
            aspect_ratio="16:9",
            force_rerun=kf_force_rerun,
            image_model=image_model,
        )

        if photos_only:
            return {
                "status": "success",
                "stage": "photos_only",
                "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results],
                "episode_dir": str(ep_dir),
            }

        # Stage 3: Motion Diffusion Gate (Parallel AI Video Diffusion with In-Flight Token Resumption)
        valid_keyframes = [p for p in image_results if p.is_file() and p.stat().st_size > 1000]
        if not valid_keyframes:
            raise RuntimeError("visual_diffusion_aborted: Zero valid keyframes were produced.")

        motion_tasks = []
        for idx, (s, kf) in enumerate(zip(sb.scenes, valid_keyframes), 1):
            custom_model_cfg = getattr(s, "model_configs", None) if isinstance(getattr(s, "model_configs", None), dict) else None
            chosen_model, m_allow_fallback, m_rationale = resolve_scene_motion_model(
                scene=s,
                tier=tier,
                requested_motion_model=motion_model,
                scene_index=idx - 1,
                total_scenes=len(valid_keyframes),
                genre=getattr(sb, "cluster", "relax/nature"),
            )
            motion_tasks.append(
                MotionClipTask(
                    image_path=kf,
                    motion_prompt=s.motion_prompt,
                    visual_prompt=s.visual_prompt,
                    output_path=ep_dir / f"motion_p{idx}.mp4",
                    duration_seconds=s.duration_seconds,
                    model=chosen_model,
                    domain=s.domain,
                    req_file=ep_dir / f"fal_motion_req_p{idx}.json",
                    allow_fallback=allow_fallback or m_allow_fallback,
                    force_rerun=force_rerun,
                    negative_prompt=_resolve_scene_negative_prompt(s),
                    model_configs=custom_model_cfg,
                )
            )

        video_clips = await visual_batch_service.render_motion_batch(
            tasks=motion_tasks,
        )

        if motion_only:
            return {
                "status": "success",
                "stage": "motion_only",
                "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results],
                "raw_videos": [str(c) for c in video_clips],
                "video_clips": [str(c) for c in video_clips],
                "episode_dir": str(ep_dir),
            }

        # Stage 4: Acoustic Foley & Brown Noise Mastering Gate
        audio_stems = []
        bgm_path = ep_dir / "raw_soundtrack.mp3"
        legacy_bgm = ep_dir / "soundscape_master.mp3"
        if legacy_bgm.is_file() and not bgm_path.is_file():
            try:
                legacy_bgm.rename(bgm_path)
            except Exception:
                pass
        if not no_bgm:
            if not bgm_path.is_file() or bgm_path.stat().st_size < 1000:
                bgm_path = await soundtrack_service.synthesize_ambient_soundtrack(
                    title=sb.title,
                    tags=sb.audio_tags or "waterfall brown noise, roaring cascade, natural water foley, 432hz ambient",
                    out_path=bgm_path,
                    total_duration=sb.total_duration,
                    genre="ambient nature waterfall soundscape",
                    episode_id=ep_dir.name,
                )
            if bgm_path and bgm_path.is_file():
                audio_stems.append(bgm_path)

        voice_path = ep_dir / "voiceover_tts.wav"
        spoken_text = getattr(sb, "spoken_narration_script", None)
        if enable_voiceover and spoken_text and spoken_text.strip():
            if not voice_path.is_file() or voice_path.stat().st_size < 1000:
                try:
                    from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
                    tts = AzureSpeechTTSAdapter()
                    v_id = "te-IN-ShrutiNeural" if any("\u0c00" <= c <= "\u0c7f" for c in spoken_text) else "en-US-JennyNeural"
                    await tts.synthesize_to_file(text=spoken_text.strip(), output_path=voice_path, voice_id=v_id)
                except Exception as tts_err:
                    logger.warning(f"tts_voiceover_failed: {tts_err}")
            if voice_path.is_file() and voice_path.stat().st_size > 1000:
                audio_stems.append(voice_path)

        spatial_audio_path = ep_dir / "velvet_binaural_master_48k.mp3"
        legacy_spatial = ep_dir / "binaural_soundscape_master.wav"
        if legacy_spatial.is_file() and not spatial_audio_path.is_file():
            try:
                legacy_spatial.rename(spatial_audio_path)
            except Exception:
                pass
        if not spatial_audio_path.is_file() or spatial_audio_path.stat().st_size < 1000:
            spatial_audio_path = await asyncio.to_thread(
                apply_binaural_spatial_mastering,
                input_audio_stems=audio_stems,
                output_path=spatial_audio_path,
                target_lufs=-14.0,
                ducking_db=-18.0,
                duration_seconds=None,
            )

        if audio_only:
            return {
                "status": "success",
                "stage": "audio_only",
                "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results],
                "spatial_audio": str(spatial_audio_path),
                "episode_dir": str(ep_dir),
            }

        # Stage 5: Broadcast Assembly & Export
        if generate_short:
            return await handle_short_export(
                sb, ep_dir, video_clips, spatial_audio_path, t_start,
                long_play_hours, fade_to_black_hours, force_rerun
            )

        target_dur = float(getattr(sb, "total_duration_seconds", None) or getattr(sb, "total_duration", None) or 60.0)
        dual_res = await asyncio.to_thread(
            assemble_dual_masters,
            video_clips=video_clips,
            audio_track=spatial_audio_path,
            ep_dir=ep_dir,
            target_fps=sb.recommended_fps,
            force_rerun=force_rerun,
            music_only_audio=bgm_path,
            target_duration_sec=target_dur,
        )

        metadata_pkgs = export_metadata_packages(sb, ep_dir)

        # Update Topic Memory
        await topic_memory.record_production(
            topic=sb.title,
            genre=f"nature_{sb.cluster}",
            tags=metadata_pkgs.get("youtube", {}).get("seo_tags", []),
            episode_id=ep_dir.name,
        )

        return {
            "status": "success",
            "production_type": "broadcast_master",
            "episode_id": ep_dir.name,
            "master_4k_path": str(dual_res["master_4k"]),
            "master_1080p_path": str(dual_res["master_1080p"]),
            "render_time_seconds": round(time.time() - t_start, 2),
            "keyframes": [str(p) for p in image_results],
            "video_clips": [str(c) for c in video_clips],
            "metadata": metadata_pkgs,
        }


# Backwards compatibility alias
AmbientWorldProducer = StudioProducer
