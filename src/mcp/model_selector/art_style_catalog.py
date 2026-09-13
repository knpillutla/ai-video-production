"""Global Aesthetics and Art Style Catalog Resolver for MCP Server."""

from typing import Any
from src.mcp.model_selector.art_style_definitions import ART_STYLE_INTELLIGENCE_CATALOG


def lookup_art_style(style_query: str | None = None, country: str | None = None) -> dict[str, Any]:
    """Retrieve art style intelligence, prompt anchors, lighting, and LoRA stack."""
    q = (style_query or "").lower().replace("-", "_").replace(" ", "_")
    c = (country or "").lower().strip()

    # Direct dictionary key match
    if q in ART_STYLE_INTELLIGENCE_CATALOG:
        return ART_STYLE_INTELLIGENCE_CATALOG[q]

    # Match Swiss Alpine aesthetics
    if "lauterbrunnen" in q or "swiss_rain" in q or "mürren" in q or "murren" in q or ("swiss" in q and "rain" in q):
        return ART_STYLE_INTELLIGENCE_CATALOG["swiss_alpine_rainy_village"]
    if "innsbruck" in q or "tegernsee" in q or "drive" in q or "road_trip" in q or "scenic_drive" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["alpine_rainy_scenic_drive"]
    if "swiss" in q or "grindelwald" in q or "alpine" in q or "eiger" in q or "jungfrau" in q or c in ("ch", "switzerland"):
        return ART_STYLE_INTELLIGENCE_CATALOG["swiss_alpine_scenic_8k"]

    # Match Greek / Aegean coastal aesthetics
    if "greek" in q or "aegean" in q or "cycladic" in q or "milos" in q or "santorini" in q or "sea_cave" in q or c in ("gr", "greece"):
        return ART_STYLE_INTELLIGENCE_CATALOG["greek_cycladic_coastal"]

    # Match Italian coastal & Lake Como
    if "lake_como" in q or "como" in q or "amalfi" in q or "positano" in q or "bellagio" in q or "coffee" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["italian_coastal_lake_como"]

    # Match Ibiza / Mediterranean lounge aesthetics
    if "ibiza" in q or "lounge" in q or "rooftop" in q or "cafe_del_mar" in q or "sunset_chillout" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["ibiza_luxury_sunset_lounge"]

    # Match Primeval Forest nature sanctuary
    if "forest" in q or "rainforest" in q or "jungle" in q or "nature_relaxation" in q or "stream" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["primeval_forest_sanctuary"]

    # Match Tropical Thailand Karst Wonders
    if "thailand" in q or "karst" in q or "chiang_mai" in q or "krabi" in q or "phuket" in q or c in ("th", "thailand"):
        return ART_STYLE_INTELLIGENCE_CATALOG["tropical_thailand_karst"]

    # Match artistic movements
    if "afro" in q or "wakanda" in q or "kente" in q or "ankara" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["african_afrofuturism"]
    if "ukiyo" in q or "hokusai" in q or "woodblock" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["japanese_ukiyo_e"]
    if "cyber" in q or "neon" in q or "blade_runner" in q:
        if "80" in q or "synth" in q or "retro" in q:
            return ART_STYLE_INTELLIGENCE_CATALOG["retro_80s_synthwave"]
        return ART_STYLE_INTELLIGENCE_CATALOG["cyberpunk_neo_tokyo"]
    if "impression" in q or "monet" in q or "renoir" in q or "plein_air" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["french_impressionism"]
    if "baroque" in q or "chiaroscuro" in q or "caravaggio" in q or "tenbrism" in q or "renaissance" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["italian_baroque_chiaroscuro"]
    if "kpop" in q or "k_pop" in q or "seoul" in q or "glam" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["korean_kpop_cyber_glam"]
    if "mural" in q or "rivera" in q or "kahlo" in q or "magical_realism" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["mexican_muralism_magical_realism"]
    if "nordic" in q or "noir" in q or "scandi" in q or "fjord" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["nordic_noir_minimalism"]
    if "mughal" in q or "miniature" in q or "rajasthani" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["indian_mughal_miniature"]
    if "synthwave" in q or "80s" in q or "vaporwave" in q or "outrun" in q:
        return ART_STYLE_INTELLIGENCE_CATALOG["retro_80s_synthwave"]

    # Country-based aesthetic defaults if style_query is unspecified
    if c in ("jp", "japan"):
        return ART_STYLE_INTELLIGENCE_CATALOG["japanese_ukiyo_e"]
    if c in ("kr", "korea", "south korea"):
        return ART_STYLE_INTELLIGENCE_CATALOG["korean_kpop_cyber_glam"]
    if c in ("ng", "gh", "nigeria", "ghana", "africa"):
        return ART_STYLE_INTELLIGENCE_CATALOG["african_afrofuturism"]
    if c in ("se", "no", "is", "sweden", "norway", "iceland"):
        return ART_STYLE_INTELLIGENCE_CATALOG["nordic_noir_minimalism"]
    if c in ("ch", "switzerland"):
        return ART_STYLE_INTELLIGENCE_CATALOG["swiss_alpine_scenic_8k"]
    if c in ("gr", "greece"):
        return ART_STYLE_INTELLIGENCE_CATALOG["greek_cycladic_coastal"]
    if c in ("at", "austria"):
        return ART_STYLE_INTELLIGENCE_CATALOG["alpine_rainy_scenic_drive"]
    if c in ("th", "thailand"):
        return ART_STYLE_INTELLIGENCE_CATALOG["tropical_thailand_karst"]

    return ART_STYLE_INTELLIGENCE_CATALOG["photorealistic_cinematic"]


__all__ = ["ART_STYLE_INTELLIGENCE_CATALOG", "lookup_art_style"]
