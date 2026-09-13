"""CLI Entrypoint to Produce an Episode Video in Phase 2 & 3."""

import argparse
import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.agents.classifier_agent import classifier_agent
from src.billing.cost_tracker import calculate_preflight_estimate
from src.compliance.rights_ledger import rights_ledger
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary, has_ffmpeg
from src.compositor.pipeline import pipeline_coordinator
from src.core.telemetry import logger
from src.domain.creative import Episode, Show
from src.domain.generation import MediaFormat
from src.domain.repo import repo
from src.domain.user import User
from src.mcp.model_selector.tier_resolver import recommend_production_tiers
from src.scripts.cli_presentation import print_cli_header, print_cli_summary
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.preflight_gate import execute_preflight_gate
from src.services.cultural_derivation import derive_cultural_context


async def run_production(
    title: str = "IT Employee WFH Confusions",
    episode_number: int = 1,
    genre: str = "comedy",
    duration: int = 480,
    language: str = "te",
    dry_run: bool = False,
    subtitle_language: str | None = None,
    force_live: bool = False,
    auto_confirm: bool = False,
    allow_fallback: bool = False,
    local: bool = False,
    tier: str | None = None,
    media_format: str = "auto",
    country: str | None = None,
    culture: str | None = None,
    costume_style: str | None = None,
    dance_type: str | None = None,
    character_name: str | None = None,
    gender: str = "female",
    art_style: str | None = None,
):
    """Execute the Phase 2 & 3 end-to-end video production and compliance pipeline."""
    active_sub = subtitle_language or ("en" if language.lower() != "en" else "en")

    # Format resolution (Auto-Detect or Explicit)
    if not media_format or media_format.lower() == "auto":
        detected = classifier_agent.detect(text=f"{genre} {title}", title=title)
        resolved_format = detected.media_format
    else:
        fmt_key = media_format.lower().replace("-", "_")
        try:
            resolved_format = MediaFormat(fmt_key)
        except ValueError:
            resolved_format = MediaFormat.WEB_SERIES

    fmt_str = resolved_format.value
    if resolved_format == MediaFormat.TRAVEL_GUIDE:
        ep_title = f"{title} - Travel Guide" if "guide" not in title.lower() else title
        badge_label, headline = "TRAVEL GUIDE", f"{title} GUIDE!"
    elif resolved_format == MediaFormat.VLOG:
        ep_title = f"{title} - Travel Vlog" if "vlog" not in title.lower() else title
        badge_label, headline = "VLOG", f"{title} VLOG!"
    elif resolved_format == MediaFormat.MOVIE_CINEMATIC:
        ep_title, badge_label, headline = title, "FILM", title
    elif resolved_format in (
        MediaFormat.SCENIC_RELAXATION, MediaFormat.WALKING_TOUR, MediaFormat.SCENIC_DRIVE,
        MediaFormat.AMBIENT_LOUNGE, MediaFormat.NATURE_SANCTUARY,
    ):
        badge_label = resolved_format.value.upper().replace("_", " ")
        ep_title, headline = title, f"{title} 4K!"
    else:
        ep_title = f"{title} - Episode {episode_number}"
        badge_label, headline = None, f"{title} EP {episode_number:02d}!"

    # 1. Initialize or load local user and record country/cultural preferences
    user = repo.get_user_by_email("creator@cineai.studio")
    if not user:
        user = User(
            email="creator@cineai.studio",
            display_name="Studio Director",
            google_sub="cli_local_user",
            storage_container_name="user-cli-director",
            api_credit_balance_usd=50.00,
            home_country=country,
            cultural_heritage=culture,
        )
        repo.save_user(user)
    else:
        if country:
            user.home_country = country
        if culture:
            user.cultural_heritage = culture
        repo.save_user(user)

    # 2. Derive cultural context and print interactive header
    culture_context = derive_cultural_context(
        script_text=f"{genre} {title}",
        user_home_country=user.home_country,
        user_cultural_heritage=user.cultural_heritage,
        language=language,
        gender=gender,
        genre=genre,
        dance_type=dance_type or "",
        video_format=fmt_str,
        art_style=art_style or "",
    )
    print_cli_header(
        title=ep_title, fmt_str=fmt_str, genre=genre, duration=duration,
        language=language, active_sub=active_sub, tier=tier, force_live=force_live,
        dry_run=dry_run, culture_context=culture_context, char_name=character_name,
    )

    show_slug = title.lower().replace(" ", "_").replace("-", "_")[:24]
    show = next((s for s in repo.list_shows(user.id) if s.slug == show_slug), None)
    if not show:
        show = Show(user_id=user.id, title=title, slug=show_slug, genre=genre)
        repo.save_show(show)

    episode = Episode(
        user_id=user.id, show_id=show.id, title=ep_title,
        episode_number=episode_number, duration_seconds=duration, format=resolved_format,
    )
    episode.cost_record = calculate_preflight_estimate(episode)
    episode.estimated_cost_usd = episode.cost_record.predicted_total_usd
    repo.save_episode(episode)

    # 3. Mandatory Pre-Flight Cost Estimation, Quota Audit & User Confirmation Gate
    decision_mode, allow_fallback_resolved, selected_tier = await execute_preflight_gate(
        episode=episode, user=user, language=language, auto_confirm=auto_confirm,
        local_flag=local, cli_tier=tier,
    )
    if decision_mode == "cancel":
        print("[!] Production cancelled by user. Zero credits deducted.\n")
        return None

    is_local_mode = decision_mode == "local" or allow_fallback or allow_fallback_resolved
    if is_local_mode:
        print("[i] Operating in LOCAL MODE: Zero external API calls, offline synthesis active.")

    tiers_info = recommend_production_tiers(metadata={"language": language}, duration_seconds=duration)
    if selected_tier in tiers_info["tiers"]:
        tier_spec = tiers_info["tiers"][selected_tier]
        episode.estimated_cost_usd = tier_spec["total_cost_usd"]
        repo.save_episode(episode)
        print(f"[i] Active Production Tier: {tier_spec['display_name']} (${episode.estimated_cost_usd:.4f})")

    print(f"\n[1/4] Confirmed Episode Project: {episode.id} (Tier: {selected_tier.upper()}, Mode: {decision_mode.upper()}, Budget: ${episode.estimated_cost_usd:.4f})")

    # 4. Generate Episodic Thumbnail with Top-Left Badge
    thumb_dir = Path("storage") / user.storage_container_name / "creative_vault" / "shows_and_titles" / show.slug / "episodes" / str(episode.id) / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    thumb_path = thumb_dir / f"thumb_ep{episode_number:02d}_{language}.jpg"
    badge_cfg = EpisodicBadgeConfig(
        episode_number=episode_number, language=language, style="pill",
        position="top_left", custom_label=badge_label,
    )
    generate_episodic_thumbnail(output_path=thumb_path, badge_config=badge_cfg, headline=headline)
    print(f"[2/4] Rendered Top-Left Episodic Thumbnail: {thumb_path}")

    # 5. Check FFmpeg availability & execute production pipeline
    ffmpeg_available = has_ffmpeg()
    effective_dry_run = dry_run or not ffmpeg_available
    if not ffmpeg_available and not dry_run:
        print("[!] Note: FFmpeg binary not found. Executing with dry_run=True (assets synthesized, filter_complex graph verified).")
    elif not dry_run:
        logger.info(f"using_ffmpeg: {get_ffmpeg_binary()}")

    print("[3/4] Synthesizing 4K Keyframes, Voice Stems, BGM, and Compiling Single-Pass FFmpeg Graph...")
    final_video = await pipeline_coordinator.produce_episode_master(
        user_id=user.id, episode_id=episode.id, dry_run=effective_dry_run, language=language,
        subtitle_language=active_sub, force_live=force_live, strict=not is_local_mode,
        tier=selected_tier, character_name=character_name, culture=culture,
        costume_style=costume_style, dance_type=dance_type, gender=gender,
        art_style=art_style,
    )
    print(f"[4/4] Master Video Generated: {final_video}")

    saved_episode = repo.get_episode(user.id, episode.id)
    cleared, _ = rights_ledger.verify_episode_rights(episode.id)
    rights_records = rights_ledger.get_records_for_episode(episode.id)
    print_cli_summary(saved_episode, user, final_video, rights_records, cleared)


