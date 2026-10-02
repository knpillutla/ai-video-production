// CineAI Studio: Presets & Creative Templates Data Hub
const NICHE_RADIO_CONFIGS = {
  // Relaxation & Ambient Group
  relax_ocean: {
    prompt: "Gentle Ocean Waves & Coastal Sunset - Rolling crystalline swells, golden horizon reflections, soothing binaural tide ebb and flow",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },
  relax_nature: {
    prompt: "Untamed Emerald Rainforest & Whispering Canopy - Dewdrop glistens on mossy boulders, gentle breeze through towering ancient pines",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },
  relax_mountains: {
    prompt: "Majestic Swiss Alpine Peaks & Morning Mist - Glacial mountain reflections in mirrored lakes, tranquil alpine meadow breeze",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },
  relax_campfire: {
    prompt: "Cozy Log Cabin Hearth & Crackling Campfire - Deep amber embers, glowing pine logs, soft snowfall outside panoramic window, warm ASMR",
    bgm: false, voice: false, pureNature: true, fps: "24", channel: "silent_hearth"
  },
  relax_rain: {
    prompt: "Calming Forest River Rain & Distant Thunder - Gentle steady rain falling on broad leaves, tranquil stream ripples, cozy atmospheric soundscape",
    bgm: false, voice: false, pureNature: true, fps: "24", channel: "earth_serenade"
  },
  relax_serenity: {
    prompt: "Kyoto Zen Rock Garden & Sacred Lotus Pond - Smooth bamboo water fountain drops, raked gravel ripples, 432Hz harmonic acoustic peace",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },
  relax_retreat: {
    prompt: "Biophilic Forest Terrace Sanctuary - Open glass pavilion, lush tropical greenery, cedar wood deck, serene meditation atmosphere",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },
  relax_architecture: {
    prompt: "Minimalist Modern Alpine Villa & Infinity Pool - Clean architectural lines, panoramic mountain vistas, warm evening lighting",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "silent_hearth"
  },
  relax_beaches: {
    prompt: "Secluded Tropical White Sand Beach & Turquoise Lagoon - Gentle crystal wave wash, swaying palm fronds, warm sea breeze",
    bgm: true, voice: false, pureNature: false, fps: "24", channel: "earth_serenade"
  },

  // Blue-Chip Documentaries Group
  doc_wildlife: {
    prompt: "African Savannah Predators & Migration - Lion prides resting under acacia trees, cheetah high-speed pursuit, wildebeest river crossings",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  },
  doc_nature: {
    prompt: "Ancient Redwood Giants & Temperate Rainforest Ecology - Towering 300ft canopy, endemic salamanders, macro moisture cycles, rich narration",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  },
  doc_ocean: {
    prompt: "Deep Coral Reef Ecosystems & Pelagic Giants - Bioluminescent abyssal creatures, humpback whale pods, vibrant shallow reef biodiversity",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  },
  doc_architecture: {
    prompt: "Eternal Granite Temples & Sacred Ancient Geometry - Dravidian gopuram carvings, monumental acoustic corridors, lost empire engineering",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  },
  doc_beaches: {
    prompt: "Coastal Geological Formations & Tidal Ecosystems - Dramatic sea stacks, marine iguana foraging, erosion forces carving rugged cliffs",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  },
  doc_mountains: {
    prompt: "Himalayan High-Altitude Nomads & Glacial Extremes - Sub-zero survival, snow leopard territory, high mountain passes and prayer flags",
    bgm: true, voice: true, pureNature: false, fps: "24", channel: "cineai_docs"
  }
};

