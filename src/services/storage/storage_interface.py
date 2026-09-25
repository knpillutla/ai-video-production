"""Storage abstraction models and interface contracts for Studio Artifacts."""

from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ArtifactCategory(str, Enum):
    """6-Section Studio Master Artifact Hierarchy."""
    SECTION_0_MASTER = "master"
    SECTION_1_IMAGES = "images"
    SECTION_2_VIDEOS = "videos"
    SECTION_3_FOLEY = "foley"
    SECTION_4_BGM = "bgm"
    SECTION_5_VOICE = "voice"
    SECTION_6_SUBTITLES = "subtitles"


class ArtifactItem(BaseModel):
    """Metadata for an individual media artifact."""
    artifact_id: str
    category: ArtifactCategory
    relative_path: str
    url: str
    scene_index: Optional[int] = None
    model_name: Optional[str] = None
    duration_seconds: Optional[float] = None
    resolution: Optional[str] = None
    created_at: Optional[str] = None


class StudioArtifactManifest(BaseModel):
    """Canonical 6-Section Manifest consumed identically by UI, CLI, and APIs."""
    project_id: str
    title: str
    studio_type: str
    topic: str
    status: str = "completed"  # pending, in_progress, completed, failed
    created_at: str
    cost_usd: float = 0.0
    section_0_master: Optional[ArtifactItem] = None
    section_1_images: List[ArtifactItem] = Field(default_factory=list)
    section_2_videos: List[ArtifactItem] = Field(default_factory=list)
    section_3_foley: List[ArtifactItem] = Field(default_factory=list)
    section_4_bgm: List[ArtifactItem] = Field(default_factory=list)
    section_5_voice: List[ArtifactItem] = Field(default_factory=list)
    section_6_subtitles: List[ArtifactItem] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)


class StorageProviderInterface(ABC):
    """Protocol for persisting and retrieving studio artifacts."""

    @abstractmethod
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
        """Persist an artifact and return its standardized item metadata."""
        pass

    @abstractmethod
    async def get_manifest(self, project_id: str) -> Optional[StudioArtifactManifest]:
        """Fetch the 6-section manifest for a project."""
        pass

    @abstractmethod
    async def save_manifest(self, manifest: StudioArtifactManifest) -> None:
        """Persist the project manifest."""
        pass

    @abstractmethod
    def get_public_url(self, relative_path: str) -> str:
        """Generate a public or direct URL for an artifact."""
        pass
