"""Idempotent YouTube Publishing Pipeline for Completed Channel Episodes.

Supports background resumable upload, state tracking, custom title/description override,
and independent selection for Short and Broadcast Music master.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import googleapiclient.discovery

from src.core.telemetry import logger
from src.services.youtube_auth_service import get_channel_credentials
from src.services.youtube_upload_service import upload_single_video

PUBLISHED_MANIFEST = "youtube_published.json"
UPLOAD_STATE_FILE = "youtube_upload_state.json"


def get_episode_publish_status(ep_dir: Path) -> Dict[str, Any]:
    """Inspect local episode directory to check if assets have been published or are in-flight."""
    ep_dir = ep_dir.resolve()
    upload_state = {}
    state_path = ep_dir / UPLOAD_STATE_FILE
    if state_path.is_file():
        try: upload_state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception: pass

    manifest_path = ep_dir / PUBLISHED_MANIFEST
    if manifest_path.is_file() and manifest_path.stat().st_size > 10:
        try:
            pub_data = json.loads(manifest_path.read_text(encoding="utf-8"))
            return {**pub_data, "upload_state": upload_state, "upload_in_progress": False}
        except Exception: pass

    in_progress = upload_state.get("status") == "uploading"
    return {
        "published": False,
        "short": None,
        "broadcast": None,
        "upload_state": upload_state,
        "upload_in_progress": in_progress,
    }


def _write_state(ep_dir: Path, status: str, step: str, progress_pct: int = 0, error: str = "") -> None:
    """Persist background upload state to disk for cross-session resumption."""
    try:
        data = {
            "status": status,
            "step": step,
            "progress_pct": progress_pct,
            "updated_at": time.time(),
            "error": error,
        }
        (ep_dir / UPLOAD_STATE_FILE).write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception as e:
        logger.debug(f"failed_to_write_upload_state: {e}")


def publish_episode_bundle_idempotent(
    ep_dir: Path,
    channel_slug: str,
    privacy_status: str = "public",
    force_reupload: bool = False,
    custom_title: Optional[str] = None,
    custom_description: Optional[str] = None,
    custom_tags: Optional[List[str]] = None,
    short_title: Optional[str] = None,
    short_description: Optional[str] = None,
    upload_short: bool = True,
    upload_broadcast: bool = True,
) -> Dict[str, Any]:
    """Execute idempotent YouTube publication for Short and/or Broadcast Music master."""
    ep_dir = ep_dir.resolve()
    if not ep_dir.is_dir():
        raise FileNotFoundError(f"Episode directory not found: {ep_dir}")

    # Check idempotency per format
    existing_status = get_episode_publish_status(ep_dir)
    short_already_done = bool(existing_status.get("short"))
    broadcast_already_done = bool(existing_status.get("broadcast"))
    needed_short = upload_short and not (short_already_done and not force_reupload)
    needed_broadcast = upload_broadcast and not (broadcast_already_done and not force_reupload)

    if not needed_short and not needed_broadcast:
        logger.info(f"decision_youtube_publish_idempotent_hit: Episode in '{ep_dir.name}' already published")
        return {
            "status": "already_published",
            "message": "Selected video assets are already published on YouTube.",
            "data": existing_status,
        }

    creds = get_channel_credentials(channel_slug)
    if not creds:
        raise PermissionError(f"YouTube credentials not authorized for channel '{channel_slug}'.")

    yt = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

    # 1. Resolve Titles & Metadata
    yt_pkg_file = ep_dir / "youtube_packaging.json"
    screenplay_file = ep_dir / "screenplay.json"
    pkg_data: Dict[str, Any] = {}
    if yt_pkg_file.is_file():
        try: pkg_data = json.loads(yt_pkg_file.read_text(encoding="utf-8"))
        except Exception: pass
    elif screenplay_file.is_file():
        try:
            sp = json.loads(screenplay_file.read_text(encoding="utf-8"))
            pub = sp.get("publishing", {})
            pkg_data = {
                "seo_title": sp.get("title", "4K Ambient Sanctuary"),
                "description_with_timestamps": pub.get("description_with_timestamps", ""),
                "seo_tags": pub.get("seo_tags", ["ambient relaxation", "4k nature", "432hz"]),
            }
        except Exception: pass

    title = (custom_title or pkg_data.get("seo_title") or pkg_data.get("title") or ep_dir.name).strip()
    description = (custom_description or pkg_data.get("description_with_timestamps") or "Ultra HD 4K Ambient Experience.").strip()
    tags = custom_tags or pkg_data.get("seo_tags") or ["4k ambient", "sleep soundscape", "meditation 432hz"]

    # 2. Locate Thumbnail
    thumbnail_path = None
    for thumb_name in ["thumbnail_variant_a.jpg", "thumbnail_a.jpg", "keyframe_p1.jpg"]:
        candidate = ep_dir / thumb_name
        if candidate.is_file() and candidate.stat().st_size > 1000:
            thumbnail_path = candidate
            break

    # 3. Locate Broadcast Master (strictly music)
    broadcast_file = None
    for cand_name in ["master_4k_3hour_broadcast.mp4", "master_4k_30min_broadcast.mp4", "master_4k_ambient.mp4"]:
        cand = ep_dir / cand_name
        if cand.is_file() and cand.stat().st_size > 500000:
            broadcast_file = cand
            break

    # 4. Locate Short (9:16 vertical)
    short_file = None
    for cand_name in ["short_9x16_ambient.mp4", "short_ambient.mp4", "short_9x16_teaser.mp4"]:
        cand = ep_dir / cand_name
        if cand.is_file() and cand.stat().st_size > 100000:
            short_file = cand
            break

    # Auto-synthesize Short on-the-fly if missing and requested
    if upload_short and not short_file:
        src_master = broadcast_file or (ep_dir / "master_4k_ambient.mp4")
        if src_master and src_master.is_file():
            try:
                from src.services.ambient_shorts_extractor import generate_ambient_short
                target_short = ep_dir / "short_9x16_ambient.mp4"
                _write_state(ep_dir, "uploading", f"Synthesizing 9:16 Short from {src_master.name}...", 8)
                generate_ambient_short(source_4k_video=src_master, output_short_path=target_short, duration_seconds=20.0)
                if target_short.is_file():
                    short_file = target_short
            except Exception as e:
                logger.warning(f"auto_short_synthesis_failed: {e}")

    results: Dict[str, Any] = {
        "published": True,
        "published_at": time.time(),
        "channel_slug": channel_slug,
        "short": existing_status.get("short"),
        "broadcast": existing_status.get("broadcast"),
    }

    _write_state(ep_dir, "uploading", "Starting uploads...", 5)

    # Upload Short if selected
    if upload_short and short_file:
        s_title = (short_title or f"{title[:70]} #Shorts").strip()
        s_desc = (short_description or f"{description[:350]}\n\n#Shorts #Relaxation #Nature").strip()
        _write_state(ep_dir, "uploading", f"Uploading Short: {short_file.name}...", 10)
        res_short = upload_single_video(
            youtube_client=yt,
            video_path=short_file,
            title=s_title,
            description=s_desc,
            tags=list(set(tags + ["Shorts", "Relaxation"])),
            privacy_status=privacy_status,
            thumbnail_path=None,
        )
        results["short"] = {
            "video_id": res_short.get("id"),
            "url": f"https://youtube.com/shorts/{res_short.get('id')}" if res_short.get("id") else None,
            "title": s_title,
            "filename": short_file.name,
        }

    # Upload 4K Broadcast Master if selected
    if upload_broadcast and broadcast_file:
        def on_broadcast_pct(pct: int):
            mapped = int(20 + (pct * 0.75))
            _write_state(ep_dir, "uploading", f"Uploading 4K Broadcast ({pct}%)...", mapped)

        _write_state(ep_dir, "uploading", f"Uploading 4K Broadcast: {broadcast_file.name}...", 20)
        res_broadcast = upload_single_video(
            youtube_client=yt,
            video_path=broadcast_file,
            title=title[:100],
            description=description,
            tags=tags[:30],
            privacy_status=privacy_status,
            thumbnail_path=thumbnail_path,
            progress_callback=on_broadcast_pct,
        )
        results["broadcast"] = {
            "video_id": res_broadcast.get("id"),
            "url": f"https://youtu.be/{res_broadcast.get('id')}" if res_broadcast.get("id") else None,
            "title": title,
            "filename": broadcast_file.name,
        }

    # Persist publication manifest
    manifest_path = ep_dir / PUBLISHED_MANIFEST
    manifest_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    _write_state(ep_dir, "completed", "Uploads complete!", 100)
    logger.info(f"youtube_publication_manifest_saved: path='{manifest_path}'")

    return {
        "status": "success",
        "message": "Successfully published to YouTube.",
        "data": results,
    }


def start_background_publish(ep_dir: Path, channel_slug: str, **kwargs) -> Dict[str, Any]:
    """Launch publishing on a detached background thread and return immediately."""
    status = get_episode_publish_status(ep_dir)
    if status.get("upload_in_progress"):
        return {"status": "in_progress", "message": "Upload already in progress."}

    _write_state(ep_dir, "uploading", "Initializing background publisher...", 2)

    def _worker():
        try:
            publish_episode_bundle_idempotent(ep_dir=ep_dir, channel_slug=channel_slug, **kwargs)
        except Exception as e:
            logger.error(f"background_publish_failed: ep='{ep_dir.name}' error='{e}'")
            _write_state(ep_dir, "failed", f"Upload failed: {e}", 0, error=str(e))

    thread = threading.Thread(target=_worker, daemon=True)
    thread.start()
    return {"status": "started", "message": "YouTube upload started in background. Safe to close browser."}
