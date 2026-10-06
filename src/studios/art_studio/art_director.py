"""Directorial Screenplay Generator for Living Art & Gallery Studio."""
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any, List, Optional
from pydantic import BaseModel, Field

from src.core.telemetry import logger
from src.services.audio_tag_service import normalize_audio_tags
from src.studios.screenplay_models import RelaxScreenplay
from src.studios.art_studio.art_catalog import ART_ARCHETYPES, get_art_archetype
from src.studios.art_studio.art_prompt import build_art_prompt


class ArtScenePrompt(BaseModel):
    scene_index: int
    perspective_type: str = "medium_canvas_picture_frame"
    visual_prompt: str
    motion_prompt: str
    duration_seconds: float = 30.0
    domain: str = "landscape_solid"
    location_hub: str = ""


class ArtStoryboard(BaseModel):
    title: str
    theme: str
    story_topic: str = ""
    genre: str = "relax/art"
    sub_genre: str = "living_impressionism"
    primary_archetype: str = "living_impressionism"
    secondary_archetype: str = ""
    cluster: str = "art"
    total_duration: float = 60.0
    recommended_fps: int = 24
    audio_tags: Any = ""
    scenes: List[ArtScenePrompt] = Field(default_factory=list)


async def generate_art_screenplay_gemini(
    genre: str = "relax/art",
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
    """Generate structured RelaxScreenplay for Living Art Studio using Gemini Flash."""
    eff_arch = primary_archetype or sub_genre or "living_impressionism"
    eff_channel = channel_id or "earth_serenade"

    from src.services.topic_memory import topic_memory
    raw_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=eff_channel, limit=20)
    excluded = [t if isinstance(t, str) else t.get("title", "") for t in raw_topics]

    sys_prompt = build_art_prompt(
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
        logger.info(f"gemini_art_director_request: archetype='{eff_arch}'")
        resp = await client.post(url, json=payload, timeout=45.0)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error (HTTP {resp.status_code}): {resp.text[:500]}")
        data = resp.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("Gemini returned no candidates")
        raw_json = candidates[0]["content"]["parts"][0]["text"].strip()

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
        screenplay.genre = "relax/art"
        screenplay.cluster = "art"
        screenplay.primary_archetype = eff_arch
        return screenplay
    except Exception as exc:
        logger.warning(f"gemini_art_director_fallback: {exc}")
        # Deterministic offline fallback using archetype catalog
        arch_data = get_art_archetype(eff_arch)
        shot_dur = duration_seconds / max(1, num_shots)
        scenes = [
            {
                "scene_index": i + 1,
                "perspective_type": "medium_canvas_picture_frame",
                "visual_prompt": f"{arch_data['visual_prompt']} Scene {i+1}.",
                "motion_prompt": arch_data["motion_prompt"],
                "duration_seconds": shot_dur,
                "domain": arch_data["domain"],
                "location_hub": eff_arch,
            }
            for i in range(num_shots)
        ]
        fb_dict = {
            "title": f"4K Living Art: {arch_data['title']}",
            "theme": arch_data["title"],
            "story_topic": custom_prompt or arch_data["title"],
            "genre": "relax/art",
            "sub_genre": eff_arch,
            "primary_archetype": eff_arch,
            "secondary_archetype": "",
            "cluster": "art",
            "total_duration": duration_seconds,
            "recommended_fps": 24,
            "audio_tags": arch_data["audio_tags"],
            "scenes": scenes,
            "_source": "fallback",
        }
        if raw_output_path:
            try:
                raw_p = Path(raw_output_path)
                raw_p.parent.mkdir(parents=True, exist_ok=True)
                raw_p.write_text(json.dumps(fb_dict, indent=2), encoding="utf-8")
                logger.info(f"raw_gemini_screenplay_fallback_saved: {raw_p}")
            except Exception as raw_save_err:
                logger.warning(f"failed_to_save_raw_gemini_fallback_json: {raw_save_err}")
        return RelaxScreenplay.model_validate(fb_dict)
