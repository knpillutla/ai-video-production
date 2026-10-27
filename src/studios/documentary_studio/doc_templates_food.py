"""Title templates, aliases, and genre mappings for food, agriculture & regional cuisines."""
from __future__ import annotations
from src.studios.documentary_studio.doc_templates import DocGenre

FOOD_TEMPLATES: dict[str, list[str]] = {
    "food_production_consumption": [
        "What {entity} Produces vs. What They Actually Eat: The Hidden Food Economy",
        "{entity}'s Food Engine: Major Crops, Massive Exports & Calorie Self-Sufficiency Explained",
    ],
    "regional_cuisines": [
        "What People Eat Across Different Regions of {entity}: North vs. South Flavor Wars",
        "The Regional Flavors of {entity}: How Every Province Cooks Completely Differently",
    ],
    "food_culture_rituals": [
        "The Sacred Food Culture of {entity}: Daily Dining Rituals & Unwritten Kitchen Rules",
        "Inside {entity}'s Food Soul: Why Eating Here Is a Sacred Daily Ritual",
    ],
    "culinary_gastronomic_heritage": [
        "Flavors of {entity}: Ancient Gastronomy, Regional Markets & Culinary Heritage",
        "{entity} on a Plate: Heritage Recipes, Vineyard Terroirs & Living Traditions",
    ],
    "agriculture_farming_harvests": [
        "{entity}'s Agricultural Powerhouse: Vast Farmlands, Golden Harvests & Precision Agritech",
        "The Agrarian Heart of {entity}: Terraced Fields, Heritage Vineyards & Farming Mastery",
    ],
    "supermarkets_and_grocery_culture": [
        "Inside {entity}'s Supermarkets: Unique Aisles, Weird Snacks & Daily Grocery Culture",
        "Why Supermarkets in {entity} Are in a League of Their Own: Aisles, Prices & Hidden Gems",
        "What Shopping in {entity}'s Supermarkets Reveals About How Locals Actually Live",
    ],
}

FOOD_ALIASES: dict[str, str] = {
    "food_production": "food_production_consumption", "food_consumption": "food_production_consumption", "what_they_produce": "food_production_consumption", "agricultural_economy": "food_production_consumption", "farm_to_table": "food_production_consumption", "food_trade": "food_production_consumption", "agri_production": "food_production_consumption",
    "regional_food": "regional_cuisines", "what_they_eat": "regional_cuisines", "provincial_cuisines": "regional_cuisines", "local_plates": "regional_cuisines", "regional_dishes": "regional_cuisines", "what_do_they_eat": "regional_cuisines",
    "food_culture": "food_culture_rituals", "dining_etiquette": "food_culture_rituals", "culinary_rituals": "food_culture_rituals", "eating_customs": "food_culture_rituals", "food_traditions": "food_culture_rituals", "kitchen_rules": "food_culture_rituals",
    "gastronomic_heritage": "culinary_gastronomic_heritage", "culinary_heritage": "culinary_gastronomic_heritage", "street_food": "culinary_gastronomic_heritage", "national_dishes": "culinary_gastronomic_heritage",
    "agriculture": "agriculture_farming_harvests", "farming": "agriculture_farming_harvests", "harvests": "agriculture_farming_harvests", "agrarian_heartland": "agriculture_farming_harvests", "crop_harvests": "agriculture_farming_harvests", "vineyards_orchards": "agriculture_farming_harvests", "farms": "agriculture_farming_harvests",
    "supermarkets": "supermarkets_and_grocery_culture", "supermarket": "supermarkets_and_grocery_culture", "grocery_stores": "supermarkets_and_grocery_culture", "grocery_store": "supermarkets_and_grocery_culture", "supermarket_culture": "supermarkets_and_grocery_culture", "grocery_culture": "supermarkets_and_grocery_culture", "hypermarkets": "supermarkets_and_grocery_culture", "convenience_stores": "supermarkets_and_grocery_culture", "food_halls": "supermarkets_and_grocery_culture", "grocery_shopping": "supermarkets_and_grocery_culture",
}

FOOD_GENRE_MAP: dict[str, DocGenre] = {
    "food_production_consumption": DocGenre.PLACES,
    "regional_cuisines": DocGenre.PLACES,
    "food_culture_rituals": DocGenre.PLACES,
    "culinary_gastronomic_heritage": DocGenre.PLACES,
    "agriculture_farming_harvests": DocGenre.PLACES,
    "supermarkets_and_grocery_culture": DocGenre.PLACES,
}

