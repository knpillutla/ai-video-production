"""Commercial SaaS Stripe billing and credit wallet API routes."""

from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.domain.repo import repo
from src.domain.user import TIER_QUOTA_LIMITS, SubscriptionTier, User

router = APIRouter(prefix="/api/billing", tags=["Billing & SaaS Subscriptions"])


class CheckoutSessionRequest(BaseModel):
    """Payload to create a Stripe checkout session."""

    plan_tier: SubscriptionTier
    success_url: str = "https://app.cineai.studio/billing?session_id={CHECKOUT_SESSION_ID}"
    cancel_url: str = "https://app.cineai.studio/billing?cancelled=true"


class CheckoutSessionResponse(BaseModel):
    """Stripe checkout session metadata."""

    session_id: str
    checkout_url: str
    plan_tier: SubscriptionTier


class CreditTopUpRequest(BaseModel):
    """Payload to instantly purchase studio generation credits."""

    amount_usd: float = Field(gt=0, description="Amount in USD to add to wallet")


class SubscriptionOverviewResponse(BaseModel):
    """Complete subscription and usage quota overview."""

    subscription_tier: SubscriptionTier
    credit_balance_usd: float
    storage_container: str
    quota_limits: dict[str, int | float]
    stripe_customer_id: str | None = None


class StripeWebhookPayload(BaseModel):
    """Stripe event payload simulation."""

    event_type: str
    user_id: str
    new_tier: SubscriptionTier | None = None
    credit_delta: float = 0.0


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    req: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a Stripe checkout session for subscription upgrades or purchases."""
    session_id = f"cs_test_{uuid4().hex[:16]}"
    # Mock or real Stripe checkout redirection URL
    checkout_url = f"https://checkout.stripe.com/pay/{session_id}"

    # Associate mock customer ID if not present
    if not current_user.stripe_customer_id:
        current_user.stripe_customer_id = f"cus_{uuid4().hex[:14]}"
        repo.save_user(current_user)

    return CheckoutSessionResponse(
        session_id=session_id,
        checkout_url=checkout_url,
        plan_tier=req.plan_tier,
    )


@router.get("/subscription", response_model=SubscriptionOverviewResponse)
async def get_subscription_overview(current_user: User = Depends(get_current_user)):
    """Retrieve the current user's subscription tier, credit balance, and quotas."""
    quotas = TIER_QUOTA_LIMITS.get(current_user.subscription_tier, TIER_QUOTA_LIMITS[SubscriptionTier.CREATOR])
    return SubscriptionOverviewResponse(
        subscription_tier=current_user.subscription_tier,
        credit_balance_usd=round(current_user.api_credit_balance_usd, 4),
        storage_container=current_user.storage_container_name,
        quota_limits=quotas,
        stripe_customer_id=current_user.stripe_customer_id,
    )


@router.post("/topup-credits", response_model=SubscriptionOverviewResponse)
async def topup_credits(
    req: CreditTopUpRequest,
    current_user: User = Depends(get_current_user),
):
    """Instantly add generation credits to the user's wallet via Stripe."""
    current_user.api_credit_balance_usd += req.amount_usd
    current_user.updated_at = datetime.now(timezone.utc)
    saved_user = repo.save_user(current_user)

    quotas = TIER_QUOTA_LIMITS.get(saved_user.subscription_tier, TIER_QUOTA_LIMITS[SubscriptionTier.CREATOR])
    return SubscriptionOverviewResponse(
        subscription_tier=saved_user.subscription_tier,
        credit_balance_usd=round(saved_user.api_credit_balance_usd, 4),
        storage_container=saved_user.storage_container_name,
        quota_limits=quotas,
        stripe_customer_id=saved_user.stripe_customer_id,
    )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(payload: StripeWebhookPayload):
    """Process incoming Stripe billing events (subscription updates, cancellations, credit top-ups)."""
    from uuid import UUID

    try:
        user_uuid = UUID(payload.user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user_id format")

    user = repo.users.get(user_uuid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found for Stripe event")

    if payload.event_type in ("checkout.session.completed", "customer.subscription.updated"):
        if payload.new_tier:
            user.subscription_tier = payload.new_tier
        if payload.credit_delta > 0:
            user.api_credit_balance_usd += payload.credit_delta
        user.updated_at = datetime.now(timezone.utc)
        repo.save_user(user)

    elif payload.event_type == "customer.subscription.deleted":
        user.subscription_tier = SubscriptionTier.FREE
        user.updated_at = datetime.now(timezone.utc)
        repo.save_user(user)

    return {"status": "processed", "user_id": str(user.id), "tier": user.subscription_tier}
