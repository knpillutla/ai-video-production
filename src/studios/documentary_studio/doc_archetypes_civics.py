"""Civics, History, Governance & Leadership Archetypes for Nations Documentaries.

Defines structured chapter syllabuses, 1:1 thematic visual grounding,
and strict bans on out-of-bounds imagery across civic and historical archetypes.
"""
from __future__ import annotations
from typing import Dict
from src.studios.documentary_studio.doc_country_syllabus import build_country_syllabus_directive

CIVICS_ALIASES: Dict[str, str] = {
    "major_projects": "major_projects", "engineering_marvels": "major_projects", "megastructures": "major_projects", "infrastructure": "major_projects",
    "history": "history", "ancient_history_dynasties": "history", "deep_history": "history", "ancient_civilizations_history": "history",
    "evolution": "evolution", "modern_evolution_transformation": "evolution", "future_evolution": "evolution", "modern_evolution": "evolution",
    "turning_points": "turning_points", "major_events": "turning_points", "defining_moments": "turning_points", "historic_crises": "turning_points", "historical_events": "turning_points",
    "elected_leaders": "elected_leaders", "presidents": "elected_leaders", "prime_ministers": "elected_leaders", "history_of_presidents": "elected_leaders", "political_leaders": "elected_leaders", "rulers": "elected_leaders", "elected_heads": "elected_leaders",
    "wealthy_dynasties": "wealthy_dynasties", "rich_families": "wealthy_dynasties", "ultra_rich_families": "wealthy_dynasties", "billionaires": "wealthy_dynasties", "dynasties": "wealthy_dynasties", "wealthy_families": "wealthy_dynasties", "old_money": "wealthy_dynasties",
    "music_and_dance": "music_and_dance", "music_dance": "music_and_dance", "music": "music_and_dance", "dance": "music_and_dance", "traditional_music": "music_and_dance", "folk_dance": "music_and_dance", "music_traditions": "music_and_dance", "classical_music": "music_and_dance",
    "cinema_and_film_industry": "cinema_and_film_industry", "movie_history": "cinema_and_film_industry", "cinema_history": "cinema_and_film_industry", "film_history": "cinema_and_film_industry", "film_industry": "cinema_and_film_industry", "cinema_culture": "cinema_and_film_industry", "film_heritage": "cinema_and_film_industry", "regional_cinema": "cinema_and_film_industry", "bollywood_tollywood": "cinema_and_film_industry", "cinema": "cinema_and_film_industry", "movies": "cinema_and_film_industry",
    "major_industries_manufacturing": "major_industries_manufacturing", "industries": "major_industries_manufacturing", "manufacturing": "major_industries_manufacturing", "industrial_powerhouse": "major_industries_manufacturing", "factories": "major_industries_manufacturing", "heavy_industry": "major_industries_manufacturing", "industrial_giants": "major_industries_manufacturing", "industrial_hub": "major_industries_manufacturing",
    "country_dossier": "country_dossier", "country_profile": "country_dossier", "country_almanac": "country_dossier", "country_information": "country_dossier",
}

