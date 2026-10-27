"""Autonomous Geographic Rotation Director for Nations & Civilizations.

Supports country-by-country ('countries') and city-by-city ('cities') exploration
across 6 continental subgenres with persistent cache deduplication and exclusion.
"""

from __future__ import annotations

import random
from typing import Optional, Tuple

from src.core.telemetry import logger
from src.services.topic_memory import topic_memory
from src.studios.documentary_studio.doc_templates import DocGenre
from src.studios.documentary_studio.doc_geo_pools import (
    CONTINENT_COUNTRIES_MAP,
    CONTINENT_CITIES_MAP,
    ARCHETYPE_TEMPLATES,
    ARCHETYPE_GENRE_MAP,
)
from src.studios.documentary_studio.doc_geo_cache import (
    get_visited_entities,
    record_visited_entity,
    select_next_unvisited_entity,
)


def is_geo_continent_subgenre(sub_genre: str) -> bool:
    """Check if subgenre belongs to continent country or city rotation."""
    clean = (sub_genre or "").lower().strip()
    return (
        clean in CONTINENT_COUNTRIES_MAP
        or clean in CONTINENT_CITIES_MAP
        or "nations" in clean
    )


def resolve_autonomous_geo_details(
    sub_genre: str,
    archetype: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> Tuple[DocGenre, str, str, str]:
    """Autonomously resolve unvisited country/city, matching theme, DocGenre, and entity name.

    Returns (DocGenre, effective_archetype, theme_title, selected_entity).
    """
    sub_clean = (sub_genre or "").lower().strip()
    arch_clean = (archetype or "").lower().strip()

    # Determine whether city-by-city or country-by-country exploration
    is_city_mode = arch_clean in ("cities", "city")
    category = "cities" if is_city_mode else "countries"
    eff_arch = "cities" if is_city_mode else ("countries" if arch_clean in ("nations", "nation", "countries", "country") else arch_clean)

    # Resolve continent pool
    if is_city_mode:
        pool = CONTINENT_CITIES_MAP.get(sub_clean, CONTINENT_CITIES_MAP["europe_nations"])
    else:
        pool = CONTINENT_COUNTRIES_MAP.get(sub_clean, CONTINENT_COUNTRIES_MAP["europe_nations"])

    # Disregard generic subgenre labels passed as custom prompts
    clean_cp = (custom_prompt or "").strip()
    clean_cp_low = clean_cp.lower()
    is_generic_label = (
        clean_cp_low in (sub_clean, "standalone", "none", "documentary", "doc/nations", "nations")
        or "nations of" in clean_cp_low
        or clean_cp_low.endswith("_nations")
    )

    # If the user explicitly typed a genuine custom prompt, honor it directly
    if clean_cp and not is_generic_label:
        eff_genre = ARCHETYPE_GENRE_MAP.get(eff_arch, DocGenre.PLACES)
        matched_entity = None
        for cand in pool:
            if cand.lower() in clean_cp.lower():
                matched_entity = cand
                record_visited_entity(cand, category, sub_clean, user_id, channel_id)
                break
        selected_entity = matched_entity or clean_cp.split(":")[0].strip()[:32]
        if clean_cp.strip().lower() == selected_entity.strip().lower():
            candidates = ARCHETYPE_TEMPLATES.get(eff_arch, ARCHETYPE_TEMPLATES.get(category, [
                "{entity}: Complete Documentary - Attractions, Nature, History, Luminaries, Inventions & Trade"
            ]))
            theme_title = candidates[0].format(entity=selected_entity)
        else:
            theme_title = clean_cp
        return eff_genre, eff_arch, theme_title, selected_entity

    # Retrieve recent topics for cross-system deduplication
    recent_topics = []
    try:
        recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=60)
    except Exception as ex:
        logger.warning(f"geo_rotation_history_lookup_failed: {ex}")

    # Select the next unvisited entity from the continent pool
    selected_entity, is_recycled = select_next_unvisited_entity(
        pool=pool,
        sub_genre=sub_clean,
        category=category,
        user_id=user_id,
        channel_id=channel_id,
        recent_topics=recent_topics,
    )

    # Immediately persist picked entity in cache so it is excluded next time
    record_visited_entity(
        entity=selected_entity,
        category=category,
        sub_genre=sub_clean,
        user_id=user_id,
        channel_id=channel_id,
    )

    # Build theme title matching archetype templates or 4-pillar exploration
    if eff_arch in ("cities", "city"):
        if is_recycled:
            theme_title = f"{selected_entity}: Hidden Gems, Great Minds, Historic Squares & Cultural Quarters"
        else:
            candidates = ARCHETYPE_TEMPLATES.get("cities", [
                "{entity}: Famous Attractions, Living Spirit, Luminaries & Historic Squares"
            ])
            theme_title = candidates[0].format(entity=selected_entity)
    elif eff_arch in ("countries", "country", "nations", "nation"):
        if is_recycled:
            theme_title = f"{selected_entity}: Hidden Frontiers, National Spirit, Great Luminaries & Gathering Piazzas"
        else:
            candidates = ARCHETYPE_TEMPLATES.get("nations", [
                "{entity}: Iconic Wonders, Great Minds, Living Heritage & Historic Squares"
            ])
            theme_title = candidates[0].format(entity=selected_entity)
    elif eff_arch in ARCHETYPE_TEMPLATES:
        # Backwards compatibility for specific thematic sub-lenses
        candidates = ARCHETYPE_TEMPLATES[eff_arch]
        tmpl = candidates[0]
        theme_title = tmpl.format(entity=selected_entity, country=selected_entity)
    else:
        theme_title = f"{selected_entity}: Famous Attractions, Living Spirit, Luminaries & Historic Squares"

    eff_genre = ARCHETYPE_GENRE_MAP.get(eff_arch, DocGenre.PLACES)
    logger.info(
        f"autonomous_geo_rotation: sub='{sub_clean}' category='{category}' "
        f"archetype='{eff_arch}' entity='{selected_entity}' recycled={is_recycled} "
        f"theme='{theme_title}' genre={eff_genre.value}"
    )
    return eff_genre, eff_arch, theme_title, selected_entity


def resolve_autonomous_geo_theme(
    sub_genre: str,
    archetype: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> Tuple[DocGenre, str, str]:
    """Compatibility wrapper returning (DocGenre, effective_archetype, theme_title)."""
    eff_genre, eff_arch, theme_title, _ = resolve_autonomous_geo_details(
        sub_genre=sub_genre,
        archetype=archetype,
        user_id=user_id,
        channel_id=channel_id,
        custom_prompt=custom_prompt,
    )
    return eff_genre, eff_arch, theme_title


def resolve_autonomous_geo_entity(
    sub_genre: str,
    archetype: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> str:
    """Resolve the specific city or country name (e.g. 'Rome' or 'Poland')."""
    _, _, _, entity = resolve_autonomous_geo_details(
        sub_genre=sub_genre,
        archetype=archetype,
        user_id=user_id,
        channel_id=channel_id,
        custom_prompt=custom_prompt,
    )
    return entity


__all__ = [
    "CONTINENT_COUNTRIES_MAP",
    "CONTINENT_CITIES_MAP",
    "ARCHETYPE_TEMPLATES",
    "ARCHETYPE_GENRE_MAP",
    "is_geo_continent_subgenre",
    "resolve_autonomous_geo_details",
    "resolve_autonomous_geo_theme",
    "resolve_autonomous_geo_entity",
]
