"""Documentary Storyboard & Model Routing Engine.

Directorial generation for 6 blue-chip documentary archetypes:
1. Wildlife (Biological kinematics, animal behaviors)
2. Ocean (Deep-sea, coral reefs, pelagic life)
3. Nature (Canopies, seasonal transitions, rainforests)
4. Mountains (Alpine peaks, glacial valleys, survival)
5. Art (Renaissance frescoes, sculptures, fine canvas macro)
6. Ancient Structures (Megaliths, pyramids, lost temples)
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from src.studios.documentary_studio.doc_templates import (
    DocGenre,
    DocScene,
    DocStoryboard,
    DOC_TEMPLATES,
    GENRE_MODEL_DEFAULTS,
    generate_documentary_storyboard,
)



async def generate_documentary_storyboard_gemini(
    genre: DocGenre = DocGenre.WILDLIFE,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    language: str = "en",
    user_id: str = "user_krishna_01",
    theme_seed: Optional[str] = None,
    num_shots: int = 1,
    raw_output_path: Optional[Any] = None,
    archetype: Optional[str] = None,
    weather: Optional[str] = "normal",
    **kwargs: Any,
) -> DocStoryboard:
    """Dynamically generate authoritative BBC/NatGeo documentary or Tour Director script and storyboard via Gemini."""
    from src.studios.documentary_studio.doc_directorial_prompt import (
        build_doc_directorial_prompt,
        build_tour_directorial_prompt,
        is_tour_archetype,
    )

    effective_theme = theme_seed or custom_prompt or genre.value
    eff_archetype = (archetype or genre.value).lower().strip()
    tour_mode = is_tour_archetype(eff_archetype)

    is_auto_dur = (duration_seconds is None or duration_seconds <= 0 or duration_seconds == -1)
    if is_auto_dur:
        nom_duration = 180.0
        num_scenes = max(6, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else (10 if not tour_mode else 8))
        dur_per_scene = round(nom_duration / num_scenes, 2)
    elif tour_mode:
        nom_duration = duration_seconds
        num_scenes = max(6, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else max(6, round(duration_seconds / 10.0)))
        dur_per_scene = round(duration_seconds / num_scenes, 2)
    else:
        nom_duration = duration_seconds
        num_scenes = max(1, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else max(2, round(duration_seconds / 12.0)))
        dur_per_scene = round(duration_seconds / num_scenes, 2)
    domain_tag, default_model = GENRE_MODEL_DEFAULTS.get(genre, ("landscape_solid", "kling_v3"))

    print(f"\n[GEMINI DIRECTORIAL AGENT INVOKED]")
    print(f"   * Domain / Archetype: {'TOUR DIRECTOR' if tour_mode else 'DOCUMENTARY'} ({eff_archetype})")
    print(f"   * Genre / Theme:      {genre.value.upper()} ~ \"{effective_theme}\"")
    print(f"   * Duration Mode:      {'AUTO (-1)' if is_auto_dur else f'{duration_seconds}s'} ({num_scenes} Scene(s) @ ~{dur_per_scene}s each)")
    print(f"   * Language:           {language.upper()}")

    from src.studios.documentary_studio.doc_voice_service import doc_voice_service
    eff_wpm, eff_wps, provider_desc = doc_voice_service.get_speech_cadence(language=language)

    # Word budget calculation calibrated to active TTS provider & speech rate
    max_words_per_scene = max(15, int(round(max(1.0, dur_per_scene - 1.5) * eff_wps)))
    total_words_budget = max_words_per_scene * num_scenes

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        from src.core.telemetry import logger
        llm = GeminiLLMAdapter()

        eff_prompt_shots = -1 if (num_shots is None or num_shots == -1) else num_scenes
        chan_id = kwargs.get("channel_id") or "euro_discovery"
        exec_mode = str(kwargs.get("execution_mode") or "prod")
        if tour_mode:
            full_prompt = build_tour_directorial_prompt(
                archetype=eff_archetype, custom_prompt=effective_theme, duration_seconds=duration_seconds,
                num_shots=eff_prompt_shots, camera_motion="perspective_drone", speech_cadence_wpm=eff_wpm,
                speech_words_per_sec=eff_wps, tts_provider_name=provider_desc, channel_id=chan_id,
                execution_mode=exec_mode,
            )
        else:
            full_prompt = build_doc_directorial_prompt(
                genre=genre.value, archetype=eff_archetype, custom_prompt=effective_theme,
                duration_seconds=duration_seconds, num_shots=eff_prompt_shots, camera_motion="perspective_drone",
                speech_cadence_wpm=eff_wpm, speech_words_per_sec=eff_wps, tts_provider_name=provider_desc,
                channel_id=chan_id, execution_mode=exec_mode,
            )

        if raw_output_path:
            try:
                from pathlib import Path
                p_out = Path(raw_output_path)
                prompt_file = p_out.parent / "gemini_input_prompt.txt" if p_out.is_file() or p_out.suffix else p_out / "gemini_input_prompt.txt"
                prompt_file.parent.mkdir(parents=True, exist_ok=True)
                prompt_file.write_text(full_prompt, encoding="utf-8")
                logger.info(f"gemini_input_prompt_saved: {prompt_file}")
            except Exception as e_p:
                logger.warning(f"failed_to_save_gemini_input_prompt: {e_p}")
        logger.info(f"gemini_directorial_request_sent: mode={'tour' if tour_mode else 'doc'} archetype='{eff_archetype}'\n--- PROMPT SENT TO GEMINI ---\n{full_prompt}\n-----------------------------")
        print(f"\n[GEMINI DIRECTORIAL REQUEST DISPATCHED ({'TOUR' if tour_mode else 'DOC'})] Generating structured screenplay...")

        data = await llm.generate_structured(full_prompt)
        logger.info(f"gemini_directorial_response_received:\n{json.dumps(data, indent=2) if isinstance(data, dict) else str(data)}")
        title_disp = (data.get("title") or "Documentary") if isinstance(data, dict) else "Documentary"
        scene_count = len(data.get("scenes", [])) if isinstance(data, dict) else 0
        try:
            print(f"\n[GEMINI DIRECTORIAL RESPONSE RECEIVED] '{title_disp}' ({scene_count} scenes synthesized)\n")
        except UnicodeEncodeError:
            print(f"\n[GEMINI DIRECTORIAL RESPONSE RECEIVED] ({scene_count} scenes synthesized)\n")

        if data and isinstance(data, dict) and data.get("scenes") and len(data["scenes"]) >= 1:
            from src.studios.documentary_studio.doc_screenplay_duration import calibrate_screenplay_durations
            data, calc_total_duration = calibrate_screenplay_durations(
                data, speech_words_per_sec=eff_wps, fallback_dur_per_scene=dur_per_scene, is_auto_duration=is_auto_dur
            )
            if raw_output_path:
                try:
                    from pathlib import Path
                    raw_p = Path(raw_output_path)
                    raw_p.parent.mkdir(parents=True, exist_ok=True)
                    raw_p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                    logger.info(f"raw_gemini_screenplay_saved: {raw_p} (total_duration={calc_total_duration}s)")
                except Exception as e_raw:
                    logger.warning(f"failed_to_save_raw_gemini_screenplay: {e_raw}")
            from src.studios.documentary_studio.doc_chapter_cadence_service import flatten_chapters_to_timeline
            raw_scenes, _ = flatten_chapters_to_timeline(data, fallback_dur_per_scene=dur_per_scene)
            has_sub_shots = any(bool(sc.get("shots")) for sc in (data.get("chapters") or data.get("scenes") or []))
            if not tour_mode and not has_sub_shots and (num_shots is not None and num_shots > 0 and num_shots != -1):
                raw_scenes = raw_scenes[:num_scenes]
            itinerary_summary = data.get("itinerary_summary")

            # Strict Zero-Fallback Validation & Interleaving for tour archetypes (omit trailing summary slide)
            if tour_mode:
                from src.studios.documentary_studio.doc_tour_validator import validate_tour_screenplay_contract
                from src.studios.documentary_studio.doc_tour_interleaver import interleave_tour_storyboard_scenes
                validate_tour_screenplay_contract(data)
                data["scenes"] = interleave_tour_storyboard_scenes(
                    data["scenes"], data.get("itinerary_summary"), duration_seconds, include_summary_card=False
                )
                raw_scenes = data["scenes"]
                itinerary_summary = data.get("itinerary_summary")

            # Eliminate any trailing infographic summary/recap cards so documentaries conclude naturally
            raw_scenes = [
                sc for sc in raw_scenes
                if not (
                    sc.get("is_itinerary_summary")
                    or "summary" in str(sc.get("shot_type", "")).lower()
                    or "recap" in str(sc.get("location_hub", "")).lower()
                    or "summary" in str(sc.get("location_hub", "")).lower()
                )
            ]

            sub_genre = str(kwargs.get("sub_genre") or data.get("sub_genre") or "").lower()
            is_geo_mode = (
                genre == DocGenre.PLACES
                or getattr(genre, "value", str(genre)).lower() in ("places", "nations", "cities")
                or (archetype or "").lower().strip() in ("cities", "countries", "nations", "country", "city", "nation")
                or (sub_genre and any(k in sub_genre for k in ("nations", "cities", "europe_nations")))
            )
            dest_entity = data.get("destination_entity") or data.get("destination_name")
            if not dest_entity and title_disp and ":" in title_disp:
                dest_entity = title_disp.split(":")[0].strip()

            from src.studios.documentary_studio.doc_storyboard_builder import build_doc_scene_list
            doc_scenes = build_doc_scene_list(
                raw_scenes=raw_scenes,
                dur_per_scene=dur_per_scene,
                is_geo_mode=is_geo_mode,
                dest_entity=dest_entity,
                tour_mode=tour_mode,
                domain_tag=domain_tag,
                default_model=default_model,
            )

            from src.studios.documentary_studio.doc_curiosity_title_service import derive_contextual_doc_titles
            ctr_t, auto_thumb, auto_vars = derive_contextual_doc_titles(
                dest_entity, data.get('title') or theme_seed, data.get('synopsis'),
                gemini_yt_title=data.get('youtube_title'),
                gemini_thumb_headline=data.get('thumbnail_headline'),
                gemini_thumb_variants=data.get('thumbnail_variants')
            )
            th_head = auto_thumb
            th_vars = auto_vars
            pin_comm = data.get('pinned_comment') or f'?? PINNED COMMUNITY QUIZ: Did you know this about {dest_entity or "this destination"}? Which landmark or story surprised you most? Drop your perspective below! ??'

            audio_m = data.get('audio_master') or {}
            suno_p = audio_m.get('suno_prompt') or data.get('suno_prompt')
            suno_t = audio_m.get('suno_musical_tags') or data.get('audio_tags') or 'cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master'

            sb = DocStoryboard(
                title=data.get('title') or (theme_seed.title() if theme_seed else 'Documentary'),
                youtube_title=ctr_t,
                genre=genre, total_duration=calc_total_duration, scenes=doc_scenes, language=language,
                audio_tags=suno_t, suno_prompt=suno_p,
                itinerary_summary=itinerary_summary, thumbnail_headline=th_head.strip().upper(),
                thumbnail_hero_scene_index=int(data.get("thumbnail_hero_scene_index", 1) or 1),
                thumbnail_curiosity_rationale=data.get("thumbnail_curiosity_rationale") or f"High-CTR curiosity hook for {dest_entity or 'documentary'}.",
                thumbnail_variants=th_vars, pinned_comment=pin_comm, community_quiz=data.get("community_quiz"),
            )
            logger.info(f"gemini_doc_storyboard_success: title='{sb.title}', scenes={len(sb.scenes)}, thumb='{sb.thumbnail_headline}'")
            return sb
        raise RuntimeError(f"Gemini LLM returned empty or malformed documentary storyboard data: {data}")
    except Exception as ex:
        from src.core.telemetry import logger
        err_detail = str(ex).strip() or repr(ex)
        logger.error(f"gemini_doc_storyboard_fatal_error: {err_detail}")
        raise RuntimeError(f"Gemini documentary directorial screenplay generation failed: {err_detail}") from ex


__all__ = ["DocGenre", "DocScene", "DocStoryboard", "generate_documentary_storyboard", "generate_documentary_storyboard_gemini"]
