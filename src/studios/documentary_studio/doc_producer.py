"""Documentary Studio 4K Single-Pass Master Producer with 4-Stage Quality Gate."""
from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional

from src.core.telemetry import logger
from src.services.soundtrack_service import soundtrack_service
from src.services.topic_memory import topic_memory
from src.services.visual_batch_service import MotionClipTask, visual_batch_service
from src.studios.documentary_studio.doc_audio_mixer import generate_documentary_subtitles, mix_documentary_audio
from src.studios.documentary_studio.doc_export_service import assemble_documentary_4k_master, export_documentary_metadata_package
from src.studios.documentary_studio.doc_storyboard import DocStoryboard
from src.studios.documentary_studio.doc_voice_service import doc_voice_service


class DocumentaryProducer:
    """Produces broadcast-grade 4K 24fps documentaries with authoritative narration."""

    def __init__(self, output_base_dir: Optional[Path] = None):
        self.output_base = (output_base_dir or Path("storage/channels/documentary")).resolve()
        self.output_base.mkdir(parents=True, exist_ok=True)

    async def produce(
        self,
        sb: DocStoryboard,
        episode_id: Optional[str] = None,
        motion_model: str = "auto",
        female_voice: bool = False,
        include_bgm: bool = False,
        photos_only: bool = False,
        allow_fallback: bool = False,
        force_local_drone: bool = True,
        force_rerun: bool = False,
    ) -> Dict[str, Any]:
        """Execute 4-Stage Progressive Quality Gate with 100% Artifact Idempotency."""
        t_start = time.time()
        ep_dir = (self.output_base / episode_id) if episode_id else (self.output_base / f"ep_doc_{sb.genre.value}_{int(time.time())}")
        ep_dir.mkdir(parents=True, exist_ok=True)

        # Stage 1: Topic Deduplication & Autonomous Creative Pivot
        if not episode_id:
            is_dup, conflict = await topic_memory.is_duplicate_topic(sb.title, genre=f"doc_{sb.genre.value}")
            if is_dup and conflict:
                logger.warning(f"documentary_duplicate_detected: '{sb.title}' matches {conflict.get('episode_id')}")
                print(f"[DECISION - TOPIC DEDUPLICATION] Topic '{sb.title}' exists in Topic Memory. Auto-pivoting angle...")
                sb.title = f"{sb.title} ~ The Untold Frontier"
            else:
                print(f"[DECISION - TOPIC DEDUPLICATION] Title '{sb.title}' is 100% novel. Proceeding.")

        # Stage 2: Keyframe Image Gate (Concurrent Idempotent Batch)
        from src.services.map_route_engine import render_4k_itinerary_summary_card, render_4k_route_map
        kf_tasks = []
        map_rendered_paths = {}

        tour_stops = []
        for i, s in enumerate(sb.scenes):
            st_type = str(getattr(s, "shot_type", "") or getattr(s, "perspective_type", "") or "").lower()
            loc_hub = str(getattr(s, "location_hub", "") or "").lower()
            is_ov = bool(getattr(s, "is_itinerary_overview", False) or "overview" in st_type or "overview" in loc_hub or "master day" in loc_hub)
            is_sum = bool(getattr(s, "is_itinerary_summary", False) or "summary" in st_type or "summary" in loc_hub)
            is_map = bool(getattr(s, "is_map_transition", False) or "overhead_cartographic" in st_type or "transit" in loc_hub)
            if not getattr(s, "origin_coords", None) or is_ov or is_sum or is_map or getattr(s, "is_vacation_scope", False):
                continue
            nxt_tr = next((nxt for nxt in sb.scenes[i + 1:] if getattr(nxt, "is_map_transition", False)), None)
            tour_stops.append({
                "name": getattr(s, "attraction_name", None) or getattr(s, "origin_name", None) or f"Stop {s.scene_index}",
                "attraction_name": getattr(s, "attraction_name", None) or getattr(s, "origin_name", None),
                "origin_name": getattr(s, "origin_name", None), "coords": s.origin_coords,
                "visit_duration": getattr(s, "visit_duration", None), "attraction_cost": getattr(s, "attraction_cost", None),
                "start_time": getattr(s, "start_time", None), "end_time": getattr(s, "end_time", None),
                "distance_local": getattr(nxt_tr, "distance_local", None) or getattr(s, "distance_local", None),
                "transit_duration": getattr(nxt_tr, "transit_duration", None) or getattr(s, "transit_duration", None),
                "transit_mode": getattr(nxt_tr, "transit_mode", None) or getattr(s, "transit_mode", None),
                "approx_leg_cost": getattr(nxt_tr, "approx_leg_cost", None) or getattr(s, "approx_leg_cost", None),
            })

        for scene in sb.scenes:
            kf_file = ep_dir / f"keyframe_p{scene.scene_index}.jpg"
            if getattr(scene, "is_vacation_scope", False):
                from src.services.map_route_engine import render_4k_leisure_vacation_card
                render_4k_leisure_vacation_card(
                    tour_title=sb.title,
                    output_path=kf_file,
                    force_rerun=force_rerun,
                )
                map_rendered_paths[scene.scene_index] = kf_file
            elif (
                scene.scene_index == 1
                or getattr(scene, "is_itinerary_overview", False)
                or getattr(scene, "is_itinerary_summary", False)
                or getattr(scene, "shot_type", "") in ("itinerary_overview_card", "itinerary_summary_card")
            ) and (sb.itinerary_summary or tour_stops):
                # 4K Hierarchical Timeline Flowchart (stop timings, walk/drive dist/time, and Uber cost)
                from src.services.itinerary_card_engine import render_4k_itinerary_hierarchy_card
                render_4k_itinerary_hierarchy_card(
                    tour_title=sb.title,
                    stops=tour_stops or [s.__dict__ for s in sb.scenes],
                    output_path=kf_file,
                    summary=sb.itinerary_summary[0] if sb.itinerary_summary else None,
                    force_rerun=force_rerun,
                )
                map_rendered_paths[scene.scene_index] = kf_file
            elif getattr(scene, "is_map_transition", False) and scene.origin_coords and scene.destination_coords:
                # 4K Google Maps route: complete circuit, green up to current stop, blue upcoming
                prior_attrs = sum(1 for ps in sb.scenes[:scene.scene_index - 1] if not (getattr(ps, "is_map_transition", False) or getattr(ps, "is_itinerary_overview", False) or getattr(ps, "is_itinerary_summary", False) or getattr(ps, "is_vacation_scope", False)))
                render_4k_route_map(
                    origin_name=scene.origin_name or "Origin",
                    dest_name=scene.destination_name or "Destination",
                    origin_coords=(scene.origin_coords[0], scene.origin_coords[1]),
                    dest_coords=(scene.destination_coords[0], scene.destination_coords[1]),
                    distance_badge=scene.distance_local or "1.5 km",
                    transit_mode=scene.transit_mode or "walk",
                    output_path=kf_file,
                    all_stops=tour_stops or None,
                    tour_title=sb.title,
                    current_stop_index=max(1, prior_attrs),
                    force_rerun=force_rerun,
                )
                map_rendered_paths[scene.scene_index] = kf_file
            else:
                kf_tasks.append((scene.visual_prompt, kf_file, ep_dir / f"fal_req_p{scene.scene_index}.json", scene.scene_index))

        diff_keyframes = await visual_batch_service.render_keyframes_batch(kf_tasks, force_rerun=force_rerun) if kf_tasks else []
        diff_map = {idx: p for (_, p, _, idx) in kf_tasks}
        keyframe_paths = [map_rendered_paths.get(s.scene_index, diff_map.get(s.scene_index, ep_dir / f"keyframe_p{s.scene_index}.jpg")) for s in sb.scenes]

        if photos_only:
            from src.services.notification import notification_service
            await notification_service.notify_keyframes_ready(
                channel_name=f"Documentary Studio ({sb.genre.value.upper()})",
                episode_id=ep_dir.name,
                title=sb.title,
                keyframe_paths=[str(p.resolve()) for p in keyframe_paths],
                pipeline_script="documentary_pipeline.py",
            )
            return {
                "episode_id": ep_dir.name, "title": sb.title, "status": "photos_ready_for_review",
                "keyframes": [str(p) for p in keyframe_paths], "storage_path": str(ep_dir),
            }

        # Stage 3: Timed Narration Voiceover Synthesis
        voice_path = ep_dir / f"voiceover_{'female' if female_voice else 'male'}_{sb.language}.wav"
        scenes_narr = [s.narration_text for s in sb.scenes]
        scenes_dur = [s.duration_seconds for s in sb.scenes]
        
        voice_res = await doc_voice_service.synthesize_full_documentary_voiceover(
            scenes_narration=scenes_narr,
            output_full_wav=voice_path,
            scene_durations=scenes_dur,
            language=sb.language,
            female=female_voice,
        )
        if isinstance(voice_res, tuple):
            voice_path, updated_durs = voice_res
            for sc, d in zip(sb.scenes, updated_durs):
                sc.duration_seconds = float(d)
            scenes_dur = [s.duration_seconds for s in sb.scenes]
            sb.total_duration = sum(scenes_dur)

        # Stage 3B: Optional Subtle BGM Synthesis & Low Ducking (-26dB)
        bgm_path = None
        if include_bgm:
            raw_bgm = ep_dir / "raw_doc_bgm.mp3"
            if not raw_bgm.is_file() or raw_bgm.stat().st_size < 1000:
                await soundtrack_service.synthesize_ambient_soundtrack(sb.title, sb.audio_tags, raw_bgm, sb.total_duration)
            bgm_path = raw_bgm

        mixed_audio = ep_dir / "master_audio_48k.aac"
        mix_documentary_audio(voice_path, bgm_path, mixed_audio, target_lufs=-14.0)

        # Generate timestamped SRT subtitles
        srt_path = ep_dir / "subtitles.srt"
        generate_documentary_subtitles(scenes_narr, scenes_dur, srt_path)

        # Stage 4: 4K Perspective Drone Motion Synthesis (Gemini Directed Choreography)
        from src.scripts.local_perspective_drone import render_perspective_drone_clip

        async def _synthesize_scene_clip(scene, kf_path: Path) -> Path:
            out_clip = ep_dir / f"motion_p{scene.scene_index}.mp4"
            if not force_rerun and out_clip.is_file() and out_clip.stat().st_size > 1000:
                from src.services.ambient_export_service import get_media_duration
                if abs(get_media_duration(out_clip) - float(scene.duration_seconds)) <= 1.0:
                    return out_clip

            # Map transitions, itinerary overviews, summary recaps, and vacation scope cards are static infographics
            is_graphic_card = (
                getattr(scene, "is_map_transition", False)
                or getattr(scene, "is_itinerary_summary", False)
                or getattr(scene, "is_itinerary_overview", False)
                or getattr(scene, "is_vacation_scope", False)
            )

            if is_graphic_card:
                logger.info(f"doc_motion_dispatch: Scene {scene.scene_index} (Map/Card) -> Static Hold Clip ({scene.duration_seconds}s)")
                # Generate smooth broadcast hold clip directly via ffmpeg without drone distortion
                from src.scripts.local_perspective_drone import render_perspective_drone_clip
                return await render_perspective_drone_clip(
                    image_path=kf_path,
                    output_path=out_clip,
                    duration_seconds=scene.duration_seconds,
                    fps=24,
                    target_res=(3840, 2160),
                    choreography="hold",
                    start_pan="center",
                    start_zoom="normal",
                    start_tilt="center",
                    curve="linear",
                    rain=False,
                    snow=False,
                    lower_third_hud=None,
                )

            use_local = force_local_drone or (getattr(scene, "motion_engine", "local_drone") == "local_drone")
            if use_local:
                logger.info(f"doc_motion_dispatch: Scene {scene.scene_index} -> 4K Local Perspective Drone (duration: {scene.duration_seconds}s)")
                raw_cfg = getattr(scene, "model_configs", None) or {}
                local_cfg = raw_cfg.get("local_drone") or raw_cfg.get("ken_burns") or {}
                framing = scene.start_framing or {"pan": local_cfg.get("start_pan", "center"), "zoom": local_cfg.get("start_zoom", "normal"), "tilt": local_cfg.get("start_tilt", "center")}
                attraction_name = getattr(scene, "attraction_name", None) or getattr(scene, "origin_name", None) or getattr(scene, "location_hub", None) or f"Stop {scene.scene_index}"
                start_t = getattr(scene, "start_time", "09:00 AM") or "09:00 AM"
                end_t = getattr(scene, "end_time", "11:30 AM") or "11:30 AM"
                vis_dur = getattr(scene, "visit_duration", "2.0 hrs") or "2.0 hrs"
                day_n = getattr(scene, "day_number", 1) or 1
                cost_t = getattr(scene, "attraction_cost", None)
                trans_dur = getattr(scene, "transit_duration", None)
                dest_n = getattr(scene, "destination_name", None)
                trans_t = f"{trans_dur} to {dest_n}" if (trans_dur and dest_n and dest_n != attraction_name and trans_dur != "concluded") else None

                hud_data = {
                    "attraction_name": attraction_name, "timing_text": f"🕒 {start_t} – {end_t}  ({vis_dur})",
                    "day_badge": f"DAY {day_n} • STOP {scene.scene_index}", "cost_text": cost_t, "transit_text": trans_t,
                }
                choreo = local_cfg.get("movement") or scene.drone_choreography or scene.motion_prompt
                return await render_perspective_drone_clip(
                    image_path=kf_path, output_path=out_clip, duration_seconds=scene.duration_seconds,
                    fps=24, target_res=(3840, 2160), choreography=choreo,
                    start_pan=framing.get("pan", "center"), start_zoom=framing.get("zoom", "normal"), start_tilt=framing.get("tilt", "center"),
                    curve=local_cfg.get("curve") or getattr(scene, "motion_curve", "cosine"),
                    rain=(getattr(scene, "weather", "none") == "rain"), snow=(getattr(scene, "weather", "none") == "snow"),
                    lower_third_hud=hud_data,
                )
            else:
                eff_model = motion_model if motion_model != "auto" else scene.recommended_model
                logger.info(f"doc_motion_dispatch: Scene {scene.scene_index} -> AI Video {eff_model}")
                task = MotionClipTask(
                    image_path=kf_path,
                    motion_prompt=scene.motion_prompt,
                    visual_prompt=scene.visual_prompt,
                    output_path=out_clip,
                    duration_seconds=scene.duration_seconds,
                    model=eff_model,
                    domain=scene.motion_domain,
                    req_file=ep_dir / f"fal_diff_req_p{scene.scene_index}.json",
                    allow_fallback=allow_fallback,
                )
                return await visual_batch_service.render_motion_clip(task)

        # Concurrently synthesize all motion clips across worker threads
        motion_coros = [_synthesize_scene_clip(sc, kp) for sc, kp in zip(sb.scenes, keyframe_paths)]
        video_clip_paths = await asyncio.gather(*motion_coros)

        # Stage 5: Master Assembly & Packaging
        master_path = ep_dir / "master_4k_documentary.mp4"
        assemble_documentary_4k_master(video_clip_paths, mixed_audio, master_path, srt_path)
        yt_pkg = export_documentary_metadata_package(sb, ep_dir)

        # Generate High-CTR Branded 4K YouTube Thumbnails
        try:
            from src.studios.documentary_studio.doc_thumbnail_service import generate_documentary_thumbnail_variants
            thumb_pkg = generate_documentary_thumbnail_variants(sb, ep_dir, keyframe_paths)
            if thumb_pkg:
                yt_pkg["thumbnail_packaging"] = thumb_pkg
                logger.info(f"high_ctr_thumbnails_created: {ep_dir.name}")
        except Exception as ex_t:
            logger.warning(f"failed_to_generate_tour_thumbnails: {ex_t}")

        await topic_memory.remember_topic(topic=sb.title, genre=f"doc_{sb.genre.value}", tags=[sb.genre.value, "documentary", sb.language], story_synopsis=f"4K Documentary on {sb.title} ({len(sb.scenes)} scenes)", episode_id=ep_dir.name)
        render_time = round(time.time() - t_start, 2)
        logger.info(f"documentary_production_ready: {ep_dir.name} in {render_time}s")

        return {
            "episode_id": ep_dir.name, "title": sb.title, "master_video_path": str(master_path),
            "voiceover_path": str(voice_path), "audio_track": str(mixed_audio), "subtitles_path": str(srt_path),
            "keyframes": [str(p) for p in keyframe_paths], "raw_videos": [str(p) for p in video_clip_paths],
            "youtube_package": yt_pkg, "render_time_seconds": render_time, "storage_path": str(ep_dir),
        }
