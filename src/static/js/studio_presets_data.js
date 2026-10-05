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
  "relax/ocean": "🏖️ Ocean Retreat & Coastal Sanctuaries (relax/ocean)",
  "relax/beach_lounge": "🏖️ Luxury Beach Lounge & Cabana (relax/beach_lounge)",
  "relax/desert": "🏜️ Luxury Desert Glamping & Dunes (relax/desert)",
  "relax/mountain": "🏔️ Mountain Peaks & High Alpine (relax/mountain)",
  "relax/valley": "🌸 Pastoral Valleys & Wildflower Meadows (relax/valley)",
  "relax/blizzard": "❄️ Alpine Blizzard & Winter Snowstorms (relax/blizzard)",
  "relax/forest": "🌲 Ancient Forest & Komorebi Sunbeams (relax/forest)",
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
  "earth_serenade": ["relax/ocean", "relax/beach_lounge", "relax/desert", "relax/mountain", "relax/valley", "relax/blizzard", "relax/forest", "relax/rain", "relax/nature", "relax/healing", "relax/zen", "relax/waterfall", "relax/ambient"],
  "silent_hearth": ["relax/hearth", "relax/rain", "relax/cozy", "relax/blizzard"],
  "cineai_docs": ["documentary"],
  "telugu_comedy": ["comedy/satire", "dance/folk"]
};

