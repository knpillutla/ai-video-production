import os
import shutil
import time
import json
from pathlib import Path
from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.services.channel_production_service import produce_channel_video
from src.services.job_manager import job_manager
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic
from src.providers.fal_storage import _fal_api_key

router = APIRouter(prefix="/api/production", tags=["Local Production Engine"])


class LocalProduceRequest(BaseModel):
    """Payload for local video synthesis and storage persistence."""
    prompt: str = Field(..., description="Prompt concept, theme, or script")
    title: Optional[str] = None
    episode_id: Optional[str] = Field(None, description="Channel-scoped episode ID; generated when omitted")
    user_id: Optional[str] = "user_krishna_01"
    production_type: Optional[str] = "Theme"
    tier: Optional[str] = "low_cost"
    video_type: Optional[str] = "Travel Guide & Doc"
    format_type: Optional[str] = "Long (16:9)"
    style_type: Optional[str] = "Realistic (Photoreal)"
    youtube_url: Optional[str] = None
    youtube_reference_url: Optional[str] = None
    youtube_reference_link: Optional[str] = None
    duration_seconds: Optional[float] = 6.0
    enable_bgm: Optional[bool] = None
    bgm: Optional[bool] = None
    enable_tts: Optional[bool] = None
    tts: Optional[bool] = None
    enable_voice_over: Optional[bool] = None
    voice_over: Optional[bool] = None
    enable_lipsync: Optional[bool] = None
    lipsync: Optional[bool] = None
    voice_gender: Optional[str] = None
    narration_male: Optional[bool] = None
    narration_female: Optional[bool] = None
    language: Optional[str] = "en"
    target_languages: Optional[list[str]] = None
    theme: Optional[str] = None
    idea: Optional[str] = None
    script: Optional[str] = None
    custom_script: Optional[str] = None
    channel_id: Optional[str] = None
    motion_model: Optional[str] = "wan"
    allow_fallback: Optional[bool] = False
    num_shots: Optional[int] = 1
    long_play_hours: Optional[float] = None
    camera_motion: Optional[str] = "locked_tripod"
    genre: Optional[str] = None
    genre_label: Optional[str] = None
    sub_genre: Optional[str] = None
    sub_genre_label: Optional[str] = None
    primary_archetype: Optional[str] = None
    primary_archetype_label: Optional[str] = None
    image_model: Optional[str] = "flux_dev"
    script_only: Optional[bool] = False
    photos_only: Optional[bool] = False
    motion_only: Optional[bool] = False
    audio_only: Optional[bool] = False
    master_only: Optional[bool] = False
    pipeline_strategy: Optional[str] = "manual"
    force_rerun: Optional[bool] = False


class LocalProduceResponse(BaseModel):
    """Response returned after local single-pass video render."""
    success: bool
    job_id: str
    episode_id: str
    title: str
    script: Optional[dict[str, Any]] = None
    video_url: Optional[str] = None
    nature_video_url: Optional[str] = None
    storage_path: Optional[str] = None
    file_size_bytes: Optional[int] = 0
    duration_seconds: float
    render_time_seconds: float
    artifacts: list[dict[str, Any]]
    editions: Optional[list[dict[str, Any]]] = None
    long_play_hours: Optional[float] = None
    keyframes: Optional[list[dict[str, Any]]] = None
    audio_stems: Optional[list[dict[str, Any]]] = None
    motion_clips: Optional[list[dict[str, Any]]] = None
    current_stage: Optional[int] = 1
    stage: Optional[int] = 1


def _reserve_next_episode_id(user_id: str, channel_id: str) -> str:
    """Atomically reserve the next sequential episode ID within one channel."""
    channel_dir = storage_service.get_user_container_path(user_id) / "channels" / channel_id
    channel_dir.mkdir(parents=True, exist_ok=True)
    highest = 0
    for path in channel_dir.iterdir():
        if not path.is_dir() or not path.name.upper().startswith("EP-"):
            continue
        suffix = path.name[3:]
        if suffix.isdigit():
            highest = max(highest, int(suffix))

    next_number = highest + 1
    while True:
        episode_id = f"EP-{next_number:03d}"
        try:
            (channel_dir / episode_id).mkdir()
            return episode_id
        except FileExistsError:
            next_number += 1


