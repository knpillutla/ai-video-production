"""Reusable YouTube Video Upload Service with Dual Packaging & Chunked Resumable Upload.

Supports Brand Account OAuth credential loading, automatic token refresh, chunked resumable upload,
thumbnail attachment, synthetic media disclosure, and dual Music/Nature package deployment.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

load_dotenv()

from src.core.telemetry import logger

SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtubepartner",
]


def get_youtube_client(
    channel_key: str,
    secrets_path: Path = Path("config/youtube_client_secret.json"),
    tokens_dir: Path = Path("config/tokens"),
):
    """Authenticate and return an authorized YouTube API service resource."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    import googleapiclient.discovery

    secrets_file = secrets_path.resolve()
    tokens_path = tokens_dir.resolve()
    tokens_path.mkdir(parents=True, exist_ok=True)
    token_file = tokens_path / f"token_{channel_key}.json"

    if not secrets_file.is_file():
        raise FileNotFoundError(f"Client secrets file not found at: {secrets_file}")

    creds = None
    if token_file.is_file():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if not creds or not creds.valid:
        refreshed = False
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                refreshed = True
            except Exception as err:
                print(f"\n[AUTH NOTICE] Stale token could not be refreshed ({err}). Re-authorizing via browser...")
                if token_file.is_file():
                    token_file.unlink(missing_ok=True)
        
        if not refreshed:
            print(f"\n🌐 Opening browser for YouTube OAuth authorization for '{channel_key}'...")
            print("👉 Please select your Google Account / Brand Account in the browser window.\n")
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_file), SCOPES)
            creds = flow.run_local_server(port=0, prompt="select_account consent")

        token_file.write_text(creds.to_json(), encoding="utf-8")
        print(f"[AUTH SUCCESS] Token saved to: {token_file.name}")

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_single_video(
    youtube_client: Any,
    video_path: Path,
    title: str,
    description: str,
    tags: List[str],
    privacy_status: str = "unlisted",
    thumbnail_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """Perform chunked resumable upload for a single video file."""
    if dry_run:
        print(f"\n[DRY RUN] Would upload: {video_path.name}")
        print(f"   * Title:   {title[:95]}")
        print(f"   * Privacy: {privacy_status}")
        print(f"   * Tags:    {', '.join(tags[:8])}...")
        return {"id": "dry_run_id", "status": "simulated", "url": "https://youtube.com/watch?v=dry_run"}

    from googleapiclient.http import MediaFileUpload

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:5000],
            "tags": tags[:30],
            "categoryId": "24",  # Entertainment / Relaxation
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
        },
        "contentDetails": {
            "containsSyntheticMedia": True,
        },
    }

    media = MediaFileUpload(str(video_path), chunksize=1024 * 1024 * 8, resumable=True)
    request = youtube_client.videos().insert(part="snippet,status,contentDetails", body=body, media_body=media)

    print(f"\n[UPLOADING] {video_path.name} ({video_path.stat().st_size / (1024*1024):.1f} MB)...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"   ... Upload progress: {pct}%")

    video_id = response.get("id")
    video_url = f"https://youtu.be/{video_id}"
    print(f"   [UPLOAD COMPLETE] Video ID: {video_id} -> {video_url}")

    # Set Custom Thumbnail if available
    if thumbnail_path and thumbnail_path.is_file():
        try:
            thumb_media = MediaFileUpload(str(thumbnail_path))
            youtube_client.thumbnails().set(videoId=video_id, media_body=thumb_media).execute()
            print(f"   [THUMBNAIL SET] Applied: {thumbnail_path.name}")
        except Exception as e:
            logger.warning(f"thumbnail_upload_failed: {e}")
            print(f"   [THUMBNAIL WARNING] Could not set thumbnail: {e}")

    return {"id": video_id, "status": "uploaded", "url": video_url}


def upload_channel_episode(
    channel_key: str,
    channel_name: str,
    episode_dir: Path,
    privacy_status: str = "unlisted",
    dry_run: bool = False,
    upload_short: bool = True,
) -> Dict[str, Any]:
    """Inspect episode directory and upload Music Master, Nature-Only Master, and Short."""
    ep_dir = episode_dir.resolve()
    if not ep_dir.is_dir():
        raise FileNotFoundError(f"Episode directory not found: {ep_dir}")

    print("\n" + "=" * 70)
    print(f"[CHANNEL UPLOAD INITIALIZED] Channel: {channel_name} ({channel_key})")
    print(f"Episode Directory: {ep_dir}")
    print(f"Target Privacy:    {privacy_status}")
    print("=" * 70)

    client = None if dry_run else get_youtube_client(channel_key)
    results = {}

    # 1. Locate Master Video Files
    music_long = sorted(list(ep_dir.glob("master_4k_*broadcast.mp4")))
    nature_long = sorted(list(ep_dir.glob("master_4k_*nature_only*broadcast.mp4")))
    
    # Filter out nature from music list
    music_long = [f for f in music_long if "nature_only" not in f.name]
    
    music_vid = music_long[0] if music_long else (ep_dir / "master_4k_ambient.mp4")
    nature_vid = nature_long[0] if nature_long else (ep_dir / "master_4k_ambient_nature_only.mp4")
    short_vid = ep_dir / "short_9x16_teaser.mp4"
    thumb_img = ep_dir / "keyframe_p1.jpg"

    total_uploads = 0
    if music_vid.is_file(): total_uploads += 1
    if nature_vid.is_file(): total_uploads += 1
    if upload_short and short_vid.is_file(): total_uploads += 1
    curr_idx = 1

    # 2. Upload Version A (Music Master)
    pkg_file = ep_dir / "youtube_packaging.json"
    pkg = json.loads(pkg_file.read_text(encoding="utf-8")) if pkg_file.is_file() else {}
    if music_vid.is_file():
        print(f"\n> [{curr_idx}/{total_uploads}] Uploading Version A: Music Master ({music_vid.name})...")
        res_a = upload_single_video(
            youtube_client=client,
            video_path=music_vid,
            title=pkg.get("title", ep_dir.name),
            description=pkg.get("description", ""),
            tags=pkg.get("tags", []),
            privacy_status=privacy_status,
            thumbnail_path=thumb_img,
            dry_run=dry_run,
        )
        results["music_version"] = res_a
        curr_idx += 1

    # 3. Upload Version B (Pure Nature Master - No Music)
    pkg_nature_file = ep_dir / "youtube_packaging_nature_only.json"
    if nature_vid.is_file() and pkg_nature_file.is_file() and nature_vid.resolve() != music_vid.resolve():
        pkg_nat = json.loads(pkg_nature_file.read_text(encoding="utf-8"))
        print(f"\n> [{curr_idx}/{total_uploads}] Uploading Version B: Pure Nature Master ({nature_vid.name})...")
        res_b = upload_single_video(
            youtube_client=client,
            video_path=nature_vid,
            title=pkg_nat.get("title", f"{ep_dir.name} Pure Nature"),
            description=pkg_nat.get("description", ""),
            tags=pkg_nat.get("tags", []),
            privacy_status=privacy_status,
            thumbnail_path=thumb_img,
            dry_run=dry_run,
        )
        results["nature_version"] = res_b
        curr_idx += 1

    # 4. Upload Vertical 9:16 Teaser Short (Automated by Default)
    if upload_short and short_vid.is_file():
        base_short_title = pkg.get("title", ep_dir.name).split("~")[0].strip()
        short_title = f"{base_short_title[:65]} #Shorts #Relaxation"
        
        # Derive specific high-volume Short tags & channel handle
        base_tags = pkg.get("tags", [])
        short_tags = ["Shorts", "4KShorts", channel_name.replace(" ", ""), "NatureShorts", "Relaxation", "DeepSleep", "ASMR", "Soundscape", "432Hz"]
        for t in base_tags:
            if t not in short_tags and len(short_tags) < 25:
                short_tags.append(t)

        short_desc = (
            f"🌿 Put on headphones for instant calm, stress relief, and deep sleep.\n\n"
            f"✨ Watch the full 3-Hour 4K Broadcast on our channel @{channel_name.replace(' ', '')}!\n\n"
            f"#Shorts #Nature #Sleep #Relaxation #4K #ASMR #Soundscape #432Hz"
        )

        print(f"\n> [{curr_idx}/{total_uploads}] Uploading Vertical Teaser Short ({short_vid.name})...")
        res_s = upload_single_video(
            youtube_client=client,
            video_path=short_vid,
            title=short_title,
            description=short_desc,
            tags=short_tags,
            privacy_status=privacy_status,
            dry_run=dry_run,
        )
        results["short_version"] = res_s

    print("\n" + "=" * 70)
    print(f"[SUMMARY] Channel '{channel_name}' Uploads Complete ({len(results)} videos deployed)!")
    for k, v in results.items():
        print(f"   * {k}: {v.get('url', 'N/A')}")
    print("=" * 70 + "\n")
    return results
