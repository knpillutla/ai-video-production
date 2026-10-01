"""Alpine Nature Studio Dedicated Directorial Agent.

Synthesizes master screenplays specifically tailored for panoramic mountain landscapes,
Swiss Alps, snow peaks, wildflower valleys, and glacial streams.
"""

from __future__ import annotations

import json
import os
import random
from typing import Optional

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
) -> RelaxScreenplay:
    """Synthesize dedicated alpine nature directorial screenplay via Gemini."""
    recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=20)

    if custom_prompt and custom_prompt.strip():
        eff_prompt = custom_prompt.strip()
    else:
        unseen = [lm for lm in ALPINE_LANDMARK_POOL if not any(lm.split(',')[0].lower() in t.lower() for t in recent_topics)]
        chosen = random.choice(unseen if unseen else ALPINE_LANDMARK_POOL)
        eff_prompt = f"Majestic panoramic alpine mountain vista at {chosen}"

    api_key = (
        settings.llm.gemini_api_key
        or settings.llm.google_api_key
        or os.getenv("GEMINI_API_KEY", "")
        or os.getenv("GOOGLE_API_KEY", "")
    )
    if not api_key:
        return _build_deterministic_alpine_screenplay(eff_prompt, duration_seconds, num_shots)

    sys_prompt = build_alpine_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        camera_motion=camera_motion,
        excluded_topics=recent_topics,
        image_model=image_model,
    )

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": sys_prompt}]}],
            "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7},
        }
        client = HTTPClientPool.get_client()
        response = await client.post(url, json=payload, timeout=45.0)

        if response.status_code != 200:
            logger.error(f"alpine_gemini_http_error: status={response.status_code}")
            return _build_deterministic_alpine_screenplay(eff_prompt, duration_seconds, num_shots)

        raw_json = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if raw_output_path:
            try:
                from pathlib import Path
                p = Path(raw_output_path)
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(raw_json, encoding="utf-8")
            except Exception:
                pass

        screenplay = RelaxScreenplay(**json.loads(raw_json))
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
    except Exception as exc:
        logger.error(f"alpine_gemini_failed: {exc}")
        return _build_deterministic_alpine_screenplay(eff_prompt, duration_seconds, num_shots)


def _build_deterministic_alpine_screenplay(prompt: str, duration_seconds: float, num_shots: int) -> RelaxScreenplay:
    """Deterministic alpine nature screenplay."""
    shot_dur = round(duration_seconds / max(1, num_shots), 1)
    scenes = []
    for i in range(num_shots):
        scenes.append(
            RelaxSceneDirective(
                scene_index=i + 1,
                location_hub=f"Alpine Vista {i + 1}",
                shot_type="wide_panoramic_picturesque",
                camera_rig="locked_tripod",
                color_temp_kelvin=5800,
                visual_prompt=(
                    f"A photorealistic, wide panoramic landscape view of {prompt}. Symmetrical 16:9 cinematic framing, "
                    "shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into "
                    "a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil "
                    "crystal-clear glacial stream gently flowing over river stones. Crisp balanced daylight, pristine natural wilderness, "
                    "strictly zero buildings, zero tourists, zero vehicles, zero modern structures, zero waterfall plunge curtains."
                ),
                image_model_configs={
                    "flux_1_1_pro_ultra": {
                        "model": "fal-ai/flux-pro/v1.1-ultra",
                        "prompt": (
                            f"A photorealistic, wide panoramic landscape view of {prompt}. Symmetrical 16:9 cinematic framing, "
                            "shot on a locked tripod. In the majestic background, towering snow-dusted jagged mountain peaks rise into "
                            "a crisp clear sky; in the foreground, lush green rolling alpine meadows dotted with wildflowers frame a tranquil "
                            "crystal-clear glacial stream. Crisp balanced daylight, pristine natural wilderness, strictly zero buildings, zero tourists."
                        ),
                        "aspect_ratio": "16:9",
                        "raw": True,
                    }
                },
                motion_prompt=(
                    "Living wallpaper cinemagraph style. Completely stationary locked frame, absolute zero camera movement. "
                    "Mountain peaks, cliffs, meadows, and horizon line remain 100% frozen and static. Only the crystal glacial stream "
                    "water gently flows over stones with subtle soft clouds drifting in the distant sky."
                ),
                motion_negative_prompt="camera movement, pan, tilt, zoom, moving mountains, morphing landscape, humans, vehicles, buildings",
                model_configs={
                    "wan_2_1": RelaxModelConfigDirective(
                        model="fal-ai/wan-i2v",
                        prompts=RelaxModelPromptsSpec(
                            positive_prompt="Living wallpaper cinemagraph, static camera. Mountain peaks and meadows remain frozen, gentle stream water flows smoothly, zero humans.",
                            negative_prompt="camera movement, morphing, humans",
                        ),
                        settings={"guide_scale": 5.0, "num_inference_steps": 30, "aspect_ratio": "16:9"},
                    )
                },
                domain="landscape_solid",
                duration_seconds=shot_dur,
            )
        )
    return RelaxScreenplay(
        production_id="EP-ALPINE-001",
        title=f"Majestic Alpine Peaks & Wildflower Meadows | {prompt}",
        story_topic=f"Tranquil panoramic alpine mountain sanctuary with snow-capped peaks and glacial streams at {prompt}.",
        genre="relax/nature",
        sub_genre="alpine_mountains",
        recommended_fps=24,
        aspect_ratio="16:9",
        total_duration_seconds=duration_seconds,
        cast=[],
        scenes=scenes,
    )
