"""Travel, Tourism, Culture, Coastal & Nature Archetypes for Nations Documentaries.

Defines structured chapter syllabuses, 1:1 thematic visual grounding,
and strict bans on out-of-bounds imagery across travel and landscape archetypes.
"""
from __future__ import annotations
from typing import Dict

TRAVEL_ALIASES: Dict[str, str] = {
    "tour_itinerary": "tour_itinerary", "travel_itinerary_tour": "tour_itinerary", "itinerary_tour": "tour_itinerary", "itinerary": "tour_itinerary", "itinerary_map_tour": "tour_itinerary",
    "top_places_to_visit": "top_places_to_visit", "places_to_visit": "top_places_to_visit", "top_places": "top_places_to_visit", "national_bucket_list": "top_places_to_visit",
    "top_10_cities": "top_10_cities", "top_cities": "top_10_cities", "best_cities": "top_10_cities", "cities_countdown": "top_10_cities",
    "cities": "cities", "city": "cities", "city_exploration": "cities", "deep_dive_city": "cities",
    "countries": "country_dossier", "country_dossier": "country_dossier", "country_profile": "country_dossier", "country": "country_dossier", "nations": "country_dossier",
    "spiritual_journeys": "spiritual_journeys", "spiritual_sanctuaries": "spiritual_journeys", "sacred_trails": "spiritual_journeys", "pilgrimage": "spiritual_journeys",
    "natural_wonders": "natural_wonders", "natural_history_geology": "natural_wonders", "geological_marvels": "natural_wonders", "doc_nature": "natural_wonders",
    "architecture": "architecture", "history_architecture": "architecture", "doc_architecture": "architecture", "monumental_architecture": "architecture",
    "culture_heritage": "culture_heritage", "culture": "culture_heritage", "cultural_heritage": "culture_heritage", "living_culture": "culture_heritage", "customs_traditions": "culture_heritage", "cultural_mosaic_traditions": "culture_heritage",
    "aviation_gateways": "aviation_gateways", "airports": "aviation_gateways", "mega_airports": "aviation_gateways", "international_airports": "aviation_gateways", "runways": "aviation_gateways", "aviation": "aviation_gateways",
    "coastal_beaches": "coastal_beaches", "beaches": "coastal_beaches", "top_beaches": "coastal_beaches", "best_beaches": "coastal_beaches", "secret_beaches": "coastal_beaches", "tropical_beaches": "coastal_beaches",
    "luxury_resorts": "luxury_resorts", "top_resorts": "luxury_resorts", "resorts": "luxury_resorts", "luxury_hotels": "luxury_resorts", "5_star_resorts": "luxury_resorts", "private_villas": "luxury_resorts",
    "medical_tourism": "medical_tourism", "healthcare_tourism": "medical_tourism", "wellness_tourism": "medical_tourism", "hospitals": "medical_tourism", "medical_travel": "medical_tourism",
    "beach_towns": "beach_towns", "coastal_towns": "beach_towns", "seaside_towns": "beach_towns", "surf_towns": "beach_towns", "harbor_towns": "beach_towns",
    "tourism_guide": "tourism_guide", "tourism": "tourism_guide", "travel_guide": "tourism_guide", "visitor_guide": "tourism_guide", "traveler_guide": "tourism_guide",
    "ancient_forests": "ancient_forests", "forests": "ancient_forests", "rainforests": "ancient_forests", "primordial_forests": "ancient_forests", "ancient_canopies": "ancient_forests", "deep_woods": "ancient_forests",
    "art_and_masterpieces": "art_and_masterpieces", "art": "art_and_masterpieces", "masterpieces": "art_and_masterpieces", "fine_arts": "art_and_masterpieces", "art_movements": "art_and_masterpieces", "galleries_museums": "art_and_masterpieces", "art_history": "art_and_masterpieces",
    "wellness_retreats": "wellness_retreats", "wellness": "wellness_retreats", "spa_retreats": "wellness_retreats", "thermal_spas": "wellness_retreats", "healing_retreats": "wellness_retreats", "health_retreats": "wellness_retreats", "sanctuaries": "wellness_retreats", "spa": "wellness_retreats",
    "top_20_places": "top_20_places", "top_20_tourist_places": "top_20_places", "top_20": "top_20_places", "20_places": "top_20_places", "top_20_attractions": "top_20_places",
    "cleanest_cities_places": "cleanest_cities_places", "cleanest_cities": "cleanest_cities_places", "cleanest_places": "cleanest_cities_places", "clean_cities": "cleanest_cities_places", "cleanest_towns": "cleanest_cities_places", "zero_waste_cities": "cleanest_cities_places",
    "islands_archipelagos": "islands_archipelagos", "islands": "islands_archipelagos", "island_life": "islands_archipelagos", "archipelagos": "islands_archipelagos", "remote_islands": "islands_archipelagos", "secret_islands": "islands_archipelagos", "island_escapes": "islands_archipelagos", "island_hopping": "islands_archipelagos",
    "states_and_provinces": "states_and_provinces", "states": "states_and_provinces", "provinces": "states_and_provinces", "states_provinces": "states_and_provinces", "regions_states": "states_and_provinces", "cantons": "states_and_provinces", "prefectures": "states_and_provinces", "territories": "states_and_provinces",
}

