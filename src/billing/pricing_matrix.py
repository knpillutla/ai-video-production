"""Production Tier, SLA Matrix, and Customer Credit Pricing Service."""

import json
from pathlib import Path
from typing import Any

from src.billing.benchmark_db import calculate_customer_credit_capacity, estimate_turnaround_time_sla, query_empirical_cost_multiplier
from src.core.telemetry import logger

PRICING_SPEC_PATH = Path("storage/pricing_and_sla_matrix.json")


def get_production_tier_spec(target_duration: float = 15.0) -> dict[str, Any]:
    """Retrieve calibrated production specifications, delivery SLAs, and customer pricing."""
    dur = max(5.0, float(target_duration))
    sla = estimate_turnaround_time_sla(dur)
    benchmark = query_empirical_cost_multiplier(dur)
    cogs_per_sec = benchmark.get("cost_per_second") or 0.0367

    cogs_usd = round(cogs_per_sec * dur, 2)
    customer_usd = round(cogs_usd * 3.0, 2)  # 67% gross margin standard
    credits = int(customer_usd * 100)

    quality_spec = {
        15: {"tier": "Shorts / Reels Ultra", "fps": 60, "optics": "Leica 24mm Wide", "cogs": cogs_usd, "price": customer_usd, "credits": credits},
        30: {"tier": "Viral Hook Clip", "fps": 60, "optics": "Arri 50mm Prime", "cogs": cogs_usd, "price": customer_usd, "credits": credits},
        60: {"tier": "Full YouTube Short", "fps": 30, "optics": "Cooke Anamorphic", "cogs": cogs_usd, "price": customer_usd, "credits": credits},
        120: {"tier": "Mini-Story / Commercial", "fps": 24, "optics": "Arri 85mm Portrait", "cogs": cogs_usd, "price": customer_usd, "credits": credits},
        300: {"tier": "Blue-Chip Documentary / Tour", "fps": 24, "optics": "Super35 Cinematic", "cogs": cogs_usd, "price": customer_usd, "credits": credits},
    }

    tier_info = quality_spec.get(int(dur), {
        "tier": f"Custom {int(dur)}s Production",
        "fps": 30, "optics": "Cinematic Optical Prime",
        "cogs": cogs_usd, "price": customer_usd, "credits": credits,
    })

    return {
        "duration_seconds": dur,
        "package_name": tier_info["tier"],
        "delivery_sla": sla["expected_display"],
        "delivery_range": sla["range_display"],
        "turnaround_seconds": sla["expected_seconds"],
        "internal_cogs_usd": cogs_usd,
        "customer_price_usd": customer_usd,
        "credits_required": credits,
        "fps": tier_info["fps"],
        "optics": tier_info["optics"],
        "resolution": "4K UHD (3840x2160)",
        "audio": "48kHz 24-bit Stereo with -18dB Ducking & Procedural Foley",
        "color_grade": "Kodak 2383 / Film Print Emulation",
        "rights": "100% Commercial Master Rights (Zero Content ID)",
    }


def generate_and_save_pricing_matrix_report() -> dict[str, Any]:
    """Compile and persist the updated production pricing and SLA matrix based on empirical benchmarks."""
    durations = [15, 30, 60, 120, 300]
    tiers = [get_production_tier_spec(d) for d in durations]
    top_up_packs = [
        {"name": "Starter Top-Up", "price_usd": 10.0, "credits": 1000, "capacity": "6x 15s Shorts or 3x 30s Videos", "cogs_usd": 3.30, "margin_pct": 67.0},
        {"name": "Creator Pack", "price_usd": 29.0, "credits": 3200, "capacity": "20x 15s Shorts or 5x 60s Videos", "cogs_usd": 9.50, "margin_pct": 67.2},
        {"name": "Studio Pro Pack", "price_usd": 99.0, "credits": 12000, "capacity": "75x 15s Shorts or 20x 60s Videos", "cogs_usd": 32.00, "margin_pct": 67.7},
    ]

    report = {
        "schema_version": "1.0.0",
        "currency": "USD",
        "credit_rate": "100 Credits = $1.00 USD",
        "production_tiers": tiers,
        "top_up_packages": top_up_packs,
        "credit_capacity_10_usd": calculate_customer_credit_capacity(10.0),
    }

    try:
        PRICING_SPEC_PATH.parent.mkdir(parents=True, exist_ok=True)
        PRICING_SPEC_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info(f"pricing_matrix_report_saved: {PRICING_SPEC_PATH}")
    except Exception as ex:
        logger.warning(f"pricing_matrix_report_save_failed: {ex}")

    return report


__all__ = [
    "get_production_tier_spec",
    "generate_and_save_pricing_matrix_report",
]
