"""CLI Entrypoint to Produce an Episode Video in Phase 2 & 3."""

import argparse
import asyncio
import json
from pathlib import Path
import re
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
if hasattr(sys.stderr, "reconfigure"):
    try: sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass

from src.agents.classifier_agent import classifier_agent
from src.billing.cost_tracker import calculate_preflight_estimate
from src.compliance.rights_ledger import rights_ledger
from src.compositor.ffmpeg_pipeline import get_ffmpeg_binary, has_ffmpeg
from src.compositor.pipeline import pipeline_coordinator
from src.compositor.pipeline_prompts import build_storyboard_prompt
from src.core.storage import storage_service; from src.core.telemetry import logger
from src.core.config import settings
from src.core.config.artifact_models import get_artifact_profile
from src.domain.creative import Episode, Show; from src.domain.generation import MediaFormat, ThemeGenre, VisualStyle
from src.domain.repo import repo; from src.domain.user import User
from src.mcp.model_selector.tier_resolver import recommend_production_tiers
from src.mcp.topic_memory.server import check_topic_duplicate
from src.services.topic_planner import get_fresh_original_topic
from src.core.utils.duration_parser import parse_duration
from src.scripts.cli_presentation import print_cli_header, print_cli_summary
from src.scripts.local_thumbnail import EpisodicBadgeConfig, generate_episodic_thumbnail
from src.scripts.preflight_gate import execute_preflight_gate; from src.services.cultural_derivation import derive_cultural_context
from src.services.provider_health import audit_all_providers_health


