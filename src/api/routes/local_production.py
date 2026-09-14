"""Local Video Production API routes for 0-cost local synthesis into storage/."""

from typing import Any, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.services.local_video_producer import produce_local_video_episode
from src.core.storage import storage_service

router = APIRouter(prefix="/api/production", tags=["Local Production Engine"])


class LocalProduceRequest(BaseModel):
    """Payload for local video synthesis and storage persistence."""

    prompt: str = Field(..., description="Prompt concept, theme, or script")
    title: Optional[str] = Field(None, description="Project title")
    episode_id: Optional[str] = Field("EP-001", description="Traceable Episode ID")
    user_id: Optional[str] = Field("user_krishna_01", description="User identifier")
    production_type: Optional[str] = Field("Theme", description="Theme, Idea, Script, or YouTube Reference")
    tier: Optional[str] = Field("low_cost", description="Production tier key")
    video_type: Optional[str] = Field("Travel Guide & Doc", description="Classified video type")
    format_type: Optional[str] = Field("Long (16:9)", description="Media aspect ratio format")
    style_type: Optional[str] = Field("Realistic (Photoreal)", description="Visual style")
    youtube_url: Optional[str] = Field(None, description="Optional YouTube reference URL")
    duration_seconds: Optional[float] = Field(6.0, description="Duration in seconds (capped to 10s)")


class LocalProduceResponse(BaseModel):
    """Response returned after local single-pass video render."""

    success: bool
    job_id: str
    episode_id: str
    title: str
    video_url: str
    storage_path: str
    file_size_bytes: int
    duration_seconds: float
    render_time_seconds: float
    artifacts: list[dict[str, Any]]


@router.post("/local-produce", response_model=LocalProduceResponse, status_code=status.HTTP_200_OK)
async def produce_video_locally(req: LocalProduceRequest):
    """Synthesize a complete broadcast-grade MP4 video locally with scenes, stems, and manifests in storage/."""
    title = req.title or (req.prompt[:36] if len(req.prompt) > 36 else req.prompt)
    if not title:
        title = "Explore Niagara Falls"

    # Enforce Rule 8 cap: maximum 10 seconds duration
    capped_duration = min(10.0, max(4.0, float(req.duration_seconds or 6.0)))

    try:
        result = await produce_local_video_episode(
            prompt=req.prompt,
            title=title,
            episode_id=req.episode_id or "EP-001",
            user_id=req.user_id or "user_krishna_01",
            production_type=req.production_type or "Theme",
            tier=req.tier or "low_cost",
            video_type=req.video_type or "Travel Guide & Doc",
            format_type=req.format_type or "Long (16:9)",
            style_type=req.style_type or "Realistic (Photoreal)",
            youtube_url=req.youtube_url,
            duration_seconds=capped_duration,
        )
        return LocalProduceResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Local production synthesis failed: {str(exc)}",
        )
