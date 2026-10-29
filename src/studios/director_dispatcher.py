"""Studio Director Dispatcher.

Routes screenplay generation to specialized, single-responsibility Studio Agents
based on channel, genre, sub-genre, archetype, and autonomous prompt analysis.
Prevents prompt cross-contamination between different nature and ambient sub-genres.
"""

from __future__ import annotations

import os
from typing import Any, Optional

from src.core.telemetry import logger
from src.studios.ambient_world.relax_models import RelaxAudioMasterSpec, RelaxScene, RelaxScreenplay
from src.studios.alpine_studio.alpine_director import generate_alpine_screenplay
from src.studios.waterfall_studio.waterfall_director import generate_waterfall_screenplay
from src.studios.silent_hearth.hearth_director import generate_hearth_screenplay
from src.studios.ambient_world.relax_director import generate_relax_screenplay_gemini
from src.studios.zen_studio.zen_director import generate_zen_screenplay_gemini
from src.studios.healing_relaxation.healing_director import generate_healing_screenplay
from src.studios.rain_retreat.rain_director import generate_rain_screenplay
from src.studios.cozy_ambiance.cozy_director import generate_cozy_screenplay


async def dispatch_studio_director(
    genre: str = "relax/nature",
    sub_genre: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    user_id: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    tier: str = "balanced",
    weather: Optional[str] = "normal",
    country: Optional[str] = None,
    language: Optional[str] = None,
    culture: Optional[str] = None,
    **extra_kwargs: Any,
) -> RelaxScreenplay:
    """Dispatch screenplay request to the appropriate specialized studio director."""
    p_lower = (custom_prompt or "").lower()
    ch_lower = (channel_id or "").lower()
    genre_lower = (genre or "").lower()
    sub_lower = (sub_genre or "").lower()
    arch_lower = (primary_archetype or "").lower()

    # Atmospheric weather injection for non-normal weather modes
    eff_custom_prompt = custom_prompt
    if weather and weather != "normal":
        weather_modifiers = {
            "rain": "heavy dramatic downpour, thick vertical sheets of cascading rain, visible falling rain streaks filling the air, heavy rainwater streaming down eaves with explosive splashing water droplets, and rich deep rain ASMR soundscape",
            "snow": "serene snowfall, frosted surfaces, and calm winter atmospheric haze",
            "fog": "morning coastal mist, volumetric god rays, and soft atmospheric haze",
            "sunset": "glorious golden hour sunset, warm 2800K illumination, and long dusk shadows",
            "night": "deep midnight starlit sky, glowing celestial stars, and tranquil nighttime atmosphere",
        }
        mod = weather_modifiers.get(weather)
        if mod and (not custom_prompt or not any(k in custom_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset", "night"])):
            eff_custom_prompt = f"{custom_prompt or ''} ({mod})".strip()

    kwargs = dict(
        custom_prompt=eff_custom_prompt, duration_seconds=duration_seconds, num_shots=num_shots,
        camera_motion=camera_motion, user_id=user_id, raw_output_path=raw_output_path,
        image_model=image_model, channel_id=channel_id or "earth_serenade",
        tier=tier, weather=weather, country=country, language=language, culture=culture,
        **extra_kwargs,
    )

    # 0. Dedicated Blue-Chip Documentary & Science Studio Dispatch
    is_science = "science" in genre_lower or "science" in sub_lower or "science" in arch_lower
    if "doc" in genre_lower or "documentary" in ch_lower or "doc" in sub_lower or is_science or "nations" in genre_lower:
        from src.studios.documentary_studio.doc_storyboard import generate_documentary_storyboard_gemini
        from src.studios.documentary_studio.doc_dispatch_helper import resolve_doc_dispatch_params
        eff_doc_genre, eff_archetype_name, theme_seed = resolve_doc_dispatch_params(
            sub_lower=sub_lower,
            arch_lower=arch_lower,
            is_science=is_science,
            primary_archetype=primary_archetype,
            sub_genre=sub_genre,
            custom_prompt=custom_prompt,
            user_id=user_id,
            channel_id=channel_id or "euro_discovery",
        )
        sb = await generate_documentary_storyboard_gemini(
            genre=eff_doc_genre,
            theme_seed=theme_seed,
            duration_seconds=duration_seconds,
            language="en",
            num_shots=num_shots,
            raw_output_path=raw_output_path,
            archetype=eff_archetype_name,
            channel_id=channel_id or "euro_discovery",
        )
        # Filter out trailing itinerary summary/recap card so documentary never ends on an infographic slide
        non_summary_scenes = [
            s for s in sb.scenes
            if not (
                getattr(s, "is_itinerary_summary", False)
                or "summary" in str(getattr(s, "shot_type", "")).lower()
                or "summary" in str(getattr(s, "location_hub", "")).lower()
                or "recap" in str(getattr(s, "location_hub", "")).lower()
            )
        ]
        full_narration = " ".join(s.narration_text.strip() for s in non_summary_scenes if getattr(s, "narration_text", None))
        relax_scenes = [
            RelaxScene(
                scene_index=idx + 1,
                location_hub=getattr(s, "location_hub", None) or getattr(s, "origin_name", None) or f"Scenic Vista {idx + 1}",
                shot_type=s.shot_type,
                camera_rig=getattr(s, "camera_rig", None) or "heavy_lift_cine_drone",
                color_temp_kelvin=getattr(s, "color_temp_kelvin", 5500),
                visual_prompt=s.visual_prompt,
                motion_prompt=s.motion_prompt,
                motion_negative_prompt=getattr(s, "motion_negative_prompt", None) or "rapid cuts, chaotic movement, jerky shake, disorienting pans",
                model_configs=getattr(s, "model_configs", None) or {},
                image_model_configs=getattr(s, "image_model_configs", None) or (__import__("src.studios.directorial_configs", fromlist=["build_default_image_model_configs"]).build_default_image_model_configs(s.visual_prompt, getattr(s, "location_hub", "Scene") or "Scene") if getattr(s, "visual_prompt", None) else {}),
                domain=getattr(s, "motion_domain", "landscape_solid"),
                motion_type=getattr(s, "motion_type", "ken_burns"),
                recommended_model="h3_max" if getattr(s, "motion_type", "") in ("ai_diffusion", "diffusion", "neural") else getattr(s, "recommended_model", "local_drone"),
                camera_movement=getattr(s, "camera_movement", None) or getattr(s, "drone_choreography", None) or "slow_drone_forward",
                motion_rationale=getattr(s, "motion_rationale", None),
                duration_seconds=s.duration_seconds,
                narration_text=getattr(s, "narration_text", "") or "",
                day_number=getattr(s, "day_number", 1) or 1,
                start_time=getattr(s, "start_time", None), end_time=getattr(s, "end_time", None),
                visit_duration=getattr(s, "visit_duration", None), transit_duration=getattr(s, "transit_duration", None),
                is_map_transition=getattr(s, "is_map_transition", False), is_itinerary_summary=False,
                is_vacation_scope=getattr(s, "is_vacation_scope", False),
                attraction_name=getattr(s, "attraction_name", None),
                origin_name=getattr(s, "origin_name", None), destination_name=getattr(s, "destination_name", None),
                origin_coords=getattr(s, "origin_coords", None), destination_coords=getattr(s, "destination_coords", None),
                distance_local=getattr(s, "distance_local", None), transit_mode=getattr(s, "transit_mode", "walk") or "walk",
                chapter_index=getattr(s, "chapter_index", None), is_chapter_head=getattr(s, "is_chapter_head", True),
                chapter_title=getattr(s, "chapter_title", None), chapter_subtitle=getattr(s, "chapter_subtitle", None),
                chapter_stats=getattr(s, "chapter_stats", None), fact_badge=getattr(s, "fact_badge", None),
                secondary_visual_prompt=getattr(s, "secondary_visual_prompt", None),
                secondary_motion_prompt=getattr(s, "secondary_motion_prompt", None),
            )
            for idx, s in enumerate(non_summary_scenes)
        ]
        return RelaxScreenplay(
            title=sb.title,
            story_topic=sb.title,
            recommended_fps=24,
            audio_master=RelaxAudioMasterSpec(
                audio_mode="documentary_voiceover",
                spoken_narration_script=full_narration,
                suno_musical_tags=sb.audio_tags or "cinematic orchestral documentary, sparse ambient foley, 48kHz broadcast master",
                target_lufs=-14.0,
                ducking_db=-18.0,
            ),
            itinerary_summary=sb.itinerary_summary,
            scenes=relax_scenes,
            total_duration_seconds=sb.total_duration,
            cluster="science" if is_science else "documentary",
            genre="science" if is_science else "documentary",
            sub_genre=sub_genre or eff_archetype_name,
            primary_archetype=primary_archetype or eff_archetype_name,
        )

    # 0. Dedicated Rain Retreat & River ASMR Dispatch (genre 'relax/rain')
    is_rain = (
        genre_lower in {"relax/rain", "rain_retreat"}
        or "rain" in genre_lower
        or sub_lower in {"biophilic_retreat", "forest_rain", "river_rain", "rainy_bedroom", "tropical_village_rain"}
        or any(k in arch_lower for k in ["rain", "bedroom", "bamboo", "village"])
        or (any(w in p_lower for w in ["rain", "rainfall", "village rain", "bamboo hut", "monsoon"]) and not any(w in p_lower for w in ["ocean", "sea", "lagoon", "beach", "coast"]))
    )
    if is_rain:
        eff_sub = sub_genre or primary_archetype or "heavy_rain_swiss_alps"
        logger.info(f"dispatcher_route: target='RainRetreatStudio' genre='{genre}' sub_genre='{eff_sub}' archetype='{primary_archetype}' prompt='{custom_prompt}'")
        return await generate_rain_screenplay(sub_genre=eff_sub, primary_archetype=primary_archetype, **kwargs)

    # 0.1 Dedicated Ocean Studio Dispatch (All 6 Diurnal Timings under genre 'relax/ocean')
    if genre_lower in {"relax/ocean", "ocean"} or "ocean" in arch_lower or "ocean" in sub_lower or "bioluminescent" in arch_lower or any(w in p_lower for w in ["ocean retreat", "ocean villa", "overwater villa", "turquoise lagoon"]):
        from src.studios.ocean_studio.ocean_director import generate_ocean_screenplay_gemini
        return await generate_ocean_screenplay_gemini(genre="relax/ocean", sub_genre=sub_genre or primary_archetype or "ocean_daytime_shore", primary_archetype=primary_archetype or "ocean_daytime_shore", **kwargs)

    # 0.1 Dedicated Desert Studio Dispatch (genre 'relax/desert')
    if "desert" in arch_lower or "desert" in sub_lower or "desert" in genre_lower or "dune" in arch_lower or any(w in p_lower for w in ["desert", "sand dune", "dunes", "bedouin"]):
        from src.studios.desert_studio.desert_director import generate_desert_screenplay_gemini
        return await generate_desert_screenplay_gemini(genre=genre or "relax/desert", sub_genre=sub_genre or primary_archetype or "desert_daytime_tent", primary_archetype=primary_archetype or "desert_daytime_tent", **kwargs)

    # 0.2 Dedicated Beach Lounge Studio Dispatch (genre 'relax/beach_lounge')
    if genre_lower in {"relax/beach_lounge", "beach_lounge"} or "beach_luxury" in arch_lower or "beach_sunset" in arch_lower or "beach_twilight" in arch_lower or "beach_starlit" in arch_lower or any(w in p_lower for w in ["beach cabana", "beach lounge", "beach daybed", "beach pergola"]):
        from src.studios.beach_lounge_studio.beach_lounge_director import generate_beach_lounge_screenplay_gemini
        return await generate_beach_lounge_screenplay_gemini(genre="relax/beach_lounge", sub_genre=sub_genre or primary_archetype or "beach_luxury_cabana_day", primary_archetype=primary_archetype or "beach_luxury_cabana_day", **kwargs)

    # 0.3 Dedicated Mountain Studio Dispatch (genre 'relax/mountain')
    if genre_lower in {"relax/mountain", "mountain"} or "mountain_summit" in arch_lower or "mountain_daytime" in arch_lower or "mountain_sunset" in arch_lower or "mountain_starlit" in arch_lower:
        from src.studios.mountain_studio.mountain_director import generate_mountain_screenplay_gemini
        return await generate_mountain_screenplay_gemini(genre="relax/mountain", sub_genre=sub_genre or primary_archetype or "mountain_daytime_vista", primary_archetype=primary_archetype or "mountain_daytime_vista", **kwargs)

    # 0.4 Dedicated Valley Studio Dispatch (genre 'relax/valley')
    if genre_lower in {"relax/valley", "valley"} or "valley_wildflower" in arch_lower or "valley_morning" in arch_lower or "valley_glacial" in arch_lower or "valley_sunset" in arch_lower:
        from src.studios.valley_studio.valley_director import generate_valley_screenplay_gemini
        return await generate_valley_screenplay_gemini(genre="relax/valley", sub_genre=sub_genre or primary_archetype or "valley_wildflower_meadow", primary_archetype=primary_archetype or "valley_wildflower_meadow", **kwargs)

    # 0.5 Dedicated Blizzard Studio Dispatch (genre 'relax/blizzard')
    if genre_lower in {"relax/blizzard", "blizzard"} or "blizzard" in arch_lower or "blizzard" in sub_lower or any(w in p_lower for w in ["blizzard", "snowstorm", "howling blizzard", "snowfall asmr"]):
        from src.studios.blizzard_studio.blizzard_director import generate_blizzard_screenplay_gemini
        return await generate_blizzard_screenplay_gemini(genre="relax/blizzard", sub_genre=sub_genre or primary_archetype or "blizzard_cozy_cabin_window", primary_archetype=primary_archetype or "blizzard_cozy_cabin_window", **kwargs)

    # 0.6 Dedicated Forest Studio Dispatch (genre 'relax/forest')
    if genre_lower in {"relax/forest", "forest"} or "forest_mossy" in arch_lower or "forest_babbling" in arch_lower or "forest_morning" in arch_lower or "forest_twilight" in arch_lower or ("forest" in arch_lower and "rain" not in arch_lower):
        from src.studios.forest_studio.forest_director import generate_forest_screenplay_gemini
        return await generate_forest_screenplay_gemini(genre="relax/forest", sub_genre=sub_genre or primary_archetype or "forest_mossy_canopy_day", primary_archetype=primary_archetype or "forest_mossy_canopy_day", **kwargs)

    # 0.7 Dedicated Travel & Scenic Wonders Studio Dispatch (genre 'travel/scenic')
    if genre_lower in {"travel/scenic", "travel", "travel_scenic"} or "travel" in genre_lower or arch_lower in {"cities", "natural_wonders", "remote_places", "tourist_places", "spiritual_places", "iconic_places"} or sub_lower in {"cities", "natural_wonders", "remote_places", "tourist_places", "spiritual_places", "iconic_places"} or any(w in p_lower for w in ["drone aerial", "city skyline", "charminar", "hitec city", "golconda"]):
        from src.studios.travel_studio.travel_director import generate_travel_screenplay_gemini
        return await generate_travel_screenplay_gemini(genre="travel/scenic", sub_genre=sub_genre or primary_archetype or "cities", primary_archetype=primary_archetype or "cities", **kwargs)

    # 0.8 Dedicated Living Art & Gallery Studio Dispatch (genre 'relax/art')
    if genre_lower in {"relax/art", "art", "living_art"} or "art" in genre_lower or arch_lower in {"living_impressionism", "grand_gallery", "artist_atelier", "sumie_ukiyoe", "stained_glass", "klimt_gold_leaf", "surrealist_dream"} or sub_lower in {"living_impressionism", "grand_gallery", "artist_atelier", "sumie_ukiyoe", "stained_glass", "klimt_gold_leaf", "surrealist_dream"} or any(w in p_lower for w in ["oil painting", "living canvas", "museum gallery", "atelier", "monet", "van gogh", "klimt"]):
        from src.studios.art_studio.art_director import generate_art_screenplay_gemini
        return await generate_art_screenplay_gemini(genre="relax/art", sub_genre=sub_genre or primary_archetype or "living_impressionism", primary_archetype=primary_archetype or "living_impressionism", **kwargs)

    # 1. Japanese Zen Studio Dispatch (Kyoto Zen, Bamboo Groves, Raked Rock Gardens, Tsukubai)
    if genre_lower in {"relax/zen", "zen"} or sub_lower in {"zen_garden", "bamboo_grove", "lotus_pond"} or arch_lower in {"zen_garden", "bamboo_grove"}:
        logger.info(f"dispatcher_route: target='ZenStudio' genre='{genre}' sub_genre='{sub_genre}' archetype='{primary_archetype}' channel='{channel_id}'")
        return await generate_zen_screenplay_gemini(genre=genre, sub_genre=sub_genre or "zen_garden", primary_archetype=primary_archetype or "zen_garden", **kwargs)

    # 2. Global Healing Sanctuaries & Solfeggio Dispatch (Himalayas, Bali, Geothermal, Redwoods)
    if genre_lower in {"relax/healing", "healing_relaxation", "healing"} or sub_lower in {"global_healing", "himalayan_valley", "geothermal_springs", "redwood_cathedral", "solfeggio_sanctuary", "crystal_spring"} or arch_lower in {"sacred_sanctuary", "healing_sanctuary", "geothermal_springs"}:
        logger.info(f"dispatcher_route: target='HealingRelaxationStudio' genre='{genre}' sub_genre='{sub_genre}'")
        return await generate_healing_screenplay(sub_genre=sub_genre or "global_healing", **kwargs)

    # 3. Cozy Ambiance & Fireplace Dispatch
    if genre_lower in {"relax/cozy", "cozy_ambiance"} or sub_lower in {"cozy_living", "cozy_shelter", "fireplace"}:
        logger.info(f"dispatcher_route: target='CozyAmbianceStudio' genre='{genre}' sub_genre='{sub_genre}'")
        return await generate_cozy_screenplay(sub_genre=sub_genre or "cozy_shelter", **kwargs)

    # 4. Waterfall Studio Dispatch
    if (
        "waterfall" in genre_lower
        or "waterfall" in sub_lower
        or "waterfall" in arch_lower
        or (not any(w in p_lower for w in ["alps", "swiss", "mountain", "hearth", "rain", "zen", "bamboo"]) and any(w in p_lower for w in ["waterfall", "niagara", "iguazu", "victoria falls", "cascade", "plunge pool"]))
    ):
        logger.info(f"dispatcher_route: target='WaterfallStudio' prompt='{custom_prompt}'")
        return await generate_waterfall_screenplay(**kwargs)

    # 5. Silent Hearth & Beach Campfire Studio Dispatch
    if (
        "hearth" in ch_lower
        or "campfire" in ch_lower
        or "hearth" in genre_lower
        or "hearth" in sub_lower
        or "campfire" in sub_lower
        or any(w in p_lower for w in ["campfire", "fire pit", "hearth", "beach fire", "shoreline fire"])
    ):
        logger.info(f"dispatcher_route: target='SilentHearthStudio' prompt='{custom_prompt}'")
        return await generate_hearth_screenplay(**kwargs)

    # 6. Alpine Nature Studio Dispatch (Swiss Alps, Dolomites, Mountains, Meadows)
    if (
        ("alpine" in genre_lower or "nature" in genre_lower or "alpine" in sub_lower or "alpine" in arch_lower or "mountain" in arch_lower
         or any(w in p_lower for w in ["alps", "swiss", "mountain", "dolomites", "peaks", "matterhorn", "meadow", "glacial stream"]))
        and not any(w in arch_lower for w in ["desert", "dune", "pavilion", "oasis"])
        and not any(w in sub_lower for w in ["desert", "dune", "pavilion", "oasis"])
    ):
        logger.info(f"dispatcher_route: target='AlpineStudio' prompt='{custom_prompt}'")
        return await generate_alpine_screenplay(**kwargs)

    # 7. Dedicated Music Video & Folk Dance Studio Dispatch (Structured rhyming lyrics, zero spoken voiceover)
    is_music = (
        genre_lower.startswith("music/")
        or genre_lower.startswith("dance/")
        or "dance" in genre_lower
        or "music" in genre_lower
        or sub_lower in {"mass_folk_dance", "classical_dance", "romantic_melody", "party_upbeat", "happy_feelgood", "festive_celebration", "soulful_devotional", "energetic_party"}
    )
    if is_music:
        from src.studios.music_video_studio.music_video_director import generate_music_video_screenplay
        logger.info(f"dispatcher_route: target='MusicVideoStudio' genre='{genre}' sub='{sub_genre}'")
        return await generate_music_video_screenplay(
            genre=genre,
            sub_genre=sub_genre,
            primary_archetype=primary_archetype,
            **kwargs,
        )

    # 8. Default Ambient World Studio (Fusion & 14 Archetypes)
    logger.info(f"dispatcher_route: target='AmbientWorldStudio' genre='{genre}' prompt='{custom_prompt}'")
    return await generate_relax_screenplay_gemini(
        primary=primary_archetype or sub_genre or "",
        genre=genre,
        **kwargs,
    )

