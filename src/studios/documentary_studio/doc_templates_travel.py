"""Title templates, aliases, and genre mappings for travel, cities, nature & coastal sanctuaries."""
from __future__ import annotations
from src.studios.documentary_studio.doc_templates import DocGenre

TRAVEL_TEMPLATES: dict[str, list[str]] = {
    "country_dossier": [
        "{entity}: The Complete Country Dossier - Geography, History, Economy & Soul",
        "{entity} Dossier: Area, Climate, Universities, Global Alliances & Iconic Heritage",
    ],
    "top_10_cities": [
        "{entity}: Top 10 Cities to Visit (Ranked Countdown #10 to #1)",
        "Top 10 Cities in {entity}: The Definitive Ranked Countdown & Hidden Gems",
    ],
    "top_places_to_visit": [
        "{entity}: Top Places to Visit (Ranked Countdown from Last to #1)",
        "50 Most Beautiful Places to Visit in {entity} - Citadels, Wonders & Towns",
    ],
    "top_20_places": [
        "Top 20 Places to Visit in {entity} (Ranked Countdown #20 to #1)",
        "{entity}: The Definitive Top 20 Bucket List - Ranked from #20 to the Ultimate #1",
    ],
    "cleanest_cities_places": [
        "Top 10 Cleanest Cities & Places in {entity} (Ranked Countdown #10 to #1)",
        "Inside {entity}'s Spotless Sanctuaries: Zero-Litter Towns & Eco-Metropolises Ranked",
    ],
    "nations": [
        "{entity}: Complete Documentary - Attractions, Nature, History, Luminaries, Inventions & Trade",
        "Exploring {entity}: Famous Landmarks, Wildlife, Great Cities, People & Living Spirit",
    ],
    "cities": [
        "{entity}: Complete City Documentary - Attractions, History, Great Minds, Squares, Trade & Culture",
        "Exploring {entity}: Iconic Sights, Historic Piazzas, Luminaries, Urban Transit & Living Soul",
    ],
    "national_identity_heritage": [
        "Soul of {entity}: Cultural Identity, Sacred Heritage & National Spirit",
        "{entity}: Timeless Heritage, Royal Symbols & The National Story",
    ],
    "great_cities_metropolises": [
        "Crowns of {entity}: Great Historic Cities, Metropolises & Urban Marvels",
        "Metropolises of {entity}: Architectural Splendor & Historic Piazzas",
    ],
    "natural_history_geology": [
        "Earth & Deep Time: The Geological Wonders & Natural History of {entity}",
        "{entity}: Ancient Canyons, Volcanic Strata & Tectonic Origins",
    ],
    "spiritual_sanctuaries": [
        "Sacred Sanctuaries of {entity}: Holy Shrines, Mountain Monasteries & Ancient Temples",
        "{entity}: Spiritual Sanctuaries, Cathedral Spires & Sacred Pilgrimage Paths",
    ],
    "cultural_entertainment_zones": [
        "Cultural Vibrance of {entity}: Historic Theatres, Entertainment Quarters & Festivals",
        "{entity}: Performing Arts, Vibrant Nightlife Quarters & Cultural Festivals",
    ],
    "sports_arenas_legacy": [
        "Athletic Glory of {entity}: Legendary Stadiums, Historic Arenas & Sporting Heritage",
        "{entity}: Sports Heritage, Monumental Colosseums & Athletic Passion",
    ],
    "scenic_landscapes_horizons": [
        "Majestic Horizons of {entity}: Postcard Vistas, Alpine Lakes & Untamed Splendor",
        "Vistas of {entity}: Iconic Horizons, Mountain Valleys & Crystalline Rivers",
    ],
    "provinces_regional_countryside": [
        "Hidden Provinces of {entity}: Idyllic Countryside, Timeless Hamlets & Bluffs",
        "{entity} Beyond the Cities: Regional Sanctuaries, Vineyards & Ancient Villages",
    ],
    "biodiversity_untamed_wildlife": [
        "Untamed {entity}: Living Biodiversity, Ancient Canopies & National Parks",
        "Wild {entity}: Primeval Ecosystems, Rare Fauna & Protected Biospheres",
    ],
    "climate_seasons_weather": [
        "Four Seasons of {entity}: Dramatic Weather, Autumn Gold & Alpine Blizzards",
        "Atmospheric {entity}: Monsoon Whispers, Winter Snows & Shifting Seasons",
    ],
    "history_architecture": [
        "Architectural Heritage of {entity}: Royal Palaces, Citadels & Classical Facades",
        "Crowns in Stone: The Master Architecture, Castles & Monuments of {entity}",
    ],
    "living_traditions_artisan_crafts": [
        "Living Traditions of {entity}: Master Artisans, Ancient Guilds & Cultural Rituals",
        "{entity} Craftsmen: Ancient Metalwork, Weaving Guilds & Timeless Arts",
    ],
    "geographic_regions_zones": [
        "Geographic Wonder of {entity}: Deserts, Alpine Valleys, Plateaus & Living Coasts",
        "{entity}: A Journey Across Varied Ecosystems, River Basins & Highlands",
    ],
    "cultural_mosaic_traditions": [
        "Cultural Mosaic of {entity}: Enduring Dialects, Folklore, Festivals & Community Spirit",
        "Voices of {entity}: Cultural Diversity, Sacred Festivals & Folk Traditions",
    ],
    "coastal_islands_maritime": [
        "Coastal Splendor of {entity}: Dramatic Cliffs, Remote Archipelagos & Maritime Lore",
        "{entity} by the Sea: Azure Fjords, Historic Lighthouses & Island Fortresses",
    ],
    "culture_heritage": [
        "The Soul of {entity}: Ancient Customs, Daily Philosophy & Living Heritage",
        "Inside {entity}'s Hidden Culture: The Values & Living Traditions Outsiders Never Understand",
    ],
    "aviation_gateways": [
        "Inside {entity}'s Most Insane Mega-Airports: Engineering Feats & Luxury Gateways",
        "{entity}'s Busiest & Most Extreme Runways: From Mountain Cliffs to 100M-Passenger Super-Hubs",
    ],
    "coastal_beaches": [
        "Top 10 Most Stunning Beaches in {entity}: Turquoise Waters & Secret Coves",
        "{entity}'s Hidden Beach Paradises: Untouched Shores & Tropical Escapes",
    ],
    "luxury_resorts": [
        "Inside {entity}'s Most Insanely Luxurious Resorts: $5,000/Night Escapes",
        "{entity}'s Ultimate Luxury Sanctuaries: Private Villas, Infinity Pools & World-Class Hospitality",
    ],
    "medical_tourism": [
        "Why Millions Fly to {entity} for Healthcare: World-Class Surgery at 80% Less",
        "{entity}'s Medical Revolution: High-Tech Hospitals, Dental Sanctuaries & Global Patients",
    ],
    "beach_towns": [
        "{entity}'s Most Charming Beach Towns: Where Locals Escape the Crowds",
        "Life in {entity}'s Coastal Havens: Surf Shacks, Pastel Harborfronts & Slow Seafood Living",
    ],
    "tourism_guide": [
        "The Complete {entity} Travel Guide: 15 Things You Must Know Before You Go",
        "How to Travel {entity} Like a Local: Best Routes, Costs & Hidden Gems",
    ],
    "ancient_forests": [
        "Inside {entity}'s Primordial Forests: Ancient Canopies & Living Giants",
        "{entity}'s Deepest Wilderness: Untamed Rainforests, Moss Glades & Secret Waterways",
    ],
    "art_and_masterpieces": [
        "The Masterpieces of {entity}: How Art & Master Painters Forged National Identity",
        "Inside {entity}'s Greatest Art & Living Masters: Classical Renaissance to Avant-Garde",
    ],
    "wellness_retreats": [
        "Inside {entity}'s Most Exclusive Wellness Retreats: Alpine Spas, Thermal Springs & Sacred Sanctuaries",
        "{entity}'s Ultimate Healing Escapes: Ancient Mineral Baths, Forest Sanctuaries & Holistic Rejuvenation",
    ],
    "islands_archipelagos": [
        "{entity}'s Most Stunning Islands: Turquoise Atolls, Secret Coves & Remote Archipelagos",
        "Island-Hopping in {entity}: The Ultimate Guide to Untouched Sea Sanctuaries",
    ],
    "states_and_provinces": [
        "Every State in {entity} Explained: Distinct Cultures, Capitals & Landscapes",
        "{entity} Province by Province: The Complete Journey Across All Regions",
    ],
}

