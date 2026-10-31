"""Dedicated Stage Orchestrator for Blue-Chip Educational Documentary Format."""
from __future__ import annotations

import asyncio
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.services.ambient_export_service import get_media_duration
from src.services.job_manager import job_manager
from src.services.soundtrack_service import soundtrack_service
from src.services.visual_batch_service import visual_batch_service
from src.studios.documentary_studio.doc_artifact_scanner import scan_documentary_artifacts
from src.studios.documentary_studio.doc_directorial_motion_service import execute_pass2_directorial_motion
from src.studios.documentary_studio.doc_export_stages import run_doc_master_stage, run_doc_motion_stage
from src.studios.documentary_studio.doc_stage_helpers import (
    load_screenplay_or_raise,
    resolve_doc_episode_dir,
    select_shots_within_user_duration,
    update_doc_pipeline_state,
    write_doc_user_inputs,
)
from src.studios.documentary_studio.doc_story_service import build_raw_documentary_story, persist_raw_documentary_story
from src.studios.documentary_studio.doc_voice_service import produce_documentary_narration_stage


async def run_doc_story_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 1: Generate 22-chapter raw_gemini_story.json and persist all initial metadata."""
    story_file = ep_dir / "raw_gemini_story.json"
    if not getattr(req, "force_rerun", False) and story_file.is_file() and story_file.stat().st_size > 200:
        story_dict = json.loads(story_file.read_text(encoding="utf-8"))
        dest = story_dict.get("destination_entity") or ep_dir.parent.name.replace("_", " ").title()
    else:
        dest = (getattr(req, "production_name", None) or getattr(req, "country", None) or "").strip()
        if (not dest or dest.lower() in ("standalone", "destination")) and ep_dir.parent.name not in ("documentary", "networks", "channels", "destination"):
            dest = ep_dir.parent.name.replace("_", " ").title()
        if not dest or dest.lower() in ("standalone", "destination"):
            dest = "Norway"
        if req is not None:
            setattr(req, "production_name", dest)
            setattr(req, "country", dest)
        story_dict = await asyncio.to_thread(
            build_raw_documentary_story,
            dest,
            getattr(req, "genre", None) or "doc/nations",
            getattr(req, "sub_genre", None) or "europe_nations",
            getattr(req, "primary_archetype", None) or "countries",
            getattr(req, "prompt", None) or "",
            getattr(req, "channel_id", None) or "euro_discovery",
        )
        import re
        final_dest = story_dict.get("destination_entity") or dest
        safe_dest = re.sub(r"[^a-zA-Z0-9_-]+", "_", final_dest.lower()).strip("_") or "destination"
        if safe_dest != ep_dir.parent.name:
            ep_dir = ep_dir.parent.parent / safe_dest / ep_dir.name
        ep_dir.mkdir(parents=True, exist_ok=True)
        persist_raw_documentary_story(ep_dir, story_dict)
        write_doc_user_inputs(ep_dir, req, final_dest, title=story_dict.get("title"))
        dest = final_dest
    update_doc_pipeline_state(ep_dir, 1, "story")
    return {"current_stage": 1, "story": story_dict, "production_name": dest, "ep_dir": str(ep_dir)}


async def run_doc_narration_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 2: Synthesize per-chapter narration stems and spoken_narration.mp3."""
    eff_tts = getattr(req, "tts_model", None) or getattr(settings.voice, "default_tts_model", "gemini")
    narr_res = await produce_documentary_narration_stage(
        ep_dir=ep_dir,
        voice_id="en-GB-RyanNeural",
        tts_model=eff_tts,
        force_rerun=bool(getattr(req, "force_rerun", False)),
        execution_mode=getattr(req, "execution_mode", None) or "test",
    )
    update_doc_pipeline_state(ep_dir, 2, "narration")
    return {"current_stage": 2, "duration_seconds": float(narr_res.get("total_duration", 60.0)), "story": narr_res.get("story")}


