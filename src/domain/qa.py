"""Quality Assurance and Post-Render Video Verification Domain Entities."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class LoudnessMetrics(BaseModel):
    """Audio loudness metrics adhering to YouTube broadcast standard (-14.0 LUFS)."""

    integrated_lufs: float = Field(description="Integrated loudness target -14.0 LUFS (+/- 1.0)")
    true_peak_dbtp: float = Field(description="True Peak dBTP ceiling <= -1.0")
    loudness_range_lu: float = Field(default=6.0, description="Loudness Range in LU")
    lufs_passed: bool = True


class FrameDefectMetrics(BaseModel):
    """Visual defect metrics detected via FFmpeg / OpenCV scans."""

    black_frame_count: int = 0
    black_duration_seconds: float = 0.0
    frozen_frame_count: int = 0
    frozen_duration_seconds: float = 0.0
    defects_passed: bool = True


class QualityScoreBreakdown(BaseModel):
    """Multi-category score aggregation for QA gate arbitration."""

    audio_score: float = Field(ge=0.0, le=100.0)
    visual_score: float = Field(ge=0.0, le=100.0)
    compliance_score: float = Field(ge=0.0, le=100.0)
    composite_score: float = Field(ge=0.0, le=100.0)
    verdict: str = Field(description="PUBLISH_ELIGIBLE, REVISION_REQUIRED, BLOCKED")


class VideoQAReport(BaseModel):
    """Comprehensive post-render quality assurance audit manifest."""

    report_id: UUID = Field(default_factory=uuid4)
    video_path: str
    duration_seconds: float
    loudness: LoudnessMetrics
    defects: FrameDefectMetrics
    scores: QualityScoreBreakdown
    passed: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


__all__ = [
    "LoudnessMetrics",
    "FrameDefectMetrics",
    "QualityScoreBreakdown",
    "VideoQAReport",
]
