"""Video motion, lip-sync, and camera dynamics configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VideoSettings(BaseSettings):
    """API credentials for video motion, dance pose, and avatar lip-sync."""

    fal_key: str = "mock-fal-key"

    default_lipsync_model: str = "fal-ai/live-portrait"
    default_video_motion_model: str = "fal-ai/minimax/video-01"
    default_dance_model: str = "fal-ai/mimic-motion"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
