"""Asset Rights Ledger and Originality Provenance Domain Entities."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Categorization of media assets within production pipeline."""

    IMAGE = "image"
    VOICE = "voice"
    MUSIC = "music"
    VIDEO_CLIP = "video_clip"
    VIDEO_MOTION = "video_motion"
    AVATAR = "avatar"
    SFX = "sfx"


class CommercialLicenseType(str, Enum):
    """Machine-readable commercial licensing tier."""

    FULL_COMMERCIAL_OWNERSHIP = "commercial_full_ownership"
    COMMERCIAL_ROYALTY_FREE = "commercial_royalty_free"
    CREATIVE_COMMONS_CC0 = "creative_commons_cc0"
    UNVERIFIED = "unverified"


class AssetRightsRecord(BaseModel):
    """Immutable ledger entry recording commercial clearance for a single asset."""

    asset_id: str = Field(default_factory=lambda: str(uuid4()))
    asset_type: AssetType
    file_path: str
    provider: str
    model_name: str
    license_type: CommercialLicenseType
    license_id: str
    cleared_for_commercial_monetization: bool
    attribution_required: bool = False
    attribution_text: str | None = None
    prompt_hash: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OriginalityEvidenceBundle(BaseModel):
    """Auditable provenance package for YPP reviews and Content ID appeals."""

    bundle_id: UUID = Field(default_factory=uuid4)
    project_id: UUID
    episode_id: UUID
    title: str
    script_thesis: str
    research_sources: list[dict[str, Any]] = Field(default_factory=list)
    originality_score: float = Field(ge=0.0, le=1.0)
    rights_records: list[AssetRightsRecord] = Field(default_factory=list)
    total_assets_cleared: int = 0
    monetization_approved: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "AssetType",
    "CommercialLicenseType",
    "AssetRightsRecord",
    "OriginalityEvidenceBundle",
]
