"""Base application and security configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Core FastAPI and authentication settings."""

    app_name: str = "Professional AI Video Producer Studio"
    app_env: str = "development"
    api_port: int = 8000
    jwt_secret: str = "super-secret-studio-jwt-encryption-key-for-local-development-32chars"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440

    google_client_id: str = "dev-google-client-id"
    google_client_secret: str = "dev-google-client-secret"
    encryption_master_key: str = "YWJjZGVmZ2hpamtsbW5vcHFyc3R1dnd4eXoxMjM0NTY="
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
