"""LLM provider credentials and model selection defaults."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """API credentials for LLM providers."""

    gemini_api_key: str = ""
    google_api_key: str = ""
    gemini_google_search_enabled: bool = False
    anthropic_api_key: str = ""
    openai_api_key: str = ""


    default_script_model: str = "gemini-1.5-pro"
    default_fast_model: str = "gemini-1.5-flash"

    @property
    def live_gemini_api_key(self) -> str:
        """Resolve active Gemini API key, dynamically checking disk .env for newly saved keys."""
        try:
            from dotenv import dotenv_values
            vals = dotenv_values(".env")
            disk_k = vals.get("GEMINI_API_KEY") or vals.get("GOOGLE_API_KEY")
            if disk_k and disk_k.strip():
                return disk_k.strip()
        except Exception:
            pass
        return self.gemini_api_key or self.google_api_key or ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

