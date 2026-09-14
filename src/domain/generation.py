"""Enums and options for user video generation toggles and style classifications."""

from enum import Enum
from pydantic import BaseModel, Field


class MediaFormat(str, Enum):
    """Media production format presets."""

    AUTO = "auto"
    WEB_SERIES = "web_series"
    MOVIE_CINEMATIC = "movie_cinematic"
    TRAVEL_GUIDE = "travel_guide"
    VLOG = "vlog"
    NEWS_TABLOID = "news_tabloid"
    PODCAST_EXPLAINER = "podcast_explainer"
    DANCE_VIDEO = "dance_video"
    SCENIC_RELAXATION = "scenic_relaxation"
    WALKING_TOUR = "walking_tour"
    SCENIC_DRIVE = "scenic_drive"
    AMBIENT_LOUNGE = "ambient_lounge"
    NATURE_SANCTUARY = "nature_sanctuary"


class VisualStyle(str, Enum):
    """Visual generation and diffusion styling."""

    AUTO = "auto"
    REALISTIC = "realistic"
    ANIMATION_3D = "animation_3d"
    ANIME = "anime"
    STYLIZED_COMIC = "stylized_comic"


class AspectRatio(str, Enum):
    """Video output frame geometry."""

    LANDSCAPE_16_9 = "16:9"
    PORTRAIT_9_16 = "9:16"
    CINEMATIC_21_9 = "21:9"


class ThemeGenre(str, Enum):
    """Creative genre and narrative theme presets."""

    AUTO = "auto"
    TELUGU_COMEDY = "telugu_comedy"
    EPIC_ACTION = "epic_action"
    BOLLYWOOD_DANCE = "bollywood_dance"
    NATURE_WILDLIFE = "nature_wildlife"
    TRAVEL_TOURISM = "travel_tourism"
    ROMANTIC_DRAMA = "romantic_drama"
    TECH_SCIFI = "tech_scifi"


class ContentClassification(BaseModel):
    """Inferred or explicit format, visual style, and theme metadata."""

    media_format: MediaFormat = MediaFormat.AUTO
    visual_style: VisualStyle = VisualStyle.AUTO
    theme: ThemeGenre = ThemeGenre.AUTO
    is_auto_detected: bool = True
    confidence: float = Field(default=0.95, ge=0.0, le=1.0)
    explanation: str = ""


class GenerationOptions(BaseModel):
    """User-toggleable generation pipeline options (all default True)."""

    enable_thumbnails: bool = Field(default=True, description="Generate localized A/B thumbnails")
    enable_bgm: bool = Field(default=True, description="Generate and duck background music")
    enable_tts: bool = Field(default=True, description="Generate neural speech voiceovers")
    enable_voice_over: bool = Field(default=True, description="Generate voice over narration")
    enable_lipsync: bool = Field(default=False, description="Apply talking avatar mouth sync")
    sync_audio_video: bool = Field(default=True, description="Apply SSML prosody time matching")
    voice_gender: str = Field(default="female", description="Voice gender: female or male")
    target_languages: list[str] = Field(default_factory=lambda: ["en"], description="Target speech languages")
