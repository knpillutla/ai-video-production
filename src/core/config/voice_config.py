"""Speech synthesis and voice provider configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class VoiceSettings(BaseSettings):
    """API credentials and regional defaults for TTS providers."""

    azure_speech_key: str = "mock-azure-speech-key"
    azure_speech_region: str = "eastus"
    elevenlabs_api_key: str = "mock-elevenlabs-key"

    default_tts_provider: str = "azure_speech"
    default_sample_rate_hz: int = 48000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
