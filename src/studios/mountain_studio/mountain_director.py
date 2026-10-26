"""Directorial Screenplay Generator for Mountain Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.mountain_studio.mountain_catalog import MOUNTAIN_ARCHETYPES
from src.studios.mountain_studio.mountain_prompt import build_mountain_prompt


class MountainScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class MountainStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/mountain"
    sub_genre: str = "mountain_daytime_vista"
    primary_archetype: str = "mountain_daytime_vista"
    secondary_archetype: str = ""
    cluster: str = "mountain"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[MountainScenePrompt] = Field(default_factory=list)


async def generate_mountain_screenplay_gemini(
    genre: str = "relax/mountain",
    sub_genre: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    user_id: Optional[str] = None,
    num_shots: int = 1,
    camera_motion: str = "locked_tripod",
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    channel_id: Optional[str] = None,
    tier: str = "balanced",
    weather: Optional[str] = "normal",
    **kwargs: Any,
) -> RelaxScreenplay:
    eff_arch = primary_archetype or sub_genre or "mountain_daytime_vista"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    eff_prompt = custom_prompt or ""
    if weather and weather != "normal" and not any(k in eff_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset"]):
        eff_prompt = f"{eff_prompt} ({weather} atmosphere)"

    sys_prompt = build_mountain_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        archetype=eff_arch,
        camera_motion=camera_motion,
        excluded_topics=excluded,
        channel_id=eff_channel,
    )

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    return await execute_directorial_screenplay(
        sys_prompt=sys_prompt,
        raw_output_path=raw_output_path,
        tier=tier or "balanced",
        genre="relax/mountain",
        cluster="mountain",
        primary_archetype=eff_arch,
        sub_genre=sub_genre or eff_arch,
    )
