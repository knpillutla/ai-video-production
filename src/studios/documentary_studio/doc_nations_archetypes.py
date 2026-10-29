"""Specialized Archetype Directives for Nations & Countries Documentary Productions.

Orchestrates BBC/NatGeo directorial mandates across:
- Curiosity & Frontiers (doc_archetypes_curiosity)
- Civics, History & Leadership (doc_archetypes_civics)
- Travel, Tourism, Beaches, Resorts, Culture & Art (doc_archetypes_travel)
"""
from __future__ import annotations

from typing import Dict
from src.studios.documentary_studio.doc_archetypes_civics import CIVICS_ALIASES, CIVICS_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_curiosity import CURIOSITY_ALIASES, CURIOSITY_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_travel import TRAVEL_ALIASES, TRAVEL_DIRECTIVES
from src.studios.documentary_studio.doc_archetypes_food import FOOD_ALIASES, FOOD_DIRECTIVES
from src.studios.documentary_studio.doc_country_syllabus import build_country_syllabus_directive

# Combined canonical aliases mapping
NATIONS_ARCHETYPE_ALIASES: Dict[str, str] = {}
NATIONS_ARCHETYPE_ALIASES.update(CIVICS_ALIASES)
NATIONS_ARCHETYPE_ALIASES.update(CURIOSITY_ALIASES)
NATIONS_ARCHETYPE_ALIASES.update(TRAVEL_ALIASES)
NATIONS_ARCHETYPE_ALIASES.update(FOOD_ALIASES)

# Combined specialized prompt directives
ARCHETYPE_DIRECTIVES: Dict[str, str] = {}
ARCHETYPE_DIRECTIVES.update(CIVICS_DIRECTIVES)
ARCHETYPE_DIRECTIVES.update(CURIOSITY_DIRECTIVES)
ARCHETYPE_DIRECTIVES.update(TRAVEL_DIRECTIVES)
ARCHETYPE_DIRECTIVES.update(FOOD_DIRECTIVES)


def get_nations_archetype_directive(
    archetype: str,
    duration_seconds: float = 60.0,
    custom_prompt: Optional[str] = None,
) -> str:
    """Return the targeted directorial prompt snippet for a nations/countries archetype."""
    clean = (archetype or "").lower().strip()
    canonical = NATIONS_ARCHETYPE_ALIASES.get(clean)
    if not canonical:
        for alias, target in NATIONS_ARCHETYPE_ALIASES.items():
            if alias in clean or clean in alias:
                canonical = target
                break

    if canonical in ("country_dossier", "country_profile", "country", "countries", "nation", "nations"):
        return build_country_syllabus_directive(duration_seconds=duration_seconds, custom_prompt=custom_prompt)

    return ARCHETYPE_DIRECTIVES.get(canonical, "")


__all__ = [
    "NATIONS_ARCHETYPE_ALIASES",
    "ARCHETYPE_DIRECTIVES",
    "get_nations_archetype_directive",
]
