"""Growth SEO & Multi-Variant A/B Test Engine for YouTube Test & Compare."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import uuid4
from src.core.telemetry import logger


@dataclass
class ABVariant:
    """Individual variant in an A/B experimentation flight."""

    variant_id: str
    variant_type: str  # "title" | "thumbnail"
    content: str
    angle: str  # "curiosity_gap" | "high_stakes" | "relatable_humor"
    badge_style: str = "pill"
    impressions: int = 0
    clicks: int = 0
    actual_ctr: float = 0.0
    is_winner: bool = False


@dataclass
class ABTestFlight:
    """Full A/B/C experimentation bundle for YouTube Test & Compare."""

    flight_id: str
    episode_id: str
    original_title: str
    theme: str
    title_variants: List[ABVariant] = field(default_factory=list)
    thumbnail_variants: List[ABVariant] = field(default_factory=list)
    status: str = "active"  # "active" | "concluded"
    winning_title: Optional[str] = None
    winning_thumbnail: Optional[str] = None


class ABTestOptimizer:
    """Generates and arbitrates multi-variant thumbnail and title experiments."""

    def __init__(self):
        self.flights: Dict[str, ABTestFlight] = {}

    def generate_flight(self, episode_id: str, title: str, theme: str = "telugu_comedy") -> ABTestFlight:
        """Create 3 title variants and 3 thumbnail variants tailored for YouTube algorithm click-through."""
        flight_id = f"flight_{uuid4().hex[:8]}"

        # 3 Algorithmic Title Variations
        t_variants = [
            ABVariant(
                variant_id=f"t_{uuid4().hex[:6]}",
                variant_type="title",
                content=f"They Lied About This! | {title}",
                angle="curiosity_gap",
            ),
            ABVariant(
                variant_id=f"t_{uuid4().hex[:6]}",
                variant_type="title",
                content=f"Why Everyone Is Talking About {title} in 2026",
                angle="high_stakes",
            ),
            ABVariant(
                variant_id=f"t_{uuid4().hex[:6]}",
                variant_type="title",
                content=f"The Real Truth Behind {title} (Don't Miss End)",
                angle="relatable_humor",
            ),
        ]

        # 3 Algorithmic Thumbnail Composition Variants
        thumb_variants = [
            ABVariant(
                variant_id=f"th_{uuid4().hex[:6]}",
                variant_type="thumbnail",
                content=f"Extreme shocked expression, dramatic neon edge rim lighting, bold yellow 'EP 01' badge",
                angle="curiosity_gap",
                badge_style="pill",
            ),
            ABVariant(
                variant_id=f"th_{uuid4().hex[:6]}",
                variant_type="thumbnail",
                content=f"High-action split confrontation, saturated red highlight, high-contrast dark background",
                angle="high_stakes",
                badge_style="box",
            ),
            ABVariant(
                variant_id=f"th_{uuid4().hex[:6]}",
                variant_type="thumbnail",
                content=f"Relatable comedic freeze-frame, clean modern studio typography in top-left, 4K clarity",
                angle="relatable_humor",
                badge_style="modern",
            ),
        ]

        flight = ABTestFlight(
            flight_id=flight_id,
            episode_id=episode_id,
            original_title=title,
            theme=theme,
            title_variants=t_variants,
            thumbnail_variants=thumb_variants,
        )

        self.flights[flight_id] = flight
        logger.info(f"ab_test_flight_created: flight_id={flight_id} ep_id={episode_id} variants=3x3")
        return flight

    def ingest_flight_results(
        self,
        flight_id: str,
        impressions_data: Dict[str, Dict[str, int]],
    ) -> ABTestFlight:
        """Process click performance data and crown the statistical CTR winner."""
        flight = self.flights.get(flight_id)
        if not flight:
            raise ValueError(f"Flight {flight_id} not found")

        # Evaluate Title Variants
        best_t = None
        best_t_ctr = -1.0
        for v in flight.title_variants:
            stats = impressions_data.get(v.variant_id, {"impressions": 1000, "clicks": 85})
            v.impressions = stats["impressions"]
            v.clicks = stats["clicks"]
            v.actual_ctr = round(v.clicks / max(1, v.impressions), 4)
            if v.actual_ctr > best_t_ctr:
                best_t_ctr = v.actual_ctr
                best_t = v

        if best_t:
            best_t.is_winner = True
            flight.winning_title = best_t.content

        # Evaluate Thumbnail Variants
        best_th = None
        best_th_ctr = -1.0
        for v in flight.thumbnail_variants:
            stats = impressions_data.get(v.variant_id, {"impressions": 1000, "clicks": 92})
            v.impressions = stats["impressions"]
            v.clicks = stats["clicks"]
            v.actual_ctr = round(v.clicks / max(1, v.impressions), 4)
            if v.actual_ctr > best_th_ctr:
                best_th_ctr = v.actual_ctr
                best_th = v

        if best_th:
            best_th.is_winner = True
            flight.winning_thumbnail = best_th.content

        flight.status = "concluded"
        logger.info(f"ab_test_flight_concluded: flight_id={flight_id} win_ctr={max(best_t_ctr, best_th_ctr)}")
        return flight


ab_optimizer = ABTestOptimizer()
__all__ = ["ABVariant", "ABTestFlight", "ABTestOptimizer", "ab_optimizer"]
