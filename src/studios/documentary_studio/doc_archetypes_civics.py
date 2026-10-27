"""Civics, History, Governance & Leadership Archetypes for Nations Documentaries."""
from __future__ import annotations
from typing import Dict

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
}

CIVICS_DIRECTIVES: Dict[str, str] = {

    "major_projects": """
--- SPECIALIZED MANDATE: MAJOR PROJECTS & MEGASTRUCTURES ---
Focus strictly on the nation's crowning engineering feats and mega-infrastructure that conquered geography:
* Subject Focus: Iconic dams, trans-continental suspension bridges, undersea tunnels, high-speed rail lines, deep-water ports, aerospace launchpads, and renewable energy grids.
* Factual Exactitude: Narration must include concrete metrics (concrete tonnage, span length, excavation depth, megawatts generated, transit speeds, workforce scale).
* Visual Aesthetics: Expansive geometric aerials, massive scale comparisons, symmetrical bridge towers, high-tech control centers, and dynamic drone tracks along transportation arteries.
* Overlay Specs: "chapter_title": "ENGINEERING MARVEL", "fact_badge": "🏗️ Concrete stats (e.g. '🚆 350 km/h Network', '⚡ 22.5 GW Capacity')".
""",
    "history": """
--- SPECIALIZED MANDATE: DEEP HISTORY & FOUNDING DYNASTIES ---
Chronicle the pivotal historical eras, foundational dynasties, decisive battles, and turning points that forged the nation:
* Subject Focus: Founding emperors and monarchies, ancient tribal confederacies, medieval citadels, decisive revolutionary treaties, and world-shaping alliances.
* Visual Aesthetics: Archival patina, weathered stone masonry, grand vaulted throne halls, ancient battlefield plains at twilight, and tactile macro craftsmanship.
* Narrative Cadence: Strict chronological resonance weaving how ancient survival instincts evolved into the modern constitutional and cultural fabric of the sovereign state.
* Overlay Specs: "chapter_title": "HISTORICAL EPOCH", "fact_badge": "⏳ Historical milestone (e.g. '📜 Founded 966 AD', '⚔️ 1214 Magna Carta')".
""",
    "evolution": """
--- SPECIALIZED MANDATE: MODERN EVOLUTION & FUTURE HORIZONS ---
Explore the nation's contemporary rise, technological transformation, economic leap, and forward-looking vision:
* Subject Focus: Advanced semiconductor fabs, clean energy transitions, automated bullet trains, AI innovation corridors, smart metropolis design, and aerospace programs.
* Narrative Thrust: How the nation transformed its economy from traditional roots into a global technological, scientific, and cultural powerhouse.
* Visual Aesthetics: Gleaming glass-and-steel skylines at blue hour, automated manufacturing robotics, bustling financial plazas, and clean green urban corridors.
* Overlay Specs: "chapter_title": "MODERN HORIZONS", "fact_badge": "🚀 Innovation metric (e.g. '🚀 #1 Global Clean Grid', '💡 4.8% GDP to R&D')".
""",
    "turning_points": """
--- SPECIALIZED MANDATE: TURNING POINTS & DEFINING MOMENTS ---
Uncover the decisive, catalytic turning points and transformative historical moments that forged the modern nation:
* Subject Focus: The singular day, crisis, historic breakthrough, treaty, or revolution that permanently altered national destiny.
* Narrative Drama: Deep investigative tension, chronological pacing, archival resonance, and cause-and-effect storytelling.
* Visual Aesthetics: Dramatic lighting, slow push-ins on historic citadels and monuments, weathered cobblestones, atmospheric overcast skies, and contrasting modern progress.
* Overlay Specs: "chapter_title": "TURNING POINT", "fact_badge": "📜 Defining moment (e.g. '⚡ The Turning Point of 1968', '🏛️ The Treaty That Forged a Nation')".
""",
    "elected_leaders": """
--- SPECIALIZED MANDATE: ELECTED HEADS & PRESIDENTIAL LEGACIES ---
Chronicle the elected heads of state (Presidents / Prime Ministers) in chronological order from independence to modern day:
* Subject Focus: Their educational pedigree (universities attended, formative influences), ideological vision, major national reforms, and honest balanced appraisal of triumphs vs. controversies.
* Country Transformation: Trace how each leadership era tangibly modernized infrastructure, economy, education, or foreign alliances.
* Visual Aesthetics: Grand neoclassical presidential palaces, parliamentary debating chambers, historic black-and-white to color transition archival footage, dignified portrait framing, and modern state motorcades.
* Overlay Specs: "chapter_title": "LEADERSHIP ERA", "fact_badge": "🏛️ Presidential legacy (e.g. '🎓 Sorbonne Alum', '📈 +180% GDP Growth')".
""",
    "wealthy_dynasties": """
--- SPECIALIZED MANDATE: WEALTHY DYNASTIES & ECONOMIC POWER ---
Explore the historic family dynasties, private empires, and ultra-wealthy titans who built and influenced the nation's economy:
* Subject Focus: Old-money shipping/banking dynasties, industrial magnates, private estates, philanthropic foundations, and modern tech billionaires.
* Economic Investigation: High journalistic integrity exploring how dynastic family businesses shaped national industries, international trade networks, and modern sovereign wealth.
* Visual Aesthetics: Gilded private country estates, sleek superyachts moored in private harbors, historic boardroom mahogany, private art collections, and panoramic penthouse views.
* Overlay Specs: "chapter_title": "DYNASTIC WEALTH", "fact_badge": "👑 Wealth legacy (e.g. '🏦 6-Generation Empire', '💎 $42B Sovereign Stake')".
""",
    "music_and_dance": """
--- SPECIALIZED MANDATE: MUSIC & TRADITIONAL DANCE HERITAGE ---
Celebrate the nation's rhythmic heartbeat, traditional dances, master musicians, and iconic indigenous instruments:
* Subject Focus: Classical music traditions (ragas, symphonies, flamenco, celtic reels), ancient instruments (sitar, koto, lute, bagpipes, bouzouki), and iconic cultural dances (Kathak, Flamenco, Samba, Polka).
* Sonic & Visual Harmony: Macro close-ups of strings being plucked, dancer footwork striking the floor in synchronized rhythm, swirling traditional skirts, and resonant acoustics of ancient amphitheaters.
* Narrative Soul: How folk melodies and traditional dances carry ancient ancestral stories, festive harvest joy, and communal solidarity.
* Overlay Specs: "chapter_title": "RHYTHM & DANCE", "fact_badge": "🎵 Musical heritage (e.g. '🪕 600-Year Instrument', '💃 UNESCO Intangible Heritage')".
""",
    "cinema_and_film_industry": """
--- SPECIALIZED MANDATE: CINEMA, FILM INDUSTRY & MOVIE HERITAGE ---
Explore the nation's cinematic golden age, major movie industries (e.g. Bollywood, Tollywood, Hollywood, Cinecittà, French New Wave), and legendary film directors:
* Subject Focus: Landmark film studios, visionary auteurs, iconic filming locations (historic backlots, desert dunes, dramatic citadels), and cultural storytelling tropes that captivated global audiences.
* Industry Scale: Box office phenomena, massive productions, star power, practical vs CGI stunts, and the socioeconomic impact of cinema.
* Visual Aesthetics: Cinematic 2.39:1 widescreen framing, rich atmospheric rim lighting, vintage 35mm film grain texture, bustling film studio soundstages, and sweeping drone glides over legendary film set locations.
* Overlay Specs: "chapter_title": "CINEMA HERITAGE", "fact_badge": "🎬 Movie lore (e.g. '🎥 1,800 Films/Year Industry', '🏆 Golden Palm & Oscar Legacy')".
""",
    "major_industries_manufacturing": """
--- SPECIALIZED MANDATE: MAJOR INDUSTRIES, MANUFACTURING & INDUSTRIAL POWER ---
Investigate the colossal factories, industrial hubs, and manufacturing titans that drive the national economy:
* Subject Focus: Automotive mega-factories, aerospace assembly hangars, precision machinery, chemical complexes, high-tech semiconductor fabs, colossal shipyards, and green industrial innovation.
* Industrial Scale: Global export rankings, robotic automation lines, skilled engineering workforces, and how manufacturing propelled the nation onto the world stage.
* Visual Aesthetics: Dynamic sweeping shots inside state-of-the-art robotic assembly plants with amber sparks, molten metal casting in high-tech foundries, colossal container ships being welded, and illuminated industrial skylines at dusk.
* Overlay Specs: "chapter_title": "INDUSTRIAL POWERHOUSE", "fact_badge": "🏭 Industrial powerhouse (e.g. '🚗 3.5M Vehicles Exported/Yr', '⚙️ Top 5 Global Manufacturer')".
""",
}