const TEMPLATES_BY_MODE = {
  theme: [
    { id: "rain_walk", badge: "World Walking", title: "Walking in the Rain", desc: "Dynamic world tour: Kyoto, Hallstatt, Amalfi Coast, Tokyo, London.", prompt: "Walking in the Rain - Atmosphere, reflections, architecture and serene raindrops" },
    { id: "nature", badge: "Nature", title: "Untamed Rainforests", desc: "Canopy mist, emerald gorges and mountain cascades.", prompt: "Untamed Rainforests & Mountain Waterfalls - Lush canopies, emerald gorges and crystalline river cascades" },
    { id: "wildlife", badge: "Animals", title: "African Wildlife Safari", desc: "Cheetah sprints, elephant herds and river migration.", prompt: "African Wildlife Safari - Lion prides, cheetah sprints and wildebeest river crossing across the golden savannah" },
    { id: "heritage", badge: "Heritage", title: "India in 4K Heritage", desc: "Dravidian granite temples, royal palaces and ghats.", prompt: "India in 4K - Eternal Wonders, Dravidian temple architecture and royal Rajasthani palaces" }
  ],
  idea: [
    { id: "comedy", badge: "Comedy", title: "Delhi Techie Moonlighting", desc: "Engineer discreetly juggling two US remote jobs with frantic calendar panic.", prompt: "A sharp Gurgaon engineer discreetly juggles two high-paying US remote jobs with frantic calendar acrobatics and hilarious near-misses" },
    { id: "scifi", badge: "Sci-Fi", title: "Quantum Barista", desc: "Coffee machine that brews beverages tuned to alternate dimensional memories.", prompt: "A Bengaluru barista discovers their espresso machine brews beverages tuned to customers' alternate dimensional memories" },
    { id: "culinary", badge: "Street Food", title: "Roadside Chai Chemistry", desc: "Thermodynamic physics and emulsion of cutting chai in 60s.", prompt: "The thermodynamic physics and sensory cultural chemistry behind brewing the perfect roadside cutting chai in 60 seconds" },
    { id: "startup", badge: "Drama", title: "Pitch Deck Panic", desc: "AI model starts quoting ancient philosophy 5 minutes before Tier-1 VC pitch.", prompt: "Three nervous founders discover their production AI model started quoting ancient philosophy 5 minutes before a Tier-1 VC pitch" }
  ],
  script: [
    { id: "monologue", badge: "Voiceover", title: "Living Stone Spire", desc: "Dawn ascent reveals carved granite gopurams catching morning amber.", prompt: "SCENE 1 (EXT. THANJAVUR TEMPLE - SUNRISE):\nA slow drone ascent reveals carved granite gopurams catching morning amber.\nNARRATOR: Carved from living stone, India's sacred geometry transcends time." },
    { id: "dialogue", badge: "Dialogue", title: "Dual Standup Sprint", desc: "Two laptops open side-by-side with comedic overlapping webcam calls.", prompt: "SCENE 1 (INT. GURGAON APARTMENT - 9:00 PM):\nTwo laptops open side-by-side with webcams.\nRAMESH: (Whispering) Deployment running... Hi Sarah, sprint velocity update!\nMEENA: (Off-screen) Ramesh, client on line two!" },
    { id: "explainer", badge: "Explainer", title: "Spice Emulsion Beat", desc: "Macro close-up steam cinematography and narration.", prompt: "SCENE 1 (EXT. STREET CHAI STALL - MORNING):\nFresh ginger root cracks under brass mortar. Whole cloves hit boiling water.\nNARRATOR: At 100°C, milk fats emulsify with cardamom, unleashing spice alchemy." },
    { id: "drama", badge: "Drama Beat", title: "The Midnight Deploy", desc: "Tense final deploy sequence in a glass-walled startup office.", prompt: "SCENE 1 (INT. STARTUP HQ - 11:59 PM):\nGlowing monitors cast blue shadows.\nVIKRAM: (Hovering over Enter) If we push this migration, we double revenue or brick fifty thousand servers.\nANANYA: Hit it." }
  ],
  youtube: [
    { id: "yt_drone", badge: "Drone 4K", title: "India 4K Drone Styling", desc: "Apply drone cinematography, golden lighting & sitar BGM.", prompt: "India in 4K - Apply drone aerials, golden-hour temple lighting, and sitar soundtrack", url: "https://www.youtube.com/watch?v=-BLxlHRYpac" },
    { id: "yt_vlog", badge: "Travel Vlog", title: "Malaysia Vistas", desc: "Tropical rainforest canopy drone vistas and night markets.", prompt: "Malaysia in 4K - Tropical rainforest canopy drone vistas, bustling night markets & modern architecture", url: "https://www.youtube.com/watch?v=-BLxlHRYpac" },
    { id: "yt_asmr", badge: "Macro ASMR", title: "Culinary Macro ASMR", desc: "Macro close-up steam, warm amber tones and percussive tabla.", prompt: "Culinary Street Craft - Macro close-up steam cinematography, warm amber lighting, rhythmic acoustic tabla", url: "https://www.youtube.com/watch?v=-BLxlHRYpac" },
    { id: "yt_tech", badge: "Fast Cuts", title: "Tech Startup Satire", desc: "Split-screen video call graphics and playful percussive score.", prompt: "Tech Startup Satire - Fast-paced comedy cuts, split-screen video call graphics, playful percussive score", url: "https://www.youtube.com/watch?v=-BLxlHRYpac" }
  ]
};

const MODE_STARTERS = {
  theme: "Gentle Ocean Waves & Coastal Sunset - Rolling crystalline swells, golden horizon reflections, soothing binaural tide ebb and flow",
  idea: "Delhi techie juggling dual remote jobs comedy satire",
  script: "SCENE 1: EXT. KITCHEN - DAY\nBoiling spiced masala chai heat transfer in 60s",
  youtube: "https://www.youtube.com/watch?v=-BLxlHRYpac"
};