def main():
    parser = argparse.ArgumentParser(description="Produce an Episode Video in Phase 2 & 3")
    parser.add_argument("--title", type=str, default="IT Employee WFH Confusions", help="Project/Show title")
    parser.add_argument("--episode", type=int, default=1, help="Episode number")
    parser.add_argument("--genre", type=str, default="comedy", help="Genre classification")
    parser.add_argument("--duration", type=int, default=480, help="Target duration in seconds")
    parser.add_argument("--language", type=str, default="te", help="Primary spoken language: te, hi, en, es, it")
    parser.add_argument("--subtitle-language", type=str, default=None, help="Burned subtitle language (defaults to 'en')")
    parser.add_argument("--live", action="store_true", help="Use live free serverless visual/voice synthesis")
    parser.add_argument("--dry-run", action="store_true", help="Compile and generate assets without running FFmpeg binary")
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm estimated cost without prompt")
    parser.add_argument("--allow-fallback", action="store_true", help="Allow fallback when provider credits depleted")
    parser.add_argument("--local", action="store_true", help="Generate in local offline mode with zero API spend")
    parser.add_argument("--tier", type=str, default=None, help="Production tier: low_cost, balanced, cinematic, local")
    parser.add_argument(
        "--type", "--format", dest="media_format", type=str, default="auto",
        help="Media format type: auto, travel_guide, vlog, movie, scenic_relaxation, walking_tour, scenic_drive, ambient_lounge, nature_sanctuary",
    )
    parser.add_argument("--art-style", "--style", dest="art_style", type=str, default=None, help="Global art style or aesthetic (e.g. swiss_alpine_rainy_village, greek_cycladic_coastal, ukiyo_e, afrofuturism)")
    parser.add_argument("--country", type=str, default=None, help="User home country code (e.g. IN, AU, IT, MX, US, CN)")
    parser.add_argument("--culture", type=str, default=None, help="Cultural heritage (e.g. indian_south, australian, italian, mexican)")
    parser.add_argument("--costume", dest="costume_style", type=str, default=None, help="Costume style override")
    parser.add_argument("--dance", dest="dance_type", type=str, default=None, help="Dance genre (e.g. bharatanatyam, tarantella, folklore, line_dance)")
    parser.add_argument("--character", dest="character_name", type=str, default=None, help="Protagonist character name")
    parser.add_argument("--gender", type=str, default="female", choices=["female", "male"], help="Protagonist character gender")

    args = parser.parse_args()
    asyncio.run(
        run_production(
            title=args.title, episode_number=args.episode, genre=args.genre, duration=args.duration,
            language=args.language, dry_run=args.dry_run, subtitle_language=args.subtitle_language,
            force_live=args.live, auto_confirm=args.yes, allow_fallback=args.allow_fallback,
            local=args.local, tier=args.tier, media_format=args.media_format, country=args.country,
            culture=args.culture, costume_style=args.costume_style, dance_type=args.dance_type,
            character_name=args.character_name, gender=args.gender, art_style=args.art_style,
        )
    )


if __name__ == "__main__":
    main()