async def run_doc_screenplay_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 3: Formulate 3-shot directorial screenplay (raw_gemini_screenplay.json) from story + narration."""
    sp_file = ep_dir / "raw_gemini_screenplay.json"
    force_rerun = bool(getattr(req, "force_rerun", False))
    if not force_rerun and sp_file.is_file() and sp_file.stat().st_size > 200:
        sp_data = json.loads(sp_file.read_text(encoding="utf-8"))
        update_doc_pipeline_state(ep_dir, 3, "screenplay")
        return {"current_stage": 3, "screenplay": sp_data, "script": sp_data}

    story_file = ep_dir / "raw_gemini_story.json"
    if not story_file.is_file():
        await run_doc_story_stage(ep_dir, req)
    story_data = json.loads(story_file.read_text(encoding="utf-8"))

    stems_dir = ep_dir / "narration_stems"
    ch_durations: Dict[int, float] = {}
    chapters = story_data.get("chapters") or []
    for idx, ch in enumerate(chapters, 1):
        c_idx = int(ch.get("chapter_index") or idx)
        raw_stem = stems_dir / f"chapter_{c_idx}_raw.mp3"
        pad_stem = stems_dir / f"chapter_{c_idx}_padded.mp3"
        if raw_stem.is_file() and raw_stem.stat().st_size > 500:
            ch_durations[c_idx] = round(float(get_media_duration(raw_stem) or 15.0), 2)
        elif pad_stem.is_file() and pad_stem.stat().st_size > 500:
            ch_durations[c_idx] = max(6.0, round(float(get_media_duration(pad_stem) or 18.0) - 3.0, 2))
        else:
            ch_durations[c_idx] = float(ch.get("duration_seconds") or 18.0)

    directed = await execute_pass2_directorial_motion(
        story_data, ch_durations, raw_output_path=sp_file, execution_mode=getattr(req, "execution_mode", None) or "test", allow_fallback=True
    )
    update_doc_pipeline_state(ep_dir, 3, "screenplay")
    return {"current_stage": 3, "screenplay": directed, "script": directed}


async def run_doc_photos_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 4: Read documentary shots from chapters[].shots and render keyframes."""
    sp_data = load_screenplay_or_raise(ep_dir)
    shots = select_shots_within_user_duration(sp_data, ep_dir, req)
    target_idx = getattr(req, "target_shot_index", None)
    force_rerun = bool(getattr(req, "force_rerun", False))

    kf_tasks = [
        (
            shot.get("visual_prompt") or shot.get("visual_description") or shot.get("description") or ch.get("visual_directive") or "Documentary vista",
            ep_dir / f"keyframe_p{s}.jpg",
            ep_dir / f"fal_req_p{s}.json",
            s,
        )
        for s, ch, shot in shots
        if target_idx is None or int(target_idx) == s
    ]

    if kf_tasks:
        exec_mode = str(getattr(req, "execution_mode", None) or "test").lower()
        await visual_batch_service.render_keyframes_batch(
            tasks=kf_tasks,
            aspect_ratio="16:9",
            force_rerun=force_rerun or (target_idx is not None),
            image_model=getattr(req, "image_model", None) or "zimage",
            enable_4k_upscale=(exec_mode == "prod"),
        )
    update_doc_pipeline_state(ep_dir, 4, "keyframes")
    return {"current_stage": 4, "screenplay": sp_data, "script": sp_data}


async def run_doc_bgm_stage(ep_dir: Path, req: Any) -> Dict[str, Any]:
    """Stage 5: Synthesize background music stem via shared soundtrack_service."""
    sp_data = load_screenplay_or_raise(ep_dir)
    shots = select_shots_within_user_duration(sp_data, ep_dir, req)
    tot_dur = sum(float(s.get("duration_seconds") or 6.0) for _, _, s in shots) or float(sp_data.get("total_duration_seconds") or 120.0)
    await soundtrack_service.synthesize_ambient_soundtrack(
        sp_data.get("title") or f"Documentary {ep_dir.name}",
        "orchestral documentary score, atmospheric strings, cinematic ambient",
        ep_dir / "raw_soundtrack.mp3",
        min(tot_dur, 240.0),
        "documentary orchestral",
        episode_id=ep_dir.name,
        force_rerun=bool(getattr(req, "force_rerun", False)),
    )
    update_doc_pipeline_state(ep_dir, 5, "bgm")
    return {"current_stage": 5, "screenplay": sp_data, "script": sp_data}