const STUDIO_SUBOPTIONS_MAP = {
  "relax/ocean": [{ val: "ocean_daytime_shore", label: "☀️ Overwater Villa & Daytime Lagoon" }, { val: "ocean_sunrise_coast", label: "🌅 Coastal Veranda & Pastel Dawn" }, { val: "ocean_sunset_horizon", label: "🌇 Cliffside Sanctuary & Golden Hour Sunset" }, { val: "ocean_night_bioluminescent", label: "🌌 Starlit Beach Pavilion & Bioluminescent Waves" }, { val: "ocean_campfire_hearth", label: "🔥 Open-Air Beach Campfire & Surf" }, { val: "ocean_tropical_rain", label: "🌧️ Sheltered Balcony & Tropical Ocean Rain" }],
  "relax/beach_lounge": [{ val: "beach_luxury_cabana_day", label: "☀️ Luxury Beach Cabana & Daytime Turquoise Surf" }, { val: "beach_sunset_terrace", label: "🌇 Sunset Beach Terrace & Golden Hour Horizon" }, { val: "beach_twilight_pergola", label: "🌆 Twilight Beach Pergola & Gentle Waves" }, { val: "beach_starlit_hammock", label: "🌌 Starlit Beachfront Hammock & Night Surf" }],
  "relax/desert": [{ val: "desert_daytime_tent", label: "☀️ Luxury Desert Tent & Daytime Dunes" }, { val: "desert_sunrise_tent", label: "🌅 Luxury Desert Tent & Sunrise Dawn" }, { val: "desert_sunset_tent", label: "🌇 Luxury Desert Tent & Golden Sunset" }, { val: "desert_night_tent", label: "🌌 Luxury Desert Tent & Starlit Milky Way" }, { val: "desert_campfire_hearth", label: "🔥 Desert Campfire & Bedouin Hearth" }, { val: "desert_rain_sanctuary", label: "🌧️ Luxury Desert Tent & Rain ASMR" }],
  "relax/mountain": [{ val: "mountain_daytime_vista", label: "☀️ Panoramic High Alpine Vista" }, { val: "mountain_summit_dawn", label: "🌅 Alpine Summit Sunrise Dawn" }, { val: "mountain_sunset_alpenglow", label: "🌇 Alpenglow Sunset & Granite Peaks" }, { val: "mountain_starlit_ridge", label: "🌌 Starlit Mountain Ridge & Milky Way" }],
  "relax/valley": [{ val: "valley_wildflower_meadow", label: "🌸 Wildflower Meadow & Alpine Stream" }, { val: "valley_morning_mist", label: "🌅 Misty Pastoral Valley Sunrise" }, { val: "valley_glacial_stream", label: "💧 Crystal Glacial Valley Stream" }, { val: "valley_sunset_pastoral", label: "🌇 Pastoral Valley Golden Sunset" }],
  "relax/blizzard": [{ val: "blizzard_cozy_cabin_window", label: "🪟 Cozy Timber Cabin Window & Blizzard Winds" }, { val: "blizzard_frosted_pine_forest", label: "🌲 Frosted Pine Forest & Heavy Snowdrift" }, { val: "blizzard_alpine_hearth_shelter", label: "🔥 Alpine Stone Shelter & Glowing Hearth Fire" }, { val: "blizzard_twilight_snowfall", label: "❄️ Twilight Alpine Cabin & Heavy Snowfall" }],
  "relax/forest": [{ val: "forest_mossy_canopy_day", label: "🌲 Emerald Mossy Canopy & Crystalline Stream" }, { val: "forest_babbling_brook", label: "💧 Babbling Forest Brook & Fern Glade" }, { val: "forest_morning_sunbeams", label: "✨ Morning Komorebi Sunbeams & Ancient Pines" }, { val: "forest_twilight_fireflies", label: "🌌 Twilight Enchanted Forest & Gentle Mist" }],
  "relax/nature": [{ val: "alpine_nature", label: "🏔️ Alpine Nature & Mountain Sanctuaries (Swiss Alps)" }, { val: "glacial_fjord_lake", label: "🛶 Glacial Mirror Lakes & Fjords" }, { val: "temperate_forest", label: "🌲 Temperate Mossy Rainforest & Streams" }],
  "relax/rain": [{ val: "rainy_bedroom", label: "🛏️ Rainy Forest Bedroom & Glass Cabin" }, { val: "forest_rain", label: "🌧️ Forest River Rainfall & ASMR" }, { val: "veranda_rain", label: "🏡 Biophilic Glass Veranda Rain" }, { val: "droplet_ripples", label: "💧 Water Droplet Ripples & Lake Reflections" }],
  "relax/waterfall": [{ val: "waterfall_gorge", label: "🌊 Monumental Plunge Cataracts (Niagara / Iguazu)" }, { val: "tiered_cascade", label: "🏞️ Multi-Tiered Glacial Cascades (Plitvice)" }],
  "relax/hearth": [{ val: "cozy_hearth", label: "🔥 Open-Air Beach Campfire & Shoreline Hearth" }, { val: "stone_hearth", label: "🪵 Rustic Cabin Stone Fireplace" }, { val: "rainy_hearth_bedroom", label: "🛏️ Rainy Cabin Bedroom with Hearth Fireplace" }],
  "relax/cozy": [{ val: "cabin_bedroom", label: "🛏️ Cozy Glass Cabin Bedroom & Rain on Window" }, { val: "biophilic_living", label: "🪵 Biophilic Living Space & Terraces" }, { val: "rainy_patio", label: "☕ Rainy Garden Patio & Warm Hearth" }],
  "relax/healing": [{ val: "global_healing", label: "✨ Global Sacred Sanctuaries & 528Hz Solfeggio" }, { val: "himalayan_valley", label: "🏔️ Himalayan Singing Bowl Valley & Mist" }, { val: "geothermal_springs", label: "♨️ Geothermal Hot Springs & Travertine Pools" }, { val: "redwood_cathedral", label: "🌲 Ancient Redwood Grove Sanctuary" }],
  "relax/zen": [{ val: "zen_garden", label: "🪷 Kyoto Zen Temple & Raked Rock Garden" }, { val: "bamboo_grove", label: "🎋 Sagano Bamboo Grove & Tsukubai Basin" }, { val: "lotus_pond", label: "🪷 Sacred Lotus Pond & Water Basin Flow" }],
  "relax/ambient": [{ val: "ambient_soundscape", label: "🌌 Velvet Ambient World (14 Ecosystems)" }, { val: "twilight_sanctuary", label: "✨ Twilight Aurora & Velvet Night Sky" }],
  "documentary": [{ val: "cinematic_doc", label: "🦅 BBC-Style 24fps Wildlife & Climate Expedition" }, { val: "volcano_arctic", label: "🌋 Volcanic Landscapes & Glacial Ice" }, { val: "ocean_depths", label: "🐋 Deep Marine Life & Coral Reefs" }],
  "travel_walking": [{ val: "alpine_village_walk", label: "🏡 Swiss Alpine Countryside Walk (1.5 km/h)" }, { val: "rain_walking_tour", label: "🌧️ 4K Rain Walking Tour (Puddles & Wet Street Reflections)" }, { val: "city_walk_pov", label: "🏙️ 4K 60fps Historic City & Night Walk" }, { val: "coastal_promenade", label: "🏖️ Secluded Ocean Bluff Walk" }],
  "dance/folk": [{ val: "mass_folk_dance", label: "💃 High-Energy Mass Folk Dance (30fps)" }, { val: "classical_dance", label: "🪘 Cultural Classical Choreography" }],
  "comedy/satire": [{ val: "satirical_short", label: "🎭 Modern Satire & Relatable Comedy Short" }]
};

