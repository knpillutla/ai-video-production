"""Long-Play Multi-Hour Broadcast Generation and Status API Router.

Stretches 4K master videos into 1-Hour, 3-Hour, or 8-Hour dual broadcasts
(Ambient BGM + Pure Nature ASMR) upon user review and approval.
"""

from __future__ import annotations

import asyncio
import json
import re
import time
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.core.storage import storage_service
from src.core.telemetry import logger
from src.services.long_play_stretcher import export_long_play_broadcast

router = APIRouter(prefix="/api/production", tags=["Long-Play Broadcast Engine"])

# In-memory progress tracking for long-play rendering jobs
long_play_jobs: dict[str, dict[str, Any]] = {}


class LongPlayStretchRequest(BaseModel):
    channel_id: Optional[str] = None
    hours: float = Field(3.0, description="Target duration in hours (1.0, 3.0, or 8.0)")
    fade_to_black_hours: Optional[float] = None
    user_id: Optional[str] = "knpillutla@gmail.com"


def _to_storage_url(p: Path | str) -> str:
    p_str = str(p).replace("\\", "/")
    if "/storage/" in p_str:
        return "/storage/" + p_str.split("/storage/", 1)[1]
    return f"/storage/{Path(p).name}"


def _find_episode_dir(episode_id: str, channel_id: Optional[str], user_id: str) -> Optional[Path]:
    norm_ep = str(episode_id).lower().strip()
    clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", norm_ep).strip("_")
    user_container = storage_service.get_user_container_path(user_id)
    scan_roots = []
    if channel_id:
        scan_roots.extend([storage_service.get_network_path(user_id, channel_id), user_container / "channels" / channel_id])
    else:
        scan_roots.extend([user_container / "networks", user_container / "channels", user_container / "productions"])

    target_names = {norm_ep, clean_ep, episode_id.strip()}

    for root in scan_roots:
        if not root.exists():
            continue
        for t in target_names:
            candidate = root / t
            if candidate.is_dir():
                return candidate
        try:
            for sub in root.rglob("*"):
                if sub.is_dir() and sub.name.lower() in target_names:
                    return sub
        except Exception as e:
            logger.warning(f"_find_episode_dir scan warning: {e}")
    return None


