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
