"""Video motion, lip-sync, and camera dynamics configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VideoSettings(BaseSettings):
    """API credentials for video motion, dance pose, and avatar lip-sync."""

    fal_key: str = ""
    fal_api_key: str = ""
    runway_api_key: str = ""
    kling_api_key: str = ""


    default_lipsync_model: str = "fal-ai/latentsync"
    default_video_motion_model: str = "fal-ai/kling-video/v1.5/pro/image-to-video"
    default_dance_model: str = "fal-ai/mimic-motion"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
