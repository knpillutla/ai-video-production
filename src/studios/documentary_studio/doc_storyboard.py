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

    if tour_mode:
        num_scenes = max(6, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else max(6, round(duration_seconds / 10.0)))
    else:
        num_scenes = max(1, num_shots if (num_shots is not None and num_shots > 0 and num_shots != -1) else max(2, round(duration_seconds / 12.0)))
    dur_per_scene = round(duration_seconds / num_scenes, 2)
    domain_tag, default_model = GENRE_MODEL_DEFAULTS.get(genre, ("landscape_solid", "kling_v3"))

    print(f"\n[GEMINI DIRECTORIAL AGENT INVOKED]")
    print(f"   * Domain / Archetype: {'TOUR DIRECTOR' if tour_mode else 'DOCUMENTARY'} ({eff_archetype})")
    print(f"   * Genre / Theme:      {genre.value.upper()} ~ \"{effective_theme}\"")
    print(f"   * Duration:           {duration_seconds}s ({num_scenes} Scene(s) @ ~{dur_per_scene}s each)")
    print(f"   * Language:           {language.upper()}")

    from src.studios.documentary_studio.doc_voice_service import doc_voice_service
    eff_wpm, eff_wps, provider_desc = doc_voice_service.get_speech_cadence(language=language)

    # Word budget calculation calibrated to active TTS provider & speech rate
    max_words_per_scene = max(6, int(round(max(1.0, dur_per_scene - 1.5) * eff_wps)))
    total_words_budget = max_words_per_scene * num_scenes

    try:
        import json
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        from src.core.telemetry import logger
        llm = GeminiLLMAdapter()

        eff_prompt_shots = -1 if (num_shots is None or num_shots == -1) else num_scenes
        chan_id = kwargs.get("channel_id") or "euro_discovery"
        if tour_mode:
            full_prompt = build_tour_directorial_prompt(
                archetype=eff_archetype,
                custom_prompt=effective_theme,
                duration_seconds=duration_seconds,
                num_shots=eff_prompt_shots,
                camera_motion="perspective_drone",
                speech_cadence_wpm=eff_wpm,
                speech_words_per_sec=eff_wps,
                tts_provider_name=provider_desc,
                channel_id=chan_id,
            )
        else:
            full_prompt = build_doc_directorial_prompt(
                genre=genre.value,
                archetype=eff_archetype,
                custom_prompt=effective_theme,
                duration_seconds=duration_seconds,
                num_shots=eff_prompt_shots,
                camera_motion="perspective_drone",
                speech_cadence_wpm=eff_wpm,
                speech_words_per_sec=eff_wps,
                tts_provider_name=provider_desc,
                channel_id=chan_id,
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
            if raw_output_path:
                try:
                    from pathlib import Path
                    raw_p = Path(raw_output_path)
                    raw_p.parent.mkdir(parents=True, exist_ok=True)
                    raw_p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                    logger.info(f"raw_gemini_screenplay_saved: {raw_p}")
                except Exception as e_raw:
                    logger.warning(f"failed_to_save_raw_gemini_screenplay: {e_raw}")

            raw_scenes = data["scenes"] if tour_mode else data["scenes"][:num_scenes]
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

            is_geo_mode = (
                genre == DocGenre.PLACES
                or getattr(genre, "value", str(genre)).lower() in ("places", "nations", "cities")
                or (archetype or "").lower().strip() in ("cities", "countries", "nations", "country", "city", "nation")
                or (sub_genre and any(k in sub_genre.lower() for k in ("nations", "cities", "europe_nations")))
            )
            dest_entity = data.get("destination_entity") or data.get("destination_name")
            if not dest_entity and title_disp and ":" in title_disp:
                dest_entity = title_disp.split(":")[0].strip()

            doc_scenes = []
            for idx, sc in enumerate(raw_scenes):
                sc_dur = max(2.0, float(sc.get("duration_seconds", dur_per_scene)))
                v_prompt = sc.get("visual_prompt") or sc.get("visual_description", "")
                loc_hub = sc.get("location_hub") or sc.get("scene_title") or sc.get("landmark_name") or sc.get("title") or "Scenic Vista"
                cam_rig = sc.get("camera_rig") or ("locked_tripod_telephoto" if "locked_tripod" in str(sc.get("shot_type", "")) else "heavy_lift_cine_drone")
                cam_move = sc.get("camera_movement") or ("locked_stationary_cinemagraph" if cam_rig == "locked_tripod_telephoto" else "slow_drone_forward")
                m_prompt = sc.get("motion_prompt") or sc.get("camera_movement_description") or f"Cinematic 4K capture from {cam_rig}. {cam_move} overlooking landscape. Natural environmental micro-motion."
                mot_type = sc.get("motion_type") or "ken_burns"
                mot_rationale = sc.get("motion_rationale") or f"Tier-0 4K drone cinematography via {cam_move} ($0.00 compute)."
                n_text = sc.get("narration_text") or sc.get("narration") or sc.get("audio_narration") or sc.get("voiceover") or ""

                if is_geo_mode and idx == 0:
                    sc_dur = max(10.0, min(12.0, sc_dur if sc_dur >= 9.0 else 11.0))
                    mot_type = "ken_burns"
                    sc["recommended_model"] = "local_drone"
                    if not cam_move or cam_move == "locked_stationary_cinemagraph":
                        cam_move = "slow_drone_forward"
                    if dest_entity and not any(k in n_text.lower() for k in ("welcome to", "in the heart", "paradox", "enigma", "lies a sovereign", "across the")):
                        n_text = f"Welcome to {dest_entity}. {n_text}".strip()
                elif is_geo_mode and idx == len(raw_scenes) - 1 and len(raw_scenes) >= 2:
                    sc_dur = max(10.0, min(12.0, sc_dur if sc_dur >= 9.0 else 11.0))
                    mot_type = "ken_burns"
                    sc["recommended_model"] = "local_drone"
                    cam_move = "dollyout"
                    if not any(k in v_prompt.lower() for k in ("twilight", "sunset", "horizon", "panorama", "pull-back", "skyline")):
                        v_prompt = f"{v_prompt} Captured at golden twilight sunset in a sweeping panoramic aerial pull-back over {dest_entity or 'the historic destination'}."
                    if not any(k in n_text.lower() for k in ("legacy", "enduring", "timeless", "spirit", "farewell", "stands as", "testament", "soul", "explore", "journey", "remains")):
                        n_text = f"From its ancient foundations to its vibrant living spirit, {dest_entity or 'this remarkable destination'} stands as an enduring testament to culture, beauty, and wonder."

                shot_type_val = str(sc.get("shot_type", "")).lower()
                is_tour_overview = bool(sc.get("is_itinerary_overview", False) or (tour_mode and (idx == 0 and "overview" in shot_type_val)))
                is_tour_summary = False
                is_tour_vacation = bool(sc.get("is_vacation_scope", False) or (tour_mode and "vacation" in shot_type_val))
                is_map_trans = bool(sc.get("is_map_transition", False) or (tour_mode and any(k in shot_type_val for k in ("map", "transition", "cartographic"))))

                is_info_slide = is_map_trans or is_tour_overview or is_tour_summary or is_tour_vacation
                if is_info_slide:
                    cam_rig, cam_move, mot_type = "locked_tripod_telephoto", "locked_stationary_cinemagraph", "ken_burns"
                    m_prompt, mot_rationale = "Static locked tripod hold on 4K display.", "Static infographic hold ($0.00 compute)."

                attr_name = None if is_tour_overview else sc.get("attraction_name")
                if not attr_name and not is_info_slide:
                    attr_name = sc.get("origin_name")
                if not is_info_slide and not any(k in v_prompt.lower() for k in ("panoramic", "ultra-wide", "wide vista", "establishing shot")):
                    v_prompt = f"{v_prompt}, expansive panoramic landscape vista, 18mm ultra-wide architectural lens, generous sky headroom and foreground breathing room"

                ld_cfg = (sc.get("model_configs") or {}).get("local_drone") or {}
                drone_choreo = ld_cfg.get("movement") or sc.get("camera_movement") or sc.get("drone_choreography")
                start_framing = sc.get("start_framing") or {
                    "pan": ld_cfg.get("start_pan", "center"),
                    "zoom": ld_cfg.get("start_zoom", "normal"),
                    "tilt": ld_cfg.get("start_tilt", "center"),
                }
                motion_curve = ld_cfg.get("curve") or sc.get("motion_curve", "cosine")
                if isinstance(drone_choreo, str) and not is_info_slide:
                    cam_move = drone_choreo

                rec_model = (
                    "local_drone" if (is_geo_mode and idx == 0)
                    else ("h3_max" if sc.get("motion_type") in ("ai_diffusion", "diffusion", "neural")
                          else (sc.get("recommended_model") or sc.get("motion_model") or default_model))
                )

                doc_scenes.append(
                    DocScene(
                        scene_index=idx + 1,
                        duration_seconds=sc_dur,
                        shot_type=sc.get("shot_type", "wide" if idx == 0 else "medium"),
                        motion_domain=sc.get("domain") or domain_tag,
                        recommended_model=rec_model,
                        visual_prompt=v_prompt,
                        motion_prompt=m_prompt,
                        narration_text=n_text,
                        motion_engine=sc.get("motion_engine", "local_drone"),
                        drone_choreography=drone_choreo,
                        start_framing=start_framing,
                        motion_curve=motion_curve,
                        weather=sc.get("weather", "none"),
                        is_map_transition=is_map_trans,
                        attraction_name=attr_name,
                        origin_name=sc.get("origin_name") or sc.get("scene_title"),
                        destination_name=sc.get("destination_name"),
                        origin_coords=sc.get("origin_coords"), destination_coords=sc.get("destination_coords"),
                        distance_local=sc.get("distance_local"), transit_mode=sc.get("transit_mode", "walk"),
                        day_number=int(sc.get("day_number", 1) or 1),
                        start_time=sc.get("start_time"), end_time=sc.get("end_time"),
                        visit_duration=sc.get("visit_duration"), transit_duration=sc.get("transit_duration"),
                        attraction_cost=sc.get("attraction_cost"), is_itinerary_overview=is_tour_overview,
                        is_itinerary_summary=is_tour_summary, is_vacation_scope=is_tour_vacation,
                        camera_rig=cam_rig, camera_movement=cam_move, motion_type=mot_type, motion_rationale=mot_rationale,
                        location_hub=loc_hub, color_temp_kelvin=int(sc.get("color_temp_kelvin") or 5500),
                        chapter_title=sc.get("chapter_title"), chapter_subtitle=sc.get("chapter_subtitle"), chapter_stats=sc.get("chapter_stats"), fact_badge=sc.get("fact_badge"),
                        model_configs=sc.get("model_configs"), image_model_configs=sc.get("image_model_configs"),
                        motion_negative_prompt=sc.get("motion_negative_prompt") or "tight crop, cropped building, cut off steeple, claustrophobic framing, camera shake, jitter, artifacts",
                    )
                )

            th_head = data.get("thumbnail_headline") or data.get("thumbnail_text") or (f"WHAT IS {dest_entity.upper()} BEST KNOWN FOR?" if is_geo_mode and dest_entity else "WHAT ARE THEY HIDING HERE?")
            th_vars = data.get("thumbnail_variants") or [
                {"variant": "A", "headline": th_head.strip().upper(), "angle": "sovereign_question"},
                {"variant": "B", "headline": f"{dest_entity.upper() if dest_entity else 'EUROPE'}'S GREATEST SECRET", "angle": "hidden_anomaly"},
                {"variant": "C", "headline": f"HOW {dest_entity.upper() if dest_entity else 'THEY'} SURVIVED", "angle": "scale_paradox"},
            ]
            pin_comm = data.get("pinned_comment") or f"📍 PINNED COMMUNITY QUIZ: Did you know this about {dest_entity or 'this destination'}? Which landmark or story surprised you most? Drop your perspective below! 👇"

            sb = DocStoryboard(
                title=data.get("title") or (theme_seed.title() if theme_seed else "Documentary"),
                genre=genre, total_duration=duration_seconds, scenes=doc_scenes, language=language,
                audio_tags=data.get("audio_tags") or "cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master",
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