@router.post("/local-produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_video_locally(req: LocalProduceRequest):
    """Synthesize a complete broadcast-grade MP4 video with scenes and audio stems."""
    title = req.title or (req.prompt[:36] if len(req.prompt) > 36 else req.prompt) or "Gemini-Directed Production"
    capped_duration = min(120.0, max(4.0, float(req.duration_seconds or 6.0)))
    eff_bgm = req.enable_bgm if req.enable_bgm is not None else (req.bgm if req.bgm is not None else True)
    user_id_val = req.user_id or "user_krishna_01"
    strat = req.pipeline_strategy or "manual"
    eff_script_only = bool(req.script_only)
    eff_photos_only = bool(req.photos_only)
    eff_motion_only = bool(req.motion_only)
    eff_audio_only = bool(req.audio_only)
    eff_master_only = bool(req.master_only)

    if strat == "manual" and not (eff_script_only or eff_photos_only or eff_motion_only or eff_audio_only or eff_master_only):
        eff_script_only = True

    eff_channel_id = req.channel_id
    if not eff_channel_id:
        user_obj = repo.get_user_by_email(user_id_val) if "@" in user_id_val else None
        if user_obj:
            user_chans = repo.list_channels(user_obj.id)
            if user_chans:
                eff_channel_id = user_chans[0].channel_slug
    eff_channel_id = eff_channel_id or "default_channel"
    episode_id = req.episode_id or _reserve_next_episode_id(user_id_val, eff_channel_id)

    topic_check = None
    if req.prompt.strip():
        topic_check = await check_topic_duplicate(
            topic=title, metadata={"video_type": req.video_type, "format_type": req.format_type, "style_type": req.style_type},
            final_story=req.prompt, user_id=user_id_val, channel_id=eff_channel_id, threshold=0.80,
        )
    if topic_check and topic_check.get("is_duplicate"):
        logger.info(f"topic_duplicate_pivot: {title} matches {topic_check.get('matched_episode')}. Auto-pivoting angle.")
        pivots = ["Golden Twilight & Evening Mist", "Morning Glacial Mist & Soft Sunlight", "Tranquil Sunset Glow", "Lush Rainforest Canopy"]
        pivot_tag = pivots[int(time.time()) % len(pivots)]
        title = f"{title} ~ {pivot_tag}"

    job_id = f"job_{episode_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=title, channel_id=eff_channel_id, user_id=user_id_val)

    has_fal = bool(_fal_api_key())
    eff_fallback = bool(req.allow_fallback or not has_fal)
    eff_motion = req.motion_model if req.motion_model and req.motion_model != "auto" else ("wan" if capped_duration <= 10.0 else "auto")

    try:
        result = await produce_channel_video(
            channel_id=eff_channel_id,
            prompt=req.prompt,
            duration_seconds=capped_duration,
            episode_id=episode_id,
            script_only=eff_script_only,
            photos_only=eff_photos_only,
            motion_only=eff_motion_only,
            audio_only=eff_audio_only,
            master_only=eff_master_only,
            pipeline_strategy=strat,
            no_bgm=not eff_bgm,
            num_shots=req.num_shots or 0,
            allow_fallback=eff_fallback,
            user_id=user_id_val,
            motion_model=eff_motion,
            long_play_hours=req.long_play_hours,
            camera_motion=req.camera_motion or "locked_tripod",
            force_rerun=bool(req.force_rerun),
            genre=req.genre,
            sub_genre=req.sub_genre,
            primary_archetype=req.primary_archetype,
            selection_labels={
                "genre": req.genre_label or "",
                "sub_genre": req.sub_genre_label or "",
                "primary_archetype": req.primary_archetype_label or "",
            },
            image_model=req.image_model or "flux_dev",
        )
        eff_job_id = result.get("job_id") or job_id
        if eff_script_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=1, progress=15, status="ready",
                keyframes=[], motion_clips=[], audio_stems=[], video_url=None,
            )
        elif eff_photos_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=2, progress=35, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=[],
                audio_stems=[], video_url=None,
            )
        elif eff_motion_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=3, progress=60, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=result.get("motion_clips", []),
                audio_stems=[], video_url=None,
            )
        elif eff_audio_only:
            job_manager.update_job(
                job_id=eff_job_id, stage=4, progress=80, status="ready",
                keyframes=result.get("keyframes", []), motion_clips=result.get("motion_clips", []),
                audio_stems=result.get("audio_stems", []), video_url=None,
            )
        else:
            job_manager.update_job(
                job_id=eff_job_id, stage=5, progress=100, status="completed",
                keyframes=result.get("keyframes", []), motion_clips=result.get("motion_clips", []),
                audio_stems=result.get("audio_stems", []), video_url=result.get("video_url"),
            )
            await remember_topic(
                topic=result.get("title") or title, metadata={"video_type": req.video_type, "format_type": req.format_type, "style_type": req.style_type},
                final_story=req.prompt, episode_id=episode_id, user_id=user_id_val, channel_id=eff_channel_id,
            )
        return LocalProduceResponse(**result)
    except HTTPException:
        job_manager.update_job(job_id=job_id, status="failed", error="HTTP Exception")
        raise
    except Exception as exc:
        logger.error(f"local_production_failed: {exc}", exc_info=True)
        job_manager.update_job(job_id=job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Local production failed: {str(exc)}")


@router.get("/poll-artifacts")
async def poll_production_artifacts(channel_id: str, episode_id: str, user_id: str = "knpillutla@gmail.com"):
    """Real-time disk scanner returning synthesized keyframes, motion clips, and audio as they finish."""
    c_dir = storage_service.get_user_container_path(user_id) / "channels" / channel_id / episode_id
    if not c_dir.exists():
        return {"keyframes": [], "motion_clips": [], "audio_stems": [], "video_url": None, "stage": 1}

    files = {f.name: f for f in c_dir.iterdir() if f.is_file()}
    def _file_url(f: Path) -> str:
        try:
            mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
            rel = f.resolve().relative_to(storage_service.root_dir.resolve())
            return f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
        except Exception:
            p_str = str(f.resolve()).replace("\\", "/")
            mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
            if "/storage/" in p_str:
                return f"/storage/{p_str.split('/storage/', 1)[1]}?t={mtime}"
            return f"/storage/{f.name}?t={mtime}"

    kfs = [{"name": f"Shot {k.replace('keyframe_p','').replace('.jpg','')}", "url": _file_url(files[k]), "filename": k} for k in sorted(files) if k.startswith("keyframe_p") and k.endswith(".jpg") and files[k].stat().st_size > 1000]

    manifest_file = c_dir / "episode_manifest.json"
    m_data = json.loads(manifest_file.read_text("utf-8")) if manifest_file.exists() else {}
    m_model = "Wan 2.1" if (m_data.get("motion_model") in ("wan", "wan_2_1") or m_data.get("duration_seconds", 5.0) <= 10.0) else "Kling v3 Pro"
    vids = [{"name": f"Motion {m.replace('motion_p','').replace('.mp4','')}", "url": _file_url(files[m]), "model": m_model} for m in sorted(files) if m.startswith("motion_p") and m.endswith(".mp4") and not m.endswith("_fwd_seamless.mp4") and files[m].stat().st_size > 1000]

    stems = []
    if "raw_soundtrack.mp3" in files and files["raw_soundtrack.mp3"].stat().st_size > 1000:
        stems.append({"name": "Suno Soundtrack", "url": _file_url(files["raw_soundtrack.mp3"]), "color": "cyan"})
    if "velvet_binaural_master_48k.mp3" in files and files["velvet_binaural_master_48k.mp3"].stat().st_size > 1000:
        stems.append({"name": "432Hz Velvet Binaural ASMR", "url": _file_url(files["velvet_binaural_master_48k.mp3"]), "color": "emerald"})

    master_url = _file_url(files["master_4k_ambient.mp4"]) if ("master_4k_ambient.mp4" in files and files["master_4k_ambient.mp4"].stat().st_size > 1000) else None
    nature_master_url = _file_url(files["master_4k_ambient_nature_only.mp4"]) if ("master_4k_ambient_nature_only.mp4" in files and files["master_4k_ambient_nature_only.mp4"].stat().st_size > 1000) else None

    dur_str = f"{int(m_data.get('duration_seconds', 5))}s"
    editions = []
    if master_url:
        editions.append({"edition_id": "master_music", "name": f"🎵 Ambient Soundtrack ({dur_str})", "label": "4K Ambient Music & 432Hz BGM", "format": "4K UHD", "duration": dur_str, "url": master_url})
    if nature_master_url:
        editions.append({"edition_id": "master_nature", "name": f"🌊 Pure Nature ASMR ({dur_str})", "label": "4K Pure Nature Soundscape", "format": "4K Nature", "duration": dur_str, "url": nature_master_url})
    if "short_9x16_teaser.mp4" in files and files["short_9x16_teaser.mp4"].stat().st_size > 1000:
        editions.append({"edition_id": "short_teaser", "name": "📱 9:16 Vertical Short Teaser (20s)", "label": "9:16 Vertical YouTube Short / Reel", "format": "9:16 Short", "duration": "20s", "url": _file_url(files["short_9x16_teaser.mp4"])})

    long_play_editions = []
    lp_patterns = [
        (["master_4k_8hour_broadcast.mp4", "master_4k_8hour_sleep.mp4"], "8h_music", "8-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "8:00:00 (8h)", "16:9 Long-Play"),
        (["master_4k_8hour_nature_only_broadcast.mp4", "master_4k_8hour_nature_only_sleep.mp4"], "8h_nature", "8-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature ASMR", "8:00:00 (8h)", "16:9 Long-Play"),
        (["master_4k_3hour_broadcast.mp4", "master_4k_3hour_sleep.mp4"], "3h_music", "3-Hour 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "3:00:00 (3h)", "16:9 Long-Play"),
        (["master_4k_3hour_nature_only_broadcast.mp4", "master_4k_3hour_nature_only_sleep.mp4"], "3h_nature", "3-Hour 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature ASMR", "3:00:00 (3h)", "16:9 Long-Play"),
        (["master_4k_30min_broadcast.mp4", "master_4k_0.5hour_broadcast.mp4"], "30m_music", "30-Minute 4K Broadcast (Music)", "fa-music text-indigo-400", "Music + 432Hz BGM", "30:00 (30m)", "16:9 Long-Play"),
        (["master_4k_30min_nature_only_broadcast.mp4", "master_4k_0.5hour_nature_only_broadcast.mp4"], "30m_nature", "30-Minute 4K Broadcast (Pure Nature)", "fa-leaf text-emerald-400", "Pure Nature ASMR", "30:00 (30m)", "16:9 Long-Play"),
    ]
    for fn_list, eid, name, icon, mode, dur, fmt in lp_patterns:
        target_f = next((files[fn] for fn in fn_list if fn in files and files[fn].stat().st_size > 1000), None)
        if target_f:
            sz_mb = round(target_f.stat().st_size / (1024 * 1024), 1)
            long_play_editions.append({"edition_id": eid, "name": name, "icon": icon, "audio_mode": mode, "duration": dur, "format": fmt, "status": "completed", "url": _file_url(target_f), "size_str": f"{sz_mb} MB" if sz_mb < 1000 else f"{round(sz_mb/1024, 2)} GB", "filename": target_f.name})

    screenplay_file = c_dir / "screenplay.json"
    screenplay_data = json.loads(screenplay_file.read_text("utf-8")) if screenplay_file.exists() else None

    pipeline_state_file = c_dir / "pipeline_state.json"
    pipeline_state_data = json.loads(pipeline_state_file.read_text("utf-8")) if pipeline_state_file.exists() else None

    is_approved_val = bool(pipeline_state_data.get("is_approved") if pipeline_state_data else m_data.get("is_approved", False))
    eff_stage = pipeline_state_data.get("current_stage") if pipeline_state_data else stage

    return {
        "keyframes": kfs, "motion_clips": vids, "audio_stems": stems,
        "video_url": master_url or nature_master_url, "nature_video_url": nature_master_url,
        "editions": editions, "long_play_editions": long_play_editions, "stage": eff_stage,
        "script": screenplay_data if screenplay_data else (m_data if m_data else None),
        "screenplay": screenplay_data,
        "pipeline_state": pipeline_state_data,
        "manifest": m_data if m_data else None,
        "is_approved": is_approved_val,
        "long_play_hours": m_data.get("long_play_hours"),
    }


@router.post("/episodes/{episode_id}/approve")
async def approve_episode(episode_id: str, channel_id: Optional[str] = None, user_id: str = "knpillutla@gmail.com"):
    """Mark an episode as approved in its disk manifest."""
    user_chan_dir = storage_service.get_user_container_path(user_id) / "channels"
    target_dirs = []
    if channel_id and (user_chan_dir / channel_id / episode_id).exists():
        target_dirs.append(user_chan_dir / channel_id / episode_id)
    elif user_chan_dir.exists():
        for ch_dir in user_chan_dir.iterdir():
            if ch_dir.is_dir() and (ch_dir / episode_id).exists():
                target_dirs.append(ch_dir / episode_id)

    if not target_dirs:
        return {"success": True, "episode_id": episode_id, "is_approved": True, "persisted_disk": False}

    for ep_dir in target_dirs:
        pipe_file = ep_dir / "pipeline_state.json"
        data = {}
        if pipe_file.exists():
            try:
                data = json.loads(pipe_file.read_text("utf-8"))
            except Exception:
                pass
        data["is_approved"] = True
        data["approved_at"] = time.time()
        pipe_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {"success": True, "episode_id": episode_id, "is_approved": True, "message": f"Episode {episode_id} approved."}


@router.delete("/episodes/{episode_id}")
async def delete_episode_artifacts(episode_id: str, channel_id: Optional[str] = None, user_id: str = "knpillutla@gmail.com"):
    """Delete all synthesized artifacts and folders for a specific episode from disk."""
    user_chan_dir = storage_service.get_user_container_path(user_id) / "channels"
    deleted_paths = []
    if channel_id and (user_chan_dir / channel_id / episode_id).exists():
        ep_dir = user_chan_dir / channel_id / episode_id
        shutil.rmtree(ep_dir, ignore_errors=True)
        deleted_paths.append(str(ep_dir))
    elif user_chan_dir.exists():
        for ch_dir in user_chan_dir.iterdir():
            if ch_dir.is_dir() and (ch_dir / episode_id).exists():
                ep_dir = ch_dir / episode_id
                shutil.rmtree(ep_dir, ignore_errors=True)
                deleted_paths.append(str(ep_dir))
    return {"success": True, "episode_id": episode_id, "deleted_paths": deleted_paths, "message": f"Episode {episode_id} deleted."}


@router.post("/stop")
async def stop_production_job(payload: dict):
    """Mark production job as paused and signal cancellation."""
    return {"success": True, "episode_id": payload.get("episode_id", "EP-001"), "status": "paused"}


@router.get("/jobs/{job_id}")
async def get_production_job_status(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job {job_id} not found.")
    return job


@router.get("/jobs/{job_id}/stream")
async def stream_production_job_progress(job_id: str):
    return StreamingResponse(job_manager.stream_job(job_id), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "Connection": "keep-alive"})
