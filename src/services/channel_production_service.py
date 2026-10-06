"""Channel Production Service executing real multi-channel pipelines for API and Web Studio."""

import json
import time
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.services.base_channel_pipeline import BaseChannelPipeline, ChannelPipelineConfig
from src.studios.ambient_world.ambient_storyboard import (
    generate_ambient_storyboard,
    generate_ambient_storyboard_gemini,
)
from src.studios.ambient_world.relax_director import (
    RelaxScreenplay,
    generate_relax_screenplay_gemini,
    relax_to_ambient_storyboard,
)
from src.studios.director_dispatcher import dispatch_studio_director

CHANNEL_MAP = {
    "earth_serenade": ChannelPipelineConfig(
        channel_name="Earth Serenade",
        channel_handle="@EarthSerenade4K",
        output_dir=Path("storage/channels/earth_serenade"),
        script_name="nature_sanctuary_pipeline.py",
        default_hours=3.0,
        strategy_description="High-CTR nature relaxation with immersive spatial foley, alpine acoustic depth, and 4K native diffusion.",
    ),
    "silent_hearth": ChannelPipelineConfig(
        channel_name="Silent Hearth",
        channel_handle="@SilentHearthSleep",
        output_dir=Path("storage/channels/silent_hearth"),
        script_name="deep_sleep_sanctuary_pipeline.py",
        default_hours=8.0,
        strategy_description="Hypnotic delta-wave entrainment, cozy hearth warmth, and ultra-fast direct-copy broadcast stretching.",
    ),
    "rain_retreat": ChannelPipelineConfig(
        channel_name="Rain & Quill",
        channel_handle="@RainAndQuill",
        output_dir=Path("storage/channels/rain_and_quill"),
        script_name="study_focus_cafe_pipeline.py",
        default_hours=3.0,
        strategy_description="Binaural rain on windowpanes, lo-fi hearth ambiance, and study-focus soundscapes.",
    ),
    "cineai_docs": ChannelPipelineConfig(
        channel_name="CineAI Docs",
        channel_handle="@CineAIDocumentaries",
        output_dir=Path("storage/channels/cineai_docs"),
        script_name="documentary_pipeline.py",
        default_hours=1.0,
        strategy_description="Blue-chip 24fps BBC-grade wildlife and extreme climate survival documentary mastering.",
    ),
}



