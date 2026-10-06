"""Directorial Screenplay Generator for Travel & Scenic Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.travel_studio.travel_catalog import TRAVEL_ARCHETYPES, get_travel_archetype
from src.studios.travel_studio.travel_prompt import build_travel_prompt


class TravelScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "wide_aerial_drone_glide"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class TravelStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "travel/scenic"
    sub_genre: str = "cities"
    primary_archetype: str = "cities"
    secondary_archetype: str = ""
    cluster: str = "travel"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[TravelScenePrompt] = Field(default_factory=list)


async def generate_travel_screenplay_gemini(
    genre: str = "travel/scenic",
    sub_genre: Optional[str] = None,
    primary_archetype: Optional[str] = None,
    custom_prompt: Optional[str] = None,
    duration_seconds: float = 60.0,
    user_id: Optional[str] = None,
    num_shots: int = 2,
    camera_motion: str = "slow_drone_forward",
    raw_output_path: Optional[os.PathLike | str] = None,
    image_model: str = "flux_1_1_pro_ultra",
    channel_id: Optional[str] = None,
    tier: str = "balanced",
) -> RelaxScreenplay:
    """Generate structured RelaxScreenplay for Travel Studio using Gemini Flash."""
    eff_arch = primary_archetype or sub_genre or "cities"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    eff_shots = max(2, round((duration_seconds or 60.0) / 12.5))
    logger.info(f"travel_director_cadence: duration={duration_seconds}s -> eff_shots={eff_shots} (ignoring incoming num_shots={num_shots})")
    sys_prompt = build_travel_prompt(
        custom_prompt=custom_prompt or "",
        duration_seconds=duration_seconds,
        num_shots=eff_shots,
        archetype=eff_arch,
        camera_motion=camera_motion,
        excluded_topics=excluded,
        channel_id=eff_channel,
        tier=tier,
    )

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    return await execute_directorial_screenplay(
        sys_prompt=sys_prompt,
        raw_output_path=raw_output_path,
        tier=tier,
        genre=genre or "travel/scenic",
        cluster="travel",
        primary_archetype=eff_arch,
        sub_genre=sub_genre or eff_arch,
    )
