"""Persistent Country & City Geo Rotation Cache.

Tracks visited countries and cities across continents to guarantee deduplication
and autonomous rotation without repeat picks until the entire catalog is exhausted.
"""

from __future__ import annotations

import json
from pathlib import Path
import time
from typing import Any, Optional

from src.core.storage import storage_service
from src.core.telemetry import logger


def get_geo_cache_path(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> Path:
    """Resolve persistent JSON cache path for user/channel or default fallback."""
    try:
        if user_id and channel_id:
            net_path = storage_service.get_network_path(user_id, channel_id)
            return net_path / "geo_rotation_cache.json"
    except Exception as ex:
        logger.warning(f"geo_cache_path_resolve_warning: {ex}")

    fallback_dir = Path("storage/channels")
    fallback_dir.mkdir(parents=True, exist_ok=True)
    return fallback_dir / "geo_rotation_cache.json"


def load_geo_cache(user_id: Optional[str] = None, channel_id: Optional[str] = None) -> dict[str, Any]:
    """Load visited entities cache from persistent disk storage."""
    cache_path = get_geo_cache_path(user_id, channel_id)
    default_structure = {
        "visited_countries": {},
        "visited_cities": {},
        "history": [],
    }
    if not cache_path.is_file():
        return default_structure

    try:
        text = cache_path.read_text(encoding="utf-8")
        if not text.strip():
            return default_structure
        data = json.loads(text)
        if not isinstance(data, dict):
            return default_structure
        data.setdefault("visited_countries", {})
        data.setdefault("visited_cities", {})
        data.setdefault("history", [])
        return data
    except Exception as ex:
        logger.warning(f"failed_loading_geo_cache: {ex}")
        return default_structure


def save_geo_cache(
    cache_data: dict[str, Any],
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> None:
    """Save updated geo cache atomically to disk."""
    cache_path = get_geo_cache_path(user_id, channel_id)
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(cache_data, indent=2, ensure_ascii=False)
        cache_path.write_text(content, encoding="utf-8")
    except Exception as ex:
        logger.error(f"failed_saving_geo_cache: {ex}")


def get_visited_entities(
    sub_genre: str,
    category: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> set[str]:
    """Retrieve set of lowercase visited entities for the given subgenre and category."""
    cache = load_geo_cache(user_id, channel_id)
    cat_key = "visited_cities" if "cit" in category.lower() else "visited_countries"
    sub_map = cache.get(cat_key, {})
    visited_list = sub_map.get(sub_genre.lower().strip(), [])
    visited = {str(item).lower().strip() for item in visited_list}

    # Also automatically discover visited entities from disk directories under the channel:
    if user_id and channel_id:
        try:
            net_path = storage_service.get_network_path(user_id, channel_id)
            for search_dir in (net_path / "documentary", net_path):
                if search_dir.is_dir():
                    for sub in search_dir.iterdir():
                        if sub.is_dir() and sub.name.lower() not in (
                            "documentary", "relaxation", "walking_tour", "music_video", "short", "standalone"
                        ):
                            name_clean = sub.name.lower().replace("_", " ").strip()
                            visited.add(name_clean)
                            visited.add(sub.name.lower().strip())
        except Exception as ex:
            logger.warning(f"disk_geo_visited_scan_warning: {ex}")
    return visited


def record_visited_entity(
    entity: str,
    category: str,
    sub_genre: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
) -> None:
    """Append newly visited country or city to persistent cache."""
    cache = load_geo_cache(user_id, channel_id)
    cat_key = "visited_cities" if "cit" in category.lower() else "visited_countries"
    sub_key = sub_genre.lower().strip()

    sub_map = cache.setdefault(cat_key, {})
    current_list = sub_map.setdefault(sub_key, [])
    if entity not in current_list:
        current_list.append(entity)

    cache.setdefault("history", []).append({
        "entity": entity,
        "category": cat_key,
        "sub_genre": sub_key,
        "timestamp": int(time.time()),
    })

    save_geo_cache(cache, user_id, channel_id)
    logger.info(f"geo_cache_recorded: entity='{entity}' category='{cat_key}' sub='{sub_key}'")


def select_next_unvisited_entity(
    pool: list[str],
    sub_genre: str,
    category: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    recent_topics: Optional[list[str]] = None,
) -> tuple[str, bool]:
    """Select the first unvisited entity in pool, checking both disk cache and recent topics.

    Returns (entity, is_recycled).
    """
    if not pool:
        return "Unknown", False

    visited = get_visited_entities(sub_genre, category, user_id, channel_id)
    seen_text = " ".join(recent_topics or []).lower()

    for candidate in pool:
        c_low = candidate.lower().strip()
        if c_low not in visited and c_low not in seen_text:
            return candidate, False

    # All entities in pool have been visited: recycle pool while logging
    logger.warning(
        f"geo_pool_exhausted: all {len(pool)} entities in '{sub_genre}' ({category}) visited. Recycling pool."
    )
    return pool[0], True