async def dispatch_documentary_stage(req: Any, stage_name: Optional[str] = None) -> Dict[str, Any]:
    """Route a documentary stage request to its dedicated stage handler and return standardized response."""
    t0 = time.time()
    user_id = req.user_id if (getattr(req, "user_id", None) and "@" in str(req.user_id)) else (getattr(req, "user_id", None) or "knpillutla@gmail.com")
    channel_id = getattr(req, "channel_id", None) or "euro_discovery"
    episode_id = getattr(req, "episode_id", None) or "ep-001"
    ep_dir = resolve_doc_episode_dir(user_id, channel_id, episode_id, getattr(req, "production_name", None), req)

    st = (stage_name or "").strip().lower()
    if not st:
        flags = [
            ("screenplay", "screenplay_only"),
            ("narration", "narration_only"),
            ("photos", "photos_only"),
            ("bgm", "bgm_only"),
            ("motion", "motion_only"),
            ("master", "master_only"),
            ("story", "script_only"),
        ]
        st = next((name for name, attr in flags if getattr(req, attr, False)), "")
        if not st:
            st = "narration" if (getattr(req, "audio_only", False) and "suno" not in str(getattr(req, "prompt", "") or "").lower()) else ("bgm" if getattr(req, "audio_only", False) else "story")

    job_id = f"job_doc_{episode_id.lower()}_{st}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=getattr(req, "title", None) or f"Documentary {episode_id}", channel_id=channel_id, user_id=user_id)
    handlers = {
        "story": run_doc_story_stage,
        "script": run_doc_story_stage,
        "narration": run_doc_narration_stage,
        "screenplay": run_doc_screenplay_stage,
        "photos": run_doc_photos_stage,
        "keyframes": run_doc_photos_stage,
        "bgm": run_doc_bgm_stage,
        "audio": run_doc_bgm_stage,
        "motion": run_doc_motion_stage,
        "master": run_doc_master_stage,
    }
    stage_res = await handlers.get(st, run_doc_story_stage)(ep_dir, req)
    dest_val = (
        stage_res.get("production_name")
        or (stage_res.get("story") or {}).get("destination_entity")
        or (stage_res.get("screenplay") or {}).get("destination_entity")
        or getattr(req, "production_name", None)
        or ep_dir.parent.name.replace("_", " ").title()
    )
    if dest_val and hasattr(req, "production_name"):
        setattr(req, "production_name", dest_val)
    scanned = scan_documentary_artifacts(
        channel_id=channel_id, episode_id=episode_id, format_slug="documentary",
        production_name=dest_val, user_id=user_id,
    )
    eff_stage = int(stage_res.get("current_stage") or scanned.get("current_stage") or 1)
    job_manager.update_job(job_id=job_id, stage=eff_stage, progress=100, status="ready")
    dur = float(stage_res.get("duration_seconds") or (scanned.get("screenplay") or {}).get("active_duration_seconds") or 120.0)
    return {
        "success": True,
        "job_id": job_id,
        "episode_id": episode_id,
        "stage": eff_stage,
        "current_stage": eff_stage,
        "title": (stage_res.get("story") or {}).get("title") or scanned.get("title") or getattr(req, "title", None) or f"Documentary {episode_id}",
        "production_name": dest_val,
        "duration_seconds": dur,
        "render_time_seconds": round(time.time() - t0, 2),
        "master_video_url": scanned.get("master_url"),
        "keyframes": scanned.get("keyframes", []),
        "motion_clips": scanned.get("motion_clips", []),
        "audio_stems": scanned.get("audio_stems", []),
        "artifacts": scanned.get("artifacts", []),
        "story": stage_res.get("story") or scanned.get("story"),
        "screenplay": stage_res.get("screenplay") or scanned.get("screenplay"),
        "script": stage_res.get("script") or scanned.get("screenplay") or scanned.get("script"),
    }
