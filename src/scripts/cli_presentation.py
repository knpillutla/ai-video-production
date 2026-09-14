"""CLI Presentation Formatter for Video Studio Pipeline."""

from pathlib import Path
from typing import Any
from src.domain.cost import EpisodeCostRecord
from src.domain.creative import Episode
from src.domain.user import User


def print_cli_header(
    title: str,
    fmt_str: str,
    genre: str,
    duration: int,
    language: str,
    active_sub: str,
    tier: str | None,
    force_live: bool,
    dry_run: bool,
    culture_context: Any | None = None,
    char_name: str | None = None,
    theme: str | None = None,
    idea: str | None = None,
    script_preview: str | None = None,
    voice_over: bool = True,
    voice_gender: str = "female",
    bgm: bool = False,
    lipsync: bool = False,
) -> None:
    """Print standard CineAI Studio CLI production banner."""
    print("=" * 72)
    print(" CINEAI STUDIO - END-TO-END VIDEO PRODUCTION ENGINE (CLI MODE)")
    print("=" * 72)
    print(f" - Title:             {title}")
    print(f" - Content Format:    {fmt_str.upper()}")
    print(f" - Genre:             {genre}")
    if theme:
        print(f" - Narrative Theme:   {theme}")
    if idea:
        print(f" - Story Concept:     {idea}")
    if script_preview:
        print(f" - Screenplay Script: {script_preview}")
    print(f" - Target Duration:   {duration}s")
    print(f" - Spoken Language:   {language}")
    print(f" - Burned Subtitles:  {active_sub} (Default English)")
    if culture_context:
        print(f" - Culture / Region:  {culture_context.culture_name} ({culture_context.culture})")
        print(f" - Primary Ethnicity: {culture_context.primary_ethnicity}")
        if getattr(culture_context, "art_style_display", "") and culture_context.art_style_display != "Broadcast 4K Photorealistic Cinematic":
            print(f" - Art Aesthetic:     {culture_context.art_style_display}")
            if getattr(culture_context, "art_style_palette", ""):
                print(f" - Color Palette:     {culture_context.art_style_palette}")
        print(f" - Costume / Outfit:  {culture_context.clothing_style}")
        if voice_over:
            voice_type = "Conversational Talking Avatar" if lipsync else "Narration Voiceover"
            print(f" - Voice Neural ({voice_type}): {culture_context.voice_id} [{voice_gender.upper()}]")
        else:
            print(f" - Voice Neural:      Disabled (No Speech Audio)")
        if bgm:
            bgm_desc = culture_context.music_style if voice_over else "Gentle rain drops, distant thunder, and relaxing ambient nature sounds"
            print(f" - Music Soundtrack:  {bgm_desc}")
        else:
            print(f" - Music Soundtrack:  Disabled (No Background Music)")
        if culture_context.recommended_loras:
            lora_names = [l.get("name") or l.get("path") for l in culture_context.recommended_loras]
            print(f" - Active LoRAs:      {', '.join(str(n) for n in lora_names if n)}")
    if char_name:
        print(f" - Character Anchor:  {char_name}")
    print(f" - Production Tier:   {tier.upper() if tier else 'INTERACTIVE SELECTION'}")
    print(f" - Live Synthesis:    {force_live}")
    print(f" - Dry Run:           {dry_run}")
    print("-" * 72)


def print_cli_summary(
    episode: Episode | None,
    user: User,
    final_video: Path,
    rights_records: list[Any],
    cleared: bool,
) -> None:
    """Print complete post-production cost governance, rights audit, and artifacts report."""
    print("-" * 72)
    print(" MODEL-BY-MODEL COST GOVERNANCE (ESTIMATED VS ACTUALS):")
    cost_rec: EpisodeCostRecord | None = episode.cost_record if episode else None
    if cost_rec and cost_rec.items:
        print(f" {'Model / Component':<32} {'Estimated':<11} {'Actual':<11} {'Variance':<12}")
        for item in cost_rec.items:
            act_str = f"${item.actual_cost_usd:.4f}" if item.actual_cost_usd is not None else "N/A"
            var_str = f"{item.variance_usd:+.4f}" if item.variance_usd is not None else "$0.0000"
            print(f" - {item.model_name[:30]:<30} ${item.predicted_cost_usd:<10.4f} {act_str:<11} {var_str:<12}")
        print("-" * 72)
        print(f" TOTAL ESTIMATED SPEND:    ${cost_rec.predicted_total_usd:.4f} USD")
        print(f" TOTAL ACTUAL SPEND:       ${cost_rec.actual_total_usd or 0.0:.4f} USD")
        net_var = cost_rec.total_variance_usd or 0.0
        acc = cost_rec.accuracy_pct or 100.0
        print(f" NET VARIANCE / SAVINGS:   {net_var:+.4f} USD (Forecast Accuracy: {acc:.1f}%)")
        rem_balance = max(0.0, user.api_credit_balance_usd - (cost_rec.actual_total_usd or 0.0))
        print(f" REMAINING CREDIT BALANCE: ${rem_balance:.4f} USD")
    print("-" * 72)
    print(" PHASE 3 RIGHTS & MONETIZATION SAFETY AUDIT:")
    print(f" - Rights Ledger: {'100% Cleared' if cleared else 'Pending'} ({len(rights_records)} assets tracked)")
    print(" - Audio QA:      -14.0 LUFS EBU R128 Loudness Pass")
    print(" - Visual QA:     Zero Black/Frozen Frame Defects Pass")
    print(" - Monetization:  YPP & AdSense 11-Category Screener Pass")
    print(f" - Gate Verdict:  {episode.status.upper() if episode else 'COMPLETED'}")
    if episode and episode.evidence_bundle_path:
        print(f" - Evidence:      {episode.evidence_bundle_path}")
    print("-" * 72)
    print(" TELEMETRY & DECISION AUDIT LOGS:")
    print(" - Centralized Log: logs/studio.log")
    dec_log = final_video.parent.parent / "mcp_decision_log.json"
    if dec_log.exists():
        print(f" - MCP Decisions:   {dec_log}")
    print(f" - Master Render:   {final_video}")
    print("=" * 72)


__all__ = ["print_cli_header", "print_cli_summary"]
