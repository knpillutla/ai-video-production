"""Persistent, idempotent script artifacts for musical dance productions."""

from pathlib import Path
from typing import Any

from src.core.storage import storage_service


async def save_dance_script(
    episode_dir: Path,
    language: str,
    storyboard: dict[str, Any],
    fallback_title_en: str,
) -> Path:
    """Save Gemini's lyrics and choreography as a language-specific reusable artifact."""
    path = episode_dir / "scripts" / f"dance_script_{language.lower()}.json"
    if path.is_file() and path.stat().st_size > 0:
        return path

    dance_scenes = [
        {
            key: scene.get(key)
            for key in ("scene_index", "location_hub", "choreography_phase", "choreography_steps", "dialogue")
        }
        for scene in storyboard.get("scenes", [])
        if isinstance(scene, dict)
    ]
    await storage_service.save_json(path, {
        "title_en": storyboard.get("title_en") or fallback_title_en,
        "title_localized": storyboard.get("title_localized") or fallback_title_en,
        "language": language,
        "hook_thesis": storyboard.get("hook_thesis", ""),
        "lyrics": storyboard.get("lyrics", ""),
        "suno_tags": storyboard.get("suno_tags", ""),
        "vocal_gender": storyboard.get("vocal_gender", "female"),
        "choreography": dance_scenes,
    })
    return path


__all__ = ["save_dance_script"]
