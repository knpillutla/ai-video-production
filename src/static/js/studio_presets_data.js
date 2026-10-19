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
    prompt: "Calming Heavy Summer Rain & Distant Thunder - Dramatic torrential rainfall streaming from eaves, visible falling rain sheets, energetic water droplet ripples, cozy atmospheric ASMR soundscape",
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

const WORLD_CONTINENTS_REGIONS_MAP = {
  "Asia": [
    { name: "India", flag: "🇮🇳" },
    { name: "Japan", flag: "🇯🇵" },
    { name: "South Korea", flag: "🇰🇷" },
    { name: "China", flag: "🇨🇳" },
    { name: "Indonesia", flag: "🇮🇩" },
    { name: "Thailand", flag: "🇹🇭" },
    { name: "Vietnam", flag: "🇻🇳" },
    { name: "Philippines", flag: "🇵🇭" },
    { name: "Turkey", flag: "🇹🇷" },
    { name: "Saudi Arabia", flag: "🇸🇦" },
    { name: "United Arab Emirates", flag: "🇦🇪" }
  ],
  "Europe": [
    { name: "France", flag: "🇫🇷" },
    { name: "Spain", flag: "🇪🇸" },
    { name: "Italy", flag: "🇮🇹" },
    { name: "Germany", flag: "🇩🇪" },
    { name: "United Kingdom", flag: "🇬🇧" },
    { name: "Ireland", flag: "🇮🇪" },
    { name: "Greece", flag: "🇬🇷" },
    { name: "Norway", flag: "🇳🇴" },
    { name: "Sweden", flag: "🇸🇪" },
    { name: "Portugal", flag: "🇵🇹" },
    { name: "Poland", flag: "🇵🇱" },
    { name: "Switzerland", flag: "🇨🇭" },
    { name: "Netherlands", flag: "🇳🇱" }
  ],
  "North America": [
    { name: "United States", flag: "🇺🇸" },
    { name: "Canada", flag: "🇨🇦" },
    { name: "Mexico", flag: "🇲🇽" },
    { name: "Jamaica", flag: "🇯🇲" },
    { name: "Cuba", flag: "🇨🇺" },
    { name: "Puerto Rico", flag: "🇵🇷" },
    { name: "Dominican Republic", flag: "🇩🇴" }
  ],
  "South America": [
    { name: "Brazil", flag: "🇧🇷" },
    { name: "Colombia", flag: "🇨🇴" },
    { name: "Argentina", flag: "🇦🇷" },
    { name: "Peru", flag: "🇵🇪" },
    { name: "Chile", flag: "🇨🇱" }
  ],
  "Africa": [
    { name: "Nigeria", flag: "🇳🇬" },
    { name: "Egypt", flag: "🇪🇬" },
    { name: "South Africa", flag: "🇿🇦" },
    { name: "Kenya", flag: "🇰🇪" },
    { name: "Morocco", flag: "🇲🇦" },
    { name: "Ghana", flag: "🇬🇭" },
    { name: "Senegal", flag: "🇸🇳" },
    { name: "Ethiopia", flag: "🇪🇹" }
  ],
  "Oceania": [
    { name: "Australia", flag: "🇦🇺" },
    { name: "New Zealand", flag: "🇳🇿" },
    { name: "Fiji", flag: "🇫🇯" }
  ]
};

const WORLD_COUNTRY_REGIONS_MAP = {
  "India": [
    {
      id: "south_india",
      name: "South India (Tollywood, Kollywood, Sandalwood, Mollywood)",
      culture: "south_indian",
      languages: [
        { code: "te", name: "Telugu (Andhra & Telangana - Tollywood)", script: "Telugu", culture: "south_indian" },
        { code: "ta", name: "Tamil (Tamil Nadu - Kollywood)", script: "Tamil", culture: "south_indian" },
        { code: "kn", name: "Kannada (Karnataka - Sandalwood)", script: "Kannada", culture: "south_indian" },
        { code: "ml", name: "Malayalam (Kerala - Mollywood)", script: "Malayalam", culture: "south_indian" }
      ]
    },
    {
      id: "east_india",
      name: "East India (Bengal, Odisha & Assam)",
      culture: "east_indian",
      languages: [
        { code: "bn", name: "Bengali (West Bengal - Baul & Tollywood)", script: "Bengali", culture: "east_indian" },
        { code: "or", name: "Odia (Odisha - Sambalpuri & Odissi)", script: "Odia", culture: "east_indian" },
        { code: "as", name: "Assamese (Assam - Bihu & Lokageet)", script: "Bengali", culture: "east_indian" }
      ]
    },
    {
      id: "west_india",
      name: "West India (Maharashtra, Gujarat, Goa & Sindh Heritage)",
      culture: "west_indian",
      languages: [
        { code: "mr", name: "Marathi (Maharashtra - Natya Sangeet & Lavani)", script: "Devanagari", culture: "west_indian" },
        { code: "gu", name: "Gujarati (Gujarat - Garba & Sugam Sangeet)", script: "Gujarati", culture: "west_indian" },
        { code: "kok", name: "Konkani (Goa & Konkan - Mandó & Dulpod)", script: "Devanagari", culture: "west_indian" },
        { code: "sd", name: "Sindhi (Sindh Heritage - Sufi Kalaam & Jhulelal)", script: "Devanagari", culture: "west_indian" }
      ]
    },
    {
      id: "north_india",
      name: "North India (Punjab, Kashmir, Hindi Heartland & Urdu)",
      culture: "north_indian",
      languages: [
        { code: "hi", name: "Hindi (Bollywood & Classical Hindustani)", script: "Devanagari", culture: "north_indian" },
        { code: "pa", name: "Punjabi (Punjab - Bhangra & Sufi)", script: "Gurmukhi", culture: "north_indian" },
        { code: "ks", name: "Kashmiri (Kashmir Valley - Rouf & Sufiyana)", script: "Devanagari", culture: "north_indian" },
        { code: "ur", name: "Urdu (Ghazal & Qawwali)", script: "Arabic", culture: "north_indian" }
      ]
    }
  ],
  "Spain": [
    {
      id: "andalusia",
      name: "Andalusia (Flamenco & Cante Jondo)",
      culture: "spanish",
      languages: [
        { code: "es", name: "Spanish (Andalusian Flamenco & Acoustic)", script: "Latin", culture: "spanish" }
      ]
    },
    {
      id: "catalonia",
      name: "Catalonia (Rumba Catalana & Nova Cançó)",
      culture: "spanish",
      languages: [
        { code: "ca", name: "Catalan (Rumba Catalana & Pop)", script: "Latin", culture: "spanish" },
        { code: "es", name: "Spanish (Barcelona Modern Pop)", script: "Latin", culture: "spanish" }
      ]
    },
    {
      id: "galicia",
      name: "Galicia (Celtic Cantigas & Alalá)",
      culture: "spanish",
      languages: [
        { code: "gl", name: "Galician (Celtic Folk & Cantigas)", script: "Latin", culture: "spanish" }
      ]
    }
  ],
  "United States": [
    {
      id: "american_south",
      name: "American South (Country, Blues & Gospel)",
      culture: "western",
      languages: [
        { code: "en", name: "English (Southern Country & Delta Blues)", script: "Latin", culture: "western" }
      ]
    },
    {
      id: "appalachia",
      name: "Appalachia (Bluegrass & Mountain Folk)",
      culture: "western",
      languages: [
        { code: "en", name: "English (Appalachian Bluegrass & Old-Time)", script: "Latin", culture: "western" }
      ]
    },
    {
      id: "southwest",
      name: "Southwest & Border (Tejano, Mariachi & Latin)",
      culture: "spanish",
      languages: [
        { code: "es", name: "Spanish (Tejano & Border Ballad)", script: "Latin", culture: "spanish" },
        { code: "en", name: "English (Desert Acoustic & Folk)", script: "Latin", culture: "western" }
      ]
    }
  ],
  "United Kingdom": [
    {
      id: "scotland",
      name: "Scotland (Highland Celtic & Folk Ballads)",
      culture: "western",
      languages: [
        { code: "gd", name: "Scottish Gaelic (Gàidhlig - Celtic)", script: "Latin", culture: "western" },
        { code: "en", name: "English (Scottish Ballads & Acoustic)", script: "Latin", culture: "western" }
      ]
    },
    {
      id: "wales",
      name: "Wales (Cerdd Dant & Choral Folk)",
      culture: "western",
      languages: [
        { code: "cy", name: "Welsh (Cymraeg - Choral & Folk)", script: "Latin", culture: "western" },
        { code: "en", name: "English (Welsh Acoustic & Hymns)", script: "Latin", culture: "western" }
      ]
    },
    {
      id: "england",
      name: "England (Traditional Folk & Modern Pop)",
      culture: "western",
      languages: [
        { code: "en", name: "English (Traditional Folk & Modern Pop)", script: "Latin", culture: "western" }
      ]
    }
  ],
  "Japan": [
    {
      id: "kanto_tokyo",
      name: "Kanto (Tokyo - Modern J-Pop & City Pop)",
      culture: "japanese",
      languages: [
        { code: "ja", name: "Japanese (Tokyo J-Pop & City Pop)", script: "Japanese", culture: "japanese" }
      ]
    },
    {
      id: "kansai_kyoto",
      name: "Kansai (Kyoto & Osaka - Traditional Gagaku & Folk)",
      culture: "japanese",
      languages: [
        { code: "ja", name: "Japanese (Koto Classical & Min'yo)", script: "Japanese", culture: "japanese" }
      ]
    },
    {
      id: "okinawa",
      name: "Okinawa (Ryukyu - Sanshin Island Folk)",
      culture: "japanese",
      languages: [
        { code: "ja", name: "Japanese / Ryukyu (Sanshin Island Folk)", script: "Japanese", culture: "japanese" }
      ]
    }
  ],
  "France": [
    {
      id: "paris_ile_de_france",
      name: "Île-de-France (Paris - Chanson Française & Pop)",
      culture: "french",
      languages: [
        { code: "fr", name: "French (Chanson Française & Parisian Pop)", script: "Latin", culture: "french" }
      ]
    },
    {
      id: "brittany",
      name: "Brittany (Celtic Fest-Noz & Folk)",
      culture: "french",
      languages: [
        { code: "fr", name: "French / Breton (Celtic Folk Ballad)", script: "Latin", culture: "french" }
      ]
    }
  ],
  "Nigeria": [
    {
      id: "yorubaland",
      name: "South-West (Yorubaland - Fuji, Jùjú & Afrobeats)",
      culture: "african",
      languages: [
        { code: "yo", name: "Yoruba (Fuji, Jùjú & Afrobeats)", script: "Latin", culture: "african" },
        { code: "en", name: "English (Lagos Afrobeats)", script: "Latin", culture: "african" }
      ]
    },
    {
      id: "igboland",
      name: "South-East (Igboland - Ogene & Highlife)",
      culture: "african",
      languages: [
        { code: "ig", name: "Igbo (Ogene & Highlife)", script: "Latin", culture: "african" }
      ]
    },
    {
      id: "northern_nigeria",
      name: "Northern Nigeria (Hausa Folk & Arewa Pop)",
      culture: "african",
      languages: [
        { code: "ha", name: "Hausa (Traditional & Arewa Pop)", script: "Latin", culture: "african" }
      ]
    }
  ]
};

