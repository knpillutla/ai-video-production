"""Phase 2 End-to-End Video Production Pipeline Coordinator.

Uses the Genre Strategy Pattern: each content format (dance, nature, walking tour,
comedy, epic, etc.) has its own strategy that configures prompt, schema, audio mode,
lipsync mode, FPS, and FFmpeg chain — while sharing model adapters and infrastructure.
"""

import time
from pathlib import Path
from uuid import UUID

from src.cinematics.color.film_luts import resolve_film_lut
from src.cinematics.foley.foley_engine import foley_engine
from src.compliance.rights_ledger import rights_ledger
from src.compositor.ffmpeg_pipeline import execute_single_pass_render
from src.compositor.genre_strategies import resolve_strategy
from src.compositor.pipeline_finalize import finalize_render
from src.compositor.pipeline_prompts import build_storyboard_prompt, extract_dialogue_text
from src.compositor.pipeline_scenes import synthesize_scenes
from src.compositor.timeline import compile_timeline_from_scenes
from src.core.storage import storage_service
from src.core.telemetry import logger
from src.domain.repo import repo
from src.domain.rights import AssetType, CommercialLicenseType
from src.mcp.model_selector.audit import audit_pipeline_models
from src.mcp.topic_memory.server import check_topic_duplicate, remember_topic
from src.providers.dance.fal_kling import FalKlingAdapter
from src.providers.lipsync.fal_latentsync import FalLatentSyncAdapter
from src.providers.llm.gemini_adapter import GeminiLLMAdapter
from src.providers.music.suno_adapter import SunoMusicAdapter
from src.providers.tts.azure_speech import AzureSpeechTTSAdapter
from src.providers.visual.fal_zimage import FalZImageAdapter
from src.scripts.cli_presentation import print_storyboard_artifact_manifest
from src.scripts.local_subtitles import generate_subtitle_bundle
from src.services.character_consistency import get_or_create_character_anchor
from src.services.cultural_derivation import derive_cultural_context


