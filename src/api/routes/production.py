"""Mandatory Pre-Flight Cost Estimation and Production Confirmation API routes."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.deps import get_current_user
from src.billing.cost_tracker import calculate_preflight_estimate
from src.core.queue import task_queue
from src.domain.cost import EpisodeCostRecord
from src.domain.creative import Episode
from src.domain.repo import repo
from src.domain.user import User

router = APIRouter(prefix="/api/projects", tags=["Production & Cost Governance"])


class CostItem(BaseModel):
    """Itemized cost component for production pipeline."""

    component: str
    provider: str
    units_measured: str
    unit_cost_usd: float
    total_cost_usd: float


class PreFlightCostEstimateResponse(BaseModel):
    """Itemized pre-flight cost breakdown returned to user before production."""

    episode_id: UUID
    project_title: str
    duration_seconds: int
    estimated_runtime_seconds: int
    items: list[CostItem]
    total_cost_usd: float
    user_credit_balance_usd: float
    can_afford: bool
    has_duplicate_warning: bool = False
    duplicate_warning_message: str | None = None
    conflicting_topic: str | None = None
    similarity_score: float = 0.0
    can_force_proceed: bool = True


class ProductionConfirmationRequest(BaseModel):
    """Confirmation request with optional force_proceed consent for warnings."""

    force_proceed: bool = False


class ProductionConfirmationResponse(BaseModel):
    """Response dispatched once user explicitly clicks Confirm & Produce."""

    job_id: str
    episode_id: UUID
    status: str
    deducted_usd: float
    remaining_balance_usd: float
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@router.post("/{episode_id}/estimate-cost", response_model=PreFlightCostEstimateResponse)
async def estimate_production_cost(
    episode_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Mandatory Step 1: Calculate itemized production cost and runtime without spending tokens."""
    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode project not found")

    # Topic & Metadata Uniqueness Check: Warn user with option to confirm & proceed
    from src.mcp.topic_memory.server import check_topic_duplicate
    show = repo.get_show(current_user.id, episode.show_id)
    show_slug = show.slug if show else "default"
    topic_check = await check_topic_duplicate(
        topic=episode.title,
        metadata={"genre": show.genre if show else "general", "show_slug": show_slug},
    )
    is_dup = topic_check.get("is_duplicate", False)
    warning_msg = topic_check.get("alert_message") if is_dup else None
    conflicting_top = topic_check.get("conflicting_topic") if is_dup else None
    sim_score = topic_check.get("max_similarity_score", 0.0) if is_dup else 0.0

    # Itemized cost computation based on duration and selected options
    duration_mins = max(1, episode.duration_seconds // 60)
    stems_count = len(episode.options.target_languages) if episode.options.enable_tts else 0

    items: list[CostItem] = [
        CostItem(
            component="Creative Script & Retention Loop",
            provider="Gemini 1.5 Pro (Tier 2)",
            units_measured="~14,000 tokens",
            unit_cost_usd=0.00000125,
            total_cost_usd=0.0200,
        ),
        CostItem(
            component=f"Multilingual Neural Voiceovers ({stems_count} Stems)",
            provider="Azure Speech HD (Neural)",
            units_measured=f"~{duration_mins * 600} characters",
            unit_cost_usd=0.000016,
            total_cost_usd=round(0.0700 * max(1, stems_count), 4),
        ),
        CostItem(
            component="4K Keyframe Visual Diffusion",
            provider="Together AI (Flux.1 Schnell)",
            units_measured=f"{duration_mins * 5} keyframe images",
            unit_cost_usd=0.003,
            total_cost_usd=round(duration_mins * 5 * 0.003, 4),
        ),
        CostItem(
            component="Hero Action Motion Synthesis",
            provider="Fal.ai (Minimax Video-01)",
            units_measured="2 cinematic motion clips",
            unit_cost_usd=0.15,
            total_cost_usd=0.3000,
        ),
        CostItem(
            component="Talking Avatar Lip-Sync",
            provider="Fal.ai (LivePortrait)",
            units_measured="45 seconds active speech",
            unit_cost_usd=0.012,
            total_cost_usd=0.5400,
        ),
        CostItem(
            component="Original Commercial Soundtrack",
            provider="Suno v3.5 Pro API",
            units_measured="1 full master track",
            unit_cost_usd=0.08,
            total_cost_usd=0.0800,
        ),
        CostItem(
            component="Python Single-Pass FFmpeg Compositor",
            provider="Azure ACA / Cloud Run (0-GPU CPU)",
            units_measured="~210 seconds render time",
            unit_cost_usd=0.00028,
            total_cost_usd=0.0600,
        ),
    ]

    total_cost = round(sum(it.total_cost_usd for it in items), 4)
    can_afford = current_user.api_credit_balance_usd >= total_cost

    # Persist estimate to episode state
    cost_rec = calculate_preflight_estimate(episode)
    episode.cost_record = cost_rec
    episode.estimated_cost_usd = total_cost
    episode.status = "estimating"
    repo.save_episode(episode)

    return PreFlightCostEstimateResponse(
        episode_id=episode.id,
        project_title=episode.title,
        duration_seconds=episode.duration_seconds,
        estimated_runtime_seconds=210,
        items=items,
        total_cost_usd=total_cost,
        user_credit_balance_usd=round(current_user.api_credit_balance_usd, 4),
        can_afford=can_afford,
        has_duplicate_warning=is_dup,
        duplicate_warning_message=warning_msg,
        conflicting_topic=conflicting_top,
        similarity_score=sim_score,
        can_force_proceed=True,
    )


@router.post("/{episode_id}/confirm-production", response_model=ProductionConfirmationResponse)
async def confirm_production(
    episode_id: UUID,
    payload: Optional[ProductionConfirmationRequest] = None,
    current_user: User = Depends(get_current_user),
):
    """Mandatory Step 2: Explicit confirmation from user to deduct credits and queue render."""
    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode project not found")

    force_proceed = payload.force_proceed if payload else False

    # Topic & Metadata Uniqueness Check: Alert and warn if duplicate content unless user confirms to proceed
    from src.mcp.topic_memory.server import check_topic_duplicate
    show = repo.get_show(current_user.id, episode.show_id)
    show_slug = show.slug if show else "default"
    topic_check = await check_topic_duplicate(
        topic=episode.title,
        metadata={"genre": show.genre if show else "general", "show_slug": show_slug},
    )
    if topic_check.get("is_duplicate") and not force_proceed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "DUPLICATE_TOPIC_WARNING",
                "warning": topic_check.get("alert_message"),
                "conflicting_topic": topic_check.get("conflicting_topic"),
                "similarity_score": topic_check.get("max_similarity_score"),
                "can_force_proceed": True,
                "message": "Similar content detected. Provide force_proceed=true to confirm and proceed anyway.",
            },
        )

    if episode.estimated_cost_usd <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pre-flight cost must be estimated before production confirmation",
        )

    if current_user.api_credit_balance_usd < episode.estimated_cost_usd:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits (${current_user.api_credit_balance_usd:.2f} available, ${episode.estimated_cost_usd:.2f} needed)",
        )

    # Deduct spend and update state
    deducted = episode.estimated_cost_usd
    current_user.api_credit_balance_usd -= deducted
    current_user.updated_at = datetime.now(timezone.utc)
    repo.save_user(current_user)

    episode.status = "queued"
    episode.actual_spend_usd = deducted
    repo.save_episode(episode)

    task = await task_queue.enqueue(
        "produce_video",
        {"user_id": str(current_user.id), "episode_id": str(episode.id)},
    )

    return ProductionConfirmationResponse(
        job_id=task.id,
        episode_id=episode.id,
        status="queued",
        deducted_usd=round(deducted, 4),
        remaining_balance_usd=round(current_user.api_credit_balance_usd, 4),
    )


@router.get("/{episode_id}/cost-breakdown", response_model=EpisodeCostRecord)
async def get_production_cost_breakdown(
    episode_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Retrieve detailed model-by-model predicted vs actual cost breakdown for an episode."""
    episode = repo.get_episode(current_user.id, episode_id)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode project not found")

    if not episode.cost_record:
        episode.cost_record = calculate_preflight_estimate(episode)
        repo.save_episode(episode)

    return episode.cost_record

