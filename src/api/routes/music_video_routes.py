"""Dedicated API Router for Global Music & Dance Video Production.

Exposes independent endpoints for music video synthesis and artifact polling,
decoupled from documentary and relaxation screenplay pipelines.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status

from src.api.routes.local_production import LocalProduceRequest, LocalProduceResponse, _reserve_next_episode_id
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic
from src.services.job_manager import job_manager
from src.studios.music_video_studio.music_pipeline import MusicVideoPipeline

router = APIRouter(prefix="/api/music-video", tags=["Music Video Studio Engine"])


def _file_url(f: Path) -> str:
    """Format safe static storage URL for client browsers."""
    try:
        mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
        rel = f.resolve().relative_to(storage_service.root_dir.resolve())
        return f"/storage/{str(rel).replace('\\', '/')}?t={mtime}"
    except Exception:
        p_str = str(f.resolve()).replace("\\", "/")
        mtime = int(f.stat().st_mtime) if f.exists() else int(time.time())
        return f"/storage/{p_str.split('/storage/', 1)[1]}?t={mtime}" if "/storage/" in p_str else f"/storage/{f.name}?t={mtime}"


@router.post("/produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_music_video(req: LocalProduceRequest):
    """Synthesize broadcast 4K music video with independent storyboards and lyrics."""
    title = req.title or (req.prompt[:36] if len(req.prompt) > 36 else req.prompt) or "Music Video Production"
    capped_duration = min(240.0, max(5.0, float(req.duration_seconds or 60.0)))
    user_id_val = req.user_id or "user_krishna_01"
    eff_channel_id = req.channel_id or "default_channel"
    episode_id = req.episode_id or _reserve_next_episode_id(user_id_val, eff_channel_id)
    strat = req.pipeline_strategy or "manual"

    eff_script_only = bool(req.script_only)
    eff_photos_only = bool(req.photos_only)
    eff_audio_only = bool(req.audio_only)
    eff_master_only = bool(req.master_only)
    if strat == "manual" and not (eff_photos_only or eff_audio_only or eff_master_only):
        eff_script_only = True

    if req.prompt.strip():
        topic_check = await check_topic_duplicate(
            topic=title, metadata={"genre": req.genre or "music/static_vocal", "country": req.country, "language": req.language},
            final_story=req.prompt, user_id=user_id_val, channel_id=eff_channel_id, threshold=0.80,
        )
        if topic_check and topic_check.get("is_duplicate"):
            pivots = ["Festival Fairgrounds Celebration", "Twilight Mountain Terrace", "Sunset Riverbank Groove"]
            title = f"{title} ~ {pivots[int(time.time()) % len(pivots)]}"

    job_id = f"job_mv_{episode_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=title, channel_id=eff_channel_id, user_id=user_id_val)

    t0 = time.time()
    try:
        pipeline = MusicVideoPipeline(
            user_id=user_id_val, channel_id=eff_channel_id, episode_id=episode_id,
            production_name=req.production_name or "standalone",
        )
        result = await pipeline.produce(
            genre=req.genre or "music/static_vocal", sub_genre=req.sub_genre, primary_archetype=req.primary_archetype,
            prompt=req.prompt, country=req.country, language=req.language, culture=req.culture,
            duration_seconds=capped_duration, num_shots=max(1, req.num_shots or 1), tier=req.tier or "balanced",
            script_only=eff_script_only, photos_only=eff_photos_only, audio_only=eff_audio_only, master_only=eff_master_only,
            vocal_gender=req.vocal_gender,
        )
        eff_stage = result.get("current_stage", 1)
        job_manager.update_job(
            job_id=job_id, stage=eff_stage, progress=100 if eff_stage >= 5 else eff_stage * 20,
            status="completed" if eff_stage >= 5 else "ready", keyframes=result.get("keyframes", []),
            motion_clips=[], audio_stems=result.get("audio_stems", []), video_url=result.get("video_url"),
        )
        if eff_stage >= 5:
            await remember_topic(
                topic=result.get("title") or title, metadata={"video_type": "music_video", "language": req.language, "country": req.country},
                final_story=req.prompt, episode_id=episode_id, user_id=user_id_val, channel_id=eff_channel_id,
            )
        return LocalProduceResponse(**result)
    except Exception as exc:
        logger.error(f"music_video_production_failed: ep={episode_id} err='{exc}'", exc_info=True)
        job_manager.update_job(job_id=job_id, status="failed", error=str(exc))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Music video failed: {str(exc)}")


@router.get("/poll-artifacts")
async def poll_music_video_artifacts(
    channel_id: str,
    episode_id: str,
    format: Optional[str] = "music_video",
    production_name: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
):
    """Disk scanner returning music video scenes, stems, and masters in real-time."""
    c_dir = storage_service.find_episode_path(
        user_id=user_id, channel_id=channel_id, episode_id=episode_id,
        format_slug=format or "music_video", production_name=production_name,
    )
    if not c_dir or not c_dir.exists():
        return {"keyframes": [], "motion_clips": [], "audio_stems": [], "video_url": None, "stage": 1, "status": "ready"}

    # 1. Keyframes from scenes/
    kfs = []
    scenes_dir = c_dir / "scenes"
    if scenes_dir.exists():
        for p in sorted(scenes_dir.glob("scene_*.jpg")):
            if p.stat().st_size > 1000:
                kfs.append({"name": f"Scene {p.stem.replace('scene_', '')}", "url": _file_url(p), "filename": p.name})

    # 2. Audio stems from stems/
    stems = []
    stems_dir = c_dir / "stems"
    if stems_dir.exists():
        for a in sorted(stems_dir.glob("*.mp3")):
            if a.stat().st_size > 1000:
                stems.append({"name": "Suno Vocal Soundtrack" if "soundtrack" in a.name else a.stem, "filename": a.name, "url": _file_url(a), "color": "cyan"})

    # 3. Master Renders & Editions
    editions = []
    master_url = None
    renders_dir = c_dir / "master_renders"
    if renders_dir.exists():
        for m in sorted(renders_dir.glob("*.mp4")):
            if m.stat().st_size > 1000:
                m_url = _file_url(m)
                if not master_url:
                    master_url = m_url
                editions.append({"edition_id": "master_music_video", "name": f"🎵 4K Vocal Master", "label": "4K Vocal Music Video Master", "format": "4K UHD", "url": m_url})

    # 4. State & Storyboard metadata
    sb_file = c_dir / "storyboard.json"
    sb_data = json.loads(sb_file.read_text("utf-8")) if sb_file.exists() else None
    pipe_file = c_dir / "pipeline_state.json"
    pipe_data = json.loads(pipe_file.read_text("utf-8")) if pipe_file.exists() else None
    manifest_file = c_dir / "episode_manifest.json"
    manifest_data = json.loads(manifest_file.read_text("utf-8")) if manifest_file.exists() else None

    eff_stage = pipe_data.get("current_stage") if pipe_data else (5 if master_url else (3 if stems else (2 if kfs else 1)))
    ep_status = "completed" if master_url else (pipe_data.get("stage_status") if pipe_data else "ready")

    return {
        "keyframes": kfs, "motion_clips": [], "audio_stems": stems, "video_url": master_url,
        "editions": editions, "long_play_editions": [], "stage": eff_stage, "current_stage": eff_stage,
        "status": ep_status, "format": "music_video", "format_slug": "music_video",
        "genre": manifest_data.get("genre") if manifest_data else "music/static_vocal",
        "script": sb_data, "screenplay": sb_data, "pipeline_state": pipe_data, "manifest": manifest_data,
        "is_approved": bool(pipe_data.get("is_approved") if pipe_data else False),
    }


@router.get("/country-languages")
async def get_country_languages_endpoint(
    country: str = "India",
    refresh: bool = False,
):
    """Retrieve or autonomously curate regional languages for any country in the world."""
    from src.studios.music_video_studio.country_language_curator import get_or_curate_country_languages
    langs = await get_or_curate_country_languages(country=country, force_refresh=refresh)
    return {"country": country, "languages": langs}


@router.get("/country-hierarchy")
async def get_country_hierarchy_endpoint(
    country: str = "India",
    refresh: bool = False,
):
    """Retrieve or autonomously curate 4-tier sub-regions and regional languages for country."""
    from src.studios.music_video_studio.country_region_curator import get_or_curate_country_hierarchy
    hierarchy = await get_or_curate_country_hierarchy(country=country, force_refresh=refresh)
    return hierarchy