CIVICS_DIRECTIVES: Dict[str, str] = {

    "major_projects": """
--- SPECIALIZED MANDATE: MAJOR PROJECTS & MEGASTRUCTURES ---
* MANDATORY CHAPTER SYLLABUS:
  1. MONUMENTAL BRIDGES & WATER CROSSINGS: Trans-continental suspension bridges, sea-crossing viaducts. Mandatory Visual: Symmetrical towers of colossal suspension bridge with vehicles crossing. Prohibited: Suburbs.
  2. UNDERSEA TUNNELS & HIGH-SPEED TRANSIT: Mega-tunnels bored through granite or beneath oceans. Mandatory Visual: High-speed electric train exiting illuminated mountain tunnel portal. Prohibited: Bare trails.
  3. HYDROELECTRIC DAMS & CLEAN MEGA-POWER: Gravity dams, massive concrete spillways. Mandatory Visual: Monumental concrete dam with roaring white water spillway and turbine hall. Prohibited: Dry rocks.
  4. DEEPWATER HARBOR TERMINALS: Automated maritime ports, gantry cranes. Mandatory Visual: High-altitude aerial drone shot of massive container terminal and freighters. Prohibited: Remote beaches.
  5. AEROSPACE LAUNCHPADS & MEGA-TELESCOPES: Spaceports, deep-space antennae arrays. Mandatory Visual: Colossal rocket launch assembly tower on coastal pad under blue sky. Prohibited: Street markets.
* MULTI-SHOT CADENCE: Shot 1: Wide geometric aerial establishing immense scale. Shot 2: Kinetic operational motion (train moving, water discharging, cranes lifting). Shot 3: Macro structural rivet/steel engineering detail.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Every shot MUST feature colossal engineering megastructures. Zero empty wilderness.
* OVERLAYS: "chapter_title": "ENGINEERING MARVEL", "fact_badge": "🏗️ Concrete stats (e.g. '🚆 350 km/h Network', '⚡ 22.5 GW Capacity')".
""",

    "history": """
--- SPECIALIZED MANDATE: DEEP HISTORY & FOUNDING DYNASTIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. ANCIENT TRIBAL FOUNDATIONS & MEGALITHS: Prehistoric foundations, ancient stone megaliths. Mandatory Visual: Ancient weathered stone monoliths in dawn mist with golden sunbeams. Prohibited: Modern glass buildings.
  2. THE FOUNDING MONARCHY & GOLDEN AGE: Imperial palaces, throne rooms, royal seals. Mandatory Visual: Grand vaulted stone throne hall with stained-glass illumination and heraldic crest. Prohibited: Office cubicles.
  3. DECISIVE MEDIEVAL CITADELS & SIEGES: Mountain stone fortresses, defensive ramparts. Mandatory Visual: Towering stone castle perched atop sheer granite precipice at golden hour. Prohibited: Concrete motorways.
  4. REVOLUTIONARY TREATIES & CONSTITUTIONAL BIRTH: Historical peace pacts, historic assembly halls. Mandatory Visual: Historic wood-paneled state hall with ancient parchment and quill. Prohibited: Strip malls.
  5. THE SOVEREIGN CONTINUITY TODAY: Timeless architectural heritage woven into the modern state. Mandatory Visual: Ancient stone bridge with national flag waving proudly above river. Prohibited: Fast food.
* MULTI-SHOT CADENCE: Shot 1: Sweeping cinematic aerial over ancient citadel. Shot 2: Living historic atmosphere (candlelight flicker, flag flapping). Shot 3: Macro 85mm archival patina on carved stone or ancient parchment.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly historical stone masonry, citadels, and ancient heritage. Zero modern neon/cars.
* OVERLAYS: "chapter_title": "HISTORICAL EPOCH", "fact_badge": "⏳ Historical milestone (e.g. '📜 Founded 966 AD', '⚔️ 1214 Magna Carta')".
""",

    "evolution": """
--- SPECIALIZED MANDATE: MODERN EVOLUTION & FUTURE HORIZONS ---
* MANDATORY CHAPTER SYLLABUS:
  1. THE AGRARIAN-TO-INDUSTRIAL PIVOT: Early industrial roots transitioning into clean modernity. Mandatory Visual: Historic brick factory clocktower framed against modern glass skyscrapers. Prohibited: Ruins.
  2. AUTOMATED BULLET TRAINS & SMART MOBILITY: High-speed rail networks, zero-emission urban transit. Mandatory Visual: Sleek aerodynamic bullet train curving along elevated concrete viaduct. Prohibited: Dirt tracks.
  3. SEMICONDUCTOR FABS & ROBOTIC INNOVATION: Advanced silicon manufacturing, robotic cleanrooms. Mandatory Visual: Robotic arms handling silicon wafers under yellow cleanroom lighting. Prohibited: Farmland.
  4. CLEAN ENERGY REVOLUTION: Nationwide green power grid, wind and solar infrastructure. Mandatory Visual: Vast coastal wind turbine array rotating over turquoise sea at golden hour. Prohibited: Bare rocks.
  5. VISIONARY METROPOLIS & FUTURE HORIZON: 21st-century architectural skyline at blue hour. Mandatory Visual: Futuristic glass-and-steel metropolis skyline with illuminated transit bridges. Prohibited: Slums.
* MULTI-SHOT CADENCE: Shot 1: Wide 4K drone over modern infrastructure. Shot 2: Living robotic/transit kinetic movement. Shot 3: Low-angle architectural reflection in polished glass facade.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Only forward-looking high-tech and modern infrastructure.
* OVERLAYS: "chapter_title": "MODERN HORIZONS", "fact_badge": "🚀 Innovation metric (e.g. '🚀 #1 Global Clean Grid', '💡 4.8% GDP to R&D')".
""",

    "turning_points": """
--- SPECIALIZED MANDATE: TURNING POINTS & DEFINING MOMENTS ---
* MANDATORY CHAPTER SYLLABUS:
  1. THE PRE-CRISIS ERA & SEEDS OF CHANGE: Society on the eve of transformation. Mandatory Visual: Historic civic square with historic clocktower ticking towards the decisive moment. Prohibited: Modern gadgets.
  2. THE CATALYTIC DAY: The singular historic day, treaty, or battle that changed history. Mandatory Visual: Dramatic push-in on the historic state building or monument where the event occurred. Prohibited: Beaches.
  3. NATIONAL RESILIENCE & SACRIFICE: How citizens united and endured through the trial. Mandatory Visual: Solemn national memorial with carved inscriptions and eternal flame. Prohibited: Shopping malls.
  4. RECONSTRUCTION & NEW SOVEREIGN COMPACT: Rebuilding the nation's political and physical fabric. Mandatory Visual: Reconstructed grand civic avenue with modern parliament architecture. Prohibited: Wilderness.
  5. THE ENDURING MODERN LEGACY: How that turning point guarantees sovereign freedom today. Mandatory Visual: Triumphant wide aerial view of the national capital with crowds celebrating heritage. Prohibited: Dilapidated ruins.
* MULTI-SHOT CADENCE: Shot 1: Dramatic establishing wide with atmospheric overcast lighting. Shot 2: Slow kinetic push on historic monument. Shot 3: Macro close-up on memorial inscription or bronze plaque.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Must stay strictly focused on the historical locations and monuments of the turning point.
* OVERLAYS: "chapter_title": "TURNING POINT", "fact_badge": "📜 Defining moment (e.g. '⚡ The Turning Point of 1968', '🏛️ The Treaty That Forged a Nation')".
""",

    "elected_leaders": """
--- SPECIALIZED MANDATE: ELECTED HEADS & PRESIDENTIAL LEGACIES ---
* MANDATORY CHAPTER SYLLABUS:
  1. FOUNDING HEAD OF STATE: First president/prime minister, constitutional inauguration. Mandatory Visual: Neoclassical presidential palace facade with sovereign flag, stately colonnades. Prohibited: Street markets.
  2. THE WARTIME / CRISIS LEADER: Leadership through survival and national defense. Mandatory Visual: Grand state council chamber, historic mahogany desk, presidential podium. Prohibited: Beaches.
  3. THE ECONOMIC MODERNIZER: Leadership that built national infrastructure and wealth. Mandatory Visual: Central bank headquarters, opening ceremonies of national expressways. Prohibited: Farmland.
  4. THE SOCIAL REFORMER & EDUCATION ADVOCATE: Expanding universities, healthcare, human rights. Mandatory Visual: Prestigious university quadrangle established under their administration. Prohibited: Empty mountains.
  5. THE CONTEMPORARY PRESIDENT & MODERN LEGACY: Current governance and foreign diplomacy. Mandatory Visual: Parliamentary debating chamber in session, motorcade arrival at executive palace. Prohibited: Suburbs.
* MULTI-SHOT CADENCE: Shot 1: Monumental wide architectural drone of the presidential palace. Shot 2: Dignified slow push toward executive podium. Shot 3: Macro of presidential seal, constitution, or state crest.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly presidential palaces, parliamentary chambers, state monuments, and executive halls.
* OVERLAYS: "chapter_title": "LEADERSHIP ERA", "fact_badge": "🏛️ Presidential legacy (e.g. '🎓 Sorbonne Alum', '📈 +180% GDP Growth')".
""",

    "wealthy_dynasties": """
--- SPECIALIZED MANDATE: WEALTHY DYNASTIES & ECONOMIC POWER ---
* MANDATORY CHAPTER SYLLABUS:
  1. OLD-MONEY MARITIME & BANKING EMPIRES: 19th-century merchant fleets and private vaults. Mandatory Visual: Grand neoclassical banking exchange with marble columns, private harbor docks. Prohibited: Slums.
  2. INDUSTRIAL GIANTS & MANUFACTURING BARONS: Steel mills, railways, dynastic factories. Mandatory Visual: Historic stone country manor overlooking vast private industrial estate. Prohibited: Farmland.
  3. PRIVATE ISLAND ESTATES & SUPERYACHT SANCTUARIES: Coastal retreats of the ultra-wealthy. Mandatory Visual: Sleek 90-meter superyacht moored off private coastal clifftop villa estate. Prohibited: Public campgrounds.
  4. DYNASTIC PHILANTHROPY & CULTURAL PATRONS: Private art collections, grand endowments. Mandatory Visual: Opulent private museum gallery with gilded baroque frames and marble statues. Prohibited: Fast food.
  5. MODERN TECH BILLIONAIRES & VENTURE DYNASTIES: Contemporary sovereign venture funds. Mandatory Visual: Penthouse boardroom overlooking glowing financial district skyline at night. Prohibited: Empty landscapes.
* MULTI-SHOT CADENCE: Shot 1: Expansive drone glide over private palace/estate. Shot 2: Smooth dolly through mahogany-paneled boardroom. Shot 3: 85mm macro on crystal decanter or dynastic crest.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly private estates, financial headquarters, superyacht harbors, and gilded architecture.
* OVERLAYS: "chapter_title": "DYNASTIC WEALTH", "fact_badge": "👑 Wealth legacy (e.g. '🏦 6-Generation Empire', '💎 $42B Sovereign Stake')".
""",

    "music_and_dance": """
--- SPECIALIZED MANDATE: MUSIC & TRADITIONAL DANCE HERITAGE ---
* MANDATORY CHAPTER SYLLABUS:
  1. ANCIENT ROOTS & INDIGENOUS INSTRUMENTS: Master instrument makers, ancient stringed lutes. Mandatory Visual: Artisan hand-carving wooden lute in sunlit workshop, acoustic close-up. Prohibited: Office cubicles.
  2. FOLK DANCE STEPS & FESTIVAL CHOREOGRAPHY: Synchronized communal dances, festive attire. Mandatory Visual: Dancers in vibrant embroidered traditional costumes spinning in town square. Prohibited: Empty rooms.
  3. ROYAL AMPHITHEATERS & CLASSICAL SYMPHONIES: Operas, royal Philharmonic orchestras. Mandatory Visual: Grand tier-balcony opera house with full symphony orchestra playing under chandelier. Prohibited: Factories.
  4. STREET RHYTHMS & CARNIVAL PAGEANTRY: Brass bands, rhythmic street celebrations. Mandatory Visual: Joyous street festival with brass horns, drums, and dancing crowds in evening light. Prohibited: Modern hospitals.
  5. MODERN GLOBAL FUSION & POP CULTURE: Global recording studios, stadium anthems. Mandatory Visual: High-tech sound engineering studio with mixing console, neon studio glow. Prohibited: Mountain peaks.
* MULTI-SHOT CADENCE: Shot 1: Wide establishing of amphitheater/plaza. Shot 2: Living synchronized dance motion or violin bow stroke. Shot 3: 85mm macro of instrument strings or embroidered textile hem.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly musical instruments, dancers in authentic costume, concert halls, and festivals.
* OVERLAYS: "chapter_title": "RHYTHM & DANCE", "fact_badge": "🎵 Musical heritage (e.g. '🪕 600-Year Instrument', '💃 UNESCO Intangible Heritage')".
""",

    "cinema_and_film_industry": """
--- SPECIALIZED MANDATE: CINEMA, FILM INDUSTRY & MOVIE HERITAGE ---
* MANDATORY CHAPTER SYLLABUS:
  1. THE GOLDEN AGE OF CELLULOID: Vintage film studios, black-and-white cinematic masters. Mandatory Visual: Classic 35mm film camera on soundstage with vintage directional tungsten spotlight. Prohibited: Corporate cubicles.
  2. COLOSSAL SOUNDSTAGES & PRODUCTION BACKLOTS: Massive film sets, practical set design. Mandatory Visual: Sweeping high-altitude aerial drone shot of massive film studio soundstages. Prohibited: Open wilderness.
  3. ICONIC CINEMATIC LOCATIONS: Natural and architectural landscapes famous in global films. Mandatory Visual: Dramatic cinematic location (citadel rampart or desert dunes) under 2.39:1 letterbox framing. Prohibited: Modern offices.
  4. ACTION CHOREOGRAPHY & PRACTICAL STUNT STAGES: Special effects, green-screen soundstages. Mandatory Visual: Action film set with camera Technocrane tracking across dramatic set. Prohibited: Supermarkets.
  5. RED CARPET GLAMOUR & BOX OFFICE PHENOMENON: Film festival palaces, international awards. Mandatory Visual: Grand film festival palace with red carpet, flashbulbs, and golden statuettes. Prohibited: Ordinary streets.
* MULTI-SHOT CADENCE: Shot 1: Cinematic widescreen wide of soundstage/location. Shot 2: Living film production camera movement (Technocrane sweep). Shot 3: Macro close-up of 35mm film reel or camera lens anamorphic flare.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: Strictly cinema production, film cameras, soundstages, and legendary movie set locations.
* OVERLAYS: "chapter_title": "CINEMA HERITAGE", "fact_badge": "🎬 Movie lore (e.g. '🎥 1,800 Films/Year Industry', '🏆 Golden Palm & Oscar Legacy')".
""",

    "major_industries_manufacturing": """
--- SPECIALIZED MANDATE: MAJOR INDUSTRIES, MANUFACTURING & INDUSTRIAL POWER ---
* MANDATORY CHAPTER SYLLABUS:
  1. AUTOMOTIVE MEGA-FACTORIES & ROBOTIC ARMS: Automated vehicle assembly lines, precision welding. Mandatory Visual: Robotic welding arms showering amber sparks over car body on automated track. Prohibited: Country roads.
  2. HEAVY SHIPYARDS & MARITIME DRY DOCKS: Colossal container ships and naval vessels being welded. Mandatory Visual: Massive dry dock with 350-meter container ship hull under towering gantry crane. Prohibited: Nature trails.
  3. AEROSPACE & TURBINE ENGINEERING: Jet engine assembly, carbon-fiber fuselage manufacturing. Mandatory Visual: Spotless aerospace hangar with engineers assembling commercial aircraft turbine. Prohibited: Farmland.
  4. SEMICONDUCTOR FOUNDRIES & HIGH-TECH CLEANROOMS: Microchips, cleanroom robotics. Mandatory Visual: Luminous yellow-lit cleanroom bay with automated wafer pods gliding on ceiling tracks. Prohibited: Street markets.
  5. EXPORT LOGISTICS & HEAVY FREIGHT CORRIDORS: Freight train terminals, logistics hubs. Mandatory Visual: Vast multi-track rail freight logistics yard linking mega-factories directly to ports. Prohibited: Empty mountains.
* MULTI-SHOT CADENCE: Shot 1: Monumental wide aerial drone flight over the industrial mega-complex. Shot 2: High-speed kinetic manufacturing motion (welding sparks, conveyor systems, robotic arms). Shot 3: Macro optical focus on precision machined gear or silicon wafer.
* STRICT BAN ON OUT-OF-BOUNDS VISUALS: STRICTLY BAN empty mountains, pristine beaches, or hiking paths. Every shot must feature heavy manufacturing, robotics, and industrial scale!
* OVERLAYS: "chapter_title": "INDUSTRIAL POWERHOUSE", "fact_badge": "🏭 Industrial powerhouse (e.g. '🚗 3.5M Vehicles Exported/Yr', '⚙️ Top 5 Global Manufacturer')".
""",

    "country_dossier": build_country_syllabus_directive(),
}
