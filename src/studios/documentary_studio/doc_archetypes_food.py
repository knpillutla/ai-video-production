"""Food, Agriculture, Regional Cuisines & Culinary Culture Archetypes for Nations Documentaries."""
from __future__ import annotations
from typing import Dict

FOOD_ALIASES: Dict[str, str] = {
    "food_production_consumption": "food_production_consumption", "food_production": "food_production_consumption", "food_consumption": "food_production_consumption", "what_they_produce": "food_production_consumption", "agricultural_economy": "food_production_consumption", "farm_to_table": "food_production_consumption", "food_trade": "food_production_consumption", "agri_production": "food_production_consumption",
    "regional_cuisines": "regional_cuisines", "regional_food": "regional_cuisines", "what_they_eat": "regional_cuisines", "provincial_cuisines": "regional_cuisines", "local_plates": "regional_cuisines", "regional_dishes": "regional_cuisines", "what_do_they_eat": "regional_cuisines",
    "food_culture_rituals": "food_culture_rituals", "food_culture": "food_culture_rituals", "dining_etiquette": "food_culture_rituals", "culinary_rituals": "food_culture_rituals", "eating_customs": "food_culture_rituals", "food_traditions": "food_culture_rituals", "kitchen_rules": "food_culture_rituals",
    "culinary_gastronomic_heritage": "culinary_gastronomic_heritage", "gastronomic_heritage": "culinary_gastronomic_heritage", "culinary_heritage": "culinary_gastronomic_heritage", "street_food": "culinary_gastronomic_heritage", "national_dishes": "culinary_gastronomic_heritage",
    "agriculture_farming_harvests": "agriculture_farming_harvests", "agriculture": "agriculture_farming_harvests", "farming": "agriculture_farming_harvests", "harvests": "agriculture_farming_harvests", "agrarian_heartland": "agriculture_farming_harvests", "crop_harvests": "agriculture_farming_harvests", "vineyards_orchards": "agriculture_farming_harvests", "farms": "agriculture_farming_harvests",
    "supermarkets_and_grocery_culture": "supermarkets_and_grocery_culture", "supermarkets": "supermarkets_and_grocery_culture", "supermarket": "supermarkets_and_grocery_culture", "grocery_stores": "supermarkets_and_grocery_culture", "grocery_store": "supermarkets_and_grocery_culture", "supermarket_culture": "supermarkets_and_grocery_culture", "grocery_culture": "supermarkets_and_grocery_culture", "hypermarkets": "supermarkets_and_grocery_culture", "convenience_stores": "supermarkets_and_grocery_culture", "food_halls": "supermarkets_and_grocery_culture", "grocery_shopping": "supermarkets_and_grocery_culture",
}

