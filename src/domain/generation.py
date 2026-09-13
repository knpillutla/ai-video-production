"""Enums and options for user video generation toggles and style classifications."""

from enum import Enum
from pydantic import BaseModel, Field


class MediaFormat(str, Enum):
    """Media production format presets."""

    AUTO = "auto"
    WEB_SERIES = "web_series"
    MOVIE_CINEMATIC = "movie_cinematic"
    NEWS_TABLOID = "news_tabloid"
    PODCAST_EXPLAINER = "podcast_explainer"
    DANCE_VIDEO = "dance_video"


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


class GenerationOptions(BaseModel):
    """User-toggleable generation pipeline options (all default True)."""

    enable_thumbnails: bool = Field(default=True, description="Generate localized A/B thumbnails")
    enable_bgm: bool = Field(default=True, description="Generate and duck background music")
    enable_tts: bool = Field(default=True, description="Generate neural speech voiceovers")
    enable_lipsync: bool = Field(default=True, description="Apply talking avatar mouth sync")
    sync_audio_video: bool = Field(default=True, description="Apply SSML prosody time matching")
    target_languages: list[str] = Field(default_factory=lambda: ["te", "hi", "en"])