const STUDIO_COUNTRY_LANGUAGE_MAP = {
  "India": [
    { code: "te", name: "Telugu (South India - Tollywood)", script: "Telugu", culture: "south_indian" },
    { code: "hi", name: "Hindi (North India - Bollywood)", script: "Devanagari", culture: "north_indian" },
    { code: "ta", name: "Tamil (South India - Kollywood)", script: "Tamil", culture: "south_indian" },
    { code: "kn", name: "Kannada (South India - Sandalwood)", script: "Kannada", culture: "south_indian" },
    { code: "ml", name: "Malayalam (South India - Mollywood)", script: "Malayalam", culture: "south_indian" },
    { code: "bn", name: "Bengali (East India - Tollywood Bengal / Baul)", script: "Bengali", culture: "east_indian" },
    { code: "mr", name: "Marathi (West India - Natya Sangeet / Bhavgeet / Lavani)", script: "Devanagari", culture: "west_indian" },
    { code: "or", name: "Odia (East India - Sambalpuri / Odissi / Bhakti)", script: "Odia", culture: "east_indian" },
    { code: "gu", name: "Gujarati (West India - Garba / Sugam Sangeet)", script: "Gujarati", culture: "west_indian" },
    { code: "pa", name: "Punjabi (North India - Bhangra / Sufi)", script: "Gurmukhi", culture: "north_indian" },
    { code: "ks", name: "Kashmiri (North India - Sufiyana Kalam / Rouf / Chakri)", script: "Devanagari", culture: "north_indian" },
    { code: "sd", name: "Sindhi (West/North India - Sufi Kalaam / Jhulelal)", script: "Devanagari", culture: "west_indian" },
    { code: "as", name: "Assamese (East India - Bihu / Folk)", script: "Bengali", culture: "east_indian" },
    { code: "ur", name: "Urdu (North India - Ghazal / Qawwali)", script: "Arabic", culture: "north_indian" },
    { code: "kok", name: "Konkani (West India - Goan Mandó / Dulpod)", script: "Devanagari", culture: "west_indian" }
  ],
  "Japan": [
    { code: "ja", name: "Japanese (Nihongo - J-Pop / Enka / Traditional)", script: "Japanese", culture: "japanese" }
  ],
  "France": [
    { code: "fr", name: "French (Chanson / Modern Pop / Acoustic)", script: "Latin", culture: "french" }
  ],
  "Spain": [
    { code: "es", name: "Spanish (Flamenco / Latin Pop / Acoustic)", script: "Latin", culture: "spanish" }
  ],
  "United States": [
    { code: "en", name: "English (Country / Pop / R&B / Acoustic)", script: "Latin", culture: "western" }
  ],
  "South Korea": [
    { code: "ko", name: "Korean (K-Pop / Ballad / Traditional)", script: "Hangul", culture: "korean" }
  ]
};

const ALL_STUDIO_GENRES = {
  "music/static_vocal": "🎤 Static Vocal (Solo Singer & Ambient Particles / VFX)",
  "music/solo_singer": "🎸 Solo Singer & Expressive Performance (4K Cinematic)",
  "music/duet_romance": "💑 Duet Romance & Dual Melodic Performance",
  "music/concert_live": "🎆 Grand Live Stage & Concert Performance",
  "dance/folk": "💃 Dance, Folk & Music Videos (dance/folk)",
  "music/mass_song": "🥁 Mass Song with Mass Beats (High-Energy Dappu & Teenmaar)",
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
  "doc/nations": "🌍 Nations & Civilizations (doc/nations)",
  "travel/scenic": "✈️ Travel & Nature Scenic Wonders (travel/scenic)",
  "relax/scenic": "✈️ Travel & Nature Scenic Wonders (travel/scenic)",
  "relax/art": "🎨 Living Art, Museum Galleries & Ateliers (relax/art)",
  "travel_walking": "🚶 Travel & 4K 60fps Walking Tours (travel_walking)",
  "comedy/satire": "🎭 Telugu Comedy & Satire Shorts (comedy/satire)",
  "science": "🔬 Science, Discovery & Cosmos (science)"
};

const DEFAULT_CHANNEL_GENRES = {
  "nature_rhythms": ["relax/nature", "relax/rain", "relax/forest", "relax/mountain", "relax/valley", "relax/ocean", "relax/beach_lounge", "relax/desert", "relax/blizzard", "relax/healing", "relax/zen", "relax/waterfall", "relax/ambient", "relax/hearth", "relax/cozy", "travel/scenic", "documentary", "doc/nations", "science", "travel_walking"],
  "earth_serenade": ["relax/nature", "relax/rain", "relax/forest", "relax/mountain", "relax/valley", "relax/ocean", "relax/beach_lounge", "relax/desert", "relax/blizzard", "relax/healing", "relax/zen", "relax/waterfall", "relax/ambient", "travel/scenic", "doc/nations", "relax/art", "science"],
  "silent_hearth": ["relax/hearth", "relax/rain", "relax/cozy", "relax/blizzard"],
  "skylinediariesindia4k": ["travel/scenic"],
  "euro_discovery": ["doc/nations", "documentary", "travel/scenic", "travel_walking"],
  "telugu_rhythms": ["music/static_vocal", "music/solo_singer", "music/duet_romance", "music/concert_live", "dance/folk", "music/mass_song"]
};

