"""Title templates, aliases, and genre mappings for curiosity, heartland, demographics & extreme frontiers."""
from __future__ import annotations
from src.studios.documentary_studio.doc_templates import DocGenre

CURIOSITY_TEMPLATES: dict[str, list[str]] = {
    "unseen_frontiers": [
        "Unseen {entity}: Hidden Worlds, Forbidden Sanctuaries & Secret Enclaves",
        "Unseen {entity}: The Subterranean Vaults & Lost Mountain Realms",
    ],
    "cultural_curiosities": [
        "Why People in {entity} Live Like This: Enigmatic Traditions & Cultural Secrets",
        "Cultural Curiosities of {entity}: Bizarre Rituals, Timeless Etiquette & Daily Secrets",
    ],
    "small_towns": [
        "Small Towns of {entity}: How People Actually Live Far From the Cities",
        "{entity}'s Hidden Villages: Daily Rhythms, Cobblestone Squares & Quiet Heritage",
    ],
    "survival_paradox": [
        "How {entity} Defied Geography: The Improbable Survival & Hidden Mastery",
        "{entity}: How They Thrived Against All Geographic & Climatic Odds",
    ],
    "unwritten_rules": [
        "10 Unwritten Rules You Must Never Break in {entity}: Secret Etiquette & Codes",
        "The Unspoken Customs of {entity}: Why Locals Do What Foreigners Misunderstand",
    ],
    "isolated_communities": [
        "At the Edge of {entity}: Inside the Most Isolated & Snowbound Communities",
        "{entity}'s Forgotten Enclaves: Life in Roadless Hamlets & Cliffside Villages",
    ],
    "lost_trades": [
        "The Last Masters of {entity}: Vanishing Crafts & Ancient Living Heritage",
        "{entity}'s Final Artisans: Centuries-Old Secrets of Master Craftsmen",
    ],
    "cost_of_living": [
        "How People in {entity} Actually Live: Real Wages, Rent & Supermarket Costs",
        "What Life Actually Costs in {entity}: How Normal Families Survive & Spend",
    ],
    "deep_heartland": [
        "{entity}'s Deep Heartland: How People Actually Survive Where Tourists Never Go",
        "Inside the Deep Heartland of {entity}: Life Beyond the Cities & Power Grid",
    ],
    "remote_outposts": [
        "Life at the Edge of Nowhere: Inside {entity}'s Most Isolated Settlements",
        "{entity}'s Extreme Outposts: 1,000 Miles From Any Road or Hospital",
    ],
    "resilience_triumph": [
        "How {entity} Survived Earth's Deadliest Forces & Rebuilt Stronger",
        "Rising From the Storm: How {entity} Conquered Cyclones, Earthquakes & Came Out Unbroken",
    ],
    "most_dangerous": [
        "The 10 Most Dangerous Places in {entity} (Where One Mistake Is Fatal)",
        "Inside {entity}'s Deadliest Frontiers: Treacherous Roads, Volcanic Chasms & Extreme Survival",
    ],
    "women_of_nation": [
        "Inside the Lives of Women in {entity}: Unwritten Rules, Daily Rhythms & Enduring Grace",
        "The Women of {entity}: How Female Leadership, Matriarchs & Living Traditions Shaped a Nation",
    ],
    "men_of_nation": [
        "What It's Actually Like Being a Man in {entity}: Work Culture, Honor & Ancient Crafts",
        "The Men of {entity}: Brotherhood, Extreme Trades & The Modern Struggle",
    ],
    "family_and_marriage_culture": [
        "Inside Family & Marriage Culture in {entity}: Sacred Weddings, Dowries & Extended Clans",
        "The Sacred Family Soul of {entity}: How Multi-Generational Bonds & Wedding Rituals Hold Society Together",
    ],
}

CURIOSITY_ALIASES: dict[str, str] = {
    "unseen": "unseen_frontiers", "curiosities": "cultural_curiosities", "why_locals_do_this": "cultural_curiosities",
    "small_town": "small_towns", "village_life": "small_towns", "how_people_live": "small_towns", "provincial_life": "small_towns",
    "paradox": "survival_paradox", "defied_geography": "survival_paradox", "social_rules": "unwritten_rules", "etiquette_rules": "unwritten_rules",
    "isolated_life": "isolated_communities", "edge_of_the_world": "isolated_communities", "ancient_crafts": "lost_trades", "master_craftsmen": "lost_trades",
    "how_locals_live": "cost_of_living", "purchasing_power": "cost_of_living",
    "hinterlands": "deep_heartland", "rural": "deep_heartland", "rural_life": "deep_heartland", "backcountry": "deep_heartland", "forgotten_provinces": "deep_heartland", "heartland": "deep_heartland",
    "remote_places": "remote_outposts", "extreme_remoteness": "remote_outposts", "edge_of_nowhere": "remote_outposts", "isolated_places": "remote_outposts",
    "natural_resilience": "resilience_triumph", "rebuilding_stronger": "resilience_triumph", "unbroken_spirit": "resilience_triumph",
    "cyclones_earthquakes": "resilience_triumph", "disaster_resilience": "resilience_triumph", "natural_calamities": "resilience_triumph", "natural_disasters": "resilience_triumph", "calamities": "resilience_triumph",
    "extreme_danger_zones": "most_dangerous", "deadliest_places": "most_dangerous", "danger_zones": "most_dangerous", "extreme_frontiers": "most_dangerous", "dangerous_places": "most_dangerous",
    "about_women": "women_of_nation", "women": "women_of_nation", "women_life": "women_of_nation", "women_traditions": "women_of_nation", "women_of_country": "women_of_nation", "daily_life_women": "women_of_nation",
    "about_men": "men_of_nation", "men": "men_of_nation", "men_life": "men_of_nation", "men_traditions": "men_of_nation", "men_of_country": "men_of_nation", "daily_life_men": "men_of_nation",
    "family_marriage": "family_and_marriage_culture", "marriage_culture": "family_and_marriage_culture", "family_culture": "family_and_marriage_culture", "weddings": "family_and_marriage_culture", "wedding_traditions": "family_and_marriage_culture", "family_traditions": "family_and_marriage_culture",
}

CURIOSITY_GENRE_MAP: dict[str, DocGenre] = {
    k: DocGenre.PLACES for k in (
        "unseen_frontiers", "cultural_curiosities", "small_towns", "survival_paradox",
        "unwritten_rules", "isolated_communities", "lost_trades", "cost_of_living",
        "deep_heartland", "remote_outposts", "women_of_nation", "men_of_nation",
        "family_and_marriage_culture",
    )
}
CURIOSITY_GENRE_MAP.update({
    "resilience_triumph": DocGenre.NATURE,
    "most_dangerous": DocGenre.NATURE,
})
