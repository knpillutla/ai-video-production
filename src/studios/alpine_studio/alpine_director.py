"""Alpine Nature Studio Dedicated Directorial Agent.

Synthesizes master screenplays specifically tailored for panoramic mountain landscapes,
Swiss Alps, snow peaks, wildflower valleys, and glacial streams.
"""

from __future__ import annotations

import os
import random
from typing import Optional

from src.services.topic_memory import topic_memory
from src.studios.ambient_world.relax_models import RelaxScreenplay
from src.studios.alpine_studio.alpine_prompt import ALPINE_LANDMARK_POOL, build_alpine_prompt


async def generate_alpine_screenplay(
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    tier: str = "balanced",
) -> RelaxScreenplay:
    """Synthesize dedicated alpine nature directorial screenplay via Gemini."""
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)

    if custom_prompt and custom_prompt.strip():
        eff_prompt = custom_prompt.strip()
    else:
        unseen = [lm for lm in ALPINE_LANDMARK_POOL if not any(lm.split(',')[0].lower() in t.lower() for t in recent_topics)]
        chosen = random.choice(unseen if unseen else ALPINE_LANDMARK_POOL)
        eff_prompt = f"Majestic panoramic alpine mountain vista at {chosen}"

    sys_prompt = build_alpine_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=recent_topics,
        image_model=image_model,
        channel_id=channel_id or "earth_serenade",
        tier=tier,
    )

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    screenplay = await execute_directorial_screenplay(
        sys_prompt=sys_prompt,
        raw_output_path=raw_output_path,
        tier=tier or "balanced",
        genre="relax/nature",
        cluster="Swiss Alps, Dolomites, Rockies",
        primary_archetype="alpine_meadow",
        sub_genre="alpine_mountains",
    )

    try:
        await topic_memory.remember_topic(
            topic=screenplay.title,
            genre="relax/nature",
            tags=screenplay.publishing.seo_tags if screenplay.publishing else [],
            story_synopsis=screenplay.story_topic,
            episode_id=screenplay.production_id,
            user_id=user_id,
            channel_id=channel_id,
        )
    except Exception:
        pass

    return screenplay
