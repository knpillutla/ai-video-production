"""Unified configuration module for AI Video Producer Studio."""

from dataclasses import dataclass, field

from src.core.config.base import AppSettings
from src.core.config.llm_config import LLMSettings
from src.core.config.media_config import MediaSettings
from src.core.config.storage_config import StorageSettings
from src.core.config.video_config import VideoSettings
from src.core.config.voice_config import VoiceSettings


@dataclass(frozen=True)
class Settings:
    """Aggregated, typed application settings."""

    app: AppSettings = field(default_factory=AppSettings)
    llm: LLMSettings = field(default_factory=LLMSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    media: MediaSettings = field(default_factory=MediaSettings)
    video: VideoSettings = field(default_factory=VideoSettings)
    storage: StorageSettings = field(default_factory=StorageSettings)


# Authoritative singleton settings instance
settings = Settings()

__all__ = ["settings", "Settings"]
