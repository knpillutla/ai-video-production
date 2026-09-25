"""Local filesystem implementation of the StorageProviderInterface."""

import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from src.core.telemetry import logger
from src.services.storage.storage_interface import (
    ArtifactCategory,
    ArtifactItem,
    StorageProviderInterface,
    StudioArtifactManifest,
)


class LocalStorageProvider(StorageProviderInterface):
    """Stores studio artifacts locally in the /storage hierarchy with URL streaming."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = (base_dir or Path("storage")).resolve()
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def get_public_url(self, relative_path: str) -> str:
        """Format a URL relative to FastAPI's mounted /storage directory."""
        clean_rel = relative_path.replace("\\", "/").lstrip("/")
        return f"/storage/{clean_rel}"

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
        """Save an artifact into the project's category folder."""
        dest_dir = self.projects_dir / project_id / category.value
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / filename

        if isinstance(source_path_or_bytes, (str, Path)):
            src_path = Path(source_path_or_bytes)
            if src_path.resolve() != dest_file.resolve() and src_path.exists():
                shutil.copy2(src_path, dest_file)
        elif isinstance(source_path_or_bytes, bytes):
            dest_file.write_bytes(source_path_or_bytes)

        rel_path = f"projects/{project_id}/{category.value}/{filename}"
        url = self.get_public_url(rel_path)

        return ArtifactItem(
            artifact_id=f"{project_id}_{category.value}_{filename}",
            category=category,
            relative_path=rel_path,
            url=url,
            scene_index=scene_index,
            model_name=model_name,
            duration_seconds=duration,
            resolution=resolution,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    async def get_manifest(self, project_id: str) -> Optional[StudioArtifactManifest]:
        """Load manifest.json from local project folder."""
        manifest_file = self.projects_dir / project_id / "manifest.json"
        if not manifest_file.exists():
            return None
        try:
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
            return StudioArtifactManifest.model_validate(data)
        except Exception as e:
            logger.warning(f"failed_to_load_manifest: {project_id} error={e}")
            return None

    async def save_manifest(self, manifest: StudioArtifactManifest) -> None:
        """Write manifest.json to local project folder."""
        project_dir = self.projects_dir / manifest.project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        manifest_file = project_dir / "manifest.json"
        manifest_file.write_text(
            json.dumps(manifest.model_dump(), indent=2), encoding="utf-8"
        )
