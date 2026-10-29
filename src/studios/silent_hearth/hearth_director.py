"""Silent Hearth & Campfire Dedicated Directorial Agent.

Synthesizes master screenplays specifically tailored for 100% open-air beach campfires,
ocean shore stone hearths, and ASMR crackling fire by the sea.
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
from src.studios.silent_hearth.hearth_prompt import HEARTH_LANDMARK_POOL, build_hearth_prompt
from src.studios.directorial_configs import build_default_image_model_configs


async def generate_hearth_screenplay(
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
    """Synthesize dedicated silent hearth directorial screenplay via Gemini."""
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)

    if custom_prompt and custom_prompt.strip():
        eff_prompt = custom_prompt.strip()
    else:
        unseen = [lm for lm in HEARTH_LANDMARK_POOL if not any(lm.split(',')[0].lower() in t.lower() for t in recent_topics)]
        chosen = random.choice(unseen if unseen else HEARTH_LANDMARK_POOL)
        eff_prompt = f"Open-air stone campfire burning directly on pebble beach at {chosen}"

    if weather and weather != "normal" and not any(k in eff_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset"]):
        eff_prompt = f"{eff_prompt} ({weather} atmosphere)"

    sys_prompt = build_hearth_prompt(
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
            genre="relax/cozy_hearth",
            cluster="hearth",
            primary_archetype="beach_campfire_pebble_shore",
            sub_genre="cozy_hearth",
        )
        try:
            await topic_memory.remember_topic(
                topic=screenplay.title,
                genre="relax/cozy_hearth",
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
        logger.warning(f"hearth_gemini_fallback: {exc}")
        return _build_deterministic_hearth_screenplay(eff_prompt, duration_seconds, num_shots)


def _build_deterministic_hearth_screenplay(prompt: str, duration_seconds: float, num_shots: int) -> RelaxScreenplay:
    """Deterministic silent hearth screenplay."""
    shot_dur = round(duration_seconds / max(1, num_shots), 1)
    scenes = []
    for i in range(num_shots):
        scenes.append(
            RelaxSceneDirective(
                scene_index=i + 1,
                location_hub=f"Beach Campfire Vista {i + 1}",
                shot_type="wide_panoramic_picturesque",
                camera_rig="locked_tripod",
                color_temp_kelvin=3200,
                visual_prompt=(
                    f"A photorealistic, eye-level frontal view of a cozy natural stone campfire burning directly on the wet pebble sand at {prompt}. "
                    "Symmetrical 16:9 cinematic framing, shot on a locked tripod. Warm glowing wood logs crackle with rich amber embers under an open "
                    "twilight sky while gentle rhythmic ocean waves roll and surge along the shoreline. 100% open-air outdoor beach, strictly zero indoor rooms, "
                    "zero sofas, zero living room furniture, zero interior walls, zero ceilings, zero glass windows."
                ),
                image_model_configs=build_default_image_model_configs(
                    prompt=f"Cozy natural stone campfire burning directly on wet pebble beach at {prompt}, glowing amber wood logs, radiant sparks, deep twilight sky, rolling rhythmic ocean waves.",
                    landmark_name=prompt,
                ),
                motion_prompt=(
                    "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. "
                    "Pebble beach, shoreline rocks, and horizon remain 100% frozen and static. Only the hypnotic glowing wood fire "
                    "flickers and crackles in the stone pit while continuous gentle ocean waves roll in the background."
                ),
                motion_negative_prompt="camera movement, pan, tilt, zoom, moving beach, indoor room, sofas, furniture, humans",
                model_configs={
                    "wan_2_1": RelaxModelConfigDirective(
                        model="fal-ai/wan-i2v",
                        prompts=RelaxModelPromptsSpec(
                            positive_prompt="Living wallpaper cinemagraph, static camera. Realistic crackling fire flames in fire pit, gentle ocean waves rolling in background, zero humans.",
                            negative_prompt="camera movement, indoor, sofas, furniture, humans",
                        ),
                        settings={"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"},
                    )
                },
                domain="water_fluid",
                duration_seconds=shot_dur,
            )
        )
    return RelaxScreenplay(
        production_id="EP-HEARTH-001",
        title=f"Cozy Oceanfront Campfire & Twilight Waves | {prompt}",
        story_topic=f"Serene open-air beach campfire with glowing wood embers and rhythmic ocean waves at {prompt}.",
        genre="relax/cozy_hearth",
        sub_genre="coastal_campfire",
        recommended_fps=24,
        aspect_ratio="16:9",
        total_duration_seconds=duration_seconds,
        cast=[],
        scenes=scenes,
    )
