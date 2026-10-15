"""Channel YouTube Credentials, OAuth Authorization & Publishing API routes."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
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
    nature_title: Optional[str] = None
    nature_description: Optional[str] = None
    nature_tags: Optional[List[str]] = None
    short_title: Optional[str] = None
    short_description: Optional[str] = None
    upload_short: bool = True
    upload_broadcast: bool = True
    upload_nature: bool = True
    target_channel_slug: Optional[str] = None

PublishRequest.model_rebuild()


@router.get("/{channel_slug}/youtube/accounts")
async def list_channel_youtube_accounts(
    channel_slug: str,
    current_user: User = Depends(get_current_user),
):
    """List all attached YouTube accounts for this network with verified live auth status."""
    from src.domain.repo import repo
    channel = repo.get_channel(current_user.id, channel_slug)
    linked = getattr(channel, "linked_youtube_channels", None) or []
    if not linked:
        linked = [{
            "id": "default",
            "name": getattr(channel, "channel_name", channel_slug) or channel_slug,
            "slug": channel_slug,
            "is_default": True,
        }]

    accounts = []
    for item in linked:
        sub_slug = item.get("slug") or channel_slug
        auth_data = get_auth_status(sub_slug)
        accounts.append({
            "id": item.get("id") or sub_slug,
            "name": item.get("name") or auth_data.get("channel_title") or sub_slug,
            "slug": sub_slug,
            "is_default": item.get("is_default", False),
            **auth_data,
        })
    return {"status": "ok", "network_slug": channel_slug, "accounts": accounts}


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


def _find_episode_path(storage_root: Path, user_email: str, channel_slug: str, episode_id: str) -> Optional[Path]:
    """Robustly resolve episode path across flat channels and hierarchical network trees."""
    norm_ep = episode_id.lower().strip()
    target_names = {norm_ep, re.sub(r"[^a-zA-Z0-9_-]", "_", norm_ep).strip("_"), episode_id.strip()}
    clean_user = f"user-{user_email.replace('@', '-').replace('.', '-')}" if user_email else "user-knpillutla-gmail-com"

    candidate_roots = [
        storage_root / clean_user / "networks" / channel_slug,
        storage_root / clean_user / "channels" / channel_slug,
        storage_root / "user-knpillutla-gmail-com" / "networks" / channel_slug,
        storage_root / "user-knpillutla-gmail-com" / "channels" / channel_slug,
        storage_root / "networks" / channel_slug,
        storage_root / "channels" / channel_slug,
    ]
    for root in candidate_roots:
        if not root.is_dir():
            continue
        for t in target_names:
            cand = root / t
            if cand.is_dir():
                return cand
        try:
            for sub in root.rglob("*"):
                if sub.is_dir() and sub.name.lower() in target_names:
                    return sub
        except Exception:
            pass

    # Fallback scan across all networks/channels for this user
    fallback_roots = [
        storage_root / clean_user / "networks",
        storage_root / clean_user / "channels",
        storage_root / "user-knpillutla-gmail-com" / "networks",
        storage_root / "user-knpillutla-gmail-com" / "channels",
    ]
    for fb in fallback_roots:
        if not fb.is_dir():
            continue
        try:
            for sub in fb.rglob("*"):
                if sub.is_dir() and sub.name.lower() in target_names:
                    return sub
        except Exception:
            pass
    return None


@router.get("/{channel_slug}/episodes/{episode_id}/publish-status")
async def get_publish_status(
    channel_slug: str,
    episode_id: str,
    target_slug: Optional[str] = None,
    current_user: User = Depends(get_current_user),
):
    """Check if the episode has already been published to YouTube."""
    storage_root = Path(__file__).resolve().parent.parent.parent.parent / "storage"
    ep_dir = _find_episode_path(storage_root, current_user.email, channel_slug, episode_id)
    pub_status = get_episode_publish_status(ep_dir) if ep_dir and ep_dir.is_dir() else {"published": False}
    eff_auth_slug = target_slug or channel_slug
    auth_info = get_auth_status(eff_auth_slug)
    return {
        "status": "ok",
        "episode_id": episode_id,
        "channel_slug": eff_auth_slug,
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
    """Idempotently upload Short and 4K Broadcast Music master to selected YouTube channel."""
    eff_slug = req.target_channel_slug or channel_slug
    auth_info = get_auth_status(eff_slug)
    if not auth_info.get("authorized"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"YouTube credentials not authorized for target channel '{eff_slug}'. Please connect your YouTube account first.",
        )

    storage_root = Path(__file__).resolve().parent.parent.parent.parent / "storage"
    ep_dir = _find_episode_path(storage_root, current_user.email, channel_slug, episode_id)

    if not ep_dir or not ep_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Episode directory not found on disk for '{episode_id}' in channel '{channel_slug}'.",
        )

    try:
        res = start_background_publish(
            ep_dir=ep_dir,
            channel_slug=eff_slug,
            privacy_status=req.privacy_status,
            force_reupload=req.force_reupload,
            custom_title=req.title,
            custom_description=req.description,
            custom_tags=req.tags,
            nature_title=req.nature_title,
            nature_description=req.nature_description,
            nature_tags=req.nature_tags,
            short_title=req.short_title,
            short_description=req.short_description,
            upload_short=req.upload_short,
            upload_broadcast=req.upload_broadcast,
            upload_nature=req.upload_nature,
        )
        return {"status": "ok", "target_channel_slug": eff_slug, **res}
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
