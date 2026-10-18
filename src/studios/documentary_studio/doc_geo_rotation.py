"""Autonomous Geographic & Continent Deduplication Director.

Provides continent-based country rotation and 20 thematic lenses (history, cities,
architecture, nature, spirituality, culinary, crafts) with persistent TopicMemory deduplication.
"""

from __future__ import annotations

import random
from typing import Optional, Tuple

from src.core.telemetry import logger
from src.services.topic_memory import topic_memory
from src.studios.documentary_studio.doc_templates import DocGenre

CONTINENT_COUNTRIES_MAP: dict[str, list[str]] = {
    "europe_nations": [
        "Poland", "Czech Republic", "Austria", "Italy", "France", "Spain",
        "Portugal", "Germany", "Greece", "Scotland", "Switzerland", "Norway",
        "Netherlands", "Ireland", "Croatia", "Hungary", "Romania", "Sweden",
        "Denmark", "Belgium", "Finland", "Slovenia", "Estonia", "Slovakia",
    ],
    "asia_nations": [
        "Japan", "India", "Vietnam", "South Korea", "Thailand", "Jordan",
        "Indonesia", "China", "Nepal", "Malaysia", "Oman", "Turkey",
        "Cambodia", "Sri Lanka", "Philippines", "Taiwan", "Uzbekistan",
        "Singapore", "Bhutan", "Laos",
    ],
    "americas_nations": [
        "Peru", "Canada", "Mexico", "Brazil", "Chile", "Colombia",
        "Argentina", "Costa Rica", "United States", "Guatemala", "Ecuador",
        "Bolivia", "Panama", "Uruguay",
    ],
    "africa_nations": [
        "Egypt", "Morocco", "Kenya", "South Africa", "Tanzania", "Namibia",
        "Ethiopia", "Zimbabwe", "Botswana", "Madagascar", "Ghana", "Tunisia",
        "Rwanda", "Uganda",
    ],
    "oceania_nations": [
        "New Zealand", "Australia", "Fiji", "French Polynesia", "Samoa",
        "Papua New Guinea", "Cook Islands", "Vanuatu",
    ],
    "nordic_polar_nations": [
        "Iceland", "Norway", "Greenland", "Svalbard", "Finland",
        "Faroe Islands", "Sweden",
    ],
}

# Backward compatibility aliases
CONTINENT_COUNTRIES_MAP["europe_countries"] = CONTINENT_COUNTRIES_MAP["europe_nations"]
CONTINENT_COUNTRIES_MAP["asia_countries"] = CONTINENT_COUNTRIES_MAP["asia_nations"]
CONTINENT_COUNTRIES_MAP["americas_countries"] = CONTINENT_COUNTRIES_MAP["americas_nations"]
CONTINENT_COUNTRIES_MAP["africa_countries"] = CONTINENT_COUNTRIES_MAP["africa_nations"]
CONTINENT_COUNTRIES_MAP["oceania_countries"] = CONTINENT_COUNTRIES_MAP["oceania_nations"]
CONTINENT_COUNTRIES_MAP["nordic_arctic_countries"] = CONTINENT_COUNTRIES_MAP["nordic_polar_nations"]