const STUDIO_SUBOPTIONS_MAP = {
  "doc/nations": [
    { val: "europe_nations", label: "🇪🇺 Nations of Europe" },
    { val: "asia_nations", label: "🌏 Nations of Asia" },
    { val: "africa_nations", label: "🌍 Nations of Africa" },
    { val: "americas_nations", label: "🌎 Nations of the Americas" },
    { val: "oceania_nations", label: "🏝️ Nations of Oceania & the Pacific" },
    { val: "nordic_polar_nations", label: "❄️ Nordic & Polar Realms" }
  ],
  "relax/art": [{ val: "living_impressionism", label: "🎨 Living Impressionist Canvas (Monet/Van Gogh)" }, { val: "grand_gallery", label: "🏛️ Louvre & Uffizi Grand Gallery Walk" }, { val: "artist_atelier", label: "🖌️ Sunlit Parisian Artist Atelier & Loft" }, { val: "sumie_ukiyoe", label: "🪷 Japanese Ukiyo-e Woodblock & Sumi-e" }, { val: "stained_glass", label: "✨ Cathedral Rose Stained Glass & Light" }, { val: "klimt_gold_leaf", label: "🪙 Art Nouveau Gold Leaf & Fluid Marble" }, { val: "surrealist_dream", label: "🌌 Surrealist Dreamscape & Floating Gardens" }],
  "travel/scenic": [{ val: "cities", label: "🏙️ Metropolises & City Skylines" }, { val: "nature", label: "🌲 Wilderness & Nature Escapes" }, { val: "remote_places", label: "🧭 Remote Places & Untouched Frontiers" }, { val: "tourist_places", label: "🏖️ Tourist Havens & Vibrant Promenades" }, { val: "spiritual_places", label: "🪔 Spiritual Places, Shrines & Ghats" }, { val: "iconic_places", label: "🏛️ Iconic World Heritage & Historic Forts" }, { val: "natural_wonders", label: "🌋 Natural Wonders, Canyons & Cataracts" }],
  "relax/scenic": [{ val: "cities", label: "🏙️ Metropolises & City Skylines" }, { val: "nature", label: "🌲 Wilderness & Nature Escapes" }, { val: "remote_places", label: "🧭 Remote Places & Untouched Frontiers" }, { val: "tourist_places", label: "🏖️ Tourist Havens & Vibrant Promenades" }, { val: "spiritual_places", label: "🪔 Spiritual Places, Shrines & Ghats" }, { val: "iconic_places", label: "🏛️ Iconic World Heritage & Historic Forts" }, { val: "natural_wonders", label: "🌋 Natural Wonders, Canyons & Cataracts" }],
  "relax/ocean": [{ val: "ocean_daytime_shore", label: "☀️ Overwater Villa & Daytime Lagoon" }, { val: "ocean_sunrise_coast", label: "🌅 Coastal Veranda & Pastel Dawn" }, { val: "ocean_sunset_horizon", label: "🌇 Cliffside Sanctuary & Golden Hour Sunset" }, { val: "ocean_night_bioluminescent", label: "🌌 Starlit Beach Pavilion & Bioluminescent Waves" }, { val: "ocean_campfire_hearth", label: "🔥 Open-Air Beach Campfire & Surf" }, { val: "ocean_tropical_rain", label: "🌧️ Sheltered Balcony & Tropical Ocean Rain" }],
  "relax/beach_lounge": [
    { val: "pool_terrace", label: "🏊 Luxury Villa Infinity Pool Terrace (Overlooking Ocean)" },
    { val: "beach_cabana", label: "🏖️ Luxury Beach Cabana & Seaside Daybed" },
    { val: "beach_luxury_cabana_day", label: "☀️ Luxury Beach Cabana & Daytime Turquoise Surf" },
    { val: "beach_sunset_terrace", label: "🌇 Sunset Beach Terrace & Golden Hour Horizon" },
    { val: "beach_twilight_pergola", label: "🌆 Twilight Beach Pergola & Gentle Waves" },
    { val: "beach_starlit_hammock", label: "🌌 Starlit Beachfront Hammock & Night Surf" }
  ],
  "relax/desert": [{ val: "desert_daytime_tent", label: "☀️ Luxury Desert Tent & Daytime Dunes" }, { val: "desert_sunrise_tent", label: "🌅 Luxury Desert Tent & Sunrise Dawn" }, { val: "desert_sunset_tent", label: "🌇 Luxury Desert Tent & Golden Sunset" }, { val: "desert_night_tent", label: "🌌 Luxury Desert Tent & Starlit Milky Way" }, { val: "desert_campfire_hearth", label: "🔥 Desert Campfire & Bedouin Hearth" }, { val: "desert_rain_sanctuary", label: "🌧️ Luxury Desert Tent & Rain ASMR" }],
  "relax/mountain": [{ val: "mountain_daytime_vista", label: "☀️ Panoramic High Alpine Vista" }, { val: "mountain_summit_dawn", label: "🌅 Alpine Summit Sunrise Dawn" }, { val: "mountain_sunset_alpenglow", label: "🌇 Alpenglow Sunset & Granite Peaks" }, { val: "mountain_starlit_ridge", label: "🌌 Starlit Mountain Ridge & Milky Way" }],
  "relax/valley": [{ val: "valley_wildflower_meadow", label: "🌸 Wildflower Meadow & Alpine Stream" }, { val: "valley_morning_mist", label: "🌅 Misty Pastoral Valley Sunrise" }, { val: "valley_glacial_stream", label: "💧 Crystal Glacial Valley Stream" }, { val: "valley_sunset_pastoral", label: "🌇 Pastoral Valley Golden Sunset" }],
  "relax/blizzard": [{ val: "blizzard_cozy_cabin_window", label: "🪟 Cozy Timber Cabin Window & Blizzard Winds" }, { val: "blizzard_frosted_pine_forest", label: "🌲 Frosted Pine Forest & Heavy Snowdrift" }, { val: "blizzard_alpine_hearth_shelter", label: "🔥 Alpine Stone Shelter & Glowing Hearth Fire" }, { val: "blizzard_twilight_snowfall", label: "❄️ Twilight Alpine Cabin & Heavy Snowfall" }],
  "relax/forest": [{ val: "forest_mossy_canopy_day", label: "🌲 Emerald Mossy Canopy & Crystalline Stream" }, { val: "forest_babbling_brook", label: "💧 Babbling Forest Brook & Fern Glade" }, { val: "forest_morning_sunbeams", label: "✨ Morning Komorebi Sunbeams & Ancient Pines" }, { val: "forest_twilight_fireflies", label: "🌌 Twilight Enchanted Forest & Gentle Mist" }],
  "relax/nature": [{ val: "alpine_nature", label: "🏔️ Alpine Nature & Mountain Sanctuaries (Swiss Alps)" }, { val: "glacial_fjord_lake", label: "🛶 Glacial Mirror Lakes & Fjords" }, { val: "temperate_forest", label: "🌲 Temperate Mossy Rainforest & Streams" }],
  "relax/rain": [
    { val: "heavy_rain_swiss_alps", label: "⛈️ Swiss Alps Heavy Rain & Chalet Torrent (Storm Clouds & River Rapids)" },
    { val: "gentle_rain_swiss_alps", label: "🌧️ Swiss Alps Gentle Rain & Meadow Mist (Soft Overcast & Glistening Veranda)" },
    { val: "heavy_rain_tropical_village", label: "🛖 Tropical Village Torrential Rain (Cascading Thatched Eaves)" },
    { val: "gentle_rain_forest_river", label: "🌲 Forest River Gentle Rain (Delicate Droplets & Concentric Ripples)" },
    { val: "gentle_rain_bedroom", label: "🛏️ Cozy Glass Bedroom Gentle Rain (Sleep ASMR & Windowpane Trickle)" },
    { val: "heavy_rain_glass_cabin", label: "⛈️ Forest Glass Cabin Torrential Downpour (Glass Roof Deluge & Thunder)" },
    { val: "droplet_ripples", label: "💧 Water Droplet Ripples & Lake Reflections" }
  ],
  "relax/waterfall": [{ val: "waterfall_gorge", label: "🌊 Monumental Plunge Cataracts (Niagara / Iguazu)" }, { val: "tiered_cascade", label: "🏞️ Multi-Tiered Glacial Cascades (Plitvice)" }],
  "relax/hearth": [{ val: "cozy_hearth", label: "🔥 Open-Air Beach Campfire & Shoreline Hearth" }, { val: "stone_hearth", label: "🪵 Rustic Cabin Stone Fireplace" }, { val: "rainy_hearth_bedroom", label: "🛏️ Rainy Cabin Bedroom with Hearth Fireplace" }],
  "relax/cozy": [{ val: "cabin_bedroom", label: "🛏️ Cozy Glass Cabin Bedroom & Rain on Window" }, { val: "biophilic_living", label: "🪵 Biophilic Living Space & Terraces" }, { val: "rainy_patio", label: "☕ Rainy Garden Patio & Warm Hearth" }],
  "relax/healing": [{ val: "global_healing", label: "✨ Global Sacred Sanctuaries & 528Hz Solfeggio" }, { val: "himalayan_valley", label: "🏔️ Himalayan Singing Bowl Valley & Mist" }, { val: "geothermal_springs", label: "♨️ Geothermal Hot Springs & Travertine Pools" }, { val: "redwood_cathedral", label: "🌲 Ancient Redwood Grove Sanctuary" }],
  "relax/zen": [{ val: "zen_garden", label: "🪷 Kyoto Zen Temple & Raked Rock Garden" }, { val: "bamboo_grove", label: "🎋 Sagano Bamboo Grove & Tsukubai Basin" }, { val: "lotus_pond", label: "🪷 Sacred Lotus Pond & Water Basin Flow" }],
  "documentary": [
    { val: "blue_chip_doc", label: "🎥 Blue-Chip Documentary (Open / Any Topic • Pure Narrative Storytelling)" },
    { val: "doc_architecture", label: "🏛️ Ancient Civilizations, History & Lost Empires" },
    { val: "doc_nature", label: "🌲 Earth, Wilderness & Living Biospheres" },
    { val: "doc_mountains", label: "🏔️ Mountains, Glaciers & Extreme Frontiers" },
    { val: "doc_ocean", label: "🌊 Oceans, Coral Reefs & Deep Abyssal Life" },
    { val: "doc_wildlife", label: "🦁 Wildlife, Predators & Animal Migrations" },
    { val: "doc_desert", label: "🏜️ Deserts, Canyons & Arid Dunes" },
    { val: "travel_itinerary_tour", label: "🗺️ Travel Itinerary Tour (Ordered Route, Day Plan & Connecting Map)" }
  ],
  "travel_walking": [{ val: "alpine_village_walk", label: "🏡 Swiss Alpine Countryside Walk (1.5 km/h)" }, { val: "rain_walking_tour", label: "🌧️ 4K Rain Walking Tour (Puddles & Wet Street Reflections)" }, { val: "city_walk_pov", label: "🏙️ 4K 60fps Historic City & Night Walk" }, { val: "coastal_promenade", label: "🏖️ Secluded Ocean Bluff Walk" }],
  "music/static_vocal": [
    { val: "romantic_melody", label: "💖 Romantic & Melodic Ballad" },
    { val: "soulful_melody", label: "✨ Soulful Melody & Acoustic Longing" },
    { val: "kids_rhyme_song", label: "🧸 Kids Song & Nursery Rhyme (3D Animation)" },
    { val: "soulful_spiritual", label: "🪔 Soulful, Devotional & Spiritual" },
    { val: "happy_uplifting", label: "☀️ Happy, Cheerful & Uplifting" },
    { val: "melancholic_emotional", label: "🌧️ Melancholic & Emotional Ballad" },
    { val: "acoustic_unplugged", label: "🎸 Acoustic Unplugged & Coffeehouse" }
  ],
  "music/solo_singer": [
    { val: "romantic_melody", label: "💖 Romantic & Melodic Solo" },
    { val: "soulful_melody", label: "✨ Soulful Melody & Acoustic Longing" },
    { val: "kids_rhyme_song", label: "🧸 Kids Song & Nursery Rhyme (3D Animation)" },
    { val: "energetic_party", label: "🎉 Energetic Party & Upbeat Club" },
    { val: "happy_uplifting", label: "☀️ Happy & Uplifting Performance" },
    { val: "festive_celebration", label: "🎆 Festive Celebration & Jathara" },
    { val: "soulful_spiritual", label: "🪔 Soulful & Devotional Strains" }
  ],
  "music/duet_romance": [
    { val: "romantic_melody", label: "💖 Romantic & Melodic Love Duet" },
    { val: "soulful_melody", label: "✨ Soulful Melody & Acoustic Longing" },
    { val: "kids_rhyme_song", label: "🧸 Kids Song & Nursery Rhyme (3D Animation)" },
    { val: "playful_banter", label: "😉 Playful Teasing & Flirty Banter" },
    { val: "rain_romance", label: "🌧️ Monsoon & Rain Romance" },
    { val: "festive_duet", label: "🎆 Festive Couple Dance & Celebration" }
  ],
  "music/concert_live": [
    { val: "energetic_party", label: "🎉 High-Voltage Stadium Anthem" },
    { val: "festival_headliner", label: "🎆 World Music Festival Headliner" },
    { val: "unplugged_arena", label: "🕯️ Intimate Arena Acoustic Set" }
  ],
  "dance/folk": [
    { val: "mass_folk_dance", label: "💃 High-Energy Mass Folk Dance (30fps)" },
    { val: "classical_dance", label: "🪘 Cultural Classical Choreography" },
    { val: "festive_celebration", label: "🎆 Festive Jathara & Village Fair" }
  ],
  "music/mass_song": [
    { val: "mass_beats", label: "🥁 High-Energy Mass Beats (Thumping Dappu & Teenmaar)" },
    { val: "commercial_hook_step", label: "🔥 Commercial Mass Hero Hook Step" },
    { val: "jathara_mass_festival", label: "🎆 Jathara Festive Mass Celebration" },
    { val: "fast_brass_whistle", label: "🎺 Fast Brass, Trumpets & Whistle Drops" }
  ],
  "comedy/satire": [{ val: "satirical_short", label: "🎭 Modern Satire & Relatable Comedy Short" }],
  "science": [
    { val: "science_space", label: "🪐 Space, Astronomy & Astrophysics" },
    { val: "science_earth", label: "🌍 Earth & Planetary Sciences" },
    { val: "human_evolution", label: "🦴 Human Evolution & Deep Ancestry" },
    { val: "science_medicine", label: "🧬 Medicine, Biology & Genetics" },
    { val: "science_physics", label: "⚛️ Physics, Quantum & Microcosm" },
    { val: "science_tech", label: "⚡ Extreme Engineering, Fusion & Tech" }
  ]
};

