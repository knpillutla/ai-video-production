"""Directorial Screenplay Generator for Desert Studio.

Conforms strictly to the global RelaxScreenplay schema contract.
Encapsulates all 6 diurnal timings: daytime, sunrise, sunset, starlight, campfire, and rain.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import (
    RelaxAudioMasterSpec,
    RelaxPublishingPackage,
    RelaxSceneDirective,
    RelaxScreenplay,
)
from src.studios.directorial_configs import build_default_image_model_configs
from src.studios.desert_studio.desert_catalog import DESERT_ARCHETYPES
from src.studios.desert_studio.desert_prompt import DESERT_LANDMARK_POOL, build_desert_prompt


class DesertScenePrompt(BaseModel):
    """Prompt definition for a Desert Studio scene."""
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class DesertStoryboard(BaseModel):
    """Complete storyboard representation for legacy compatibility."""
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/desert"
    sub_genre: str = "desert_daytime_tent"
    primary_archetype: str = "desert_daytime_tent"
    secondary_archetype: str = ""
    cluster: str = ""
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[DesertScenePrompt] = Field(default_factory=list)


def desert_screenplay_to_storyboard(sp: RelaxScreenplay) -> DesertStoryboard:
    """Convert RelaxScreenplay to DesertStoryboard contract."""
    return DesertStoryboard(
        title=sp.title,
        theme=sp.title,
        story_topic=sp.story_topic,
        genre=sp.genre or "relax/desert",
        sub_genre=sp.sub_genre or sp.primary_archetype or "desert_daytime_tent",
        primary_archetype=sp.primary_archetype or "desert_daytime_tent",
        secondary_archetype=sp.secondary_archetype or "",
        cluster=sp.cluster or "desert",
        total_duration=sp.total_duration_seconds,
        recommended_fps=sp.recommended_fps or 24,
        audio_tags=sp.audio_master.suno_musical_tags if sp.audio_master else "",
        scenes=[
            DesertScenePrompt(
                scene_index=s.scene_index,
                perspective_type=s.shot_type,
                visual_prompt=s.visual_prompt,
                motion_prompt=s.motion_prompt,
                duration_seconds=s.duration_seconds,
                domain=s.domain or "landscape_solid",
                location_hub=s.location_hub,
            )
            for s in sp.scenes
        ],
    )


async def generate_desert_screenplay_gemini(
    genre: str = "relax/desert",
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
    """Generate 8K broadcast-grade master screenplay for Desert Studio via Gemini Flash."""
    eff_arch = primary_archetype or sub_genre or "desert_daytime_tent"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    eff_prompt = custom_prompt or ""
    if weather and weather != "normal" and not any(k in eff_prompt.lower() for k in [weather, "rain", "snow", "fog", "sunset"]):
        eff_prompt = f"{eff_prompt} ({weather} atmosphere)"

    sys_prompt = build_desert_prompt(
        custom_prompt=eff_prompt,
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        archetype=eff_arch,
        camera_motion=camera_motion,
        excluded_topics=excluded,
        channel_id=eff_channel,
    )

    from src.studios.base_screenplay_engine import execute_directorial_screenplay
    screenplay = await execute_directorial_screenplay(
        sys_prompt=sys_prompt,
        raw_output_path=raw_output_path,
        tier=tier or "balanced",
        genre="relax/desert",
        cluster="desert",
        primary_archetype=eff_arch,
        sub_genre=sub_genre or eff_arch,
    )

    # Culturally aligned & diurnal-permuted 432Hz audio master
    from src.studios.desert_studio.desert_cultural_audio import generate_desert_cultural_audio_spec
    dest = (screenplay.travel_tourism.destination_name if screenplay.travel_tourism else "") or screenplay.title
    tags, arr_prompt = generate_desert_cultural_audio_spec(
        region_or_landmark=dest,
        timing_or_archetype=screenplay.primary_archetype or eff_arch,
        seed_key=screenplay.production_id or str(os.urandom(4).hex()),
    )
    if screenplay.audio_master:
        screenplay.audio_master.suno_musical_tags = tags
        screenplay.audio_master.vocal_gender = "none"
        screenplay.audio_master.target_lufs = -21.0
        screenplay.audio_master.singing_lyrics_spec = arr_prompt

    try:
        await topic_memory.remember_topic(
            topic=screenplay.story_topic or screenplay.title,
            genre=screenplay.genre or "relax/desert",
            tags=[screenplay.primary_archetype or "desert"],
            story_synopsis=screenplay.story_topic or screenplay.title,
            episode_id="",
            user_id=user_id,
            channel_id=eff_channel,
        )
    except Exception as mem_ex:
        logger.warning(f"desert_topic_memory_record_failed: {mem_ex}")
    return screenplay


def _fallback_catalog_screenplay(archetype: str, prompt: Optional[str], duration: float) -> RelaxScreenplay:
    """Deterministic fallback using DESERT_ARCHETYPES."""
    arch = DESERT_ARCHETYPES.get(archetype) or DESERT_ARCHETYPES.get("desert_daytime_tent")
    scenes = [
        RelaxSceneDirective(
            scene_index=1,
            location_hub=arch.display_name,
            shot_type="wide_panoramic_picturesque",
            visual_prompt=arch.wide_visual_prompt,
            image_model_configs=build_default_image_model_configs(prompt=arch.wide_visual_prompt, landmark_name=arch.display_name),
            motion_prompt=arch.wide_motion_prompt,
            duration_seconds=duration,
            domain=arch.default_domain,
        )
    ]
    return RelaxScreenplay(
        production_id="EP-001",
        title=f"{arch.display_name} Sanctuary",
        story_topic=arch.wide_visual_prompt[:200],
        genre="relax/desert",
        sub_genre=arch.key,
        primary_archetype=arch.key,
        cluster=arch.cluster,
        total_duration_seconds=duration,
        recommended_fps=24,
        scenes=scenes,
        audio_master=RelaxAudioMasterSpec(
            audio_mode="ambient_nature",
            suno_musical_tags=arch.acoustic_tags,
            vocal_gender="none",
            target_lufs=-21.0,
        ),
        publishing=RelaxPublishingPackage(
            ctr_titles=[f"4K {arch.display_name}", "Pure Desert Relaxation Living Wallpaper"],
            description_with_timestamps=f"Immerse into {arch.display_name}.",
            seo_tags=arch.tags,
        ),
    )
