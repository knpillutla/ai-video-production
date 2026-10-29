"""Food, Agriculture, Regional Cuisines & Culinary Culture Archetypes for Nations Documentaries.

Defines structured chapter syllabuses, 1:1 thematic visual grounding,
and strict bans on out-of-bounds imagery across culinary documentary archetypes.
"""
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
* MANDATORY CHAPTER SYLLABUS:
  1. STAPLE GRAIN BELTS & CALORIE ENGINES: Wheat, rice, or maize harvest fields. Mandatory Visual: Golden wheat plains with combine harvesters. Prohibited: Offices, empty roads.
  2. HIGH-TECH GREENHOUSES & AGRI-TECH: Automated glass hydroponics, climate-controlled farming. Mandatory Visual: Luminous green LED hydroponic bays, automated irrigation. Prohibited: Barren rocks.
  3. PASTORAL DAIRY & PROTEIN POWER: Cattle herds, grazing pastures, milking technology. Mandatory Visual: Lush green dairy pastures with grazing cows, automated milking stations. Prohibited: Shipping docks.
  4. WHOLESALE FOOD TERMINALS & EXPORT PORTS: National food distribution, refrigerated shipping containers. Mandatory Visual: Bustling wholesale food hall with crates, refrigerated container berths. Prohibited: Beaches.
  5. DOMESTIC CONSUMPTION & SELF-SUFFICIENCY: Family tables, self-sufficiency metrics, import balance. Mandatory Visual: Generous family dining table with national staples. Prohibited: Empty landscapes.
* MULTI-SHOT CADENCE: Shot 1: Wide 4K drone over agricultural subject. Shot 2: Living 5s kinetic action (harvesters rolling, workers sorting produce). Shot 3: 85mm macro detail of fresh produce/grains.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Every shot MUST depict food, crops, farms, or food logistics. Never show empty mountains, generic highways, or unrelated city skylines!
* OVERLAYS: "chapter_title": "FOOD PRODUCTION", "fact_badge": "🌾 Agri-Engine (e.g. '🚜 #1 Global Olive Oil Exporter', '🍚 82% Calorie Self-Sufficiency')".
""",

    "regional_cuisines": """
--- SPECIALIZED MANDATE: REGIONAL CUISINES (WHAT THEY EAT ACROSS DIFFERENT REGIONS) ---
* MANDATORY CHAPTER SYLLABUS:
  1. NORTHERN HEARTY TRADITIONS: Alpine stews, cured mountain meats, wood-fired bread. Mandatory Visual: Steaming cast-iron cauldron, wood-fired hearth oven, rustic dining lodge. Prohibited: Tropical beaches.
  2. SOUTHERN SUN-DRENCHED FLAVORS: Olive oils, vine-ripened tomatoes, fresh herbs, citrus. Mandatory Visual: Sunlit stone patio table laden with fresh salads, olive oil drizzled on bread. Prohibited: Snowstorms.
  3. COASTAL SEAFOOD GASTRONOMY: Daily catch, grilled fish, harbor-side tavernas. Mandatory Visual: Fisherman docking wooden boat with fresh catch, sizzling seafood pan. Prohibited: Inland grain silos.
  4. MOUNTAIN CELLAR & CHEESE TRADITIONS: Cave-aged cheeses, polenta, charcuterie. Mandatory Visual: Rustic wooden table with sliced mountain cheese and smoked meats. Prohibited: Fast food.
  5. NIGHT MARKETS & REGIONAL STREET FOOD: Bustling street carts, regional specialties, night woks. Mandatory Visual: Bustling evening street food lane, steam rising from woks. Prohibited: Generic corporate offices.
* MULTI-SHOT CADENCE: Shot 1: Wide regional landscape setting the terroir. Shot 2: Living cooking action (sizzling pan, rolling pasta, grilling over coals). Shot 3: Tactile 85mm macro of the plated dish.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Every shot MUST feature regional food, kitchens, or dining culture.
* OVERLAYS: "chapter_title": "REGIONAL PLATE", "fact_badge": "🍲 Provincial specialty (e.g. '🏔️ Alpine Fondue & Cured Ham', '🐟 Coastal Saffron Broth')".
""",

    "food_culture_rituals": """
