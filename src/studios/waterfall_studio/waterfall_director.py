"""Waterfall Studio Dedicated Directorial Agent.

Synthesizes master screenplays specifically tailored for monumental waterfalls
and roaring cascades with brown noise audio and fluid cinemagraph dynamics.
"""

from __future__ import annotations

import json
import os
import random
from typing import Any, Optional

from src.core.config import settings
from src.core.telemetry import logger
from src.providers.base import HTTPClientPool
from src.services.topic_memory import topic_memory
from src.studios.ambient_world.relax_models import (
    RelaxModelConfigDirective,
    RelaxModelPromptsSpec,
    RelaxSceneDirective,
    RelaxScreenplay,
)
from src.studios.waterfall_studio.waterfall_prompt import WATERFALL_LANDMARK_POOL, build_waterfall_prompt
from src.studios.directorial_configs import build_default_image_model_configs


async def generate_waterfall_screenplay(
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    tier: str = "balanced",
    weather: Optional[str] = "normal",
    **kwargs: Any,
) -> RelaxScreenplay:
    """Synthesize dedicated waterfall directorial screenplay via Gemini."""
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)

    if custom_prompt and custom_prompt.strip():
        eff_prompt = custom_prompt.strip()
    else:
        unseen = [lm for lm in WATERFALL_LANDMARK_POOL if not any(lm.split(',')[0].lower() in t.lower() for t in recent_topics)]
        chosen = random.choice(unseen if unseen else WATERFALL_LANDMARK_POOL)
        eff_prompt = f"Monumental wall-to-wall cascading waterfall at {chosen}"

    if weather and weather != "normal" and not any(k in eff_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset"]):
        eff_prompt = f"{eff_prompt} ({weather} atmosphere)"

    sys_prompt = build_waterfall_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=recent_topics,
        image_model=image_model,
    )

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    try:
        screenplay = await execute_directorial_screenplay(
            sys_prompt=sys_prompt,
            raw_output_path=raw_output_path,
            tier="balanced",
            genre="relax/waterfall",
            cluster="waterfall",
            primary_archetype="waterfall_monumental_cascade",
            sub_genre="waterfall_cascade",
        )
        try:
            await topic_memory.remember_topic(
                topic=screenplay.title,
                genre="relax/waterfall",
                tags=screenplay.publishing.seo_tags if screenplay.publishing else [],
                story_synopsis=screenplay.story_topic,
                episode_id=screenplay.production_id,
                user_id=user_id,
                channel_id=channel_id,
            )
        except Exception:
            pass
        return screenplay
    except Exception as exc:
        logger.warning(f"waterfall_gemini_fallback: {exc}")
        return _build_deterministic_waterfall_screenplay(eff_prompt, duration_seconds, num_shots)


def _build_deterministic_waterfall_screenplay(prompt: str, duration_seconds: float, num_shots: int) -> RelaxScreenplay:
    """Deterministic waterfall screenplay."""
    shot_dur = round(duration_seconds / max(1, num_shots), 1)
    scenes = []
    for i in range(num_shots):
        scenes.append(
            RelaxSceneDirective(
                scene_index=i + 1,
                location_hub=f"Waterfall Vista {i + 1}",
                shot_type="wide_panoramic_picturesque",
                camera_rig="locked_tripod",
                color_temp_kelvin=5500,
                visual_prompt=(
                    f"A photorealistic, eye-level frontal view directly confronting the monumental roaring waterfall wall at {prompt}. "
                    "Symmetrical 16:9 cinematic framing, shot on a locked tripod. The powerful cascading cataract spans wall-to-wall "
                    "across the screen into a churning turquoise basin with soft rising mist under moody diffused overcast skies. "
                    "Pristine natural wilderness, strictly zero buildings, zero boats, zero tourists, zero structures."
                ),
                image_model_configs=build_default_image_model_configs(
                    prompt=f"Monumental cascading waterfall wall at {prompt}, churning turquoise basin, sun-drenched golden amber sidelight, vibrant emerald moss on dark rock cliffs, crystalline rising mist, razor-sharp textures.",
                    landmark_name=prompt,
                ),
                motion_prompt=(
                    "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. "
                    "Rock cliffs and horizon remain 100% frozen and static. Only the water moves: continuous downward flowing cataract curtains "
                    "into the churning basin below, with soft vapor mist steadily rising."
                ),
                motion_negative_prompt="camera movement, pan, tilt, zoom, moving rocks, morphing landscape, humans, boats",
                model_configs={
                    "wan_2_1": RelaxModelConfigDirective(
                        model="fal-ai/wan-i2v",
                        prompts=RelaxModelPromptsSpec(
                            positive_prompt="Living wallpaper cinemagraph, static camera. Continuous laminar water cascades flowing downward into the basin, rising mist, zero humans.",
                            negative_prompt="camera movement, morphing, humans",
                        ),
                        settings={"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"},
                    )
                },
                domain="water_fluid",
                duration_seconds=shot_dur,
            )
        )
    return RelaxScreenplay(
        production_id="EP-WATERFALL-001",
        title=f"Monumental Waterfall Plunge | {prompt}",
        story_topic=f"Direct eye-level encounter with the monumental falling water curtain at {prompt}.",
        genre="relax/waterfall",
        sub_genre="waterfall_gorge",
        recommended_fps=24,
        aspect_ratio="16:9",
        total_duration_seconds=duration_seconds,
        cast=[],
        scenes=scenes,
    )
