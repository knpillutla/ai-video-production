"""Curiosity, Cultural Enigmas & Deep Heartland Archetypes for Nations Documentaries."""
from __future__ import annotations
from typing import Dict

CURIOSITY_ALIASES: Dict[str, str] = {
    "unseen_frontiers": "unseen_frontiers", "unseen": "unseen_frontiers", "hidden_world": "unseen_frontiers", "forbidden_places": "unseen_frontiers",
    "cultural_curiosities": "cultural_curiosities", "curiosities": "cultural_curiosities", "why_locals_do_this": "cultural_curiosities", "cultural_enigmas": "cultural_curiosities",
    "small_towns": "small_towns", "small_town": "small_towns", "village_life": "small_towns", "how_people_live": "small_towns", "provincial_life": "small_towns", "rural_towns": "small_towns",
    "survival_paradox": "survival_paradox", "paradox": "survival_paradox", "defied_geography": "survival_paradox",
    "unwritten_rules": "unwritten_rules", "social_rules": "unwritten_rules", "etiquette_rules": "unwritten_rules",
    "isolated_communities": "isolated_communities", "isolated_life": "isolated_communities", "edge_of_the_world": "isolated_communities",
    "lost_trades": "lost_trades", "ancient_crafts": "lost_trades", "master_craftsmen": "lost_trades",
    "cost_of_living": "cost_of_living", "how_locals_live": "cost_of_living", "purchasing_power": "cost_of_living",
    "deep_heartland": "deep_heartland", "hinterlands": "deep_heartland", "rural": "deep_heartland", "rural_life": "deep_heartland", "backcountry": "deep_heartland", "forgotten_provinces": "deep_heartland", "heartland": "deep_heartland",
    "remote_outposts": "remote_outposts", "remote_places": "remote_outposts", "extreme_remoteness": "remote_outposts", "edge_of_nowhere": "remote_outposts", "isolated_places": "remote_outposts",
    "resilience_triumph": "resilience_triumph", "natural_resilience": "resilience_triumph", "rebuilding_stronger": "resilience_triumph", "unbroken_spirit": "resilience_triumph", "cyclones_earthquakes": "resilience_triumph", "disaster_resilience": "resilience_triumph", "natural_calamities": "resilience_triumph", "natural_disasters": "resilience_triumph", "calamities": "resilience_triumph",
    "most_dangerous": "most_dangerous", "extreme_danger_zones": "most_dangerous", "deadliest_places": "most_dangerous", "danger_zones": "most_dangerous", "extreme_frontiers": "most_dangerous", "dangerous_places": "most_dangerous", "most_dangerous_places": "most_dangerous",
    "women_of_nation": "women_of_nation", "about_women": "women_of_nation", "women": "women_of_nation", "women_life": "women_of_nation", "women_traditions": "women_of_nation", "women_of_country": "women_of_nation", "daily_life_women": "women_of_nation", "women_culture": "women_of_nation",
    "men_of_nation": "men_of_nation", "about_men": "men_of_nation", "men": "men_of_nation", "men_life": "men_of_nation", "men_traditions": "men_of_nation", "men_of_country": "men_of_nation", "daily_life_men": "men_of_nation", "men_culture": "men_of_nation",
    "family_and_marriage_culture": "family_and_marriage_culture", "family_marriage": "family_and_marriage_culture", "marriage_culture": "family_and_marriage_culture", "family_culture": "family_and_marriage_culture", "weddings": "family_and_marriage_culture", "wedding_traditions": "family_and_marriage_culture", "family_traditions": "family_and_marriage_culture", "marriage_traditions": "family_and_marriage_culture",
}

