"""Directorial Screenplay Generator for Healing Meditation & Relaxing Zen Music.

Conforms strictly to the global RelaxScreenplay schema contract.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.ambient_world.relax_models import (
    RelaxAudioMasterSpec,
    RelaxPublishingPackage,
    RelaxSceneDirective,
    RelaxScreenplay,
)
from src.studios.zen_studio.zen_prompt import ZEN_LANDMARK_POOL, build_zen_prompt


class ZenScenePrompt(BaseModel):
    """Prompt definition for a Zen Studio scene."""
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class ZenStoryboard(BaseModel):
    """Complete storyboard representation for legacy compatibility."""
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/zen"
    sub_genre: str = "zen_healing"
    primary_archetype: str = "zen_garden"
    secondary_archetype: str = ""
    cluster: str = ""
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[ZenScenePrompt] = Field(default_factory=list)


async def generate_zen_screenplay_gemini(
    genre: str = "relax/zen",
    sub_genre: str = "zen_healing",
    primary_archetype: str = "zen_garden",
    custom_prompt: str = "",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
    num_shots: int = 1,
    raw_output_path: Optional[str | Path] = None,
    image_model: str = "flux_1_1_pro_ultra",
    channel_id: Optional[str] = None,
) -> RelaxScreenplay:
    """Dynamically generate 432Hz healing meditation screenplay via Gemini LLM."""
    logger.info(f"generating_zen_screenplay: prompt='{custom_prompt}' genre='{genre}' shots={num_shots} channel={channel_id}")
    num_shots = max(1, int(num_shots))

    prompt = build_zen_prompt(
        custom_prompt=custom_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        image_model=image_model,
        sub_genre=sub_genre,
        channel_id=channel_id,
    )

    try:
        from src.providers.llm.gemini_adapter import GeminiLLMAdapter
        llm = GeminiLLMAdapter(strict=True)

        logger.info(f"gemini_zen_request_sent:\n--- PROMPT SENT TO GEMINI ---\n{prompt}\n-----------------------------")
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

        logger.info(f"gemini_zen_response_received:\n{raw_json}")

        if data and isinstance(data, dict):
            screenplay = RelaxScreenplay.model_validate(data)
            logger.info(f"gemini_zen_screenplay_success: title='{screenplay.title}' scenes={len(screenplay.scenes)}")
            return screenplay

        raise RuntimeError("Gemini returned invalid or empty screenplay payload")
    except Exception as ex:
        logger.error(f"gemini_zen_screenplay_fatal_error: {ex}")
        raise RuntimeError(f"Gemini Zen directorial screenplay generation failed: {ex}") from ex


async def generate_zen_storyboard_gemini(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
    user_id: str = "user_krishna_01",
    genre: str = "relax/zen",
    sub_genre: str = "zen_healing",
    primary_archetype: str = "zen_garden",
    num_shots: int = 1,
    raw_output_path: Optional[str | Path] = None,
) -> ZenStoryboard:
    """Legacy helper returning ZenStoryboard."""
    sp = await generate_zen_screenplay_gemini(
        genre=genre,
        sub_genre=sub_genre,
        primary_archetype=primary_archetype,
        custom_prompt=theme,
        duration_seconds=duration_seconds,
        user_id=user_id,
        num_shots=num_shots,
        raw_output_path=raw_output_path,
    )
    return ZenStoryboard(
        title=sp.title,
        theme=theme,
        story_topic=sp.story_topic,
        genre=sp.genre,
        sub_genre=sp.sub_genre or sub_genre,
        primary_archetype=sp.primary_archetype or primary_archetype,
        secondary_archetype=sp.secondary_archetype or "",
        cluster=sp.cluster or "",
        total_duration=sp.total_duration_seconds,
        recommended_fps=sp.recommended_fps,
        audio_tags=sp.audio_master.suno_musical_tags if sp.audio_master else "",
        scenes=[
            ZenScenePrompt(
                scene_index=sc.scene_index,
                perspective_type=sc.shot_type,
                visual_prompt=sc.visual_prompt,
                motion_prompt=sc.motion_prompt,
                duration_seconds=sc.duration_seconds,
                domain=sc.domain,
                location_hub=sc.location_hub,
            )
            for sc in sp.scenes
        ],
    )


def generate_zen_storyboard(
    theme: str = "Tranquil Zen Garden & Sacred Lotus Pond at Dawn",
    duration_seconds: float = 60.0,
    num_shots: int = 1,
) -> ZenStoryboard:
    """Deterministic fallback returning ZenStoryboard."""
    num_shots = max(1, int(num_shots))
    return ZenStoryboard(
        title=theme,
        theme=theme,
        story_topic="Tranquil Kyoto Zen garden sanctuary",
        total_duration=duration_seconds,
        recommended_fps=24,
        audio_tags="432Hz deep inner peace melody, Japanese bamboo shakuhachi flute, soft temple bell, -14 LUFS",
        scenes=[
            ZenScenePrompt(
                scene_index=idx + 1,
                perspective_type="wide_panoramic_picturesque",
                visual_prompt="Masterpiece 4K photograph of a sacred tranquil Japanese Zen garden at dawn with raked gravel and mossy granite stones.",
                motion_prompt="Fixed locked tripod camera, zero movement, morning mist slowly drifting across gravel ripples.",
                duration_seconds=duration_seconds / num_shots,
                domain="landscape_solid",
                location_hub="Kyoto Zen Courtyard",
            )
            for idx in range(num_shots)
        ],
    )


__all__ = [
    "ZenScenePrompt",
    "ZenStoryboard",
    "generate_zen_storyboard",
    "generate_zen_screenplay_gemini",
    "generate_zen_storyboard_gemini",
]
