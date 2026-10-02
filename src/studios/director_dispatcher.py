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
) -> RelaxScreenplay:
    """Dispatch screenplay request to the appropriate specialized studio director."""
    p_lower = (custom_prompt or "").lower()
    ch_lower = (channel_id or "").lower()
    genre_lower = (genre or "").lower()
    sub_lower = (sub_genre or "").lower()
    arch_lower = (primary_archetype or "").lower()

    if genre_lower in {"relax/healing", "relax/zen"} or sub_lower in {"zen_healing", "lotus_pond"} or arch_lower == "zen_garden":
        logger.info(f"dispatcher_route: target='ZenStudio' genre='{genre}' sub_genre='{sub_genre}' archetype='{primary_archetype}'")
        return await generate_zen_screenplay_gemini(
            genre=genre,
            sub_genre=sub_genre or "zen_healing",
            primary_archetype=primary_archetype or "zen_garden",
            custom_prompt=custom_prompt or "",
            duration_seconds=duration_seconds,
            user_id=user_id or "user_krishna_01",
            num_shots=num_shots,
            raw_output_path=raw_output_path,
        )

    # 1. Waterfall Studio Dispatch
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

    # 2. Silent Hearth & Beach Campfire Studio Dispatch
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

    # 3. Alpine Nature Studio Dispatch (Swiss Alps, Dolomites, Mountains, Meadows)
    if (
        "alpine" in genre_lower
        or "nature" in genre_lower
        or "alpine" in sub_lower
        or "alpine" in arch_lower
        or "mountain" in arch_lower
        or any(w in p_lower for w in ["alps", "swiss", "mountain", "dolomites", "peaks", "matterhorn", "meadow", "glacial stream"])
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

    # 4. Default Ambient World Studio (Rain, Zen, Cozy Living Spaces, Fusion)
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
