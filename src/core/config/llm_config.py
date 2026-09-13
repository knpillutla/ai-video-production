"""LLM provider credentials and model selection defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """API credentials for LLM providers."""

    gemini_api_key: str = "mock-gemini-key"
    google_api_key: str = "mock-google-key"
    anthropic_api_key: str = "mock-anthropic-key"
    openai_api_key: str = "mock-openai-key"

    default_script_model: str = "gemini-1.5-pro"
    default_fast_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
