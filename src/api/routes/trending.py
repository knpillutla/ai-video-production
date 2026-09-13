"""YouTube Trending Topics Ingestion & Transformative Script Ideation API."""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.domain.creative import Episode
from src.domain.repo import repo
from src.domain.user import User
from src.scripts.youtube_ingest import distill_reference_source

router = APIRouter(prefix="/api/trending", tags=["Trending Topics & Ingestion"])

# High-velocity curated trending topics across Telugu, Indian entertainment, and Tech
TRENDING_TOPICS_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "trend_001",
        "title": "Why Indian Tech Companies Are Calling Everyone Back to Office in 2026",
        "channel_title": "Tech Bharat Insider",
        "views_count": 1420000,
        "region": "IN",
        "category": "tech_corporate",
        "genre": "comedy",
        "suggested_angle": "Satirical day-in-the-life of a senior software engineer pretending to work at the cafeteria",
        "tags": ["wfh", "office_return", "tech_humor", "corporate_life", "india_tech"],
        "published_at": "2026-09-12T10:00:00Z",
    },
    {
        "id": "trend_002",
        "title": "SS Rajamouli & Mahesh Babu Globe-Trotting Action Adventure Sneak Peek",
        "channel_title": "Tollywood Cinema World",
        "views_count": 3890000,
        "region": "IN",
        "category": "cinema",
        "genre": "epic_action",
        "suggested_angle": "Fictional mass action elevation scene analyzing legendary jungle exploration stunts",
        "tags": ["tollywood", "rajamouli", "mahesh_babu", "mass_cinema", "telugu"],
        "published_at": "2026-09-11T14:30:00Z",
    },
    {
        "id": "trend_003",
        "title": "The Secret Submarine Cable Network Carrying 99% of Global Internet Traffic",
        "channel_title": "Engineering Marvels",
        "views_count": 2100000,
        "region": "GLOBAL",
        "category": "documentary",
        "genre": "documentary",
        "suggested_angle": "Deep-sea fiber optic survival documentary with 2.5D camera zoompan over ocean trenches",
        "tags": ["engineering", "internet", "deep_sea", "technology", "documentary"],
        "published_at": "2026-09-10T18:00:00Z",
    },
    {
        "id": "trend_004",
        "title": "Hyderabad Sunday Biryani Wars: Old City vs Gachibowli Showdown",
        "channel_title": "Telugu Foodie Diaries",
        "views_count": 980000,
        "region": "IN",
        "category": "food_culture",
        "genre": "comedy",
        "suggested_angle": "Humorous linguistic debate between an IT fresher and an Old City Biryani maestro",
        "tags": ["hyderabad", "biryani", "telugu_comedy", "food_wars", "gachibowli"],
        "published_at": "2026-09-12T08:15:00Z",
    },
    {
        "id": "trend_005",
        "title": "Autonomous AI Agents Running Real Companies: Hype vs Reality",
        "channel_title": "Silicon Valley Dispatch",
        "views_count": 1750000,
        "region": "GLOBAL",
        "category": "tech_corporate",
        "genre": "documentary",
        "suggested_angle": "Investigative breakdown of multi-agent swarms replacing manual workflows in 2026",
        "tags": ["artificial_intelligence", "ai_agents", "future_tech", "automation"],
        "published_at": "2026-09-12T16:45:00Z",
    },
]


class SelectTrendingTopicRequest(BaseModel):
    """Payload to instantiate a video project directly from a trending YouTube topic."""
    trending_id: str
    show_id: UUID
    custom_title: Optional[str] = None
    target_duration_seconds: int = 480


class TrendingTopicResponse(BaseModel):
    """Item in trending topic feed."""
    id: str
    title: str
    channel_title: str
    views_count: int
    region: str
    category: str
    genre: str
    suggested_angle: str
    tags: List[str]
    published_at: str


@router.get("/youtube", response_model=List[TrendingTopicResponse])
async def list_youtube_trending_topics(
    region: str = Query(default="IN", description="ISO country code or GLOBAL"),
    category: Optional[str] = Query(default=None, description="Optional category filter"),
    current_user: User = Depends(get_current_user),
) -> List[Dict[str, Any]]:
    """Retrieve top YouTube trending video topics for script ideation."""
    results = TRENDING_TOPICS_CATALOG
    if region and region.upper() != "ALL":
        results = [t for t in results if t["region"].upper() in (region.upper(), "GLOBAL")]
    if category and category.lower() != "all":
        results = [t for t in results if t["category"].lower() == category.lower()]
    return results


@router.post("/select-topic", status_code=status.HTTP_201_CREATED)
async def create_episode_from_trending_topic(
    request: SelectTrendingTopicRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Transform a trending YouTube topic into a 100% original, anti-mimicked Episode project."""
    match = next((t for t in TRENDING_TOPICS_CATALOG if t["id"] == request.trending_id), None)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trending topic not found")

    # Stage 1: Distill core abstract premise without copying any source dialogue
    distilled = distill_reference_source(match["title"] + " " + match["suggested_angle"], genre_hint=match["genre"])

    # Create original project title from transformative angle
    project_title = request.custom_title or f"{match['suggested_angle']}"

    episode = Episode(
        user_id=current_user.id,
        show_id=request.show_id,
        title=project_title,
        duration_seconds=request.target_duration_seconds,
    )
    repo.save_episode(episode)

    return {
        "status": "created",
        "episode_id": episode.id,
        "title": episode.title,
        "genre": match["genre"],
        "source_trend": match["title"],
        "abstract_theme": distilled.core_theme,
        "psychological_hook": distilled.psychological_hook,
        "tags": match["tags"],
    }
