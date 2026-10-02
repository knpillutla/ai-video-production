"""Directorial Screenplay Generator for Rain Retreat & River ASMR.

Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path
from typing import Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.services.topic_memory import topic_memory
from src.studios.ambient_world.relax_models import RelaxScreenplay
from src.studios.rain_retreat.rain_prompt import (
    RAIN_BEDROOM_LANDMARK_POOL,
    RAIN_FOREST_LANDMARK_POOL,
    RAIN_LANDMARK_POOL,
    build_rain_prompt,
)


async def generate_rain_screenplay(
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    sub_genre: str = "rainy_bedroom",
    primary_archetype: Optional[str] = None,
) -> RelaxScreenplay:
    """Synthesize dedicated rain retreat directorial screenplay via Gemini."""
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)
    is_bedroom = ("bedroom" in (sub_genre or "").lower() or "cabin" in (sub_genre or "").lower() or "bedroom" in (primary_archetype or "").lower())
    pool = RAIN_BEDROOM_LANDMARK_POOL if is_bedroom else RAIN_FOREST_LANDMARK_POOL

    if custom_prompt and custom_prompt.strip():
        eff_prompt = custom_prompt.strip()
    else:
        unseen = [lm for lm in pool if not any(lm.split(',')[0].lower() in t.lower() for t in recent_topics)]
        chosen = random.choice(unseen if unseen else pool)
        if is_bedroom:
            eff_prompt = f"Cozy luxury glass cabin bedroom with warm amber lamp and rain streaming on floor-to-ceiling panoramic window overlooking misty fir forest at {chosen}"
        else:
            eff_prompt = f"Lush temperate forest river during steady gentle rain at {chosen}"

    num_shots = max(1, int(num_shots))
    prompt = build_rain_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=recent_topics,
        image_model=image_model,
        sub_genre=sub_genre,
        primary_archetype=primary_archetype,
        channel_id=channel_id,
    )

    try:
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter(strict=True)

        logger.info(f"gemini_rain_request_sent:\n--- PROMPT SENT TO GEMINI ---\n{prompt}\n-----------------------------")
        data = await llm.generate_structured(prompt)
        raw_json = json.dumps(data, indent=2, ensure_ascii=False)

        if raw_output_path:
            try:
                raw_path = Path(raw_output_path)
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                raw_path.write_text(raw_json, encoding="utf-8")
                logger.info(f"raw_gemini_screenplay_saved: {raw_path}")
            except OSError as save_error:
                logger.warning(f"failed_to_save_raw_gemini_screenplay: {save_error}")

        if data and isinstance(data, dict):
            screenplay = RelaxScreenplay.model_validate(data)
            logger.info(f"gemini_rain_screenplay_success: title='{screenplay.title}' scenes={len(screenplay.scenes)}")
            try:
                await topic_memory.remember_topic(
                    topic=screenplay.title,
                    genre="relax/rain",
                    tags=screenplay.publishing.seo_tags if screenplay.publishing else [],
                    story_synopsis=screenplay.story_topic,
                    episode_id=screenplay.production_id,
                    user_id=user_id,
                    channel_id=channel_id,
                )
            except Exception:
                pass
            return screenplay

        raise RuntimeError("Gemini returned invalid or empty rain screenplay payload")
    except Exception as ex:
        logger.error(f"gemini_rain_screenplay_fatal_error: {ex}")
        raise RuntimeError(f"Gemini Rain directorial screenplay generation failed: {ex}") from ex


__all__ = [
    "generate_rain_screenplay",
]