ARCHETYPE_TEMPLATES: dict[str, list[str]] = {
    "ancient_history_dynasties": [
        "Chronicles of {country}: Ancient Dynasties, Lost Empires & Historic Foundations",
        "{country}: Deep History, Monumental Eras & Timeless Ruins",
    ],
    "national_identity_heritage": [
        "Soul of {country}: Cultural Identity, Sacred Heritage & National Spirit",
        "{country}: Timeless Heritage, Royal Symbols & The National Story",
    ],
    "great_cities_metropolises": [
        "Crowns of {country}: Great Historic Cities, Metropolises & Urban Marvels",
        "Metropolises of {country}: Architectural Splendor & Historic Piazzas",
    ],
    "natural_history_geology": [
        "Earth & Deep Time: The Geological Wonders & Natural History of {country}",
        "{country}: Ancient Canyons, Volcanic Strata & Tectonic Origins",
    ],
    "spiritual_sanctuaries": [
        "Sacred Sanctuaries of {country}: Holy Shrines, Mountain Monasteries & Ancient Temples",
        "{country}: Spiritual Sanctuaries, Cathedral Spires & Sacred Pilgrimage Paths",
    ],
    "cultural_entertainment_zones": [
        "Cultural Vibrance of {country}: Historic Theatres, Entertainment Quarters & Festivals",
        "{country}: Performing Arts, Vibrant Nightlife Quarters & Cultural Festivals",
    ],
    "sports_arenas_legacy": [
        "Athletic Glory of {country}: Legendary Stadiums, Historic Arenas & Sporting Heritage",
        "{country}: Sports Heritage, Monumental Colosseums & Athletic Passion",
    ],
    "luminaries_pioneers": [
        "Great Minds of {country}: Famous Figures, Visionaries, Artists & Historic Pioneers",
        "Luminaries of {country}: The Pioneers, Philosophers & Masterminds Who Shaped History",
    ],
    "modern_evolution_transformation": [
        "The Evolution of {country}: From Ancient Foundations to Futuristic Megastructures",
        "{country} Transformed: Modern Engineering, High-Speed Vistas & Visionary Frontiers",
    ],
    "scenic_landscapes_horizons": [
        "Majestic Horizons of {country}: Postcard Vistas, Alpine Lakes & Untamed Splendor",
        "Vistas of {country}: Iconic Horizons, Mountain Valleys & Crystalline Rivers",
    ],
    "provinces_regional_countryside": [
        "Hidden Provinces of {country}: Idyllic Countryside, Timeless Hamlets & Bluffs",
        "{country} Beyond the Cities: Regional Sanctuaries, Vineyards & Ancient Villages",
    ],
    "biodiversity_untamed_wildlife": [
        "Untamed {country}: Living Biodiversity, Ancient Canopies & National Parks",
        "Wild {country}: Primeval Ecosystems, Rare Fauna & Protected Biospheres",
    ],
    "climate_seasons_weather": [
        "Four Seasons of {country}: Dramatic Weather, Autumn Gold & Alpine Blizzards",
        "Atmospheric {country}: Monsoon Whispers, Winter Snows & Shifting Seasons",
    ],
    "engineering_marvels": [
        "Engineering Marvels of {country}: Monumental Bridges, Aqueducts & Megastructures",
        "Master Builders of {country}: Colossal Engineering Feats & Structural Wonders",
    ],
    "history_architecture": [
        "Architectural Heritage of {country}: Royal Palaces, Citadels & Classical Facades",
        "Crowns in Stone: The Master Architecture, Castles & Monuments of {country}",
    ],
    "archaeological_ruins_lost_empires": [
        "Lost Civilizations of {country}: Megalithic Ruins, Buried Fortresses & Sacred Stones",
        "{country} Unearthed: Lost Empires, Ancient Necropolises & Megalithic Mysteries",
    ],
    "culinary_gastronomic_heritage": [
        "Culinary Heritage of {country}: Historic Street Markets, Artisan Flavors & Gastronomy",
        "The Flavors of {country}: Ancient Culinary Traditions, Vineyards & Sacred Feasts",
    ],
    "living_traditions_artisan_crafts": [
        "Living Traditions of {country}: Master Artisans, Folk Pageantry & Ancient Crafts",
        "Soul & Craft of {country}: Traditional Folk Festivals, Living Guilds & Heritage Artisans",
    ],
    "coastal_islands_maritime": [
        "Maritime Wonders of {country}: Ocean Clifftops, Historic Harbors & Azure Islands",
        "Coastal Sanctuaries of {country}: Sea Cliffs, Lighthouses & Turquoise Waters",
    ],
    "historic_trade_routes_journeys": [
        "Historic Journeys of {country}: Ancient Trade Routes, Mountain Passes & Caravan Trails",
        "The Great Trails of {country}: Ancient Pilgrimage Passes, Silk Corridors & Alpine Crossings",
    ],
    "geographic_regions_zones": [
        "Geographic Regions of {country}: Exploring the Great Territories, Zones & Divided Landscapes",
        "{country} by Region: North, South, East & West - Diverse Terrains & Cultural Frontiers",
    ],
    "cultural_mosaic_traditions": [
        "Cultural Mosaic of {country}: Regional Sub-Cultures, Diverse Peoples & Living Customs",
        "The Cultural Tapestry of {country}: Indigenous Heritage, Regional Customs & Communities",
    ],
}

# Aliases for backwards compatibility with earlier tests & variations
ARCHETYPE_TEMPLATES["wonders_of_country"] = ARCHETYPE_TEMPLATES["national_identity_heritage"]
ARCHETYPE_TEMPLATES["famous_cities"] = ARCHETYPE_TEMPLATES["great_cities_metropolises"]
ARCHETYPE_TEMPLATES["architecture_country"] = ARCHETYPE_TEMPLATES["history_architecture"]
ARCHETYPE_TEMPLATES["architecture_cities"] = ARCHETYPE_TEMPLATES["engineering_marvels"]
ARCHETYPE_TEMPLATES["history_of_country"] = ARCHETYPE_TEMPLATES["ancient_history_dynasties"]
ARCHETYPE_TEMPLATES["nature_wilderness"] = ARCHETYPE_TEMPLATES["scenic_landscapes_horizons"]
ARCHETYPE_TEMPLATES["coastal_maritime"] = ARCHETYPE_TEMPLATES["coastal_islands_maritime"]
ARCHETYPE_TEMPLATES["regions_of_country"] = ARCHETYPE_TEMPLATES["geographic_regions_zones"]
ARCHETYPE_TEMPLATES["regions_in_country"] = ARCHETYPE_TEMPLATES["geographic_regions_zones"]
ARCHETYPE_TEMPLATES["cultures_of_country"] = ARCHETYPE_TEMPLATES["cultural_mosaic_traditions"]
ARCHETYPE_TEMPLATES["cultures_in_country"] = ARCHETYPE_TEMPLATES["cultural_mosaic_traditions"]