--- SPECIALIZED MANDATE: FOOD CULTURE & DINING RITUALS ---
* MANDATORY CHAPTER SYLLABUS:
  1. THE SACRED MORNING RITUAL: Morning coffee/tea traditions, bakery visits, breakfast codes. Mandatory Visual: Sunlit historic espresso bar or traditional tea room with porcelain cups. Prohibited: Nightclubs.
  2. UNWRITTEN TABLE ETIQUETTE: Dining rules, utensil customs, courses sequence. Mandatory Visual: Elegant table setting, dignified diners observing mealtime customs. Prohibited: Fast-food drive-thrus.
  3. THE 3-HOUR SUNDAY FAMILY FEAST: Generational gathering, feast courses, shared platters. Mandatory Visual: Multi-generational family seated along long table, laughing, pouring wine. Prohibited: Solitary diners.
  4. STREET FOOD CODES & NIGHT DINING: Night market etiquette, after-work socializing. Mandatory Visual: Lively street food lane with locals gathered around communal benches. Prohibited: Empty streets.
  5. TOASTING, COMMUNICATING & DIGESTIFS: Toasting rituals, after-dinner digestive drinks, farewells. Mandatory Visual: Crystal glasses raised in synchronized toast, amber digestive bottles. Prohibited: Industrial factories.
* MULTI-SHOT CADENCE: Shot 1: Wide establishing scene of the dining venue. Shot 2: Living human interaction (pouring, toasting, serving). Shot 3: Close-up macro of glasses, dishes, or hands.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Zero empty nature or unrelated machinery. The subject is human culinary culture.
* OVERLAYS: "chapter_title": "DINING RITUAL", "fact_badge": "🍷 Food culture (e.g. '☕ Sacred Morning Espresso Rule', '🥖 3-Hour Family Lunch Ritual')".
""",

    "culinary_gastronomic_heritage": """
--- SPECIALIZED MANDATE: CULINARY HERITAGE & GASTRONOMY ---
* MANDATORY CHAPTER SYLLABUS:
  1. ANCIENT SOURDOUGH & STONE MILLING: Heritage bakeries, ancient stone mills, wood ovens. Mandatory Visual: Master baker scoring golden sourdough loaves before wood-fired oven. Prohibited: Modern factories.
  2. MULTI-CENTURY CHEESE AGING CAVES: Natural stone caves, wooden shelves of cheese wheels. Mandatory Visual: Vast subterranean stone vault lined with golden aging cheese wheels. Prohibited: Concrete parking lots.
  3. HERITAGE VINEYARDS & OAK CELLARS: Ancient cellars, oak casks, historical wine estates. Mandatory Visual: Ancient vaulted cellar with rows of aged oak barrels, crystal wine glass. Prohibited: Beer factories.
  4. CURED MEAT VAULTS & TRADITIONAL SMOKE: Curing chambers, hung hams, natural sea salt cure. Mandatory Visual: Dramatic hanging rows of prosciutto/jamon in temperature-controlled curing cellar. Prohibited: Supermarket shelves.
  5. UNESCO GASTRONOMIC RECIPES: Master chef preparation of iconic protected dishes. Mandatory Visual: Master chef hands plating iconic heritage dish with exquisite precision. Prohibited: Fast food.
* MULTI-SHOT CADENCE: Shot 1: Atmospheric wide of historic cellar/bakery. Shot 2: Living artisan craft action (brushing cheese, turning barrels, slicing ham). Shot 3: 85mm macro texture of the aged food.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Only heritage artisanal food production and UNESCO recipes.
* OVERLAYS: "chapter_title": "GASTRONOMIC HERITAGE", "fact_badge": "🧀 Artisan craft (e.g. '🧀 24-Month Cave-Aged Parmigiano', '🍷 400-Year Vineyard Terroir')".
""",

    "agriculture_farming_harvests": """