async def produce_channel_video(
    channel_id: str,
    prompt: str,
    duration_seconds: float = 5.0,
    episode_id: Optional[str] = None,
    photos_only: bool = False,
    script_only: bool = False,
    motion_only: bool = False,
    audio_only: bool = False,
    master_only: bool = False,
    pipeline_strategy: str = "manual",
    no_bgm: bool = False,
    enable_voiceover: bool = False,
    num_shots: Optional[int] = 1,
    allow_fallback: bool = False,
    user_id: Optional[str] = "user_krishna_01",
    motion_model: str = "auto",
    image_model: str = "flux_1_1_pro_ultra",
    long_play_hours: Optional[float] = None,
    camera_motion: Optional[str] = "locked_tripod",
    execution_mode: str = "test",
    force_rerun: bool = False,
    genre: Optional[str] = None,
    sub_genre: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    selection_labels: Optional[dict[str, str]] = None,
    dual_editions: bool = False,
    tier: Optional[str] = "balanced",
) -> Dict[str, Any]:
    """Execute live channel pipeline script for selected channel inside isolated user channel folder."""
    effective_user = user_id or "user_krishna_01"
    user_chan_dir = storage_service.get_user_container_path(effective_user) / "channels" / channel_id
    user_chan_dir.mkdir(parents=True, exist_ok=True)

    # Dynamic lookup from DB or fallback map
    ch_entity = None
    user_obj = repo.get_user_by_email(effective_user) if "@" in effective_user else None
    if user_obj:
        ch_entity = repo.get_channel(user_obj.id, channel_id)

    if ch_entity:
        cfg = ChannelPipelineConfig(
            channel_name=ch_entity.channel_name,
            channel_handle=ch_entity.channel_handle,
            output_dir=user_chan_dir,
            script_name="nature_sanctuary_pipeline.py",
            default_hours=3.0,
            strategy_description=ch_entity.description or "Automated 4K Diffusion Pipeline",
        )
    elif channel_id in CHANNEL_MAP:
        cfg = replace(CHANNEL_MAP[channel_id], output_dir=user_chan_dir)
    else:
        cfg = ChannelPipelineConfig(
            channel_name=channel_id.replace("_", " ").title(),
            channel_handle=f"@{channel_id}",
            output_dir=user_chan_dir,
            script_name="nature_sanctuary_pipeline.py",
            default_hours=3.0,
            strategy_description="Automated 4K Diffusion Pipeline",
        )

    pipeline = BaseChannelPipeline(cfg)

    # Determine effective channel genre & normalize human names
    raw_g = (genre or "").strip()
    if raw_g.lower() in ("travel guide & doc", "travel", "travel/scenic") or "travel & nature scenic wonders" in raw_g.lower():
        eff_genre = "travel/scenic"
    elif raw_g:
        eff_genre = raw_g
    else:
        eff_genre = (
            "relax/nature" if channel_id in ("earth_serenade", "nature_retreat", "rain_retreat")
            else ("relax/cozy" if channel_id == "cozy_ambiance"
            else ("relax/zen" if channel_id in ("healing_relaxation", "zen_studio")
            else ("comedy/telugu" if channel_id == "telugu_comedy"
            else ("documentary/cineai" if channel_id == "cineai_docs"
            else (channel_id or "relax/nature")))))
        )
    eff_genre_label = (selection_labels or {}).get("genre") or ("✈️ Travel & Nature Scenic Wonders (travel/scenic)" if eff_genre == "travel/scenic" else eff_genre)
    selected_options = {
        "genre": {"value": eff_genre, "label": eff_genre_label},
        "sub_genre": {"value": sub_genre or "", "label": (selection_labels or {}).get("sub_genre", "")},
        "primary_archetype": {
            "value": primary_archetype or "",
            "label": (selection_labels or {}).get("primary_archetype", ""),
        },
    }

    ep_dir = (user_chan_dir / episode_id) if episode_id else None
    screenplay_file = (ep_dir / "screenplay.json") if ep_dir else None
    pipeline_state_file = (ep_dir / "pipeline_state.json") if ep_dir else None
    manifest_file = (ep_dir / "episode_manifest.json") if ep_dir else None
    user_inputs_file = (ep_dir / "user_inputs.json") if ep_dir else None

    saved_pipeline_state: dict[str, Any] = {}
    if pipeline_state_file and pipeline_state_file.is_file():
        try:
            saved_pipeline_state = json.loads(pipeline_state_file.read_text("utf-8"))
        except Exception:
            pass

    saved_inputs: dict[str, Any] = {}
    if user_inputs_file and user_inputs_file.is_file():
        try:
            saved_inputs = json.loads(user_inputs_file.read_text("utf-8"))
            if (num_shots is None or num_shots <= 0) and saved_inputs.get("num_shots"):
                num_shots = int(saved_inputs["num_shots"])
        except Exception:
            pass

    is_downstream_stage = bool(photos_only or motion_only or audio_only or master_only)
    is_resume_flow = not (script_only or force_rerun)

    existing_sp = None
    if screenplay_file and screenplay_file.is_file() and screenplay_file.stat().st_size > 50:
        if is_downstream_stage or is_resume_flow:
            try:
                sp_data = json.loads(screenplay_file.read_text("utf-8"))
                is_legacy_fallback = (
                    str(sp_data.get("title", "")).startswith("8K Living Wallpaper:")
                    and str(sp_data.get("story_topic", "")).startswith(
                        "Ultra-tranquil living wallpaper soundscape capturing "
                    )
                )
                if is_legacy_fallback:
                    logger.warning(f"ignoring_legacy_fallback_screenplay: episode='{episode_id}'")
                elif sp_data.get("scenes"):
                    existing_sp = RelaxScreenplay(**sp_data)
                    logger.info(f"reusing_existing_screenplay: episode='{episode_id}' title='{existing_sp.title}' scenes={len(existing_sp.scenes)}")
            except Exception as ex:
                logger.warning(f"screenplay_read_error: {ex}")

    eff_tier = (getattr(existing_sp, "tier", None) or saved_inputs.get("tier") or tier or "balanced") if (is_downstream_stage or existing_sp) else (tier or saved_inputs.get("tier", "balanced"))
    eff_voiceover = enable_voiceover or bool(saved_inputs.get("enable_voiceover", False))
    eff_no_bgm = no_bgm if not is_downstream_stage else bool(saved_inputs.get("no_bgm", no_bgm))

    if existing_sp and existing_sp.scenes:
        effective_shots = len(existing_sp.scenes)
        if getattr(existing_sp, "total_duration_seconds", None):
            duration_seconds = float(existing_sp.total_duration_seconds)
    elif num_shots is not None and num_shots > 0:
        effective_shots = num_shots
    else:
        effective_shots = 1

    eff_genre_final = (getattr(existing_sp, "genre", None) if existing_sp else None) or eff_genre
    sub_genre_final = (getattr(existing_sp, "sub_genre", None) if existing_sp else None) or (sub_genre or "")
    primary_archetype_final = (getattr(existing_sp, "primary_archetype", None) if existing_sp else None) or (primary_archetype or "")
    prompt_final = (getattr(existing_sp, "story_topic", None) or prompt or saved_inputs.get("prompt", "")) if existing_sp else (prompt or "")

    user_inputs_payload = {
        "input_schema_version": 1,
        "prompt": prompt_final,
        "channel_id": channel_id,
        "genre": eff_genre_final,
        "sub_genre": sub_genre_final,
        "primary_archetype": primary_archetype_final,
        "selected_options": selected_options if not is_downstream_stage else saved_inputs.get("selected_options", selected_options),
        "screenplay_generation_status": "completed" if existing_sp else "pending",
        "episode_id": episode_id or "EP-001",
        "user_id": effective_user,
        "duration_seconds": duration_seconds,
        "long_play_hours": long_play_hours,
        "num_shots": effective_shots,
        "image_model": image_model,
        "motion_model": motion_model,
        "camera_motion": camera_motion,
        "pipeline_strategy": pipeline_strategy,
        "allow_fallback": allow_fallback,
        "dual_editions": dual_editions,
        "enable_bgm": not eff_no_bgm,
        "enable_voiceover": eff_voiceover,
        "no_bgm": eff_no_bgm,
        "tier": eff_tier,
    }
    if user_inputs_file:
        try:
            from datetime import datetime, timezone
            user_inputs_payload["created_at"] = saved_inputs.get("created_at") or datetime.now(timezone.utc).isoformat()
            user_inputs_file.parent.mkdir(parents=True, exist_ok=True)
            user_inputs_file.write_text(json.dumps(user_inputs_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"user_inputs_saved: {user_inputs_file.name}")
        except Exception as ex:
            logger.warning(f"failed_to_write_user_inputs: {ex}")

    t_stage1 = time.time()
    logger.info(f"stage_triggered: stage='Stage 1: Screenplay' episode_id='{episode_id}' timestamp={t_stage1}")
    if existing_sp:
        universal_sp = existing_sp
        dur_stage1 = time.time() - t_stage1
        logger.info(f"stage_reused: stage='Stage 1: Screenplay' episode_id='{episode_id}' title='{universal_sp.title}' duration={dur_stage1:.2f}s reason='cache_hit' timestamp={time.time()}")
        print(f"[STAGE 1 CACHE REUSED] Screenplay reused for {episode_id} in {dur_stage1:.2f}s ($0.00 spend).")
    elif is_downstream_stage and screenplay_file and screenplay_file.is_file() and screenplay_file.stat().st_size > 50:
        universal_sp = RelaxScreenplay(**json.loads(screenplay_file.read_text("utf-8")))
        logger.info(f"downstream_stage_screenplay_fallback_preserved: episode_id='{episode_id}' title='{universal_sp.title}'")
    else:
        print(f"\n[STAGE 1 TRIGGERED] Formulating Screenplay for {episode_id}...")
        try:
            universal_sp = await dispatch_studio_director(
                genre=eff_genre,
                sub_genre=sub_genre,
                primary_archetype=primary_archetype,
                channel_id=channel_id,
                custom_prompt=prompt,
                duration_seconds=duration_seconds or 60.0,
                num_shots=effective_shots,
                camera_motion=camera_motion or "locked_tripod",
                user_id=effective_user,
                raw_output_path=(ep_dir / "raw_gemini_screenplay.json") if ep_dir else None,
                image_model=image_model,
                tier=eff_tier,
            )
            dur_stage1 = time.time() - t_stage1
            if ep_dir:
                raw_target = ep_dir / "raw_gemini_screenplay.json"
                if not raw_target.exists():
                    try:
                        raw_target.parent.mkdir(parents=True, exist_ok=True)
                        raw_target.write_text(json.dumps(universal_sp.model_dump(), indent=2), encoding="utf-8")
                        logger.info(f"raw_gemini_screenplay_guaranteed: {raw_target}")
                    except Exception as raw_g_err:
                        logger.warning(f"failed_to_guarantee_raw_gemini_screenplay: {raw_g_err}")
            logger.info(f"stage_completed: stage='Stage 1: Screenplay' episode_id='{episode_id}' duration={dur_stage1:.2f}s scenes={len(universal_sp.scenes)} timestamp={time.time()}")
            print(f"[STAGE 1 COMPLETED] Screenplay ready in {dur_stage1:.2f}s ({len(universal_sp.scenes)} scenes).")
        except Exception as ex:
            dur_stage1 = time.time() - t_stage1
            logger.error(f"stage_failed: stage='Stage 1: Screenplay' episode_id='{episode_id}' duration={dur_stage1:.2f}s error='{ex}' timestamp={time.time()}")
            raise

    if episode_id:
        universal_sp.production_id = episode_id
    if screenplay_file and not existing_sp:
        try:
            screenplay_file.parent.mkdir(parents=True, exist_ok=True)
            screenplay_file.write_text(json.dumps(universal_sp.model_dump(), indent=2), encoding="utf-8")
        except Exception as ex:
            logger.warning(f"failed_to_write_screenplay_file: {ex}")

    generated_sub_genre = getattr(universal_sp, "sub_genre", None) or eff_genre
    sb = relax_to_ambient_storyboard(universal_sp)

    generated_primary_archetype = getattr(universal_sp, "primary_archetype", None) or generated_sub_genre
    secondary_archetype = getattr(universal_sp, "secondary_archetype", None)
    cluster_val = getattr(universal_sp, "cluster", None) or sb.cluster

    if user_inputs_file:
        try:
            user_inputs_payload["screenplay_generation_status"] = "completed"
            user_inputs_payload["generated_output"] = {
                "title": universal_sp.title,
                "story_topic": universal_sp.story_topic,
                "genre": universal_sp.genre,
                "sub_genre": universal_sp.sub_genre,
                "primary_archetype": universal_sp.primary_archetype,
                "secondary_archetype": universal_sp.secondary_archetype,
                "cluster": universal_sp.cluster,
            }
            user_inputs_file.write_text(json.dumps(user_inputs_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"user_inputs_output_saved: {user_inputs_file.name}")
        except Exception as ex:
            logger.warning(f"failed_to_update_user_inputs_output: {ex}")

    # Pure operational pipeline state (Separated from creative script)
    pipeline_state_payload = {
        "episode_id": episode_id or "EP-001",
        "channel_id": channel_id,
        "pipeline_strategy": pipeline_strategy,
        "execution_mode": execution_mode,
        "tier": eff_tier,
        "current_stage": 1 if script_only else 5,
        "stage_status": "ready" if script_only else "completed",
        "stage_approvals": {"script": True, "keyframes": not script_only, "motion": not script_only, "audio": not script_only, "master": not script_only},
        "stages_completed": {"script": True, "keyframes": not script_only, "motion": not script_only, "audio": not script_only, "master": not script_only},
        "artifacts": [],
    }

    if pipeline_state_file:
        try:
            pipeline_state_file.parent.mkdir(parents=True, exist_ok=True)
            pipeline_state_file.write_text(json.dumps(pipeline_state_payload, indent=2), encoding="utf-8")
        except Exception as ex:
            logger.warning(f"failed_to_write_pipeline_state: {ex}")

    manifest_payload = {
        "episode_id": episode_id,
        "title": universal_sp.title,
        "tier": eff_tier,
        "prompt": prompt,
        "genre": eff_genre,
        "primary_archetype": generated_primary_archetype,
        "secondary_archetype": secondary_archetype,
        "cluster": cluster_val,
        "story_topic": universal_sp.story_topic,
        "duration_seconds": duration_seconds,
        "num_shots": effective_shots,
        "recommended_fps": universal_sp.recommended_fps,
        "camera_motion": camera_motion or "locked_tripod",
        "audio_tags": universal_sp.audio_master.suno_musical_tags if universal_sp.audio_master else sb.audio_tags,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    if manifest_file:
        try:
            manifest_file.parent.mkdir(parents=True, exist_ok=True)
            manifest_file.write_text(json.dumps(manifest_payload, indent=2), encoding="utf-8")
        except Exception as ex:
            logger.warning(f"failed_to_write_manifest: {ex}")

    if script_only:
        return {
            "success": True,
            "job_id": f"job_{episode_id.lower() if episode_id else 'ep001'}",
            "episode_id": episode_id or "EP-001",
            "title": universal_sp.title,
            "channel_id": channel_id,
            "script": universal_sp.model_dump(),
            "pipeline_state": pipeline_state_payload,
            "current_stage": 1,
            "stage": 1,
            "video_url": None,
            "nature_video_url": None,
            "editions": [],
            "long_play_hours": long_play_hours,
            "storage_path": str(user_chan_dir / (episode_id or "EP-001")),
            "file_size_bytes": 0,
            "duration_seconds": duration_seconds,
            "render_time_seconds": 0.5,
            "keyframes": [],
            "motion_clips": [],
            "audio_stems": [],
            "artifacts": [],
        }

    eff_motion = motion_model
    if not eff_motion or eff_motion == "auto":
        eff_motion = "wan" if duration_seconds <= 10.0 else "auto"

    result = await pipeline.execute(
        sb=sb,
        episode_id=episode_id,
        tier=eff_tier,
        motion_model=eff_motion,
        image_model=image_model or "flux_dev",
        photos_only=photos_only,
        motion_only=motion_only,
        audio_only=audio_only,
        master_only=master_only,
        no_bgm=eff_no_bgm,
        enable_voiceover=eff_voiceover,
        generate_short=True,
        allow_fallback=allow_fallback,
        long_play_hours=long_play_hours,
        force_rerun=force_rerun,
    )

    ep_id = result.get("episode_id") or episode_id or "EP-001"
    raw_kfs = result.get("keyframes", [])
    raw_vids = result.get("raw_videos", [])
    master_v = result.get("master_video_path") or result.get("master_video")

    def _to_url(p: Any) -> str:
        if not p:
            return ""
        p_str = str(p).replace("\\", "/")
        if "/storage/" in p_str:
            return "/storage/" + p_str.split("/storage/", 1)[1]
        if p_str.startswith("storage/"):
            return "/" + p_str
        try:
            root = getattr(storage_service, "root_dir", Path("storage")).resolve()
            rel = Path(p).resolve().relative_to(root).as_posix()
            return f"/storage/{rel}"
        except Exception:
            return f"/storage/{p_str.lstrip('/')}"

    keyframes = []
    for idx, kf_path in enumerate(raw_kfs, 1):
        url = _to_url(kf_path)
        scene_label = universal_sp.scenes[idx - 1].location_hub if (idx - 1 < len(universal_sp.scenes) and getattr(universal_sp.scenes[idx - 1], "location_hub", None)) else universal_sp.title
        keyframes.append({"name": f"Shot {idx}: {scene_label}", "url": url, "timing": f"{duration_seconds / max(1, len(raw_kfs)):.1f}s"})

    motion_clips = []
    m_label = "Wan 2.1" if eff_motion in ("wan", "wan_2_1", "wan21") else "Kling v3 4K Native"
    for idx, mv_path in enumerate(raw_vids, 1):
        url = _to_url(mv_path)
        scene_label = universal_sp.scenes[idx - 1].location_hub if (idx - 1 < len(universal_sp.scenes) and getattr(universal_sp.scenes[idx - 1], "location_hub", None)) else universal_sp.title
        motion_clips.append({"name": f"Motion {idx}: {scene_label}", "model": m_label, "duration": f"{duration_seconds:.0f}s", "url": url})

    audio_stems = []
    if manifest_file and (manifest_file.parent / "raw_soundtrack.mp3").exists() and (manifest_file.parent / "raw_soundtrack.mp3").stat().st_size > 1000:
        raw_suno_f = manifest_file.parent / "raw_soundtrack.mp3"
        audio_stems.append({
            "name": "Suno Soundtrack",
            "filename": "raw_soundtrack.mp3",
            "type": "suno_bgm",
            "duration": f"{duration_seconds:.0f}s",
            "url": _to_url(str(raw_suno_f)),
            "status": "completed",
            "color": "cyan",
        })
    bgm_path = result.get("bgm_path")
    if not bgm_path and manifest_file and (manifest_file.parent / "velvet_binaural_master_48k.mp3").exists():
        bgm_path = str(manifest_file.parent / "velvet_binaural_master_48k.mp3")
    if bgm_path and not photos_only and not motion_only and Path(bgm_path).exists() and Path(bgm_path).stat().st_size > 1000:
        audio_stems.append({
            "name": "432Hz Velvet Binaural BGM",
            "filename": "velvet_binaural_master_48k.mp3",
            "type": "BGM Soundtrack",
            "duration": f"{duration_seconds:.0f}s",
            "url": _to_url(bgm_path),
            "status": "completed",
            "color": "emerald",
        })

    if manifest_file and (manifest_file.parent / "spoken_narration.mp3").exists() and (manifest_file.parent / "spoken_narration.mp3").stat().st_size > 1000:
        raw_narr_f = manifest_file.parent / "spoken_narration.mp3"
        audio_stems.append({
            "name": "TTS Spoken Narration",
            "filename": "spoken_narration.mp3",
            "type": "Spoken Narration",
            "duration": f"{duration_seconds:.0f}s",
            "url": _to_url(str(raw_narr_f)),
            "status": "completed",
            "color": "amber",
        })

    master_nature_v = result.get("master_nature_video_path") or result.get("master_nature_video")
    if not master_nature_v and manifest_file and (manifest_file.parent / "master_4k_narration.mp4").is_file():
        master_nature_v = str(manifest_file.parent / "master_4k_narration.mp4")
    video_url = _to_url(master_v) if master_v else (motion_clips[0]["url"] if motion_clips and not photos_only else None)
    nature_video_url = _to_url(master_nature_v) if master_nature_v else video_url

    dur_str = f"{int(duration_seconds)}s"
    editions = []
    if video_url and not photos_only and not motion_only and not audio_only and master_v:
        if dual_editions:
            editions.append({
                "edition_id": "master_music",
                "name": f"🎵 Music Soundtrack Edition ({dur_str})",
                "label": "4K Ambient Music & BGM (No Narration)",
                "icon": "fa-music text-indigo-400",
                "audio_mode": "Music Master",
                "duration": dur_str,
                "format": "4K UHD",
                "status": "completed",
                "url": video_url,
            })
            editions.append({
                "edition_id": "master_narration",
                "name": f"🎙️ Narration Only Edition ({dur_str})",
                "label": "4K Documentary Narration (Without Music)",
                "icon": "fa-microphone text-amber-400",
                "audio_mode": "Narration Master",
                "duration": dur_str,
                "format": "4K Narration",
                "status": "completed",
                "url": nature_video_url,
            })
        else:
            editions.append({
                "edition_id": "master_broadcast",
                "name": f"🎬 4K Broadcast Master ({dur_str})",
                "label": "4K Broadcast Master",
                "icon": "fa-film text-indigo-400",
                "audio_mode": "Broadcast Master",
                "duration": dur_str,
                "format": "4K UHD",
                "status": "completed",
                "url": video_url,
            })

    if script_only:
        current_stage = 1
    elif photos_only:
        current_stage = 2
    elif motion_only:
        current_stage = 3
    elif audio_only:
        current_stage = 4
    elif master_v:
        current_stage = 5
    else:
        current_stage = 3

    if not keyframes and saved_pipeline_state.get("keyframes"):
        keyframes = saved_pipeline_state["keyframes"]
    if not motion_clips and saved_pipeline_state.get("motion_clips"):
        motion_clips = saved_pipeline_state["motion_clips"]
    if not audio_stems and saved_pipeline_state.get("audio_stems"):
        audio_stems = saved_pipeline_state["audio_stems"]

    # Enrich motion clips with remote URLs from .fal_meta.json or existing pipeline state
    if ep_dir:
        for m in motion_clips:
            if not m.get("remote_url"):
                fn = m.get("filename") or Path(m.get("url", "")).name.split("?")[0]
                for cand in (ep_dir / f"{fn}.fal_meta.json", ep_dir / f"raw_diff_{fn}.fal_meta.json"):
                    if cand.is_file():
                        try:
                            meta_d = json.loads(cand.read_text("utf-8"))
                            if meta_d.get("video_url"):
                                m["remote_url"] = meta_d["video_url"]
                                break
                        except Exception:
                            pass

    # Update operational pipeline state in pipeline_state.json ONLY
    pipeline_state_payload = {
        "episode_id": ep_id,
        "channel_id": channel_id,
        "pipeline_strategy": pipeline_strategy,
        "execution_mode": execution_mode,
        "tier": eff_tier,
        "current_stage": current_stage,
        "stage_status": "ready" if current_stage < 5 else "completed",
        "stage_approvals": {
            "script": True,
            "keyframes": current_stage >= 2 and len(keyframes) > 0,
            "motion": current_stage >= 3 and len(motion_clips) > 0,
            "audio": current_stage >= 4 and len(audio_stems) > 0,
            "master": current_stage >= 5 and bool(master_v),
        },
        "stages_completed": {
            "script": True,
            "keyframes": current_stage >= 2 and len(keyframes) > 0,
            "motion": current_stage >= 3 and len(motion_clips) > 0,
            "audio": current_stage >= 4 and len(audio_stems) > 0,
            "master": current_stage >= 5 and bool(master_v),
        },
        "keyframes": keyframes,
        "motion_clips": motion_clips,
        "audio_stems": audio_stems,
        "master_video": {
            "url": video_url,
            "nature_url": nature_video_url,
            "path": str(master_v) if master_v else None,
        },
        "artifacts": result.get("artifacts", []),
    }

    # Build canonical artifact registry with model, owner, status, and local/remote locations
    registry_map: dict[str, Any] = saved_pipeline_state.get("artifact_registry", {})
    if screenplay_file and screenplay_file.is_file():
        registry_map[f"{ep_id}_screenplay"] = {
            "artifact_id": f"{ep_id}_screenplay",
            "category": "screenplay",
            "model": "gemini-2.5-pro",
            "owner": effective_user,
            "status": "synthesized",
            "local_path": screenplay_file.name,
            "local_url": _to_url(screenplay_file),
            "file_size_bytes": screenplay_file.stat().st_size,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"title": universal_sp.title, "tier": eff_tier},
        }

    for idx, kf in enumerate(keyframes, 1):
        fn = kf.get("filename") or f"keyframe_p{idx}.jpg"
        fp = ep_dir / fn if ep_dir else None
        sz = fp.stat().st_size if fp and fp.is_file() else 0
        registry_map[f"{ep_id}_keyframe_p{idx}"] = {
            "artifact_id": f"{ep_id}_keyframe_p{idx}",
            "category": "image",
            "scene_index": idx,
            "model": image_model or "flux_dev",
            "owner": effective_user,
            "status": "synthesized" if sz > 1000 else "pending",
            "local_path": fn,
            "local_url": kf.get("url"),
            "file_size_bytes": sz,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"scene_label": kf.get("name", "")},
        }

    for idx, mc in enumerate(motion_clips, 1):
        fn = mc.get("filename") or f"motion_p{idx}.mp4"
        fp = ep_dir / fn if ep_dir else None
        sz = fp.stat().st_size if fp and fp.is_file() else 0
        s_scene = universal_sp.scenes[idx - 1] if (idx - 1 < len(universal_sp.scenes)) else None
        m_type = getattr(s_scene, "motion_type", "ai_diffusion") if s_scene else "ai_diffusion"
        m_model = "local_zoompan" if m_type == "ken_burns" else (mc.get("model") or eff_motion)
        registry_map[f"{ep_id}_motion_p{idx}"] = {
            "artifact_id": f"{ep_id}_motion_p{idx}",
            "category": "video",
            "scene_index": idx,
            "model": m_model,
            "owner": effective_user,
            "status": "synthesized" if sz > 1000 else ("cached" if mc.get("remote_url") else "pending"),
            "local_path": fn,
            "local_url": mc.get("url"),
            "remote_url": mc.get("remote_url"),
            "file_size_bytes": sz,
            "duration_seconds": duration_seconds / max(1, len(motion_clips)),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"motion_type": m_type, "scene_label": mc.get("name", "")},
        }

    for s in audio_stems:
        fn = s.get("filename") or "raw_soundtrack.mp3"
        fp = ep_dir / fn if ep_dir else None
        sz = fp.stat().st_size if fp and fp.is_file() else 0
        s_type = s.get("type", "bgm")
        s_model = "azure_speech" if "voice" in s_type else "suno_v3_5"
        registry_map[f"{ep_id}_{s_type}"] = {
            "artifact_id": f"{ep_id}_{s_type}",
            "category": "audio",
            "model": s_model,
            "owner": effective_user,
            "status": "synthesized" if sz > 1000 else "pending",
            "local_path": fn,
            "local_url": s.get("url"),
            "file_size_bytes": sz,
            "duration_seconds": duration_seconds,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"audio_name": s.get("name", "")},
        }

    if master_v and Path(master_v).is_file():
        mv_path = Path(master_v)
        registry_map[f"{ep_id}_master_4k"] = {
            "artifact_id": f"{ep_id}_master_4k",
            "category": "master",
            "model": "single_pass_ffmpeg",
            "owner": effective_user,
            "status": "synthesized",
            "local_path": mv_path.name,
            "local_url": video_url,
            "file_size_bytes": mv_path.stat().st_size,
            "duration_seconds": duration_seconds,
            "resolution": "3840x2160",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {"editions": len(editions)},
        }

    pipeline_state_payload["artifact_registry"] = registry_map

    if pipeline_state_file:
        try:
            pipeline_state_file.parent.mkdir(parents=True, exist_ok=True)
            pipeline_state_file.write_text(json.dumps(pipeline_state_payload, indent=2), encoding="utf-8")
        except Exception as ex:
            logger.warning(f"failed_to_write_pipeline_state: {ex}")

    return {
        "success": True,
        "job_id": f"job_{ep_id.lower()}",
        "episode_id": ep_id,
        "title": universal_sp.title,
        "channel_id": channel_id,
        "script": universal_sp.model_dump(),
        "pipeline_state": pipeline_state_payload,
        "current_stage": current_stage,
        "stage": current_stage,
        "video_url": video_url if not photos_only and not motion_only and not audio_only else None,
        "nature_video_url": nature_video_url if not photos_only and not motion_only and not audio_only else None,
        "editions": editions if not photos_only and not motion_only and not audio_only else [],
        "long_play_hours": long_play_hours,
        "storage_path": str(master_v) if master_v else str(cfg.output_dir / ep_id),
        "file_size_bytes": Path(master_v).stat().st_size if master_v and Path(master_v).exists() else 1048576,
        "duration_seconds": duration_seconds,
        "render_time_seconds": 1.5,
        "keyframes": keyframes,
        "motion_clips": motion_clips if not photos_only else [],
        "audio_stems": audio_stems if not photos_only and not motion_only else [],
        "artifacts": result.get("artifacts", []),
    }
