"""User-scoped Episode and Project management API routes."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.deps import get_current_user
from src.core.storage import storage_service
from src.domain.creative import Episode, EpisodeCreate
from src.domain.generation import ContentClassification, MediaFormat, ThemeGenre, VisualStyle
from src.domain.repo import repo
from src.domain.user import User

router = APIRouter(prefix="/api/projects", tags=["Projects & Episodes"])


@router.post("", response_model=Episode, status_code=status.HTTP_201_CREATED)
async def create_project(req: EpisodeCreate, current_user: User = Depends(get_current_user)):
    """Create a new video project/episode under a show owned by the user."""
    show = repo.get_show(current_user.id, req.show_id)
    if not show:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parent Show not found")

    from src.agents.classifier_agent import classifier_agent

    resolved = classifier_agent.resolve_classification(
        text=req.topic_or_idea or req.title,
        user_format=req.format,
        user_style=req.visual_style,
        user_theme=req.theme,
        title=req.title,
    )

    episode = Episode(
        user_id=current_user.id,
        show_id=req.show_id,
        title=req.title,
        duration_seconds=req.duration_seconds,
        format=resolved.media_format,
        visual_style=resolved.visual_style,
        theme=resolved.theme,
        aspect_ratio=req.aspect_ratio,
        options=req.options,
    )
    saved_ep = repo.save_episode(episode)
    # Ensure physical episode directory in user's creative vault
    ep_path = storage_service.get_episode_path(str(current_user.id), show.slug, str(saved_ep.id))
    manifest = saved_ep.model_dump(mode="json")
    manifest["topic_or_idea"] = req.topic_or_idea
    manifest["youtube_reference_url"] = req.youtube_reference_url
    await storage_service.save_json(ep_path / "project_manifest.json", manifest)
    return saved_ep


@router.get("", response_model=list[Episode])
async def list_projects(show_id: UUID | None = None, current_user: User = Depends(get_current_user)):
    """List only projects and episodes owned by the current authenticated user, sorted by date desc."""
    episodes = repo.list_episodes(current_user.id, show_id)
    return sorted(episodes, key=lambda e: e.created_at, reverse=True)


@router.get("/{episode_id}", response_model=Episode)
async def get_project(episode_id: UUID, current_user: User = Depends(get_current_user)):
    """Get details of a specific episode project owned by the user."""
    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode project not found")
    return episode


class ThumbnailGenRequest(BaseModel):
    """Payload to render an episodic thumbnail."""

    language: str = "en"
    style: str = "pill"
    headline: str = ""


class IngestSourceRequest(BaseModel):
    """Payload to distill reference YouTube URL or script text."""

    source_text: str
    genre: str = "comedy"


@router.post("/{episode_id}/thumbnail")
async def generate_episode_thumbnail(
    episode_id: UUID,
    req: ThumbnailGenRequest,
    current_user: User = Depends(get_current_user),
):
    """Render a high-contrast episodic thumbnail with top-left numbering badge."""
    from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail

    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    show = repo.get_show(current_user.id, episode.show_id)
    show_slug = show.slug if show else "default"

    ep_path = storage_service.get_episode_path(str(current_user.id), show_slug, str(episode.id))
    out_thumb = ep_path / "thumbnails" / f"{req.language}_ep{episode.episode_number:02d}.jpg"

    badge_config = EpisodicBadgeConfig(
        episode_number=episode.episode_number,
        language=req.language,
        style=req.style,
        position="top_left",
    )

    saved_path = generate_episodic_thumbnail(
        output_path=out_thumb,
        badge_config=badge_config,
        headline=req.headline or episode.title,
    )

    return {
        "status": "generated",
        "episode_number": episode.episode_number,
        "language": req.language,
        "thumbnail_path": str(saved_path),
        "position": "top_left",
    }


@router.post("/ingest-source")
async def ingest_reference_source(
    req: IngestSourceRequest,
    current_user: User = Depends(get_current_user),
):
    """Stage 1: Transformative ingestion distilling abstract tension without copying dialogue."""
    from src.scripts.youtube_ingest import distill_reference_source

    distilled = distill_reference_source(req.source_text, genre_hint=req.genre)
    return distilled


class ClassifyContentRequest(BaseModel):
    """Payload to detect or override content format and style."""

    text: str
    title: str | None = None
    user_format: MediaFormat = MediaFormat.AUTO
    user_style: VisualStyle = VisualStyle.AUTO
    user_theme: ThemeGenre = ThemeGenre.AUTO


@router.post("/classify-content", response_model=ContentClassification)
async def classify_content(
    req: ClassifyContentRequest,
    current_user: User = Depends(get_current_user),
):
    """Auto-detect Media Format, Visual Style, and Theme with user override support."""
    from src.agents.classifier_agent import classifier_agent

    return classifier_agent.resolve_classification(
        text=req.text,
        user_format=req.user_format,
        user_style=req.user_style,
        user_theme=req.user_theme,
        title=req.title,
    )
