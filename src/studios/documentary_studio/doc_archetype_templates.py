"""Documentary Archetype Title Templates and Genre Mapping for Nations & Civilizations.

Aggregates specialized title templates, aliases, and genre mappings from:
- doc_templates_civics (history, engineering, leaders, music & cinema)
- doc_templates_curiosity (enigmas, heartlands, demographics & danger)
- doc_templates_travel (cities, countdowns, wellness, nature & art)
- doc_templates_food (production, regional cuisines & dining rituals)
"""
from __future__ import annotations
from src.studios.documentary_studio.doc_templates import DocGenre
from src.studios.documentary_studio.doc_templates_civics import (
    CIVICS_TEMPLATES, CIVICS_ALIASES, CIVICS_GENRE_MAP,
)
from src.studios.documentary_studio.doc_templates_curiosity import (
    CURIOSITY_TEMPLATES, CURIOSITY_ALIASES, CURIOSITY_GENRE_MAP,
)
from src.studios.documentary_studio.doc_templates_travel import (
    TRAVEL_TEMPLATES, TRAVEL_ALIASES, TRAVEL_GENRE_MAP,
)
from src.studios.documentary_studio.doc_templates_food import (
    FOOD_TEMPLATES, FOOD_ALIASES, FOOD_GENRE_MAP,
)

ARCHETYPE_TEMPLATES: dict[str, list[str]] = {}
ARCHETYPE_TEMPLATES.update(CIVICS_TEMPLATES)
ARCHETYPE_TEMPLATES.update(CURIOSITY_TEMPLATES)
ARCHETYPE_TEMPLATES.update(TRAVEL_TEMPLATES)
ARCHETYPE_TEMPLATES.update(FOOD_TEMPLATES)

_ALIASES: dict[str, str] = {}
_ALIASES.update(CIVICS_ALIASES)
_ALIASES.update(CURIOSITY_ALIASES)
_ALIASES.update(TRAVEL_ALIASES)
_ALIASES.update(FOOD_ALIASES)

for k, v in _ALIASES.items():
    if v in ARCHETYPE_TEMPLATES:
        ARCHETYPE_TEMPLATES[k] = ARCHETYPE_TEMPLATES[v]

ARCHETYPE_GENRE_MAP: dict[str, DocGenre] = {}
ARCHETYPE_GENRE_MAP.update(CIVICS_GENRE_MAP)
ARCHETYPE_GENRE_MAP.update(CURIOSITY_GENRE_MAP)
ARCHETYPE_GENRE_MAP.update(TRAVEL_GENRE_MAP)
ARCHETYPE_GENRE_MAP.update(FOOD_GENRE_MAP)

# Map alias keys to their target genre
for k, v in _ALIASES.items():
    if v in ARCHETYPE_GENRE_MAP:
        ARCHETYPE_GENRE_MAP[k] = ARCHETYPE_GENRE_MAP[v]

__all__ = ["ARCHETYPE_TEMPLATES", "ARCHETYPE_GENRE_MAP"]
