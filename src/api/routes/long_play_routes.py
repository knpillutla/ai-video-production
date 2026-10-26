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
from src.services.long_play_stretcher import export_long_play_broadcast, remux_long_play_audio

router = APIRouter(prefix="/api/production", tags=["Long-Play Broadcast Engine"])

# In-memory progress tracking for long-play rendering jobs
long_play_jobs: dict[str, dict[str, Any]] = {}


class LongPlayStretchRequest(BaseModel):
    channel_id: Optional[str] = None
    production_name: Optional[str] = None
    storage_path: Optional[str] = None
    hours: float = Field(3.0, description="Target duration in hours (1.0, 3.0, or 8.0)")
    fade_to_black_hours: Optional[float] = None
    user_id: Optional[str] = "knpillutla@gmail.com"


def _to_storage_url(p: Path | str) -> str:
    p_str = str(p).replace("\\", "/")
    if "/storage/" in p_str:
        return "/storage/" + p_str.split("/storage/", 1)[1]
    return f"/storage/{Path(p).name}"


def _find_episode_dir(
    episode_id: str,
    channel_id: Optional[str] = None,
    user_id: str = "knpillutla@gmail.com",
    production_name: Optional[str] = None,
    storage_path: Optional[str] = None,
) -> Optional[Path]:
    if storage_path:
        sp = Path(storage_path)
        if sp.is_dir():
            return sp
        clean_sp = storage_path.replace("\\", "/").lstrip("/")
        if (Path("storage") / clean_sp).is_dir():
            return Path("storage") / clean_sp

    direct = Path(episode_id)
    if direct.is_dir():
        return direct
    if (Path("storage") / episode_id.replace("\\", "/").lstrip("/")).is_dir():
        return Path("storage") / episode_id.replace("\\", "/").lstrip("/")

    user_container = storage_service.get_user_container_path(user_id)
    scan_roots = []
    if channel_id:
        scan_roots.extend([storage_service.get_network_path(user_id, channel_id), user_container / "channels" / channel_id])
    else:
        scan_roots.extend([user_container / "networks", user_container / "channels", user_container / "productions"])

    norm_ep = str(episode_id).lower().strip()
    clean_ep = re.sub(r"[^a-zA-Z0-9_-]", "_", norm_ep).strip("_")
    target_names = {norm_ep, clean_ep, episode_id.strip()}

    if production_name:
        prod_clean = re.sub(r"[^a-zA-Z0-9_-]", "_", production_name.lower().strip()).strip("_")
        for root in scan_roots:
            if not root.exists():
                continue
            for sub in root.rglob("*"):
                if sub.is_dir() and prod_clean in sub.name.lower():
                    for t in target_names:
                        if (sub / t).is_dir():
                            return sub / t
                    return sub

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
    target_dir = _find_episode_dir(
        episode_id,
        channel_id=req.channel_id,
        user_id=req.user_id or "knpillutla@gmail.com",
        production_name=req.production_name,
        storage_path=req.storage_path,
    )
    if not target_dir:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Episode {episode_id} directory not found.")

    ambient_src = target_dir / "master_4k_ambient.mp4"
    if not ambient_src.is_file():
        masters = [f for f in target_dir.glob("master_4k*.mp4") if "hour" not in f.name and "short" not in f.name]
        ambient_src = masters[0] if masters else None

    nature_src = target_dir / "master_4k_nature.mp4"
    if not nature_src.is_file():
        for cand in [target_dir / "master_4k_ambient_nature_only.mp4", target_dir / "master_4k_ambient.mp4"]:
            if cand.is_file() and cand != ambient_src:
                nature_src = cand
                break
        else:
            nature_src = None
    if not ambient_src or not ambient_src.is_file():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No 4K master video found on disk to stretch.")

    # Verify format: Long-play multi-hour broadcasts (3h/8h) are strictly for relaxation format productions
    ep_genre, ep_fmt = "", ""
    for meta_p in [target_dir / "user_inputs.json", target_dir / "episode_manifest.json"]:
        if meta_p.is_file():
            try:
                d = json.loads(meta_p.read_text("utf-8"))
                ep_fmt = ep_fmt or str(d.get("format", "")).lower()
                ep_genre = ep_genre or str(d.get("genre", "")).lower()
            except Exception:
                pass

    is_relax = (
        ep_fmt in ("relaxation", "relax")
        or ep_fmt.startswith("relax")
        or ep_genre.startswith("relax")
        or "relax" in ep_genre
        or "/relaxation/" in target_dir.as_posix().lower()
        or "\\relaxation\\" in target_dir.as_posix().lower()
    )
    if not is_relax and ep_fmt and ep_fmt not in ("relaxation", "relax"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Long-play 3h broadcast is only supported for relaxation format productions (current: '{ep_fmt}', genre: '{ep_genre}')."
        )

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
            target_sec = req.hours * 3600.0
            primary_src = nature_src if (nature_src and nature_src.is_file()) else ambient_src
            primary_out = out_nature if (nature_src and nature_src.is_file()) else out_ambient
            secondary_src = ambient_src if (nature_src and nature_src.is_file()) else nature_src
            secondary_out = out_ambient if (nature_src and nature_src.is_file()) else out_nature

            primary_is_nat = (primary_out == out_nature)
            if primary_is_nat:
                job_state["nature_progress"] = 30
            else:
                job_state["ambient_progress"] = 30

            # 1. Generate Primary 4K Broadcast
            if not primary_out.is_file() or primary_out.stat().st_size < 1000:
                await asyncio.to_thread(
                    export_long_play_broadcast,
                    source_4k_video=primary_src,
                    output_long_play=primary_out,
                    target_duration_seconds=target_sec,
                    fade_to_black_hours=req.fade_to_black_hours,
                )

            if primary_is_nat:
                job_state["nature_progress"] = 100
                job_state["nature_url"] = _to_storage_url(out_nature)
            else:
                job_state["ambient_progress"] = 100
                job_state["ambient_url"] = _to_storage_url(out_ambient)

            # 2. Fast Audio Remux for Secondary Edition (under 60s)
            if secondary_src and secondary_src.is_file():
                if primary_is_nat:
                    job_state["ambient_progress"] = 40
                else:
                    job_state["nature_progress"] = 40

                if not secondary_out.is_file() or secondary_out.stat().st_size < 1000:
                    await asyncio.to_thread(
                        remux_long_play_audio,
                        source_long_play_video=primary_out,
                        alternate_audio_source=secondary_src,
                        output_long_play=secondary_out,
                        target_duration_seconds=target_sec,
                    )

                if primary_is_nat:
                    job_state["ambient_progress"] = 100
                    job_state["ambient_url"] = _to_storage_url(out_ambient)
                else:
                    job_state["nature_progress"] = 100
                    job_state["nature_url"] = _to_storage_url(out_nature)
            else:
                job_state["ambient_progress"] = 100
                job_state["nature_progress"] = 100

            job_state["status"] = "completed"
            logger.info(f"long_play_dual_stretch_finished: {episode_id} ({req.hours}h)")
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
