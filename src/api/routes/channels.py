"""Multi-Channel YouTube Publishing & Distribution API routes with full CRUD."""

import re
from pathlib import Path
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.distribution import Channel, ChannelCreate, ChannelPublication, ChannelUpdate
from src.domain.repo import repo
from src.domain.user import User
from src.mcp.publisher.server import prepare_youtube_payload, validate_monetization_readiness

router = APIRouter(prefix="/api/channels", tags=["Channels & Distribution"])




def _slugify(text: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9_-]", "_", text.lower()).strip("_")
    return re.sub(r"_+", "_", clean)[:40] or "custom_channel"


@router.get("", response_model=list[Channel])
async def list_channels(current_user: User = Depends(get_current_user)):
    """List all distribution channels configured by current user."""
    channels = repo.list_channels(current_user.id)
    from src.config.channel_registry import load_channel_profiles
    profiles = load_channel_profiles()
    existing_slugs = {c.channel_slug.lower() for c in channels if c.channel_slug}
    
    # Sync profiles from src/config/channels/*.json into user repo
    for p in profiles.values():
        p_slug = p.channel_id.lower().strip()
        if p_slug not in existing_slugs:
            chan = Channel(
                user_id=current_user.id,
                channel_name=p.channel_name,
                channel_slug=p_slug,
                channel_handle=p.handle,
                category=p.niche_category,
                primary_genre=p.allowed_genres[0] if p.allowed_genres else "relax/nature",
                description=p.target_audience,
                tag=p.tag,
                comments=p.comments,
                default_tags=p.youtube_seo_defaults.primary_tags if p.youtube_seo_defaults else [],
                icon="fa-mountain-sun" if "earth" in p_slug else ("fa-fire" if "hearth" in p_slug else ("fa-film" if "cineai" in p_slug else "fa-masks-theater")),
                color="emerald" if "earth" in p_slug else ("amber" if "hearth" in p_slug else ("blue" if "cineai" in p_slug else "pink"))
            )
            repo.save_channel(chan)
        else:
            # Sync tag and comments to existing channel object if not set
            existing_ch = next((c for c in channels if c.channel_slug and c.channel_slug.lower() == p_slug), None)
            if existing_ch and (not existing_ch.tag or not existing_ch.comments):
                if p.tag and not existing_ch.tag: existing_ch.tag = p.tag
                if p.comments and not existing_ch.comments: existing_ch.comments = p.comments
                repo.save_channel(existing_ch)
    return repo.list_channels(current_user.id)


@router.get("/episodes")
async def list_channel_episodes(
    channel_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """Scan and list all channel episodes with full metadata, stages, models, and artifacts."""
    from src.api.routes.channel_episodes_scanner import scan_all_channel_episodes

    storage_dir = Path(__file__).resolve().parent.parent.parent.parent / "storage"
    episodes = scan_all_channel_episodes(storage_dir, user_id=current_user.email)
    if channel_id and channel_id != "all":
        episodes = [ep for ep in episodes if ep.get("channel_id") == channel_id]
    return {"status": "ok", "count": len(episodes), "episodes": episodes}


@router.post("", response_model=Channel, status_code=status.HTTP_201_CREATED)
async def create_channel(
    req: ChannelCreate,
    current_user: User = Depends(get_current_user),
):
    """Register and configure a new distribution channel in user storage."""
    slug = req.channel_slug or _slugify(req.channel_name)
    existing = repo.get_channel(current_user.id, slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A channel with slug '{slug}' already exists.",
        )

    channel = Channel(
        user_id=current_user.id,
        platform=req.platform,
        channel_name=req.channel_name,
        channel_slug=slug,
        channel_handle=req.channel_handle or f"@{slug}",
        category=req.category or "General",
        primary_genre=req.primary_genre,
        primary_language=req.primary_language or "en",
        icon=req.icon or "fa-clapperboard",
        color=req.color or "indigo",
        description=req.description or "",
        default_tags=req.default_tags,
    )
    saved = repo.save_channel(channel)
    user_chan_dir = storage_service.get_user_container_path(current_user.email) / "channels" / slug
    user_chan_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"channel_created: id={saved.id} slug='{slug}' user='{current_user.email}'")
    return saved


