"""Studio Director Dispatcher.

Routes screenplay generation to specialized, single-responsibility Studio Agents
based on channel, genre, sub-genre, archetype, and autonomous prompt analysis.
Prevents prompt cross-contamination between different nature and ambient sub-genres.
"""

from __future__ import annotations

import os
from typing import Optional

from src.core.telemetry import logger
from src.studios.ambient_world.relax_models import RelaxScreenplay
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
) -> RelaxScreenplay:
    """Dispatch screenplay request to the appropriate specialized studio director."""
    p_lower = (custom_prompt or "").lower()
    ch_lower = (channel_id or "").lower()
    genre_lower = (genre or "").lower()
    sub_lower = (sub_genre or "").lower()
    arch_lower = (primary_archetype or "").lower()

    kwargs = dict(
        custom_prompt=custom_prompt, duration_seconds=duration_seconds, num_shots=num_shots,
        camera_motion=camera_motion, user_id=user_id, raw_output_path=raw_output_path,
        image_model=image_model, channel_id=channel_id or "earth_serenade",
        tier=tier,
    )

    # 0. Dedicated Ocean Studio Dispatch (All 6 Diurnal Timings under genre 'relax/ocean')
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
        return await generate_zen_screenplay_gemini(
            genre=genre,
            sub_genre=sub_genre or "zen_garden",
            primary_archetype=primary_archetype or "zen_garden",
            custom_prompt=custom_prompt or "",
            duration_seconds=duration_seconds,
            user_id=user_id or "user_krishna_01",
            num_shots=num_shots,
            raw_output_path=raw_output_path,
            image_model=image_model,
            channel_id=channel_id or "earth_serenade",
        )

    # 2. Global Healing Sanctuaries & Solfeggio Dispatch (Himalayas, Bali, Geothermal, Redwoods)
    if genre_lower in {"relax/healing", "healing_relaxation", "healing"} or sub_lower in {"global_healing", "himalayan_valley", "geothermal_springs", "redwood_cathedral", "solfeggio_sanctuary", "crystal_spring"} or arch_lower in {"sacred_sanctuary", "healing_sanctuary", "geothermal_springs"}:
        logger.info(f"dispatcher_route: target='HealingRelaxationStudio' genre='{genre}' sub_genre='{sub_genre}'")
        return await generate_healing_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
            sub_genre=sub_genre or "global_healing",
        )

    # 2. Rain Retreat & River ASMR Dispatch
    if genre_lower in {"relax/rain", "rain_retreat"} or sub_lower in {"biophilic_retreat", "forest_rain", "river_rain", "rainy_bedroom"} or "rain" in arch_lower or "bedroom" in arch_lower:
        logger.info(f"dispatcher_route: target='RainRetreatStudio' genre='{genre}' sub_genre='{sub_genre}' archetype='{primary_archetype}'")
        return await generate_rain_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
            sub_genre=sub_genre or "rainy_bedroom",
            primary_archetype=primary_archetype,
        )

    # 3. Cozy Ambiance & Fireplace Dispatch
    if genre_lower in {"relax/cozy", "cozy_ambiance"} or sub_lower in {"cozy_living", "cozy_shelter", "fireplace"}:
        logger.info(f"dispatcher_route: target='CozyAmbianceStudio' genre='{genre}' sub_genre='{sub_genre}'")
        return await generate_cozy_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
            sub_genre=sub_genre or "cozy_shelter",
        )

    # 4. Waterfall Studio Dispatch
    if (
        "waterfall" in genre_lower
        or "waterfall" in sub_lower
        or "waterfall" in arch_lower
        or (not any(w in p_lower for w in ["alps", "swiss", "mountain", "hearth", "rain", "zen", "bamboo"]) and any(w in p_lower for w in ["waterfall", "niagara", "iguazu", "victoria falls", "cascade", "plunge pool"]))
    ):
        logger.info(f"dispatcher_route: target='WaterfallStudio' prompt='{custom_prompt}'")
        return await generate_waterfall_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
        )

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
        return await generate_hearth_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
        )

    # 6. Alpine Nature Studio Dispatch (Swiss Alps, Dolomites, Mountains, Meadows)
    if (
        ("alpine" in genre_lower or "nature" in genre_lower or "alpine" in sub_lower or "alpine" in arch_lower or "mountain" in arch_lower
         or any(w in p_lower for w in ["alps", "swiss", "mountain", "dolomites", "peaks", "matterhorn", "meadow", "glacial stream"]))
        and not any(w in arch_lower for w in ["desert", "dune", "pavilion", "oasis"])
        and not any(w in sub_lower for w in ["desert", "dune", "pavilion", "oasis"])
    ):
        logger.info(f"dispatcher_route: target='AlpineStudio' prompt='{custom_prompt}'")
        return await generate_alpine_screenplay(
            custom_prompt=custom_prompt,
            duration_seconds=duration_seconds,
            num_shots=num_shots,
            camera_motion=camera_motion,
            user_id=user_id,
            channel_id=channel_id,
            raw_output_path=raw_output_path,
            image_model=image_model,
        )

    # 7. Default Ambient World Studio (Fusion & 14 Archetypes)
    logger.info(f"dispatcher_route: target='AmbientWorldStudio' genre='{genre}' prompt='{custom_prompt}'")
    return await generate_relax_screenplay_gemini(
        primary=primary_archetype or sub_genre or "",
        custom_prompt=custom_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        genre=genre,
        user_id=user_id,
        channel_id=channel_id,
        raw_output_path=raw_output_path,
        image_model=image_model,
    )
