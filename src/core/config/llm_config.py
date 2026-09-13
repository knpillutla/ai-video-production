"""LLM provider credentials and model selection defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """API credentials for LLM providers."""

    gemini_api_key: str = ""
    google_api_key: str = ""
    anthropic_api_key: str = ""
    openai_api_key: str = ""


    default_script_model: str = "gemini-1.5-pro"
    default_fast_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
