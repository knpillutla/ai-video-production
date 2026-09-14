"""CLI Entrypoint to Produce an Episode Video in Phase 2 & 3."""

import argparse
import asyncio
import json
import sys
import time
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
from src.domain.generation import MediaFormat, ThemeGenre
from src.domain.repo import repo
from src.domain.user import User
from src.mcp.model_selector.tier_resolver import recommend_production_tiers
from src.scheduling.daily_scheduler import daily_scheduler
from src.scripts.cli_presentation import print_cli_header, print_cli_summary
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.preflight_gate import execute_preflight_gate
from src.services.cultural_derivation import derive_cultural_context


async def run_production(
    title: str = "IT Employee WFH Confusions", episode_number: int = 1, genre: str = "comedy",
    duration: int = 480, language: str = "en", dry_run: bool = False, subtitle_language: str | None = None,
    force_live: bool = False, auto_confirm: bool = False, allow_fallback: bool = False,
    local: bool = False, tier: str | None = None, media_format: str = "auto", country: str | None = None,
    culture: str | None = None, costume_style: str | None = None, dance_type: str | None = None,
    character_name: str | None = None, gender: str = "female", art_style: str | None = None,
    theme: str | None = None, idea: str | None = None, script: str | None = None,
    refine_script: bool = False, voice_gender: str | None = None, target_languages: str | None = None,
    voice_over: bool = False, narration_male: bool = False, narration_female: bool = False,
    bgm: bool = False, tts: bool = False, youtube_reference_link: str | None = None,
):
    """Execute the Phase 2 & 3 end-to-end video production and compliance pipeline."""
    # Dynamic title resolution based on theme, idea, or script when title is not overridden
    is_default_title = (title == "IT Employee WFH Confusions" or not title)
    if theme and is_default_title:
        title = await daily_scheduler.get_fresh_original_topic(theme=theme, show_slug="theme-universe")
    elif idea and is_default_title:
        title = (idea[:36].strip() + "...") if len(idea) > 36 else idea.strip()
    elif script and is_default_title:
        title = Path(script).stem.replace("_", " ").title() if Path(script).is_file() else "Custom Screenplay"

    active_sub = subtitle_language or ("en" if language.lower() != "en" else "en")

    # Script input resolution (file path vs raw screenplay text)
    script_text: str | None = None
    script_label: str | None = None
    if script:
        s_path = Path(script)
        if s_path.is_file():
            script_text = s_path.read_text(encoding="utf-8")
            script_label = f"File: {s_path.name} ({len(script_text)} chars)"
        else:
            script_text = script
            script_label = f"Text: {script[:36]}..." if len(script) > 36 else f"Text: {script}"

    # Theme enum resolution
    resolved_theme = ThemeGenre.AUTO
    if theme:
        for tg in ThemeGenre:
            if theme.lower().replace("-", "_") in (tg.value.lower(), tg.name.lower()):
                resolved_theme = tg
                break

    # Format resolution (Auto-Detect or Explicit)
    creative_context = " ".join(filter(None, [genre, theme, idea, title, youtube_reference_link, script_text[:200] if script_text else None]))
    if not media_format or media_format.lower() == "auto":
        detected = classifier_agent.detect(text=creative_context, title=title)
        resolved_format = detected.media_format
        if resolved_theme == ThemeGenre.AUTO and detected.theme != ThemeGenre.AUTO:
            resolved_theme = detected.theme
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
        user = User(email="creator@cineai.studio", display_name="Studio Director", google_sub="cli_local_user", storage_container_name="user-cli-director", api_credit_balance_usd=50.00, home_country=country, cultural_heritage=culture)
    else:
        if country: user.home_country = country
        if culture: user.cultural_heritage = culture
    repo.save_user(user)

    # 2. Derive cultural context and audio modalities (Auto-identify TTS & Lipsync if not explicit)
    if voice_over or narration_male or narration_female or tts:
        is_voice_over = True
        effective_voice_gender = "male" if narration_male else ("female" if narration_female else (voice_gender or "female"))
        enable_lipsync = bool(tts)
    else:
        auto_tts, auto_lipsync = classifier_agent.infer_audio_modalities(
            theme=theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None),
            idea=idea, script=script_text, media_format=resolved_format,
        )
        is_voice_over, enable_lipsync = auto_tts, auto_lipsync
        effective_voice_gender = voice_gender or gender or "female"

    enable_bgm = bool(bgm)

    ref_attrs = None
    if youtube_reference_link:
        from src.scripts.youtube_ingest import extract_reference_video_attributes
        ref_attrs = extract_reference_video_attributes(
            url=youtube_reference_link, title=title, text=f"{idea or ''} {theme or ''}",
            default_genre=genre, user_format=fmt_str,
        )
        if not art_style:
            art_style = ref_attrs.art_style
        print(f"[i] Reference Video Attributes Distilled:\n - Art Style: {ref_attrs.art_style_display}\n - Architecture: {ref_attrs.architecture_style}\n - Lighting: {ref_attrs.lighting_scheme}\n - Palette: {ref_attrs.color_palette}\n - Camera Motion: {ref_attrs.camera_language}\n - Soundtrack: {ref_attrs.soundtrack_style}")

    culture_context = derive_cultural_context(
        script_text=creative_context, user_home_country=user.home_country,
        user_cultural_heritage=user.cultural_heritage, language=language,
        gender=effective_voice_gender, genre=genre, dance_type=dance_type or "",
        video_format=fmt_str, art_style=art_style or "",
    )
    print_cli_header(
        title=ep_title, fmt_str=fmt_str, genre=genre, duration=duration,
        language=language, active_sub=active_sub, tier=tier, force_live=force_live,
        dry_run=dry_run, culture_context=culture_context, char_name=character_name,
        theme=theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None),
        idea=idea, script_preview=script_label,
        voice_over=is_voice_over, voice_gender=effective_voice_gender,
        bgm=enable_bgm, lipsync=enable_lipsync,
    )

    show_slug = title.lower().replace(" ", "_").replace("-", "_")[:24]
    show = next((s for s in repo.list_shows(user.id) if s.slug == show_slug), None)
    if not show:
        show = Show(user_id=user.id, title=title, slug=show_slug, genre=genre)
        repo.save_show(show)

    episode = Episode(
        user_id=user.id, show_id=show.id, title=ep_title,
        episode_number=episode_number, duration_seconds=duration, format=resolved_format,
        theme=resolved_theme, topic_or_idea=idea or (theme if theme else ""),
        custom_script=script_text, youtube_reference_url=youtube_reference_link,
    )
    episode.options.enable_tts, episode.options.enable_voice_over = is_voice_over, is_voice_over
    episode.options.enable_bgm, episode.options.enable_lipsync = enable_bgm, enable_lipsync
    episode.options.voice_gender = effective_voice_gender
    if target_languages and is_voice_over:
        parsed_langs = [l.strip() for l in target_languages.split(",") if l.strip()]
        if parsed_langs:
            episode.options.target_languages = parsed_langs

    # 0. User inputs JSON is the very first file created in episode workspace
    ep_ws = Path("storage") / user.storage_container_name / "creative_vault" / "shows_and_titles" / show.slug / "episodes" / str(episode.id)
    ep_ws.mkdir(parents=True, exist_ok=True)
    user_inputs = {
        "user_id": str(user.id), "episode_id": str(episode.id), "title": ep_title,
        "duration_seconds": duration, "format": fmt_str, "genre": genre,
        "theme": theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None),
        "idea": idea, "script": script_text, "youtube_reference_url": youtube_reference_link,
        "tier": tier, "language": language, "subtitle_language": active_sub,
        "gender": effective_voice_gender, "character_name": character_name, "art_style": art_style,
        "enable_voice_over": is_voice_over, "enable_bgm": enable_bgm, "enable_lipsync": enable_lipsync,
        "reference_attributes": ref_attrs.model_dump(mode="json") if ref_attrs else None,
        "target_languages": episode.options.target_languages, "created_at": time.time(),
    }
    with open(ep_ws / "user_inputs.json", "w", encoding="utf-8") as f:
        json.dump(user_inputs, f, indent=2)

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
    thumb_dir = ep_ws / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    generate_episodic_thumbnail(
        output_path=thumb_dir / f"thumb_ep{episode_number:02d}_{language}.jpg",
        badge_config=EpisodicBadgeConfig(episode_number=episode_number, language=language, style="pill", position="top_left", custom_label=badge_label),
        headline=headline,
    )
    print(f"[2/4] Rendered Top-Left Episodic Thumbnail: thumb_ep{episode_number:02d}_{language}.jpg")

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
        costume_style=costume_style, dance_type=dance_type, gender=effective_voice_gender,
        art_style=art_style, custom_script=script_text, idea=idea, theme=theme,
        refine_script=refine_script, enable_voice_over=is_voice_over,
        enable_bgm=enable_bgm, enable_lipsync=enable_lipsync,
    )
    print(f"[4/4] Master Video Generated: {final_video}")

    saved_episode = repo.get_episode(user.id, episode.id)
    cleared, _ = rights_ledger.verify_episode_rights(episode.id)
    rights_records = rights_ledger.get_records_for_episode(episode.id)
    print_cli_summary(saved_episode, user, final_video, rights_records, cleared)