const ALL_STUDIO_GENRES = {
  "relax/nature": "🏔️ Nature & Alpine Sanctuaries (relax/nature)",
  "relax/healing": "✨ Global Healing Sanctuaries & 528Hz (relax/healing)",
  "relax/zen": "🪷 Japanese Zen Gardens & Engawa (relax/zen)",
  "relax/waterfall": "🌊 Monumental Waterfall & Cataracts (relax/waterfall)",
  "relax/hearth": "🔥 Beach Campfire & Shoreline Hearth (relax/hearth)",
  "relax/rain": "🌧️ Rain Retreat & River ASMR (relax/rain)",
  "relax/cozy": "🪵 Cozy Living Spaces & Fireplace (relax/cozy)",
  "relax/ambient": "🌌 Velvet Ambient World 14 Archetypes (relax/ambient)",
  "documentary": "🦅 BBC-Style 24fps Wildlife & Documentary (documentary)",
  "travel_walking": "🚶 Travel & 4K 60fps Walking Tours (travel_walking)",
  "dance/folk": "💃 Dance, Folk & Music Videos (dance/folk)",
  "comedy/satire": "🎭 Telugu Comedy & Satire Shorts (comedy/satire)"
};

const DEFAULT_CHANNEL_GENRES = {
  "earth_serenade": ["relax/nature", "relax/healing", "relax/zen", "relax/waterfall", "relax/ambient"],
  "silent_hearth": ["relax/hearth", "relax/rain", "relax/cozy"],
  "cineai_docs": ["documentary"],
  "telugu_comedy": ["comedy/satire", "dance/folk"]
};

const STUDIO_SUBOPTIONS_MAP = {
  "relax/nature": [{ val: "alpine_nature", label: "🏔️ Alpine Nature & Mountain Sanctuaries (Swiss Alps)" }, { val: "glacial_fjord_lake", label: "🛶 Glacial Mirror Lakes & Fjords" }, { val: "temperate_forest", label: "🌲 Temperate Mossy Rainforest & Streams" }],
  "relax/rain": [{ val: "forest_rain", label: "🌧️ Forest River Rainfall & ASMR" }, { val: "veranda_rain", label: "🏡 Biophilic Glass Veranda Rain" }, { val: "droplet_ripples", label: "💧 Water Droplet Ripples & Lake Reflections" }],
  "relax/waterfall": [{ val: "waterfall_gorge", label: "🌊 Monumental Plunge Cataracts (Niagara / Iguazu)" }, { val: "tiered_cascade", label: "🏞️ Multi-Tiered Glacial Cascades (Plitvice)" }],
  "relax/hearth": [{ val: "cozy_hearth", label: "🔥 Open-Air Beach Campfire & Shoreline Hearth" }, { val: "stone_hearth", label: "🪵 Rustic Cabin Stone Fireplace" }],
  "relax/cozy": [{ val: "biophilic_living", label: "🪵 Biophilic Living Space & Terraces" }, { val: "rainy_patio", label: "☕ Rainy Garden Patio & Warm Hearth" }],
  "relax/healing": [{ val: "global_healing", label: "✨ Global Sacred Sanctuaries & 528Hz Solfeggio" }, { val: "himalayan_valley", label: "🏔️ Himalayan Singing Bowl Valley & Mist" }, { val: "geothermal_springs", label: "♨️ Geothermal Hot Springs & Travertine Pools" }, { val: "redwood_cathedral", label: "🌲 Ancient Redwood Grove Sanctuary" }],
  "relax/zen": [{ val: "zen_garden", label: "🪷 Kyoto Zen Temple & Raked Rock Garden" }, { val: "bamboo_grove", label: "🎋 Sagano Bamboo Grove & Tsukubai Basin" }, { val: "lotus_pond", label: "🪷 Sacred Lotus Pond & Water Basin Flow" }],
  "relax/ambient": [{ val: "ambient_soundscape", label: "🌌 Velvet Ambient World (14 Ecosystems)" }, { val: "twilight_sanctuary", label: "✨ Twilight Aurora & Velvet Night Sky" }],
  "documentary": [{ val: "cinematic_doc", label: "🦅 BBC-Style 24fps Wildlife & Climate Expedition" }, { val: "volcano_arctic", label: "🌋 Volcanic Landscapes & Glacial Ice" }, { val: "ocean_depths", label: "🐋 Deep Marine Life & Coral Reefs" }],
  "travel_walking": [{ val: "alpine_village_walk", label: "🏡 Swiss Alpine Countryside Walk (1.5 km/h)" }, { val: "city_walk_pov", label: "🏙️ 4K 60fps Historic City & Night Walk" }, { val: "coastal_promenade", label: "🏖️ Secluded Ocean Bluff Walk" }],
  "dance/folk": [{ val: "mass_folk_dance", label: "💃 High-Energy Mass Folk Dance (30fps)" }, { val: "classical_dance", label: "🪘 Cultural Classical Choreography" }],
  "comedy/satire": [{ val: "satirical_short", label: "🎭 Modern Satire & Relatable Comedy Short" }]
};

