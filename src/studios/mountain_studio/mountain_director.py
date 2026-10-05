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
) -> RelaxScreenplay:
    eff_arch = primary_archetype or sub_genre or "mountain_daytime_vista"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    sys_prompt = build_mountain_prompt(
        custom_prompt=custom_prompt or "",
        duration_seconds=duration_seconds,
        num_shots=num_shots,
        archetype=eff_arch,
        camera_motion=camera_motion,
        excluded_topics=excluded,
        channel_id=eff_channel,
    )

    try:
        from src.core.config import settings
        from src.providers.base import HTTPClientPool
        api_key = settings.llm.google_api_key or settings.llm.gemini_api_key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
        payload = {
            "contents": [{"parts": [{"text": sys_prompt}]}],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.7,
            },
        }
        client = HTTPClientPool.get_client()
        logger.info(f"gemini_mountain_director_request: archetype='{eff_arch}'")
        resp = await client.post(url, json=payload, timeout=45.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error (HTTP {resp.status_code}): {resp.text[:500]}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")
        raw_json = candidates[0]["content"]["parts"][0]["text"].strip()

        # Save raw Gemini response JSON for permanent reference
        if raw_output_path:
            try:
                raw_p = Path(raw_output_path)
                raw_p.parent.mkdir(parents=True, exist_ok=True)
                raw_p.write_text(raw_json, encoding="utf-8")
                logger.info(f"raw_gemini_screenplay_saved: {raw_p}")
            except Exception as raw_save_err:
                logger.warning(f"failed_to_save_raw_gemini_json: {raw_save_err}")

        parsed = json.loads(raw_json)
        screenplay = RelaxScreenplay.model_validate(parsed)
        screenplay.genre = "relax/mountain"
        screenplay.cluster = "mountain"
        screenplay.primary_archetype = eff_arch
        return screenplay
    except Exception as exc:
        logger.error(f"gemini_mountain_director_failed: {exc}")
        raise RuntimeError(f"Gemini mountain director screenplay generation failed: {exc}") from exc
