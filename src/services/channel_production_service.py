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
    generate_relax_screenplay_gemini,
    relax_to_ambient_storyboard,
)

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


def _resolve_archetypes(channel_id: str, prompt: str) -> tuple[str, Optional[str]]:
    """Determine primary and secondary archetype based on channel and user prompt keywords."""
    p = (prompt or "").lower()
    
    # Priority 1: Geographic / Sanctuary Location
    geo_mapping = [
        ("swiss_alps", ["swiss", "alps", "alpine", "lauterbrunnen", "meadow", "edelweiss", "matterhorn", "chalet", "village"]),
        ("himalayas", ["himalaya", "monastery", "tibet", "prayer flag", "sherpa"]),
        ("zen_garden", ["zen", "kyoto", "lotus", "bamboo fountain", "gravel", "temple garden", "rock garden", "serenity"]),
        ("ocean_world", ["ocean", "waves", "coastal", "coral", "sea", "reef", "lagoon", "tide", "aquatic", "marine", "beach"]),
        ("biophilic_living", ["biophilic", "terrace", "pavilion", "patio", "deck", "retreat", "indoor garden"]),
        ("lake", ["lake", "placid", "dock", "mirror lake", "reflection pool", "fjord"]),
        ("forest", ["forest", "rainforest", "woods", "canopy", "moss", "trees", "pine", "jungle", "emerald"]),
        ("mountains", ["mountain", "misty mountain", "peak", "ridge", "highlands"]),
    ]

    weather_has_rain = any(k in p for k in ("rain", "raining", "rainfall", "downpour", "storm", "puddle", "drizzle"))
    weather_has_snow = any(k in p for k in ("blizzard", "snow", "snowstorm", "frost", "winter", "sub-zero", "arctic", "ice"))
    weather_has_fire = any(k in p for k in ("campfire", "fire", "hearth", "fireplace", "ember", "flame", "cabin fire"))

    for arch_key, kws in geo_mapping:
        if any(kw in p for kw in kws):
            sec = "rain" if weather_has_rain else ("blizzard" if weather_has_snow else ("camp_fire" if weather_has_fire else None))
            return arch_key, sec

    # Priority 2: Pure Atmospheric Fallback
    if weather_has_rain:
        return "rain", None
    if weather_has_snow:
        return "blizzard", "camp_fire"
    if weather_has_fire:
        return "camp_fire", None

    if channel_id == "silent_hearth":
        return "blizzard", "camp_fire"
    elif channel_id in ("rain_retreat", "study_focus_cafe"):
        return "rain", None
    elif channel_id == "cineai_docs":
        return "mountains", None
    return "swiss_alps", None


async def produce_channel_video(
    channel_id: str,
    prompt: str,
    duration_seconds: float = 10.0,
    episode_id: Optional[str] = None,
    photos_only: bool = False,
    script_only: bool = False,
    motion_only: bool = False,
    audio_only: bool = False,
    master_only: bool = False,
    pipeline_strategy: str = "manual",
    no_bgm: bool = False,
    num_shots: int = 4,
    allow_fallback: bool = False,
    user_id: Optional[str] = "user_krishna_01",
    motion_model: str = "auto",
    long_play_hours: Optional[float] = None,
    camera_motion: Optional[str] = "locked_tripod",
    execution_mode: str = "test",
    force_rerun: bool = False,
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
    primary, secondary = _resolve_archetypes(channel_id, prompt)

    ep_dir = (user_chan_dir / episode_id) if episode_id else None
    screenplay_file = (ep_dir / "screenplay.json") if ep_dir else None
    pipeline_state_file = (ep_dir / "pipeline_state.json") if ep_dir else None
    manifest_file = (ep_dir / "episode_manifest.json") if ep_dir else None

    existing_sp = None
    if not force_rerun and screenplay_file and screenplay_file.is_file() and screenplay_file.stat().st_size > 50:
        try:
            sp_data = json.loads(screenplay_file.read_text("utf-8"))
            existing_sp = UniversalScreenplay(**sp_data)
            logger.info(f"reusing_existing_screenplay: episode='{episode_id}' title='{existing_sp.title}'")
        except Exception as ex:
            logger.warning(f"screenplay_read_error: {ex}")

    effective_shots = num_shots if num_shots and num_shots > 0 else (1 if duration_seconds <= 5.0 else (2 if duration_seconds <= 10.0 else 4))

    if existing_sp:
        universal_sp = existing_sp
    else:
        universal_sp = await generate_relax_screenplay_gemini(
            primary=primary,
            custom_prompt=prompt,
            duration_seconds=duration_seconds or 60.0,
            num_shots=effective_shots,
            camera_motion=camera_motion or "locked_tripod",
            genre=channel_id or "relax/nature",
            user_id=effective_user,
            channel_id=channel_id,
        )
        if screenplay_file:
            try:
                screenplay_file.parent.mkdir(parents=True, exist_ok=True)
                screenplay_file.write_text(json.dumps(universal_sp.model_dump(), indent=2), encoding="utf-8")
            except Exception as ex:
                logger.warning(f"failed_to_write_screenplay_file: {ex}")

    user_inputs_file = (ep_dir / "user_inputs.json") if ep_dir else None
    if user_inputs_file:
        try:
            from datetime import datetime, timezone
            eff_genre = (
                "relax/nature" if channel_id in ("earth_serenade", "nature_retreat", "rain_retreat")
                else ("relax/cozy" if channel_id == "cozy_ambiance"
                else ("relax/healing" if channel_id == "healing_relaxation"
                else ("comedy/telugu" if channel_id == "telugu_comedy"
                else ("documentary/cineai" if channel_id == "cineai_docs"
                else (channel_id or "general")))))
            )
            user_inputs_payload = {
                "prompt": prompt,
                "channel_id": channel_id,
                "genre": eff_genre,
                "primary_archetype": primary,
                "secondary_archetype": secondary,
                "episode_id": episode_id or "EP-001",
                "user_id": effective_user,
                "duration_seconds": duration_seconds,
                "long_play_hours": long_play_hours,
                "num_shots": effective_shots,
                "motion_model": motion_model,
                "camera_motion": camera_motion,
                "pipeline_strategy": pipeline_strategy,
                "allow_fallback": allow_fallback,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            user_inputs_file.parent.mkdir(parents=True, exist_ok=True)
            user_inputs_file.write_text(json.dumps(user_inputs_payload, indent=2), encoding="utf-8")
            logger.info(f"user_inputs_saved: {user_inputs_file.name}")
        except Exception as ex:
            logger.warning(f"failed_to_write_user_inputs: {ex}")

    sb = relax_to_ambient_storyboard(universal_sp)

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
        "primary_archetype": primary,
        "secondary_archetype": secondary,
        "cluster": sb.cluster,
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
        keyframes.append({"name": f"Shot {idx}: {primary.replace('_', ' ').title()}", "url": url, "timing": f"{duration_seconds / max(1, len(raw_kfs)):.1f}s"})

    motion_clips = []
    m_label = "Wan 2.1" if eff_motion in ("wan", "wan_2_1", "wan21") else "Kling v3 4K Native"
    for idx, mv_path in enumerate(raw_vids, 1):
        url = _to_url(mv_path)
        motion_clips.append({"name": f"Motion {idx}: {primary.title()}", "model": m_label, "duration": f"{duration_seconds:.0f}s", "url": url})

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
