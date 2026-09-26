"""Scanner service to discover and structure channel episodes for the Video Hub."""

import json
from pathlib import Path
from typing import Any

CHANNELS_CONFIG: dict[str, dict[str, str]] = {
    "earth_serenade": {
        "id": "earth_serenade",
        "name": "Earth Serenade",
        "handle": "@EarthSerenade",
        "category": "Travel & Events",
        "icon": "fa-mountain-sun",
        "color": "emerald",
        "desc": "Alpine & Mountain Sanctuaries, Pristine Lakes & Nature Retreats",
    },
    "silent_hearth": {
        "id": "silent_hearth",
        "name": "Silent Hearth",
        "handle": "@SilentHearthSleep",
        "category": "Music",
        "icon": "fa-fire-flame-curved",
        "color": "amber",
        "desc": "Cozy Shelters, Hearth Fireplaces, Campfires & Deep Sleep ASMR",
    },
    "telugu_comedy": {
        "id": "telugu_comedy",
        "name": "Telugu Comedy Hub",
        "handle": "@telugucomedyhub",
        "category": "Entertainment",
        "icon": "fa-masks-theater",
        "color": "purple",
        "desc": "Telugu Satire, Office Skits & Cultural Comedy Series",
    },
    "cineai_docs": {
        "id": "cineai_docs",
        "name": "CineAI Docs",
        "handle": "@cineai_docs",
        "category": "Education",
        "icon": "fa-compass",
        "color": "blue",
        "desc": "Blue-Chip Wildlife, Natural Wonders & Ocean Science",
    },
}


def scan_all_channel_episodes(storage_dir: Path) -> list[dict[str, Any]]:
    """Scan disk directory structure to return comprehensive metadata for all episodes."""
    episodes: list[dict[str, Any]] = []
    channels_dir = storage_dir / "channels"
    if not channels_dir.exists():
        return episodes

    for ch_path in channels_dir.iterdir():
        if not ch_path.is_dir():
            continue
        ch_key = ch_path.name
        ch_meta = CHANNELS_CONFIG.get(
            ch_key,
            {
                "id": ch_key,
                "name": ch_key.replace("_", " ").title(),
                "handle": f"@{ch_key}",
                "category": "General",
                "icon": "fa-clapperboard",
                "color": "indigo",
                "desc": "Autonomous Video Channel",
            },
        )

        for ep_path in ch_path.iterdir():
            if not ep_path.is_dir() or not ep_path.name.startswith("ep_"):
                continue
            ep_dict = _build_episode_record(ep_path, ch_meta)
            if ep_dict:
                episodes.append(ep_dict)

    # Sort DESC by created_at timestamp
    episodes.sort(key=lambda x: x.get("created_timestamp", 0), reverse=True)
    return episodes


