"""Storage abstraction package for Studio Artifacts."""

from typing import Optional

from src.core.config import settings
from src.services.storage.azure_blob_storage import AzureBlobStorageProvider
from src.services.storage.local_storage import LocalStorageProvider
from src.services.storage.storage_interface import (
    ArtifactCategory,
    ArtifactItem,
    StorageProviderInterface,
    StudioArtifactManifest,
)

_storage_instance: Optional[StorageProviderInterface] = None


def get_storage_provider() -> StorageProviderInterface:
    """Return the configured storage provider (Azure Blob or Local)."""
    global _storage_instance
    if _storage_instance is None:
        backend = getattr(settings.storage, "storage_backend", "local")
        if backend == "azure":
            _storage_instance = AzureBlobStorageProvider()
        else:
            _storage_instance = LocalStorageProvider()
    return _storage_instance


__all__ = [
    "ArtifactCategory",
    "ArtifactItem",
    "AzureBlobStorageProvider",
    "LocalStorageProvider",
    "StorageProviderInterface",
    "StudioArtifactManifest",
    "get_storage_provider",
]