async def run_production(
    title: str = "Telugu Melody Song", episode_number: int = 1, genre: str = "vocal",
    duration: int | str = 10, language: str = "te", dry_run: bool = False, subtitle_language: str | None = None,
    force_live: bool = False, auto_confirm: bool = False, allow_fallback: bool = False,
    local: bool = False, tier: str | None = None, media_format: str = "vocal_song", country: str | None = None,
    culture: str | None = None, costume_style: str | None = None, dance_type: str | None = None,
    character_name: str | None = None, gender: str = "female", art_style: str | None = None,
    theme: str | None = None, idea: str | None = None, script: str | None = None,
    refine_script: bool = False, voice_gender: str | None = None, target_languages: str | None = None,
    voice_over: bool = False, narration_male: bool = False, narration_female: bool = False,
    bgm: bool = False, tts: bool = False, youtube_reference_link: str | None = None, prompt: str | None = None,
    restart_id: str | None = None, profile: str = "development",
    music_style: str | None = None, similar_to: str | None = None,
    user_id: str | None = None, network: str | None = None,
    num_images: int = 1, use_loras: bool = False,
    preview_only: bool = False, full_confirmed: bool = False,
    solo_male: bool = False, solo_female: bool = False, duet: bool = False,
    mass_song: bool = False,
    rescript: bool = False,
):
    """Execute the Phase 2 & 3 end-to-end video production and compliance pipeline."""
    duration = parse_duration(duration)
    if local:
        profile = "local"
    artifact_profile = get_artifact_profile(profile)
    local = artifact_profile.name == "local"
    force_live = artifact_profile.name in ("development", "production") if not local else False
    if artifact_profile.name == "production":
        allow_fallback = False
        if not tier:
            tier = "cinematic"
    if user_id:
        from uuid import UUID, uuid5, NAMESPACE_DNS
        from src.core.storage import sanitize_container_name
        try:
            uid = UUID(user_id)
        except Exception:
            uid = uuid5(NAMESPACE_DNS, user_id)
        clean_email = user_id if "@" in user_id else f"user_{str(uid)[:8]}@cineai.studio"
        d_name = user_id.split("@")[0] if "@" in user_id else "Studio Creator"
        cont_name = sanitize_container_name(user_id)
        user = repo.get_user_by_email(clean_email) or repo.users.get(uid) or User(
            id=uid, email=clean_email, display_name=d_name, google_sub=f"cli_{str(uid)[:12]}",
            storage_container_name=cont_name, api_credit_balance_usd=50.00, home_country=country, cultural_heritage=culture,
        )
    else:
        user = repo.get_user_by_email("creator@cineai.studio")
        if not user:
            user = User(email="creator@cineai.studio", display_name="Studio Director", google_sub="cli_local_user", storage_container_name="user-cli-director", api_credit_balance_usd=50.00, home_country=country, cultural_heritage=culture)
        else:
            if country: user.home_country = country
            if culture: user.cultural_heritage = culture
    repo.save_user(user)

    # ---------------------------------------------------------------------------
    # Restart/Resume Logic: If --id passed, reload existing episode & skip metadata steps
    # ---------------------------------------------------------------------------
    existing_ep = None
    show = None
    if restart_id:
        try:
            from uuid import UUID
            rid = UUID(restart_id)
            # Find disk workspace strictly prioritizing music_video paths
            disk_matches = [p for p in Path(settings.storage.local_storage_root).glob(f"**/{restart_id}/user_inputs.json") if "music_video" in str(p)]
            if not disk_matches:
                for ui_path in Path(settings.storage.local_storage_root).glob("**/user_inputs.json"):
                    if "music_video" not in str(ui_path):
                        continue
                    try:
                        d = json.loads(ui_path.read_text(encoding="utf-8"))
                        if d.get("episode_id") == str(restart_id) or str(d.get("id")) == str(restart_id):
                            disk_matches = [ui_path]
                            break
                    except Exception:
                        continue

            existing_ep = repo.get_episode(user.id, rid) or repo.episodes.get(rid)
            if not existing_ep:
                if disk_matches:
                    stored = json.loads(disk_matches[0].read_text(encoding="utf-8"))
                    u_id = UUID(stored.get("user_id", str(user.id)))
                    matched_cont = next((p for p in disk_matches[0].parts if p.startswith("user-")), "user-cli-director")
                    user = repo.users.get(u_id) or User(id=u_id, email=f"{matched_cont}@cineai.studio", display_name="Studio Director", google_sub="cli_local_user", storage_container_name=matched_cont)
                    user.storage_container_name = matched_cont
                    repo.save_user(user)
                    raw_theme = str(stored.get("theme", "")).lower()
                    t_genre = next((tg for tg in ThemeGenre if tg.value in raw_theme), ThemeGenre.ROMANTIC_DRAMA)
                    show = Show(user_id=user.id, title=stored.get("title", "Music Video"), slug=disk_matches[0].parent.parent.parent.name, genre=t_genre)
                    repo.save_show(show)
                    raw_style = str(stored.get("art_style", "")).lower()
                    v_style = next((vs for vs in VisualStyle if vs.value in raw_style), VisualStyle.REALISTIC)
                    existing_ep = Episode(
                        id=rid, user_id=user.id, show_id=show.id, title=stored.get("title", "Episode"),
                        duration_seconds=stored.get("duration_seconds", 60), format=MediaFormat.VOCAL_SONG,
                        visual_style=v_style, theme=t_genre, topic_or_idea=stored.get("idea", ""),
                    )
                    repo.save_episode(existing_ep)
                else:
                    print(f"[!] Error: Episode ID {restart_id} not found in repository or storage.")
                    return None
            else:
                existing_ep.format = MediaFormat.VOCAL_SONG
            show = repo.get_show(existing_ep.user_id, existing_ep.show_id) or repo.shows.get(existing_ep.show_id)
            user = repo.users.get(existing_ep.user_id, user)
            if show: show.genre = "vocal"
            print(f"[i] Restarting production for existing Episode ID: {restart_id}")
            print(f"    Title: {existing_ep.title} | Format: {existing_ep.format}")
            # Overlay saved attributes for continuity
            title = existing_ep.title
            episode_number = existing_ep.episode_number
            duration = existing_ep.duration_seconds
            resolved_format = MediaFormat.VOCAL_SONG
            resolved_theme = existing_ep.theme
            idea = existing_ep.topic_or_idea
            script_text = existing_ep.custom_script
            youtube_reference_link = existing_ep.youtube_reference_url
            fmt_str = "vocal_song"
            genre = "vocal"
            
            # Lock workspace to exact disk match folder
            u_cont = getattr(user, "storage_container_name", None) or getattr(user, "email", None) or str(user.id)
            if disk_matches and disk_matches[0].parent.is_dir():
                ep_ws = disk_matches[0].parent
                match_ep = re.search(r"ep-(\d+)", ep_ws.name, re.IGNORECASE)
                episode_number = int(match_ep.group(1)) if match_ep else (existing_ep.episode_number or 1)
                existing_ep.episode_number = episode_number
                parts = list(ep_ws.parts)
                if "networks" in parts:
                    net_idx = parts.index("networks")
                    if len(parts) > net_idx + 1:
                        network = parts[net_idx + 1]
            else:
                found_dir = storage_service.find_episode_path(u_cont, network, str(existing_ep.id), format_slug="music_video")
                ep_ws = found_dir if (found_dir and found_dir.is_dir()) else storage_service.get_channel_format_production_episode_path(u_cont, network or (show.slug if show else "default_network"), "music_video", re.sub(r"[^a-zA-Z0-9]+", "_", str(title).lower()).strip("_") or "standalone", f"ep-{existing_ep.episode_number:03d}" if existing_ep.episode_number else "ep-001")
                match_ep = re.search(r"ep-(\d+)", ep_ws.name, re.IGNORECASE)
                episode_number = int(match_ep.group(1)) if match_ep else (existing_ep.episode_number or 1)
                existing_ep.episode_number = episode_number
                parts = list(ep_ws.parts)
                if "networks" in parts:
                    net_idx = parts.index("networks")
                    if len(parts) > net_idx + 1:
                        network = parts[net_idx + 1]
            inputs_json = ep_ws / "user_inputs.json"
            if inputs_json.exists():
                try:
                    stored_inputs = json.loads(inputs_json.read_text(encoding="utf-8"))
                    title = stored_inputs.get("title", title)
                    existing_ep.title = title
                    idea = stored_inputs.get("idea", idea)
                    theme = stored_inputs.get("theme", theme)
                    prompt = stored_inputs.get("prompt", prompt)
                    music_style = music_style or stored_inputs.get("music_style") or stored_inputs.get("style")
                    similar_to = similar_to or stored_inputs.get("similar_to")
                    language = stored_inputs.get("language", language)
                    character_name = character_name or stored_inputs.get("character_name")
                    country = country or stored_inputs.get("country")
                    culture = culture or stored_inputs.get("culture")
                    costume_style = costume_style or stored_inputs.get("costume_style")
                    dance_type = dance_type or stored_inputs.get("dance_type")
                    art_style = art_style or stored_inputs.get("art_style")
                    active_sub = stored_inputs.get("subtitle_language", subtitle_language or "en")
                    if num_images == 1 and "num_images" in stored_inputs:
                        num_images = int(stored_inputs["num_images"])
                    if not use_loras and "use_loras" in stored_inputs:
                        use_loras = bool(stored_inputs["use_loras"])
                    if not (solo_male or solo_female or duet):
                        duet = stored_inputs.get("duet", False) or (stored_inputs.get("gender") == "duet")
                        solo_male = stored_inputs.get("solo_male", False) or (stored_inputs.get("gender") == "male")
                        solo_female = stored_inputs.get("solo_female", False) or (stored_inputs.get("gender") == "female" and not duet)
                    effective_voice_gender = "duet" if duet else ("male" if solo_male else ("female" if solo_female else stored_inputs.get("gender", "duet")))
                    gender = effective_voice_gender
                    is_voice_over = stored_inputs.get("enable_voice_over", False)
                    enable_bgm = stored_inputs.get("enable_bgm", True)
                    enable_lipsync = stored_inputs.get("enable_lipsync", True)
                except Exception: pass
            
            # Preserve existing master renders on resume (Rule 3 Tier 1 Disk Check)
            renders_dir = ep_ws / "master_renders"
            if force_live and renders_dir.exists():
                for old_master in renders_dir.glob("master_*.mp4"):
                    try:
                        old_master.unlink()
                        logger.info(f"force_live_master_cleared: {old_master.name}")
                    except Exception: pass

            # Skip metadata derivation and duplication checks if resuming
            goto_production = True
        except ValueError as ex:
            print(f"[!] Error: Failed to resume episode {restart_id}: {ex}")
            return None
    else:
        goto_production = False

    # Multi-language batch execution
    active_langs_str = target_languages or language
    if "," in active_langs_str and not goto_production:
        parsed_langs = [l.strip() for l in active_langs_str.split(",") if l.strip()]
        if len(parsed_langs) > 1:
            print(f"[i] Multi-Language Batch Mode: Producing {len(parsed_langs)} regional editions: {', '.join(parsed_langs)}")
            results = []
            for idx, lng in enumerate(parsed_langs):
                print(f"\n=======================================================\n [Edition {idx+1}/{len(parsed_langs)}] Language: {lng.upper()}\n=======================================================")
                res = await run_production(
                    title=title, episode_number=episode_number, genre=genre, duration=duration, language=lng,
                    dry_run=dry_run, subtitle_language=subtitle_language, force_live=force_live,
                    auto_confirm=auto_confirm, allow_fallback=allow_fallback, local=local, tier=tier,
                    media_format=media_format, country=country, culture=culture, costume_style=costume_style,
                    dance_type=dance_type, character_name=character_name, gender=gender, art_style=art_style,
                    theme=theme, idea=idea, script=script, refine_script=refine_script, voice_gender=voice_gender,
                    target_languages=None, voice_over=voice_over, narration_male=narration_male,
                    narration_female=narration_female, bgm=bgm, tts=tts,
                    youtube_reference_link=youtube_reference_link, prompt=prompt, profile=profile,
                )
                results.append(res)
            return results

    if not goto_production:
        is_default_title = (title in ("IT Employee WFH Confusions", "Telugu Melody Song") or not title)
        if is_default_title and (idea or theme or prompt):
            raw_input = idea or theme or prompt
            from src.services.creative_director import expand_creative_idea
            extracted_lang = classifier_agent.extract_language_from_text(raw_input)
            if extracted_lang:
                language = extracted_lang

            bp = await expand_creative_idea(idea=raw_input, target_format="walking_tour" if any(k in raw_input.lower() for k in ("walk", "tour", "city", "street", "europe")) else "general", language=language, user_id=str(user.id))
            title = bp.title
            idea = f"{bp.destination_name}, {bp.country} - {bp.visual_theme}"
            if not country:
                country = bp.country
            if not culture:
                culture = bp.culture
            if not theme:
                theme = bp.visual_theme
        elif youtube_reference_link and is_default_title:
            from src.scripts.youtube_ingest import fetch_youtube_oembed_title, extract_reference_video_attributes
            yt_title = fetch_youtube_oembed_title(youtube_reference_link)
            ref_info = extract_reference_video_attributes(url=youtube_reference_link, title=yt_title)
            title = yt_title or ref_info.art_style_display or "YouTube Reference Walk"
            idea = yt_title or title
            if not theme:
                theme = ref_info.art_style_display
        elif script and is_default_title:
            title = Path(script).stem.replace("_", " ").title() if Path(script).is_file() else "Custom Screenplay"
        elif media_format.lower().replace("-", "_") in ("vocal", "vocal_song", "lyrical_video", "music_video") and is_default_title:
            title = ""
            if not theme:
                theme = "Romantic Vocal Melody"

        active_sub = subtitle_language or ("en" if language.lower() != "en" else "en")
        script_text, script_label = None, None
        if script:
            s_path = Path(script)
            script_text = s_path.read_text(encoding="utf-8") if s_path.is_file() else script
            script_label = f"File: {s_path.name}" if s_path.is_file() else f"Text: {script[:36]}..."

        resolved_theme = ThemeGenre.AUTO
        if theme:
            for tg in ThemeGenre:
                if theme.lower().replace("-", "_") in (tg.value.lower(), tg.name.lower()):
                    resolved_theme = tg; break

        effective_genre_cue = genre if (genre != "comedy" or not theme) else None
        creative_context = " ".join(filter(None, [effective_genre_cue, theme, idea, title, prompt, youtube_reference_link, script_text[:200] if script_text else None]))
        if not media_format or media_format.lower() == "auto":
            if genre in ("vocal", "vocal_song", "song"):
                resolved_format = MediaFormat.VOCAL_SONG
            else:
                detected = classifier_agent.detect(text=creative_context, title=title)
                resolved_format = detected.media_format
                if resolved_theme == ThemeGenre.AUTO and detected.theme != ThemeGenre.AUTO:
                    resolved_theme = detected.theme
                if genre == "comedy" and detected.theme != ThemeGenre.TELUGU_COMEDY:
                    genre = "travel_tourism" if detected.theme == ThemeGenre.TRAVEL_TOURISM else (
                        "nature_documentary" if detected.theme == ThemeGenre.NATURE_WILDLIFE else (
                            "dance" if detected.theme == ThemeGenre.BOLLYWOOD_DANCE else detected.theme.value
                        )
                    )
        else:
            fmt_raw = media_format.lower().replace("-", "_")
            if fmt_raw in ("movie", "film", "cinema", "cinematic", "epic_cinematic"):
                resolved_format = MediaFormat.MOVIE_CINEMATIC
                if genre == "comedy": genre = "cinematic"
            elif fmt_raw in ("tourist_guide", "travel_guide", "tourist_attractions", "city_guide"):
                resolved_format = MediaFormat.TRAVEL_GUIDE
                if genre == "comedy": genre = "travel_tourism"
            elif fmt_raw in ("dance", "dance_song", "mass_dance"):
                resolved_format = MediaFormat.DANCE_VIDEO
                if genre == "comedy": genre = "dance"
            elif fmt_raw in ("walk", "walking", "walk_tour", "walking_tour"):
                resolved_format = MediaFormat.WALKING_TOUR
                if genre == "comedy": genre = "walking_tour"
            elif fmt_raw in ("vocal", "vocal_song", "lyrical_video", "music_video"):
                resolved_format = MediaFormat.VOCAL_SONG
                if genre == "comedy": genre = "vocal"
            else:
                try:
                    resolved_format = MediaFormat(fmt_raw)
                except ValueError:
                    resolved_format = MediaFormat.WEB_SERIES

        fmt_str = resolved_format.value
        prompt_overrides = classifier_agent.extract_prompt_overrides(creative_context)
        if "media_format" in prompt_overrides and media_format == "auto":
            resolved_format = prompt_overrides["media_format"]
            fmt_str = resolved_format.value
        if "language" in prompt_overrides and language == "en": language = prompt_overrides["language"]
        if "gender" in prompt_overrides and gender == "female": gender = prompt_overrides["gender"]
        if "duration" in prompt_overrides and duration == 480: duration = prompt_overrides["duration"]

        # ---------------------------------------------------------------------------
        # Title derivation + duplicate check with up to 3 auto-retry attempts
        # ---------------------------------------------------------------------------
        _MAX_DUP_RETRIES = 3
        _t_hint = "dance" if prompt and "dance" in prompt.lower() else ("nature" if prompt and any(k in (prompt or "").lower() for k in ("mountain", "nature", "wildlife", "alps")) else ("comedy" if prompt and "comedy" in (prompt or "").lower() else None))

        for _attempt in range(1, _MAX_DUP_RETRIES + 1):
            if network:
                clean_net = re.sub(r"[^a-zA-Z0-9_-]", "_", network.lower()).strip("_")[:32] or "default_network"
                show_slug = clean_net
                show_title = network.replace("_", " ").title()
            else:
                show_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", title.lower()).strip("_")[:32] or "default_show"
                show_slug = re.sub(r"_+", "_", show_slug)
                show_title = title
            show = next((s for s in repo.list_shows(user.id) if s.slug == show_slug), None)
            if not show:
                show = Show(user_id=user.id, title=show_title, slug=show_slug, genre=genre)
                repo.save_show(show)

            existing_eps = repo.list_episodes(user.id, show.id) if show else []
            existing_ep = None
            if episode_number is None:
                episode_number = max((ep.episode_number for ep in existing_eps), default=0) + 1
            ep_num_str = f"Episode {episode_number:02d}"
            base_t = re.sub(r"\s*[-–—]?\s*episode\s*\d+", "", str(title or "New Song"), flags=re.IGNORECASE).strip()
            ep_title = f"{base_t} - {ep_num_str}"
            badge_label = "MUSIC VIDEO" if resolved_format in (MediaFormat.MUSIC_VIDEO, MediaFormat.VOCAL_SONG) else (resolved_format.value.upper().replace("_", " "))
            headline = f"{base_t} EP {episode_number:02d}!"
            existing_ep = next((e for e in existing_eps if e.title == ep_title), None)

            # Pre-creation language-scoped duplicate check
            # Composite key = full user context (prompt+genre+theme+idea) + LLM title
            _dup_topic = f"{creative_context} | {ep_title}".strip()
            topic_dup = await check_topic_duplicate(topic=_dup_topic, metadata={"genre": genre, "language": language}, user_id=str(user.id), language=language)
            if not topic_dup.get("is_duplicate"):
                break  # Fresh title found — proceed

            if _attempt < _MAX_DUP_RETRIES and (prompt or theme):
                print(f"\n[~] Attempt {_attempt}: Title '{ep_title}' already exists. Requesting a new original title from the scheduler (attempt {_attempt + 1}/{_MAX_DUP_RETRIES})...")
                title = await get_fresh_original_topic(
                    theme=_t_hint or genre, show_slug=show_slug,
                    language=language, user_id=str(user.id),
                )
                idea = idea or prompt  # keep original user intent as idea
                logger.info(f"duplicate_retry: attempt={_attempt} new_title='{title}'")
            else:
                print(f"\n[!] {topic_dup.get('alert_message')}")
                print(f"[!] All {_MAX_DUP_RETRIES} title regeneration attempts produced duplicates. Try a more specific prompt.\n")
                return None
    else:
        # For resumes, ensure badge_label and ep_title are set
        ep_title = existing_ep.title
        badge_label = "SERIES" if resolved_format == MediaFormat.WEB_SERIES else resolved_format.value.upper()
        headline = f"{ep_title}!"
        show_slug = show.slug
        creative_context = f"{ep_title} {idea or ''}"
        script_label = f"Text: {script_text[:36]}..." if script_text else "None"
        active_sub = subtitle_language or "en"

    if solo_male:
        effective_voice_gender = "male"
        gender = "male"
    elif solo_female:
        effective_voice_gender = "female"
        gender = "female"
    elif duet:
        effective_voice_gender = "duet"
        gender = "duet"
    else:
        effective_voice_gender = voice_gender or gender or "female"

    if mass_song or any("mass" in str(x).lower() for x in (genre, music_style, media_format, theme, idea)):
        mass_song = True
        if genre in ("vocal", "vocal_song", "dance"):
            genre = "music/mass_song"
        mass_desc = "mass commercial dance, thumping dappu drums, fast teenmaar rhythm, energetic brass trumpets, whistle drops"
        if not music_style or "mass" not in music_style.lower():
            music_style = f"{mass_desc}, {music_style}" if music_style else mass_desc

    is_voice_over = False
    enable_lipsync = False
    enable_bgm = bool(bgm)
    if voice_over or narration_male or narration_female or tts or goto_production:
        if not goto_production:
            is_voice_over = True
            effective_voice_gender = "male" if narration_male else ("female" if narration_female else (voice_gender or gender or "female"))
            enable_lipsync = bool(tts)
    else:
        is_voice_over, enable_lipsync = classifier_agent.infer_audio_modalities(theme=theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None), idea=idea, script=script_text, media_format=resolved_format)
        if not (solo_male or solo_female or duet):
            effective_voice_gender = voice_gender or ("male" if resolved_format in (MediaFormat.WALKING_TOUR, MediaFormat.MOVIE_CINEMATIC, MediaFormat.EPIC_CINEMATIC) and gender == "female" else (gender or "female"))

    if resolved_format in (MediaFormat.DANCE_VIDEO, MediaFormat.MUSIC_VIDEO):
        enable_bgm, enable_lipsync, is_voice_over = True, True, False
    elif resolved_format in (MediaFormat.SCENIC_RELAXATION, MediaFormat.WALKING_TOUR, MediaFormat.SCENIC_DRIVE, MediaFormat.AMBIENT_LOUNGE, MediaFormat.NATURE_SANCTUARY, MediaFormat.TRAVEL_GUIDE, MediaFormat.TOURIST_GUIDE):
        enable_bgm = True
    else:
        enable_bgm = bool(bgm)

    ref_attrs = None
    if youtube_reference_link:
        from src.scripts.youtube_ingest import extract_reference_video_attributes
        ref_attrs = extract_reference_video_attributes(url=youtube_reference_link, title=title, text=f"{idea or ''} {theme or ''}", default_genre=genre, user_format=fmt_str)
        if not art_style: art_style = ref_attrs.art_style

    culture_context = derive_cultural_context(script_text=creative_context, user_home_country=user.home_country, user_cultural_heritage=user.cultural_heritage, language=language, gender=effective_voice_gender, genre=genre, dance_type=dance_type or "", video_format=fmt_str, art_style=art_style or "")
    print_cli_header(title=ep_title, fmt_str=fmt_str, genre=genre, duration=duration, language=language, active_sub=active_sub, tier=tier, force_live=force_live, dry_run=dry_run, culture_context=culture_context, char_name=character_name, theme=theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None), idea=idea, script_preview=script_label, voice_over=is_voice_over, voice_gender=effective_voice_gender, bgm=enable_bgm, lipsync=enable_lipsync)

    episode = existing_ep or Episode(user_id=user.id, show_id=show.id, title=ep_title, episode_number=episode_number, duration_seconds=duration, format=resolved_format, theme=resolved_theme, topic_or_idea=idea or (theme if theme else ""), custom_script=script_text, youtube_reference_url=youtube_reference_link)
    episode.options.enable_tts, episode.options.enable_voice_over = is_voice_over, is_voice_over
    episode.options.enable_bgm, episode.options.enable_lipsync = enable_bgm, enable_lipsync
    episode.options.voice_gender = effective_voice_gender
    episode.options.target_languages = [language]
    ep_code = f"ep-{episode.episode_number:03d}" if episode.episode_number else f"ep-001"

    eff_net = network or (show.slug if show else "default_network")
    if not restart_id or not ep_ws or not ep_ws.exists():
        clean_fmt = "music_video" if (fmt_str in ("vocal", "music_video", "vocal_song") or "music" in str(fmt_str).lower() or "vocal" in str(fmt_str).lower() or genre in ("vocal", "vocal_song", "song")) else (re.sub(r"[^a-zA-Z0-9_-]", "_", str(fmt_str).lower()).strip("_") or "music_video")
        clean_name = re.sub(r"\s*[-–—]?\s*episode\s*\d+", "", str(title), flags=re.IGNORECASE).strip()
        clean_prod = re.sub(r"[^a-zA-Z0-9]+", "_", clean_name.lower()).strip("_") or "standalone"
        u_cont = getattr(user, "storage_container_name", None) or getattr(user, "email", None) or str(user.id)
        ep_ws = storage_service.get_channel_format_production_episode_path(u_cont, eff_net, clean_fmt, clean_prod, ep_code)
    ep_ws.mkdir(parents=True, exist_ok=True)
    eff_idea = idea or (theme if theme else None) or prompt
    eff_theme = theme or (resolved_theme.value if resolved_theme != ThemeGenre.AUTO else None) or eff_idea
    user_inputs = {
        "user_id": str(user.id), "episode_id": str(episode.id), "episode_number": episode_number,
        "title": ep_title, "duration_seconds": duration, "format": fmt_str, "genre": genre,
        "theme": eff_theme, "idea": eff_idea, "prompt": prompt, "script": script_text, "youtube_reference_url": youtube_reference_link,
        "tier": tier, "profile": profile, "language": language, "subtitle_language": active_sub,
        "gender": effective_voice_gender, "voice_gender": voice_gender, "character_name": character_name,
        "solo_male": solo_male, "solo_female": solo_female, "duet": duet,
        "mass_song": mass_song,
        "music_style": music_style, "style": music_style, "similar_to": similar_to,
        "country": country, "culture": culture, "costume_style": costume_style, "dance_type": dance_type,
        "art_style": art_style or (ref_attrs.art_style if ref_attrs else ""),
        "enable_voice_over": is_voice_over, "enable_bgm": enable_bgm, "enable_lipsync": enable_lipsync,
        "reference_attributes": ref_attrs.model_dump(mode="json") if ref_attrs else None,
        "target_languages": episode.options.target_languages, "num_images": num_images, "use_loras": use_loras,
        "network": eff_net, "created_at": time.time(),
    }
    with open(ep_ws / "user_inputs.json", "w", encoding="utf-8") as f: json.dump(user_inputs, f, indent=2, ensure_ascii=False)

    # 1. Generate Structured Scene Storyboard Plan via Gemini 1.5 Pro (non-dance formats)
    storyboard_path = ep_ws / "storyboard.json"
    storyboard_data = None
    if not rescript and storyboard_path.exists() and storyboard_path.stat().st_size > 0:
        try:
            storyboard_data = json.loads(storyboard_path.read_text(encoding="utf-8"))
            if not storyboard_data.get("id") or not storyboard_data.get("episode_id"):
                storyboard_data["id"] = str(episode.id)
                storyboard_data["episode_id"] = str(episode.id)
                storyboard_path.write_text(json.dumps(storyboard_data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[i] Resume: Loaded existing storyboard from disk.")
        except Exception: pass
    elif rescript:
        print(f"[i] --rescript passed: Bypassing cached storyboard. Generating fresh script via Gemini with saved user inputs...")

    if not storyboard_data:
        # Resolve reference attributes for the prompt if not already available
        if not ref_attrs and youtube_reference_link:
            from src.scripts.youtube_ingest import extract_reference_video_attributes
            ref_attrs = extract_reference_video_attributes(url=youtube_reference_link, title=title, text=f"{idea or ''} {theme or ''}", default_genre=genre, user_format=fmt_str)

        from src.compositor.genre_strategies import resolve_strategy
        strategy = resolve_strategy(media_format=fmt_str, genre=genre, idea=idea or title)
        # Derive gemini_inputs directly from user_inputs (Single Source of Truth)
        gemini_inputs = {
            "title": user_inputs["title"], "duration_seconds": user_inputs["duration_seconds"],
            "language": user_inputs["language"], "genre": user_inputs["genre"],
            "idea": user_inputs["idea"], "theme": user_inputs["theme"],
            "music_style": user_inputs["music_style"], "num_images": user_inputs["num_images"],
            "similar_to": user_inputs["similar_to"], "country": user_inputs["country"],
            "culture": user_inputs["culture"], "gender": user_inputs["gender"],
            "duet": user_inputs["duet"], "solo_male": user_inputs["solo_male"],
            "solo_female": user_inputs["solo_female"], "mass_song": user_inputs.get("mass_song", False),
            "art_style": user_inputs["art_style"],
            "culture_ctx": culture_context, "character_name": user_inputs["character_name"],
            "prompt": user_inputs["prompt"], "user_id": user_inputs["user_id"],
            "network": user_inputs["network"], "episode_number": user_inputs["episode_number"],
        }
        with open(ep_ws / "gemini_inputs.json", "w", encoding="utf-8") as f:
            json.dump(gemini_inputs, f, indent=2, default=str, ensure_ascii=False)

        if script_text:
            gemini_prompt = build_storyboard_prompt(
                title=ep_title, duration_seconds=duration,
                language=language, fmt_str=fmt_str, genre=genre,
                custom_script=script_text, idea=eff_idea, theme=eff_theme,
                refine_script=refine_script,
                art_style=art_style or (ref_attrs.art_style if ref_attrs else ""),
                architecture_style=ref_attrs.architecture_style if ref_attrs else None,
                camera_language=ref_attrs.camera_language if ref_attrs else None,
            )
            schema = None
        else:
            gemini_prompt = strategy.build_gemini_prompt(**gemini_inputs)
            schema = strategy.build_gemini_schema()

        with open(ep_ws / "gemini_prompt.txt", "w", encoding="utf-8") as f:
            f.write(gemini_prompt)
        if schema:
            with open(ep_ws / "gemini_schema.json", "w", encoding="utf-8") as f:
                json.dump(schema, f, indent=2, ensure_ascii=False)

        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter()
        storyboard_data = await llm.generate_structured(gemini_prompt, schema=schema) if schema else await llm.generate_structured(gemini_prompt)
        storyboard_data["id"] = str(episode.id)
        storyboard_data["episode_id"] = str(episode.id)
        strategy.validate_storyboard(storyboard_data)
        with open(storyboard_path, "w", encoding="utf-8") as f:
            json.dump(storyboard_data, f, indent=2, ensure_ascii=False)

    # The canonical project title and storage identity stay English. Localized
    # titles remain inside the storyboard/script artifact for audience-facing use.
    if storyboard_data.get("title_en"):
        ep_title = storyboard_data["title_en"]
        episode.title = ep_title
        headline = f"{ep_title}!"
        if network and not restart_id:
            clean_fmt = "music_video" if (fmt_str in ("vocal", "music_video", "vocal_song") or "music" in str(fmt_str).lower() or "vocal" in str(fmt_str).lower() or genre in ("vocal", "vocal_song", "song")) else (re.sub(r"[^a-zA-Z0-9_-]", "_", str(fmt_str).lower()).strip("_") or "music_video")
            clean_name = re.sub(r"\s*[-–—]?\s*episode\s*\d+", "", str(ep_title), flags=re.IGNORECASE).strip()
            clean_prod = re.sub(r"[^a-zA-Z0-9]+", "_", clean_name.lower()).strip("_") or "standalone"
            new_ep_ws = storage_service.get_channel_format_production_episode_path(u_cont, network, clean_fmt, clean_prod, ep_code)
            if new_ep_ws != ep_ws:
                new_ep_ws.mkdir(parents=True, exist_ok=True)
                import shutil
                for item in ep_ws.iterdir():
                    dst = new_ep_ws / item.name
                    if not dst.exists():
                        shutil.move(str(item), str(dst))
                try:
                    ep_ws.rmdir()
                except Exception:
                    pass
                ep_ws = new_ep_ws
                thumb_dir = ep_ws / "thumbnails"
                storyboard_path = ep_ws / "storyboard.json"

    start_user_balance = float(user.api_credit_balance_usd)
    episode.cost_record = calculate_preflight_estimate(episode)
    episode.estimated_cost_usd = episode.cost_record.predicted_total_usd; repo.save_episode(episode)

    decision_mode, allow_fallback_resolved, selected_tier = await execute_preflight_gate(episode=episode, user=user, language=language, auto_confirm=auto_confirm, local_flag=local, cli_tier=tier)
    if decision_mode == "cancel":
        print("[!] Production cancelled by user. Zero credits deducted.\n"); return None

    is_local_mode = decision_mode == "local" or allow_fallback or allow_fallback_resolved
    if is_local_mode: print("[i] Operating in LOCAL MODE: Zero external API calls, offline synthesis active.")
    tiers_info = recommend_production_tiers(metadata={"language": language}, duration_seconds=duration)
    if selected_tier in tiers_info["tiers"]:
        tier_spec = tiers_info["tiers"][selected_tier]
        episode.estimated_cost_usd = tier_spec["total_cost_usd"]
        repo.save_episode(episode)
        print(f"[i] Active Production Tier: {tier_spec['display_name']} (${episode.estimated_cost_usd:.4f})")

    print(f"\n[1/4] Confirmed Episode Project: {episode.id} (Profile: {profile.upper()}, Tier: {selected_tier.upper()}, Mode: {decision_mode.upper()}, Budget: ${episode.estimated_cost_usd:.4f})")
    thumb_dir = ep_ws / "thumbnails"
    thumb_dir.mkdir(parents=True, exist_ok=True)
    # Always pick the LAST scene image for high-CTR thumbnail with VFX
    all_imgs = sorted([p for p in (ep_ws / "scenes").glob("scene_*.jpg") if p.is_file() and p.stat().st_size > 1000])
    base_keyframe = all_imgs[-1] if all_imgs else None
    generate_episodic_thumbnail(
        output_path=thumb_dir / f"thumb_ep{episode_number:02d}_{language}.jpg",
        base_image_path=base_keyframe,
        badge_config=EpisodicBadgeConfig(episode_number=episode_number, language=language, style="pill", position="top_left", custom_label=badge_label),
        headline=headline,
        enable_vfx=True,
    )
    print(f"[2/4] Rendered Top-Left Episodic Thumbnail with VFX: thumb_ep{episode_number:02d}_{language}.jpg")

    ffmpeg_available = has_ffmpeg()
    effective_dry_run = dry_run or not ffmpeg_available
    if not ffmpeg_available and not dry_run: print("[!] Note: FFmpeg binary not found. Executing with dry_run=True.")
    elif not dry_run: logger.info(f"using_ffmpeg: {get_ffmpeg_binary()}")

    print("[3/4] Synthesizing 4K Keyframes, Voice Stems, BGM, and Compiling Single-Pass FFmpeg Graph...")
    final_video = await pipeline_coordinator.produce_episode_master(
        user_id=user.id, episode_id=episode.id, dry_run=effective_dry_run, language=language,
        subtitle_language=active_sub, force_live=force_live, strict=not is_local_mode, tier=selected_tier,
        character_name=character_name, culture=culture, costume_style=costume_style, dance_type=dance_type,
        gender=effective_voice_gender, art_style=art_style, custom_script=script_text, idea=idea, theme=theme,
        refine_script=refine_script, enable_voice_over=is_voice_over, enable_bgm=enable_bgm, enable_lipsync=enable_lipsync,
        auto_confirm=auto_confirm, profile=profile, music_style=music_style, similar_to=similar_to, country=country,
        network=network, num_images=num_images, use_loras=use_loras,
        preview_only=preview_only, full_confirmed=full_confirmed,
    )
    if not final_video:
        print("[!] Production stopped at Image Quality Gate. No video rendered.\n")
        return None

    # Refresh episodic thumbnail using the LAST picture from scenes all the time with VFX
    all_imgs = sorted([p for p in (ep_ws / "scenes").glob("scene_*.jpg") if p.is_file() and p.stat().st_size > 1000])
    base_keyframe = all_imgs[-1] if all_imgs else None
    if base_keyframe:
        generate_episodic_thumbnail(
            output_path=thumb_dir / f"thumb_ep{episode_number:02d}_{language}.jpg",
            base_image_path=base_keyframe,
            badge_config=EpisodicBadgeConfig(episode_number=episode_number, language=language, style="pill", position="top_left", custom_label=badge_label),
            headline=headline,
            enable_vfx=True,
        )
        print(f"[4/4] Rendered Final 4K Thumbnail from last scene ({base_keyframe.name}) with VFX: thumb_ep{episode_number:02d}_{language}.jpg")
    print(f"[4/4] Master Video Generated: {final_video}")

    saved_episode = repo.get_episode(user.id, episode.id)
    cleared, _ = rights_ledger.verify_episode_rights(episode.id)
    postflight_health = await audit_all_providers_health(force_probe=False)
    print_cli_summary(
        saved_episode, user, final_video,
        rights_ledger.get_records_for_episode(episode.id), cleared,
        provider_statuses=postflight_health,
        start_user_balance=start_user_balance,
    )
    return final_video


def main():
    p = argparse.ArgumentParser(description="Produce a 4K Music Video with Suno vocals, multi-scene keyframes, and kinetic native lyrics.")
    for fl, d, t, h, dst in [
        ("--title", "Soulful Romantic Melody", str, "Title", None), ("--episode", None, int, "Episode #", "episode_number"),
        ("--id", None, str, "Restart/Resume from specific Episode ID", "restart_id"),
        ("--genre", "vocal", str, "Genre (default: vocal)", None), ("--theme", None, str, "Theme", None), ("--idea", None, str, "Idea", None),
        ("--script", None, str, "Script", None), ("--duration", "10s", parse_duration, "Duration (e.g. 10s, 30m, 1h, 20)", None), ("--language", "en", str, "Lang", None),
        ("--subtitle-language", None, str, "Sub", None), ("--tier", None, str, "Tier", None), ("--country", None, str, "Country", None),
        ("--culture", None, str, "Culture", None), ("--costume", None, str, "Costume", "costume_style"),
        ("--dance", None, str, "Dance", "dance_type"), ("--character", None, str, "Char", "character_name"),
        ("--gender", "female", str, "Gender", None), ("--type", "music_video", str, "Format (default: music_video)", "media_format"),
        ("--style", None, str, "Musical style (e.g. soft, energetic, poetic, festive, romantic)", "music_style"),
        ("--similar-to", None, str, "Reference famous song for mood/tenderness/pattern", "similar_to"),
        ("--art-style", None, str, "Style", "art_style"), ("--voice-gender", None, str, "Voice gender", "voice_gender"),
        ("--youtube-reference-link", None, str, "YouTube URL", "youtube_reference_link"),
        ("--user-id", None, str, "User ID scope", "user_id"),
        ("--network", None, str, "Network or Channel universe name/slug", "network"),
        ("--name", None, str, "Project / Episode name (alias for --title)", "name_alias"),
        ("--format", None, str, "Media format (alias for --type)", "format_alias"),
        ("--languages", None, str, "Target Languages (e.g. en,te,hi)", "target_languages"),
        ("--target-languages", None, str, "Target Languages alias (e.g. en,te,hi)", "target_languages"),
        ("--prompt", None, str, "Prompt directive", None),
        ("--images", 1, int, "Number of images to generate and rotate across song duration (default: 1)", "num_images"),
    ]:
        p.add_argument(fl, **{"type": t, "default": d, "help": h, **({"dest": dst} if dst else {})})
    for fls, h, dst in [
        (["--dry-run"], "Dry run", "dry_run"),
        (["-y", "--yes"], "Auto confirm", "auto_confirm"), (["--allow-fallback"], "Fallback", "allow_fallback"),
        (["--voice-over"], "Voiceover", "voice_over"),
        (["--narration-male"], "Male voice", "narration_male"), (["--narration-female"], "Female voice", "narration_female"),
        (["--tts"], "Conversational TTS", "tts"), (["--bgm"], "Background music", "bgm"),
        (["--refine", "--refine-script"], "Refine screenplay", "refine_script"),
        (["--loras", "--use-loras"], "Use persistent network LoRA models", "use_loras"),
        (["--preview-only"], "Render only 30s fast preview", "preview_only"),
        (["--full"], "Skip interactive preview pause and render full master directly", "full_confirmed"),
        (["--solo-male"], "Solo male vocalist and solo male lead", "solo_male"),
        (["--solo-female"], "Solo female vocalist and solo female lead", "solo_female"),
        (["--duet"], "Duet vocalists (male & female) with both leads", "duet"),
        (["--mass", "--mass-song", "--mass-beats"], "Mass song with mass beats (high-energy dappu, teenmaar & brass)", "mass_song"),
        (["--rescript", "--regenerate-script"], "Regenerate storyboard script via Gemini even if cached", "rescript"),
    ]:
        p.add_argument(*fls, action="store_true", default=False, help=h, dest=dst)
    profile_group = p.add_mutually_exclusive_group()
    profile_group.add_argument("--local", dest="profile", action="store_const", const="local", help="Offline deterministic production")
    profile_group.add_argument("--dev", dest="profile", action="store_const", const="development", help="Live providers with development fallbacks")
    profile_group.add_argument("--live", dest="profile", action="store_const", const="production", help="Live production providers, strict fallback policy")
    args = vars(p.parse_args())
    if args.get("name_alias"):
        args["title"] = args.pop("name_alias")
    else:
        args.pop("name_alias", None)
    if args.get("format_alias"):
        args["media_format"] = args.pop("format_alias")
    else:
        args.pop("format_alias", None)
    profile = args.pop("profile") or "development"
    args["profile"] = profile
    args["local"] = profile == "local"
    args["force_live"] = profile in ("development", "production")
    if profile == "production":
        args["allow_fallback"] = False
    asyncio.run(run_production(**args))

if __name__ == "__main__":
    main()
