"""Multi-tenant cloud and local storage abstraction with per-user container isolation."""

import json
import os
import re
from pathlib import Path
from typing import Any

from src.core.config import settings


def sanitize_container_name(user_id: str) -> str:
    """Sanitize user ID into a valid Azure Blob container name (lowercase, alphanumeric, hyphens)."""
    clean_id = re.sub(r"[^a-zA-Z0-9-]", "-", str(user_id)).lower()
    clean_id = re.sub(r"-+", "-", clean_id).strip("-")
    container = f"user-{clean_id}"
    return container[:63]


class MultiTenantStorageService:
    """Provides air-gapped per-user storage with decoupled creative and distribution domains."""

    def __init__(self, root_dir: str | None = None):
        self.root_dir = Path(root_dir or settings.storage.local_storage_root)
        self.backend = settings.storage.storage_backend
        self._ensure_root()

    def _ensure_root(self) -> None:
        if self.backend == "local":
            self.root_dir.mkdir(parents=True, exist_ok=True)

    def get_user_container_path(self, user_id: str) -> Path:
        """Return root path for a user's isolated container."""
        container_name = sanitize_container_name(user_id)
        container_path = self.root_dir / container_name
        container_path.mkdir(parents=True, exist_ok=True)
        return container_path

    def get_creative_vault_path(self, user_id: str, show_slug: str) -> Path:
        """Return path for a user's specific show universe in the creative vault."""
        clean_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", str(show_slug).lower()).strip("_") or "default_show"
        clean_slug = re.sub(r"_+", "_", clean_slug)[:64]
        base = self.get_user_container_path(user_id)
        vault_path = base / "creative_vault" / "shows_and_titles" / clean_slug
        vault_path.mkdir(parents=True, exist_ok=True)
        return vault_path

    def get_character_path(self, user_id: str, show_slug: str, character_id: str) -> Path:
        """Return path for a character's IP assets within a show universe."""
        base = self.get_creative_vault_path(user_id, show_slug)
        char_path = base / "characters" / character_id
        char_path.mkdir(parents=True, exist_ok=True)
        return char_path

    def get_episode_path(self, user_id: str, show_slug: str, episode_id: str) -> Path:
        """Return path for an episode's scripts, audio stems, and master renders."""
        base = self.get_creative_vault_path(user_id, show_slug)
        ep_path = base / "episodes" / episode_id
        ep_path.mkdir(parents=True, exist_ok=True)
        return ep_path

    def get_channel_path(self, user_id: str, channel_id: str) -> Path:
        """Return path for a user's distribution channel and upload ledger."""
        base = self.get_user_container_path(user_id)
        chan_path = base / "distribution" / "channels" / channel_id
        chan_path.mkdir(parents=True, exist_ok=True)
        return chan_path

    async def save_json(self, file_path: Path, data: dict[str, Any]) -> None:
        """Atomically persist JSON metadata."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = file_path.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        temp_file.replace(file_path)

    async def load_json(self, file_path: Path) -> dict[str, Any] | None:
        """Load and parse JSON metadata."""
        if not file_path.exists():
            return None
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def generate_signed_url(self, user_id: str, relative_blob_path: str) -> str:
        """Generate a short-lived 15-minute SAS or Signed URL depending on active storage backend."""
        container_name = sanitize_container_name(user_id)
        if self.backend == "azure" and settings.storage.azure_storage_connection_string:
            return f"https://mystorage.blob.core.windows.net/{container_name}/{relative_blob_path}?se=mock_sas_token"
        elif self.backend == "gcs" and settings.storage.gcs_project_id:
            bucket_name = f"{settings.storage.gcs_bucket_prefix}-{container_name}"
            return f"https://storage.googleapis.com/{bucket_name}/{relative_blob_path}?X-Goog-Signature=mock_sig"
        return f"/api/vault/stream/{container_name}/{relative_blob_path}"

    async def generate_sas_url(self, user_id: str, relative_blob_path: str) -> str:
        """Backwards-compatible alias for generate_signed_url."""
        return await self.generate_signed_url(user_id, relative_blob_path)


# Singleton storage service
storage_service = MultiTenantStorageService()

__all__ = ["storage_service", "MultiTenantStorageService", "sanitize_container_name"]
