"""Database, Redis, and multi-tenant cloud storage configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """Connection strings and filesystem roots for multi-tenant storage."""

    storage_backend: str = "local"  # "local" | "azure" | "gcs"
    local_storage_root: str = "./storage"
    azure_storage_connection_string: str = ""
    gcs_project_id: str = ""
    gcs_bucket_prefix: str = "video-studio"
    gcs_credentials_file: str = ""

    database_url: str = "sqlite+aiosqlite:///./storage/studio_local.db"
    redis_url: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