const STUDIO_SUBGENRE_PLACEHOLDERS = {
  living_impressionism: "e.g. Masterpiece living oil painting with visible textured brushstrokes, gently rippling water lilies, and Claude Debussy piano...",
  grand_gallery: "e.g. Elegant high-ceilinged Louvre salon at twilight, warm gallery spotlights illuminating gilded oil canvases, peaceful reverb...",
  artist_atelier: "e.g. Sunbeams cutting through a Paris rooftop artist loft, wooden easels, paint palettes, resting oil canvases, warm dust motes...",
  sumie_ukiyoe: "e.g. Living Japanese woodblock print with gentle rolling Great Wave swells, falling cherry blossom petals, koto and shakuhachi...",
  stained_glass: "e.g. Monumental Gothic cathedral rose stained glass casting kaleidoscopic jewel-toned sunlight across stone floors...",
  klimt_gold_leaf: "e.g. Gustav Klimt inspired gold leaf textures with flowing marble fluid dynamics, undulating metallic pigments, velvet pads...",
  surrealist_dream: "e.g. Salvador Dali inspired ethereal floating architectural archways, celestial moons, and dream gardens in starry night...",
  cities: "e.g. 4K cinematic drone flight over illuminated Hyderabad skyline, Charminar, Hussain Sagar, and HITEC City...",
  remote_places: "e.g. Majestic aerial drone glide over remote windswept peaks of Patagonia and solitary glacial outposts...",
  tourist_places: "e.g. Sun-drenched drone vista soaring along Amalfi Coast colorful cliffside villas and azure waters...",
  spiritual_places: "e.g. Sacred sunrise aerial glide over Varanasi Ganga Ghats with glowing brass lamps and morning mist...",
  iconic_places: "e.g. Majestic 4K drone orbit around ancient Golconda Fort granite ramparts and royal bastions at sunset...",
  pool_terrace: "e.g. Elevated luxury villa terrace with infinity swimming pool overlooking the panoramic ocean at twilight, low designer loungers, recessed warm floor lights...",
  beach_cabana: "e.g. Shaded teak daybed on pristine white sand beach with billowing sheer linen drapes, gentle turquoise surf, ocean breeze...",
  natural_wonders: "e.g. Monumental drone flight revealing colossal crimson depths of Grand Canyon in golden hour light...",
  alpine_nature: "e.g. Majestic Swiss Alps panoramic peaks, wildflower valley, and crystal glacial stream...",
  glacial_fjord_lake: "e.g. Glassy mirror-still turquoise glacial lake reflecting towering forested cliffs...",
  temperate_forest: "e.g. Ancient mossy rainforest and gentle babbling river over rounded stones...",
  rainy_bedroom: "e.g. Cozy glass cabin bedroom in a misty pine forest during heavy rainfall, warm bedside lamp (2700K), rain on window...",
  tropical_village_rain: "e.g. Sheltered rustic bamboo pavilion in a peaceful tropical village during heavy torrential rainfall, thatched roof eaves with water cascading in continuous glassy sheets, warm glowing amber lantern (2700K), cozy outdoor bed...",
  cabin_bedroom: "e.g. Warm biophilic timber glass cabin bedroom overlooking rainy forest, plush duvet, and steaming tea mug...",
  rainy_hearth_bedroom: "e.g. Intimate timber bedroom with glowing stone hearth fireplace, soft bed, and steady rain on windowpanes...",
  heavy_rain_swiss_alps: "e.g. Sheltered wooden chalet veranda overlooking emerald green Swiss alpine village during heavy torrential summer rainstorm, dark storm clouds, cascading eaves, roaring turquoise glacial river...",
  gentle_rain_swiss_alps: "e.g. Swiss alpine chalet balcony during gentle steady rain, soft cool overcast daylight, glistening red geraniums, misty emerald valley...",
  heavy_rain_tropical_village: "e.g. Sheltered rustic bamboo pavilion in tropical village during heavy torrential rainfall, cascading thatched eaves, warm amber lantern...",
  gentle_rain_forest_river: "e.g. Temperate rainforest stream during gentle continuous rain, delicate droplets on mossy stones, expanding concentric ripples...",
  gentle_rain_bedroom: "e.g. Cozy glass cabin bedroom in misty pine forest during gentle rain, warm 2700K bedside lamp, rain streaming on windowpane...",
  heavy_rain_glass_cabin: "e.g. Forest glass cabin during torrential downpour, dramatic rain sheets pounding on glass ceiling, distant rolling thunder...",
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
  blue_chip_doc: "e.g. Enter any documentary topic: Indus Valley Civilization, The Roman Empire, Apollo 11 Lunar Missions, Deep Sea Trenches...",
  travel_itinerary_tour: "e.g. London Tour, 3 Days (or Oslo Highlights, 2 Days) - Gemini curates top attractions, transit & day itinerary...",
  doc_places: "e.g. Oslo Tour, 2 Days (or London Tour, 3 Days - Gemini autonomously curates top attractions & route)...",
  doc_beaches: "e.g. Whitehaven Beach, Whitsunday Islands: 98% pure silica sands, shifting turquoise tides, and pristine barrier reefs...",
  doc_mountains: "e.g. Matterhorn & Zermatt, Swiss Alps: Titanic granite pyramid, glacial seracs, and high alpine weather frontiers...",
  doc_nature: "e.g. Ancient Olympic Temperate Rainforest: 300ft Sitka spruce canopies, velvet moss cathedrals, and glacial river ecology...",
  doc_ocean: "e.g. Great Barrier Reef & Coral Sea: Vast coral atolls, humpback whale nursing grounds, and caustic sunbeams dancing on reef shelves...",
  doc_desert: "e.g. Grand Erg Oriental, Sahara: Monumental 500ft star dunes, wind-carved ripples, and extreme nocturnal desert survival...",
  doc_wildlife: "e.g. Serengeti Great Migration: Golden savannah predators, cheetah hunting kinematics, and wildebeest river crossings...",
  doc_architecture: "e.g. Giza Necropolis: The Great Pyramid & Sphinx, astronomical cardinal alignments, and megalithic quarrying secrets...",
  cinematic_doc: "e.g. BBC-style 24fps cinematic wildlife documentary across rugged alpine peaks...",
  volcano_arctic: "e.g. Dramatic volcanic black sand coast meets glacial blue ice caves...",
  ocean_depths: "e.g. Deep marine coral reefs with schools of luminous fish in crystal blue waters...",
  alpine_village_walk: "e.g. Ultra-slow 1.5 km/h human walking tour through Swiss alpine village and meadow path...",
  city_walk_pov: "e.g. 4K 60fps tranquil historic European cobblestone street walk at twilight...",
  mass_folk_dance: "e.g. High-energy festive village celebration with dynamic troupe choreography...",
  satirical_short: "e.g. Relatable everyday comedy satire with sharp comedic timing and witty dialogue...",
  science_space: "e.g. James Webb infrared deep field galaxies, supermassive black hole accretion disk, Europa subsurface ocean...",
  science_earth: "e.g. Mariana Trench hydrothermal vents, Hadal zone bioluminescence, mantle plumes, supervolcano calderas...",
  human_evolution: "e.g. East African Rift Valley hominin origins, Neanderthal ice age survival, Lascaux cave art...",
  science_medicine: "e.g. Synaptic connectome of the human brain, CRISPR Cas9 editing molecular DNA strands, cellular mitosis...",
  science_physics: "e.g. Quantum superposition & entanglement, CERN Large Hadron Collider proton collisions, atomic lattice microscopy...",
  science_tech: "e.g. Tokamak nuclear fusion reactor magnetic confinement, superconducting quantum computing cryostats, ion drives...",
  europe_nations: "e.g. Leave empty for autonomous European country & topic rotation via TopicMemory, or specify (e.g. Poland, Austria, Greece)...",
  asia_nations: "e.g. Leave empty for autonomous Asian country & topic rotation via TopicMemory, or specify (e.g. Japan, India, Vietnam)...",
  africa_nations: "e.g. Leave empty for autonomous African country & topic rotation via TopicMemory, or specify (e.g. Egypt, Morocco, Kenya)...",
  americas_nations: "e.g. Leave empty for autonomous Americas country & topic rotation via TopicMemory, or specify (e.g. Peru, Canada, Mexico)...",
  oceania_nations: "e.g. Leave empty for autonomous Pacific nation & topic rotation via TopicMemory, or specify (e.g. New Zealand, Australia)...",
  nordic_polar_nations: "e.g. Leave empty for autonomous Nordic realm & topic rotation via TopicMemory, or specify (e.g. Iceland, Norway, Svalbard)..."
};

