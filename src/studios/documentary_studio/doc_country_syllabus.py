"""Authoritative 360° Country Profile & Almanac Master Syllabus.

Defines the 35 Master Sovereign Almanac Pillars, duration-aware chapter scaling,
and strict visual grounding matrices for country documentary productions.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.studios.documentary_studio.doc_syllabus_catalog import (
    ALMANAC_35_KEYS,
    BROADCAST_21_KEYS,
    CORE_10_KEYS,
    PILLARS_ALMANAC,
)

# Backwards-compatibility aliases
PILLARS: Dict[str, Dict[str, str]] = PILLARS_ALMANAC
ALL_21_KEYS: List[str] = BROADCAST_21_KEYS
ALL_35_KEYS: List[str] = ALMANAC_35_KEYS

PRINCIPAL_15_KEYS: List[str] = [
    "identity", "capital_governance", "geography_topography", "climate_seasons",
    "people_society", "major_cities", "education_universities", "jobs_livelihood",
    "agriculture_harvest", "industry_manufacturing", "clean_energy",
    "trade_ports", "airports_aviation", "national_parks", "conclusion_future"
]


def build_country_syllabus_directive(
    duration_seconds: float = 60.0,
    custom_prompt: Optional[str] = None,
    force_all_21: bool = False,
    force_all_35: bool = False,
) -> str:
    """Builds the 360° Country Profile Chapter Syllabus covering Core, Broadcast (21) or Almanac (35)."""
    prompt_lower = (custom_prompt or "").lower()
    is_almanac = (
        force_all_35
        or "35" in prompt_lower
        or "almanac" in prompt_lower
        or "exhaustive" in prompt_lower
        or (duration_seconds is not None and duration_seconds > 1800.0)
    )

    if is_almanac:
        keys = list(ALMANAC_35_KEYS)
        cadence_label = "DEFINITIVE SOVEREIGN ALMANAC (ALL 35 CHAPTERS - 5 THEMATIC ACTS)"
    elif force_all_21 or duration_seconds is None or duration_seconds <= 0 or duration_seconds == -1:
        keys = list(BROADCAST_21_KEYS)
        cadence_label = "COMPLETE MASTER DOSSIER (ALL 21 CHAPTERS - UNABRIDGED FULL STORY)"
    elif duration_seconds <= 300.0:
        keys = list(CORE_10_KEYS)
        cadence_label = "SHORT MASTER DOSSIER (10 CORE CHAPTERS)"
    elif duration_seconds <= 900.0:
        keys = list(PRINCIPAL_15_KEYS)
        cadence_label = "STANDARD EXTENDED DOSSIER (15 PRINCIPAL CHAPTERS)"
    else:
        keys = list(BROADCAST_21_KEYS)
        cadence_label = "25-MINUTE BROADCAST MASTER DOSSIER (21 COMPLETE CHAPTERS)"

    # Prioritize user-specified focus areas (filter common stop words)
    stop_words = {"and", "the", "in", "of", "to", "for", "a", "an", "soul", "dossier", "complete", "country", "national"}
    priority_keys = []
    for k, p in PILLARS.items():
        meaningful_words = [w for w in p["title"].lower().split() if w not in stop_words and len(w) > 3]
        if k in prompt_lower or any(word in prompt_lower for word in meaningful_words):
            if k not in keys:
                keys.insert(-1, k)
            priority_keys.append(k)

    lines = [
        f"--- 360° COUNTRY PROFILE MASTER SYLLABUS ({cadence_label}) ---",
        "STRICTLY FORBIDDEN: Showing out-of-bounds imagery (e.g. mountains during education or trade).",
        "MANDATORY CHAPTER SEQUENCE & VISUAL GROUNDING MATRIX:",
    ]

    for idx, k in enumerate(keys, 1):
        p = PILLARS[k]
        prio_tag = " [★ USER PRIORITY FOCUS]" if k in priority_keys else ""
        lines.append(f"{idx}. {p['title']}{prio_tag}:")
        lines.append(f"   - Narration: {p['focus']}")
        lines.append(f"   - Mandatory Visual: {p['visual']} (Banned: {p['banned']}) [Badge: \"{p['badge']}\"]")

    lines.append("")
    lines.append("HIERARCHICAL MULTI-SHOT CHAPTER EXPANSION (FOR EACH CHAPTER):")
    lines.append("- Shot 1: Wide 4K aerial drone vista establishing chapter's specific subject.")
    lines.append("- Shot 2: Living 5s kinetic perspective inside that subject (e.g. students walking, cranes moving, jet taxiing).")
    lines.append("- Shot 3: Intimate 85mm optical bokeh or macro architectural detail of that specific subject.")
    lines.append("- All 3 sub-shots MUST depict chapter subject. NEVER insert unrelated river rapids or empty mountains!")

    return "\n".join(lines)
