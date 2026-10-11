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
    return ", ".join([p for p in [base_neg, "camera movement, camera pan, panning, tilt, zoom, camera shake, jitter, rapid motion, flickering, temporal jump, loop seam, morphing, changing environment, clouds, overcast, storm clouds, gelatinous water, artifacts"] if p])


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
            m_target = (image_model or "flux_dev").lower()
            cfgs = getattr(s, "image_model_configs", None) or {}
            keys = ["flux_dev", "flux", "flux_pro", "zimage"] if "dev" in m_target else (["flux_pro", "flux_1_1_pro_ultra", "flux_dev", "zimage"] if "pro" in m_target or "ultra" in m_target else ["zimage", "flux_dev", "flux_pro"])
            for k in keys:
                if k in cfgs and isinstance(cfgs[k], dict) and cfgs[k].get("prompt"):
                    return str(cfgs[k]["prompt"]).strip()
            return s.visual_prompt.strip()

        keyframe_tasks = []
        map_rendered_paths = {}
        from src.services.map_route_engine import render_4k_itinerary_summary_card, render_4k_route_map

        tour_stops = []
        for idx, s in enumerate(sb.scenes):
            if not getattr(s, "origin_coords", None) or getattr(s, "is_map_transition", False) or getattr(s, "is_itinerary_summary", False) or getattr(s, "is_itinerary_overview", False) or getattr(s, "is_vacation_scope", False) or getattr(s, "shot_type", "") in ("itinerary_overview_card", "itinerary_summary_card", "leisure_vacation_scope_card", "overhead_cartographic"):
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

        for idx, s in enumerate(sb.scenes, 1):
            target_kf = ep_dir / f"keyframe_p{idx}.jpg"
            if getattr(s, "is_vacation_scope", False):
                from src.services.map_route_engine import render_4k_leisure_vacation_card
                render_4k_leisure_vacation_card(
                    tour_title=sb.title,
                    output_path=target_kf,
                    force_rerun=force_rerun,
                )
                map_rendered_paths[idx] = target_kf
            elif (
                idx == 1
                or getattr(s, "is_itinerary_summary", False)
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
            elif getattr(s, "is_map_transition", False) and getattr(s, "origin_coords", None) and getattr(s, "destination_coords", None):
                curr_idx = 1 if idx <= 2 else 0
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
                    current_stop_index=curr_idx,
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
                )
                if narr_res.get("narration_path") and Path(narr_res["narration_path"]).is_file():
                    voice_path = Path(narr_res["narration_path"])
                if narr_res.get("shot_durations"):
                    for sc, n_dur in zip(sb.scenes, narr_res["shot_durations"]):
                        sc.duration_seconds = max(float(sc.duration_seconds or 0.0), float(n_dur))
                    tot_d = sum(float(sc.duration_seconds) for sc in sb.scenes)
                    if hasattr(sb, "total_duration"): sb.total_duration = tot_d
                    if hasattr(sb, "total_duration_seconds"): sb.total_duration_seconds = tot_d
                log_pipeline_step("checking audio", "Spoken Narration Voiceover", "completed", "narration synchronized and shot durations locked", {"file": voice_path.name, "total_duration": getattr(sb, "total_duration", None)})
            except Exception as tts_err:
                logger.warning(f"tts_voiceover_failed: {tts_err}")

        # Stage 4: Motion Diffusion Gate (Parallel AI Video Diffusion with In-Flight Token Resumption)
        existing_vids = [ep_dir / f"motion_p{idx}.mp4" for idx in range(1, len(sb.scenes) + 1)]
        all_motion_exist = all(p.is_file() and p.stat().st_size > 1000 for p in existing_vids)

        if (audio_only or master_only) and all_motion_exist and not (force_rerun and motion_only):
            logger.info(f"downstream_stage_reuse_motion: episode='{ep_dir.name}' reusing {len(existing_vids)} existing motion clips ($0 spend)")
            video_clips = existing_vids
        else:
            valid_keyframes = [p for p in image_results if p.is_file() and p.stat().st_size > 1000]
            if not valid_keyframes:
                raise RuntimeError("visual_diffusion_aborted: Zero valid keyframes were produced.")

            motion_tasks = []
            video_clips = []
            from src.scripts.local_perspective_drone import render_perspective_drone_clip

            local_coros = []
            local_indices = []

            for idx, (s, kf) in enumerate(zip(sb.scenes, valid_keyframes), 1):
                out_clip = ep_dir / f"motion_p{idx}.mp4"
                is_tour_slide = (
                    getattr(s, "is_itinerary_summary", False)
                    or getattr(s, "is_itinerary_overview", False)
                    or getattr(s, "is_map_transition", False)
                    or getattr(s, "is_vacation_scope", False)
                )
                use_local = is_tour_slide or (motion_model == "locked_tripod") or (getattr(s, "motion_type", "") in ("ken_burns", "static", "local_drone"))

                if use_local:
                    if is_tour_slide:
                        # Static map/card hold: skip drone camera movement and HUD overlay
                        coro = render_perspective_drone_clip(
                            image_path=kf,
                            output_path=out_clip,
                            duration_seconds=s.duration_seconds,
                            fps=sb.recommended_fps or 24,
                            target_res=(3840, 2160),
                            choreography="hold",
                            start_pan="center",
                            start_zoom="normal",
                            start_tilt="center",
                            curve="linear",
                            lower_third_hud=None,
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
                        }

                        coro = render_perspective_drone_clip(
                            image_path=kf,
                            output_path=out_clip,
                            duration_seconds=s.duration_seconds,
                            fps=sb.recommended_fps or 24,
                            target_res=(3840, 2160),
                            choreography=s.motion_prompt or "slow_pan",
                            start_pan="center",
                            start_zoom="normal",
                            start_tilt="center",
                            curve="cosine",
                            lower_third_hud=hud_data,
                        )
                    local_coros.append(coro)
                    local_indices.append(idx)
                else:
                    custom_model_cfg = getattr(s, "model_configs", None) if isinstance(getattr(s, "model_configs", None), dict) else None
                    chosen_model, m_allow_fallback, m_rationale = resolve_scene_motion_model(
                        scene=s, tier=tier, requested_motion_model=motion_model,
                        scene_index=idx - 1, total_scenes=len(valid_keyframes), genre=getattr(sb, "cluster", "relax/nature"),
                    )
                    motion_tasks.append(
                        MotionClipTask(
                            image_path=kf, motion_prompt=s.motion_prompt, visual_prompt=s.visual_prompt,
                            output_path=out_clip, duration_seconds=s.duration_seconds,
                            model=chosen_model, domain=s.domain, req_file=ep_dir / f"fal_motion_req_p{idx}.json",
                            allow_fallback=allow_fallback or m_allow_fallback, force_rerun=force_rerun,
                            negative_prompt=_resolve_scene_negative_prompt(s), model_configs=custom_model_cfg,
                            camera_waypoints=getattr(s, "camera_waypoints", None), kinetic_micro_zones=getattr(s, "kinetic_micro_zones", None),
                            camera_movement=getattr(s, "camera_movement", None),
                        )
                    )

            # Synthesize all local drone and static holding clips in parallel
            rendered_clips_map = {}
            if local_coros:
                logger.info(f"parallel_local_motion_dispatch: Launching {len(local_coros)} local drone clips in parallel")
                local_results = await asyncio.gather(*local_coros)
                for sc_idx, clip_p in zip(local_indices, local_results):
                    rendered_clips_map[sc_idx] = clip_p

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

        # Stage 5: Acoustic Foley & Brown Noise Mastering Gate
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
                log_pipeline_step("checking audio", "BGM Soundtrack", "started", "soundtrack missing, synthesizing via Suno/DSP", {"file": bgm_path.name})
                bgm_path = await soundtrack_service.synthesize_ambient_soundtrack(
                    title=sb.title, tags=sb.audio_tags or "432Hz ambient soundscape, deep relaxation, -14 LUFS",
                    out_path=bgm_path, total_duration=sb.total_duration, genre=f"{getattr(sb, 'cluster', 'studio')} soundscape", episode_id=ep_dir.name,
                )
                log_pipeline_step("checking audio", "BGM Soundtrack", "completed", "soundtrack synthesized", {"file": bgm_path.name})
            if bgm_path and bgm_path.is_file():
                audio_stems.append(bgm_path)

        if enable_voiceover and (spoken_text or has_narr):
            if not voice_path.is_file() or voice_path.stat().st_size < 1000 or (force_rerun and audio_only):
                log_pipeline_step("checking audio", "Spoken Narration Voiceover", "started", metadata={"file": voice_path.name})
                try:
                    from src.services.shot_narration_service import synthesize_shot_aligned_narration
                    narr_res = await synthesize_shot_aligned_narration(
                        scenes=sb.scenes, ep_dir=ep_dir, fallback_script=spoken_text,
                        total_target_sec=float(sb.total_duration or 60.0), force_rerun=force_rerun and audio_only,
                    )
                    if narr_res.get("narration_path") and Path(narr_res["narration_path"]).is_file():
                        voice_path = Path(narr_res["narration_path"])
                    log_pipeline_step("checking audio", "Spoken Narration Voiceover", "completed", "narration synthesized", {"file": voice_path.name})
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
                "bgm_path": str(spatial_audio_path),
                "narration_path": str(voice_path) if voice_path.is_file() else None,
                "spatial_audio": str(spatial_audio_path),
                "episode_dir": str(ep_dir),
            }

        target_dur = float(getattr(sb, "total_duration_seconds", None) or getattr(sb, "total_duration", None) or 60.0)
        if generate_short:
            return await handle_short_export(
                sb, ep_dir, video_clips, spatial_audio_path, t_start,
                long_play_hours, fade_to_black_hours, force_rerun,
                narration_audio_path=voice_path,
                target_duration_sec=target_dur,
            )
        dual_res = await asyncio.to_thread(
            assemble_dual_masters,
            video_clips=video_clips, audio_path=spatial_audio_path, ep_dir=ep_dir,
            target_fps=sb.recommended_fps, force_rerun=force_rerun,
            narration_audio_path=voice_path, target_duration_sec=target_dur,
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

