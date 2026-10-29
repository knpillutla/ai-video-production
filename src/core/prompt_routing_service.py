"""Prompt Routing Service.

Provides an extensible, configuration-driven routing engine that resolves
(format, genre, subgenre, archetype, stage) tuples to dedicated prompt blueprint files
for both Story Generation (Stage 1) and Screenplay/Directorial Generation (Stage 3)
directly from the unified format taxonomy catalog.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parent.parent.parent
_TAXONOMY_PATH = _ROOT / "src" / "core" / "config" / "format_taxonomy.json"

_TAXONOMY_CACHE: Optional[Dict[str, Any]] = None
_PROMPT_FILE_CACHE: Dict[str, str] = {}

ARCHETYPE_ALIASES: Dict[str, str] = {
    "country_dossier": "country_overview",
    "countries": "country_overview",
    "nation_overview": "country_overview",
    "country_almanac": "country_encyclopedia",
    "national_encyclopedia": "country_encyclopedia",
    "ancient_civilizations_history": "civilizational_origins",
    "itinerary_map_tour": "tour_itinerary",
    "travel_itinerary": "tour_itinerary",
    "top_places": "top_places_to_visit",
    "bucket_list": "top_places_to_visit",
    "top_cities": "top_10_cities",
}


def _load_taxonomy() -> Dict[str, Any]:
    global _TAXONOMY_CACHE
    if _TAXONOMY_CACHE is not None:
        return _TAXONOMY_CACHE
    if not _TAXONOMY_PATH.exists():
        _TAXONOMY_CACHE = {}
        return _TAXONOMY_CACHE
    try:
        with open(_TAXONOMY_PATH, "r", encoding="utf-8") as f:
            _TAXONOMY_CACHE = json.load(f)
    except Exception:
        _TAXONOMY_CACHE = {}
    return _TAXONOMY_CACHE


def _normalize(val: Optional[str]) -> str:
    return (val or "").strip().lower()


def resolve_prompt_file(
    format_name: str,
    genre_name: Optional[str] = None,
    subgenre_name: Optional[str] = None,
    archetype_name: Optional[str] = None,
    stage: str = "story",
) -> Path:
    """Resolves the best-matching prompt blueprint Path for the given hierarchy and stage."""
    tax = _load_taxonomy()

    fmt = _normalize(format_name) or "documentary"
    genre = _normalize(genre_name)
    sub = _normalize(subgenre_name)
    raw_arch = _normalize(archetype_name)
    arch = ARCHETYPE_ALIASES.get(raw_arch, raw_arch)
    stg = _normalize(stage) or "story"
    stage_key = f"{stg}_prompt_file"

    format_obj = tax.get(fmt) or tax.get("documentary", {})
    genres_list = format_obj.get("genres", [])

    # Step 1: Scan matching genre (or all genres in format)
    for g in genres_list:
        g_id = _normalize(g.get("id"))
        if genre and g_id != genre:
            continue
        for s in g.get("subgenres", []):
            s_id = _normalize(s.get("id"))
            if sub and s_id != sub:
                continue
            for a in s.get("archetypes", []):
                a_id = _normalize(a.get("id"))
                if a_id == arch or a_id == raw_arch:
                    rel = a.get(stage_key) or a.get("story_prompt_file") or a.get("prompt_file")
                    if rel:
                        return _ROOT / rel

    # Step 2: Fallback across any subgenre in matching genre
    for g in genres_list:
        g_id = _normalize(g.get("id"))
        if genre and g_id != genre:
            continue
        for s in g.get("subgenres", []):
            for a in s.get("archetypes", []):
                a_id = _normalize(a.get("id"))
                if a_id == arch or a_id == raw_arch:
                    rel = a.get(stage_key) or a.get("story_prompt_file") or a.get("prompt_file")
                    if rel:
                        return _ROOT / rel

    # Step 3: Format-level fallback
    if fmt == "documentary":
        if stg == "screenplay":
            return _ROOT / "prompts" / "documentary" / "nations" / "country_overview.screenplay.prompt.md"
        return _ROOT / "prompts" / "documentary" / "nations" / "country_overview.prompt.md"
    elif fmt == "relaxation":
        return _ROOT / "prompts" / "relaxation" / "nature" / "alpine_peaks_meadow.prompt.md"
    elif fmt == "walking_tour":
        return _ROOT / "prompts" / "walking_tour" / "rain_city_walk.prompt.md"
    elif fmt == "music_video":
        return _ROOT / "prompts" / "music_video" / "village_jathara_square.prompt.md"

    return _ROOT / "prompts" / "documentary" / "nations" / "country_overview.prompt.md"


def get_prompt_blueprint(
    format_name: str,
    genre_name: Optional[str] = None,
    subgenre_name: Optional[str] = None,
    archetype_name: Optional[str] = None,
    stage: str = "story",
) -> str:
    """Reads and returns the composed prompt blueprint text (base prompt + archetype prompt) for the given stage."""
    path = resolve_prompt_file(format_name, genre_name, subgenre_name, archetype_name, stage=stage)
    path_key = f"{path}:{stage}"

    if path_key in _PROMPT_FILE_CACHE:
        return _PROMPT_FILE_CACHE[path_key]

    content = ""
    if path.exists():
        try:
            content = path.read_text(encoding="utf-8")
        except Exception:
            pass

    if not content:
        content = f"# Default {stage.title()} Blueprint for {format_name} / {archetype_name}\nDirect standard scenes."

    # Compose with format-level base prompt if available (e.g. base_documentary_story.prompt.md)
    fmt = _normalize(format_name) or "documentary"
    stg = _normalize(stage) or "story"
    base_file = _ROOT / "prompts" / fmt / f"base_{fmt}_{stg}.prompt.md"
    if base_file.exists() and base_file.resolve() != path.resolve():
        try:
            base_content = base_file.read_text(encoding="utf-8")
            content = f"{base_content}\n\n---\n\n{content}"
        except Exception:
            pass

    _PROMPT_FILE_CACHE[path_key] = content
    return content
