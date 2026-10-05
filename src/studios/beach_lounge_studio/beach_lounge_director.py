"""Directorial Screenplay Generator for Beach Lounge Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.beach_lounge_studio.beach_lounge_catalog import BEACH_LOUNGE_ARCHETYPES
from src.studios.beach_lounge_studio.beach_lounge_prompt import build_beach_lounge_prompt


class BeachLoungeScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "wide_panoramic_picturesque"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "water_fluid"
    location_hub: str = ""


class BeachLoungeStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/beach_lounge"
    sub_genre: str = "beach_luxury_cabana_day"
    primary_archetype: str = "beach_luxury_cabana_day"
    secondary_archetype: str = ""
    cluster: str = "beach_lounge"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[BeachLoungeScenePrompt] = Field(default_factory=list)


async def generate_beach_lounge_screenplay_gemini(
    genre: str = "relax/beach_lounge",
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
    eff_arch = primary_archetype or sub_genre or "beach_luxury_cabana_day"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    sys_prompt = build_beach_lounge_prompt(
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
            prompt="Generate the Beach Lounge Studio Master Screenplay JSON now.",
            system_instruction=sys_prompt,
            response_schema=RelaxScreenplay,
            temperature=0.7,
        )
        data = json.loads(raw_response) if isinstance(raw_response, str) else raw_response
        data = normalize_audio_tags(data)
        screenplay = RelaxScreenplay.model_validate(data)
        screenplay.genre = "relax/beach_lounge"
        screenplay.cluster = "beach_lounge"
        screenplay.primary_archetype = eff_arch

        if raw_output_path:
            p = Path(raw_output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(screenplay.model_dump_json(indent=2), encoding="utf-8")
        return screenplay
    except Exception as exc:
        logger.error(f"beach_lounge_director_gemini_fallback: {exc}")
        arch = BEACH_LOUNGE_ARCHETYPES.get(eff_arch, BEACH_LOUNGE_ARCHETYPES["beach_luxury_cabana_day"])
        from src.studios.screenplay_models import RelaxAudioMasterSpec, RelaxSceneDirective, RelaxPublishingPackage
        fallback = RelaxScreenplay(
            production_id=f"BCH-{os.urandom(3).hex().upper()}",
            title=arch["title"],
            story_topic=custom_prompt or arch["visual_prompt"],
            genre="relax/beach_lounge",
            sub_genre=eff_arch,
            primary_archetype=eff_arch,
            cluster="beach_lounge",
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
                    domain=arch.get("domain", "water_fluid"),
                    duration_seconds=duration_seconds,
                )
            ],
            publishing=RelaxPublishingPackage(
                ctr_titles=[f"4K {arch['title']}", "Luxury Beach Lounge Living Wallpaper 4K"],
                description_with_timestamps=f"Tranquil 4K Beach Lounge Relaxation: {arch['title']}",
                seo_tags=["beach_lounge", "4k", "cabana", "ocean", "relaxation", "432hz"],
            ),
        )
        if raw_output_path:
            p = Path(raw_output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(fallback.model_dump_json(indent=2), encoding="utf-8")
        return fallback
