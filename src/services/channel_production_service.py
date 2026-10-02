"""Channel Production Service executing real multi-channel pipelines for API and Web Studio."""

import json
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

    # Determine effective channel genre
    eff_genre = genre or (
        "relax/nature" if channel_id in ("earth_serenade", "nature_retreat", "rain_retreat")
        else ("relax/cozy" if channel_id == "cozy_ambiance"
        else ("relax/zen" if channel_id in ("healing_relaxation", "zen_studio")
        else ("comedy/telugu" if channel_id == "telugu_comedy"
        else ("documentary/cineai" if channel_id == "cineai_docs"
        else (channel_id or "relax/nature")))))
    )
    selected_options = {
        "genre": {"value": eff_genre, "label": (selection_labels or {}).get("genre", "")},
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

    saved_inputs: dict[str, Any] = {}
    if user_inputs_file and user_inputs_file.is_file():
        try:
            saved_inputs = json.loads(user_inputs_file.read_text("utf-8"))
            if (num_shots is None or num_shots <= 0) and saved_inputs.get("num_shots"):
                num_shots = int(saved_inputs["num_shots"])
        except Exception:
            pass

    inputs_match = (
        saved_inputs.get("input_schema_version") == 1
        and saved_inputs.get("screenplay_generation_status") == "completed"
        and saved_inputs.get("prompt", "") == (prompt or "")
        and saved_inputs.get("selected_options") == selected_options
        and saved_inputs.get("num_shots") == num_shots
    )
    existing_sp = None
    if not force_rerun and inputs_match and screenplay_file and screenplay_file.is_file() and screenplay_file.stat().st_size > 50:
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
            else:
                existing_sp = RelaxScreenplay(**sp_data)
                if num_shots and len(existing_sp.scenes) != num_shots:
                    logger.info(f"screenplay_cache_shot_count_mismatch: episode='{episode_id}' requested={num_shots} cached={len(existing_sp.scenes)}; regenerating")
                    existing_sp = None
                else:
                    logger.info(f"reusing_existing_screenplay: episode='{episode_id}' title='{existing_sp.title}'")
        except Exception as ex:
            logger.warning(f"screenplay_read_error: {ex}")

    if existing_sp and existing_sp.scenes:
        effective_shots = len(existing_sp.scenes)
    elif num_shots is not None and num_shots > 0:
        effective_shots = num_shots
    else:
        effective_shots = 1

    user_inputs_payload = {
        "input_schema_version": 1,
        "prompt": prompt or "",
        "channel_id": channel_id,
        "genre": eff_genre,
        "sub_genre": sub_genre or "",
        "primary_archetype": primary_archetype or "",
        "selected_options": selected_options,
        "screenplay_generation_status": "pending",
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
    }
    if user_inputs_file:
        try:
            from datetime import datetime, timezone
            user_inputs_payload["created_at"] = datetime.now(timezone.utc).isoformat()
            user_inputs_file.parent.mkdir(parents=True, exist_ok=True)
            user_inputs_file.write_text(json.dumps(user_inputs_payload, indent=2, ensure_ascii=False), encoding="utf-8")
            logger.info(f"user_inputs_saved: {user_inputs_file.name}")
        except Exception as ex:
            logger.warning(f"failed_to_write_user_inputs: {ex}")

    if existing_sp:
        universal_sp = existing_sp
    else:
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
        )

    if episode_id:
        universal_sp.production_id = episode_id
    if screenplay_file:
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
        motion_model=eff_motion,
        image_model=image_model or "flux_dev",
        photos_only=photos_only,
        motion_only=motion_only,
        audio_only=audio_only,
        master_only=master_only,
        no_bgm=no_bgm,
        generate_short=False,
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
    bgm_path = result.get("bgm_path")
    if not bgm_path and manifest_file and (manifest_file.parent / "velvet_binaural_master_48k.mp3").exists():
        bgm_path = str(manifest_file.parent / "velvet_binaural_master_48k.mp3")
    if bgm_path and not photos_only and not motion_only:
        audio_stems.append({
            "name": "432Hz Velvet Binaural BGM",
            "filename": "velvet_binaural_master_48k.mp3",
            "type": "BGM Soundtrack",
            "duration": f"{duration_seconds:.0f}s",
            "url": _to_url(bgm_path),
            "status": "completed",
        })

    master_nature_v = result.get("master_nature_video_path") or result.get("master_nature_video")
    video_url = _to_url(master_v) if master_v else (motion_clips[0]["url"] if motion_clips and not photos_only else None)
    nature_video_url = _to_url(master_nature_v) if master_nature_v else None

    dur_str = f"{int(duration_seconds)}s"
    editions = []
    if video_url and not photos_only and not motion_only and not audio_only and master_v:
        editions.append({
            "edition_id": "master_music",
            "name": f"🎵 Ambient Soundtrack ({dur_str})",
            "label": "4K Ambient Music & 432Hz BGM",
            "icon": "fa-music text-indigo-400",
            "audio_mode": "Music Master",
            "duration": dur_str,
            "format": "4K UHD",
            "status": "completed",
            "url": video_url,
        })
    if nature_video_url and not photos_only and not motion_only and not audio_only and master_v:
        editions.append({
            "edition_id": "master_nature",
            "name": f"🌊 Pure Nature ASMR ({dur_str})",
            "label": "4K Pure Nature Soundscape (No Music)",
            "icon": "fa-water text-cyan-400",
            "audio_mode": "Pure Nature ASMR",
            "duration": dur_str,
            "format": "4K Nature",
            "status": "completed",
            "url": nature_video_url,
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

    # Update operational pipeline state in pipeline_state.json ONLY
    pipeline_state_payload = {
        "episode_id": ep_id,
        "channel_id": channel_id,
        "pipeline_strategy": pipeline_strategy,
        "execution_mode": execution_mode,
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
        "artifacts": result.get("artifacts", []),
    }

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