const MUSIC_VIDEO_BACKGROUND_ARCHETYPES = [
  // 1. 🏛️ Royal Palaces, Temples & Historical Architecture
  { val: "palace_courtyard", label: "🏛️ Royal Palace Courtyard & Veranda (Heritage Carved Pillars)" },
  { val: "palace_darbar_hall", label: "👑 Royal Darbar & Mirrored Hall (Ornate Marble & Chandeliers)" },
  { val: "temple_mandapam_lotus", label: "🪷 Sacred Temple Mandapam & Lotus Pond (Ancient Carved Stone)" },
  { val: "historic_fort_ramparts", label: "🏰 Historic Fort Ramparts & Stone Arches (Scenic Valley Vista)" },

  // 2. 🎭 Live Concert Stages & Performance Recitals
  { val: "classical_sabha_concert", label: "🪕 Classical Sabha Concert (Seated Dais, Accompanists & Audience)" },
  { val: "live_vocal_arena_concert", label: "🎤 Live Singing Arena Concert (Illuminated Stage, Spotlights & Cheering Crowd)" },
  { val: "dance_recital_theatre", label: "💃 Classical Dance Recital Stage (Proscenium Arch, Footwork Floor & Audience)" },
  { val: "contemporary_dance_concert", label: "🕺 Grand Contemporary Dance Stage (Backup Troupe, Stage Smoke & LED Walls)" },
  { val: "open_air_amphitheatre", label: "🏛️ Open-Air Stone Amphitheatre (Starlit Sky, Lanterns & Tiered Audience)" },
  { val: "concert_hall_stage", label: "🎭 Grand Symphony Concert Hall & Stage (Mahogany Acoustics & Spotlights)" },

  // 3. 🏡 Indoor, Acoustic & Intimate (Classical / Jugalbandi / Baithak)
  { val: "traditional_heritage_home", label: "🏡 Traditional Heritage Home Living Room & Veranda (Warm Wood & Lamps)" },
  { val: "royal_baithak_chamber", label: "🪕 Royal Baithak / Acoustic Chamber (Silk Bolsters & Persian Carpets)" },
  { val: "glass_penthouse_lounge", label: "🏙️ Modern Luxury Glass Penthouse (Skyline Panoramic Backdrop)" },

  // 3. 🏔️ Majestic Nature & Grand Landscapes
  { val: "swiss_alps_meadow", label: "🏔️ Swiss Alps & Wildflower Meadows (Lauterbrunnen Valley)" },
  { val: "norwegian_fjords_waters", label: "🌊 Norwegian Fjords & Glacial Waters (Granite Cliffs & Waterfalls)" },
  { val: "misty_pine_forest_stream", label: "🌲 Misty Ancient Pine Forest & Glacial Stream (Komorebi Beams)" },
  { val: "pastoral_wildflower_valley", label: "🌸 Pastoral Wildflower Valley & Rolling Foothills (Sunset Golden Hour)" },

  // 4. 🗼 World Iconic Cities & European Romance
  { val: "paris_seine_eiffel", label: "🗼 Paris Romantic Seine Riverbank & Eiffel Twilight" },
  { val: "london_thames_westminster", label: "🇬🇧 London Thames Riverbank & Historic Westminster (Misty Romance)" },
  { val: "venice_grand_canal", label: "🛶 Venice Grand Canal & Historic Palazzos (Gondola Twilight)" },
  { val: "tokyo_shinjuku_rooftop", label: "🌆 Tokyo Shinjuku Twilight Rooftop (Glass Balustrade & Neon Glow)" },

  // 5. 🌊 Coastal, Maritime & Nautical
  { val: "tropical_white_beach", label: "🏖️ Tropical White Sand Beach & Sunset Surf (Golden Tide Wash)" },
  { val: "luxury_cruise_deck", label: "🚢 Luxury Yacht / Cruise Ship Observation Deck (Infinite Ocean Horizon)" },
  { val: "cliffside_ocean_terrace", label: "🌊 Cliffside Mediterranean Stone Terrace & Azure Sea" },

  // 6. ✈️ Luxury Travel & Exotic Frontiers
  { val: "private_jet_cabin", label: "✈️ In-Flight Luxury Private Jet VIP Cabin (Clouds Outside Oval Windows)" },
  { val: "desert_dunes_oasis", label: "🏜️ Arabian Desert Sand Dunes & Sunset Oasis Camp (Silk Pavilions)" },
  { val: "royal_heritage_train", label: "🚂 Luxury Royal Heritage Train Salon (Countryside Gliding Past Windows)" },

  // 7. 🌌 Fantasy & Celestial Dreamscapes
  { val: "celestial_fantasy_garden", label: "🌌 Celestial Ethereal Fantasy Garden (Luminescent Blossoms & Mist)" },
  { val: "starlit_sacred_lotus", label: "✨ Starlit Sacred Lotus Sanctuary (Milky Way & Floating Lanterns)" },

  // 8. 🎪 Traditional Folk & Mass Grounds
  { val: "village_jathara_square", label: "🎪 Village Fairground Stage & Jathara Grounds (Festive Banners)" },
  { val: "lush_paddy_fields", label: "🌾 Verdant Rural Paddy Fields & Palm Groves" }
];

const COUNTRY_MUSIC_BACKGROUND_DEFAULTS = {
  "Switzerland": "swiss_alps_meadow",
  "Norway": "norwegian_fjords_waters",
  "France": "paris_seine_eiffel",
  "United Kingdom": "london_thames_westminster",
  "Italy": "venice_grand_canal",
  "Japan": "tokyo_shinjuku_rooftop",
  "United States": "glass_penthouse_lounge",
  "India": "palace_courtyard",
  "United Arab Emirates": "desert_dunes_oasis",
  "Saudi Arabia": "desert_dunes_oasis",
  "Egypt": "historic_fort_ramparts",
  "Greece": "cliffside_ocean_terrace",
  "Spain": "cliffside_ocean_terrace",
  "Maldives": "tropical_white_beach",
  "Indonesia": "tropical_white_beach",
  "Thailand": "tropical_white_beach",
  "Germany": "concert_hall_stage",
  "Austria": "concert_hall_stage"
};

