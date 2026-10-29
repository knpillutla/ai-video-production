"""Format-specific artifact models for decoupled multi-format video production."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DocumentaryChapter(BaseModel):
    """Sovereign syllabus chapter model for educational documentaries."""
    chapter_index: int
    chapter_key: str
    chapter_title: str
    chapter_subtitle: str = ""
    fact_badge: str = ""
    chapter_stats: str = ""
    location_hub: str = ""
    origin_coords: Optional[List[float]] = None
    narration: str = ""
    estimated_narration_seconds: float = 12.0
    shots: List[Dict[str, Any]] = Field(default_factory=list)


class DocumentaryStoryArtifact(BaseModel):
    """Raw story script artifact containing the 21 sovereign chapters."""
    title: str
    destination_entity: str
    synopsis: str = ""
    total_chapters: int = 21
    chapters: List[DocumentaryChapter] = Field(default_factory=list)
    status: str = "ready"


class DocumentaryArtifacts(BaseModel):
    """Artifact suite for blue-chip 7-stage educational documentary format."""
    format: str = "documentary"
    episode_id: str
    channel_id: str
    title: str
    current_stage: int = 1
    story: Optional[DocumentaryStoryArtifact] = None
    narration: Optional[Dict[str, Any]] = None
    screenplay: Optional[Dict[str, Any]] = None
    keyframes: List[Dict[str, Any]] = Field(default_factory=list)
    bgm_soundtrack: Optional[Dict[str, Any]] = None
    motion_clips: List[Dict[str, Any]] = Field(default_factory=list)
    master_deliverables: List[Dict[str, Any]] = Field(default_factory=list)


class RelaxationArtifacts(BaseModel):
    """Artifact suite for 6-stage biophilic ambient relaxation format."""
    format: str = "relaxation"
    episode_id: str
    channel_id: str
    title: str
    current_stage: int = 1
    storyboard: Optional[Dict[str, Any]] = None
    keyframes: List[Dict[str, Any]] = Field(default_factory=list)
    audio_stems: List[Dict[str, Any]] = Field(default_factory=list)
    motion_clips: List[Dict[str, Any]] = Field(default_factory=list)
    master_deliverables: List[Dict[str, Any]] = Field(default_factory=list)
    long_play_deliverables: List[Dict[str, Any]] = Field(default_factory=list)


class MusicVideoArtifacts(BaseModel):
    """Artifact suite for 5-stage musical dance and vocal performance format."""
    format: str = "music_video"
    episode_id: str
    channel_id: str
    title: str
    current_stage: int = 1
    lyrics: Optional[Dict[str, Any]] = None
    song_master: Optional[Dict[str, Any]] = None
    keyframes: List[Dict[str, Any]] = Field(default_factory=list)
    motion_clips: List[Dict[str, Any]] = Field(default_factory=list)
    master_deliverables: List[Dict[str, Any]] = Field(default_factory=list)