def _build_episode_record(ep_path: Path, ch_meta: dict[str, str]) -> dict[str, Any]:
    """Extract metadata, stage milestones, files, models, and packaging for one episode."""
    ep_id = ep_path.name
    files = {f.name: f for f in ep_path.iterdir() if f.is_file()}

    # Load packaging JSONs if present
    yt_pack = {}
    if "youtube_packaging.json" in files:
        try:
            yt_pack = json.loads(files["youtube_packaging.json"].read_text(encoding="utf-8"))
        except Exception:
            pass

    yt_pack_nature = {}
    if "youtube_packaging_nature_only.json" in files:
        try:
            yt_pack_nature = json.loads(
                files["youtube_packaging_nature_only.json"].read_text(encoding="utf-8")
            )
        except Exception:
            pass

    # Determine titles and topic
    title = yt_pack.get("title") or ep_id.replace("ep_", "").replace("_", " ").title()
    desc = yt_pack.get("description", "")
    category = ch_meta["category"]

    # Timestamps
    stat = ep_path.stat()
    created_ts = stat.st_ctime
    updated_ts = stat.st_mtime
    from datetime import datetime, timezone

    created_iso = datetime.fromtimestamp(created_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    updated_iso = datetime.fromtimestamp(updated_ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Stages and File Deliverables Check
    has_p1 = "keyframe_p1.jpg" in files
    has_motion = "motion_p1.mp4" in files
    has_ambient_master = "master_4k_ambient.mp4" in files
    has_nature_master = "master_4k_ambient_nature_only.mp4" in files
    has_3h = "master_4k_3hour_broadcast.mp4" in files
    has_8h = "master_4k_8hour_broadcast.mp4" in files
    has_8h_nature = "master_4k_8hour_nature_only_broadcast.mp4" in files
    has_short = "short_9x16_teaser.mp4" in files

    # Duration calculation
    duration_str = "90s (Master)"
    if has_8h:
        duration_str = "8:00:00 (8 Hours)"
    elif has_3h:
        duration_str = "3:00:00 (3 Hours)"

    # Status
    status = "completed"
    if has_8h or has_3h:
        status = "published"
    elif has_ambient_master:
        status = "pending_review"
    elif has_motion:
        status = "processing"
    elif has_p1:
        status = "queued"

    # Stage flags
    stages = {
        "stage_1_keyframes": has_p1,
        "stage_2_cineloop_masters": has_ambient_master,
        "stage_3_crf22_compression": has_ambient_master,
        "stage_4_long_play_stretch": has_8h or has_3h,
        "stage_5_short_teaser": has_short,
    }

    # Relative URL paths for static serving
    rel_prefix = f"/storage/channels/{ch_meta['id']}/{ep_id}"
    artifacts = {
        "master_music": f"{rel_prefix}/master_4k_ambient.mp4" if has_ambient_master else None,
        "master_nature": f"{rel_prefix}/master_4k_ambient_nature_only.mp4" if has_nature_master else None,
        "broadcast_8h_music": f"{rel_prefix}/master_4k_8hour_broadcast.mp4" if has_8h else None,
        "broadcast_8h_nature": f"{rel_prefix}/master_4k_8hour_nature_only_broadcast.mp4" if has_8h_nature else None,
        "broadcast_3h_music": f"{rel_prefix}/master_4k_3hour_broadcast.mp4" if has_3h else None,
        "short_teaser": f"{rel_prefix}/short_9x16_teaser.mp4" if has_short else None,
        "thumbnail_p1": f"{rel_prefix}/keyframe_p1.jpg" if has_p1 else None,
        "thumbnail_p2": f"{rel_prefix}/keyframe_p2.jpg" if "keyframe_p2.jpg" in files else None,
        "thumbnail_p3": f"{rel_prefix}/keyframe_p3.jpg" if "keyframe_p3.jpg" in files else None,
        "audio_master": f"{rel_prefix}/velvet_binaural_master_48k.mp3" if "velvet_binaural_master_48k.mp3" in files else None,
    }

    return {
        "episode_id": ep_id,
        "channel_id": ch_meta["id"],
        "channel_name": ch_meta["name"],
        "channel_handle": ch_meta["handle"],
        "channel_icon": ch_meta["icon"],
        "channel_color": ch_meta["color"],
        "title": title,
        "description": desc,
        "category": category,
        "status": status,
        "audio_mode": "Dual (Music + Pure Nature)" if (has_ambient_master and has_nature_master) else "Music Master",
        "duration": duration_str,
        "cost_usd": 2.20 if (has_8h or has_3h) else 0.14,
        "models_used": {
            "scripting": "Gemini 2.5 Pro",
            "visuals": "FLUX.1 Dev (Fal)",
            "motion": "Kling v3 Pro (48kHz Stereo)",
            "audio": "Suno v3.5 + Kling Field DSP",
            "encoding": "Single-Pass FFmpeg CRF 22",
        },
        "stages": stages,
        "created_at": created_iso,
        "updated_at": updated_iso,
        "created_timestamp": created_ts,
        "created_by": "AI Studio Autonomous Producer",
        "artifacts": artifacts,
        "youtube_packaging": yt_pack,
        "youtube_packaging_nature_only": yt_pack_nature,
    }
