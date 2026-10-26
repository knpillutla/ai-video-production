"""Studio 4K Single-Pass Master Producer.

Enforces Universal Artifact Caching, Resilient Idempotency, FAL Request State Persistence,
Velvet Anti-Fatigue Acoustic Mastering, AI Video Diffusion (Wan/Kling/Hunyuan), and 4K UHD rendering.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Dict, List, Optional

from src.core.step_logger import log_pipeline_step
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
    w_text = f"{getattr(scene, 'weather', '')} {getattr(scene, 'visual_prompt', '')} {getattr(scene, 'motion_prompt', '')}".lower()
    weather_negs = ""
    if any(k in w_text for k in ("rain", "storm", "downpour", "cyclone", "monsoon")):
        weather_negs = "snow, snowfall, snowflakes, blizzard, ice, frost, frosty, frozen ground, snowy mountains, winter, sleet, hail, slush, white snow caps"
    elif any(k in w_text for k in ("snow", "blizzard", "winter")):
        weather_negs = "rain, rainfall, rain droplets, torrential rain, downpour, puddle reflections, wet water drops, monsoon, thunderstorm, liquid rain, summer rain"
    return ", ".join([p for p in [base_neg, weather_negs, "camera movement, camera pan, panning, tilt, zoom, camera shake, jitter, rapid motion, flickering, temporal jump, loop seam, morphing, changing environment, clouds, overcast, storm clouds, gelatinous water, artifacts"] if p])


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
        tts_model: Optional[str] = None,
        execution_mode: str = "test",
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_{sb.primary_archetype[:20]}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        eff_exec = (execution_mode or "").strip().lower()
        if (not eff_exec or eff_exec == "auto") and ep_dir and (ep_dir / "user_inputs.json").is_file():
            try:
                import json
                eff_exec = (json.loads((ep_dir / "user_inputs.json").read_text("utf-8")).get("execution_mode") or "test").strip().lower()
            except Exception:
                eff_exec = "test"
        eff_exec = eff_exec or "test"

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
            m_target = (image_model or "flux_dev").lower()
            cfgs = getattr(s, "image_model_configs", None) or {}
            key_map = {"zimage": ["zimage", "z_image"], "pro": ["flux_pro", "flux_1_1_pro_ultra"], "dev": ["flux_dev", "flux"]}
            match_keys = next((v for k, v in key_map.items() if k in m_target), [m_target])
            for k in match_keys:
                if k in cfgs and isinstance(cfgs[k], dict) and cfgs[k].get("prompt"):
                    return str(cfgs[k]["prompt"]).strip()
            if ("gemini" in m_target or "imagen" in m_target) and s.visual_prompt and s.visual_prompt.strip():
                return s.visual_prompt.strip()
            raise RuntimeError(f"Mandatory image_model_configs['{m_target}'] missing or empty. No fallbacks allowed.")

        keyframe_tasks = []
        map_rendered_paths = {}
        from src.services.map_route_engine import render_4k_itinerary_summary_card, render_4k_route_map

        tour_stops = []
        for idx, s in enumerate(sb.scenes):
            st_type = str(getattr(s, "shot_type", "") or getattr(s, "perspective_type", "") or "").lower()
            loc_hub = str(getattr(s, "location_hub", "") or "").lower()
            is_ov = bool(getattr(s, "is_itinerary_overview", False) or "overview" in st_type or "overview" in loc_hub or "master day" in loc_hub)
            is_sum = bool(getattr(s, "is_itinerary_summary", False) or "summary" in st_type or "summary" in loc_hub)
            is_map = bool(getattr(s, "is_map_transition", False) or "overhead_cartographic" in st_type or "transit" in loc_hub)
            if not getattr(s, "origin_coords", None) or is_ov or is_sum or is_map or getattr(s, "is_vacation_scope", False):
                continue
            nxt_tr = next((nxt for nxt in sb.scenes[idx + 1:] if getattr(nxt, "is_map_transition", False)), None)
            tour_stops.append({
                "name": getattr(s, "attraction_name", None) or getattr(s, "origin_name", None) or f"Stop {idx + 1}",
                "attraction_name": getattr(s, "attraction_name", None) or getattr(s, "origin_name", None),
                "origin_name": getattr(s, "origin_name", None),
                "coords": s.origin_coords,
                "visit_duration": getattr(s, "visit_duration", None),
                "attraction_cost": getattr(s, "attraction_cost", None),
                "start_time": getattr(s, "start_time", None),
                "end_time": getattr(s, "end_time", None),
                "distance_local": getattr(nxt_tr, "distance_local", None) or getattr(s, "distance_local", None),
                "transit_duration": getattr(nxt_tr, "transit_duration", None) or getattr(s, "transit_duration", None),
                "transit_mode": getattr(nxt_tr, "transit_mode", None) or getattr(s, "transit_mode", None),
                "approx_leg_cost": getattr(nxt_tr, "approx_leg_cost", None) or getattr(s, "approx_leg_cost", None),
            })

        from src.studios.documentary_studio.doc_directorial_prompt import is_tour_archetype
        is_itinerary_tour = is_tour_archetype(
            getattr(sb, "primary_archetype", "")
            or getattr(sb, "archetype", "")
            or getattr(sb, "sub_genre", "")
            or getattr(sb, "genre", "")
            or ""
        )

        for idx, s in enumerate(sb.scenes, 1):
            target_kf = ep_dir / f"keyframe_p{idx}.jpg"
            if is_itinerary_tour and getattr(s, "is_vacation_scope", False):
                from src.services.map_route_engine import render_4k_leisure_vacation_card
                render_4k_leisure_vacation_card(
                    tour_title=sb.title,
                    output_path=target_kf,
                    force_rerun=force_rerun,
                )
                map_rendered_paths[idx] = target_kf
            elif is_itinerary_tour and (
                getattr(s, "is_itinerary_summary", False)
                or getattr(s, "is_itinerary_overview", False)
                or getattr(s, "shot_type", "") in ("itinerary_overview_card", "itinerary_summary_card")
            ) and (getattr(sb, "itinerary_summary", None) or tour_stops):
                from src.services.itinerary_card_engine import render_4k_itinerary_hierarchy_card
                render_4k_itinerary_hierarchy_card(
                    tour_title=sb.title,
                    stops=tour_stops or [getattr(sc, "__dict__", {}) for sc in sb.scenes],
                    output_path=target_kf,
                    summary=sb.itinerary_summary[0] if getattr(sb, "itinerary_summary", None) else None,
                    force_rerun=force_rerun,
                )
                map_rendered_paths[idx] = target_kf
            elif is_itinerary_tour and getattr(s, "is_map_transition", False) and getattr(s, "origin_coords", None) and getattr(s, "destination_coords", None):
                prior_attrs = sum(1 for ps in sb.scenes[:idx - 1] if not (getattr(ps, "is_map_transition", False) or getattr(ps, "is_itinerary_overview", False) or getattr(ps, "is_itinerary_summary", False) or getattr(ps, "is_vacation_scope", False)))
                render_4k_route_map(
                    origin_name=s.origin_name or "Origin",
                    dest_name=s.destination_name or "Destination",
                    origin_coords=(s.origin_coords[0], s.origin_coords[1]),
                    dest_coords=(s.destination_coords[0], s.destination_coords[1]),
                    distance_badge=s.distance_local or "1.5 km",
                    transit_mode=s.transit_mode or "walk",
                    output_path=target_kf,
                    all_stops=tour_stops or None,
                    tour_title=sb.title,
                    current_stop_index=max(1, prior_attrs),
                    force_rerun=force_rerun,
                )
                map_rendered_paths[idx] = target_kf
            else:
                keyframe_tasks.append((
                    _resolve_scene_image_prompt(s),
                    target_kf,
                    ep_dir / f"fal_req_p{idx}.json",
                    idx,
                ))

        existing_kfs = [ep_dir / f"keyframe_p{idx}.jpg" for idx in range(1, len(sb.scenes) + 1)]
        all_kfs_exist = all(p.is_file() and p.stat().st_size > 1000 for p in existing_kfs)

        if (motion_only or audio_only or master_only) and all_kfs_exist:
            logger.info(f"downstream_stage_reuse_keyframes: episode='{ep_dir.name}' reusing {len(existing_kfs)} existing keyframes ($0 spend)")
            image_results = existing_kfs
        else:
            if (motion_only or audio_only or master_only) and not all_kfs_exist:
                for kf_idx, target_kf in enumerate(existing_kfs, 1):
                    if not (target_kf.is_file() and target_kf.stat().st_size > 1000):
                        for cand in ep_dir.parent.rglob(f"keyframe_p{kf_idx}.jpg"):
                            if cand.is_file() and cand.stat().st_size > 1000 and cand != target_kf:
                                import shutil
                                shutil.copy2(cand, target_kf)
                                break
                all_kfs_exist = all(p.is_file() and p.stat().st_size > 1000 for p in existing_kfs)
                if all_kfs_exist:
                    logger.info(f"downstream_stage_recovered_keyframes: episode='{ep_dir.name}' recovered {len(existing_kfs)} keyframes ($0 spend)")
                    image_results = existing_kfs
            if not ((motion_only or audio_only or master_only) and all_kfs_exist):
                kf_force_rerun = force_rerun and photos_only
                eff_img_model = "google_imagen3" if (motion_only or audio_only or master_only) and (not image_model or "flux" in image_model) else image_model
                diff_results = await visual_batch_service.render_keyframes_batch(
                    tasks=keyframe_tasks,
                    aspect_ratio="16:9",
                    force_rerun=kf_force_rerun,
                    image_model=eff_img_model,
                ) if keyframe_tasks else []
                diff_map = {idx: p for (_, p, _, idx) in keyframe_tasks}
                image_results = [map_rendered_paths.get(idx, diff_map.get(idx, ep_dir / f"keyframe_p{idx}.jpg")) for idx in range(1, len(sb.scenes) + 1)]

        if photos_only:
            return {
                "status": "success",
                "stage": "photos_only",
                "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results],
                "episode_dir": str(ep_dir),
            }

        # Stage 3: Shot-Aligned Narration Gate (Synthesized during Audio Stage or full auto pipeline)
        voice_path = ep_dir / "spoken_narration.mp3"
        spoken_text = getattr(sb, "spoken_narration_script", None)
        has_narr = any(bool(getattr(s, "narration_text", None)) for s in sb.scenes) if hasattr(sb, "scenes") else False
        if not motion_only and not photos_only and enable_voiceover and (spoken_text or has_narr):
            log_pipeline_step("checking audio", "Spoken Narration Voiceover", "started", metadata={"file": voice_path.name})
            try:
                from src.services.shot_narration_service import synthesize_shot_aligned_narration
                narr_res = await synthesize_shot_aligned_narration(
                    scenes=sb.scenes, ep_dir=ep_dir, fallback_script=spoken_text,
                    total_target_sec=float(sb.total_duration or 60.0), force_rerun=force_rerun and audio_only,
                    tts_model=tts_model,
                )
                if narr_res.get("narration_path") and Path(narr_res["narration_path"]).is_file():
                    voice_path = Path(narr_res["narration_path"])
                if narr_res.get("shot_durations"):
                    for sc, n_dur in zip(sb.scenes, narr_res["shot_durations"]):
                        sc.duration_seconds = max(float(sc.duration_seconds or 0.0), float(n_dur))
                    tot_d = sum(float(sc.duration_seconds) for sc in sb.scenes)
                    if hasattr(sb, "total_duration"): sb.total_duration = tot_d
                if not voice_path.is_file() or voice_path.stat().st_size < 1000:
                    raise RuntimeError(f"Narration voiceover master '{voice_path.name}' was not created or is empty.")
                log_pipeline_step("checking audio", "Spoken Narration Voiceover", "completed", "narration synchronized and shot durations locked", {"file": voice_path.name, "total_duration": getattr(sb, "total_duration", None)})
            except Exception as tts_err:
                log_pipeline_step("checking audio", "Spoken Narration Voiceover", "failed", str(tts_err), {"file": voice_path.name})
                logger.error(f"tts_voiceover_failed: {tts_err}")
                raise RuntimeError(f"Documentary voiceover narration synthesis failed: {tts_err}") from tts_err

        # Acoustic Foley & Brown Noise Mastering Gate
        audio_stems = []
        bgm_path = ep_dir / "raw_soundtrack.mp3"
        legacy_bgm = ep_dir / "soundscape_master.mp3"
        if legacy_bgm.is_file() and not bgm_path.is_file():
            try: legacy_bgm.rename(bgm_path)
            except Exception: pass
        if not no_bgm:
            log_pipeline_step("checking audio", "BGM Soundtrack", "started", metadata={"file": bgm_path.name})
            if bgm_path.is_file() and bgm_path.stat().st_size >= 1000 and not force_rerun:
                log_pipeline_step("checking audio", "BGM Soundtrack", "completed", "soundtrack exists, soundtrack not recreated", {"file": bgm_path.name, "cost": "$0.00"})
            else:
                from src.services.relaxation_instruments import get_random_soothing_instrument_set
                first_scene = sb.scenes[0] if hasattr(sb, "scenes") and sb.scenes else None
                scene_visual = getattr(first_scene, "visual_prompt", "") or getattr(sb, "story_topic", "") or getattr(sb, "title", "")
                dyn_palette = get_random_soothing_instrument_set(setting_context=f"{getattr(sb, 'genre', '')} {getattr(sb, 'primary_archetype', '')} {scene_visual[:120]}")
                eff_tags = getattr(sb, "audio_tags", "") or dyn_palette.suno_tags
                raw_prompt = getattr(sb, "audio_prompt", "") or (sb.audio_master.suno_prompt if hasattr(sb, "audio_master") and getattr(sb, "audio_master") and hasattr(sb.audio_master, "suno_prompt") else "")
                if raw_prompt and raw_prompt.strip():
                    eff_prompt = raw_prompt.strip()
                    if "Scene Context" not in eff_prompt and scene_visual:
                        eff_prompt = f"[Scene Context: {scene_visual[:140]}]\n{eff_prompt}"
                else:
                    eff_prompt = dyn_palette.suno_prompt
                bgm_path = await soundtrack_service.synthesize_ambient_soundtrack(
                    title=sb.title, tags=eff_tags,
                    out_path=bgm_path, total_duration=sb.total_duration, genre=f"{getattr(sb, 'genre', 'relax')} {getattr(sb, 'cluster', 'studio')} soundscape",
                    episode_id=ep_dir.name, archetype=getattr(sb, "primary_archetype", ""),
                    prompt=eff_prompt, visual_prompt=scene_visual, force_rerun=force_rerun,
                )
                log_pipeline_step("checking audio", "BGM Soundtrack", "completed", "soundtrack synthesized", {"file": bgm_path.name})
            if bgm_path and bgm_path.is_file():
                audio_stems.append(bgm_path)

        if voice_path.is_file() and voice_path.stat().st_size > 1000:
            audio_stems.append(voice_path)

        spatial_audio_path = ep_dir / "velvet_binaural_master_48k.mp3"
        legacy_spatial = ep_dir / "binaural_soundscape_master.wav"
        if legacy_spatial.is_file() and not spatial_audio_path.is_file():
            try:
                legacy_spatial.rename(spatial_audio_path)
            except Exception:
                pass
        log_pipeline_step("checking audio", "Spatial Binaural Master", "started", metadata={"file": spatial_audio_path.name})
        if spatial_audio_path.is_file() and spatial_audio_path.stat().st_size >= 1000 and not force_rerun:
            log_pipeline_step("checking audio", "Spatial Binaural Master", "completed", "spatial audio exists, spatial audio not recreated", {"file": spatial_audio_path.name, "cost": "$0.00"})
        else:
            if bgm_path and Path(bgm_path).is_file():
                spatial_audio_path = await asyncio.to_thread(
                    apply_binaural_spatial_mastering,
                    input_audio=bgm_path,
                    output_audio=spatial_audio_path,
                    target_lufs=-14.0,
                )
                log_pipeline_step("checking audio", "Spatial Binaural Master", "completed", "spatial audio synthesized", {"file": spatial_audio_path.name})

        if audio_only:
            return {
                "status": "success",
                "stage": "audio_only",
                "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results],
                "bgm_path": str(spatial_audio_path) if spatial_audio_path else (str(bgm_path) if bgm_path else None),
                "narration_path": str(voice_path) if voice_path.is_file() else None,
                "spatial_audio": str(spatial_audio_path) if spatial_audio_path else None,
                "audio_stems": [str(p) for p in audio_stems if p.is_file()],
                "episode_dir": str(ep_dir),
            }

        # Stage 4: Motion Diffusion Gate (Parallel AI Video Diffusion with In-Flight Token Resumption)
        existing_vids = [ep_dir / f"motion_p{idx}.mp4" for idx in range(1, len(sb.scenes) + 1)]
        all_motion_exist = len(existing_vids) > 0 and all(p.is_file() and p.stat().st_size > 1000 for p in existing_vids)

        if master_only and all_motion_exist and not (force_rerun and motion_only):
            logger.info(f"downstream_stage_reuse_motion: episode='{ep_dir.name}' reusing {len(existing_vids)} existing motion clips ($0 spend)")
            video_clips = existing_vids
        else:
            valid_keyframes = [p for p in image_results if p.is_file() and p.stat().st_size > 1000]
            if not valid_keyframes:
                raise RuntimeError("visual_diffusion_aborted: Zero valid keyframes were produced.")

            motion_tasks = []
            video_clips = []
            from src.scripts.local_perspective_drone import render_perspective_drone_clip

            u_inputs = {}
            u_path = ep_dir / "user_inputs.json"
            if u_path.is_file():
                try:
                    u_inputs = json.loads(u_path.read_text("utf-8"))
                except Exception:
                    pass
            u_weather = str(u_inputs.get("weather", "")).lower()
            u_genre = str(u_inputs.get("genre", "")).lower()
            u_subgenre = str(u_inputs.get("sub_genre", "")).lower()
            u_format = str(u_inputs.get("format", "")).lower()

            local_coros = []
            local_indices = []
            local_weather_info = {}

            for idx, (s, kf) in enumerate(zip(sb.scenes, valid_keyframes), 1):
                out_clip = ep_dir / f"motion_p{idx}.mp4"
                if not force_rerun and out_clip.is_file() and out_clip.stat().st_size > 1000:
                    video_clips.append(out_clip)
                    continue
                is_tour_slide = (
                    getattr(s, "is_itinerary_summary", False)
                    or getattr(s, "is_itinerary_overview", False)
                    or getattr(s, "is_map_transition", False)
                    or getattr(s, "is_vacation_scope", False)
                )
                is_relax = (
                    str(getattr(sb, "genre", "")).lower().startswith("relax")
                    or "relax" in str(getattr(sb, "cluster", "")).lower()
                    or u_genre.startswith("relax")
                    or "relax" in u_format
                )
                is_diffusion_model = (motion_model or "").lower() in (
                    "kling_v3_4k", "kling_v3", "kling_4k", "kling_pro", "kling_1_6", "kling_v1_6_pro",
                    "wan", "wan_2_1", "wan_4k", "hunyuan",
                )
                is_local_requested = (
                    (motion_model or "").lower() in ("locked_tripod", "local_drone", "local_zoompan", "local", "offline", "ken_burns")
                    or (getattr(s, "motion_type", "") in ("ken_burns", "static", "local_drone", "locked_tripod"))
                )
                is_test_mode = (eff_exec == "test")
                use_local = (not is_diffusion_model and not motion_only) and (
                    is_test_mode
                    or is_tour_slide
                    or is_local_requested
                    or (is_relax and (motion_model or "").lower() in ("locked_tripod", "local_drone", "local", "ken_burns", None, ""))
                )

                if use_local:
                    raw_cfg = getattr(s, "model_configs", None) or {}
                    local_cfg = {}
                    if hasattr(raw_cfg, "get"):
                        local_cfg = raw_cfg.get("local_drone") or raw_cfg.get("ken_burns") or {}
                    if hasattr(local_cfg, "model_dump"):
                        local_cfg = local_cfg.model_dump()
                    elif not isinstance(local_cfg, dict):
                        local_cfg = {}

                    target_choreo = local_cfg.get("movement") or getattr(s, "drone_choreography", None) or getattr(s, "camera_movement", None)
                    cam_mov = str(getattr(s, "camera_movement", "") or getattr(s, "camera_rig", "") or motion_model or "").lower()

                    if is_tour_slide:
                        eff_choreo = "stay"
                    elif target_choreo:
                        if any(w in str(target_choreo).lower() for w in ("stay", "hold", "static", "fixed", "cinemagraph")):
                            eff_choreo = "stay"
                        else:
                            eff_choreo = str(target_choreo).lower()
                    elif is_relax or any(w in cam_mov for w in ("locked", "tripod", "static", "fixed", "stay", "hold")):
                        eff_choreo = "stay"
                    else:
                        eff_choreo = "dollyin"

                    w_combo = f"{u_weather} {u_genre} {u_subgenre} {getattr(s, 'weather', '')} {getattr(sb, 'weather', '')} {getattr(sb, 'cluster', '')} {getattr(sb, 'title', '')}".lower()
                    is_rain_scene = (u_weather == "rain") or any(k in w_combo for k in ("rain", "storm", "downpour", "cyclone", "monsoon", "relax/rain"))
                    is_snow_scene = not is_rain_scene and ((u_weather == "snow") or any(k in w_combo for k in ("snow", "blizzard", "winter", "relax/blizzard")))
                    rain_int = "heavy" if (u_weather == "rain" or any(k in w_combo for k in ("heavy", "high", "torrent", "cyclone", "storm", "downpour"))) else "light"
                    snow_int = "heavy" if (u_weather == "snow" or any(k in w_combo for k in ("heavy", "high", "blizzard", "storm"))) else "medium"
                    local_weather_info[idx] = {"rain": is_rain_scene, "snow": is_snow_scene}

                    clip_dur = 5.0 if is_relax else (s.duration_seconds or 5.0)

                    is_water_scene = any(k in f"{getattr(s, 'visual_prompt', '')} {getattr(s, 'location_hub', '')}".lower() for k in ("water", "lake", "ocean", "river", "fjord", "sea", "pond", "waterfall", "stream", "bay", "coast"))
                    if eff_choreo == "stay":
                        # Static locked tripod hold: pure locked stationary frame ($0.00 compute)
                        coro = render_perspective_drone_clip(
                            image_path=kf,
                            output_path=out_clip,
                            duration_seconds=clip_dur,
                            fps=sb.recommended_fps or 24,
                            target_res=(3840, 2160),
                            choreography="stay",
                            start_pan=local_cfg.get("start_pan", "center"),
                            start_zoom=local_cfg.get("start_zoom", "normal"),
                            start_tilt=local_cfg.get("start_tilt", "center"),
                            curve="linear",
                            rain=is_rain_scene,
                            rain_intensity=rain_int,
                            snow=is_snow_scene,
                            snow_intensity=snow_int,
                            lower_third_hud=None,
                            water=is_water_scene,
                        )
                    else:
                        attraction_name = getattr(s, "attraction_name", None) or getattr(s, "origin_name", None) or getattr(s, "location_hub", None) or f"Stop {idx}"
                        start_t = getattr(s, "start_time", "09:00 AM") or "09:00 AM"
                        end_t = getattr(s, "end_time", "11:30 AM") or "11:30 AM"
                        vis_dur = getattr(s, "visit_duration", "2.0 hrs") or "2.0 hrs"
                        day_n = getattr(s, "day_number", 1) or 1
                        cost_t = getattr(s, "attraction_cost", None)
                        trans_dur = getattr(s, "transit_duration", None)
                        dest_n = getattr(s, "destination_name", None)
                        trans_t = f"{trans_dur} to {dest_n}" if (trans_dur and dest_n and dest_n != attraction_name and trans_dur != "concluded") else None

                        hud_data = {
                            "attraction_name": attraction_name,
                            "timing_text": f"🕒 {start_t} – {end_t}  ({vis_dur})",
                            "day_badge": f"DAY {day_n} • STOP {idx}",
                            "cost_text": cost_t,
                            "transit_text": trans_t,
                        } if is_itinerary_tour else None

                        coro = render_perspective_drone_clip(
                            image_path=kf,
                            output_path=out_clip,
                            duration_seconds=clip_dur,
                            fps=sb.recommended_fps or 24,
                            target_res=(3840, 2160),
                            choreography=eff_choreo,
                            start_pan=local_cfg.get("start_pan", "center"),
                            start_zoom=local_cfg.get("start_zoom", "normal"),
                            start_tilt=local_cfg.get("start_tilt", "center"),
                            curve=local_cfg.get("curve", "cosine"),
                            rain=is_rain_scene,
                            rain_intensity=rain_int,
                            snow=is_snow_scene,
                            snow_intensity=snow_int,
                            lower_third_hud=hud_data,
                            water=is_water_scene,
                        )
                    local_coros.append(coro)
                    local_indices.append(idx)
                else:
                    custom_model_cfg = getattr(s, "model_configs", None)
                    if hasattr(custom_model_cfg, "model_dump"):
                        custom_model_cfg = custom_model_cfg.model_dump()
                    elif not isinstance(custom_model_cfg, dict):
                        custom_model_cfg = None
                    chosen_model, m_allow_fallback, m_rationale = resolve_scene_motion_model(
                        scene=s, tier=tier, requested_motion_model=motion_model,
                        scene_index=idx - 1, total_scenes=len(valid_keyframes), genre=getattr(sb, "cluster", "relax/nature"),
                        execution_mode=eff_exec,
                        force_ai_motion=bool(motion_only or force_rerun or is_diffusion_model),
                    )
                    s.recommended_model = chosen_model
                    motion_tasks.append(
                        MotionClipTask(
                            image_path=kf, motion_prompt=s.motion_prompt, visual_prompt=s.visual_prompt,
                            output_path=out_clip, duration_seconds=s.duration_seconds,
                            model=chosen_model, domain=s.domain, req_file=ep_dir / f"fal_motion_req_p{idx}.json",
                            allow_fallback=allow_fallback or m_allow_fallback, force_rerun=force_rerun,
                            negative_prompt=_resolve_scene_negative_prompt(s), model_configs=custom_model_cfg,
                            camera_waypoints=getattr(s, "camera_waypoints", None), kinetic_micro_zones=getattr(s, "kinetic_micro_zones", None),
                            camera_movement=getattr(s, "camera_movement", None), is_relaxation=is_relax,
                        )
                    )

            # Synthesize all local drone and static holding clips in parallel
            rendered_clips_map = {}
            if local_coros:
                logger.info(f"parallel_local_motion_dispatch: Launching {len(local_coros)} local drone clips in parallel")
                local_results = await asyncio.gather(*local_coros)
                for sc_idx, clip_p in zip(local_indices, local_results):
                    rendered_clips_map[sc_idx] = clip_p
                    try:
                        foley_stem = ep_dir / f"nature_foley_p{sc_idx}.wav"
                        from src.services.procedural_foley import synthesize_foley_stem
                        sc_w = local_weather_info.get(sc_idx, {})
                        if sc_w.get("rain"):
                            w_type = "heavy rain and river rapids"
                        elif sc_w.get("snow"):
                            w_type = "blizzard winter wind"
                        elif any(k in u_genre for k in ("ocean", "beach", "coast")):
                            w_type = "ocean rolling waves"
                        elif any(k in u_genre for k in ("hearth", "fire", "cozy")):
                            w_type = "fireplace campfire crackle embers"
                        elif any(k in u_genre for k in ("waterfall", "river", "stream")):
                            w_type = "water stream rapids"
                        else:
                            w_type = "mountain breeze"
                        synthesize_foley_stem(w_type, "nature", "outdoor", 8.0, foley_stem)

                        music_src = None
                        if not no_bgm:
                            if (ep_dir / "velvet_binaural_master_48k.mp3").is_file():
                                music_src = ep_dir / "velvet_binaural_master_48k.mp3"
                            elif (ep_dir / "raw_soundtrack.mp3").is_file():
                                music_src = ep_dir / "raw_soundtrack.mp3"

                        if clip_p.is_file():
                            import imageio_ffmpeg
                            ff_bin = imageio_ffmpeg.get_ffmpeg_exe()

                            # 1. Dedicated Nature-Only Clip (100% Pure Nature ASMR, Zero BGM)
                            nature_clip = clip_p.parent / f"motion_nature_p{sc_idx}.mp4"
                            if foley_stem.is_file():
                                cmd_nat = [
                                    ff_bin, "-y", "-i", str(clip_p), "-i", str(foley_stem),
                                    "-map", "0:v", "-map", "1:a",
                                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                                    "-shortest", str(nature_clip)
                                ]
                                subprocess.run(cmd_nat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                            # 2. Dedicated BGM-Only Clip (100% Music, Zero Nature Foley)
                            if music_src and music_src.is_file():
                                tmp_bgm = clip_p.parent / f"_mux_{clip_p.name}"
                                cmd_bgm = [
                                    ff_bin, "-y", "-i", str(clip_p), "-i", str(music_src),
                                    "-map", "0:v", "-map", "1:a",
                                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                                    "-shortest", str(tmp_bgm)
                                ]
                                mux_res = subprocess.run(cmd_bgm, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                if mux_res.returncode == 0 and tmp_bgm.is_file() and tmp_bgm.stat().st_size > 1000:
                                    tmp_bgm.replace(clip_p)
                            elif foley_stem.is_file() and not nature_clip.is_file():
                                cmd_nat = [
                                    ff_bin, "-y", "-i", str(clip_p), "-i", str(foley_stem),
                                    "-map", "0:v", "-map", "1:a",
                                    "-c:v", "copy", "-c:a", "aac", "-b:a", "256k",
                                    "-shortest", str(clip_p)
                                ]
                                subprocess.run(cmd_nat, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    except Exception as mux_err:
                        logger.warning(f"local_drone_audio_mux_skipped: {mux_err}")

            if motion_tasks:
                diff_clips = await visual_batch_service.render_motion_batch(tasks=motion_tasks)
                for t, c in zip(motion_tasks, diff_clips):
                    # Extract index from motion_p{idx}.mp4
                    try:
                        sc_num = int(t.output_path.stem.split("_p")[-1])
                        rendered_clips_map[sc_num] = c
                    except Exception:
                        pass

            video_clips = [rendered_clips_map.get(idx, ep_dir / f"motion_p{idx}.mp4") for idx in range(1, len(sb.scenes) + 1)]

        if motion_only:
            return {
                "status": "success", "stage": "motion_only", "episode_id": ep_dir.name,
                "keyframes": [str(p) for p in image_results], "raw_videos": [str(c) for c in video_clips],
                "video_clips": [str(c) for c in video_clips], "episode_dir": str(ep_dir),
            }

        # Stage 5: Broadcast Master Assembly Gate
        eff_shot_durs = [float(s.duration_seconds) for s in sb.scenes] if hasattr(sb, "scenes") else None
        target_dur = float(getattr(sb, "total_duration_seconds", None) or (sum(eff_shot_durs) if eff_shot_durs else 60.0))

        from src.services.outro_slide_engine import is_documentary_or_tour, render_4k_outro_slide, render_4k_outro_video
        sb_genre = getattr(sb, "genre", "") or ""
        sb_subgenre = getattr(sb, "sub_genre", "") or ""
        sb_arch = getattr(sb, "primary_archetype", "") or getattr(sb, "cluster", "") or ""
        is_doc = is_documentary_or_tour(sb_genre, sb_subgenre, sb_arch)

        if is_doc:
            outro_img = ep_dir / "outro_slide.jpg"
            outro_clip = ep_dir / "motion_outro.mp4"
            last_kf = image_results[-1] if image_results else None
            is_tour_mode = any(t in f"{sb_genre} {sb_subgenre} {sb_arch}".lower() for t in ("tour", "travel", "itinerary", "walking"))
            tour_stops_data = getattr(sb, "itinerary_summary", None)

            if force_rerun or not outro_img.is_file() or outro_img.stat().st_size < 1000:
                render_4k_outro_slide(
                    output_image_path=outro_img,
                    title=sb.title,
                    channel_name=getattr(sb, "channel_name", "Euro Discovery"),
                    is_tour=is_tour_mode,
                    tour_stops=tour_stops_data,
                    base_keyframe_path=Path(last_kf) if last_kf else None,
                )
            if force_rerun or not outro_clip.is_file() or outro_clip.stat().st_size < 1000:
                render_4k_outro_video(
                    output_video_path=outro_clip,
                    outro_image_path=outro_img,
                    duration_seconds=4.5,
                    fps=sb.recommended_fps or 24,
                )

            if outro_clip.is_file() and str(outro_clip) not in [str(c) for c in video_clips]:
                video_clips.append(outro_clip)
                if eff_shot_durs:
                    eff_shot_durs.append(4.5)

            # Natural documentary narrative ends when scenes conclude: do not loop!
            narrative_dur = sum(eff_shot_durs[:-1]) if (eff_shot_durs and len(eff_shot_durs) > 1) else (sum(eff_shot_durs) if eff_shot_durs else target_dur)
            target_dur = narrative_dur + 4.5

        if generate_short:
            return await handle_short_export(
                sb, ep_dir, video_clips, spatial_audio_path, t_start,
                long_play_hours, fade_to_black_hours, force_rerun,
                narration_audio_path=voice_path,
                target_duration_sec=target_dur,
                shot_durations=eff_shot_durs,
                no_loop=is_doc,
            )
        dual_res = await asyncio.to_thread(
            assemble_dual_masters,
            video_clips=video_clips, audio_path=spatial_audio_path, ep_dir=ep_dir,
            target_fps=sb.recommended_fps, force_rerun=force_rerun,
            narration_audio_path=voice_path, target_duration_sec=target_dur,
            shot_durations=eff_shot_durs,
            no_loop=is_doc,
        )
        metadata_pkgs = export_metadata_packages(sb, ep_dir)

        try:
            await topic_memory.remember_topic(
                topic=sb.title, genre=f"studio_{getattr(sb, 'cluster', 'travel')}",
                tags=metadata_pkgs.get("youtube", {}).get("seo_tags", []),
                story_synopsis=getattr(sb, "story_topic", sb.title) or sb.title, episode_id=ep_dir.name,
            )
        except Exception:
            pass

        return {
            "status": "success",
            "production_type": "broadcast_master",
            "episode_id": ep_dir.name,
            "title": getattr(sb, "title", ep_dir.name),
            "master_video_path": str(dual_res["master_4k"]),
            "master_4k_path": str(dual_res["master_4k"]),
            "master_nature_video_path": str(dual_res.get("nature_master", dual_res["master_4k"])),
            "master_narration_path": str(dual_res.get("narration_master", dual_res["master_4k"])),
            "render_time_seconds": round(time.time() - t_start, 2),
            "keyframes": [str(p) for p in image_results],
            "video_clips": [str(c) for c in video_clips],
            "metadata": metadata_pkgs,
        }


# Universal backwards compatibility aliases
AmbientWorldProducer = TravelStudioProducer = ZenStudioProducer = ArtStudioProducer = BeachLoungeStudioProducer = BlizzardStudioProducer = CozyAmbianceProducer = StudioProducer
DesertStudioProducer = ForestStudioProducer = HealingRelaxationProducer = MountainStudioProducer = NatureRetreatProducer = OceanStudioProducer = RainRetreatProducer = ValleyStudioProducer = StudioProducer

