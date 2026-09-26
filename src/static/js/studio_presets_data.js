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
  theme: "Walking in the Rain",
  idea: "Delhi techie juggling dual remote jobs comedy satire",
  script: "SCENE 1: EXT. KITCHEN - DAY\nBoiling spiced masala chai heat transfer in 60s",
  youtube: "https://www.youtube.com/watch?v=-BLxlHRYpac"
};
