"""Directorial Screenplay Generator for Forest Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.forest_studio.forest_catalog import FOREST_ARCHETYPES
from src.studios.forest_studio.forest_prompt import build_forest_prompt


class ForestScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class ForestStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/forest"
    sub_genre: str = "forest_mossy_canopy_day"
    primary_archetype: str = "forest_mossy_canopy_day"
    secondary_archetype: str = ""
    cluster: str = "forest"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[ForestScenePrompt] = Field(default_factory=list)


async def generate_forest_screenplay_gemini(
    genre: str = "relax/forest",
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
    eff_arch = primary_archetype or sub_genre or "forest_mossy_canopy_day"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    eff_prompt = custom_prompt or ""
    if weather and weather != "normal" and not any(k in eff_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset"]):
        eff_prompt = f"{eff_prompt} ({weather} atmosphere)"

    sys_prompt = build_forest_prompt(
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
        genre="relax/forest",
        cluster="forest",
        primary_archetype=eff_arch,
        sub_genre=sub_genre or eff_arch,
    )