CURIOSITY_DIRECTIVES: Dict[str, str] = {
    "unseen_frontiers": """
--- SPECIALIZED MANDATE: UNSEEN FRONTIERS & FORBIDDEN REALMS ---
Take viewers beyond standard tourist postcards into the nation's restricted, hidden, and off-limits worlds:
* Subject Focus: Subterranean cities, locked fortress chambers, isolated monastic cliff enclaves, restricted nature reserves, and forbidden mountain passes.
* Narrative Mystery: Build deep investigative curiosity, historical secrecy, and exclusivity ("What is hidden behind these sealed gates?").
* Visual Aesthetics: Atmospheric mist-veiled drone ascents over jagged ridgelines, dramatic chiaroscuro lighting, heavy ancient gates, subterranean vaults with lanterns, and razor-sharp architectural masonry.
* Overlay Specs: "chapter_title": "UNSEEN REALM", "fact_badge": "🔒 Restricted mystery (e.g. '🔒 Off-Limits for 400 Years', '⛰️ 3,100m Hidden Enclave')".
""",
    "cultural_curiosities": """
--- SPECIALIZED MANDATE: CULTURAL CURIOSITIES & ENIGMATIC TRADITIONS ---
Investigate the nation's most fascinating, unique daily rituals, gender traditions, and social enigmas that captivate outsiders:
* Subject Focus: Centuries-old daily rituals, social etiquette codes ("Why women do this", "Why men do this", "Why locals never do this"), unusual laws, and distinct lifestyle philosophies.
* Journalistic Respect: Approach customs with anthropological wonder, historical depth, and cultural admiration (strictly BBC/NatGeo style, zero derogatory stereotypes).
* Visual Aesthetics: Intimate 85mm eye-level lenses (f/1.8) capturing authentic human artisans, bustling historic markets, traditional attire, tea ceremonies, and warm golden lighting.
* Overlay Specs: "chapter_title": "CULTURAL ENIGMA", "fact_badge": "🎭 Living custom (e.g. '🎭 400-Year Etiquette', '☀️ Daily 2 PM Ritual')".
""",
    "small_towns": """
--- SPECIALIZED MANDATE: SMALL TOWNS & PROVINCIAL LIVING ---
Reveal authentic daily rhythms, intimate communities, and quiet heritage in the nation's historic small towns and villages:
* Subject Focus: Cobblestone town squares, multi-generational family bakers, village bell towers, morning produce markets, rustic stone cottages, and communal traditions far removed from bustling capital metropolises.
* Narrative Atmosphere: Warm, evocative, tranquil, and deeply human ("How do ordinary families actually live when the tourists leave?").
* Visual Aesthetics: Golden hour sidelight catching weathered pastel shutters, steam rising from fresh village bread, 85mm intimate portraits of smiling town elders, and slow sweeping crane glides over terracotta rooftops and river bridges.
* Overlay Specs: "chapter_title": "SMALL TOWN LIFE", "fact_badge": "🏡 Village rhythm (e.g. '🏡 Pop: 1,400 Residents', '🍞 300-Year Family Bakery')".
""",
    "survival_paradox": """
--- SPECIALIZED MANDATE: SURVIVAL PARADOX & GEOGRAPHIC INGENUITY ---
Explore how the nation conquered extreme geography, impossible climate, or economic odds that would bankrupt any other state:
* Subject Focus: Geo-engineering triumphs, geothermal mastery, building cities on water, harvesting snow/volcanoes, or extreme self-sufficiency.
* Narrative Tension: Frame the central paradox ("How did they survive and thrive without resources?").
* Visual Aesthetics: Sweeping 4K aerial glides over harsh terrain, monumental infrastructure, steam vents, icy waters, and bold resilience.
* Overlay Specs: "chapter_title": "SURVIVAL PARADOX", "fact_badge": "🌋 National anomaly (e.g. '🌋 90% Geothermal Grid', '🌊 20% Reclaimed Land')".
""",
    "unwritten_rules": """
--- SPECIALIZED MANDATE: UNWRITTEN RULES & SOCIAL ETIQUETTE ---
Decipher the nation's unspoken cultural laws, daily taboos, and subtle social codes that locals obey instinctively:
* Subject Focus: Dining etiquette, public transit courtesies, body language, daily hospitality customs, and things foreigners misunderstand.
* Narrative Tone: Witty, deeply observant, respectful, and educational travel sociology.
* Visual Aesthetics: Observational 50mm/85mm street photography, bustling cafes, respectful interactions, and lively piazzas in warm natural light.
* Overlay Specs: "chapter_title": "UNWRITTEN RULE", "fact_badge": "📜 Social etiquette (e.g. '☕ No Cappuccino After 11 AM', '🤫 Silent Train Commutes')".
""",
    "isolated_communities": """
--- SPECIALIZED MANDATE: ISOLATED COMMUNITIES & REMOTE LIVING ---
Journey into the nation's most cut-off, extreme, or inaccessible settlements where life operates on ancient time:
* Subject Focus: Island enclaves with no roads, winter-locked alpine hamlets, cliffside monasteries, and desert oases.
* Narrative Atmosphere: Meditative quietude, resilience, deep communal solidarity, and pure tranquil escapism.
* Visual Aesthetics: Epic wide aerial drone vistas highlighting sheer geographic isolation, mist rolling through valleys, and cozy stone hearths.
* Overlay Specs: "chapter_title": "REMOTE ENCLAVE", "fact_badge": "🏔️ Isolation metric (e.g. '❄️ 6 Months Snowbound', '👥 38 Residents Only')".
""",
    "lost_trades": """
--- SPECIALIZED MANDATE: LOST TRADES & MASTER CRAFTSMEN ---
Celebrate the nation's final generational masters preserving centuries-old artisanal crafts before they vanish:
* Subject Focus: Hand-forged swords/tools, wooden barrel coopers, mechanical clockmakers, stone masons, handloom weavers, and glassblowers.
* Sensory Immersion: Tactile 85mm macro f/1.8 cinematography, flying sparks, wood shavings, glowing embers, and artisanal ASMR foley.
* Narrative Soul: Reverence for human devotion, patience, and heritage passed through generations.
* Overlay Specs: "chapter_title": "LIVING MASTER", "fact_badge": "🪵 Heritage craft (e.g. '🔥 700-Year Tradition', '⏱️ 400 Hours per Piece')".
""",
    "cost_of_living": """
--- SPECIALIZED MANDATE: COST OF LIVING & LOCAL REALITY ---
Provide a transparent, grounded exploration of daily wages, grocery costs, housing, and purchasing power across the country:
* Subject Focus: Real supermarket prices, neighborhood bakeries, family home rentals, public transit fares, and typical middle-class life.
* Narrative Tone: Realistic, fascinating, practical, and highly engaging comparison for curious global viewers.
* Visual Aesthetics: Vibrant morning neighborhood markets, authentic residential streets, grocery stalls with price tags, and comfortable family homes.
* Overlay Specs: "chapter_title": "LIVING REALITY", "fact_badge": "💶 Economic reality (e.g. '🥖 €1.20 Fresh Baguette', '🏠 €750 Avg City Rent')".
""",
    "deep_heartland": """
--- SPECIALIZED MANDATE: DEEP HEARTLAND & HINTERLANDS ---
Focus strictly on the nation's authentic, off-grid heartland and hinterlands where life thrives far beyond the capital:
* Subject Focus: Remote farmsteads, off-grid valleys, self-reliant artisans, multi-generational homesteads, and daily survival skills.
* Narrative Tone: Respectful, earthy, grounding, revealing how real people live with peace, pride, and self-sufficiency.
* Visual Aesthetics: Atmospheric dawn mist over expansive fields, rustic stone chimneys, intimate 85mm portraits of weathered resilient hands, and sweeping aerial glides over quiet untamed landscapes.
* Overlay Specs: "chapter_title": "DEEP HEARTLAND", "fact_badge": "🌾 Heartland life (e.g. '🌾 100% Off-Grid Living', '🌲 4 Generations on Same Land')".
""",
    "remote_outposts": """
--- SPECIALIZED MANDATE: REMOTE OUTPOSTS & FRONTIER EDGES ---
Journey into the nation's most geographically extreme, isolated, and frontier outposts:
* Subject Focus: Settlements bordered by glaciers, desert expanses, or ocean cliffs, hundreds of miles from the nearest hospital or road.
* Narrative Atmosphere: Existential awe, human tenacity, and the unique psychology of thriving at the literal edge of civilization.
* Visual Aesthetics: Ultra-wide 4K drone cinematography contrasting minuscule human dwellings against colossal wilderness, glowing window lights against arctic or desert twilights.
* Overlay Specs: "chapter_title": "REMOTE OUTPOST", "fact_badge": "📍 Extreme outpost (e.g. '📍 800 Miles to Nearest Road', '❄️ -40°C Winter Endurance')".
""",
    "resilience_triumph": """
--- SPECIALIZED MANDATE: RESILIENCE & REBUILDING TRIUMPH ---
Celebrate the nation's indomitable human spirit, communal unity, and how locals coped with and triumphed over major cyclones, earthquakes, and tsunamis:
* Subject Focus: Epic human solidarity, rebuilding modern earthquake/cyclone-resilient architecture, community volunteerism, early-warning mastery, and vibrant cultural optimism.
* Positive Narrative Thrust: Avoid sensationalist misery; focus on awe-inspiring resilience, smiling communities rebuilding their homeland, and how adversity forged deeper national strength.
* Visual Aesthetics: Dramatic storm clouds breaking as warm golden sunlight floods rebuilt coastal villages, vibrant community markets, earthquake-absorbing architectural joints, and lush nature restored.
* Overlay Specs: "chapter_title": "UNBROKEN SPIRIT", "fact_badge": "🛡️ Resilience triumph (e.g. '🏗️ Rebuilt Stronger in 2 Years', '🛡️ Cyclone-Proof Shelters')".
""",
    "most_dangerous": """
--- SPECIALIZED MANDATE: MOST DANGEROUS PLACES & EXTREME FRONTIERS ---
Investigate the nation's most perilous, treacherous, and extreme frontiers where survival demands absolute vigilance:
* Subject Focus: Treacherous cliffside mountain passes with zero guardrails, active seismic/volcanic caldera fissures, deadly oceanic rip-current reefs, harsh frozen tundras, or extreme wilderness zones.
* Respectful High Tension: Capture the raw natural peril, geological instability, and local survival wisdom without gratuitous sensationalism.
* Visual Aesthetics: Dramatic low-angle drone flyovers along sheer thousand-meter cliffs, roaring volcanic steam plumes, crashing 10-meter coastal breakers, and rugged emergency outposts.
* Overlay Specs: "chapter_title": "DANGER FRONTIER", "fact_badge": "⚠️ Extreme hazard (e.g. '⚠️ 4,000m Unpaved Cliff Pass', '🌋 Active Caldera Zone')".
""",
    "women_of_nation": """
--- SPECIALIZED MANDATE: WOMEN OF THE NATION (LIVES, ROLES & LIVING SPIRIT) ---
Celebrate the daily lives, enduring values, traditional rituals, family foundations, and trailblazing leaders among the nation's women:
* Subject Focus: Authentic daily rhythms, multi-generational matriarchs, centuries-old beauty and wellness traditions, unwritten social etiquette, entrepreneurial leadership, and modern work-life balance.
* Journalistic Depth: Balanced, deeply respectful, and culturally rich storytelling honoring both traditional heritage (crafts, festivals, family wisdom) and modern achievements in science, business, and arts.
* Visual Aesthetics: Intimate 85mm natural-light portraiture, vibrant colorful traditional attire, elegant modern professional spaces, warm sunlit kitchens, and dignified expressive framing.
* Overlay Specs: "chapter_title": "SOUL & SISTERHOOD", "fact_badge": "👩 Cultural role (e.g. '🌸 88-Year Life Expectancy', '👩‍💼 48% Workforce Leadership')".
""",
    "men_of_nation": """
--- SPECIALIZED MANDATE: MEN OF THE NATION (CRAFT, BROTHERHOOD & ENDURANCE) ---
Explore the daily realities, unspoken codes of honor, fraternal camaraderie, traditional crafts, and modern identity of the nation's men:
* Subject Focus: Traditional demanding trades (alpine shepherds, deep-sea fishermen, stonemasons, blacksmiths), civic duties and defense service, cafe/square gathering rituals, and evolving modern fatherhood.
* Authentic Tone: Grounded, authentic, and emotionally resonant examination of masculine culture, mentorship across generations, work ethic, and community solidarity.
* Visual Aesthetics: Tactile macro cinematography of calloused hands shaping wood or iron, morning conversations in historic espresso/tea joints, rugged outdoor endurance in shifting elements, and confident tailored elegance.
* Overlay Specs: "chapter_title": "BROTHERHOOD & CRAFT", "fact_badge": "👨 Traditional craft (e.g. '⚓ 5th-Generation Fisherman', '🤝 Fraternal Guild Heritage')".
""",
    "family_and_marriage_culture": """
--- SPECIALIZED MANDATE: FAMILY & MARRIAGE CULTURE ---
Investigate the nation's intimate family structures, sacred wedding traditions, multi-generational bonds, and courtship customs:
* Subject Focus: Multi-day traditional wedding celebrations (e.g. Indian Sangeet & Baraat, Greek orthodox crowns, Korean Pyebaek, Italian reception feasts), sacred vows, courtship etiquette, living with extended family, and revering elders.
* Societal Soul: Deep cultural exploration of how family loyalty, communal child-rearing, ancestral lineage, and marital unity anchor society against modern isolation.
* Visual Aesthetics: Warm cinematic 50mm and 85mm shallow depth-of-field, glowing floral mandaps or cathedral arches, joyous folk dance circles, tearful elder blessings, and vibrant festive attire.
* Overlay Specs: "chapter_title": "SACRED BONDS", "fact_badge": "💍 Wedding tradition (e.g. '🎉 3-Day Wedding Pageantry', '🏡 3-Generation Family Home')".
""",
}


