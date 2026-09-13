"""User identity, authentication, and subscription domain models."""

from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    """User billing and quota tiers."""

    FREE = "free"
    CREATOR = "creator"
    PRO_STUDIO = "pro_studio"
    ENTERPRISE = "enterprise"


class UserBase(BaseModel):
    """Base user profile attributes."""

    email: str
    display_name: str
    avatar_url: str | None = None
    subscription_tier: SubscriptionTier = SubscriptionTier.CREATOR


class UserCreate(UserBase):
    """Payload to register or upsert a user via Google OAuth."""

    google_sub: str


class User(UserBase):
    """Authenticated user domain entity."""

    id: UUID = Field(default_factory=uuid4)
    google_sub: str
    storage_container_name: str
    api_credit_balance_usd: float = 10.0000
    stripe_customer_id: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserSubscription(BaseModel):
    """Active subscription status and usage quota tracking."""

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    plan_tier: SubscriptionTier
    status: str = "active"
    monthly_render_minutes_quota: int = 60
    monthly_render_minutes_used: int = 0
    storage_limit_gb: int = 50
    current_period_end: datetime | None = None


TIER_QUOTA_LIMITS: dict[SubscriptionTier, dict[str, int | float]] = {
    SubscriptionTier.FREE: {
        "monthly_minutes": 10,
        "storage_gb": 5,
        "included_credits": 2.00,
        "max_resolution": 720,
    },
    SubscriptionTier.CREATOR: {
        "monthly_minutes": 120,
        "storage_gb": 50,
        "included_credits": 30.00,
        "max_resolution": 1080,
    },
    SubscriptionTier.PRO_STUDIO: {
        "monthly_minutes": 480,
        "storage_gb": 250,
        "included_credits": 90.00,
        "max_resolution": 2160,
    },
    SubscriptionTier.ENTERPRISE: {
        "monthly_minutes": 2000,
        "storage_gb": 1000,
        "included_credits": 300.00,
        "max_resolution": 2160,
    },
}
