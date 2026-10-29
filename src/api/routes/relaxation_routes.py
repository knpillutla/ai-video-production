"""Dedicated API Router for Biophilic Relaxation & Ambient World Productions.

Provides independent endpoints for ambient storyboard generation, binaural acoustic
mastering, and long-play broadcast rendering, decoupled from documentary and music video.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.api.routes.local_production import LocalProduceRequest, LocalProduceResponse, _reserve_next_episode_id
from src.core.storage import storage_service, sanitize_container_name
from src.core.telemetry import logger
from src.domain.format_artifacts import RelaxationArtifacts
from src.services.job_manager import job_manager
from src.services.network_production_service import produce_channel_video

router = APIRouter(prefix="/api/relaxation", tags=["Relaxation Studio Engine"])


class RelaxationCreateEpisodeRequest(BaseModel):
    """Payload to create a new relaxation episode."""
    channel_id: str = "earth_serenade"
    genre: Optional[str] = "relax/nature"
    archetype: Optional[str] = "alpine_streams"
    prompt: Optional[str] = None
    user_id: Optional[str] = "user_krishna_01"
    tier: Optional[str] = "balanced"


class RelaxationCreateEpisodeResponse(BaseModel):
    """Response containing created relaxation episode metadata."""
    success: bool
    episode_id: str
    title: str
    format: str = "relaxation"
    genre: str
    archetype: str


def _resolve_relax_episode_dir(user_id: str, channel_id: str, episode_id: str) -> Path:
    """Computes storage path for a relaxation episode."""
    c_name = sanitize_container_name(user_id) if "@" in user_id else user_id
    base = storage_service.root_dir / c_name / "networks" / channel_id / "relaxation" / "nature" / episode_id.lower()
    base.mkdir(parents=True, exist_ok=True)
    return base


def _find_relax_episode_dir(channel_id: str, episode_id: str) -> Optional[Path]:
    """Locates an existing relaxation episode directory."""
    ep_lower = episode_id.lower()
    for root in [storage_service.root_dir / "user-knpillutla-gmail-com" / "networks" / channel_id / "relaxation",
                 storage_service.root_dir / "networks" / channel_id / "relaxation",
                 storage_service.root_dir / "channels" / channel_id]:
        if root.exists():
            for sub_dir in root.iterdir():
                if sub_dir.is_dir():
                    candidate = sub_dir / ep_lower if sub_dir.name != ep_lower else sub_dir
                    if candidate.exists():
                        return candidate
    return None


@router.post("/create-episode", response_model=RelaxationCreateEpisodeResponse, status_code=status.HTTP_201_CREATED)
async def create_relaxation_episode(req: RelaxationCreateEpisodeRequest):
    """Initializes a new relaxation episode with channel-matched ambiance defaults."""
    user_id_val = req.user_id or "user_krishna_01"
    eff_channel = req.channel_id or "earth_serenade"
    next_id = _reserve_next_episode_id(user_id_val, eff_channel)
    ep_dir = _resolve_relax_episode_dir(user_id_val, eff_channel, next_id)

    genre = req.genre or "relax/nature"
    archetype = req.archetype or "alpine_streams"
    title = (req.prompt or f"{archetype.replace('_', ' ').title()} Sanctuary").strip()

    job_id = f"job_rel_{next_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=next_id, title=title, channel_id=eff_channel, user_id=user_id_val)

    logger.info(f"relax_episode_created: id={next_id} title='{title}' dir={ep_dir}")

    return RelaxationCreateEpisodeResponse(
        success=True,
        episode_id=next_id,
        title=title,
        genre=genre,
        archetype=archetype,
    )


@router.post("/stages/{stage_name}", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def execute_relaxation_stage(stage_name: str, req: LocalProduceRequest):
    """Execute a specific relaxation stage (script, photos, audio, motion, master)."""
    st = (stage_name or "").strip().lower()
    req.script_only = st in ("script", "story", "screenplay")
    req.photos_only = st in ("photos", "keyframes")
    req.audio_only = st in ("audio", "bgm")
    req.motion_only = st == "motion"
    req.master_only = st == "master"
    return await produce_relaxation(req)


@router.post("/produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_relaxation(req: LocalProduceRequest):
    """Produces relaxation stages independently (Storyboard -> Photos -> Audio -> Motion -> Master -> LongPlay)."""
    user_id_val = req.user_id or "user_krishna_01"
    eff_channel = req.channel_id or "earth_serenade"
    episode_id = req.episode_id or _reserve_next_episode_id(user_id_val, eff_channel)
    title = (req.title or req.prompt or f"Relaxation {episode_id}").strip()

    job_id = f"job_rel_{episode_id.lower()}_{int(time.time())}"
    job_manager.create_job(job_id=job_id, episode_id=episode_id, title=title, channel_id=eff_channel, user_id=user_id_val)

    res = await produce_channel_video(
        channel_id=eff_channel,
        prompt=req.prompt,
        duration_seconds=float(req.duration_seconds or 180.0),
        episode_id=episode_id,
        script_only=bool(req.script_only),
        photos_only=bool(req.photos_only),
        motion_only=bool(req.motion_only),
        audio_only=bool(req.audio_only),
        master_only=bool(req.master_only),
        pipeline_strategy=req.pipeline_strategy or "manual",
        num_shots=req.num_shots or 1,
        user_id=user_id_val,
        motion_model=req.motion_model or "auto",
        image_model=req.image_model or "flux_1_1_pro_ultra",
        long_play_hours=float(req.long_play_hours or 0.0),
        tier=req.tier or "balanced",
        weather=req.weather or "normal",
        format_slug="relaxation",
    )
    return LocalProduceResponse(**res)


@router.get("/artifacts/{channel_id}/{episode_id}", response_model=RelaxationArtifacts)
async def get_relaxation_artifacts(channel_id: str, episode_id: str):
    """Scans and returns the decoupled RelaxationArtifacts domain model for an episode."""
    ep_dir = _find_relax_episode_dir(channel_id, episode_id)
    if not ep_dir or not ep_dir.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Relaxation episode '{episode_id}' not found.")

    storyboard = None
    sb_p = ep_dir / "storyboard.json"
    if sb_p.exists():
        try:
            storyboard = json.loads(sb_p.read_text(encoding="utf-8"))
        except Exception:
            pass

    keyframes = []
    for ext in ("*.png", "*.jpg", "*.webp"):
        for img in sorted(ep_dir.glob(f"keyframe_{ext}")) + sorted(ep_dir.glob(f"shot_{ext}")):
            keyframes.append({"filename": img.name, "url": f"/storage/{img.name}", "size": img.stat().st_size})

    return RelaxationArtifacts(
        episode_id=episode_id,
        channel_id=channel_id,
        title=storyboard.get("title", f"Relaxation {episode_id}") if storyboard else f"Relaxation {episode_id}",
        current_stage=1 if not keyframes else 2,
        storyboard=storyboard,
        keyframes=keyframes,
    )
