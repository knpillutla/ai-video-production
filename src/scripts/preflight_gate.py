"""Interactive Pre-Flight Cost, Quota, Production Tiers, and Mode Gate."""

from typing import Any
from src.core.telemetry import logger
from src.domain.cost import EpisodeCostRecord
from src.domain.creative import Episode
from src.domain.user import User
from src.mcp.model_selector.server import audit_provider_credits, select_best_model
from src.mcp.model_selector.tier_resolver import recommend_production_tiers


def _normalize_tier_choice(raw: str, default: str = "balanced") -> str:
    """Normalize user input or CLI flag into a canonical tier key."""
    val = raw.strip().lower()
    if val in ("1", "low", "low_cost", "quick", "test"):
        return "low_cost"
    if val in ("2", "bal", "balanced", "std", "creator"):
        return "balanced"
    if val in ("3", "cine", "cinematic", "movie", "high"):
        return "cinematic"
    if val in ("4", "l", "local", "offline"):
        return "local"
    return default


async def execute_preflight_gate(
    episode: Episode,
    user: User,
    language: str = "en",
    auto_confirm: bool = False,
    local_flag: bool = False,
    cli_tier: str | None = None,
) -> tuple[str, bool, str]:
    """Display pre-flight cost breakdown, 3 production tiers, quota audit, and prompt user selection.

    Returns:
        tuple[str, bool, str]: (selected_mode: "live" | "local" | "cancel", allow_fallback: bool, selected_tier: str)
    """
    tiers_data = recommend_production_tiers(
        metadata={"language": language},
        duration_seconds=float(episode.duration_seconds),
        scenes_count=4,
    )
    tiers = tiers_data["tiers"]
    t_low, t_bal, t_cine = tiers["low_cost"], tiers["balanced"], tiers["cinematic"]

    print("\n" + "=" * 74)
    print(" PRE-FLIGHT COST ESTIMATION & PRODUCTION OPTIONS (RULE 7 GATE)")
    print("=" * 74)
    print(" 3 PRODUCTION TIERS AVAILABLE (MODEL SELECTOR MCP SERVER):")
    print("-" * 74)
    print(f" [1] Low-Cost Quick Test:        ${t_low['total_cost_usd']:.4f} USD")
    print(f"     Stack: Gemini 1.5 Flash + FLUX Schnell + Edge TTS + Pan-Zoom")
    print(f"     Best for: {t_low['target_use_case']}")
    print(f" [2] Balanced Creator Standard:  ${t_bal['total_cost_usd']:.4f} USD  (Recommended Default)")
    print(f"     Stack: Gemini 1.5 Pro + FLUX Schnell + Azure Neural HD + Suno BGM")
    print(f"     Best for: {t_bal['target_use_case']}")
    print(f" [3] High-Fidelity Movie-Like:   ${t_cine['total_cost_usd']:.4f} USD")
    print(f"     Stack: Claude/Pro + FLUX Dev + ElevenLabs Acting + LivePortrait + Vocal Song")
    print(f"     Best for: {t_cine['target_use_case']}")
    print(f" [4] Local Mode (Zero Cost):     $0.0000 USD  (Local mock/synthesizer)")
    print("-" * 74)
    print(f" USER CREDIT BALANCE:            ${user.api_credit_balance_usd:.4f} USD")
    print("=" * 74)

    # 1. Audit AI Provider Health and Quota Status
    health = await audit_provider_credits(force_probe=True, strict_production=True)
    print(" AI PROVIDER CREDITS & QUOTA AUDIT (MCP SERVER):")
    print("-" * 74)
    for p in health["providers"]:
        status_tag = f"[{p['status']}]"
        print(f" - {p['provider_name']:<24} {status_tag:<14} {p['quota_details']}")
    print("-" * 74)

    # 2. Formulate Recommendation
    has_depleted = not health["production_ready"]
    if local_flag:
        rec_mode, rec_reason = "LOCAL", "User specified --local flag."
    elif has_depleted:
        blockers = "; ".join(health["blockers"][:2])
        rec_mode, rec_reason = "LOCAL", f"Cloud quota depleted ({blockers})."
    else:
        rec_mode, rec_reason = "LIVE (Balanced)", "All AI cloud providers active with valid credits."

    print(" ENGINE RECOMMENDATION:")
    print(f" - System Recommendation:   {rec_mode}")
    print(f" - Rationale:               {rec_reason}")
    print("-" * 74)

    # 3. Handle explicit CLI tier flag or Auto-Confirm
    if cli_tier:
        norm_tier = _normalize_tier_choice(cli_tier)
        if norm_tier == "local" or local_flag:
            return "local", True, norm_tier
        if has_depleted:
            print(f"[!] Alert: Cloud quota depleted for live tier '{norm_tier}'. Local mode recommended.")
        return "live", False, norm_tier

    if auto_confirm:
        if local_flag or has_depleted:
            print(f"[i] Auto-selected LOCAL mode (--yes flag provided).\n")
            return "local", True, "local"
        return "live", False, "balanced"

    # 4. Interactive Confirmation & Tier Selection Prompt
    print(" Select Production Option:")
    if has_depleted:
        print("  [1] Low-Cost Quick Test (~$" + f"{t_low['total_cost_usd']:.4f} USD - May fail if quota exhausted)")
        print("  [2] Balanced Creator Standard (~$" + f"{t_bal['total_cost_usd']:.4f} USD)")
        print("  [3] High-Fidelity Movie-Like (~$" + f"{t_cine['total_cost_usd']:.4f} USD)")
        print("  [4] Generate in LOCAL mode (Recommended: offline synthesis, zero API spend)")
        print("  [5] Cancel and top up cloud provider credits")
        try:
            choice = input("\nSelect tier [1/2/3/4/5] (Default: 4 - Local Mode): ").strip().lower()
            if choice in ("5", "c", "cancel", "no", "n"):
                return "cancel", False, "cancel"
            if choice in ("1", "low", "low_cost", "quick"):
                return "live", False, "low_cost"
            if choice in ("2", "bal", "balanced"):
                return "live", False, "balanced"
            if choice in ("3", "cine", "cinematic", "movie"):
                return "live", False, "cinematic"
            return "local", True, "local"
        except EOFError:
            return "local", True, "local"
    else:
        print("  [1] Low-Cost Quick Test (~$" + f"{t_low['total_cost_usd']:.4f} USD - Rapid validation)")
        print("  [2] Balanced Creator Standard (~$" + f"{t_bal['total_cost_usd']:.4f} USD - Recommended Default)")
        print("  [3] High-Fidelity Movie-Like (~$" + f"{t_cine['total_cost_usd']:.4f} USD - Maximum fidelity)")
        print("  [4] Switch to LOCAL mode ($0.0000 USD, zero external API spend)")
        print("  [5] Cancel production")
        try:
            choice = input("\nSelect tier [1/2/3/4/5] (Default: 2 - Balanced): ").strip().lower()
            if choice in ("5", "c", "cancel", "no", "n"):
                return "cancel", False, "cancel"
            if choice in ("1", "low", "low_cost", "quick"):
                return "live", False, "low_cost"
            if choice in ("3", "cine", "cinematic", "movie"):
                return "live", False, "cinematic"
            if choice in ("4", "l", "local"):
                return "local", True, "local"
            return "live", False, "balanced"
        except EOFError:
            return "live", False, "balanced"


__all__ = ["execute_preflight_gate"]