TRAVEL_ALIASES: dict[str, str] = {
    "top_cities": "top_10_cities", "top_50_places": "top_places_to_visit", "top_places": "top_places_to_visit", "places_to_visit": "top_places_to_visit",
    "top_20": "top_20_places", "top_20_tourist_places": "top_20_places", "20_places": "top_20_places", "top_20_attractions": "top_20_places",
    "cleanest_cities": "cleanest_cities_places", "cleanest_places": "cleanest_cities_places", "clean_cities": "cleanest_cities_places", "cleanest_towns": "cleanest_cities_places", "zero_waste_cities": "cleanest_cities_places",
    "country_profile": "country_dossier", "country_information": "country_dossier", "countries": "country_dossier", "nation": "nations", "city": "cities",
    "wonders_of_country": "national_identity_heritage", "famous_cities": "great_cities_metropolises", "architecture_country": "history_architecture",
    "nature_wilderness": "scenic_landscapes_horizons", "coastal_maritime": "coastal_islands_maritime", "spiritual_journeys": "spiritual_sanctuaries",
    "regions_of_country": "geographic_regions_zones", "regions_in_country": "geographic_regions_zones", "cultures_of_country": "cultural_mosaic_traditions",
    "cultures_in_country": "cultural_mosaic_traditions", "culture": "culture_heritage", "cultural_heritage": "culture_heritage", "living_culture": "culture_heritage",
    "airports": "aviation_gateways", "mega_airports": "aviation_gateways", "runways": "aviation_gateways", "aviation": "aviation_gateways",
    "beaches": "coastal_beaches", "top_beaches": "coastal_beaches", "secret_beaches": "coastal_beaches",
    "top_resorts": "luxury_resorts", "resorts": "luxury_resorts", "luxury_hotels": "luxury_resorts", "5_star_resorts": "luxury_resorts",
    "healthcare_tourism": "medical_tourism", "wellness_tourism": "medical_tourism", "medical_travel": "medical_tourism",
    "coastal_towns": "beach_towns", "seaside_towns": "beach_towns", "surf_towns": "beach_towns", "harbor_towns": "beach_towns",
    "tourism": "tourism_guide", "travel_guide": "tourism_guide", "visitor_guide": "tourism_guide",
    "forests": "ancient_forests", "rainforests": "ancient_forests", "primordial_forests": "ancient_forests",
    "art": "art_and_masterpieces", "masterpieces": "art_and_masterpieces", "fine_arts": "art_and_masterpieces", "art_history": "art_and_masterpieces",
    "wellness": "wellness_retreats", "spa_retreats": "wellness_retreats", "thermal_spas": "wellness_retreats", "healing_retreats": "wellness_retreats", "sanctuaries": "wellness_retreats", "spa": "wellness_retreats",
    "islands": "islands_archipelagos", "island_life": "islands_archipelagos", "archipelagos": "islands_archipelagos", "remote_islands": "islands_archipelagos", "secret_islands": "islands_archipelagos", "island_escapes": "islands_archipelagos", "island_hopping": "islands_archipelagos",
    "states": "states_and_provinces", "provinces": "states_and_provinces", "states_provinces": "states_and_provinces", "regions_states": "states_and_provinces", "cantons": "states_and_provinces", "prefectures": "states_and_provinces", "territories": "states_and_provinces",
}