class ProductionPipelineCoordinator:
    """Orchestrates the 0-GPU end-to-end video synthesis and single-pass FFmpeg render."""

    def __init__(self, strict: bool = False):
        self.strict = strict
        self.llm = GeminiLLMAdapter(strict=strict)
        self.visual = FalZImageAdapter()
        self.fal_flux = self.visual
        self.fal_kling = FalKlingAdapter()
        self.fal_lipsync = FalLatentSyncAdapter()
        self.tts = AzureSpeechTTSAdapter()
        self.music = SunoMusicAdapter()

    async def produce_episode_master(
        self,
        user_id: UUID,
        episode_id: UUID,
        dry_run: bool = False,
        language: str = "en",
        subtitle_language: str | None = None,
        force_live: bool = False,
        strict: bool = False,
        tier: str = "balanced",
        character_name: str | None = None,
        culture: str | None = None,
        costume_style: str | None = None,
        dance_type: str | None = None,
        gender: str = "female",
        art_style: str | None = None, custom_script: str | None = None,
        idea: str | None = None, theme: str | None = None, refine_script: bool = False,
        enable_voice_over: bool = True, enable_bgm: bool | None = None,
        enable_lipsync: bool | None = None,
    ) -> Path:
        """Produce a complete broadcast-grade master video for an episode project."""
        self.llm.strict = strict
        if tier == "low_cost": self.llm.model = "gemini-1.5-flash"
        elif tier == "cinematic": self.llm.model = "gemini-1.5-pro"

        episode = repo.get_episode(user_id, episode_id)
        if not episode:
            raise ValueError(f"Episode {episode_id} not found for user {user_id}")

        enable_bgm = getattr(episode.options, "enable_bgm", True) if enable_bgm is None else enable_bgm
        enable_lipsync = getattr(episode.options, "enable_lipsync", False) if enable_lipsync is None else enable_lipsync

        show = repo.get_show(user_id, episode.show_id)
        show_slug = show.slug if show else "default_universe"

        ep_dir = storage_service.get_episode_path(str(user_id), show_slug, str(episode_id))
        scenes_dir, stems_dir, renders_dir = ep_dir / "scenes", ep_dir / "audio_stems", ep_dir / "master_renders"
        for d in (scenes_dir, stems_dir, renders_dir):
            d.mkdir(parents=True, exist_ok=True)

        fmt_str = str(episode.format.value if hasattr(episode.format, "value") else episode.format).lower()
        eff_script, eff_idea = custom_script or getattr(episode, "custom_script", None), idea or getattr(episode, "topic_or_idea", None)
        eff_theme, yt_url = theme or getattr(getattr(episode, "theme", None), "value", None), getattr(episode, "youtube_reference_url", None)

        from src.scripts.youtube_ingest import extract_reference_video_attributes
        ref_attrs = extract_reference_video_attributes(
            url=yt_url, title=episode.title, text=f"{eff_idea or ''} {eff_script or ''}",
            default_genre=show.genre if show else "comedy", user_format=fmt_str,
        )
        effective_art_style = art_style or (ref_attrs.art_style if yt_url else "")

        user_inputs = {
            "user_id": str(user_id), "episode_id": str(episode_id), "title": episode.title,
            "duration_seconds": episode.duration_seconds, "format": fmt_str, "theme": eff_theme,
            "idea": eff_idea, "script": eff_script, "youtube_reference_url": yt_url,
            "tier": tier, "language": language, "subtitle_language": subtitle_language,
            "gender": gender, "character_name": character_name, "art_style": effective_art_style or ref_attrs.art_style_display,
            "enable_voice_over": enable_voice_over, "enable_bgm": enable_bgm, "enable_lipsync": enable_lipsync,
            "reference_attributes": ref_attrs.model_dump(mode="json"),
            "refine_script": refine_script, "dry_run": dry_run, "created_at": time.time(),
        }
        await storage_service.save_json(ep_dir / "user_inputs.json", user_inputs)

        logger.info(f"starting_production_pipeline: ep={episode.title}, user={user_id}, tier={tier}")

        meta_dict = {"genre": show.genre if show else "general", "show_slug": show_slug, "tier": tier, "language": language}
        if episode_id:
            logger.info(f"skipping_duplicate_check: episode_id {episode_id} provided")
        else:
            _composite_topic = " ".join(filter(None, [eff_theme, fmt_str, meta_dict.get("genre")])) + f" | {episode.title}"
            _composite_topic = _composite_topic.strip(" |")
            topic_check = await check_topic_duplicate(topic=_composite_topic, metadata=meta_dict, user_id=str(user_id), language=language)
            if topic_check.get("is_duplicate"):
                raise ValueError(topic_check.get("alert_message") or "Duplicate content detected.")

        await audit_pipeline_models(
            language=language, budget_tier=tier, output_dir=ep_dir,
            metadata={"episode_id": str(episode.id), "title": episode.title, "genre": meta_dict["genre"], "tier": tier},
        )

        # Resolve genre strategy — determines prompt, schema, audio mode, lipsync, FPS, FFmpeg chain
        eff_genre = show.genre if show else "comedy"
        strategy = resolve_strategy(media_format=fmt_str, genre=eff_genre, idea=eff_idea)
        logger.info(f"genre_strategy_resolved: {strategy.genre_id} (audio={strategy.audio_mode}, lipsync={strategy.lipsync_mode})")

        # 1. Generate Structured Scene Storyboard Plan via Gemini (strategy-configured)
        storyboard_path = ep_dir / "storyboard.json"
        storyboard_data = None
        if storyboard_path.exists() and storyboard_path.stat().st_size > 0:
            try:
                import json
                storyboard_data = json.loads(storyboard_path.read_text(encoding="utf-8"))
                logger.info(f"storyboard_cache_hit: loading existing storyboard for {episode_id}")
            except Exception as e:
                logger.warning(f"storyboard_load_failed: {e}, regenerating...")
        if not storyboard_data:
            storyboard_data = await self._generate_storyboard(
                strategy, episode, language, eff_genre, eff_idea, eff_script,
                eff_theme, effective_art_style, ref_attrs, refine_script, fmt_str,
            )
            await storage_service.save_json(storyboard_path, storyboard_data)

        # Lightweight sanity check (no rigid Pydantic validation, no retry loops)
        issues = strategy.validate_storyboard(storyboard_data)
        if issues:
            logger.warning(f"storyboard_quality_issues: {issues}")

        scenes_list = storyboard_data.get("scenes", [])
        full_story_text = " ".join(extract_dialogue_text(s) for s in scenes_list)
        await remember_topic(topic=episode.title, metadata=meta_dict, final_story=full_story_text, episode_id=str(episode.id), show_slug=show_slug, user_id=str(user_id))

        chars_list = storyboard_data.get("characters", [])
        lead_c = chars_list[0] if (chars_list and isinstance(chars_list[0], dict)) else {}
        eff_gender = gender or lead_c.get("gender") or storyboard_data.get("vocal_gender", "female")
        user_entity = repo.get_user(user_id)
        derived_culture = derive_cultural_context(
            script_text=f"{episode.title} {full_story_text}",
            user_home_country=user_entity.home_country if user_entity else None,
            user_cultural_heritage=culture or (user_entity.cultural_heritage if user_entity else None),
            language=language, gender=eff_gender, genre=show.genre if show else "comedy",
            dance_type=dance_type or "", video_format=fmt_str, art_style=effective_art_style or "",
        )

        tot_raw = sum(float(s.get("duration_seconds", 4.0)) for s in scenes_list)
        tgt_dur = float(episode.duration_seconds)
        scale = (tgt_dur / tot_raw) if (tgt_dur > 0 and tot_raw > 0 and abs(tgt_dur - tot_raw) > 0.5) else 1.0

        char_anchor = None
        is_scenic_strategy = strategy.genre_id in ("walking_tour", "nature_documentary", "tourist_guide", "epic_cinematic", "mountain_survival")
        wants_character = bool(character_name or lead_c.get("name") or (not is_scenic_strategy and any(k in fmt_str for k in ("web_series", "movie", "dance", "music"))))
        if wants_character:
            effective_culture = culture or derived_culture.culture
            effective_costume = costume_style or derived_culture.clothing_style
            c_name = character_name or lead_c.get("name")
            char_anchor = get_or_create_character_anchor(
                user_id=user_id, show_id=episode.show_id, character_name=c_name,
                culture=effective_culture, costume_style=effective_costume, gender=eff_gender,
                language=language, age=lead_c.get("age"), body_composition=lead_c.get("body_composition"),
                height=lead_c.get("height"), role=lead_c.get("role"), appearance_summary=lead_c.get("appearance_summary"),
                source_text=" ".join(filter(None, [episode.title, eff_idea, eff_script])),
            )

        # 2. Synthesize Visual Keyframes, Motion Video, and Voice Stems for each scene
        enable_video_motion = force_live or strategy.genre_id in ("walking_tour", "dance", "tourist_guide", "travel_guide", "nature_documentary", "epic_cinematic", "mountain_survival", "music_video") or getattr(episode.options, "enable_video_motion", False)
        print_storyboard_artifact_manifest(
            storyboard_data=storyboard_data, fmt_str=fmt_str,
            enable_voice_over=enable_voice_over, enable_bgm=enable_bgm,
            enable_video_motion=enable_video_motion, enable_lipsync=bool(enable_lipsync),
            culture_context=derived_culture,
        )
        compiled_scenes, subtitle_segments, current_time = await synthesize_scenes(
            scenes_list=scenes_list, scenes_dir=scenes_dir, stems_dir=stems_dir,
            episode=episode, scale=scale, char_anchor=char_anchor,
            derived_culture=derived_culture, visual_adapter=self.visual,
            tts_adapter=self.tts, language=language,
            enable_voice_over=enable_voice_over, enable_lipsync=bool(enable_lipsync),
            force_live=force_live, kling_adapter=self.fal_kling,
            enable_video_motion=enable_video_motion,
        )

        # 3. Generate Commercially Cleared Soundtrack via Suno & record rights (if BGM enabled)
        bgm_path = stems_dir / "bgm_master.wav" if enable_bgm else None
        if enable_bgm and bgm_path:
            bgm_style = storyboard_data.get("suno_tags") or (ref_attrs.soundtrack_style if (yt_url and ref_attrs.soundtrack_style) else (derived_culture.music_style or "Gentle rain drops, distant thunder, ambient nature"))
            full_lyrics = storyboard_data.get("lyrics") or " ".join(extract_dialogue_text(s) for s in scenes_list if extract_dialogue_text(s))
            eff_vocal = (gender if gender in ("male", "duet", "female") else None) or (getattr(episode.options, "voice_gender", None) if getattr(episode.options, "voice_gender", None) in ("male", "duet", "female") else None) or storyboard_data.get("vocal_gender") or "female"
            await self.music.generate_to_file(output_path=bgm_path, genre=bgm_style, duration_seconds=current_time, lyrics=full_lyrics, vocal_gender=eff_vocal, title=episode.title, force_live=force_live)
            rights_ledger.record_asset(episode_id=episode.id, asset_type=AssetType.MUSIC, file_path=str(bgm_path), provider="Suno/CineAI", model_name="v3.5-pro", license_type=CommercialLicenseType.FULL_COMMERCIAL_OWNERSHIP, license_id=f"SUNO-COMM-{episode.id}", cleared=True)

        # 4. Generate Multi-Language Subtitle Bundle & Procedural Atmospheric Foley Stem
        active_sub_lang = subtitle_language or ("en" if language.lower() != "en" else "en")
        bundle_info = generate_subtitle_bundle(
            base_segments=subtitle_segments if enable_voice_over else [],
            base_language=language, output_dir=ep_dir / "subtitles", default_subtitle_lang=active_sub_lang,
        )
        burned_ass_path = bundle_info["burned_ass_path"] if enable_voice_over else None

        foley_path = stems_dir / "foley_master.wav"
        if not (foley_path.is_file() and foley_path.stat().st_size > 1000):
            foley_engine.synthesize(
                weather_type=derived_culture.weather_condition,
                setting_type=derived_culture.setting_type,
                space=derived_culture.environment_space,
                duration_seconds=max(1.0, current_time),
                output_path=foley_path,
            )

        # 5. Compile Multi-Track Timeline Layout & Film Color Grade (4K UHD per Directive 14)
        is_vert = "9_16" in fmt_str or "vertical" in fmt_str
        target_res = (2160, 3840) if is_vert else (3840, 2160)
        eff_fps = int(storyboard_data.get("recommended_fps") or getattr(strategy, "default_fps", 30))
        film_lut = resolve_film_lut(culture=derived_culture.culture, genre=eff_genre, weather=derived_culture.weather_condition)
        timeline = compile_timeline_from_scenes(
            scene_data=compiled_scenes, bgm_path=bgm_path, foley_path=foley_path,
            subtitle_path=burned_ass_path, target_resolution=target_res, fps=eff_fps, film_lut=film_lut,
        )

        # 6. Execute Single-Pass FFmpeg Compositing
        render_t0 = time.perf_counter()
        render_name = f"master_16x9_ep{episode.episode_number:02d}_{language}.mp4" if language and language != "en" else f"master_16x9_ep{episode.episode_number:02d}.mp4"
        final_video = await execute_single_pass_render(
            timeline=timeline, output_path=renders_dir / render_name,
            dry_run=dry_run,
        )
        render_elapsed = max(0.5, time.perf_counter() - render_t0)

        # 7–10. Post-Render QA, Evidence, Cost, Episode Finalization
        final_video = await finalize_render(
            episode, final_video, storyboard_data, scenes_list, ep_dir, timeline,
            render_elapsed, enable_voice_over, enable_bgm, enable_lipsync,
        )
        return final_video

    # ---------------------------------------------------------------------------
    # Strategy-aware storyboard generation
    # ---------------------------------------------------------------------------
    async def _generate_storyboard(self, strategy, episode, language, genre, idea,
                                   script, theme, art_style, ref_attrs, refine_script, fmt_str):
        """Generate storyboard using strategy's prompt + schema, with custom script fallback."""
        if script:
            prompt = build_storyboard_prompt(
                title=episode.title, duration_seconds=episode.duration_seconds,
                language=language, fmt_str=fmt_str, genre=genre,
                custom_script=script, idea=idea, theme=theme, refine_script=refine_script,
                art_style=art_style or ref_attrs.art_style_display,
                architecture_style=ref_attrs.architecture_style, camera_language=ref_attrs.camera_language,
            )
            return await self.llm.generate_structured(prompt)
        prompt = strategy.build_gemini_prompt(
            title=episode.title, duration_seconds=episode.duration_seconds,
            language=language, genre=genre, idea=idea, art_style=art_style,
            culture_ctx=None,
        )
        schema = strategy.build_gemini_schema()
        return await self.llm.generate_structured(prompt, schema=schema)


pipeline_coordinator = ProductionPipelineCoordinator()

__all__ = ['ProductionPipelineCoordinator', 'pipeline_coordinator']
