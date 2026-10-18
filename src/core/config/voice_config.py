"""Speech synthesis and voice provider configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VoiceSettings(BaseSettings):
    """API credentials and regional defaults for TTS providers."""

    azure_speech_key: str = ""
    azure_speech_region: str = "eastus"
    elevenlabs_api_key: str = ""


    default_tts_provider: str = "azure_speech"
    default_tts_model: str = "azure_speech"
    gemini_tts_voice: str = "Charon"
    kokoro_voice: str = "bm_george"
    default_sample_rate_hz: int = 48000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