TRAVEL_GENRE_MAP: dict[str, DocGenre] = {
    k: DocGenre.PLACES for k in (
        "country_dossier", "top_10_cities", "top_places_to_visit", "top_20_places", "cleanest_cities_places",
        "nations", "cities", "national_identity_heritage", "great_cities_metropolises",
        "cultural_entertainment_zones", "sports_arenas_legacy", "living_traditions_artisan_crafts",
        "geographic_regions_zones", "cultural_mosaic_traditions", "culture_heritage",
        "aviation_gateways", "luxury_resorts", "medical_tourism", "beach_towns", "tourism_guide",
        "wellness_retreats", "states_and_provinces",
    )
}
TRAVEL_GENRE_MAP.update({
    k: DocGenre.ANCIENT_STRUCTURES for k in (
        "spiritual_sanctuaries", "history_architecture", "art_and_masterpieces",
    )
})
TRAVEL_GENRE_MAP.update({
    k: DocGenre.NATURE for k in (
        "natural_history_geology", "scenic_landscapes_horizons", "provinces_regional_countryside",
        "climate_seasons_weather", "ancient_forests",
    )
})
TRAVEL_GENRE_MAP.update({
    "biodiversity_untamed_wildlife": DocGenre.WILDLIFE,
    "coastal_islands_maritime": DocGenre.OCEAN,
    "coastal_beaches": DocGenre.OCEAN,
    "islands_archipelagos": DocGenre.OCEAN,
})
