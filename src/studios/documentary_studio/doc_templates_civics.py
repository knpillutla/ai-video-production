"""Title templates, aliases, and genre mappings for civics, history & performing arts."""
from __future__ import annotations
from src.studios.documentary_studio.doc_templates import DocGenre

CIVICS_TEMPLATES: dict[str, list[str]] = {
    "ancient_history_dynasties": [
        "Chronicles of {entity}: Ancient Dynasties, Lost Empires & Historic Foundations",
        "{entity}: Deep History, Monumental Eras & Timeless Ruins",
    ],
    "modern_evolution_transformation": [
        "The Evolution of {entity}: From Ancient Foundations to Futuristic Megastructures",
        "{entity} Transformed: Modern Engineering, High-Speed Vistas & Visionary Frontiers",
    ],
    "major_projects": [
        "Engineering Marvels of {entity}: Monumental Bridges, Aqueducts & Megastructures",
        "Master Builders of {entity}: Colossal Engineering Feats & Structural Wonders",
    ],
    "engineering_marvels": [
        "Engineering Marvels of {entity}: Monumental Bridges, Aqueducts & Megastructures",
        "Master Builders of {entity}: Colossal Engineering Feats & Structural Wonders",
    ],
    "luminaries_pioneers": [
        "Great Minds of {entity}: Famous Figures, Visionaries, Artists & Historic Pioneers",
        "Luminaries of {entity}: The Pioneers, Philosophers & Masterminds Who Shaped History",
    ],
    "archaeological_ruins_lost_empires": [
        "Lost Civilizations of {entity}: Megalithic Ruins, Buried Fortresses & Sacred Stones",
        "{entity} Unearthed: Lost Empires, Ancient Necropolises & Megalithic Mysteries",
    ],
    "historic_trade_routes_journeys": [
        "Historic Trade Routes of {entity}: Ancient Silk Roads, Caravan Trails & River Highways",
        "Caravans & Ports: The Epic Merchant Highways & Maritime Fortunes of {entity}",
    ],
    "turning_points": [
        "The Day Everything Changed in {entity}: The Untold Turning Point That Forged a Nation",
        "{entity}'s Defining Moment: The Epic Crisis That Reshaped Their Entire Destiny",
    ],
    "elected_leaders": [
        "Every President of {entity} in Order: Where They Studied & How They Transformed the Nation",
        "The Rulers of {entity}: Independence to Today (Triumphs, Scandals & Legacies)",
    ],
    "wealthy_dynasties": [
        "The Secret Billionaire Dynasties of {entity}: Who Actually Controls the Wealth?",
        "Inside {entity}'s Ultra-Rich Families: Private Estates, Dynastic Power & Untold Fortunes",
    ],
    "music_and_dance": [
        "The Rhythms of {entity}: Sacred Melodies, Folk Dances & Living Musical Soul",
        "Inside {entity}'s Music & Dance Heritage: From Ancient Folk Steps to Modern Beats",
    ],
    "cinema_and_film_industry": [
        "Inside {entity}'s Movie Industry: The Golden Age of Cinema, Superstars & Visionary Directors",
        "{entity}'s Film Phenomenon: How Cinema, Blockbusters & Box Office Legends Forged Culture",
    ],
    "major_industries_manufacturing": [
        "Inside {entity}'s Colossal Industries: Mega-Factories, Robotics & Manufacturing Power",
        "{entity}'s Industrial Empire: How Heavy Industry & Engineering Built a Global Powerhouse",
    ],
}

CIVICS_ALIASES: dict[str, str] = {
    "history": "ancient_history_dynasties", "deep_history": "ancient_history_dynasties", "ancient_civilizations_history": "ancient_history_dynasties", "history_of_country": "ancient_history_dynasties",
    "evolution": "modern_evolution_transformation", "future_evolution": "modern_evolution_transformation",
    "infrastructure": "major_projects", "megastructures": "major_projects", "architecture_cities": "engineering_marvels",
    "major_events": "turning_points", "defining_moments": "turning_points", "historic_crises": "turning_points", "historical_events": "turning_points",
    "presidents": "elected_leaders", "prime_ministers": "elected_leaders", "history_of_presidents": "elected_leaders", "political_leaders": "elected_leaders", "rulers": "elected_leaders", "elected_heads": "elected_leaders",
    "rich_families": "wealthy_dynasties", "ultra_rich_families": "wealthy_dynasties", "billionaires": "wealthy_dynasties", "dynasties": "wealthy_dynasties", "old_money": "wealthy_dynasties", "wealthy_families": "wealthy_dynasties",
    "music": "music_and_dance", "dance": "music_and_dance", "music_dance": "music_and_dance", "traditional_music": "music_and_dance", "folk_dance": "music_and_dance", "music_traditions": "music_and_dance", "classical_music": "music_and_dance",
    "movie_history": "cinema_and_film_industry", "cinema_history": "cinema_and_film_industry", "film_history": "cinema_and_film_industry", "film_industry": "cinema_and_film_industry", "cinema_culture": "cinema_and_film_industry", "film_heritage": "cinema_and_film_industry", "regional_cinema": "cinema_and_film_industry", "bollywood_tollywood": "cinema_and_film_industry", "cinema": "cinema_and_film_industry", "movies": "cinema_and_film_industry",
    "industries": "major_industries_manufacturing", "manufacturing": "major_industries_manufacturing", "industrial_powerhouse": "major_industries_manufacturing", "factories": "major_industries_manufacturing", "heavy_industry": "major_industries_manufacturing", "industrial_giants": "major_industries_manufacturing", "industrial_hub": "major_industries_manufacturing",
}

CIVICS_GENRE_MAP: dict[str, DocGenre] = {
    k: DocGenre.ANCIENT_STRUCTURES for k in (
        "ancient_history_dynasties", "engineering_marvels", "major_projects",
        "archaeological_ruins_lost_empires", "turning_points", "elected_leaders",
        "wealthy_dynasties", "music_and_dance", "cinema_and_film_industry",
    )
}
CIVICS_GENRE_MAP.update({
    "modern_evolution_transformation": DocGenre.PLACES,
    "luminaries_pioneers": DocGenre.PLACES,
    "historic_trade_routes_journeys": DocGenre.PLACES,
    "major_industries_manufacturing": DocGenre.PLACES,
})