TRAVEL_DIRECTIVES: Dict[str, str] = {

    "aviation_gateways": """
--- SPECIALIZED MANDATE: AVIATION GATEWAYS & MEGA-AIRPORTS ---
* MANDATORY CHAPTER SYLLABUS:
  1. TERMINAL ARCHITECTURE & BIOPHILIC DESIGN: Curved glass roof, indoor waterfalls/gardens. Mandatory Visual: Futuristic glass-and-steel terminal concourse with natural light. Prohibited: Highways.
  2. RUNWAYS & COMMERCIAL JETLINER OPERATIONS: 4,000m Cat-III runway, widebody airliners. Mandatory Visual: Boeing 777/A350 on final approach or taxiing along runway with heat shimmer. Prohibited: Beaches.
  3. AIR TRAFFIC RADAR & FLIGHT CONTROL: Tower operations, radar systems. Mandatory Visual: Sleek air traffic control tower with sweeping panoramic view of active tarmac. Prohibited: Malls.
  4. AIR CARGO APRONS & FREIGHT HANDLING: Freight jumbo jets, automated cargo pallet loaders. Mandatory Visual: Cargo freighters parked on illuminated apron with cargo loaders operating. Prohibited: Nature trails.
  5. TRANSIT EXPERIENCE & GLOBAL FLIGHT HUBS: Departures concourse, flight information boards. Mandatory Visual: Luminous international departures concourse with travelers and flight boards. Prohibited: Dirt roads.
* MULTI-SHOT CADENCE: Shot 1: Wide 4K drone of airport complex. Shot 2: Living 5s kinetic aircraft taxiing. Shot 3: Macro optical focus on runway touchdown markings or control tower radar.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly airport runways, passenger jetliners, air traffic towers, and terminal concourses. Zero empty countryside or unrelated city traffic.
* OVERLAYS: "chapter_title": "AVIATION GATEWAY", "fact_badge": "✈️ Airport metric (e.g. '🛫 85M Passengers/Year', '🛬 4,000m Cat-III Runway')".
""",

    "coastal_beaches": """
--- SPECIALIZED MANDATE: PRISTINE BEACHES & COASTAL PARADISES ---
* MANDATORY CHAPTER SYLLABUS:
  1. TURQUOISE LAGOONS & CORAL REEFS: Crystalline shallow waters, offshore coral reef barrier. Mandatory Visual: High-angle polarizing drone glide over turquoise lagoon with breaking white reef curl. Prohibited: Container ports.
  2. POWDER SAND SHORES & COASTAL PALMS: Vast stretches of untouched white or golden sand. Mandatory Visual: Sweeping wide view of pristine curved beach with emerald palm trees swaying. Prohibited: Highways.
  3. DRAMATIC SEA STACKS & COASTAL CLIFFS: Offshore limestone monoliths, ocean wave impact. Mandatory Visual: Towering weathered sea stacks rising sheer from churning turquoise ocean waves. Prohibited: Cities.
  4. HIDDEN SEA COVES & MARINE ARCHES: Sheltered emerald coves, natural rock arches. Mandatory Visual: Tranquil secluded cove with emerald water lapping against golden sea arch. Prohibited: Factories.
  5. TWILIGHT HORIZON & OCEAN SWELLS: Golden hour reflections across rolling swells. Mandatory Visual: Cinematic sunset over tranquil ocean shoreline with wet sand mirror reflections. Prohibited: Commercial malls.
* MULTI-SHOT CADENCE: Shot 1: Sweeping 4K aerial drone over coastline. Shot 2: Living wave curl and wash onto wet sand. Shot 3: Macro glistening sea foam ribbons and polished shells.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly pristine beaches, lagoons, sea cliffs, and marine shores. Zero industrial ports or inland mountains.
* OVERLAYS: "chapter_title": "COASTAL PARADISE", "fact_badge": "🏖️ Shoreline highlight (e.g. '🌊 Crystal 30m Water Clarity', '🏝️ 15km Untouched Sands')".
""",

    "luxury_resorts": """
--- SPECIALIZED MANDATE: TOP RESORTS & 5-STAR LUXURY SANCTUARIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. OVERWATER VILLAS & PRIVATE PIERS: Architectural villas on stilts over turquoise water. Mandatory Visual: Elegant wooden overwater villa with private sundeck and ladder into crystal lagoon. Prohibited: Budget motels.
  2. CANTILEVERED CLIFFTOP INFINITY POOLS: Edge pools meeting the ocean horizon at dusk. Mandatory Visual: 50-meter mirror infinity pool with water spilling seamlessly into twilight sea vista. Prohibited: Public city pools.
  3. TROPICAL BIOPHILIC COURTYARDS: Private villa gardens, outdoor rain showers, teak decks. Mandatory Visual: Lush private garden pavilion with tropical flora and stone relaxation terrace. Prohibited: Concrete alleys.
  4. MICHELIN-STARRED JUNGLE DINING: Open-air dining pavilion under the stars. Mandatory Visual: Candlelit timber dining pavilion suspended over jungle canopy with wine glasses. Prohibited: Fast food.
  5. HOLISTIC OVERWATER SPA PAVILIONS: Peaceful treatment rooms, trickling water. Mandatory Visual: Teak massage pavilion with glass floor viewing swimming marine life beneath. Prohibited: Gym locker rooms.
* MULTI-SHOT CADENCE: Shot 1: Expansive drone vista over luxury sanctuary. Shot 2: Living water ripples in infinity pool or gentle linen sway. Shot 3: Macro 85mm optical bokeh on champagne flute or teak grain.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly ultra-luxury resort architecture, infinity pools, and private villas. Zero commercial sprawl or crowded public beaches.
* OVERLAYS: "chapter_title": "LUXURY SANCTUARY", "fact_badge": "✨ 5-Star luxury (e.g. '🏊 50m Clifftop Infinity Pool', '🌟 Forbes 5-Star Winner')".
""",

    "architecture": """
--- SPECIALIZED MANDATE: MONUMENTAL ARCHITECTURE & CITADELS ---
* MANDATORY CHAPTER SYLLABUS:
  1. CLASSICAL ANTIQUITY & STONE TEMPLES: Colonnades, ancient marble arches, amphitheaters. Mandatory Visual: Weathered marble columns of classical temple standing against deep blue sky. Prohibited: Modern plastic.
  2. GOTHIC STONE LACE & CATHEDRAL SPIRES: Vaulted stone arches, stained-glass rose windows. Mandatory Visual: Towering gothic cathedral facade with intricate stone carved lace and slate spires. Prohibited: Concrete boxes.
  3. RENAISSANCE DOMES & BAROQUE PALACES: Golden-ratio symmetry, grand palace courtyards. Mandatory Visual: Symmetrical terracotta dome rising above historic palace quadrangle and fountains. Prohibited: Factories.
  4. CONTEMPORARY CANTILEVERS & GLASS MARVELS: Futuristic museums, dynamic bridge towers. Mandatory Visual: Sweeping architectural view of futuristic cantilevered titanium and glass cultural pavilion. Prohibited: Old ruins.
  5. VERNACULAR STONEWORK & LIVING PATINA: Weathered stone cloisters, ancient roof tiles. Mandatory Visual: Intimate sunlit stone cloister arcade with morning sunbeams illuminating carved arches. Prohibited: Commercial strip malls.
* MULTI-SHOT CADENCE: Shot 1: Monumental wide architectural drone establishing geometry. Shot 2: Slow crane glide along facade relief. Shot 3: Macro 85mm optical bokeh on carved stonework or structural joint.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly world-class monumental architecture. Zero ordinary suburban houses or empty nature without structures.
* OVERLAYS: "chapter_title": "ARCHITECTURAL TRIUMPH", "fact_badge": "🏛️ Structural feat (e.g. '🏛️ 43m Free-Standing Dome', '🏰 14th-Century Fortress')".
""",

    "ancient_forests": """
--- SPECIALIZED MANDATE: ANCIENT FORESTS & PRIMORDIAL CANOPIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. PRIMORDIAL GIANTS & OLD-GROWTH TRUNKS: Thousand-year-old tree giants, mossy root systems. Mandatory Visual: Monumental upward crane tilt along colossal moss-crusted tree trunk into cathedral canopy. Prohibited: Deforested clearings.
  2. KOMOREBI SUNBEAMS & MISTY GLADES: Morning mist filtering golden daylight rays. Mandatory Visual: Radiant golden sunbeams piercing emerald morning mist over lush fern-carpeted forest floor. Prohibited: Paved parking lots.
  3. GLACIAL RIVERS & MOSSY BOULDER STREAMS: Pristine mountain streams flowing through ferns. Mandatory Visual: Crystal clear river tumbling over mossy granite boulders beneath ancient tree ferns. Prohibited: Concrete culverts.
  4. CANOPY BIODIVERSITY & ANCIENT FLORA: Lichen, wild orchids, native canopy birds. Mandatory Visual: Native bird perched on mossy branch among flowering wild canopy orchids. Prohibited: Caged animals.
  5. UNDULATING PRIMORDIAL RIDGELINES: Vast unbroken ancient forest stretching to horizons. Mandatory Visual: Sweeping high-altitude aerial drone shot of endless undulating emerald forest canopy. Prohibited: Logging trucks.
* MULTI-SHOT CADENCE: Shot 1: Sweeping top-down aerial canopy vista. Shot 2: Living water ripples in forest stream or swaying ferns. Shot 3: 85mm macro dewdrop on emerald moss or textured tree bark.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly ancient old-growth forests, mossy glades, and canopy ecosystems. Zero urban elements or timber machinery.
* OVERLAYS: "chapter_title": "ANCIENT FOREST", "fact_badge": "🌲 Primordial canopy (e.g. '🌳 2,000-Year Ancient Pines', '🌿 85% Forest Cover')".
""",

    "islands_archipelagos": """
--- SPECIALIZED MANDATE: ISLANDS & SECRET ARCHIPELAGOS ---
* MANDATORY CHAPTER SYLLABUS:
  1. ARCHIPELAGO OVERVIEW & TURQUOISE PASSAGES: Emerald island chains scattered across cobalt seas. Mandatory Visual: Sweeping high-altitude aerial drone panorama of emerald volcanic islands in turquoise sea. Prohibited: Landlocked plains.
  2. VOLCANIC HEADLANDS & BLACK SAND COVES: Rugged sea cliffs, volcanic blowholes, sea arches. Mandatory Visual: Sheer volcanic black cliffs meeting churning ocean waves with dramatic sea arch. Prohibited: Urban highways.
  3. TRADITIONAL ISLAND VILLAGES & WATERFRONT DOCKS: Pastel stone cottages, fishing dories. Mandatory Visual: Sheltered island harbor with colorful wooden boats bobbing along pastel quayside. Prohibited: Modern factories.
  4. REMOTE OFFSHORE CORAL ATOLLS: Untouched sandy atolls, barrier reefs, marine life. Mandatory Visual: Pristine circular coral atoll with shallow luminous turquoise center and white sand rim. Prohibited: Large cruise ships.
  5. ISOLATED LIGHTHOUSE & TWILIGHT RETREAT: Solitary lighthouse on rocky promontory at dusk. Mandatory Visual: Solitary stone lighthouse atop craggy island bluff with beacon flashing at blue hour. Prohibited: Suburbs.
* MULTI-SHOT CADENCE: Shot 1: High-altitude aerial archipelago overview. Shot 2: Kinetic ocean swells breaking over reef or ferry gliding into dock. Shot 3: Macro textured volcanic stone or weathered nautical rope.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly islands, archipelagos, coastal reefs, and maritime harbors. Zero landlocked inland cities.
* OVERLAYS: "chapter_title": "ISLAND SANCTUARY", "fact_badge": "🏝️ Archipelago metric (e.g. '🏝️ 1,192 Coral Islands', '⛵ Population: 340 Islanders')".
""",

    "spiritual_journeys": """
--- SPECIALIZED MANDATE: SPIRITUAL JOURNEYS & SACRED SANCTUARIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. ANCIENT PILGRIMAGE TRAILS: Millennia-old stone paths worn smooth by footsteps through mist. Mandatory Visual: Ancient mossy stone staircase ascending through misty mountain cedar grove. Prohibited: Modern traffic.
  2. CLIFF-HUNG MONASTERIES: Perched sanctuaries carved into granite walls. Mandatory Visual: Whitewashed monastery clinging to sheer vertical cliff face with prayer flags. Prohibited: Industrial plants.
  3. SACRED TEMPLE SANCTUMS & BUTTER LAMPS: Inner sanctums, incense smoke, gold leaf relief. Mandatory Visual: Vaulted wooden temple interior with golden Buddha/deity illuminated by butter lamps. Prohibited: Strip malls.
  4. SACRED WATER CONFLUENCES & ABLUTIONS: Holy river ghats, temple purification fountains. Mandatory Visual: Pilgrim hands cupping crystal water from ancient carved stone dragon fountain. Prohibited: Public swimming pools.
  5. MEDITATIVE TWILIGHT & TEMPLE BELLS: Sunset meditation halls, ringing bronze bell resonance. Mandatory Visual: Monumental bronze temple bell silhouette against crimson mountain sunset. Prohibited: Neon city signs.
* MULTI-SHOT CADENCE: Shot 1: Atmospheric wide of sacred mountain sanctuary. Shot 2: Living incense curl or fluttering prayer flags. Shot 3: Macro 85mm focus on carved deity relief or aged bell surface.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly sacred shrines, pilgrimage routes, monasteries, and spiritual architecture.
* OVERLAYS: "chapter_title": "SACRED PILGRIMAGE", "fact_badge": "🪔 Spiritual heritage (e.g. '🪔 1,200-Year Pilgrimage', '⛰️ 2,400m Cliff Monastery')".
""",

    "natural_wonders": """
--- SPECIALIZED MANDATE: NATURAL WONDERS & GEOLOGICAL MARVELS ---
* MANDATORY CHAPTER SYLLABUS:
  1. MONUMENTAL PLUNGE WATERFALLS: Colossal waterfalls plunging into sheer canyons. Mandatory Visual: Wall-to-wall 4K aerial drone shot of roaring plunge waterfall with mist plume and rainbow. Prohibited: Concrete dams.
  2. ACTIVE VOLCANIC CALDERAS & STEAM FIELDS: Craggy craters, sulfur vents, glowing lava vents. Mandatory Visual: Dramatic bird's-eye view looking directly into steaming turquoise volcanic crater lake. Prohibited: Suburban lawns.
  3. GLACIAL ICE SHEETS & BLUE ICE CAVERNS: Ancient glaciers, crystalline turquoise ice caves. Mandatory Visual: Deep blue translucent cathedral arch inside ancient glacial ice cave with melting drips. Prohibited: City roads.
  4. SUBTERRANEAN KARST CAVES & STALACTITES: Giant limestone caverns, underground rivers. Mandatory Visual: Colossal underground karst cavern illuminated by natural sinkhole sunbeam. Prohibited: Subways.
  5. DRAMATIC SHEER OCEAN PRECIPICES: Vertical oceanic cliffs buffeted by crashing waves. Mandatory Visual: 300-meter vertical sea cliffs meeting raging ocean surf under dramatic storm clouds. Prohibited: Sandy beach loungers.
* MULTI-SHOT CADENCE: Shot 1: Monumental wide establishing the extreme geological scale. Shot 2: Living fluid kinematics (roaring cascade impact, swirling volcanic steam). Shot 3: Macro crystalline ice or layered tectonic strata.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly untamed monumental natural wonders. Zero modern human structures or commercial clutter.
* OVERLAYS: "chapter_title": "NATURAL WONDER", "fact_badge": "🌋 Geological metric (e.g. '🌊 72 Glacial Waterfalls', '🌋 Active Stratovolcano')".
""",

    "culture_heritage": """
--- SPECIALIZED MANDATE: LIVING CULTURE & NATIONAL SOUL ---
* MANDATORY CHAPTER SYLLABUS:
  1. ANCIENT TRADITIONS IN DAILY LIFE: Living heritage customs observed in modern squares. Mandatory Visual: Town square where locals practice centuries-old communal rituals in traditional clothing. Prohibited: Sterile offices.
  2. SACRED CEREMONIES & FESTIVAL COSTUMES: Intricate embroidered garments, ceremonial headpieces. Mandatory Visual: Colorful close-medium portrait of cultural performer in elaborate traditional regalia. Prohibited: Modern t-shirts.
  3. GENERATIONAL ARTISAN GUILDS: Master apprenticeships, pottery, weaving, metalcraft. Mandatory Visual: Elderly master artisan guiding young apprentice hands at traditional pottery wheel. Prohibited: Industrial factories.
  4. COMMUNITY RITUALS & HARVEST FEASTS: Festive communal banquet, traditional music. Mandatory Visual: Long wooden table in village square laden with celebratory dishes under festive lanterns. Prohibited: Empty rooms.
  5. LIVING CULTURAL RESILIENCE TODAY: How young generations celebrate ancestral heritage. Mandatory Visual: Vibrant youth group performing energetic traditional dance with proud expressions. Prohibited: Generic classrooms.
* MULTI-SHOT CADENCE: Shot 1: Wide cultural gathering or historic town backdrop. Shot 2: Living cultural action (dance spin, artisan tool work). Shot 3: 85mm macro on handcrafted textiles or ceremonial ornaments.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly human culture, traditional festivals, crafts, and living heritage.
* OVERLAYS: "chapter_title": "CULTURAL SOUL", "fact_badge": "🎭 Living heritage (e.g. '🏮 UNESCO Heritage Ritual', '🍲 500-Year Culinary Custom')".
""",

    "medical_tourism": """
--- SPECIALIZED MANDATE: MEDICAL TOURISM & WORLD-CLASS HEALTHCARE ---
* MANDATORY CHAPTER SYLLABUS:
  1. JCI-ACCREDITED SMART HOSPITAL CAMPUSES: State-of-the-art architectural medical complexes. Mandatory Visual: Luminous glass-and-steel architectural facade of world-class international hospital. Prohibited: Rundown clinics.
  2. ROBOTIC SURGERY & HIGH-TECH INNOVATION: Da Vinci surgical robots, digital imaging suites. Mandatory Visual: Spotless operating theater with multi-arm robotic surgery system and amber digital displays. Prohibited: Nature trails.
  3. DENTAL AESTHETICS & HIGH-PRECISION CLINICS: Advanced 3D scanning, ceramic milling. Mandatory Visual: High-end private dental clinic suite with panoramic city skyline view and 3D digital scanner. Prohibited: Crowded waiting rooms.
  4. INTEGRATIVE THERMAL WELLNESS & RECOVERY: Thermal mineral rehabilitation, recovery spas. Mandatory Visual: Peaceful therapeutic mineral bath pavilion surrounded by private recovery gardens. Prohibited: Public pools.
  5. VIP PATIENT SUITES & HEALING HOSPITALITY: 5-star recovery suites, personalized care. Mandatory Visual: Luxury private hospital recovery suite with hardwood floors, sofa, and floor-to-ceiling windows. Prohibited: Slums.
* MULTI-SHOT CADENCE: Shot 1: Wide architectural campus shot. Shot 2: Living precision medical technology in action. Shot 3: Macro optical focus on robotic arm or digital diagnostic screen.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly high-tech medical facilities, robotic suites, recovery gardens, and clinical campuses.
* OVERLAYS: "chapter_title": "HEALTHCARE HUB", "fact_badge": "🏥 Medical excellence (e.g. '🩺 1.2M Global Patients/Year', '💡 75% Cost Advantage')".
""",

    "beach_towns": """
--- SPECIALIZED MANDATE: CHARMING BEACH TOWNS & SEASIDE HAVENS ---
* MANDATORY CHAPTER SYLLABUS:
  1. PASTEL HARBOR & WOODEN FISHING BOATS: Colorful waterfront houses, bobbing boats. Mandatory Visual: Pastel-painted seaside town houses curving around sheltered harbor with wooden dories. Prohibited: Mega-resorts.
  2. COBBLESTONE PROMENADES & CAFE CULTURE: Waterfront promenade lanes, sun-drenched cafes. Mandatory Visual: Quayside cafe terrace with sun umbrellas and locals sipping coffee beside the water. Prohibited: Highways.
  3. MORNING FISH DOCKS & SEASIDE MARKETS: Fresh daily catch sold directly from boats. Mandatory Visual: Quayside wooden table with glistening fresh fish, lemon crates, and friendly fishermen. Prohibited: Supermarkets.
  4. SECLUDED SURF BREAKS & COASTAL COVES: Golden hour waves breaking along rocky point. Mandatory Visual: Surfer walking along quiet sandy beach path toward gentle peeling waves. Prohibited: Concrete factories.
  5. TWILIGHT HARBOR LIGHTS & SEAFOOD TAVERNAS: Lanterns reflecting in dark harbor waters. Mandatory Visual: Waterfront tavern glowing warmly with golden lanterns as fishing boats rest at dock. Prohibited: Urban skyscrapers.
* MULTI-SHOT CADENCE: Shot 1: Wide panoramic drone over harbor and town. Shot 2: Living harbor movement (boats bobbing, cafe patrons). Shot 3: Macro fresh grilled seafood or weathered mooring bollard.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly quaint seaside villages, fishing harbors, and coastal tavernas. Zero industrial ports or inland terrain.
* OVERLAYS: "chapter_title": "SEASIDE CHARM", "fact_badge": "⛵ Harbor rhythm (e.g. '🐟 Fresh Daily Catch Dock', '🏠 17th-Century Fishing Village')".
""",

    "tourism_guide": """
--- SPECIALIZED MANDATE: ULTIMATE NATIONAL TRAVEL & BUCKET LIST ---
* MANDATORY CHAPTER SYLLABUS:
  1. THE #1 MUST-SEE CROWN JEWEL: The nation's single most iconic, world-famous monument. Mandatory Visual: Hero 4K aerial drone shot of the nation's crowning landmark under pristine lighting. Prohibited: Generic malls.
  2. HIGH-SPEED TRANSIT & EXPLORATION LOOPS: Bullet trains linking major regions effortlessly. Mandatory Visual: Sleek high-speed train gliding past scenic mountains and picturesque countryside. Prohibited: Dirt tracks.
  3. CULTURAL CAPITAL & HISTORIC QUARTERS: Ancient city lanes, historic plazas, street food. Mandatory Visual: Vibrant historic old town square with cobblestones, street vendors, and heritage facades. Prohibited: Industrial complexes.
  4. NATURAL WILDERNESS EXPEDITION: Peak alpine vista, national park, or glacial lake. Mandatory Visual: Majestic panoramic viewpoint over turquoise alpine lake and rugged peaks. Prohibited: Traffic jams.
  5. COASTAL RETREAT & SUNSET CLIMAX: Ocean shoreline, beach sanctuary, or seaside fortress. Mandatory Visual: Breathtaking golden hour sunset over tranquil coastal beach with sea cliffs. Prohibited: Dull suburbs.
* MULTI-SHOT CADENCE: Shot 1: Wide scenic overview. Shot 2: Kinetic travel motion (train moving, footsteps on path). Shot 3: Low-angle architectural or natural landmark detail.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Every shot must showcase an authoritative, top-tier travel destination. Zero mundane infrastructure.
* OVERLAYS: "chapter_title": "TRAVEL GUIDE", "fact_badge": "🎒 Travel essential (e.g. '🚆 Eurail / Shinkansen Pass', '🗓️ Best Season: May–Oct')".
""",

    "art_and_masterpieces": """
--- SPECIALIZED MANDATE: ART, MASTERPIECES & LIVING CREATORS ---
* MANDATORY CHAPTER SYLLABUS:
  1. NATIONAL MUSEUM OF FINE ARTS: Grand palatial gallery, marbled floors, skylit halls. Mandatory Visual: Expansive marbled museum hall with classical paintings in gilded frames and visitors. Prohibited: Office cubicles.
  2. RENAISSANCE FRESCOES & CEILING VAULTS: Monumental religious frescoes, gold leaf leafing. Mandatory Visual: Upward camera gaze at soaring baroque frescoed ceiling with intricate biblical figures. Prohibited: Modern billboards.
  3. SCULPTURE & MONUMENTAL MARBLE: Masterpiece marble statues, chisel craftsmanship. Mandatory Visual: Dramatic raking light across museum marble sculpture capturing chiseled muscle anatomy. Prohibited: Plastic toys.
  4. MASTER ATELIERS & ARTISAN OIL PAINTERS: Living artists in sunlit historic lofts. Mandatory Visual: Artist palette laden with rich oil colors and sable brushes before large oil canvas. Prohibited: Factories.
  5. MODERN GALLERIES & BOUNDARY-PUSHING ART: Contemporary installations, titanium architecture. Mandatory Visual: High-ceilinged contemporary white-cube gallery with bold modern sculpture. Prohibited: Street graffiti.
* MULTI-SHOT CADENCE: Shot 1: Wide establishing of museum hall/atelier. Shot 2: Slow push-in toward masterpiece canvas. Shot 3: 85mm macro of textured oil impasto brushstrokes or carved stone.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly fine art galleries, masterpieces, sculptures, and artists at work. Zero outdoor wilderness or unrelated commerce.
* OVERLAYS: "chapter_title": "ARTISTIC MASTERPIECE", "fact_badge": "🎨 Fine art heritage (e.g. '🖼️ 15th-Century Renaissance Masterpiece', '🏛️ National Gallery Treasure')".
""",

    "wellness_retreats": """
--- SPECIALIZED MANDATE: WELLNESS RETREATS & HEALING SANCTUARIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. NATURAL GEOTHERMAL ONSENS & MINERAL SPRINGS: Steaming outdoor stone pools among pines. Mandatory Visual: Steaming outdoor natural stone mineral spring pool surrounded by snowy evergreen pines. Prohibited: Crowded waterparks.
  2. ALPINIC MEDICAL WELLNESS CLINICS: Architectural healing sanatoriums in mountain air. Mandatory Visual: Minimalist timber-and-glass wellness lodge with outdoor terrace overlooking alpine peaks. Prohibited: Hospitals.
  3. ANCIENT HERBAL HAMMAMS & STEAM VAULTS: Dome skylights, marble slabs, eucalyptus steam. Mandatory Visual: Ancient domed Turkish hammam with shafts of light piercing rising steam over warm marble. Prohibited: Plastic showers.
  4. FOREST BATHING SOUND PAVILIONS: Teak meditation decks nestled in bamboo groves. Mandatory Visual: Suspended wooden meditation deck nestled deep in lush bamboo forest with bronze singing bowl. Prohibited: City traffic.
  5. SUNSET YOGA & HOLISTIC REJUVENATION: Open-air wooden deck at golden hour. Mandatory Visual: Silhouette of meditators on clifftop timber deck overlooking tranquil sea at sunset. Prohibited: Shopping centers.
* MULTI-SHOT CADENCE: Shot 1: Wide tranquil establishing of sanctuary landscape. Shot 2: Living water ripples or rising thermal steam plumes. Shot 3: Macro 85mm focus on smooth hot stones, bamboo spout, or herbal tea.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly serene wellness retreats, natural mineral springs, and peaceful meditation pavilions.
* OVERLAYS: "chapter_title": "HEALING SANCTUARY", "fact_badge": "🌿 Healing retreat (e.g. '♨️ 42°C Mineral Springs', '🧘 500-Year Thermal Heritage')".
""",

    "top_20_places": """
--- SPECIALIZED MANDATE: TOP 20 PLACES COUNTDOWN (REVERSE ORDER #20 TO #1) ---
* RETENTION RULE (COUNT BACKWARDS): Every scene MUST count strictly backwards (#20, #19, #18... down to #01) building viral suspense towards the nation's crowning #1 landmark!
* SCENE FORMULA: Attraction atmosphere + #1 iconic hero landmark + nearby surrounding hidden gem.
* MANDATORY VISUAL: Hero wide 4K aerial drone shot of that specific landmark at its best natural lighting.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Never show a landmark that does not match the rank and chapter title!
* OVERLAYS: "chapter_title": "RANK #[XX] • [LANDMARK NAME]", "fact_badge": "🏛️ UNESCO World Heritage / National Wonder".
""",

    "cleanest_cities_places": """
--- SPECIALIZED MANDATE: CLEANEST CITIES & ZERO-WASTE COMMUNITIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. SPOTLESS METROPOLITAN BOULEVARDS: Pristine streets, spotless pavements, electric trams. Mandatory Visual: Sunlit modern urban boulevard with spotless stone paving, flower planters, and quiet tram. Prohibited: Litter, graffiti.
  2. ROBOTIC & AUTOMATED SWEEPING SYSTEMS: Autonomous street cleaning machines. Mandatory Visual: Sleek compact municipal street-washing vehicle cleaning pavement with fine water spray. Prohibited: Rundown alleys.
  3. ADVANCED ZERO-WASTE SORTING HUBS: High-tech recycling facilities, automated optical sorters. Mandatory Visual: Ultra-clean, modern automated recycling facility with colorful sorting bins. Prohibited: Open landfills.
  4. BIOPHILIC URBAN PARKS & CLEAN WATERWAYS: Crystal clear urban canals, lush city gardens. Mandatory Visual: Pristine clear city canal with swans gliding past manicured flower-lined banks. Prohibited: Murky sludge.
  5. SUSTAINABLE GREEN ARCHITECTURE: Living vertical gardens, solar-powered civic buildings. Mandatory Visual: Modern residential tower draped in lush green vertical foliage and solar glass panels. Prohibited: Smog, smokestacks.
* MULTI-SHOT CADENCE: Shot 1: Expansive 4K drone shot over gleaming clean city skyline. Shot 2: Eye-level tracking shot along pristine spotless street. Shot 3: Macro focus on clear canal water or blooming planters.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly spotless, highly organized urban streets, green parks, and recycling hubs. Zero clutter or decay.
* OVERLAYS: "chapter_title": "CLEANEST METROPOLIS", "fact_badge": "🌿 Eco-Standard (e.g. '🌱 92% Waste Recycled', '💧 #1 Drinking Water Purity')".
""",

    "states_and_provinces": """
--- SPECIALIZED MANDATE: STATES & PROVINCES EXPLORATION TOUR ---
* MANDATORY CHAPTER SYLLABUS:
  Gemini must systematically journey through the nation's primary states/provinces/regions in geographic sequence:
  - Each chapter represents ONE distinct state/province, highlighting its capital, signature landscape, and unique culture.
  - Mandatory Visual: The state's crowning natural or architectural landmark clearly labeled on screen.
  - Prohibited: Mixing landmarks from different provinces in the same chapter!
* MULTI-SHOT CADENCE: Shot 1: Regional aerial establishing shot. Shot 2: Cultural or natural action within that state. Shot 3: Landmark architectural detail.
* OVERLAYS: "chapter_title": "STATE OF [REGION NAME]", "fact_badge": "📍 Regional Capital & Stats".
""",
}
