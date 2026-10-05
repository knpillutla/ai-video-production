"""Channel YouTube Credentials, OAuth Authorization & Publishing API routes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.core.telemetry import logger
from src.domain.user import User
from src.services.youtube_auth_service import (
    disconnect_channel,
    get_auth_status,
    save_client_secret,
    authorize_channel_local_flow,
)
from src.services.youtube_publish_pipeline import (
    get_episode_publish_status,
    publish_episode_bundle_idempotent,
    start_background_publish,
)

router = APIRouter(prefix="/api/channels", tags=["YouTube OAuth & Publishing"])


class PublishRequest(BaseModel):
    privacy_status: str = "public"  # public, unlisted, private
    force_reupload: bool = False
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    short_title: Optional[str] = None
    short_description: Optional[str] = None
    upload_short: bool = True
    upload_broadcast: bool = True


@router.get("/{channel_slug}/youtube/auth-status")
async def get_channel_youtube_status(
    channel_slug: str,
    current_user: User = Depends(get_current_user),
):
    """Retrieve verified YouTube authorization status and channel details."""
    status_data = get_auth_status(channel_slug)
    return {"status": "ok", "channel_slug": channel_slug, **status_data}


@router.post("/{channel_slug}/youtube/credentials")
async def upload_channel_credentials(
    channel_slug: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """Upload Google OAuth client_secret_*.json for this channel."""
    content = await file.read()
    try:
        import json
        parsed = json.loads(content)
        if "installed" not in parsed and "web" not in parsed:
            raise ValueError("Invalid client_secret.json: missing 'installed' or 'web' block.")
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OAuth client secret JSON: {err}",
        )

    saved_path = save_client_secret(channel_slug, content)
    return {
        "status": "ok",
        "message": f"Client secrets saved for '{channel_slug}'",
        "path": str(saved_path),
    }


@router.post("/{channel_slug}/youtube/authorize")
async def authorize_channel_oauth(
    channel_slug: str,
    current_user: User = Depends(get_current_user),
):
    """Launch local OAuth 2.0 authorization server to authorize with Google."""
    try:
        auth_info = authorize_channel_local_flow(channel_slug)
        return {"status": "ok", "message": "Successfully authorized with Google!", **auth_info}
    except FileNotFoundError as fnf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(fnf))
    except Exception as err:
        logger.error(f"oauth_flow_failed: channel='{channel_slug}' error='{err}'")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"OAuth failed: {err}")


@router.delete("/{channel_slug}/youtube/disconnect")
async def disconnect_channel_oauth(
    channel_slug: str,
    current_user: User = Depends(get_current_user),
):
    """Revoke and delete the stored YouTube authorization token."""
    disconnected = disconnect_channel(channel_slug)
    return {"status": "ok", "disconnected": disconnected}


@router.get("/{channel_slug}/episodes/{episode_id}/publish-status")
async def get_publish_status(
    channel_slug: str,
    episode_id: str,
    current_user: User = Depends(get_current_user),
):
    """Check if the episode has already been published to YouTube."""
    storage_root = Path(__file__).resolve().parent.parent.parent.parent / "storage"
    ep_dir = storage_root / f"user-{current_user.email.replace('@', '-').replace('.', '-')}" / "channels" / channel_slug / episode_id
    if not ep_dir.is_dir():
        # Also check without sanitized email
        ep_dir = storage_root / "channels" / channel_slug / episode_id

    pub_status = get_episode_publish_status(ep_dir) if ep_dir.is_dir() else {"published": False}
    auth_info = get_auth_status(channel_slug)
    return {
        "status": "ok",
        "episode_id": episode_id,
        "channel_slug": channel_slug,
        "youtube_authorized": auth_info.get("authorized", False),
        "channel_title": auth_info.get("channel_title"),
        **pub_status,
    }


@router.post("/{channel_slug}/episodes/{episode_id}/publish")
async def publish_episode_to_youtube(
    channel_slug: str,
    episode_id: str,
    req: PublishRequest,
    current_user: User = Depends(get_current_user),
):
    """Idempotently upload Short and 4K Broadcast Music master to YouTube."""
    auth_info = get_auth_status(channel_slug)
    if not auth_info.get("authorized"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"YouTube credentials not authorized for channel '{channel_slug}'. Please connect your YouTube account first.",
        )

    storage_root = Path(__file__).resolve().parent.parent.parent.parent / "storage"
    ep_dir = storage_root / f"user-{current_user.email.replace('@', '-').replace('.', '-')}" / "channels" / channel_slug / episode_id
    if not ep_dir.is_dir():
        ep_dir = storage_root / "channels" / channel_slug / episode_id

    if not ep_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode directory not found on disk: {ep_dir}",
        )

    try:
        res = start_background_publish(
            ep_dir=ep_dir,
            channel_slug=channel_slug,
            privacy_status=req.privacy_status,
            force_reupload=req.force_reupload,
            custom_title=req.title,
            custom_description=req.description,
            custom_tags=req.tags,
            short_title=req.short_title,
            short_description=req.short_description,
            upload_short=req.upload_short,
            upload_broadcast=req.upload_broadcast,
        )
        return {"status": "ok", **res}
    except Exception as err:
        err_str = str(err)
        logger.error(f"failed_to_publish_episode: ep='{episode_id}' error='{err}'")
        if "authenticatedUserAccountSuspended" in err_str:
            detail = "Google reports: The YouTube account selected during authorization has no active channel or is suspended. Please verify your channel at https://studio.youtube.com, then disconnect and re-authorize, selecting your active Brand Account channel."
            status_code = status.HTTP_403_FORBIDDEN
        else:
            detail = f"Failed to publish to YouTube: {err_str}"
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(status_code=status_code, detail=detail)
