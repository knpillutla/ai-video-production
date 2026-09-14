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
    youtube_reference_url: Optional[str] = Field(None, description="YouTube reference link/URL")
    youtube_reference_link: Optional[str] = Field(None, description="YouTube reference URL alias")
    duration_seconds: Optional[float] = Field(6.0, description="Duration in seconds (capped to 10s)")
    enable_bgm: Optional[bool] = Field(None, description="Include background music")
    bgm: Optional[bool] = Field(None, description="Alias for enable_bgm")
    enable_tts: Optional[bool] = Field(None, description="Conversational audio with lipsync")
    tts: Optional[bool] = Field(None, description="Alias for enable_tts")
    enable_voice_over: Optional[bool] = Field(None, description="Neural voiceover narration")
    voice_over: Optional[bool] = Field(None, description="Alias for enable_voice_over")
    enable_lipsync: Optional[bool] = Field(None, description="Talking avatar mouth sync")
    lipsync: Optional[bool] = Field(None, description="Alias for enable_lipsync")
    voice_gender: Optional[str] = Field(None, description="Voice gender: female or male")
    narration_male: Optional[bool] = Field(None, description="Flag for male voiceover")
    narration_female: Optional[bool] = Field(None, description="Flag for female voiceover")
    language: Optional[str] = Field("en", description="Primary spoken language (default: en)")
    target_languages: Optional[list[str]] = Field(None, description="Multilingual target languages")
    theme: Optional[str] = Field(None, description="Theme preset or narrative theme")
    idea: Optional[str] = Field(None, description="Story idea or creative angle")
    script: Optional[str] = Field(None, description="Screenplay dialogue text")
    custom_script: Optional[str] = Field(None, description="Alias for script")


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

    yt_link = req.youtube_reference_link or req.youtube_reference_url or req.youtube_url
    eff_bgm = req.enable_bgm if req.enable_bgm is not None else (req.bgm if req.bgm is not None else True)
    eff_tts = req.enable_tts if req.enable_tts is not None else req.tts
    eff_vo = req.enable_voice_over if req.enable_voice_over is not None else req.voice_over
    eff_lipsync = req.enable_lipsync if req.enable_lipsync is not None else req.lipsync
    eff_gender = "male" if req.narration_male else ("female" if req.narration_female else (req.voice_gender or "female"))
    eff_script = req.script or req.custom_script

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
            youtube_url=yt_link,
            duration_seconds=capped_duration,
            enable_bgm=eff_bgm,
            enable_tts=eff_tts,
            enable_voice_over=eff_vo,
            enable_lipsync=eff_lipsync,
            voice_gender=eff_gender,
            language=req.language or "en",
            theme=req.theme,
            idea=req.idea,
            script=eff_script,
        )
        return LocalProduceResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Local production synthesis failed: {str(exc)}",
        )