FOOD_DIRECTIVES: Dict[str, str] = {

    "food_production_consumption": """
--- SPECIALIZED MANDATE: WHAT THE NATION PRODUCES & CONSUMES FOR FOOD ---
Investigate the nation's massive agricultural powerhouses, major crop harvests, food exports, and domestic consumption:
* Subject Focus: Staple calorie engines (wheat, rice, maize, dairy, olive oil, coffee, wine, seafood), domestic self-sufficiency rates, import vulnerabilities, high-tech greenhouses, and vertical farming.
* Economic Trade Rigor: Trace the journey from vast terraced fields and automated mega-farms to container cargo ports feeding the world and domestic supermarket shelves.
* Visual Aesthetics: Expansive golden harvest fields under morning sun, high-tech hydroponic green glow, combine harvesters working in tandem, bustling wholesale food terminals, and colorful grain silos.
* Overlay Specs: "chapter_title": "FOOD PRODUCTION", "fact_badge": "🌾 Agri-Engine (e.g. '🚜 #1 Global Olive Oil Exporter', '🍚 82% Calorie Self-Sufficiency')".
""",
    "regional_cuisines": """
--- SPECIALIZED MANDATE: REGIONAL CUISINES (WHAT THEY EAT ACROSS DIFFERENT REGIONS) ---
Explore how every province and region in the nation cooks and eats completely differently:
* Subject Focus: North vs South culinary divides, coastal seafood feasts vs mountain winter comfort stews, arid spice blends vs fertile valley dairy and truffles.
* Cultural Micro-Climates: How distinct geographic micro-climates, historical invasion routes, and local soil terroirs dictated unique regional signature dishes and flavor palettes.
* Visual Aesthetics: Sizzling cast-iron pans, steaming clay pots, rustic wooden farm tables laden with regional plates, macro close-ups of bubbling broths, and fresh olive oil drizzled on stone hearth bread.
* Overlay Specs: "chapter_title": "REGIONAL PLATE", "fact_badge": "🍲 Provincial specialty (e.g. '🏔️ Alpine Fondue & Cured Ham', '🐟 Coastal Saffron Broth')".
""",
    "food_culture_rituals": """
--- SPECIALIZED MANDATE: FOOD CULTURE & DINING RITUALS ---
Celebrate the sacred dining etiquette, unwritten kitchen codes, and generational philosophy of eating in the country:
* Subject Focus: Strict mealtime etiquette ("Why you never order cappuccino after 11 AM", "Why bread is never placed upside down"), 3-hour Sunday family feasts, sacred coffee/tea rituals, street food night markets vs home cooking, and seasonal reverence.
* Human Philosophy: How cooking is revered as the ultimate act of love, communal respect, and identity preservation where rushing a meal is considered a cultural sacrilege.
* Visual Aesthetics: Warm amber candlelight over packed family dining tables, nonnas hand-rolling pasta or rolling grape leaves with rhythmic precision, steam rising from bustling street woks, and joyous toasts.
* Overlay Specs: "chapter_title": "DINING RITUAL", "fact_badge": "🍷 Food culture (e.g. '☕ Sacred Morning Espresso Rule', '🥖 3-Hour Family Lunch Ritual')".
""",
    "culinary_gastronomic_heritage": """
--- SPECIALIZED MANDATE: CULINARY HERITAGE & GASTRONOMY ---
Delve into the historic street markets, master artisan food producers, and UNESCO-recognized gastronomic recipes:
* Subject Focus: Multi-century cheese caves, heritage vineyards, cured ham cellars, street food alleys, and traditional confectioneries.
* Artisanal Mastery: Highlight living artisans who have guarded secret family recipes and sourdough mothers across 5 generations.
* Visual Aesthetics: Macro close-ups of golden crusts cracking, molten cheese stretching, rich wine swirling in crystal, and bustling market stalls packed with vibrant produce.
* Overlay Specs: "chapter_title": "GASTRONOMIC HERITAGE", "fact_badge": "🧀 Artisan craft (e.g. '🧀 24-Month Cave-Aged Parmigiano', '🍷 400-Year Vineyard Terroir')".
""",
    "agriculture_farming_harvests": """
--- SPECIALIZED MANDATE: AGRICULTURE, FARMING & HARVEST SEASONS ---
Celebrate the nation's fertile lands, master farmers, ancient irrigation systems, and seasonal harvests:
* Subject Focus: Golden wheat fields stretching to the horizon, terraced emerald rice paddies, sun-drenched vineyards, ancient olive groves, dairy pastures, and modern precision agritech.
* Earthy Human Resonance: The deep bond between farmers and soil, generational agricultural wisdom, harvest festival pageantry, and farm-to-table pride.
* Visual Aesthetics: Slow low-altitude drone glides across undulating crop terraces in dawn mist, golden hour wheat swaying in gentle breezes, combine harvesters creating dust spirals, and macro dew on ripe grapes.
* Overlay Specs: "chapter_title": "AGRARIAN HARVEST", "fact_badge": "🚜 Agricultural wealth (e.g. '🌾 14M Hectares Arable Land', '🍇 2,000-Year Vineyard Terroir')".
""",
    "supermarkets_and_grocery_culture": """
--- SPECIALIZED MANDATE: SUPERMARKETS & GROCERY CULTURE ---
Explore the nation's unique supermarkets, hypermarkets, gourmet food halls, and daily grocery rituals:
* Subject Focus: Iconic domestic grocery chains and formats (hypermarkets, discounters, gourmet food halls, neighborhood convenience stores / konbini / bodegas), packaging aesthetics, specialty snack and beverage aisles, and the sheer abundance of local staples.
* Cultural Consumer Habits: Daily fresh market vs weekly bulk buying habits, fresh bakery counters (baguettes, pastries, warm bread), artisanal cheese and charcuterie stations, prepared bento/ready-meals, zero-waste initiatives, and bottle deposit return machines.
* Visual Aesthetics: Smooth eye-level steadycam glides through brightly lit, colorfully stacked grocery aisles; mouthwatering macro focus on fresh deli/bakery counters; vibrant produce misting systems; and bustling checkouts.
* Overlay Specs: "chapter_title": "GROCERY CULTURE", "fact_badge": "🛒 Supermarket quirk (e.g. '🥖 30M Daily Fresh Baguettes', '🍱 50,000 Konbini Nationwide', '🧀 1,200 AOC Cheeses on Shelf')".
""",
}

