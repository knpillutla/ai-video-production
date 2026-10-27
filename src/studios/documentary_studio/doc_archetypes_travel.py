"""Travel, Tourism, Culture, Coastal & Nature Archetypes for Nations Documentaries."""
from __future__ import annotations
from typing import Dict

TRAVEL_ALIASES: Dict[str, str] = {
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
    "spiritual_journeys": """
--- SPECIALIZED MANDATE: SPIRITUAL JOURNEYS & SACRED SANCTUARIES ---
Focus deeply on the nation's spiritual soul, sacred pilgrimage routes, and timeless meditative shrines:
* Subject Focus: Millennia-old pilgrimage trails worn smooth by footsteps, cliff-hung monasteries, sacred river confluences, ancient stone sanctums, and temple complexes.
* Tone & Atmosphere: Deep reverence, meditative quietude, atmospheric dawn mist, incense smoke filtering through ancient cedar beams, butter lamps, and ritual bells.
* Overlay Specs: "chapter_title": "SACRED PILGRIMAGE", "fact_badge": "🪔 Spiritual heritage (e.g. '🪔 1,200-Year Pilgrimage', '⛰️ 2,400m Cliff Monastery')".
""",
    "natural_wonders": """
--- SPECIALIZED MANDATE: NATURAL WONDERS & GEOLOGICAL MARVELS ---
Showcase the nation's untamed raw wilderness, monumental geological anomalies, and living biospheres:
* Subject Focus: Colossal plunge waterfalls, glacial ice sheets, volcanic calderas, subterranean karst caverns, primordial rainforests, and dramatic sea cliffs.
* Geological Lore: Authoritative natural history narrative explaining tectonic collisions, glacial gouging, volcanic crystallization, and endemic ecological adaptations.
* Overlay Specs: "chapter_title": "NATURAL WONDER", "fact_badge": "🌋 Geological metric (e.g. '🌊 72 Glacial Waterfalls', '🌋 Active Stratovolcano')".
""",
    "architecture": """
--- SPECIALIZED MANDATE: MONUMENTAL ARCHITECTURE & CITADELS ---
Celebrate the nation's greatest architectural triumphs spanning antiquity to visionary modernism:
* Subject Focus: Classical stone temples, Gothic stone lace cathedrals, Renaissance domes, baroque imperial palaces, and gravity-defying contemporary cantilevers.
* Architectural Rigor: Discuss structural engineering, masonry material origins, golden ratio proportions, acoustic vaults, and light orientation.
* Overlay Specs: "chapter_title": "ARCHITECTURAL TRIUMPH", "fact_badge": "🏛️ Structural feat (e.g. '🏛️ 43m Free-Standing Dome', '🏰 14th-Century Fortress')".
""",
    "culture_heritage": """
--- SPECIALIZED MANDATE: LIVING CULTURE & NATIONAL SOUL ---
Immerse viewers in the living cultural heartbeat, daily philosophies, and communal rituals that define the nation:
* Subject Focus: Generational culinary rituals, folk storytelling, performing arts, seasonal harvest festivals, family reverence, and living societal values.
* Narrative Soul: Warm, human-centric storytelling exploring how ancient traditions seamlessly blend into contemporary urban life.
* Visual Aesthetics: Saturated colors, vibrant traditional textiles, golden festival lanterns, warm smiles of multi-generational families, and intimate eye-level lens framing.
* Overlay Specs: "chapter_title": "CULTURAL SOUL", "fact_badge": "🎭 Living heritage (e.g. '🏮 UNESCO Heritage Ritual', '🍲 500-Year Culinary Custom')".
""",
    "aviation_gateways": """
--- SPECIALIZED MANDATE: AVIATION GATEWAYS & MEGA-AIRPORTS ---
Explore the nation's architectural super-terminals, extreme mountain runways, and global transit crossroads:
* Subject Focus: World-class architectural airport terminals, biophilic indoor gardens and waterfalls, high-speed automated baggage grids, air traffic radar hubs, and thrilling crosswind landings.
* Engineering Scope: Showcase runway lengths, passenger capacity (50M-100M+ passengers/year), futuristic curved steel roofs, and geopolitical aviation routes.
* Visual Aesthetics: Sweeping twilight aerial glides over illuminated runways, glowing blue taxiway lights, colossal wide-body aircraft boarding, and glass skylight reflections.
* Overlay Specs: "chapter_title": "AVIATION GATEWAY", "fact_badge": "✈️ Airport metric (e.g. '🛫 85M Passengers/Year', '🛬 4,000m Cat-III Runway')".
""",
    "coastal_beaches": """
--- SPECIALIZED MANDATE: PRISTINE BEACHES & COASTAL PARADISES ---
Unveil the nation's most breathtaking turquoise shores, hidden sea coves, and dramatic coastal frontiers:
* Subject Focus: White, golden, and volcanic black sand beaches, crystalline turquoise lagoons, dramatic offshore limestone stacks, and secluded barrier reefs.
* Sensory Immersion: High temporal clarity capturing turquoise wave curl wash, sea foam ribbons on sand, palm fronds dancing in trade winds, and warm 5400K tropical daylight.
* Visual Aesthetics: Polarizing lens aerial glides over coral lagoons, intimate low-angle water-line shots, and golden hour sunset reflections across rolling ocean swells.
* Overlay Specs: "chapter_title": "COASTAL PARADISE", "fact_badge": "🏖️ Shoreline highlight (e.g. '🌊 Crystal 30m Water Clarity', '🏝️ 15km Untouched Sands')".
""",
    "luxury_resorts": """
--- SPECIALIZED MANDATE: TOP RESORTS & 5-STAR LUXURY SANCTUARIES ---
Take viewers inside the nation's most exclusive, ultra-luxury resorts, overwater villas, and private island hideaways:
* Subject Focus: World-renowned architectural retreats, private clifftop infinity pools, Michelin-starred jungle dining pavilions, personalized butler estates, and overwater hammocks.
* Aspirational Pacing: Elegant, serene, and visually lavish cinematography highlighting flawless craftsmanship, imported linen, tropical hardwoods, and panoramic horizon vistas.
* Visual Aesthetics: Golden hour champagne terraces, glowing candlelit infinity pool edges at twilight, lush private gardens, and crisp natural tropical lighting.
* Overlay Specs: "chapter_title": "LUXURY SANCTUARY", "fact_badge": "✨ 5-Star luxury (e.g. '🏊 50m Clifftop Infinity Pool', '🌟 Forbes 5-Star Winner')".
""",
    "medical_tourism": """
--- SPECIALIZED MANDATE: MEDICAL TOURISM & WORLD-CLASS HEALTHCARE ---
Investigate why millions of international patients travel to the nation for world-class surgical, dental, and wellness care:
* Subject Focus: State-of-the-art JCI-accredited smart hospitals, robotic surgery suites, dental aesthetics centers, integrative thermal mineral wellness, and cost comparisons (saving 60%-80%).
* Authority & Trust: Highlight board-certified international specialists, cutting-edge technology (Da Vinci robotics, AI diagnostics), luxury patient recovery suites, and healing hospitality.
* Visual Aesthetics: Clean, luminous architectural healthcare campuses, sterile robotic operating rooms with amber status displays, lush recovery garden terraces, and warm professional interactions.
* Overlay Specs: "chapter_title": "HEALTHCARE HUB", "fact_badge": "🏥 Medical excellence (e.g. '🩺 1.2M Global Patients/Year', '💡 75% Cost Advantage')".
""",
    "beach_towns": """
--- SPECIALIZED MANDATE: CHARMING BEACH TOWNS & SEASIDE HAVENS ---
Capture the tranquil rhythms, pastel harbors, and laid-back surf culture of the nation's most enchanting coastal towns:
* Subject Focus: Sleepy fishing harbors, pastel-painted waterfront tavernas, wooden boat docks, cobblestone promenade lanes, morning fish markets, and friendly local cafe culture.
* Narrative Vibe: Slow living, seaside escapism, fresh sea air, and the authentic charm of coastal life away from commercial mega-resorts.
* Visual Aesthetics: Morning golden hour illuminating gently bobbing wooden dories, seagulls gliding over harbor breakwaters, fresh grilled seafood with lemon, and sun-drenched cafe terraces.
* Overlay Specs: "chapter_title": "SEASIDE CHARM", "fact_badge": "⛵ Harbor rhythm (e.g. '🐟 Fresh Daily Catch Dock', '🏠 17th-Century Fishing Village')".
""",
    "tourism_guide": """
--- SPECIALIZED MANDATE: ULTIMATE NATIONAL TRAVEL & BUCKET LIST ---
Deliver the definitive, high-value visual travel guide for anyone planning an unforgettable expedition across the nation:
* Subject Focus: Top 10 must-see bucket list landmarks, regional highlight loops, high-speed rail transit logistics, local culinary specialties, and smart travel insider tips.
* Directorial Practicality: Dynamic, highly informative, and visually engaging itinerary structure that leaves viewers equipped to explore like seasoned travelers.
* Visual Aesthetics: Cinematic drone transitions linking diverse regions (from mountain citadels to bustling night markets), crisp on-screen route overlays, and breathtaking vistas.
* Overlay Specs: "chapter_title": "TRAVEL GUIDE", "fact_badge": "🎒 Travel essential (e.g. '🚆 Eurail / Shinkansen Pass', '🗓️ Best Season: May–Oct')".
""",
    "ancient_forests": """
--- SPECIALIZED MANDATE: ANCIENT FORESTS & PRIMORDIAL CANOPIES ---
Immerse viewers in the towering green cathedrals, misty moss glades, and ancient old-growth canopies of the nation:
* Subject Focus: Thousand-year-old tree giants, temperate and tropical rainforest ecosystems, endemic canopy birds, fern-lined glacial rivers, and biophilic peace.
* Sensory Depth: Komorebi sunbeams piercing emerald mist, rich binaural foley of distant bird calls and rustling leaves, damp fertile soil scents, and deep ancient silence.
* Visual Aesthetics: Slow upward crane tilts along colossal moss-crusted tree trunks, expansive top-down drone canopies undulating in mountain breezes, and macro dewdrops on ferns.
* Overlay Specs: "chapter_title": "ANCIENT FOREST", "fact_badge": "🌲 Primordial canopy (e.g. '🌳 2,000-Year Ancient Pines', '🌿 85% Forest Cover')".
""",
    "art_and_masterpieces": """
--- SPECIALIZED MANDATE: ART, MASTERPIECES & LIVING CREATORS ---
Celebrate the nation's monumental fine arts heritage, legendary museum masterpieces, and boundary-pushing creators:
* Subject Focus: Iconic classical canvas paintings, Renaissance fresco ceilings, monumental stone and bronze sculptures, historic artist ateliers, and cutting-edge contemporary galleries.
* Curatorial Precision: Explore brushstroke techniques (chiaroscuro, impasto, sfumato), historical artistic rebellions, national patron dynasties, and the philosophical soul behind masterpieces.
* Visual Aesthetics: Raking gallery directional lighting illuminating tactile oil paint textures, slow push-ins on expressive painted eyes, grand marbled museum skylight halls, and artists working in sunlit lofts.
* Overlay Specs: "chapter_title": "ARTISTIC MASTERPIECE", "fact_badge": "🎨 Fine art heritage (e.g. '🖼️ 15th-Century Renaissance Masterpiece', '🏛️ National Gallery Treasure')".
""",
    "wellness_retreats": """
--- SPECIALIZED MANDATE: WELLNESS RETREATS & HEALING SANCTUARIES ---
Immerse viewers in the nation's most rejuvenating thermal spas, holistic mountain retreats, and ancient healing traditions:
* Subject Focus: Geothermal mineral onsens, Ayurvedic healing ashrams, high-alpine medical wellness clinics, ancient Turkish hammams, and forest bathing sound pavilions.
* Sensory Atmosphere: Calming, serene, deeply restorative binaural foley of trickling mineral water, ambient temple chimes, rising thermal steam, and peaceful mountain vistas.
* Visual Aesthetics: Minimalist stone architecture, steam rising over infinity pools overlooking snowy pines or bamboo forests, fragrant herbal steam baths, and golden hour meditation decks.
* Overlay Specs: "chapter_title": "HEALING SANCTUARY", "fact_badge": "🌿 Healing retreat (e.g. '♨️ 42°C Mineral Springs', '🧘 500-Year Thermal Heritage')".
""",
    "top_20_places": """
--- SPECIALIZED MANDATE: TOP 20 PLACES COUNTDOWN (REVERSE ORDER #20 TO #1) ---
Deliver the definitive national bucket list countdown counting strictly backwards from #20 down to #1:
* RETENTION RULE (COUNT BACKWARDS): Every scene MUST count strictly backwards (#20, #19, #18... down to #01) building viral suspense towards the nation's crowning #1 landmark.
* Subject Focus: 20 most jaw-dropping wonders across the nation—ancient stone citadels, fairy-tale coastal coves, alpine glacial peaks, and historic royal palaces.
* In & Nearby Formula: Each countdown scene highlights the primary landmark plus 1 nearby hidden gem / scenic day trip.
* Visual Aesthetics: Sweeping 4K drone establishes, dynamic lighting transitions, and dramatic numbered lower-third badge overlays.
* Overlay Specs: "chapter_title": "RANK #14", "fact_badge": "📍 Bucket list (e.g. '⭐ Ranked #14 of 20', '🏆 UNESCO Masterpiece')".
""",
    "cleanest_cities_places": """
--- SPECIALIZED MANDATE: TOP CLEANEST CITIES & PRISTINE PLACES (REVERSE COUNTDOWN) ---
Showcase the nation's cleanest, most immaculate cities, spotless towns, and pristine eco-sanctuaries:
* RETENTION RULE (COUNT BACKWARDS): Count strictly in reverse sequence from lowest rank down to the crowning #1 cleanest place for maximum viewer retention.
* Subject Focus: Zero-litter streets, crystalline urban canals, pneumatic underground waste networks, spotless subway systems, biophilic architecture, and cultural cleanliness ethics (e.g. Japanese souji, Swiss municipal perfection).
* Narrative Angle: How civic pride, environmental technology, and communal habits achieved the world's highest living standards and purest air.
* Visual Aesthetics: Gleaming cobblestones, sparkling riverways with visible fish, lush vertical flower walls, sunlit spotless sidewalks, and crisp 5600K balanced daylight.
* Overlay Specs: "chapter_title": "PRISTINE HAVEN #03", "fact_badge": "🌱 Cleanliness metric (e.g. '🧹 99.8% Waste Diverted', '💧 Drinkable Municipal Tap')".
""",
    "islands_archipelagos": """
--- SPECIALIZED MANDATE: ISLANDS & SECRET ARCHIPELAGOS ---
Explore the nation's most breathtaking islands, remote archipelagos, and secluded sea sanctuaries:
* Subject Focus: Volcanic island chains, car-free fishing isles, turquoise coral atolls, rugged northern outposts, island-hopping routes, and distinct island customs.
* Directorial Atmosphere: Sun-drenched azure waters, wooden ferry arrivals, dramatic sea stacks, clifftop lighthouses, and the peaceful self-contained rhythm of island living.
* Visual Aesthetics: Expansive top-down aerials of white-sand atolls fringed by turquoise lagoons, weathered wooden dories bobbing in quiet coves, dramatic sea mist against dark volcanic cliffs, and radiant golden sunsets over open water.
* Overlay Specs: "chapter_title": "ISLAND SANCTUARY", "fact_badge": "🏝️ Island lore (e.g. '⛴️ 1,200 Off-Shore Islands', '🌊 Marine Biosphere Reserve')".
""",
    "states_and_provinces": """
--- SPECIALIZED MANDATE: STATES & PROVINCES (COMPLETE NATIONAL BREAKDOWN) ---
Deliver a comprehensive journey across every state, province, canton, or prefecture of the nation:
* Subject Focus: The distinct personality, capital city, landscape, economic engine, dialect, and cultural pride of every major administrative region.
* Comparative Directorial Structure: Dynamic pacing comparing northern mountain provinces to southern coastal realms, showcasing how diverse regional identities unite under one flag.
* Visual Aesthetics: 3D animated geographic boundary maps sweeping into 4K cinematic landscapes, regional flags, historic provincial capitals, and distinct local architecture.
* Overlay Specs: "chapter_title": "PROVINCE: BAVARIA", "fact_badge": "🗺️ Regional profile (e.g. '📍 Largest State by Area', '🏛️ Capital: Munich • Pop: 13M')".
""",
}


