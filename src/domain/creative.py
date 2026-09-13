"""Creative Domain models: Shows, Persistent Characters, and Episodes."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from src.domain.cost import EpisodeCostRecord
from src.domain.generation import AspectRatio, GenerationOptions, MediaFormat, VisualStyle


class ShowBase(BaseModel):
    """Base show/title universe attributes."""

    title: str
    slug: str
    genre: str = "comedy"
    synopsis: str = ""


class ShowCreate(BaseModel):
    """Payload to create a show universe."""

    title: str
    genre: str = "comedy"
    synopsis: str = ""


class Show(ShowBase):
    """Show universe entity owned by user."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CharacterBase(BaseModel):
    """Persistent character attributes across episodes."""

    name: str
    age_bracket: str = "20s"
    gender: str = "unspecified"
    backstory: str = ""
    voice_profile_id: str = "azure_ravi_neural"


class CharacterCreate(CharacterBase):
    """Payload to add a character to a show universe."""

    pass


class Character(CharacterBase):
    """Persistent character entity tied to a show and user."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    show_id: UUID
    face_embedding_path: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EpisodeBase(BaseModel):
    """Episode metadata and render configuration."""

    title: str
    episode_number: int = 1
    duration_seconds: int = 480
    format: MediaFormat = MediaFormat.WEB_SERIES
    visual_style: VisualStyle = VisualStyle.REALISTIC
    aspect_ratio: AspectRatio = AspectRatio.LANDSCAPE_16_9
    options: GenerationOptions = Field(default_factory=GenerationOptions)


class EpisodeCreate(EpisodeBase):
    """Payload to initiate a new episode under a show."""

    show_id: UUID
    topic_or_idea: str = ""
    youtube_reference_url: str | None = None


class Episode(EpisodeBase):
    """Episode project entity."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    show_id: UUID
    status: str = "draft"  # draft | estimating | queued | rendering | completed | failed
    estimated_cost_usd: float = 0.0
    actual_spend_usd: float = 0.0
    compliance_score: float = 0.0
    master_video_path: str | None = None
    evidence_bundle_path: str | None = None
    cost_record: EpisodeCostRecord | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
