"""Documentary Sovereign Chapter Declarative Templates Catalog.

Contains declarative 4-tuples (subtitle_tmpl, badge_tmpl, stats_tmpl, narration_tmpl)
for all 35 sovereign documentary chapters across 5 Acts.
"""
from typing import Dict, Tuple

CHAPTER_TEMPLATES: Dict[str, Tuple[str, str, str, str]] = {
    # --- ACT I: ORIGINS, SOVEREIGNTY & LAND ---
    "prologue": (
        "Prologue & The Sovereign Expedition of {dest_name}",
        "🌍 {dest_name}: Sovereign Expedition",
        "{area_km2} • Pop: {population} • {hdi_rank}",
        "{dest_name}. A sovereign nation sculpted by monumental landscapes and forged in ancient resilience, spanning {area_km2} and home to {population}. Behind its breathtaking natural beauty lies a living society balancing centuries of proud heritage with cutting-edge 21st-century innovation. In this definitive 360-degree documentary expedition, we uncover the complete story of {dest_name}—from its ancient foundational citadels and primeval biospheres, to its industrial powerhouses, cultural soul, and future horizons.",
    ),
    "identity": (
        "Origins, Independence & Constitutional Dawn of {dest_name}",
        "🏛️ Sovereignty Established: {official_name}",
        "{head_of_state} • {parliament}",
        "Officially proclaimed as {official_name}, the sovereign state was forged through centuries of historical self-determination and constitutional rebirth. Guided by {head_of_state} and the legislative authority of {parliament}, the nation's independence milestone cemented its sovereign self-rule, establishing an enduring democratic covenant rooted in ancestral fortitude and civic resilience.",
    ),
    "ancient_history": (
        "Prehistoric Settlements, Bronze Age & Medieval Kingdoms",
        "📜 Heritage: {ancient_history}",
        "Civilizational Epochs • Medieval Dynasties",
        "Before the emergence of the modern state, {dest_name}'s civilizational roots were forged across millennia of human settlement: {ancient_history}. These transformative ancient eras and founding dynasties established the enduring cultural foundations of the sovereign nation.",
    ),
    "capital_governance": (
        "Executive Governance & Civic Halls of {capital}",
        "🏛️ Capital: {capital}",
        "Parliament: {parliament} • Seat: {capital}",
        "The sovereign capital of {dest_name} is centered in {capital}. Here, executive authority and national legislation are enacted through the {parliament}, where elected representatives steer the nation's democratic policies, statutory laws, and civic stewardship.",
    ),
    "geography_topography": (
        "Geological Spine, Mountains & Coastal Frontiers",
        "🏔️ Area: {area_km2}",
        "Area: {area_km2} • Coastline: {coastline_km}",
        "Spanning {area_km2} of territory and {coastline_km}, {dest_name}'s physical landscape is defined by monumental geological diversity: {geography}. These natural landforms shape both the nation's ecological biomes and human settlement patterns.",
    ),
    "inland_waterways": (
        "Great River Basins, Glacial Lakes & Canals",
        "🌊 Hydrology: {inland_waterways}",
        "Freshwater Basins • Navigable Corridors",
        "The freshwater lifeblood of {dest_name} flows through vital hydrological networks: {inland_waterways}. These river corridors and expansive lakes support regional commerce, historic navigation, and vital aquatic ecosystems.",
    ),
    "climate_seasons": (
        "The Four Seasons & Weather Extremes",
        "❄️ Climate: {climate}",
        "Atmospheric Range • Seasonal Shifts",
        "The nation's climate is characterized as {climate}. Marked seasonal shifts bring dramatic transformations across the landscape, influencing agricultural harvests, coastal waters, and the enduring rhythms of daily life.",
    ),
    "monuments_architecture": (
        "Ancient Citadels & Sovereign Memorials",
        "🏰 Heritage: {monuments}",
        "National Citadels • UNESCO Sanctuaries",
        "Preserving centuries of civilization, {dest_name}'s architectural legacy is embodied in its master monuments, notably {monuments}. These revered citadels and UNESCO World Heritage sites stand as physical chronicles of ancient engineering genius and sovereign perseverance.",
    ),
    # --- ACT II: PEOPLE, LANGUAGE, SOCIETY & WELL-BEING ---
    "people_society": (
        "Demographics, Civic Trust & Multigenerational Harmony",
        "👥 Population: {population}",
        "Population: {population} • {hdi_rank}",
        "Inhabited by {population}, {dest_name} is celebrated for its {people}. The social fabric thrives on community solidarity, civic responsibility, and mutual respect that unite generations across urban metropolises and rural communities.",
    ),
    "language_heritage": (
        "Living Dialects, Scripts & Oral Storytelling",
        "🗣️ Language: {language_heritage}",
        "Official Tongues • Linguistic Preservation",
        "The soul of {dest_name} is expressed through its rich linguistic inheritance: {language_heritage}. From ancient scripts to living regional dialects, linguistic traditions carry the oral lore and sovereign memory of the people.",
    ),
    "spiritual_heritage": (
        "Sacred Sanctuaries, Medieval Abbeys & Pluralism",
        "⛪ Faith: {spiritual_heritage}",
        "Sacred Sanctuaries • Historic Monasteries",
        "Rooted in deep contemplative traditions, {dest_name}'s spiritual landmarks include {spiritual_heritage}. These sacred stone sanctuaries and historic abbeys embody centuries of scholarly reflection, artistic illumination, and community solace.",
    ),
    "major_cities": (
        "Great Metropolises & Dynamic Regional Hubs",
        "🏙️ Regional Hubs: {major_cities}",
        "Regional Centers • Urban Skylines",
        "Beyond the capital city, {dest_name}'s economic and cultural life flourishes across dynamic regional metropolises: {major_cities}. Each regional hub serves as a distinctive provincial powerhouse of commerce, university education, arts, and civic identity.",
    ),
    "education_universities": (
        "Top Research Universities & Collegiate Excellence",
        "🎓 Universities: {universities}",
        "Collegiate Research • Academic Distinction",
        "Higher education and scientific advancement in {dest_name} are anchored by premier collegiate institutions, notably {universities}. These centers of academic distinction cultivate groundbreaking scientific research, technological patents, and generations of global scholars.",
    ),
    "science_inventions": (
        "Nobel Discoveries, Inventions & Space Horizons",
        "🔬 Inventions: {science_inventions}",
        "Nobel Laureates • Scientific Discovery",
        "A global contributor to human progress, {dest_name}'s scientific trailblazers have delivered transformative breakthroughs: {science_inventions}. These milestones of ingenuity have reshaped modern medicine, physics, and world technological standards.",
    ),
    "healthcare_longevity": (
        "Public Healthcare, Life Expectancy & Wellness",
        "🩺 Healthcare: {healthcare_longevity}",
        "Universal Health • High Life Expectancy",
        "Public health and human longevity in {dest_name} are supported by {healthcare_longevity}. A commitment to universal healthcare, active outdoor living, and preventative wellness sustains one of the highest qualities of life in the world.",
    ),
    # --- ACT III: ECONOMY, INFRASTRUCTURE & INDUSTRY ---
    "currency_wealth_fund": (
        "Sovereign Currency, Fiscal Reserves & Banking",
        "🪙 Currency: {currency_wealth_fund}",
        "Fiscal Stability • Sovereign Reserves",
        "Financial sovereignty and macroeconomic stability in {dest_name} are underpinned by {currency_wealth_fund}. Prudently managed capital markets and strategic national funds ensure long-term generational wealth and global investment security.",
    ),
    "economy_jobs": (
        "GDP Powerhouses, Innovation & Global Trade",
        "💼 Tech & Trade: {economy_jobs}",
        "High-Tech Corridors • Global Exports",
        "With a dynamic national economy, {dest_name} thrives across {economy_jobs}. Resilient trade corridors and knowledge-based industries attract international enterprise and support high-value employment across all provinces.",
    ),
    "agriculture_farming": (
        "Pastoral Valleys, Agritech & Bountiful Harvests",
        "🌾 Harvest: {agriculture}",
        "Sustainable Agritech • Export Markets",
        "Nourishing the population and world export markets, agricultural production in {dest_name} is celebrated for {agriculture}. Modern agritech practices combined with sustainable stewardship preserve soil vitality and ensure reliable food security.",
    ),
    "industry_manufacturing": (
        "Precision Engineering, Advanced Tech & Fabs",
        "🏭 Industry: {industry}",
        "Advanced Robotics • Clean Manufacturing",
        "Industrial capability in {dest_name} is driven by world-class precision engineering: {industry}. High-tech fabrication hubs, robotics, and export manufacturing establish the country as an indispensable global supplier.",
    ),
    "domestic_rail_transit": (
        "High-Speed Rail Networks & Commuter Transit",
        "🚆 Rail Transit: {domestic_rail_transit}",
        "Electrified Networks • Intercity Corridors",
        "Connecting urban metropolises to remote provinces, domestic transport is anchored by {domestic_rail_transit}. Highly efficient passenger rail and multimodal public transit ensure rapid, low-carbon mobility across the nation.",
    ),
    "ports_logistics": (
        "Deepwater Sea Harbors & Freight Terminals",
        "⚓ Maritime Ports: {ports}",
        "Global Shipping • Maritime Logistics",
        "Global maritime commerce flows through {dest_name}'s premier deepwater terminals: {ports}. These world-class port hubs facilitate seamless transshipment, container logistics, and strategic trade links to international waters.",
    ),
    "airports_aviation": (
        "International Aviation Gateways & Flight Hubs",
        "✈️ Aviation: {airports}",
        "Global Air Corridors • Hub Terminals",
        "Connecting the sovereign state to all continents, aviation infrastructure is anchored by {airports}. These state-of-the-art international airports process millions of passengers and air cargo shipments every year.",
    ),
    "clean_energy_grid": (
        "Renewable Energy, Wind, Hydro & Decarbonization",
        "⚡ Clean Grid: {clean_energy}",
        "Zero-Carbon Target • Grid Resilience",
        "Pioneering the green transition, {dest_name}'s electrical grid harnesses {clean_energy}. Rapid deployment of clean power sources advances national energy independence while safeguarding the planet for future generations.",
    ),
    "environmental_stewardship": (
        "Carbon Neutrality, Recycling & Conservation",
        "🌱 Eco: {environmental_stewardship}",
        "Circular Economy • Zero-Waste Targets",
        "Environmental preservation is a core civic commitment in {dest_name}: {environmental_stewardship}. Aggressive carbon neutrality goals, comprehensive circular recycling, and clean air mandates set international benchmarks in sustainability.",
    ),
    # --- ACT IV: CULTURE, GASTRONOMY, ARTS & HERITAGE ---
    "food_gastronomy": (
        "Farm-to-Table Gastronomy & Regional Culinary Lore",
        "🍲 Cuisine: {food}",
        "Culinary Heritage • Farm-to-Table",
        "Gastronomy in {dest_name} is an art form rooted in terroir and fresh local ingredients: {food}. Treasured family recipes passed across generations showcase the country's rich culinary hospitality.",
    ),
    "arts_literature": (
        "Fine Arts, Master Craftsmanship & Literary Icons",
        "🎨 Fine Arts: {arts}",
        "Literary Masters • National Galleries",
        "Artistic expression in {dest_name} is celebrated worldwide through {arts}. From classic literary luminaries to avant-garde contemporary galleries, creative genius flourishes at the core of national life.",
    ),
    "music_performing_arts": (
        "Musical Heritage, Symphonic Orchestras & Theatre",
        "🎵 Music: {music}",
        "Symphonic Halls • Folk Traditions",
        "The soundscape of {dest_name} resonates through {music}. Traditional acoustic melodies and renowned international concert halls celebrate the nation's profound performing arts lineage.",
    ),
    "national_sports": (
        "National Sporting Passion, Arenas & World Titles",
        "⚽ Sports: {national_sports}",
        "Championship Arenas • Youth Athletics",
        "Athletic excellence and national sporting passion in {dest_name} center upon {national_sports}. Iconic stadiums and spirited grassroots leagues unite the nation in healthy competition and international prestige.",
    ),
    "festivals_traditions": (
        "Annual Carnivals, Folk Celebrations & Public Holidays",
        "🎉 Festivals: {festivals_traditions}",
        "Living Folklore • Public Celebrations",
        "The cultural calendar of {dest_name} is enlivened by vibrant celebrations: {festivals_traditions}. These beloved annual carnivals and sacred traditions unite neighborhoods in joyful folk music, dance, and communal feasts.",
    ),
    # --- ACT V: NATURE, WILDLIFE, GEOPOLITICS & HORIZONS ---
    "national_parks": (
        "Untamed Wilderness, Glacial Fjords & Biospheres",
        "🌲 Wilderness: {parks}",
        "Protected Biospheres • Glacial Valleys",
        "Preserving pristine wilderness, {dest_name}'s crown natural sanctuaries encompass {parks}. These protected national reserves preserve endemic ecosystems, crystalline glacial waters, and ancient forests.",
    ),
    "wildlife_fauna": (
        "Protected Native Fauna, Birds & Marine Life",
        "🦌 Wildlife: {wildlife_fauna}",
        "Endemic Species • Habitat Protection",
        "The diverse natural habitats of {dest_name} shelter extraordinary wildlife: {wildlife_fauna}. Strict conservation laws and wilderness corridors safeguard these vital species for generations to come.",
    ),
    "beaches_coastal": (
        "Scenic Coastlines, Golden Sands & Offshore Atolls",
        "🏖️ Coast: {beaches}",
        "Coastal Sanctuaries • Marine Reserves",
        "The dramatic coastal frontiers of {dest_name} feature iconic marine environments: {beaches}. Sweeping coastal waters and tidal cliffs draw nature enthusiasts and marine researchers seeking untouched oceanic wilderness.",
    ),
    "defense_security": (
        "Sovereign Defense, Naval Patrol & Peacekeeping",
        "🛡️ Defense: {defense_security}",
        "Maritime Patrol • Armed Neutrality",
        "Sovereign security and emergency preparedness in {dest_name} are safeguarded by {defense_security}. Maintaining vigilance across national boundaries and territorial waters, these services protect citizens while championing international peace.",
    ),
    "politics_alliances": (
        "Global Diplomacy, Sovereign Alliances & Peacekeeping",
        "🌐 Alliances: {alliances}",
        "Diplomatic Treaties • International Accords",
        "On the world stage, {dest_name}'s foreign policy and global partnerships are defined by {alliances}. Through active multilateral participation, the nation upholds international rule of law, diplomatic dialogue, and humanitarian peace.",
    ),
    "global_diaspora": (
        "Worldwide Diaspora & International Soft Power",
        "🌍 Diaspora: {global_diaspora}",
        "Global Influence • Soft Power",
        "Extending far beyond territorial borders, {dest_name}'s global impact is amplified by {global_diaspora}. This international community fosters deep cross-border goodwill, cultural diplomacy, and global leadership.",
    ),
    "conclusion_future": (
        "Sovereign Resilience & The 21st-Century Horizon",
        "✨ Future: {future}",
        "Sovereign Resilience • Modern Vision",
        "Looking forward into the twenty-first century, {dest_name} charts its course through {future}. Rooted in the sovereign strength of its history and guided by visionary sustainable progress, the nation strides forward with lasting purpose.",
    ),
}

# Backwards-compatible aliases for 21-chapter key variations
CHAPTER_TEMPLATES["arts_crafts"] = CHAPTER_TEMPLATES["arts_literature"]
CHAPTER_TEMPLATES["music_entertainment"] = CHAPTER_TEMPLATES["music_performing_arts"]
CHAPTER_TEMPLATES["jobs_livelihood"] = CHAPTER_TEMPLATES["economy_jobs"]
CHAPTER_TEMPLATES["agriculture_harvest"] = CHAPTER_TEMPLATES["agriculture_farming"]
CHAPTER_TEMPLATES["trade_ports"] = CHAPTER_TEMPLATES["ports_logistics"]
CHAPTER_TEMPLATES["clean_energy"] = CHAPTER_TEMPLATES["clean_energy_grid"]
CHAPTER_TEMPLATES["food_culinary"] = CHAPTER_TEMPLATES["food_gastronomy"]
CHAPTER_TEMPLATES["beaches_resorts"] = CHAPTER_TEMPLATES["beaches_coastal"]