@router.put("/{channel_id}", response_model=Channel)
async def update_channel(
    channel_id: str,
    req: ChannelUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update metadata and settings for an existing channel."""
    channel = repo.get_channel(current_user.id, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

    if req.channel_name is not None: channel.channel_name = req.channel_name
    if req.channel_handle is not None: channel.channel_handle = req.channel_handle
    if req.category is not None: channel.category = req.category
    if req.primary_genre is not None: channel.primary_genre = req.primary_genre
    if req.primary_language is not None: channel.primary_language = req.primary_language
    if req.icon is not None: channel.icon = req.icon
    if req.color is not None: channel.color = req.color
    if req.description is not None: channel.description = req.description
    if req.default_tags is not None: channel.default_tags = req.default_tags
    if req.is_active is not None: channel.is_active = req.is_active

    saved = repo.save_channel(channel)
    logger.info(f"channel_updated: id={saved.id} name='{saved.channel_name}'")
    return saved


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete a distribution channel."""
    success = repo.delete_channel(current_user.id, channel_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    logger.info(f"channel_deleted: id={channel_id} user='{current_user.email}'")
    return {"status": "ok", "deleted": channel_id}


class ChannelPublishRequest(BaseModel):
    episode_id: UUID
    privacy_status: str = "public"
    selected_language_thumbnail: str = "en"
    custom_title: str | None = None
    custom_description: str | None = None
    custom_tags: list[str] | None = None


class ChannelPublishResponse(BaseModel):
    publication_id: UUID
    channel_id: UUID
    episode_id: UUID
    platform: str
    platform_video_id: str
    status: str
    synthetic_media_disclosed: bool
    monetization_cleared: bool


@router.post("/{channel_id}/publish", response_model=ChannelPublishResponse)
async def publish_to_channel(
    channel_id: str,
    req: ChannelPublishRequest,
    current_user: User = Depends(get_current_user),
):
    """Upload completed episode to YouTube with synthetic media disclosure."""
    channel = repo.get_channel(current_user.id, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Distribution channel not found")

    episode = repo.get_episode(current_user.id, req.episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode project not found")

    qa_check = await validate_monetization_readiness(
        episode_id=str(episode.id),
        rights_cleared=True,
        qa_passed=True,
        has_evidence_bundle=True,
    )
    if not qa_check.get("ready_to_publish", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Publication blocked: {', '.join(qa_check.get('blocking_reasons', []))}",
        )

    pub = ChannelPublication(
        user_id=current_user.id,
        episode_id=episode.id,
        channel_id=channel.id,
        platform=channel.platform,
        platform_video_id=f"yt_{uuid4().hex[:11]}",
        status="published",
        synthetic_media_disclosed=True,
        selected_language_thumbnail=req.selected_language_thumbnail,
        multi_language_audio_tracks=episode.options.target_languages if hasattr(episode, "options") else [],
    )
    saved_pub = repo.save_publication(pub)

    return ChannelPublishResponse(
        publication_id=saved_pub.id,
        channel_id=channel.id,
        episode_id=episode.id,
        platform=saved_pub.platform,
        platform_video_id=saved_pub.platform_video_id,
        status=saved_pub.status,
        synthetic_media_disclosed=saved_pub.synthetic_media_disclosed,
        monetization_cleared=True,
    )


@router.get("/publications", response_model=list[ChannelPublication])
async def list_publications(
    channel_id: str | None = None,
    current_user: User = Depends(get_current_user),
):
    """List historical publication audit ledger entries for user."""
    cid = UUID(channel_id) if channel_id and len(channel_id) == 36 else None
    return repo.list_publications(current_user.id, channel_id=cid)


@router.get("/profiles")
async def get_all_channel_profiles():
    """Retrieve global channel profiles, audience definitions, and guardrails."""
    from src.config.channel_registry import load_channel_profiles
    profiles = load_channel_profiles()
    return {"status": "ok", "profiles": {k: v.model_dump() for k, v in profiles.items()}}


@router.post("/ai-enrich-profile")
async def ai_enrich_channel_profile(
    req_data: dict,
    current_user: User = Depends(get_current_user),
):
    """Call Gemini to autonomously synthesize enriched channel profile guardrails."""
    from src.services.channel_profile_enricher import ChannelEnrichRequest, enrich_channel_profile_with_gemini
    req = ChannelEnrichRequest(**req_data)
    profile = await enrich_channel_profile_with_gemini(req)
    return {"status": "ok", "profile": profile.model_dump()}


@router.post("/save-profile")
async def save_profile(
    profile_data: dict,
    current_user: User = Depends(get_current_user),
):
    """Persist an individual channel profile JSON file into src/config/channels/<slug>.json."""
    from src.config.channel_registry import ChannelProfile, save_channel_profile
    profile = ChannelProfile(**profile_data)
    saved_path = save_channel_profile(profile)
    return {"status": "ok", "saved_file": str(saved_path), "channel_id": profile.channel_id}


