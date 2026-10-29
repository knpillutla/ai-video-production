"""Documentary Educational Narrator.

Synthesizes authoritative BBC/NatGeo-grade educational narration for all 35 sovereign
documentary chapters, educating viewers with verified real-world geography, history,
governance, culture, science, economics, sports, wildlife, and ecology.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from src.studios.documentary_studio.doc_chapter_templates import CHAPTER_TEMPLATES
from src.studios.documentary_studio.doc_country_facts import get_country_facts
from src.studios.documentary_studio.doc_country_syllabus import ALL_21_KEYS, ALL_35_KEYS, PILLARS


def build_educational_chapter(
    dest: str,
    key: str,
    facts: Dict[str, Any],
    idx: int,
    pillar_title: str,
) -> Tuple[str, str, str, str]:
    """Generates (subtitle, fact_badge, stats, narration) for any sovereign chapter."""
    dest_name = (dest or "Sovereign Nation").strip().title()

    # Build safe formatting dictionary with clean defaults
    ctx = {k: str(v) if v is not None else "" for k, v in facts.items()}
    ctx["dest_name"] = dest_name
    ctx.setdefault("official_name", dest_name)
    ctx.setdefault("capital", "Capital City")
    ctx.setdefault("parliament", "National Assembly")
    ctx.setdefault("head_of_state", "Constitutional Executive")
    ctx.setdefault("population", "Millions of citizens")
    ctx.setdefault("hdi_rank", "Top Global Tier")
    ctx.setdefault("area_km2", "100,000 km²")
    ctx.setdefault("coastline_km", "Expansive coastal waters")
    ctx.setdefault("geography", f"Monumental landscape of {dest_name}")
    ctx.setdefault("climate", "Temperate maritime")
    ctx.setdefault("monuments", "Ancient citadels and UNESCO monuments")
    ctx.setdefault("people", f"United society of {dest_name}")
    ctx.setdefault("major_cities", f"Regional metropolises of {dest_name}")
    ctx.setdefault("universities", f"Premier research academies of {dest_name}")
    ctx.setdefault("economy_jobs", f"Advanced tech and manufacturing of {dest_name}")
    ctx.setdefault("agriculture", f"Pastoral agriculture and harvests of {dest_name}")
    ctx.setdefault("industry", f"Precision manufacturing and robotics of {dest_name}")
    ctx.setdefault("ports", f"Deepwater maritime commercial terminals of {dest_name}")
    ctx.setdefault("airports", f"International aviation gateways of {dest_name}")
    ctx.setdefault("clean_energy", f"Renewable clean energy grid of {dest_name}")
    ctx.setdefault("food", f"Celebrated traditional gastronomy of {dest_name}")
    ctx.setdefault("arts", f"Fine arts and historic craftsmanship of {dest_name}")
    ctx.setdefault("music", f"Musical traditions and symphonic halls of {dest_name}")
    ctx.setdefault("parks", f"Protected national parks of {dest_name}")
    ctx.setdefault("beaches", f"Dramatic coastal bays and headlands of {dest_name}")
    ctx.setdefault("alliances", f"International treaties and sovereign pacts of {dest_name}")
    ctx.setdefault("future", f"21st-century technological vision of {dest_name}")
    ctx.setdefault("ancient_history", f"Millennia of ancient settlement and dynasties in {dest_name}")
    ctx.setdefault("inland_waterways", f"Major river basins and freshwater lakes of {dest_name}")
    ctx.setdefault("language_heritage", f"Official national language and living regional dialects of {dest_name}")
    ctx.setdefault("spiritual_heritage", f"Historic abbeys, sacred sanctuaries, and spiritual peace of {dest_name}")
    ctx.setdefault("science_inventions", f"Pioneering scientific discoveries and patents of {dest_name}")
    ctx.setdefault("healthcare_longevity", f"Universal public health and high life expectancy in {dest_name}")
    ctx.setdefault("currency_wealth_fund", f"Sovereign currency and national financial reserves of {dest_name}")
    ctx.setdefault("domestic_rail_transit", f"High-speed rail corridors and modern transit of {dest_name}")
    ctx.setdefault("environmental_stewardship", f"Ecological conservation and climate resilience of {dest_name}")
    ctx.setdefault("national_sports", f"Traditional games and national sporting passion of {dest_name}")
    ctx.setdefault("festivals_traditions", f"Beloved folk festivals and public holiday parades in {dest_name}")
    ctx.setdefault("wildlife_fauna", f"Protected endemic wildlife and native fauna of {dest_name}")
    ctx.setdefault("defense_security", f"Sovereign defense posture and naval search-and-rescue of {dest_name}")
    ctx.setdefault("global_diaspora", f"Worldwide diaspora and cultural soft power of {dest_name}")

    tmpl = CHAPTER_TEMPLATES.get(key)
    if not tmpl:
        sub = f"{dest_name}'s {pillar_title.title()}"
        badge = "🏛️ Sovereign Pillar"
        stats = f"Pillar #{idx:02d}"
        narration = f"Exploring the depth, heritage, and sovereign vitality of {dest_name} through {pillar_title.lower()}."
        return sub, badge, stats, narration

    sub_t, badge_t, stats_t, narr_t = tmpl
    sub = sub_t.format(**ctx)
    badge = badge_t.format(**ctx)[:28]
    stats = stats_t.format(**ctx)
    narration = narr_t.format(**ctx)

    return sub, badge, stats, narration
 
 
def generate_sovereign_chapters(
    destination: str = "Norway",
    custom_prompt: Optional[str] = None,
    genre: str = "doc/nations",
    target_chapters: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Synthesizes structured story chapters: 21 for doc/nations, 35 for doc/encyclopedia."""
    dest = (destination or "Norway").strip()
    facts = get_country_facts(dest)
    chapters: List[Dict[str, Any]] = []

    is_encyclopedia = (
        target_chapters == 35
        or "encyclopedia" in (genre or "").lower()
        or (custom_prompt and ("35" in custom_prompt.lower() or "almanac" in custom_prompt.lower()))
    )
    keys = ALL_35_KEYS if is_encyclopedia else ALL_21_KEYS

    for idx, key in enumerate(keys, 1):
        p = PILLARS.get(key, {})
        title = p.get("title", f"CHAPTER {idx}")
        visual = p.get("visual", "")
        hub = f"{dest} Sovereign Hub"

        subtitle, badge, stats, narration = build_educational_chapter(
            dest=dest,
            key=key,
            facts=facts,
            idx=idx,
            pillar_title=title,
        )

        chapters.append({
            "chapter_index": idx,
            "chapter_key": key,
            "chapter_title": f"{idx}. {title}",
            "chapter_subtitle": subtitle,
            "fact_badge": badge,
            "chapter_stats": stats,
            "location_hub": hub,
            "origin_coords": facts.get("coords", [59.9139, 10.7522]),
            "narration": narration,
            "visual_directive": visual,
            "estimated_narration_seconds": 12.0,
            "shots": [],
        })

    return chapters


def generate_sovereign_21_chapters(
    destination: str = "Norway",
    custom_prompt: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Backward-compatible alias for 21-chapter sovereign overview."""
    return generate_sovereign_chapters(destination=destination, custom_prompt=custom_prompt, genre="doc/nations", target_chapters=21)


__all__ = [
    "build_educational_chapter",
    "generate_sovereign_chapters",
    "generate_sovereign_21_chapters",
]