const STUDIO_SUBGENRE_PLACEHOLDERS = {
  alpine_nature: "e.g. Majestic Swiss Alps panoramic peaks, wildflower valley, and crystal glacial stream...",
  glacial_fjord_lake: "e.g. Glassy mirror-still turquoise glacial lake reflecting towering forested cliffs...",
  temperate_forest: "e.g. Ancient mossy rainforest and gentle babbling river over rounded stones...",
  rainy_bedroom: "e.g. Cozy glass cabin bedroom in a misty pine forest during heavy rainfall, warm bedside lamp (2700K), rain on window...",
  cabin_bedroom: "e.g. Warm biophilic timber glass cabin bedroom overlooking rainy forest, plush duvet, and steaming tea mug...",
  rainy_hearth_bedroom: "e.g. Intimate timber bedroom with glowing stone hearth fireplace, soft bed, and steady rain on windowpanes...",
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

const STUDIO_ARCHETYPES_MAP = {
  "relax/ocean": [{ val: "ocean_daytime_shore", label: "☀️ Overwater Villa (Lagoon)" }, { val: "ocean_sunrise_coast", label: "🌅 Coastal Veranda (Dawn)" }, { val: "ocean_sunset_horizon", label: "🌇 Cliffside Sanctuary (Sunset)" }, { val: "ocean_night_bioluminescent", label: "🌌 Beach Pavilion (Bioluminescent)" }, { val: "ocean_campfire_hearth", label: "🔥 Beach Campfire & Surf" }, { val: "ocean_tropical_rain", label: "🌧️ Sheltered Balcony (Rain ASMR)" }],
  "relax/beach_lounge": [{ val: "beach_luxury_cabana_day", label: "☀️ Luxury Beach Cabana" }, { val: "beach_sunset_terrace", label: "🌇 Sunset Beach Terrace" }, { val: "beach_twilight_pergola", label: "🌆 Twilight Beach Pergola" }, { val: "beach_starlit_hammock", label: "🌌 Starlit Beachfront Hammock" }],
  "relax/desert": [{ val: "desert_daytime_tent", label: "☀️ Luxury Desert Tent (Dunes)" }, { val: "desert_sunrise_tent", label: "🌅 Luxury Desert Tent (Sunrise)" }, { val: "desert_sunset_tent", label: "🌇 Luxury Desert Tent (Sunset)" }, { val: "desert_night_tent", label: "🌌 Luxury Desert Tent (Milky Way)" }, { val: "desert_campfire_hearth", label: "🔥 Desert Campfire & Hearth" }, { val: "desert_rain_sanctuary", label: "🌧️ Desert Rain Sanctuary ASMR" }],
  "relax/mountain": [{ val: "mountain_daytime_vista", label: "☀️ High Alpine Vista" }, { val: "mountain_summit_dawn", label: "🌅 Summit Sunrise Dawn" }, { val: "mountain_sunset_alpenglow", label: "🌇 Alpenglow Sunset" }, { val: "mountain_starlit_ridge", label: "🌌 Starlit Mountain Ridge" }],
  "relax/valley": [{ val: "valley_wildflower_meadow", label: "🌸 Wildflower Meadow" }, { val: "valley_morning_mist", label: "🌅 Misty Valley Sunrise" }, { val: "valley_glacial_stream", label: "💧 Glacial Valley Stream" }, { val: "valley_sunset_pastoral", label: "🌇 Pastoral Sunset" }],
  "relax/blizzard": [{ val: "blizzard_cozy_cabin_window", label: "🪟 Cozy Cabin Window" }, { val: "blizzard_frosted_pine_forest", label: "🌲 Frosted Pine Forest" }, { val: "blizzard_alpine_hearth_shelter", label: "🔥 Alpine Hearth Shelter" }, { val: "blizzard_twilight_snowfall", label: "❄️ Twilight Snowfall" }],
  "relax/forest": [{ val: "forest_mossy_canopy_day", label: "🌲 Emerald Mossy Canopy" }, { val: "forest_babbling_brook", label: "💧 Babbling Forest Brook" }, { val: "forest_morning_sunbeams", label: "✨ Morning Sunbeams" }, { val: "forest_twilight_fireflies", label: "🌌 Twilight Fireflies" }],
  "relax/nature": [{ val: "alpine_peaks_meadow", label: "🏔️ Swiss Alps Peaks & Meadow" }, { val: "glacial_mirror_lake", label: "🛶 Glacial Mirror Lake" }, { val: "temperate_mossy_forest", label: "🌲 Mossy Rainforest & Stream" }, { val: "dolomites_panoramic", label: "⛰️ Dolomite Granite Spires" }],
  "relax/rain": [{ val: "rainy_cabin_bedroom", label: "🛏️ Glass Cabin Bedroom" }, { val: "misty_forest_stream", label: "🌲 Rainforest Glacial Stream" }, { val: "biophilic_veranda", label: "🏡 Biophilic Covered Veranda" }, { val: "rainy_attic_loft", label: "🕯️ Rain on Skylight Attic" }, { val: "lake_reflection_rain", label: "💧 Mirror Mountain Pond" }],
  "relax/waterfall": [{ val: "monumental_plunge", label: "🌊 Roaring Cataract Plunge" }, { val: "tiered_mossy_cascade", label: "🏞️ Multi-Tiered Cascades" }, { val: "icelandic_canyon_fall", label: "🌋 Basalt Column Waterfall" }],
  "relax/hearth": [{ val: "pebble_beach_shore", label: "🏖️ Pebble Shore Fire Ring" }, { val: "cliffside_stone_hearth", label: "🌊 Cliffside Stone Hearth" }, { val: "driftwood_cove_fire", label: "🪵 Driftwood Cove Fire" }, { val: "rainy_hearth_bedroom", label: "🛏️ Cabin Hearth Bedroom" }],
  "relax/cozy": [{ val: "glass_cabin_bedroom", label: "🛏️ Biophilic Bedroom & Rain" }, { val: "mountain_chalet_living", label: "🪵 Chalet Living & Fireplace" }, { val: "rainy_patio_terrace", label: "☕ Garden Patio & Hearth" }, { val: "library_reading_nook", label: "📚 Reading Nook & Soft Rain" }],
  "relax/healing": [{ val: "himalayan_valley", label: "🏔️ Himalayan Valley & Bowls" }, { val: "geothermal_mineral_pool", label: "♨️ Geothermal Mineral Pools" }, { val: "redwood_cathedral", label: "🌲 Redwood Grove Cathedral" }, { val: "bali_sacred_water", label: "✨ Bali Sacred Water Temple" }],
  "relax/zen": [{ val: "karesansui_temple", label: "🪷 Kyoto Raked Stone Garden" }, { val: "sagano_bamboo_basin", label: "🎋 Bamboo Grove & Basin" }, { val: "sacred_lotus_pond", label: "🪷 Sacred Lotus Pond & Koi" }],
  "relax/ambient": [{ val: "nordic_aurora_fjord", label: "🌌 Nordic Aurora Borealis" }, { val: "twilight_alpine_valley", label: "✨ Velvet Twilight Cabin" }, { val: "desert_oasis_starlight", label: "🏜️ Desert Oasis & Milky Way" }, { val: "biophilic_greenhouse", label: "🌿 Greenhouse & Velvet Rain" }],
  "documentary": [{ val: "alpine_tundra_wildlife", label: "🦅 High Alpine Glacial Ridge" }, { val: "arctic_ice_shelf", label: "🧊 Arctic Sea Ice Shelf" }, { val: "volcanic_geothermal", label: "🌋 Volcanic Black Sand Dunes" }, { val: "deep_ocean_trench", label: "🐋 Deep Sea Coral Abyss" }],
  "travel_walking": [{ val: "rain_city_walk", label: "🌧️ 4K Rain Walking Tour" }, { val: "swiss_village_walk", label: "🏡 Swiss Alpine Village Lane" }, { val: "historic_old_town", label: "🏙️ Historic Old Town Street" }, { val: "coastal_bluff_trail", label: "🏖️ Coastline Cliffside Trail" }, { val: "bamboo_forest_path", label: "🎋 Bamboo Grove Walking Path" }],
  "dance/folk": [{ val: "village_jathara_square", label: "🎪 Village Fairground Stage" }, { val: "lush_paddy_fields", label: "🌾 Verdant Paddy Fields" }, { val: "historic_fort_courtyard", label: "🏛️ Ancient Stone Fort" }, { val: "modern_city_rooftop", label: "🌆 Neon City Rooftop Stage" }],
  "comedy/satire": [{ val: "it_wfh_apartment", label: "💻 Modern Apartment WFH Office" }, { val: "street_chai_stall", label: "☕ Bustling Street Chai Stall" }, { val: "village_panchayat_tree", label: "🌳 Village Banyan Tree Chhavadi" }, { val: "corporate_meeting_room", label: "🏢 Corporate Conference Room" }]
};

const STUDIO_ARCHETYPE_HINTS = {
  ocean_daytime_shore: "e.g. Shaded deck of luxury overwater villa looking out at vast turquoise lagoon and rolling waves in bright 5500K daylight, sheer curtains...",
  ocean_sunrise_coast: "e.g. Dawn view from Mediterranean coastal veranda, sun rising over ocean horizon, steaming coffee on stone ledge, pastel morning sea mist...",
  ocean_sunset_horizon: "e.g. Sunset golden hour from stone cliffside terrace, fiery molten gold horizon reflecting across rolling Pacific swells, evening breeze...",
  ocean_night_bioluminescent: "e.g. Midnight open-air beachfront cabana looking out at gentle dark ocean waves glowing with electric-blue bioluminescence, starlit sky...",
  ocean_campfire_hearth: "e.g. Cozy driftwood campfire burning in beach stone pit at dark twilight, rhythmic dark ocean surf in immediate background...",
  ocean_tropical_rain: "e.g. Sheltered teak balcony during warm tropical rain, gentle raindrops creating ripples across calm turquoise ocean, rain ASMR...",
  beach_luxury_cabana_day: "e.g. Shaded luxury beachfront cabana with billowing sheer linen drapes looking out at pristine turquoise ocean surf in bright 5500K daylight...",
  beach_sunset_terrace: "e.g. Private teakwood terrace overlooking golden hour ocean sunset, glowing lanterns, and gentle rolling waves...",
  beach_twilight_pergola: "e.g. Open-air beach pergola at deep violet twilight, warm amber lanterns, and soothing ocean tide lullaby...",
  beach_starlit_hammock: "e.g. Starlit beachfront hammock between palms, glowing starlight reflecting on gentle dark turquoise waves...",
  desert_daytime_tent: "e.g. View from inside luxury glamping tent looking out at vast golden dunes in bright 5500K daylight, sheer cream curtains, brass teapot...",
  desert_sunrise_tent: "e.g. Dawn view from luxury desert tent, first morning sun rays cresting dunes, delicate steam from Moroccan mint tea glass...",
  desert_sunset_tent: "e.g. Golden hour sunset over fiery terracotta dunes from inside Bedouin tent, long purple shadows, warm glowing brass lantern...",
  desert_night_tent: "e.g. View looking out from dark cozy tent into deep indigo sky with glittering Milky Way galaxy, soft candle lantern...",
  desert_campfire_hearth: "e.g. Open-air Bedouin desert pavilion on sand dunes at midnight, Persian rugs, glowing brass lanterns, crackling stone hearth campfire...",
  desert_rain_sanctuary: "e.g. Rare desert rain shower, gentle raindrops falling on canvas tent roof, damp ripples in golden sand, cozy warm shelter...",
  mountain_daytime_vista: "e.g. Panoramic high alpine mountain pass in bright 5500K daylight, snow-capped granite spires, emerald valley below...",
  mountain_summit_dawn: "e.g. Alpine mountain peak at sunrise dawn, pastel rose alpenglow lighting glacial crags and sea of morning clouds...",
  mountain_sunset_alpenglow: "e.g. Fiery alpenglow sunset bathing towering jagged granite peaks, deep purple valley shadows, tranquil evening breeze...",
  mountain_starlit_ridge: "e.g. Starlit high alpine ridge under crystal clear night sky and brilliant Milky Way galaxy arching over snowy peaks...",
  valley_wildflower_meadow: "e.g. Lush Swiss alpine valley meadow blooming with purple lupines and yellow buttercups, crystal glacial stream meandering through...",
  valley_morning_mist: "e.g. Pastoral green valley awakening at dawn with soft ribbons of morning mist drifting across emerald hills...",
  valley_glacial_stream: "e.g. Crystal turquoise glacial stream babbling through peaceful valley pasture with snow-capped peaks in distance...",
  valley_sunset_pastoral: "e.g. Golden hour sunset sweeping across pastoral alpine valley, rustic wooden hay barn, long warm shadows...",
  blizzard_cozy_cabin_window: "e.g. Warm interior of timber cabin looking out panoramic window at raging alpine blizzard, frosted glass, steaming cocoa mug...",
  blizzard_frosted_pine_forest: "e.g. Heavy swirling snowstorm sweeping through dense frosted pine forest, thick snowdrifts accumulating...",
  blizzard_alpine_hearth_shelter: "e.g. Glowing stone fireplace hearth inside rustic mountain shelter, blizzard howling outside thick timber walls...",
  blizzard_twilight_snowfall: "e.g. Peaceful heavy snowfall at deep blue twilight settling on alpine cabin roof and evergreen boughs...",
  forest_mossy_canopy_day: "e.g. Ancient temperate rainforest with moss-draped cedar canopy, crystal forest river flowing over smooth stones...",
  forest_babbling_brook: "e.g. Tranquil forest brook cascading over small mossy rock ledges, lush emerald ferns, serene nature ASMR...",
  forest_morning_sunbeams: "e.g. Golden morning sunbeams piercing through misty redwood canopy (komorebi effect), dew glistening on forest floor...",
  forest_twilight_fireflies: "e.g. Enchanted forest glade at twilight, gentle bioluminescent fireflies dancing among ferns and ancient tree trunks...",
  rainy_cabin_bedroom: "e.g. Cozy glass cabin bedroom in a misty pine forest during heavy rainfall, warm bedside lamp (2700K), rain on window...",
  misty_forest_stream: "e.g. Ancient mossy rainforest canopy with gentle stream and floating leaves...",
  alpine_peaks_meadow: "e.g. Towering Swiss Alps snow-capped jagged peaks, lush wildflower meadows, and crystal mountain stream...",
  monumental_plunge: "e.g. Monumental roaring cataract plunging into turquoise pool with heavy rising mist...",
  pebble_beach_shore: "e.g. Gentle rain falling on warm driftwood campfire burning on wet pebble shoreline by ocean surf...",
  glacial_mirror_lake: "e.g. Mirror-still turquoise glacial lake reflecting towering pine-covered granite cliffs...",
  karesansui_temple: "e.g. Peaceful Kyoto dry raked stone garden, bamboo water fountain, and cedar veranda...",
  himalayan_valley: "e.g. Sacred Himalayan valley with singing bowls, crystal dawn sunbeams, and restorative 528Hz serenity..."
};

