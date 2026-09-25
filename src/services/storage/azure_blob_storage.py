"""Azure Blob Storage provider with transparent local fallback."""

from pathlib import Path
from typing import Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.services.storage.local_storage import LocalStorageProvider
from src.services.storage.storage_interface import (
    ArtifactCategory,
    ArtifactItem,
    StorageProviderInterface,
    StudioArtifactManifest,
)


class AzureBlobStorageProvider(StorageProviderInterface):
    """Stores artifacts in Azure Blob Storage with SAS URLs, falling back to local storage."""

    def __init__(self):
        self._local_fallback = LocalStorageProvider()
        self._azure_client = None
        self._container_name = "studio-artifacts"
        self._init_azure_client()

    def _init_azure_client(self) -> None:
        """Initialize Azure Blob Service client if credentials are configured."""
        conn_str = getattr(settings.storage, "azure_storage_connection_string", None)
        if conn_str:
            try:
                from azure.storage.blob import BlobServiceClient
                self._azure_client = BlobServiceClient.from_connection_string(conn_str)
                container = self._azure_client.get_container_client(self._container_name)
                if not container.exists():
                    container.create_container()
                logger.info("azure_blob_storage_initialized")
            except Exception as exc:
                logger.warning(f"azure_blob_storage_init_failed: {exc}. Falling back to local.")
                self._azure_client = None

    def get_public_url(self, relative_path: str) -> str:
        """Return Azure Blob URL or fallback local URL."""
        if self._azure_client:
            blob_name = relative_path.replace("\\", "/").lstrip("/")
            blob_client = self._azure_client.get_blob_client(
                container=self._container_name, blob=blob_name
            )
            return blob_client.url
        return self._local_fallback.get_public_url(relative_path)

    async def save_artifact(
        self,
        project_id: str,
        category: ArtifactCategory,
        filename: str,
        source_path_or_bytes: bytes | Path | str,
        scene_index: Optional[int] = None,
        model_name: Optional[str] = None,
        duration: Optional[float] = None,
        resolution: Optional[str] = None,
    ) -> ArtifactItem:
        """Save artifact to Azure Blob Storage and local mirror."""
        # Always mirror locally for immediate FFmpeg and local caching access
        local_item = await self._local_fallback.save_artifact(
            project_id=project_id,
            category=category,
            filename=filename,
            source_path_or_bytes=source_path_or_bytes,
            scene_index=scene_index,
            model_name=model_name,
            duration=duration,
            resolution=resolution,
        )

        if self._azure_client:
            try:
                blob_name = local_item.relative_path
                blob_client = self._azure_client.get_blob_client(
                    container=self._container_name, blob=blob_name
                )
                if isinstance(source_path_or_bytes, bytes):
                    blob_client.upload_blob(source_path_or_bytes, overwrite=True)
                else:
                    with open(source_path_or_bytes, "rb") as data:
                        blob_client.upload_blob(data, overwrite=True)
                local_item.url = blob_client.url
            except Exception as e:
                logger.warning(f"azure_blob_upload_error: {e}")

        return local_item

    async def get_manifest(self, project_id: str) -> Optional[StudioArtifactManifest]:
        """Fetch manifest from Azure or local fallback."""
        return await self._local_fallback.get_manifest(project_id)

    async def save_manifest(self, manifest: StudioArtifactManifest) -> None:
        """Persist manifest to local storage and Azure Blob."""
        await self._local_fallback.save_manifest(manifest)
        if self._azure_client:
            try:
                import json
                blob_name = f"projects/{manifest.project_id}/manifest.json"
                blob_client = self._azure_client.get_blob_client(
                    container=self._container_name, blob=blob_name
                )
                blob_client.upload_blob(
                    json.dumps(manifest.model_dump(), indent=2), overwrite=True
                )
            except Exception as e:
                logger.warning(f"azure_blob_manifest_upload_error: {e}")
