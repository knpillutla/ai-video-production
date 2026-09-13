"""Distribution Domain models: Channels, Credentials, and Upload Ledgers."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ChannelBase(BaseModel):
    """Distribution channel attributes."""

    platform: str = "youtube"  # youtube | tiktok | instagram
    channel_name: str
    channel_handle: str | None = None
    default_tags: list[str] = Field(default_factory=list)


class ChannelCreate(ChannelBase):
    """Payload to configure a new distribution channel."""

    oauth_credentials_json: str = ""


class Channel(ChannelBase):
    """Distribution channel entity owned by user."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChannelPublication(BaseModel):
    """Audit ledger record of an episode published to a channel."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    episode_id: UUID
    channel_id: UUID
    platform: str = "youtube"
    platform_video_id: str | None = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "published"  # pending | published | failed
    synthetic_media_disclosed: bool = True
    selected_language_thumbnail: str | None = None
    multi_language_audio_tracks: list[str] = Field(default_factory=list)


class ScheduleJobBase(BaseModel):
    """Autonomous recurring schedule attributes."""

    theme: str = "telugu_comedy"
    format: str = "web_series"
    visual_style: str = "realistic"
    cadence: str = "daily"  # daily | weekly
    time_of_day_utc: str = "06:00"
    target_languages: list[str] = Field(default_factory=lambda: ["te", "hi", "en"])
    auto_publish: bool = False
    auto_publish_channel_id: UUID | None = None


class ScheduleJobCreate(ScheduleJobBase):
    """Payload to schedule recurring video creation."""

    show_id: UUID


class ScheduleJob(ScheduleJobBase):
    """Scheduled autonomous generation entity."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    show_id: UUID
    is_active: bool = True
    last_run_at: datetime | None = None
    total_videos_created: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
