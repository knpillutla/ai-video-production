"""Pydantic data models for Studio Orchestrator and Job Lifecycle."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.services.storage.storage_interface import StudioArtifactManifest


class ProductionStage(str, Enum):
    """4-Stage Progressive Quality Gate Stages."""
    STAGE_1_PREFLIGHT = "stage_1_preflight"
    STAGE_2_KEYFRAMES = "stage_2_keyframes"
    STAGE_3_AUDIO = "stage_3_audio"
    STAGE_4_MOTION_MASTER = "stage_4_motion_master"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED_DUPLICATE = "blocked_duplicate"


class StudioCostEstimate(BaseModel):
    """Itemized pre-flight cost breakdown."""
    llm_cost_usd: float = 0.005
    tts_cost_usd: float = 0.000
    image_cost_usd: float = 0.060
    video_motion_cost_usd: float = 0.800
    compute_cost_usd: float = 0.010
    total_cost_usd: float = 0.875


class StudioProductionRequest(BaseModel):
    """Decoupled UI & CLI production submission contract."""
    studio_id: str = "nature_retreat"
    topic: str
    duration_seconds: int = 20
    scene_count: int = 3
    aspect_ratio: str = "16:9"
    dry_run: bool = False
    custom_params: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[str] = "default_user"


class StudioJobStatus(BaseModel):
    """Real-time job execution state tracked by orchestrator."""
    job_id: str
    studio_id: str
    topic: str
    stage: ProductionStage = ProductionStage.STAGE_1_PREFLIGHT
    progress_pct: int = 0
    message: str = "Job initialized"
    cost_estimate: Optional[StudioCostEstimate] = None
    manifest: Optional[StudioArtifactManifest] = None
    error: Optional[str] = None
    duplicate_conflict: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
