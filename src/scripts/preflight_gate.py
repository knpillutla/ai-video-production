"""Interactive Pre-Flight Cost, Quota, and Production Mode Gate."""

from typing import Any
from src.core.telemetry import logger
from src.domain.cost import EpisodeCostRecord
from src.domain.creative import Episode
from src.domain.user import User
from src.mcp.model_selector.server import audit_provider_credits, select_best_model


async def execute_preflight_gate(
    episode: Episode,
    user: User,
    language: str = "en",
    auto_confirm: bool = False,
    local_flag: bool = False,
) -> tuple[str, bool]:
    """Execute pre-flight cost display, quota audit, mode recommendation, and user confirmation.

    Returns:
        tuple[str, bool]: (selected_mode: "live" | "local" | "cancel", allow_fallback: bool)
    """
    print("\n" + "=" * 70)
    print(" PRE-FLIGHT COST ESTIMATION & MODEL BREAKDOWN (RULE 7 GATE)")
    print("=" * 70)
    print(f" {'Component / Task':<26} {'Model / Engine':<22} {'Est. Units':<13} {'Est. Spend':<10}")
    print("-" * 70)
    if episode.cost_record and episode.cost_record.items:
        for item in episode.cost_record.items:
            print(f" - {item.component[:24]:<24} {item.model_name[:20]:<20} {str(item.predicted_units)[:11]:<11} ${item.predicted_cost_usd:.4f}")

    print("-" * 70)
    print(" MCP ROUTING STRATEGY & SELECTION RATIONALE:")
    for cat, name in [("script_creative", "Scripting"), ("voice_tts", "Voiceover"), ("visual_image", "Visuals"), ("music_bgm", "BGM")]:
        dec = await select_best_model(category=cat, language=language)
        print(f" - {name} [{dec['provider']} {dec['selected_model']}]: {dec['selection_reasoning']}")

    print("-" * 70)
    print(f" TOTAL ESTIMATED SPEND:    ${episode.estimated_cost_usd:.4f} USD")
    print(f" USER CREDIT BALANCE:      ${user.api_credit_balance_usd:.4f} USD")
    can_afford = user.api_credit_balance_usd >= episode.estimated_cost_usd
    print(f" AFFORDABILITY STATUS:     {'APPROVED' if can_afford else 'INSUFFICIENT CREDITS'}")
    print("=" * 70)

    # 1. Audit AI Provider Health and Quota Status
    health = await audit_provider_credits(force_probe=True, strict_production=True)
    print(" AI PROVIDER CREDITS & QUOTA AUDIT (MCP SERVER):")
    print("-" * 70)
    for p in health["providers"]:
        status_tag = f"[{p['status']}]"
        print(f" - {p['provider_name']:<24} {status_tag:<14} {p['quota_details']}")
    print("-" * 70)

    # 2. Formulate Recommendation
    has_depleted = not health["production_ready"]
    if local_flag:
        rec_mode = "LOCAL"
        rec_reason = "User explicitly specified --local mode flag."
    elif has_depleted:
        rec_mode = "LOCAL"
        blockers_str = "; ".join(health["blockers"][:2])
        rec_reason = f"Cloud provider quota depleted ({blockers_str})."
    else:
        rec_mode = "LIVE"
        rec_reason = "All AI cloud providers active with valid API credits."

    print(" ENGINE RECOMMENDATION & PRODUCTION MODE SELECTION:")
    print("-" * 70)
    print(f" - System Recommendation:   {rec_mode} MODE")
    print(f" - Rationale:               {rec_reason}")
    print("-" * 70)

    if not can_afford and rec_mode == "LIVE":
        print(f"[!] Warning: Insufficient studio credits for live mode. Local mode is recommended.")

    # 3. Interactive Confirmation Prompt with Mode Switching
    if auto_confirm:
        if local_flag or has_depleted:
            print(f"[i] Auto-selected {rec_mode} mode (--yes flag provided).\n")
            return "local", True
        return "live", False

    print(" Options Available:")
    if has_depleted:
        print("  [1] Generate in LOCAL mode (Recommended: offline synthesis, zero API spend)")
        print("  [2] Cancel and top up cloud provider credits")
        try:
            choice = input("\nSelect option [1/2] or [L/c] (Default: 1 - Local): ").strip().lower()
            if choice in ("2", "c", "cancel", "no", "n"):
                return "cancel", False
            return "local", True
        except EOFError:
            return "local", True
    else:
        print("  [1] Proceed with LIVE cloud production (Recommended: full photorealism & neural voice)")
        print("  [2] Switch to LOCAL mode (Zero API spend, offline synthesis)")
        print("  [3] Cancel production")
        try:
            choice = input("\nSelect option [1/2/3] or [Y/l/c] (Default: 1 - Live): ").strip().lower()
            if choice in ("2", "l", "local"):
                return "local", True
            if choice in ("3", "c", "cancel", "no", "n"):
                return "cancel", False
            return "live", False
        except EOFError:
            return "live", False


__all__ = ["execute_preflight_gate"]