@router.post("/episodes/{episode_id}/generate-long-play")
async def generate_long_play_for_episode(episode_id: str, req: LongPlayStretchRequest):
    """Trigger background generation of dual long-play broadcasts (Ambient BGM + Pure Nature ASMR)."""
    target_dir = _find_episode_dir(episode_id, req.channel_id, req.user_id or "knpillutla@gmail.com")
    if not target_dir:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Episode {episode_id} directory not found.")

    ambient_src = target_dir / "master_4k_ambient.mp4"
    if not ambient_src.is_file():
        if (target_dir / "master_4k_ambient.mp4").is_file():
            ambient_src = target_dir / "master_4k_ambient.mp4"
        elif (target_dir / "master_4k_narration.mp4").is_file():
            ambient_src = target_dir / "master_4k_narration.mp4"
        else:
            masters = [f for f in target_dir.glob("master_4k*.mp4") if "hour" not in f.name and "short" not in f.name]
            ambient_src = masters[0] if masters else None

    if (target_dir / "master_4k_nature.mp4").is_file():
        nature_src = target_dir / "master_4k_nature.mp4"
    elif (target_dir / "master_4k_ambient_nature_only.mp4").is_file():
        nature_src = target_dir / "master_4k_ambient_nature_only.mp4"
    elif ambient_src and ambient_src.name == "master_4k_narration.mp4" and (target_dir / "master_4k_ambient.mp4").is_file():
        nature_src = target_dir / "master_4k_ambient.mp4"
    else:
        nature_src = None
    if not ambient_src or not ambient_src.is_file():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No 4K master video found on disk to stretch.")

    # Verify format: Long-play multi-hour broadcasts (3h/8h) are strictly for relaxation format productions
    user_inputs_file = target_dir / "user_inputs.json"
    if user_inputs_file.is_file():
        try:
            u_data = json.loads(user_inputs_file.read_text("utf-8"))
            ep_fmt = str(u_data.get("format", "")).lower()
            if ep_fmt and ep_fmt not in ("relaxation", "relax"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Long-play 3h broadcast is only supported for relaxation format productions (current: '{ep_fmt}').")
        except HTTPException:
            raise
        except Exception:
            pass

    # Mark episode as approved in manifest
    manifest_file = target_dir / "episode_manifest.json"
    m_data = {}
    if manifest_file.exists():
        try:
            m_data = json.loads(manifest_file.read_text("utf-8"))
        except Exception:
            pass
    m_data["is_approved"] = True
    m_data["long_play_hours"] = req.hours
    m_data["approved_at"] = time.time()
    manifest_file.write_text(json.dumps(m_data, indent=2), encoding="utf-8")

    hours_label = int(req.hours) if req.hours.is_integer() else req.hours
    suffix = f"_{int(req.fade_to_black_hours)}h_black" if req.fade_to_black_hours else ""
    out_ambient = target_dir / f"master_4k_{hours_label}hour{suffix}_broadcast.mp4"
    is_doc = ambient_src and ambient_src.name == "master_4k_narration.mp4"
    sec_suffix = "_music_only" if is_doc else "_nature_only"
    out_nature = target_dir / f"master_4k_{hours_label}hour{sec_suffix}{suffix}_broadcast.mp4"

    job_state = {
        "episode_id": episode_id,
        "hours": req.hours,
        "status": "processing",
        "ambient_progress": 15,
        "nature_progress": 15,
        "ambient_url": None,
        "nature_url": None,
        "error": None,
    }
    long_play_jobs[episode_id] = job_state
    long_play_jobs[episode_id.lower().strip()] = job_state

    async def _run_stretch():
        try:
            job_state["ambient_progress"] = 20
            await asyncio.to_thread(
                export_long_play_broadcast,
                source_4k_video=ambient_src,
                output_long_play=out_ambient,
                target_duration_seconds=req.hours * 3600.0,
                fade_to_black_hours=req.fade_to_black_hours,
            )
            job_state["ambient_progress"] = 60
            out_30m = target_dir / "master_4k_30min_broadcast.mp4"
            await asyncio.to_thread(
                export_long_play_broadcast,
                source_4k_video=ambient_src,
                output_long_play=out_30m,
                target_duration_seconds=1800.0,
            )
            job_state["ambient_progress"] = 100
            job_state["ambient_url"] = _to_storage_url(out_ambient)

            if nature_src and nature_src.is_file():
                job_state["nature_progress"] = 20
                await asyncio.to_thread(
                    export_long_play_broadcast,
                    source_4k_video=nature_src,
                    output_long_play=out_nature,
                    target_duration_seconds=req.hours * 3600.0,
                    fade_to_black_hours=req.fade_to_black_hours,
                )
                job_state["nature_progress"] = 60
                out_30m_nature = target_dir / f"master_4k_30min{sec_suffix}_broadcast.mp4"
                await asyncio.to_thread(
                    export_long_play_broadcast,
                    source_4k_video=nature_src,
                    output_long_play=out_30m_nature,
                    target_duration_seconds=1800.0,
                )
                job_state["nature_progress"] = 100
                job_state["nature_url"] = _to_storage_url(out_nature)
            else:
                job_state["nature_progress"] = 100

            job_state["status"] = "completed"
            logger.info(f"long_play_dual_stretch_finished: {episode_id} ({req.hours}h & 30min)")
        except Exception as err:
            logger.error(f"long_play_stretch_failed: {err}", exc_info=True)
            job_state["status"] = "failed"
            job_state["error"] = str(err)

    asyncio.create_task(_run_stretch())
    return {
        "success": True,
        "episode_id": episode_id,
        "status": "processing",
        "message": f"Generating {req.hours}-hour dual 4K broadcasts in background.",
    }


@router.get("/episodes/{episode_id}/long-play-status")
async def get_long_play_status(episode_id: str, channel_id: Optional[str] = None, user_id: str = "knpillutla@gmail.com"):
    """Get live progress and artifacts for dual long-play broadcast rendering."""
    norm_ep = episode_id.lower().strip()
    if norm_ep in long_play_jobs:
        return long_play_jobs[norm_ep]
    if episode_id in long_play_jobs:
        return long_play_jobs[episode_id]

    target_dir = _find_episode_dir(episode_id, channel_id, user_id)
    if target_dir:
        lp_files = list(target_dir.glob("master_4k_*hour*.mp4"))
        if lp_files:
            ambient_f = next((f for f in lp_files if "nature" not in f.name), lp_files[0])
            nature_f = next((f for f in lp_files if "nature" in f.name), None)
            return {
                "episode_id": episode_id,
                "status": "completed",
                "ambient_progress": 100,
                "nature_progress": 100 if nature_f else 0,
                "ambient_url": _to_storage_url(ambient_f),
                "nature_url": _to_storage_url(nature_f) if nature_f else None,
            }

    return {"episode_id": episode_id, "status": "idle", "ambient_progress": 0, "nature_progress": 0}
