"""Directorial Screenplay Generator for Valley Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.valley_studio.valley_catalog import VALLEY_ARCHETYPES
from src.studios.valley_studio.valley_prompt import build_valley_prompt


class ValleyScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class ValleyStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/valley"
    sub_genre: str = "valley_wildflower_meadow"
    primary_archetype: str = "valley_wildflower_meadow"
    secondary_archetype: str = ""
    cluster: str = "valley"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[ValleyScenePrompt] = Field(default_factory=list)


async def generate_valley_screenplay_gemini(
    genre: str = "relax/valley",
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
) -> RelaxScreenplay:
    eff_arch = primary_archetype or sub_genre or "valley_wildflower_meadow"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    sys_prompt = build_valley_prompt(
        custom_prompt=custom_prompt or "",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        archetype=eff_arch,
        camera_motion=camera_motion,
        excluded_topics=excluded,
        channel_id=eff_channel,
    )

    try:
        from src.services.llm_service import call_gemini_pro
        raw_response = await call_gemini_pro(
            prompt="Generate the Valley Studio Master Screenplay JSON now.",
            system_instruction=sys_prompt,
            response_schema=RelaxScreenplay,
            temperature=0.7,
        )
        data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
        data = normalize_audio_tags(data)
        screenplay = RelaxScreenplay.model_validate(data)
        screenplay.genre = "relax/valley"
        screenplay.cluster = "valley"
        screenplay.primary_archetype = eff_arch

        if raw_output_path:
            p = Path(raw_output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(screenplay.model_dump_json(indent=2), encoding="utf-8")
        return screenplay
    except Exception as exc:
        logger.error(f"valley_director_gemini_fallback: {exc}")
        arch = VALLEY_ARCHETYPES.get(eff_arch, VALLEY_ARCHETYPES["valley_wildflower_meadow"])
        from src.studios.screenplay_models import RelaxAudioMasterSpec, RelaxSceneDirective, RelaxPublishingPackage
        fallback = RelaxScreenplay(
            production_id=f"VAL-{os.urandom(3).hex().upper()}",
            title=arch["title"],
            story_topic=custom_prompt or arch["visual_prompt"],
            genre="relax/valley",
            sub_genre=eff_arch,
            primary_archetype=eff_arch,
            cluster="valley",
            recommended_fps=24,
            total_duration_seconds=duration_seconds,
            audio_master=RelaxAudioMasterSpec(
                audio_mode="ambient_nature",
                suno_musical_tags=arch["audio_tags"],
                target_lufs=-21.0,
                ducking_db=-18.0,
            ),
            scenes=[
                RelaxSceneDirective(
                    scene_index=1,
                    location_hub=arch["title"],
                    shot_type="wide_panoramic_picturesque",
                    camera_rig=camera_motion,
                    visual_prompt=custom_prompt or arch["visual_prompt"],
                    motion_prompt=arch["motion_prompt"],
                    domain=arch.get("domain", "landscape_solid"),
                    duration_seconds=duration_seconds,
                )
            ],
            publishing=RelaxPublishingPackage(
                ctr_titles=[f"4K {arch['title']}", "Pastoral Valley Living Wallpaper 4K"],
                description_with_timestamps=f"Tranquil 4K Valley Relaxation: {arch['title']}",
                seo_tags=["valley", "4k", "wildflowers", "relaxation", "meadow"],
            ),
        )
        if raw_output_path:
            p = Path(raw_output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(fallback.model_dump_json(indent=2), encoding="utf-8")
        return fallback