const STUDIO_ARCHETYPES_MAP = {
  "music_video": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/static_vocal": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/solo_singer": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/duet_romance": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/concert_live": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/mass_song": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/carnatic_fusion": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/golden_retro": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/jugalbandi": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/instrumental_solo": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "music/instrumental_jugalbandi": MUSIC_VIDEO_BACKGROUND_ARCHETYPES,
  "relax/art": [{ val: "living_impressionism", label: "🎨 Living Impressionism" }, { val: "grand_gallery", label: "🏛️ Grand Nocturne Gallery" }, { val: "artist_atelier", label: "🖌️ Sunlit Artist Atelier" }, { val: "sumie_ukiyoe", label: "🪷 Ukiyo-e Woodblock" }, { val: "stained_glass", label: "✨ Cathedral Stained Glass" }, { val: "klimt_gold_leaf", label: "🪙 Gold Leaf & Marble" }, { val: "surrealist_dream", label: "🌌 Surrealist Dreamscape" }],
  "travel/scenic": [{ val: "cities", label: "🏙️ Metropolises & Skylines" }, { val: "nature", label: "🌲 Wilderness & Nature" }, { val: "remote_places", label: "🧭 Remote Frontiers" }, { val: "tourist_places", label: "🏖️ Tourist Havens" }, { val: "spiritual_places", label: "🪔 Spiritual & Sacred" }, { val: "iconic_places", label: "🏛️ Iconic Heritage Forts" }, { val: "natural_wonders", label: "🌋 Natural Wonders" }],
  "relax/ocean": [{ val: "ocean_daytime_shore", label: "☀️ Overwater Villa (Lagoon)" }, { val: "ocean_sunrise_coast", label: "🌅 Coastal Veranda (Dawn)" }, { val: "ocean_sunset_horizon", label: "🌇 Cliffside Sanctuary (Sunset)" }, { val: "ocean_night_bioluminescent", label: "🌌 Beach Pavilion (Bioluminescent)" }, { val: "ocean_campfire_hearth", label: "🔥 Beach Campfire & Surf" }, { val: "ocean_tropical_rain", label: "🌧️ Sheltered Balcony (Rain ASMR)" }],
  "relax/beach_lounge:pool_terrace": [
    { val: "pool_terrace_twilight", label: "🌆 Twilight Infinity Pool & Ocean Horizon" },
    { val: "pool_terrace_sunset", label: "🌇 Sunset Infinity Pool Terrace & Molten Gold" },
    { val: "pool_terrace_daylight", label: "☀️ Daytime Infinity Pool & Turquoise Sea" },
    { val: "pool_terrace_starlit", label: "🌌 Starlit Midnight Pool & Ambient Glow" }
  ],
  "relax/beach_lounge:beach_cabana": [
    { val: "beach_luxury_cabana_day", label: "☀️ Luxury Beach Cabana & Daybed" },
    { val: "beach_sunset_terrace", label: "🌇 Sunset Beach Cabana & Horizon" },
    { val: "beach_twilight_pergola", label: "🌆 Twilight Beach Pergola" },
    { val: "beach_starlit_hammock", label: "🌌 Starlit Beachfront Hammock" }
  ],
  "relax/beach_lounge": [
    { val: "pool_terrace_twilight", label: "🌆 Twilight Infinity Pool & Ocean Horizon" },
    { val: "pool_terrace_sunset", label: "🌇 Sunset Infinity Pool Terrace & Molten Gold" },
    { val: "pool_terrace_daylight", label: "☀️ Daytime Infinity Pool & Turquoise Sea" },
    { val: "pool_terrace_starlit", label: "🌌 Starlit Midnight Pool & Ambient Glow" },
    { val: "beach_luxury_cabana_day", label: "☀️ Luxury Beach Cabana" },
    { val: "beach_sunset_terrace", label: "🌇 Sunset Beach Terrace" },
    { val: "beach_twilight_pergola", label: "🌆 Twilight Beach Pergola" },
    { val: "beach_starlit_hammock", label: "🌌 Starlit Beachfront Hammock" }
  ],
  "relax/desert": [{ val: "desert_daytime_tent", label: "☀️ Luxury Desert Tent (Dunes)" }, { val: "desert_sunrise_tent", label: "🌅 Luxury Desert Tent (Sunrise)" }, { val: "desert_sunset_tent", label: "🌇 Luxury Desert Tent (Sunset)" }, { val: "desert_night_tent", label: "🌌 Luxury Desert Tent (Milky Way)" }, { val: "desert_campfire_hearth", label: "🔥 Desert Campfire & Hearth" }, { val: "desert_rain_sanctuary", label: "🌧️ Desert Rain Sanctuary ASMR" }],
  "relax/mountain": [{ val: "mountain_daytime_vista", label: "☀️ High Alpine Vista" }, { val: "mountain_summit_dawn", label: "🌅 Summit Sunrise Dawn" }, { val: "mountain_sunset_alpenglow", label: "🌇 Alpenglow Sunset" }, { val: "mountain_starlit_ridge", label: "🌌 Starlit Mountain Ridge" }],
  "relax/valley": [{ val: "valley_wildflower_meadow", label: "🌸 Wildflower Meadow" }, { val: "valley_morning_mist", label: "🌅 Misty Valley Sunrise" }, { val: "valley_glacial_stream", label: "💧 Glacial Valley Stream" }, { val: "valley_sunset_pastoral", label: "🌇 Pastoral Sunset" }],
  "relax/blizzard": [{ val: "blizzard_cozy_cabin_window", label: "🪟 Cozy Cabin Window" }, { val: "blizzard_frosted_pine_forest", label: "🌲 Frosted Pine Forest" }, { val: "blizzard_alpine_hearth_shelter", label: "🔥 Alpine Hearth Shelter" }, { val: "blizzard_twilight_snowfall", label: "❄️ Twilight Snowfall" }],
  "relax/forest": [{ val: "forest_mossy_canopy_day", label: "🌲 Emerald Mossy Canopy" }, { val: "forest_babbling_brook", label: "💧 Babbling Forest Brook" }, { val: "forest_morning_sunbeams", label: "✨ Morning Sunbeams" }, { val: "forest_twilight_fireflies", label: "🌌 Twilight Fireflies" }],
  "relax/nature": [{ val: "alpine_peaks_meadow", label: "🏔️ Swiss Alps Peaks & Meadow" }, { val: "glacial_mirror_lake", label: "🛶 Glacial Mirror Lake" }, { val: "temperate_mossy_forest", label: "🌲 Mossy Rainforest & Stream" }, { val: "dolomites_panoramic", label: "⛰️ Dolomite Granite Spires" }],
  "relax/rain": [{ val: "swiss_chalet_balcony", label: "🏡 Swiss Chalet Balcony & Village Rain" }, { val: "biophilic_veranda", label: "🏡 Biophilic Covered Veranda" }, { val: "misty_forest_stream", label: "🌲 Rainforest Glacial Stream" }, { val: "peaceful_village_sleep", label: "🛌 Open-Air Veranda Bed & Heavy Village Rain" }, { val: "bamboo_hut_veranda", label: "🛖 Thatched Eaves Waterfall & Bamboo Veranda" }, { val: "rainy_cabin_bedroom", label: "🛏️ Glass Cabin Bedroom" }, { val: "rainy_attic_loft", label: "🕯️ Rain on Skylight Attic" }, { val: "lake_reflection_rain", label: "💧 Mirror Mountain Pond" }],
  "relax/waterfall": [{ val: "monumental_plunge", label: "🌊 Roaring Cataract Plunge" }, { val: "tiered_mossy_cascade", label: "🏞️ Multi-Tiered Cascades" }, { val: "icelandic_canyon_fall", label: "🌋 Basalt Column Waterfall" }],
  "relax/hearth": [{ val: "pebble_beach_shore", label: "🏖️ Pebble Shore Fire Ring" }, { val: "cliffside_stone_hearth", label: "🌊 Cliffside Stone Hearth" }, { val: "driftwood_cove_fire", label: "🪵 Driftwood Cove Fire" }, { val: "rainy_hearth_bedroom", label: "🛏️ Cabin Hearth Bedroom" }],
  "relax/cozy": [{ val: "glass_cabin_bedroom", label: "🛏️ Biophilic Bedroom & Rain" }, { val: "mountain_chalet_living", label: "🪵 Chalet Living & Fireplace" }, { val: "rainy_patio_terrace", label: "☕ Garden Patio & Hearth" }, { val: "library_reading_nook", label: "📚 Reading Nook & Soft Rain" }],
  "relax/healing": [{ val: "himalayan_valley", label: "🏔️ Himalayan Valley & Bowls" }, { val: "geothermal_mineral_pool", label: "♨️ Geothermal Mineral Pools" }, { val: "redwood_cathedral", label: "🌲 Redwood Grove Cathedral" }, { val: "bali_sacred_water", label: "✨ Bali Sacred Water Temple" }],
  "relax/zen": [{ val: "karesansui_temple", label: "🪷 Kyoto Raked Stone Garden" }, { val: "sagano_bamboo_basin", label: "🎋 Bamboo Grove & Basin" }, { val: "sacred_lotus_pond", label: "🪷 Sacred Lotus Pond & Koi" }],
  "relax/ambient": [{ val: "nordic_aurora_fjord", label: "🌌 Nordic Aurora Borealis" }, { val: "twilight_alpine_valley", label: "✨ Velvet Twilight Cabin" }, { val: "desert_oasis_starlight", label: "🏜️ Desert Oasis & Milky Way" }, { val: "biophilic_greenhouse", label: "🌿 Greenhouse & Velvet Rain" }],
  "documentary": [
    { val: "open_topic_documentary", label: "🌐 Universal / Open Topic (Type anything in prompt box)" },
    { val: "ancient_civilizations_history", label: "🏛️ Ancient Civilizations & World History (Indus Valley, Rome, Egypt, etc.)" },
    { val: "giza_megalithic_pyramids", label: "🏛️ Ancient Giza & Megalithic Engineering" },
    { val: "scotland_highlands_isles", label: "🏰 Scottish Highlands, Castles & Historic Isles" },
    { val: "swiss_alps_valleys", label: "🏔️ Swiss Alps & Glacial Valleys (Lauterbrunnen / Zermatt)" },
    { val: "iceland_volcanic_coasts", label: "🌋 Iceland: Land of Fire & Glacial Ice" },
    { val: "pacific_northwest_redwoods", label: "🌲 Olympic Rainforest & Redwood Giants" },
    { val: "serengeti_savannah_predators", label: "🦁 Serengeti Great Migration & Savannah" },
    { val: "whitehaven_barrier_reef", label: "🏖️ Great Barrier Reef & Whitehaven Beach" },
    { val: "amalfi_cliffside_mediterranean", label: "🌊 Amalfi Coast & Azure Sea Cliffs" },
    { val: "sahara_dunes_canyons", label: "🏜️ Sahara Monumental Star Dunes" }
  ],
  "doc/nations": [
    { val: "ancient_history_dynasties", label: "⏳ Deep History: Founding Dynasties & Eras" },
    { val: "national_identity_heritage", label: "👑 Soul of the Nation: Identity & Heritage" },
    { val: "great_cities_metropolises", label: "🏙️ Great Cities & Urban Marvels" },
    { val: "natural_history_geology", label: "🌋 Natural History & Geological Marvels" },
    { val: "spiritual_sanctuaries", label: "🪔 Spiritual Centers & Sacred Sanctuaries" },
    { val: "cultural_entertainment_zones", label: "🎭 Cultural Life, Entertainment & Festivals" },
    { val: "sports_arenas_legacy", label: "🏟️ Sports Heritage & Iconic Arenas" },
    { val: "luminaries_pioneers", label: "📜 Famous Figures, Luminaries & Pioneers" },
    { val: "modern_evolution_transformation", label: "🚀 Modern Evolution & Future Transformation" },
    { val: "scenic_landscapes_horizons", label: "🌄 Scenic Beauty: Horizons & Postcard Vistas" },
    { val: "provinces_regional_countryside", label: "🌾 Regional Landscapes, Provinces & Countryside" },
    { val: "biodiversity_untamed_wildlife", label: "🌿 Biodiversity, National Parks & Living Nature" },
    { val: "climate_seasons_weather", label: "⛅ Climate, Seasons & Atmospheric Weather" },
    { val: "engineering_marvels", label: "📐 Engineering Feats & Architectural Wonders" },
    { val: "history_architecture", label: "🏛️ Ancient History & Monumental Architecture" },
    { val: "archaeological_ruins_lost_empires", label: "🏺 Ancient Ruins, Megaliths & Lost Civilizations" },
    { val: "culinary_gastronomic_heritage", label: "🍷 Culinary Traditions, Food Markets & Gastronomy" },
    { val: "living_traditions_artisan_crafts", label: "🎨 Living Traditions, Folk Festivals & Master Artisans" },
    { val: "coastal_islands_maritime", label: "🏖️ Coastal Wonders, Historic Ports & Island Sanctuaries" },
    { val: "historic_trade_routes_journeys", label: "🧭 Historic Trade Routes, Mountain Passes & Trails" },
    { val: "geographic_regions_zones", label: "🗺️ Geographic Regions, Territories & Zones" },
    { val: "cultural_mosaic_traditions", label: "🪕 Cultural Mosaic, Sub-Cultures & Traditions" }
  ],
  "documentary:tour": [
    { val: "itinerary_map_tour", label: "🗺️ Itinerary Tour (Ordered Route, Day Plan & Connecting Map)" },
    { val: "grand_tour", label: "🏛️ Grand Tour (City Highlights, Plazas & Defining Vistas)" },
    { val: "top_attractions_tour", label: "⭐ Top Attractions Tour (Must-See Landmarks in Sequence)" },
    { val: "local_neighborhood_tour", label: "🏘️ Local Neighborhood Tour (Squares, Local Cafes & Hidden Gems)" },
    { val: "culinary_food_tour", label: "🍽️ Culinary & Food Tour (Historic Markets, Bakeries & Eateries)" },
    { val: "architecture_design_tour", label: "📐 Architecture & Design Tour (Classical to Modernist Marvels)" }
  ],
  "travel_walking": [{ val: "rain_city_walk", label: "🌧️ 4K Rain Walking Tour" }, { val: "swiss_village_walk", label: "🏡 Swiss Alpine Village Lane" }, { val: "historic_old_town", label: "🏙️ Historic Old Town Street" }, { val: "coastal_bluff_trail", label: "🏖️ Coastline Cliffside Trail" }, { val: "bamboo_forest_path", label: "🎋 Bamboo Grove Walking Path" }],
  "dance/folk": [{ val: "village_jathara_square", label: "🎪 Village Fairground Stage" }, { val: "lush_paddy_fields", label: "🌾 Verdant Paddy Fields" }, { val: "historic_fort_courtyard", label: "🏛️ Ancient Stone Fort" }, { val: "modern_city_rooftop", label: "🌆 Neon City Rooftop Stage" }],
  "comedy/satire": [{ val: "it_wfh_apartment", label: "💻 Modern Apartment WFH Office" }, { val: "street_chai_stall", label: "☕ Bustling Street Chai Stall" }, { val: "village_panchayat_tree", label: "🌳 Village Banyan Tree Chhavadi" }, { val: "corporate_meeting_room", label: "🏢 Corporate Conference Room" }],
  "science": [
    { val: "deep_space_webb", label: "🪐 James Webb Deep Field & Cosmic Dawn" },
    { val: "deep_ocean_abyss", label: "🌊 Mariana Trench & Abyssal Hydrothermal Vents" },
    { val: "neuroscience_brain_connectome", label: "🧠 Human Connectome & Synaptic Mind" },
    { val: "quantum_superposition", label: "⚛️ Quantum Superposition & Entanglement" },
    { val: "fusion_energy_tokamak", label: "⚡ Tokamak Fusion Energy & Magnetic Fields" }
  ],
  "science:science_space": [
    { val: "deep_space_webb", label: "🪐 James Webb Deep Field & Cosmic Dawn" },
    { val: "black_holes_gravity", label: "🕳️ Black Hole Singularities & Gravitational Waves" },
    { val: "solar_system_moons", label: "🌕 Subsurface Oceans: Europa & Enceladus" },
    { val: "exoplanets_alien_worlds", label: "🔭 Exoplanets & The Goldilocks Zone" }
  ],
  "science:science_earth": [
    { val: "deep_ocean_abyss", label: "🌊 Mariana Trench & Abyssal Hydrothermal Vents" },
    { val: "plate_tectonics_volcano", label: "🌋 Mantle Plumes & Supervolcano Calderas" },
    { val: "paleontology_fossil_epochs", label: "🦕 Deep Time & The Cambrian Explosion" },
    { val: "extreme_meteorology", label: "🌪️ Atmospheric Supercells & Jet Streams" }
  ],
  "science:human_evolution": [
    { val: "hominin_origins_rift_valley", label: "🦴 Rift Valley Hominins & Bipedal Dawn" },
    { val: "ice_age_neanderthals", label: "❄️ Neanderthals & Denisovans: Ice Age Survival" },
    { val: "mastery_of_fire_stone_tools", label: "🔥 Fire Mastery & Acheulean Tool Flaking" },
    { val: "cognitive_revolution_cave_art", label: "🎨 Lascaux Cave Art & Shamanic Rituals" }
  ],
  "science:science_medicine": [
    { val: "neuroscience_brain_connectome", label: "🧠 Human Connectome & Synaptic Mind" },
    { val: "cellular_microbiology", label: "🔬 Nanomachines of Life: Cellular Mitosis" },
    { val: "genetics_crispr_dna", label: "🧬 CRISPR Gene Editing & Double Helix DNA" },
    { val: "immunology_body_defense", label: "🛡️ The Immune Fortress & T-Cell Warfare" }
  ],
  "science:science_physics": [
    { val: "quantum_superposition", label: "⚛️ Quantum Superposition & Entanglement" },
    { val: "particle_accelerator_cern", label: "💥 Inside CERN: Large Hadron Collider & Higgs" },
    { val: "atomic_lattice_microscopy", label: "🔬 Atomic Lattice & Scanning Tunneling Microscopy" },
    { val: "thermodynamics_entropy", label: "⏳ Arrow of Time: Entropy & Absolute Zero" }
  ],
  "science:science_tech": [
    { val: "fusion_energy_tokamak", label: "⚡ Tokamak Fusion Energy & Magnetic Confinement" },
    { val: "quantum_computing", label: "💻 Quantum Supremacy & Cryostat Qubits" },
    { val: "deep_space_propulsion", label: "🚀 Interstellar Propulsion: Ion Thrusters & Sails" },
    { val: "megastructures_future", label: "🏗️ Megastructures: Orbital Rings & Dyson Swarms" }
  ],
  "music/static_vocal": [
    { val: "local_country_heritage", label: "🏛️ Local Regional Heritage & Ancient Architecture" },
    { val: "local_riverside_ghats", label: "🌊 Local Sacred Riverside & Morning Mist" },
    { val: "local_lush_countryside", label: "🌾 Local Verdant Countryside & Green Meadows" },
    { val: "swiss_alps_snow", label: "🏔️ Swiss Alps Snow Peaks & Pines (International)" },
    { val: "paris_seine_terrace", label: "🗼 Paris Rooftop & Seine Riverfront (International)" },
    { val: "kyoto_bamboo_temple", label: "🎋 Kyoto Bamboo Grove & Shrines (International)" },
    { val: "santorini_cliffside", label: "🌊 Santorini White Cliffside & Aegean Sea (International)" },
    { val: "dolomites_meadow", label: "⛰️ Dolomites Wildflower Meadows & Glacial Stream" }
  ],
  "music/solo_singer": [
    { val: "local_country_heritage", label: "🏛️ Local Regional Heritage & Ancient Architecture" },
    { val: "local_riverside_ghats", label: "🌊 Local Sacred Riverside & Morning Mist" },
    { val: "local_lush_countryside", label: "🌾 Local Verdant Countryside & Green Meadows" },
    { val: "local_historic_street", label: "🏮 Local Historic Old Town & Twilight Lanterns" },
    { val: "swiss_alps_snow", label: "🏔️ Swiss Alps Snow Peaks & Pines (International)" },
    { val: "paris_seine_terrace", label: "🗼 Paris Rooftop & Seine Riverfront (International)" },
    { val: "santorini_cliffside", label: "🌊 Santorini White Cliffside & Aegean Sea (International)" }
  ],
  "music/duet_romance": [
    { val: "local_lush_countryside", label: "🌾 Local Verdant Countryside & Green Meadows" },
    { val: "local_riverside_ghats", label: "🌊 Local Sacred Riverside & Morning Mist" },
    { val: "swiss_alps_snow", label: "🏔️ Swiss Alps Snow Peaks & Pines (International)" },
    { val: "dolomites_meadow", label: "⛰️ Dolomites Wildflower Meadows & Glacial Stream" },
    { val: "paris_seine_terrace", label: "🗼 Paris Rooftop & Seine Riverfront (International)" },
    { val: "santorini_cliffside", label: "🌊 Santorini White Cliffside & Aegean Sea (International)" }
  ],
  "music/concert_live": [
    { val: "local_heritage_palace", label: "🏛️ Grand Historic Palace Arena Courtyard" },
    { val: "festival_fairgrounds", label: "🎆 Illuminated Fairgrounds & Night Sky Pyrotechnics" },
    { val: "modern_stadium_stage", label: "🏟️ 4K Laser Stadium Stage & Moving Beams" }
  ],
  "dance/folk": [
    { val: "festive_village_square", label: "🎪 Vibrant Village Festival Square & Jathara" },
    { val: "local_lush_countryside", label: "🌾 Swaying Emerald Paddy Fields & Coconut Palms" },
    { val: "ancient_banyan_platform", label: "🌳 Sacred Ancient Banyan Tree Platform" },
    { val: "historic_temple_gopuram", label: "🛕 Grand Temple Gopuram Courtyard" }
  ],
  "music/mass_song": [
    { val: "mass_jathara_grounds", label: "🎪 Festive Mass Jathara Fairgrounds & Confetti" },
    { val: "festive_village_square", label: "🎪 Vibrant Village Festival Square & Banners" },
    { val: "local_heritage_palace", label: "🏛️ Grand Historic Palace Arena Courtyard" },
    { val: "modern_city_rooftop", label: "🌆 Neon City Rooftop Stage" }
  ]
};

