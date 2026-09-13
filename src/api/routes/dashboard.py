"""Executive Analytics Dashboard API routes."""

from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.domain.generation import AspectRatio
from src.domain.repo import repo
from src.domain.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Executive Dashboard & Analytics"])


class GenreStat(BaseModel):
    """Aggregate creation, publication, and cost breakdown per genre."""

    genre: str
    display_name: str
    created_count: int = 0
    published_count: int = 0
    total_cost_usd: float = 0.0


class FormatBreakdown(BaseModel):
    """Breakdown of content length and geometry."""

    long_form_count: int = 0  # 16:9 or 21:9 Widescreen (8-12 mins)
    short_form_count: int = 0  # 9:16 Vertical Shorts (30-60s)
    long_form_pct: float = 0.0
    short_form_pct: float = 0.0
    long_form_cost: float = 0.0
    short_form_cost: float = 0.0


class SampleShowcaseVideo(BaseModel):
    """Curated sample video for first-time user onboarding."""

    id: str
    title: str
    genre: str
    format: str
    duration: str
    thumbnail_url: str
    preview_url: str
    headline: str
    template_topic: str


class DashboardStatsResponse(BaseModel):
    """Executive metrics returned for user dashboard."""

    is_first_time_user: bool
    total_videos_created: int
    total_videos_published: int
    pending_approval_count: int
    total_cost_usd: float
    avg_compliance_score: float
    format_breakdown: FormatBreakdown
    genre_breakdown: dict[str, dict[str, Any]]
    sample_videos: list[SampleShowcaseVideo]
    sample_showcase_videos: list[SampleShowcaseVideo] = Field(default_factory=list)


SAMPLE_VIDEOS = [
    SampleShowcaseVideo(
        id="sample_01",
        title="They Lied About Remote Work! | IT Employee Comedy",
        genre="telugu_comedy",
        format="Web Series",
        duration="8m 00s",
        thumbnail_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=500&auto=format&fit=crop&q=80",
        preview_url="/previews/sample_wfh.mp4",
        headline="వర్క్ ఫ్రమ్ హోమ్ గోల!",
        template_topic="IT Employee WFH Standup Confusions",
    ),
    SampleShowcaseVideo(
        id="sample_02",
        title="Battle of the Red Dunes: The Rebel Leader Elevation",
        genre="epic_action",
        format="Cinematic Movie",
        duration="10m 30s",
        thumbnail_url="https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        preview_url="/previews/sample_action.mp4",
        headline="బాహుబలి తరహా మాస్ యాక్షన్!",
        template_topic="Rebel Commander Fortress Breach at Midnight",
    ),
    SampleShowcaseVideo(
        id="sample_03",
        title="Himalayan Ghost: The Snow Leopard Winter Stalk",
        genre="nature_wildlife",
        format="Documentary",
        duration="7m 45s",
        thumbnail_url="https://images.unsplash.com/photo-1456926631375-92c8ce872def?w=500&auto=format&fit=crop&q=80",
        preview_url="/previews/sample_nature.mp4",
        headline="4K Wildlife UHD",
        template_topic="Himalayan Snow Leopard Stealth Stalking",
    ),
]


@router.get("/stats", response_model=DashboardStatsResponse)
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """Compute executive statistics: first-time welcome status, format/genre split, and cost matrices."""
    user_episodes = repo.list_episodes(current_user.id)
    user_pubs = repo.list_publications(current_user.id)

    total_created = len(user_episodes)
    published_ep_ids = {p.episode_id for p in user_pubs if p.status == "published"} | {
        e.id for e in user_episodes if e.status == "published"
    }
    total_published = len(published_ep_ids)
    pending_count = sum(1 for e in user_episodes if e.status == "pending_approval")

    # Format breakdown: Long-form (16:9 or >= 180s) vs Short-form (9:16 or < 180s)
    long_eps = [
        e
        for e in user_episodes
        if e.aspect_ratio != AspectRatio.PORTRAIT_9_16 and e.duration_seconds >= 180
    ]
    short_eps = [e for e in user_episodes if e not in long_eps]
    long_form = len(long_eps)
    short_form = len(short_eps)
    long_pct = round((long_form / max(1, total_created)) * 100, 1)
    short_pct = round((short_form / max(1, total_created)) * 100, 1)
    long_cost = round(sum(e.actual_spend_usd or e.estimated_cost_usd or 0.15 for e in long_eps), 4)
    short_cost = round(sum(e.actual_spend_usd or e.estimated_cost_usd or 0.119 for e in short_eps), 4)

    # Genre breakdown
    genre_data: dict[str, dict[str, Any]] = {}
    known_genres = {
        "telugu_comedy": "Telugu Comedy & Satire",
        "epic_action": "Pan-Indian Epic Action",
        "bollywood_dance": "Bollywood Dance",
        "nature_wildlife": "Nature & Wildlife",
        "travel_tourism": "Travel & Tourism",
        "romantic_drama": "Romantic Drama",
        "tech_scifi": "Tech & Cyberpunk",
        "general": "General / Other",
    }

    for ep in user_episodes:
        g = ep.theme.value if hasattr(ep.theme, "value") else str(ep.theme)
        if g not in genre_data:
            genre_data[g] = {
                "genre": g,
                "display_name": known_genres.get(g, g.replace("_", " ").title()),
                "created": 0,
                "created_count": 0,
                "published": 0,
                "published_count": 0,
                "total_cost": 0.0,
                "total_cost_usd": 0.0,
            }
        genre_data[g]["created"] += 1
        genre_data[g]["created_count"] += 1
        if ep.id in published_ep_ids:
            genre_data[g]["published"] += 1
            genre_data[g]["published_count"] += 1
        ep_cost = ep.actual_spend_usd or ep.estimated_cost_usd or 0.15
        genre_data[g]["total_cost"] = round(genre_data[g]["total_cost"] + ep_cost, 4)
        genre_data[g]["total_cost_usd"] = genre_data[g]["total_cost"]

    total_cost = round(sum(e.actual_spend_usd or e.estimated_cost_usd or 0.15 for e in user_episodes), 4)
    avg_score = round(sum(e.compliance_score or 0.96 for e in user_episodes) / max(1, total_created), 2)

    return DashboardStatsResponse(
        is_first_time_user=total_created == 0,
        total_videos_created=total_created,
        total_videos_published=total_published,
        pending_approval_count=pending_count,
        total_cost_usd=total_cost,
        avg_compliance_score=avg_score if total_created > 0 else 0.98,
        format_breakdown=FormatBreakdown(
            long_form_count=long_form,
            short_form_count=short_form,
            long_form_pct=long_pct,
            short_form_pct=short_pct,
            long_form_cost=long_cost,
            short_form_cost=short_cost,
        ),
        genre_breakdown=genre_data,
        sample_videos=SAMPLE_VIDEOS,
        sample_showcase_videos=SAMPLE_VIDEOS,
    )