ARCHETYPE_GENRE_MAP: dict[str, DocGenre] = {
    "ancient_history_dynasties": DocGenre.ANCIENT_STRUCTURES,
    "national_identity_heritage": DocGenre.PLACES,
    "great_cities_metropolises": DocGenre.PLACES,
    "natural_history_geology": DocGenre.NATURE,
    "spiritual_sanctuaries": DocGenre.ANCIENT_STRUCTURES,
    "cultural_entertainment_zones": DocGenre.PLACES,
    "sports_arenas_legacy": DocGenre.PLACES,
    "luminaries_pioneers": DocGenre.PLACES,
    "modern_evolution_transformation": DocGenre.PLACES,
    "scenic_landscapes_horizons": DocGenre.NATURE,
    "provinces_regional_countryside": DocGenre.NATURE,
    "biodiversity_untamed_wildlife": DocGenre.WILDLIFE,
    "climate_seasons_weather": DocGenre.NATURE,
    "engineering_marvels": DocGenre.ANCIENT_STRUCTURES,
    "history_architecture": DocGenre.ANCIENT_STRUCTURES,
    "archaeological_ruins_lost_empires": DocGenre.ANCIENT_STRUCTURES,
    "culinary_gastronomic_heritage": DocGenre.PLACES,
    "living_traditions_artisan_crafts": DocGenre.PLACES,
    "coastal_islands_maritime": DocGenre.OCEAN,
    "historic_trade_routes_journeys": DocGenre.PLACES,
    "geographic_regions_zones": DocGenre.PLACES,
    "cultural_mosaic_traditions": DocGenre.PLACES,
    "regions_of_country": DocGenre.PLACES,
    "regions_in_country": DocGenre.PLACES,
    "cultures_of_country": DocGenre.PLACES,
    "cultures_in_country": DocGenre.PLACES,
    "wonders_of_country": DocGenre.PLACES,
    "famous_cities": DocGenre.PLACES,
    "architecture_country": DocGenre.ANCIENT_STRUCTURES,
    "architecture_cities": DocGenre.ANCIENT_STRUCTURES,
    "history_of_country": DocGenre.ANCIENT_STRUCTURES,
    "nature_wilderness": DocGenre.NATURE,
    "coastal_maritime": DocGenre.OCEAN,
}


def is_geo_continent_subgenre(sub_genre: str) -> bool:
    """Check if subgenre belongs to continent country rotation."""
    return (sub_genre or "").lower().strip() in CONTINENT_COUNTRIES_MAP


def resolve_autonomous_geo_theme(
    sub_genre: str,
    archetype: str,
    user_id: Optional[str] = None,
    channel_id: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> Tuple[DocGenre, str, str]:
    """Autonomously resolve unvisited country, matching theme, and DocGenre with zero prompt requirement."""
    sub_clean = (sub_genre or "").lower().strip()
    arch_clean = (archetype or "").lower().strip()
    if arch_clean not in ARCHETYPE_TEMPLATES:
        arch_clean = "national_identity_heritage"

    # If the user explicitly typed a custom prompt, honor it directly
    if custom_prompt and custom_prompt.strip():
        eff_genre = ARCHETYPE_GENRE_MAP.get(arch_clean, DocGenre.PLACES)
        return eff_genre, arch_clean, custom_prompt.strip()

    country_pool = CONTINENT_COUNTRIES_MAP.get(sub_clean, CONTINENT_COUNTRIES_MAP["europe_nations"])

    recent_topics = []
    try:
        recent_topics = topic_memory.get_recent_topics(user_id=user_id, channel_id=channel_id, limit=60)
    except Exception as ex:
        logger.warning(f"geo_rotation_history_lookup_failed: {ex}")

    seen_text = " ".join(recent_topics).lower()

    # Find the first country in the continent pool that has not appeared in recent topics
    selected_country = None
    for country in country_pool:
        if country.lower() not in seen_text:
            selected_country = country
            break

    # If all countries in this continent have had an episode, auto-pivot to a secondary angle
    if not selected_country:
        selected_country = random.choice(country_pool)
        angle_pivots = [
            "Hidden Gems & Secret Sanctuaries",
            "Ancient Heartland & Northern Coast",
            "Lost Valleys & Alpine Strongholds",
        ]
        chosen_pivot = random.choice(angle_pivots)
        theme_title = f"{selected_country}: {chosen_pivot} ({arch_clean.replace('_', ' ').title()})"
    else:
        template_candidates = ARCHETYPE_TEMPLATES.get(arch_clean, ARCHETYPE_TEMPLATES["national_identity_heritage"])
        theme_title = template_candidates[0].format(country=selected_country)

    eff_genre = ARCHETYPE_GENRE_MAP.get(arch_clean, DocGenre.PLACES)
    logger.info(
        f"autonomous_geo_rotation: continent='{sub_clean}' archetype='{arch_clean}' "
        f"country='{selected_country}' theme='{theme_title}' genre={eff_genre.value}"
    )
    return eff_genre, arch_clean, theme_title


__all__ = [
    "CONTINENT_COUNTRIES_MAP",
    "ARCHETYPE_TEMPLATES",
    "ARCHETYPE_GENRE_MAP",
    "is_geo_continent_subgenre",
    "resolve_autonomous_geo_theme",
]