const STUDIO_SUBGENRE_PLACEHOLDERS = {
  alpine_nature: "e.g. Majestic Swiss Alps panoramic peaks, wildflower valley, and crystal glacial stream...",
  glacial_fjord_lake: "e.g. Glassy mirror-still turquoise glacial lake reflecting towering forested cliffs...",
  temperate_forest: "e.g. Ancient mossy rainforest and gentle babbling river over rounded stones...",
  forest_rain: "e.g. Gentle rain falling on mossy temperate rainforest river and floating leaf ripples...",
  veranda_rain: "e.g. Biophilic glass veranda overlooking misty mountain forest during gentle twilight rainfall...",
  droplet_ripples: "e.g. Ultra-macro 4K raindrops creating concentric ripples on mirror-still mountain pond...",
  waterfall_gorge: "e.g. Monumental cascading cataract with heavy rising mist and turquoise plunge pool...",
  tiered_cascade: "e.g. Multi-tiered emerald forest cascades flowing gently over moss-covered limestone ledges...",
  cozy_hearth: "e.g. Gentle night rain on cozy stone campfire burning on wet pebble beach by ocean surf...",
  stone_hearth: "e.g. Glowing cedar log hearth in rustic mountain stone lodge with snowy forest view...",
  biophilic_living: "e.g. Modern biophilic living terrace with warm glowing fire and lush interior plants...",
  rainy_patio: "e.g. Cozy sheltered patio with amber lanterns and rain pattering softly on foliage...",
  zen_garden: "e.g. Tranquil Kyoto dry raked stone karesansui garden, weathered cedar engawa, and mossy stone lanterns...",
  bamboo_grove: "e.g. Ethereal Sagano bamboo grove with gentle morning mist, tsukubai water basin, and shakuhachi tones...",
  lotus_pond: "e.g. Sacred temple lotus pond with blooming water lilies and gentle bamboo fountain...",
  global_healing: "e.g. Sacred mountain sanctuary with 528Hz Solfeggio sound therapy, crystal bowls, and morning sunlight...",
  himalayan_valley: "e.g. Misty Himalayan sacred valley with Tibetan singing bowls, prayer flags, and glacial stream...",
  geothermal_springs: "e.g. Natural turquoise geothermal travertine mineral pools with soft rising steam vapors in Tuscany...",
  redwood_cathedral: "e.g. Ancient giant California Redwood grove cathedral with sunbeams piercing morning mist...",
  ambient_soundscape: "e.g. Majestic 4K nature living wallpaper with tranquil mountain valley morning glow...",
  twilight_sanctuary: "e.g. Ethereal twilight mountain sanctuary under soft purple skies and velvet stars...",
  cinematic_doc: "e.g. BBC-style 24fps cinematic wildlife documentary across rugged alpine peaks...",
  volcano_arctic: "e.g. Dramatic volcanic black sand coast meets glacial blue ice caves...",
  ocean_depths: "e.g. Deep marine coral reefs with schools of luminous fish in crystal blue waters...",
  alpine_village_walk: "e.g. Ultra-slow 1.5 km/h human walking tour through Swiss alpine village and meadow path...",
  city_walk_pov: "e.g. 4K 60fps tranquil historic European cobblestone street walk at twilight...",
  mass_folk_dance: "e.g. High-energy festive village celebration with dynamic troupe choreography...",
  satirical_short: "e.g. Relatable everyday comedy satire with sharp comedic timing and witty dialogue..."
};

const STUDIO_ARCHETYPE_HINTS = {
  alpine_mountains: "e.g. Towering Swiss Alps snow-capped jagged peaks, lush wildflower meadows, and crystal mountain stream...",
  waterfall_gorge: "e.g. Monumental roaring cataract plunging into turquoise pool with heavy rising mist...",
  coastal_ocean: "e.g. Gentle rain falling on warm driftwood campfire burning on wet pebble shoreline by ocean surf...",
  glacial_fjord_lake: "e.g. Mirror-still turquoise glacial lake reflecting towering pine-covered granite cliffs...",
  temperate_forest: "e.g. Ancient mossy rainforest canopy with gentle stream and floating leaves...",
  zen_garden: "e.g. Peaceful Kyoto dry raked stone garden, bamboo water fountain, and cedar veranda...",
  sacred_sanctuary: "e.g. Sacred Himalayan valley with singing bowls, crystal dawn sunbeams, and restorative 528Hz serenity..."
};
