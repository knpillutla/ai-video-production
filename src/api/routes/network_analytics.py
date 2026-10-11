"""Channel Management, YouTube Analytics Drilldown, and Credential Import API."""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.core.cache import cache, cached
from src.core.security import encrypt_secret
from src.core.telemetry import logger
from src.domain.distribution import Channel
from src.domain.repo import repo
from src.domain.user import User

router = APIRouter(prefix="/api/channels", tags=["Channel Management & YouTube Analytics"])


class ImportChannelCredentialsRequest(BaseModel):
    """Payload to import and encrypt YouTube API credentials."""

    channel_name: str
    channel_handle: Optional[str] = None
    primary_genre: str = "telugu_comedy"
    primary_language: str = "te"
    default_tags: List[str] = Field(default_factory=lambda: ["AIStudio", "4K", "TeluguComedy"])
    # Credential inputs
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    refresh_token: Optional[str] = None
    service_account_json: Optional[str] = None
    simulate_subscribers: int = 425000


class ChannelStatsResponse(BaseModel):
    """Aggregated YouTube metrics for a channel."""

    channel_id: str
    channel_name: str
    channel_handle: Optional[str]
    primary_genre: Optional[str]
    primary_language: str
    total_videos: int
    total_views: int
    total_revenue_usd: float
    total_likes: int
    subscribers_count: int
    credentials_configured: bool


class ChannelVideoDrilldownItem(BaseModel):
    """Video-level analytics within a channel."""

    video_id: str
    publication_id: str
    episode_id: str
    title: str
    format: str
    duration_seconds: int
    views: int
    likes: int
    comments: int
    estimated_revenue_usd: float
    ctr_pct: float
    retention_30s_pct: float
    published_at: str
    status: str


class PortfolioOverviewResponse(BaseModel):
    """Portfolio-wide statistics across all connected channels."""

    total_channels: int
    total_videos: int
    total_views: int
    total_revenue_usd: float
    total_subscribers: int
    channels: List[ChannelStatsResponse]


@router.get("/overview", response_model=PortfolioOverviewResponse)
@cached(ttl_seconds=300, namespace="channels_overview")
async def get_portfolio_overview(current_user: User = Depends(get_current_user)):
    """Fetch high-performance cached portfolio metrics across all channels."""
    user_channels = repo.list_channels(current_user.id)
    stats_list = []
    tot_views = 0
    tot_rev = 0.0
    tot_subs = 0
    tot_vids = 0

    for ch in user_channels:
        stat_dict = repo.get_channel_stats(current_user.id, ch.id)
        if stat_dict:
            stat_obj = ChannelStatsResponse(**stat_dict)
            stats_list.append(stat_obj)
            tot_views += stat_obj.total_views
            tot_rev += stat_obj.total_revenue_usd
            tot_subs += stat_obj.subscribers_count
            tot_vids += stat_obj.total_videos

    return PortfolioOverviewResponse(
        total_channels=len(user_channels),
        total_videos=tot_vids,
        total_views=tot_views,
        total_revenue_usd=round(tot_rev, 2),
        total_subscribers=tot_subs,
        channels=stats_list,
    )


@router.get("/recommend/{episode_id}")
async def recommend_channel_for_episode(
    episode_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Auto-select the most relevant channel based on video genre and language metadata."""
    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    recommended = repo.recommend_channel_for_episode(current_user.id, episode)
    if not recommended:
        return {"recommended_channel_id": None, "reason": "No channels configured"}

    ep_genre = episode.theme.value if hasattr(episode.theme, "value") else str(episode.theme)
    return {
        "recommended_channel_id": str(recommended.id),
        "channel_name": recommended.channel_name,
        "primary_genre": recommended.primary_genre,
        "primary_language": recommended.primary_language,
        "matched_genre": bool(recommended.primary_genre and recommended.primary_genre.lower() == ep_genre.lower()),
        "reason": f"Matches genre '{ep_genre}' and language '{recommended.primary_language}'",
    }


@router.post("/import-credentials", response_model=ChannelStatsResponse, status_code=status.HTTP_201_CREATED)
async def import_channel_credentials(
    req: ImportChannelCredentialsRequest,
    current_user: User = Depends(get_current_user),
):
    """Securely import and encrypt YouTube channel credentials with AES-256-GCM."""
    raw_secrets = req.service_account_json or f"{req.client_id}:{req.client_secret}:{req.refresh_token}"
    encrypted = encrypt_secret(raw_secrets)

    channel = Channel(
        user_id=current_user.id,
        channel_name=req.channel_name,
        channel_handle=req.channel_handle or f"@{req.channel_name.lower().replace(' ', '')}",
        primary_genre=req.primary_genre,
        primary_language=req.primary_language,
        default_tags=req.default_tags,
        subscribers_count=req.simulate_subscribers,
        total_views=req.simulate_subscribers * 3,
        total_revenue_usd=round((req.simulate_subscribers * 3 / 1000) * 3.45, 2),
        total_likes=int(req.simulate_subscribers * 0.25),
        encrypted_credentials=encrypted,
        credentials_configured=True,
    )
    saved = repo.save_channel(channel)
    # Invalidate cached overview
    await cache.clear()
    logger.info(f"channel_credentials_imported: id={saved.id} name='{saved.channel_name}'")

    stats = repo.get_channel_stats(current_user.id, saved.id)
    return ChannelStatsResponse(**stats)


@router.get("/{channel_id}/stats", response_model=ChannelStatsResponse)
async def get_channel_statistics(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed YouTube statistics for a single channel."""
    stats = repo.get_channel_stats(current_user.id, channel_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return ChannelStatsResponse(**stats)


@router.get("/{channel_id}/videos", response_model=List[ChannelVideoDrilldownItem])
async def list_channel_videos_drilldown(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Drill down to the video list for a specific channel with video-level performance metrics."""
    channel = repo.get_channel(current_user.id, channel_id)
    if not channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    videos = repo.list_channel_videos(current_user.id, channel_id)
    return [ChannelVideoDrilldownItem(**v) for v in videos]


@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Remove a channel from distribution."""
    success = repo.delete_channel(current_user.id, channel_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    await cache.clear()
    return {"status": "deleted", "channel_id": str(channel_id)}