--- SPECIALIZED MANDATE: AGRICULTURE, FARMING & HARVEST SEASONS ---
* MANDATORY CHAPTER SYLLABUS:
  1. GOLDEN GRAIN BREADBASKET: Expansive wheat, barley, or oat plains during peak harvest. Mandatory Visual: Sweeping aerial drone flight over golden wheat fields with modern harvesters. Prohibited: City towers.
  2. GEOMETRIC VINEYARDS & ORCHARDS: Terraced hillsides, grape picking, stone olive groves. Mandatory Visual: Perfect geometric rows of grapevine trellises along rolling emerald hills. Prohibited: Industrial shipyards.
  3. PASTORAL VALLEYS & HERD HERITAGE: Dairy cattle, sheep pastures, alpine meadows. Mandatory Visual: Cattle grazing peacefully on lush green alpine slopes with snowcapped peaks behind. Prohibited: Concrete docks.
  4. IRRIGATION & AGRARIAN WATERWAYS: Center-pivot systems, ancient canals, mountain runoff. Mandatory Visual: Circular center-pivot irrigation rig spraying fine mist over green crop circle. Prohibited: Desert sand without water.
  5. MODERN PRECISION AGRITECH: Satellite-guided tractors, drone crop analysis, green storage silos. Mandatory Visual: Sleek modern autonomous tractor working fertile soil under golden sunrise. Prohibited: Abandoned rusty machinery.
* MULTI-SHOT CADENCE: Shot 1: Expansive 4K panoramic aerial drone flight over the farmland. Shot 2: Living agricultural kinetic motion (combine harvester cutting grain, sprayers working). Shot 3: Tactile macro close-up of ripe wheat head, plump grape cluster, or fresh soil.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly agrarian landscape, crops, livestock, and harvest machinery.
* OVERLAYS: "chapter_title": "AGRARIAN HARVEST", "fact_badge": "🚜 Agricultural wealth (e.g. '🌾 14M Hectares Arable Land', '🍇 2,000-Year Vineyard Terroir')".
""",

    "supermarkets_and_grocery_culture": """
--- SPECIALIZED MANDATE: SUPERMARKETS & GROCERY CULTURE ---
* MANDATORY CHAPTER SYLLABUS:
  1. MEGA-HYPERMARKETS & ABUNDANCE: Massive brightly lit aisles, towering shelves, organized sections. Mandatory Visual: High-angle wide steadycam glide through pristine, brightly lit hypermarket aisles. Prohibited: Street markets.
  2. FRESH BAKERY & DELI COUNTERS: Crusty baguettes, artisanal cheese displays, cured meats. Mandatory Visual: Mouthwatering counter display of warm artisan breads, sliced cheeses, and cured meats. Prohibited: Nature trails.
  3. PREPARED MEALS & BENTO CULTURE: Ready-to-eat sections, konbini meal boxes, sushi packs. Mandatory Visual: Pristinely packaged gourmet bento boxes and ready meals in refrigerated illuminated cases. Prohibited: Empty shelves.
  4. LOCAL STAPLES & SPECIALTY AISLES: Regional snack corridors, indigenous condiments, beverage walls. Mandatory Visual: Rows of colorful local snack bags, specialty sauces, and bottled regional drinks. Prohibited: Non-food hardware.
  5. RECYCLING & CHECKOUT INNOVATION: Bottle return machines, self-checkout kiosks, eco-shopping. Mandatory Visual: Modern automated bottle return reverse-vending kiosk with digital counter. Prohibited: Rubbish heaps.
* MULTI-SHOT CADENCE: Shot 1: High-angle overview of the bright supermarket interior. Shot 2: Eye-level smooth tracking shot along packed shelves. Shot 3: Macro close-up of distinctive local packaging and price tags.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly inside modern supermarkets, convenience stores (konbini), or gourmet food halls. Zero outdoor wilderness or unrelated street traffic.
* OVERLAYS: "chapter_title": "GROCERY CULTURE", "fact_badge": "🛒 Supermarket quirk (e.g. '🥖 30M Daily Fresh Baguettes', '🍱 50,000 Konbini Nationwide', '🧀 1,200 AOC Cheeses on Shelf')".
""",
}
