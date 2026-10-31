"""Documentary Syllabus Catalog.

Authoritative catalog of all 35 Sovereign Almanac Pillars spanning:
- Act I: Origins, Sovereignty & Land (1-7)
- Act II: People, Language, Society & Well-being (8-14)
- Act III: Economy, Infrastructure & Industry (15-21)
- Act IV: Living Culture, Gastronomy & Recreation (22-28)
- Act V: Ecology, Diplomacy, Diaspora & The Horizon (29-35)
"""
from __future__ import annotations

from typing import Dict

PILLARS_ALMANAC: Dict[str, Dict[str, str]] = {
    # --- ACT I: ORIGINS, SOVEREIGNTY & LAND ---
    "prologue": {
        "title": "PROLOGUE & SOVEREIGN EXPEDITION ROADMAP",
        "focus": "Topic declaration, national character, geographic scale, central paradox, and 360° journey roadmap.",
        "visual": "Sweeping golden-hour aerial drone flight over iconic topography, kinetic societal pulse, hero landmark reveal.",
        "banned": "Generic office cubicles or hyper-local details without national scope.",
        "badge": "🌍 Sovereign Expedition",
    },
    "identity": {
        "title": "ORIGINS, INDEPENDENCE & CONSTITUTIONAL DAWN",
        "focus": "When and how it became a nation, ancient founding cradle, declaration of independence, and constitutional sovereignty.",
        "visual": "Ancient stone fortress ruins, historic independence landmark/square, original constitution parchment.",
        "banned": "Generic office cubicles or random highways.",
        "badge": "🏛️ Sovereignty Established",
    },
    "ancient_history": {
        "title": "ANCIENT HISTORY, BRONZE AGE & MEDIEVAL KINGDOMS",
        "focus": "Prehistoric settlements, Bronze Age culture, medieval dynasties, civilizational turning points.",
        "visual": "Ancient megalithic stone circles, weathered castle ruins at misty dawn, archaeological relics.",
        "banned": "Modern traffic or industrial factories.",
        "badge": "📜 Civilizational Epochs",
    },
    "capital_governance": {
        "title": "CAPITAL CITY & EXECUTIVE GOVERNANCE",
        "focus": "The capital city (MUST explicitly state it is the capital of the nation), parliamentary democracy, executive seat.",
        "visual": "National parliament building, executive state house, civic precinct.",
        "banned": "Residential suburbs or generic park benches.",
        "badge": "🏛️ Capital & Government Seat",
    },
    "geography_topography": {
        "title": "PHYSICAL GEOGRAPHY, MOUNTAINS & COASTLINES",
        "focus": "Land area in km², coastline length, geological spine, monumental mountain ranges, peaks.",
        "visual": "Razor-sharp alpine peaks, deep glacial fjords, dramatic oceanic headlands (ONLY HERE).",
        "banned": "Factories, container cranes, or urban malls.",
        "badge": "🏔️ Area & Geological Spine",
    },
    "inland_waterways": {
        "title": "INLAND WATERWAYS, GREAT LAKES & RIVER BASINS",
        "focus": "Hydrological spine, major rivers, freshwater lakes, canal networks, aquatic ecology.",
        "visual": "Expansive freshwater river basin, cascading river bends, historic canal barges.",
        "banned": "Dry arid deserts or open saltwater oceans.",
        "badge": "🌊 Great Inland Waterways",
    },
    "climate_seasons": {
        "title": "FOUR SEASONS, CLIMATE & WEATHER EXTREMES",
        "focus": "Seasonal transitions, temperature shifts, precipitation, maritime and alpine weather currents.",
        "visual": "Dramatic weather front, sunbeams through autumn canopy, winter frost over valleys.",
        "banned": "Indoor spaces or generic city traffic.",
        "badge": "❄️ Annual Climate Range",
    },
    "monuments_architecture": {
        "title": "ICONIC NATIONAL MONUMENTS & CITADELS",
        "focus": "Historic stone fortresses, ancient citadels, UNESCO memorials, landmark stone architecture.",
        "visual": "Weathered stone fortress ramparts, monumental arches, ancient architectural cloisters.",
        "banned": "Modern strip malls or temporary structures.",
        "badge": "🏰 UNESCO National Heritage",
    },
    # --- ACT II: PEOPLE, LANGUAGE, SOCIETY & WELL-BEING ---
    "people_society": {
        "title": "PEOPLE, DEMOGRAPHICS & CULTURAL HARMONY",
        "focus": "Population count, demographic mosaic, social trust, community solidarity, family traditions.",
        "visual": "Historic living town squares, multigenerational gathering spaces, vibrant civic pedestrian avenues.",
        "banned": "Empty barren rocks or unpopulated wilderness.",
        "badge": "👥 Population & Demographics",
    },
    "language_heritage": {
        "title": "LANGUAGE, DIALECTS & ANCIENT SCRIPTS",
        "focus": "Official tongues, regional dialects, ancient scripts, linguistic preservation, oral storytelling.",
        "visual": "Ancient stone inscriptions, historic illuminated calligraphy, bilingual street signs, oral recitations.",
        "banned": "Generic modern highway signage.",
        "badge": "🗣️ Living Linguistic Heritage",
    },
    "spiritual_heritage": {
        "title": "SPIRITUAL HERITAGE, ABBEYS & SACRED SANCTUARIES",
        "focus": "Historic monastic centers, medieval abbeys, sacred architectural heritage, interfaith tolerance.",
        "visual": "Atmospheric medieval stone cloisters, cathedral stained glass, ancient monastic ruins on green hills.",
        "banned": "Modern shopping streets or neon arcades.",
        "badge": "⛪ Sacred Heritage & Abbeys",
    },
    "major_cities": {
        "title": "GREAT METROPOLISES & REGIONAL CITIES",
        "focus": "Major regional economic and cultural hubs beyond the capital, skyline architecture.",
        "visual": "Expansive aerial drone vista over major regional metropolis skyline and waterfront harbor.",
        "banned": "Rural farmlands or remote mountain passes.",
        "badge": "🏙️ Major Urban Hubs",
    },
    "education_universities": {
        "title": "EDUCATION, RESEARCH & TOP UNIVERSITIES",
        "focus": "Literacy rate, national education system, world-ranked universities, scientific inquiry.",
        "visual": "Prestigious university campus, collegiate clocktower, sunlit historic library, research laboratories.",
        "banned": "Empty mountains, waterfalls, or random roads.",
        "badge": "🎓 World-Ranked Universities",
    },
    "science_inventions": {
        "title": "SCIENCE, GLOBAL INVENTIONS & BREAKTHROUGHS",
        "focus": "Nobel laureates, historic scientific discoveries, space missions, medical patents, breakthrough tech.",
        "visual": "Cutting-edge laser laboratories, cleanroom nanotechnology, astronomical observatories, space tech.",
        "banned": "Farming tractors or coastal beaches.",
        "badge": "🔬 Scientific Breakthroughs",
    },
    "healthcare_longevity": {
        "title": "PUBLIC HEALTHCARE, WELL-BEING & LONGEVITY",
        "focus": "Universal healthcare system, world-leading life expectancy, wellness philosophy, active outdoor living.",
        "visual": "Modern medical healthcare centers, alpine wellness baths, seniors cycling along sunlit greenways.",
        "banned": "Fast food drive-throughs or smoggy highways.",
        "badge": "🩺 Healthcare & Longevity",
    },
    # --- ACT III: ECONOMY, INFRASTRUCTURE & INDUSTRY ---
    "currency_wealth_fund": {
        "title": "MONETARY ARCHITECTURE, BANKING & SOVEREIGN FUNDS",
        "focus": "National currency, central banking architecture, sovereign wealth reserves, financial resilience.",
        "visual": "Central bank headquarters, historic mint architecture, financial exchange trading concourse.",
        "banned": "Unrelated pastoral farms or nature reserves.",
        "badge": "🪙 Currency & Sovereign Reserves",
    },
    "jobs_livelihood": {
        "title": "JOBS, EMPLOYMENT & DOMINANT LIVELIHOODS",
        "focus": "Primary employment sectors, service economy, digital tech, skilled engineering, artisan guilds.",
        "visual": "Modern technology innovation campus, high-tech engineering hubs, skilled artisan design studios.",
        "banned": "Generic empty countryside or nature reserves.",
        "badge": "💼 Employment & Livelihood",
    },
    "agriculture_harvest": {
        "title": "FARMING, AGRICULTURE & RURAL HARVEST",
        "focus": "Agricultural staples, dairy herds, viticulture, rural cooperatives, modern harvest technology.",
        "visual": "Golden crop fields, geometric vineyard rows, combine harvesters, center-pivot irrigation rigs.",
        "banned": "Concrete cityscapes or container docks.",
        "badge": "🌾 Agricultural Output",
    },
    "industry_manufacturing": {
        "title": "MANUFACTURING, INDUSTRY & HIGH-TECH",
        "focus": "Heavy manufacturing, aerospace, precision robotics, biopharmaceuticals, advanced industrial output.",
        "visual": "State-of-the-art robotic assembly plant with amber sparks, modern foundries, cleanrooms.",
        "banned": "Pristine nature trails or quiet beaches.",
        "badge": "⚙️ Manufacturing Engine",
    },
    "trade_ports": {
        "title": "TRADE & MARITIME COMMERCE: MAJOR PORTS",
        "focus": "Top export/import partners, commercial shipping, trade balance, deepwater harbor berths.",
        "visual": "Deepwater container terminal, massive red gantry cranes loading cargo freighters, container stacks.",
        "banned": "Beaches, remote mountains, or empty hills.",
        "badge": "🚢 Maritime Cargo Terminal",
    },
    "domestic_rail_transit": {
        "title": "HIGH-SPEED RAIL & DOMESTIC INFRASTRUCTURE",
        "focus": "High-speed rail corridors, monumental mountain tunnels, deep-sea bridges, green public mobility.",
        "visual": "Sleek aerodynamic high-speed train gliding across viaduct, modern transit interchange, alpine tunnel portal.",
        "banned": "Airport baggage carousels or dirt horse paths.",
        "badge": "🚆 High-Speed Rail Corridors",
    },
    "airports_aviation": {
        "title": "NATIONAL TRANSIT: AIRPORTS & AVIATION",
        "focus": "International air corridors, passenger traffic, airport infrastructure, continental flight gateways.",
        "visual": "International airport runways, commercial passenger airliners taxiing/taking off, glass terminal concourse.",
        "banned": "Empty highways or generic open skies.",
        "badge": "✈️ International Air Gateway",
    },
    # --- ACT IV: LIVING CULTURE, GASTRONOMY & RECREATION ---
    "clean_energy": {
        "title": "POWER, CLEAN ENERGY & NATIONAL UTILITIES",
        "focus": "National energy grid, renewable electricity percentage, wind farms, hydro dams, geothermal power.",
        "visual": "Modern coastal wind turbine arrays, geothermal steam vents, massive hydroelectric dam spillways.",
        "banned": "Bare unpowered rocks or mountains.",
        "badge": "⚡ Clean Energy Grid",
    },
    "environmental_stewardship": {
        "title": "ENVIRONMENTAL STEWARDSHIP & CLIMATE RESILIENCE",
        "focus": "Ecological conservation, circular recycling economy, sea barriers, flood defense, reforestation.",
        "visual": "Monumental sea defense storm surge barrier, wetland reforestation project, pristine eco-sanctuary.",
        "banned": "Smokestacks or landfill dumps.",
        "badge": "🌱 Environmental Resilience",
    },
    "food_culinary": {
        "title": "CULINARY SOUL & FOOD CULTURE",
        "focus": "Traditional gastronomy, national dishes, artisanal ingredients, historic food market halls.",
        "visual": "Bustling historic food market hall, artisanal culinary preparation, authentic local food specialties.",
        "banned": "Generic sterile supermarkets or fast food chains.",
        "badge": "🍷 Gastronomic Heritage",
    },
    "arts_crafts": {
        "title": "ARTS, CRAFTSMANSHIP & CULTURAL HERITAGE",
        "focus": "Fine arts, architectural craftsmanship, stone masonry, historic guild crafts, national galleries.",
        "visual": "Grand museum sculpture gallery, tactile 85mm macro craftsmanship, intricate stone carving.",
        "banned": "Modern office buildings or container yards.",
        "badge": "🎨 Arts & Craftsmanship",
    },
    "music_entertainment": {
        "title": "MUSIC, TRADITIONAL DANCE & ENTERTAINMENT",
        "focus": "Folk music traditions, classical orchestras, native dances, modern cinema and entertainment culture.",
        "visual": "Acoustic concert auditorium, traditional dancers in authentic festive attire, film soundstage.",
        "banned": "Empty desolate landscapes.",
        "badge": "🎵 Music & Cultural Soul",
    },
    "national_sports": {
        "title": "NATIONAL SPORTS, ATHLETICS & TRADITIONAL GAMES",
        "focus": "Indigenous sports, Olympic heritage, national athletic stadiums, grassroots sporting passion.",
        "visual": "Packed 80,000-seat national stadium, fast-paced indigenous field sport, athletic training arenas.",
        "banned": "Empty abandoned playgrounds or generic gyms.",
        "badge": "🏆 National Sports & Athletics",
    },
    "festivals_traditions": {
        "title": "NATIONAL HOLIDAYS, FOLK FESTIVALS & LIVING CUSTOMS",
        "focus": "Annual public holidays, historic carnivals, ancestral fire rituals, traditional costumes, national parades.",
        "visual": "Vibrant street carnival with brass bands, citizens in traditional regional folk attire, festive fireworks.",
        "banned": "Quiet empty streets or corporate offices.",
        "badge": "🎉 Folk Festivals & Living Customs",
    },
    # --- ACT V: ECOLOGY, DIPLOMACY, DIASPORA & THE HORIZON ---
    "national_parks": {
        "title": "NATIONAL PARKS & CONSERVED BIOMES",
        "focus": "Protected wilderness sanctuaries, endemic fauna and flora, biodiversity conservation zones.",
        "visual": "Lush temperate rainforest canopy, crystal clear conservation streams, pristine wilderness.",
        "banned": "Urban sprawl or industrial facilities.",
        "badge": "🌿 Protected Sanctuaries",
    },
    "wildlife_fauna": {
        "title": "ENDEMIC WILDLIFE, NATIVE FAUNA & MARINE KINGDOMS",
        "focus": "Native mammals, migratory bird flyways, marine life, sea mammals, ancient forest species.",
        "visual": "Stately stag in misty ancient forest, nesting puffins on oceanic cliffs, breaching marine whales.",
        "banned": "Zoos, cages, or urban domestic pets.",
        "badge": "🦌 Native Wildlife & Fauna",
    },
    "beaches_resorts": {
        "title": "COASTAL SANCTUARIES: BEACHES & HEADLANDS",
        "focus": "Oceanic coastlines, golden sand beaches, marine reserves, tidal cliffs and island retreats.",
        "visual": "Sweeping turquoise coastal bay, dramatic sea stacks, tranquil ocean shoreline, luxury cabana terraces.",
        "banned": "Industrial ports or crowded shopping districts.",
        "badge": "🏖️ Coastal Marine Haven",
    },
    "defense_security": {
        "title": "SOVEREIGN DEFENSE, COAST GUARD & PEACEKEEPING",
        "focus": "National defense posture, naval coastal patrol, search-and-rescue, international peacekeeping.",
        "visual": "Naval patrol vessel cutting through coastal waters, coast guard rescue helicopter, disciplined guard.",
        "banned": "Active warzone destruction or chaotic combat.",
        "badge": "🛡️ Sovereign Defense & Patrol",
    },
    "politics_alliances": {
        "title": "POLITICS, GLOBAL ALLIANCES & TREATIES",
        "focus": "International diplomacy, global treaties (UN, EU, NATO, OECD), international peacekeeping.",
        "visual": "Diplomatic assembly hall, national flags along sovereign plaza, grand neoclassical state building.",
        "banned": "Random traffic or wilderness.",
        "badge": "🌐 International Treaties",
    },
    "global_diaspora": {
        "title": "WORLDWIDE DIASPORA & GLOBAL SOFT POWER",
        "focus": "Historical emigration, global diaspora communities, international cultural diplomacy, soft power.",
        "visual": "Illuminated world map connections, international cultural embassies, global celebration of national day.",
        "banned": "Narrow provincial views without global scope.",
        "badge": "🌍 Worldwide Diaspora & Soft Power",
    },
    "conclusion_future": {
        "title": "SOVEREIGN RESILIENCE & FUTURE HORIZON",
        "focus": "Authoritative summary of national resilience, modern vision, 21st-century trajectory, closing reflection.",
        "visual": "Wide panoramic twilight/sunset drone pull-back over illuminated capital skyline or majestic horizon.",
        "banned": "Infographic recap slides or abrupt cuts.",
        "badge": "✨ Sovereign Future Horizon",
    },
}

CORE_10_KEYS = [
    "identity", "capital_governance", "geography_topography", "people_society",
    "education_universities", "agriculture_harvest", "clean_energy",
    "trade_ports", "airports_aviation", "conclusion_future"
]

BROADCAST_21_KEYS = [
    "identity", "capital_governance", "geography_topography", "climate_seasons",
    "monuments_architecture", "people_society", "major_cities", "education_universities",
    "jobs_livelihood", "agriculture_harvest", "industry_manufacturing", "trade_ports",
    "airports_aviation", "clean_energy", "food_culinary", "arts_crafts",
    "music_entertainment", "national_parks", "beaches_resorts", "politics_alliances",
    "conclusion_future"
]

BROADCAST_22_KEYS = ["prologue"] + BROADCAST_21_KEYS
ALMANAC_35_KEYS = list(PILLARS_ALMANAC.keys())
