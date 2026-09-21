"""Visual diffusion and background music configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class MediaSettings(BaseSettings):
    """API credentials for image generation and commercial music scoring."""

    together_api_key: str = ""
    suno_api_key: str = ""


    default_image_model: str = "fal-ai/flux/dev"
    default_music_model: str = "suno-v3.5-pro"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