const STUDIO_ARCHETYPE_HINTS = {
  open_topic_documentary: "e.g. Enter any documentary topic: Space Exploration, Quantum Computing, Renaissance Philosophy, Deep Ocean Trenches, Silk Road...",
  ancient_civilizations_history: "e.g. Indus Valley Civilization 2500 BCE: Mohenjo-daro & Harappa urban planning, Great Bath, trade networks...",
  living_impressionism: "e.g. Masterpiece living oil painting with visible textured brushstrokes, gently rippling water lilies, and Debussy piano...",
  grand_gallery: "e.g. Elegant high-ceilinged museum gallery at twilight, warm gallery spotlights illuminating gilded oil canvases, peaceful reverb...",
  artist_atelier: "e.g. Sunbeams cutting through a Paris rooftop artist loft, wooden easels, paint palettes, resting oil canvases, warm dust motes...",
  sumie_ukiyoe: "e.g. Living Japanese woodblock print with gentle rolling Great Wave swells, falling cherry blossom petals, koto and shakuhachi...",
  stained_glass: "e.g. Monumental Gothic cathedral rose stained glass casting kaleidoscopic jewel-toned sunlight across stone floors...",
  klimt_gold_leaf: "e.g. Gustav Klimt inspired gold leaf textures with flowing marble fluid dynamics, undulating metallic pigments, velvet pads...",
  surrealist_dream: "e.g. Salvador Dali inspired ethereal floating architectural archways, celestial moons, and dream gardens in starry night...",
  cities: "e.g. 4K cinematic drone flight over illuminated city skyline, landmark towers, and futuristic bridges with evening traffic glow...",
  remote_places: "e.g. Remote untouched mountain frontier with glacial valleys, zero human structures, pure raw wilderness...",
  tourist_places: "e.g. Vibrant Mediterranean coastal harbor, turquoise waters, pastel promenades, and bustling seaside charm...",
  spiritual_places: "e.g. Sacred ancient temple complex with towering gopurams, incense mist, and sacred river reflections...",
  iconic_places: "e.g. Ancient stone fortress ramparts and heritage citadel arches glowing with warm alpenglow...",
  natural_wonders: "e.g. Monumental geological chasm, roaring cataract, or geothermal emerald pools in dramatic landscape...",
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
  bamboo_hut_veranda: "e.g. Rustic bamboo pavilion veranda in a peaceful tropical village during heavy torrential rainfall, thatched roof eaves with water cascading down in continuous glassy sheets and droplets...",
  peaceful_village_sleep: "e.g. Cozy outdoor sleeping bed with plush duvet on sheltered wooden veranda deck of a bamboo hut, heavy rain pouring outside, warm lantern glow...",
  misty_forest_stream: "e.g. Ancient mossy rainforest canopy with gentle stream and floating leaves...",
  alpine_peaks_meadow: "e.g. Towering Swiss Alps snow-capped jagged peaks, lush wildflower meadows, and crystal mountain stream...",
  monumental_plunge: "e.g. Monumental roaring cataract plunging into turquoise pool with heavy rising mist...",
  pebble_beach_shore: "e.g. Gentle rain falling on warm driftwood campfire burning on wet pebble shoreline by ocean surf...",
  glacial_mirror_lake: "e.g. Mirror-still turquoise glacial lake reflecting towering pine-covered granite cliffs...",
  karesansui_temple: "e.g. Peaceful Kyoto dry raked stone garden, bamboo water fountain, and cedar veranda...",
  himalayan_valley: "e.g. Sacred Himalayan valley with singing bowls, crystal dawn sunbeams, and restorative 528Hz serenity...",
  swiss_alps_valleys: "e.g. Lauterbrunnen Valley & Jungfrau, Swiss Alps: Sheer 1,000ft limestone rock walls, Staubbach waterfall mist, emerald meadows, and traditional timber chalets...",
  itinerary_map_tour: "e.g. Oslo Tour, 2 Days: Day 1 Opera House, Akershus Fortress & harbor, Day 2 Vigeland Park & Holmenkollen with connecting route map transitions...",
  grand_tour: "e.g. London Tour: Buckingham Palace, Westminster Abbey, Tower Bridge, and the River Thames in crisp 5500K daylight...",
  top_attractions_tour: "e.g. Rome Tour: Colosseum amphitheater, Roman Forum, Trevi Fountain, and Pantheon in cinematic daylight...",
  local_neighborhood_tour: "e.g. Paris Tour: Bohemian Montmartre cobblestone lanes, artisan street cafes, secret corner plazas, and Sacré-Cœur vistas...",
  culinary_food_tour: "e.g. Tokyo Tour: Tsukiji outer market food stalls, artisan ramen houses, historic bakeries, and traditional street stalls...",
  heritage_history_tour: "e.g. Edinburgh Tour: Royal Mile medieval stone closes, Edinburgh Castle rock ramparts, and Holyroodhouse Palace...",
  architecture_design_tour: "e.g. Barcelona Tour: Antoni Gaudí's Sagrada Família geometric towers, modernist Casa Batlló facade, and Gothic Quarter stone arches...",
  iceland_volcanic_coasts: "e.g. South Coast of Iceland: Basalt sea stacks of Reynisfjara, roaring Skógafoss cataract plumes, and vast black volcanic sands meeting Arctic white surf...",
  scotland_highlands_isles: "e.g. Isle of Skye & Glen Coe: Jagged volcanic pinnacle of the Old Man of Storr, purple heather moorlands, and moody mist rolling over Scottish lochs...",
  whitehaven_barrier_reef: "e.g. Whitsunday Islands & Whitehaven Beach: Swirling turquoise tidal estuaries over pure silica sandbars, aerial drone perspective over the Great Barrier Reef...",
  amalfi_cliffside_mediterranean: "e.g. Amalfi Coast, Italy: Pastel-hued cliffside villas perched over azure Tyrrhenian waters, terraced lemon orchards, and dramatic Mediterranean sea caves...",
  serengeti_savannah_predators: "e.g. Serengeti Plains at Dawn: Golden grass whispering in morning breeze, lioness stalking acacia shadows, and dust billowing from the Great Migration...",
  pacific_northwest_redwoods: "e.g. Hoh Rainforest & Redwood Coast: 300ft ancient conifers draped in velvet club moss, crystal glacial riverbeds, and soft volumetric god rays piercing fog...",
  sahara_dunes_canyons: "e.g. Erg Chebbi & Grand Canyon: Monumental 500ft terracotta sand crests carved by desert wind, sharp razor-edge shadows, and infinite arid horizon...",
  giza_megalithic_pyramids: "e.g. Giza Plateau at Golden Dawn: Khufu's Great Pyramid towering against desert sky, weathering limestone courses, and low desert wind sweeping golden sands...",
  deep_space_webb: "e.g. Cosmic Dawn: James Webb Space Telescope infrared vista of redshifted early galaxies 13.4 billion years ago...",
  black_holes_gravity: "e.g. Event Horizon: Supermassive black hole accretion disk glowing with relativistic Doppler beaming and gravitational lensing...",
  solar_system_moons: "e.g. Subsurface Oceans: Europa's icy fractured crust, cryovolcanic water vapor geysers, and hydrothermal vents...",
  exoplanets_alien_worlds: "e.g. Exoplanetary Atmospheres: Atmospheric transmission spectroscopy of TRAPPIST-1e in the habitable Goldilocks zone...",
  deep_ocean_abyss: "e.g. The Hadal Zone: Mariana Trench 11,000m abyssal plain, hydrothermal black smoker chimneys, and chemotrophic microbes...",
  plate_tectonics_volcano: "e.g. Earth's Molten Engine: Subducting tectonic plates, mantle plume upwelling, and Yellowstone caldera magma chamber...",
  paleontology_fossil_epochs: "e.g. Deep Time: Burgess Shale fossil beds, Cambrian explosion multicellular life forms, and primordial seas...",
  extreme_meteorology: "e.g. Atmospheric Supercells: Mesocyclone rotation, jet stream shear, and lightning dynamics in tornadic storm systems...",
  neuroscience_brain_connectome: "e.g. The Human Connectome: Fluorescent synaptic firing pathways, neocortex neural plasticity, and neurotransmitter diffusion...",
  cellular_microbiology: "e.g. Nanomachines of Life: Cryo-electron microscopy of ATP synthase molecular motors, ribosome translation, and mitosis...",
  genetics_crispr_dna: "e.g. The Genetic Code: CRISPR-Cas9 ribonucleoprotein navigating double-helix DNA chromatin in cell nucleus...",
  immunology_body_defense: "e.g. The Immune Fortress: Cytotoxic T-cells hunting viral pathogens, macrophage engulfment, and antibody binding cascades...",
  quantum_superposition: "e.g. Quantum Superposition: Single-photon double slit wave-particle interference patterns and quantum entanglement states...",
  particle_accelerator_cern: "e.g. Inside CERN: Superconducting quad magnets, 13 TeV proton-proton bunch crossings, and Higgs boson decay signatures...",
  atomic_lattice_microscopy: "e.g. Imaging the Atom: Sub-angstrom scanning tunneling microscopy showing individual silicon crystal atomic lattice points...",
  thermodynamics_entropy: "e.g. The Arrow of Time: Thermodynamic entropy increase, cosmic microwave background, and asymptotic heat death of the universe...",
  fusion_energy_tokamak: "e.g. Harnessing Star Power: 100-million-degree deuterium-tritium plasma swirling within superconducting tokamak magnetic fields...",
  quantum_computing: "e.g. Quantum Supremacy: Golden chandelier dilution refrigerator cryostat cooled to 15 millikelvin with superconducting transmon qubits...",
  deep_space_propulsion: "e.g. Interstellar Propulsion: Hall effect xenon ion thruster glowing electric blue, interstellar solar sail accelerated by orbital laser...",
  megastructures_future: "e.g. Planetary Megastructures: Geosynchronous orbital ring tethered to planetary space elevators and circumstellar Dyson swarm collector arrays...",
  hominin_origins_rift_valley: "e.g. East African Rift Valley: Australopithecus hominins walking upright across ancient savannah, Olduvai Gorge basalt strata...",
  ice_age_neanderthals: "e.g. Pleistocene Ice Age Eurasia: Neanderthal clan sheltering in limestone cave, woolly mammoth hunt in blizzard, Denisovan lineage...",
  mastery_of_fire_stone_tools: "e.g. The Dawn of Fire: Early hominins knapping flint Acheulean handaxes, striking pyrites to spark hearth fires, communal cooking...",
  cognitive_revolution_cave_art: "e.g. Chauvet & Lascaux Caves: Flickering animal fat lamp illuminating red ochre bison murals, hand stencils, deep cavern ritualism...",
  ancient_history_dynasties: "e.g. Chronicles of Poland: Piast dynasty foundations, Gniezno coronation cathedral, Teutonic knights...",
  national_identity_heritage: "e.g. Soul of Japan: Shinto shrines, imperial Chrysanthemum throne, samurai code, and timeless national heritage...",
  great_cities_metropolises: "e.g. Crowns of Italy: Rome, Florence, and Venice - marble piazzas, Renaissance palaces, and grand canals...",
  natural_history_geology: "e.g. Earth & Deep Time: Iceland's rift valley tectonic boundary, basalt lava tubes, and subglacial caldera...",
  spiritual_sanctuaries: "e.g. Sacred Sanctuaries of Greece: Meteora cliff-hanging monasteries, Mount Athos Byzantine frescoes, Delphi...",
  cultural_entertainment_zones: "e.g. Cultural Life of Austria: Vienna State Opera, historic coffeehouse literary salons, and Salzburg music festival...",
  sports_arenas_legacy: "e.g. Athletic Glory of the United Kingdom: Wimbledon grass courts, Wembley Stadium, and historic rowing boathouses...",
  luminaries_pioneers: "e.g. Luminaries of France: Marie Curie, Louis Pasteur, Victor Hugo, and Claude Monet - visionary pioneers who shaped history...",
  modern_evolution_transformation: "e.g. Modern Evolution of South Korea: From post-war recovery to Seoul high-tech digital metropolis and bullet trains...",
  scenic_landscapes_horizons: "e.g. Vistas of New Zealand: Southern Alps snow peaks, Milford Sound fjord waterfalls, and turquoise glacial lakes...",
  provinces_regional_countryside: "e.g. Hidden Provinces of Spain: Andalusia white villages, olive groves, Basque coastal fishing hamlets...",
  biodiversity_untamed_wildlife: "e.g. Untamed Brazil: Amazon rainforest canopy, Pantanal jaguar wetlands, and endemic river dolphin habitats...",
  climate_seasons_weather: "e.g. Four Seasons of Canada: Canadian Rockies autumn larches, winter blizzard icefields, and blooming alpine meadows...",
  engineering_marvels: "e.g. Master Builders of the Netherlands: Delta Works storm surge barrier, historic windmills, and canal engineering...",
  history_architecture: "e.g. Architectural Heritage of Germany: Neuschwanstein Castle, Cologne Cathedral Gothic spires, and Bauhaus design...",
  archaeological_ruins_lost_empires: "e.g. Lost Civilizations of Peru: Machu Picchu Inca granite masonry, Nazca lines, and sacred Urubamba ruins...",
  culinary_gastronomic_heritage: "e.g. Culinary Heritage of Vietnam: Hanoi street food alleyways, pho broth simmering over charcoal, and Mekong delta markets...",
  living_traditions_artisan_crafts: "e.g. Living Traditions of India: Varanasi silk weavers, Jaipur block-printing guilds, and Rajasthan desert folk fairs...",
  coastal_islands_maritime: "e.g. Maritime Wonders of Norway: Lofoten Islands fishing rorbuer, sheer fjord cliff walls, and Arctic cod drying racks...",
  historic_trade_routes_journeys: "e.g. The Great Silk Road of Uzbekistan: Samarkand turquoise tile domes, Bukhara trading caravanserais, and Kyzylkum desert trails...",
  geographic_regions_zones: "e.g. Regions of the United States: Pacific Northwest, American Southwest, New England, and Deep South...",
  cultural_mosaic_traditions: "e.g. Cultural Mosaic of India: Kashmiri, Punjabi, Bengali, Rajasthani, and Tamil living customs & heritage..."
};