def main():
    p = argparse.ArgumentParser(description="Produce an Episode Video in Phase 2 & 3")
    for fl, d, t, h, dst in [
        ("--title", "IT Employee WFH Confusions", str, "Title", None), ("--episode", 1, int, "Episode #", "episode_number"),
        ("--genre", "comedy", str, "Genre", None), ("--theme", None, str, "Theme", None), ("--idea", None, str, "Idea", None),
        ("--script", None, str, "Script", None), ("--duration", 480, int, "Duration", None), ("--language", "en", str, "Lang", None),
        ("--subtitle-language", None, str, "Sub", None), ("--tier", None, str, "Tier", None), ("--country", None, str, "Country", None),
        ("--culture", None, str, "Culture", None), ("--costume", None, str, "Costume", "costume_style"),
        ("--dance", None, str, "Dance", "dance_type"), ("--character", None, str, "Char", "character_name"),
        ("--gender", "female", str, "Gender", None), ("--type", "auto", str, "Format", "media_format"),
        ("--art-style", None, str, "Style", "art_style"), ("--voice-gender", None, str, "Voice gender", "voice_gender"),
        ("--youtube-reference-link", None, str, "YouTube URL", "youtube_reference_link"), ("--languages", None, str, "Languages", "target_languages"),
    ]:
        kw = {"type": t, "default": d, "help": h}
        if dst: kw["dest"] = dst
        p.add_argument(fl, **kw)
    for fls, h, dst in [
        (["--live"], "Live synthesis", "force_live"), (["--dry-run"], "Dry run", "dry_run"),
        (["-y", "--yes"], "Auto confirm", "auto_confirm"), (["--allow-fallback"], "Fallback", "allow_fallback"),
        (["--local"], "Local mode", "local"), (["--voice-over"], "Voiceover", "voice_over"),
        (["--narration-male"], "Male voice", "narration_male"), (["--narration-female"], "Female voice", "narration_female"),
        (["--tts"], "Conversational TTS", "tts"), (["--bgm"], "Background music", "bgm"),
        (["--refine", "--refine-script"], "Refine screenplay", "refine_script"),
    ]:
        p.add_argument(*fls, action="store_true", default=False, help=h, dest=dst)
    asyncio.run(run_production(**vars(p.parse_args())))


if __name__ == "__main__":
    main()
