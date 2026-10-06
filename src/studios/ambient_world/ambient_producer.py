"""Ambient World & Relaxation 4K Single-Pass Master Producer.

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
from src.services.ambient_export_service import (
    assemble_4k_master,
    assemble_dual_masters,
    export_metadata_packages,
    handle_long_play_export,
    handle_short_export,
)
from src.services.binaural_spatial_audio import apply_binaural_spatial_mastering
from src.services.soundtrack_service import soundtrack_service
from src.services.topic_memory import topic_memory
from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.ambient_world.ambient_storyboard import AmbientStoryboard


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


class AmbientWorldProducer:
    """Produces 4K broadcast-grade relaxing ambient videos with Velvet audio & AI video diffusion."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/ambient_world")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)
        self.fal_key = os.getenv("FAL_KEY", "")

    async def produce(
        self,
        sb: AmbientStoryboard,
        episode_id: Optional[str] = None,
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
        allow_fallback: bool = False,
        force_rerun: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_{sb.primary_archetype[:20]}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Pre-Flight Deduplication & Autonomous Creative Auto-Pivot Gate
        if not episode_id:
            is_dup, conflict = await topic_memory.is_duplicate_topic(sb.title, genre=f"ambient_{sb.cluster}")
            if is_dup and conflict:
                logger.warning(f"decision_duplicate_detected: '{sb.title}' matches {conflict.get('episode_id')}. Auto-pivoting to unique sunset theme...")
                print(f"[DECISION - TOPIC DEDUPLICATION] Duplicate topic detected (matches {conflict.get('episode_id')}). Auto-pivoting to unique Twilight variation to protect channel CTR.")
                sb.title = f"{sb.title} ~ Golden Twilight Serenade"
                for s in sb.scenes:
                    s.visual_prompt = f"{s.visual_prompt} Bathed in warm golden twilight and serene evening tranquility."
            else:
                logger.info(f"decision_deduplication_clean: '{sb.title}' is unique. Proceeding without conflict.")
                print(f"[DECISION - TOPIC DEDUPLICATION] Title '{sb.title}' is 100% novel in Topic Memory. Proceeding without conflict.")

        # Stage 2: Keyframe Image Gate (Concurrent Idempotent Batch via visual_batch_service)
        def _resolve_scene_image_prompt(s: AmbientScenePrompt) -> str:
            raw_prompt = ""
            if getattr(s, "image_model_configs", None) and isinstance(s.image_model_configs, dict):
                for m_key in ("flux_1_1_pro_ultra", "flux_pro_ultra", "flux_1_1_pro", "flux", "zimage"):
                    if m_key in s.image_model_configs:
                        cfg = s.image_model_configs[m_key]
                        if isinstance(cfg, dict) and cfg.get("prompt"):
                            raw_prompt = str(cfg["prompt"]).strip()
                            break
            if not raw_prompt:
                raw_prompt = s.visual_prompt.strip()

            # Dual-layer structural fail-safe for symmetrical frontal living wallpapers:
            sub_genre = (getattr(sb, "sub_genre", "") or getattr(sb, "primary_archetype", "") or "").lower()
            if "waterfall" in sub_genre or "cascade" in sub_genre or "gorge" in sub_genre or "river" in sub_genre:
                for bad_kw in ("shoreline", "wild stone riverbank", "bottom-left and bottom-right corners", "side overlook", "gravel shoreline"):
                    raw_prompt = raw_prompt.replace(bad_kw, "centered water basin")
                if "symmetrical" not in raw_prompt.lower() and "dead-center" not in raw_prompt.lower():
                    raw_prompt = "Dead-center symmetrical frontal vantage point, eye-level head-on straight perspective, centered bilateral composition with zero side-angle, zero three-quarter view. " + raw_prompt
            return raw_prompt

        t_stage2 = time.time()
        logger.info(f"stage_triggered: stage='Stage 2: Keyframes' episode_id='{ep_dir.name}' timestamp={t_stage2}")
        print(f"\n[STAGE 2 TRIGGERED] Synthesizing Keyframes for {ep_dir.name}...")
        try:
            kf_tasks = [
                (_resolve_scene_image_prompt(scene), ep_dir / f"keyframe_p{scene.scene_index}.jpg", ep_dir / f"fal_req_p{scene.scene_index}.json", scene.scene_index)
                for scene in sb.scenes
            ]
            kf_force_rerun = force_rerun and photos_only
            keyframe_paths = await visual_batch_service.render_keyframes_batch(kf_tasks, force_rerun=kf_force_rerun, image_model=image_model)
            dur_stage2 = time.time() - t_stage2
            logger.info(f"stage_completed: stage='Stage 2: Keyframes' episode_id='{ep_dir.name}' duration={dur_stage2:.2f}s count={len(keyframe_paths)} timestamp={time.time()}")
            print(f"[STAGE 2 COMPLETED] Keyframes ready in {dur_stage2:.2f}s ({len(keyframe_paths)} images).")
        except Exception as ex:
            dur_stage2 = time.time() - t_stage2
            logger.error(f"stage_failed: stage='Stage 2: Keyframes' episode_id='{ep_dir.name}' duration={dur_stage2:.2f}s error='{ex}' timestamp={time.time()}")
            raise

        # Stage 2 Gate: If photos_only is requested, dispatch review notification and stop
        if photos_only:
            from src.services.notification import notification_service
            await notification_service.notify_keyframes_ready(
                channel_name=f"Studio Ambient ({sb.cluster.upper()})",
                episode_id=ep_dir.name,
                title=sb.title,
                keyframe_paths=[str(p.resolve()) for p in keyframe_paths],
            )
            return {
                "episode_id": ep_dir.name, "title": sb.title, "status": "photos_ready_for_review",
                "keyframes": [str(p) for p in keyframe_paths],
                "thumbnails": [],
                "storage_path": str(ep_dir),
            }

        # Stage 3: AI Video Diffusion Motion Synthesis
        t_stage3 = time.time()
        logger.info(f"stage_triggered: stage='Stage 3: Video Motion' episode_id='{ep_dir.name}' model='{motion_model}' timestamp={t_stage3}")
        print(f"\n[STAGE 3 TRIGGERED] Synthesizing Video Motion for {ep_dir.name} ({motion_model})...")
        try:
            motion_tasks = []
            for i, (scene, kf_path) in enumerate(zip(sb.scenes, keyframe_paths)):
                s_m = (getattr(scene, "motion_type", None) or "").lower()
                is_ai = (s_m == "ai_diffusion") or (not s_m and (getattr(scene, "domain", "") in ("water_fluid", "water_impact_collision") or i == 0 or len(sb.scenes) == 1))
                m_choice = motion_model if is_ai else "local_zoompan"
                motion_tasks.append(MotionClipTask(
                    image_path=kf_path,
                    motion_prompt=scene.motion_prompt,
                    visual_prompt=scene.visual_prompt,
                    output_path=ep_dir / f"motion_p{scene.scene_index}.mp4",
                    duration_seconds=scene.duration_seconds,
                    model=m_choice,
                    domain=scene.domain,
                    req_file=ep_dir / f"fal_diff_req_p{scene.scene_index}.json",
                    allow_fallback=allow_fallback or (m_choice == "local_zoompan"),
                    force_rerun=force_rerun,
                    negative_prompt=_resolve_scene_negative_prompt(scene),
                    model_configs=getattr(scene, "model_configs", {}),
                ))
            video_clip_paths = await visual_batch_service.render_motion_batch(motion_tasks)
            dur_stage3 = time.time() - t_stage3
            logger.info(f"stage_completed: stage='Stage 3: Video Motion' episode_id='{ep_dir.name}' duration={dur_stage3:.2f}s count={len(video_clip_paths)} timestamp={time.time()}")
            print(f"[STAGE 3 COMPLETED] Motion clips ready in {dur_stage3:.2f}s ({len(video_clip_paths)} clips).")
        except Exception as ex:
            dur_stage3 = time.time() - t_stage3
            logger.error(f"stage_failed: stage='Stage 3: Video Motion' episode_id='{ep_dir.name}' duration={dur_stage3:.2f}s error='{ex}' timestamp={time.time()}")
            raise

        # Stage 3 Gate: If motion_only is requested, stop and return motion clips for review
        if motion_only:
            return {
                "episode_id": ep_dir.name, "title": sb.title, "status": "motion_ready_for_review",
                "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
                "storage_path": str(ep_dir),
            }

        # Stage 4: Audio Synthesis & Binaural 3D Velvet Mastering (unless --no-bgm)
        t_stage4 = time.time()
        logger.info(f"stage_triggered: stage='Stage 4: Audio' episode_id='{ep_dir.name}' timestamp={t_stage4}")
        print(f"\n[STAGE 4 TRIGGERED] Synthesizing & Mastering Audio for {ep_dir.name}...")
        try:
            master_bgm_path = None
            if not no_bgm:
                raw_bgm_path, master_bgm_path = ep_dir / "raw_soundtrack.mp3", ep_dir / "velvet_binaural_master_48k.mp3"
                if not master_bgm_path.is_file() or master_bgm_path.stat().st_size < 1000:
                    eff_archetype = sb.primary_archetype or getattr(sb, "sub_genre", "")
                    await soundtrack_service.synthesize_ambient_soundtrack(
                        title=sb.title,
                        tags=sb.audio_tags,
                        out_path=raw_bgm_path,
                        total_duration=sb.total_duration,
                        genre=f"ambient_{sb.cluster}",
                        episode_id=ep_dir.name,
                        archetype=eff_archetype,
                        force_rerun=force_rerun and audio_only,
                        prompt=getattr(sb, "audio_prompt", None),
                    )
                    await asyncio.to_thread(apply_binaural_spatial_mastering, input_audio=raw_bgm_path, output_audio=master_bgm_path, target_lufs=-21.0)
                else:
                    logger.info(f"decision_audio_master_cache_hit: Reusing {master_bgm_path.name} ($0.00 spend)")
                    print(f"[DECISION - AUDIO MASTER CACHE HIT] Master audio already exists on disk ({master_bgm_path.name}). Reusing asset ($0.00 spend).")
            dur_stage4 = time.time() - t_stage4
            logger.info(f"stage_completed: stage='Stage 4: Audio' episode_id='{ep_dir.name}' duration={dur_stage4:.2f}s timestamp={time.time()}")
            print(f"[STAGE 4 COMPLETED] Audio ready in {dur_stage4:.2f}s.")
        except Exception as ex:
            dur_stage4 = time.time() - t_stage4
            logger.error(f"stage_failed: stage='Stage 4: Audio' episode_id='{ep_dir.name}' duration={dur_stage4:.2f}s error='{ex}' timestamp={time.time()}")
            raise

        # Stage 4 Gate: If audio_only is requested, stop and return stems for review
        if audio_only:
            return {
                "episode_id": ep_dir.name, "title": sb.title, "status": "audio_ready_for_review",
                "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
                "bgm_path": str(master_bgm_path) if master_bgm_path else None, "storage_path": str(ep_dir),
            }

        # Stage 5: Master Assembly & Packaging Delegation
        t_stage5 = time.time()
        logger.info(f"stage_triggered: stage='Stage 5: 4K Master & Packaging' episode_id='{ep_dir.name}' duration_target={sb.total_duration}s timestamp={t_stage5}")
        print(f"\n[STAGE 5 TRIGGERED] Assembling 4K Master & Packaging for {ep_dir.name} (target: {sb.total_duration}s)...")
        try:
            masters = await asyncio.to_thread(
                assemble_dual_masters,
                video_clips=video_clip_paths,
                audio_path=master_bgm_path,
                ep_dir=ep_dir,
                scene_hold_sec=sb.total_duration or 60.0,
                force_rerun=force_rerun,
            )
            master_4k_path = masters["music_master"]
            master_nature_path = masters["nature_master"]

            long_play_path = await asyncio.to_thread(handle_long_play_export, master_4k_path, ep_dir, long_play_hours, fade_to_black_hours)
            short_video_path = await asyncio.to_thread(handle_short_export, master_4k_path, ep_dir, generate_short)

            # Render high-CTR SEO Thumbnails in Stage 5 once master broadcast is locked
            long_thumb_prompt = f"Award-winning high-CTR YouTube thumbnail landscape photograph of {sb.title}. High contrast, stunning cinematic depth, crisp 35mm bokeh, cozy atmospheric light, 8k, zero text."
            short_thumb_prompt = f"Award-winning high-CTR vertical YouTube Short thumbnail photograph of {sb.title}. Striking 9:16 vertical composition, intense visual depth, rich atmospheric mist, 8k, zero text."
            thumbnail_paths = await visual_batch_service.render_thumbnails_batch(
                tasks=[
                    (long_thumb_prompt, ep_dir / "thumbnail_music_4k.jpg", "16:9"),
                    (short_thumb_prompt, ep_dir / "thumbnail_9x16_short.jpg", "9:16"),
                ],
                force_rerun=force_rerun,
                image_model=image_model,
            )

            yt_package, ab_thumbnails, localized = export_metadata_packages(sb, ep_dir, long_play_hours, fade_to_black_hours)
            await topic_memory.remember_topic(
                topic=sb.title,
                genre=f"ambient_{sb.cluster}",
                tags=[sb.primary_archetype, sb.cluster],
                story_synopsis=f"{sb.title} ({len(sb.scenes)} visual perspectives 4K UHD)",
                episode_id=ep_dir.name,
            )
            dur_stage5 = time.time() - t_stage5
            logger.info(f"stage_completed: stage='Stage 5: 4K Master & Packaging' episode_id='{ep_dir.name}' duration={dur_stage5:.2f}s master='{master_4k_path.name}' timestamp={time.time()}")
            print(f"[STAGE 5 COMPLETED] 4K Master & Packaging finished in {dur_stage5:.2f}s.")
        except Exception as ex:
            dur_stage5 = time.time() - t_stage5
            logger.error(f"stage_failed: stage='Stage 5: 4K Master & Packaging' episode_id='{ep_dir.name}' duration={dur_stage5:.2f}s error='{ex}' timestamp={time.time()}")
            raise

        render_time = round(time.time() - t_start, 2)
        logger.info(f"ambient_production_ready: {ep_dir.name} in {render_time}s")
        return {
            "episode_id": ep_dir.name, "title": sb.title, "master_video_path": str(master_4k_path),
            "master_nature_video_path": str(master_nature_path),
            "long_play_video_path": str(long_play_path) if long_play_path else None,
            "short_video_path": str(short_video_path) if short_video_path else None,
            "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
            "bgm_path": str(master_bgm_path), "youtube_package": yt_package.model_dump(),
            "thumbnail_variants": ab_thumbnails.model_dump(),
            "localized_metadata": {k: v.model_dump() for k, v in localized.items()},
            "render_time_seconds": render_time, "storage_path": str(ep_dir),
        }
