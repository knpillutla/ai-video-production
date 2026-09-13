"""Cost Governance Domain Contracts: Pre-Flight Estimation and Post-Execution Actuals."""

from datetime import datetime, timezone
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class ModelCostItem(BaseModel):
    """Itemized cost prediction and measured actuals for an individual AI model."""

    component: str
    model_name: str
    category: str  # scripting, voice, visuals, motion, lipsync, soundtrack, compute
    unit_cost_usd: float
    predicted_units: str
    predicted_cost_usd: float
    actual_units: str | None = None
    actual_cost_usd: float | None = None
    variance_usd: float | None = None  # actual - predicted
    variance_pct: float | None = None  # percentage difference


class EpisodeCostRecord(BaseModel):
    """Unified cost tracking record capturing pre-flight estimates and actualized spend."""

    id: UUID = Field(default_factory=uuid4)
    episode_id: UUID
    project_title: str
    currency: str = "USD"
    predicted_total_usd: float = 0.0
    actual_total_usd: float | None = None
    total_variance_usd: float | None = None
    accuracy_pct: float | None = None
    items: list[ModelCostItem] = Field(default_factory=list)
    status: str = "estimated"  # estimated | actualized
    estimated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    actualized_at: datetime | None = None


__all__ = ["ModelCostItem", "EpisodeCostRecord"]
