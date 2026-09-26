// CineAI Studio: Prompt Hero, Dynamic Niche Radio Groups & Tier Controller
let currentCreationMode = "theme";

function selectProductionTier(tierKey) {
  currentTier = tierKey;
  ["low_cost", "balanced", "cinematic"].forEach(t => {
    const card = document.getElementById("tier-card-" + t);
    const radio = document.getElementById("tier-radio-" + t);
    if (!card) return;
    const isSel = t === tierKey;
    card.className = isSel
      ? "p-3 bg-indigo-950/40 border-2 border-indigo-500 rounded-xl cursor-pointer transition ring-1 ring-indigo-500/40"
      : "p-3 bg-slate-950/70 border border-slate-800 hover:border-indigo-500/50 rounded-xl cursor-pointer transition";
    if (radio) radio.checked = isSel;
  });
  const sel = document.getElementById("studio-tier-select");
  const pill = document.getElementById("sidebar-tier-price-pill");
  const tier = PRODUCTION_TIERS[tierKey] || PRODUCTION_TIERS.balanced;
  if (sel) sel.value = tierKey;
  if (pill) pill.textContent = tier.priceStr;
}

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

function selectNicheRadio(nicheKey) {
  const cfg = NICHE_RADIO_CONFIGS[nicheKey];
  if (!cfg) return;

  const promptInput = document.getElementById("youtube-prompt-input");
  if (promptInput) {
    promptInput.value = cfg.prompt;
    flashPromptInput(promptInput);
  }

  const setC = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };
  const setV = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };

  setC("studio-toggle-bgm", cfg.bgm);
  setC("studio-toggle-voice-over", cfg.voice);
  setC("studio-toggle-pure-nature", cfg.pureNature);
  setV("studio-fps", cfg.fps || "24");

  if (typeof togglePureNatureMode === "function") {
    togglePureNatureMode(cfg.pureNature);
  }
}

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

const MODE_CONFIG = {
  theme: { ph: "Describe your theme or select a niche radio button above...", hint: "Theme active • World Cities, Villages, Mountains, Oceans & Architecture" },
  idea: { ph: "Describe your creative story concept, characters, comedic angle...", hint: "Idea active • Narrative concepts, characters & comedy" },
  script: { ph: "Paste your screenplay, dialogue lines, voiceover narration, or scene breakdown...", hint: "Script active • Full screenplay, scene beats or dialogue stems" },
  youtube: { ph: "Enter prompt or styling directions to apply from reference video...", hint: "YouTube Reference active • Paste video link & prompt to apply reference styling" }
};

function clearTemplateCardHighlights() {
  document.querySelectorAll("[id^='creative-card-']").forEach(c => c.classList.remove("ring-2", "ring-indigo-500"));
}

function renderTemplatesForMode(mode) {
  const container = document.getElementById("creative-templates-container");
  if (!container) return;
  const templates = TEMPLATES_BY_MODE[mode] || TEMPLATES_BY_MODE.theme;
  const titleEl = document.getElementById("creative-presets-title");
  if (titleEl) titleEl.textContent = mode === "theme" ? "Theme Presets (Nature, Wildlife, Heritage, Travel)" : "Creative Templates";

  container.innerHTML = templates.map((t, idx) => `
    <div id="creative-card-${t.id}" onclick="applyTemplate('${mode}', ${idx})" class="p-3.5 bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] hover:border-indigo-500/50 rounded-xl cursor-pointer transition space-y-1 group active:scale-95 shadow-sm">
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${t.badge}</span>
        <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-gray-500 group-hover:text-indigo-400"></i>
      </div>
      <div class="font-bold text-slate-900 dark:text-white text-xs group-hover:text-indigo-300">${t.title}</div>
      <div class="text-[10px] text-slate-600 dark:text-gray-400 leading-tight">${t.desc}</div>
    </div>
  `).join("");
}

function applyTemplate(mode, idxOrObj) {
  const list = TEMPLATES_BY_MODE[mode] || TEMPLATES_BY_MODE.theme;
  const t = typeof idxOrObj === "number" ? list[idxOrObj] : idxOrObj;
  if (!t) return;
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");

  if (mode === "youtube") {
    if (uInput) { uInput.value = t.url || ""; flashPromptInput(uInput); }
  } else if (uInput) { uInput.value = ""; }
  if (pInput) { pInput.value = t.prompt; flashPromptInput(pInput); }

  clearTemplateCardHighlights();
  document.getElementById("creative-card-" + t.id)?.classList.add("ring-2", "ring-indigo-500");
}

function setCreationMode(mode, autoPopulate = false) {
  currentCreationMode = mode;
  ["theme", "idea", "script", "youtube"].forEach(m => {
    const btn = document.getElementById("mode-pill-" + m);
    if (btn) {
      btn.className = m === mode
        ? "px-3.5 py-1 text-xs font-bold rounded-lg transition bg-indigo-600 text-white shadow flex items-center gap-1.5 ring-1 ring-indigo-400"
        : "px-3.5 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5";
    }
  });

  const textarea = document.getElementById("youtube-prompt-input");
  const urlInput = document.getElementById("youtube-url-input");
  const urlContainer = document.getElementById("youtube-url-container");
  const genreShelf = document.getElementById("theme-genre-shelf");
  const hint = document.getElementById("creation-mode-hint");
  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.theme;

  if (textarea) {
    textarea.placeholder = cfg.ph;
    if (hint) hint.textContent = cfg.hint;
    if (autoPopulate) {
      if (mode === "youtube") {
        if (urlInput && !urlInput.value) urlInput.value = MODE_STARTERS.youtube;
        textarea.value = "India in 4K - Apply drone aerials, golden-hour temple lighting, and sitar soundtrack";
        flashPromptInput(urlInput);
      } else {
        textarea.value = MODE_STARTERS[mode] || "";
      }
      flashPromptInput(textarea);
    }
  }

  if (genreShelf) {
    genreShelf.classList.toggle("hidden", mode !== "theme");
  }

  if (urlContainer) {
    if (mode === "youtube") {
      urlContainer.classList.remove("hidden");
    } else {
      urlContainer.classList.add("hidden");
      if (urlInput) urlInput.value = "";
    }
  }

  renderTemplatesForMode(mode);
}

function flashPromptInput(el) {
  if (!el) return;
  el.classList.add("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40");
  setTimeout(() => el.classList.remove("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40"), 1000);
}

function clearStudioInputs() {
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");
  if (pInput) { pInput.value = ""; pInput.focus(); flashPromptInput(pInput); }
  if (uInput) uInput.value = "";
  document.querySelectorAll("input[name='niche_theme_radio']").forEach(r => r.checked = false);
  const setV = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
  const setC = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };
  setV("studio-duration", "10"); setC("studio-toggle-bgm", true); setC("studio-toggle-voice-over", true);
  setC("studio-toggle-tts", false); setC("studio-toggle-lipsync", false);
  setV("studio-voice-gender", "female"); setV("studio-language", "en");
  clearTemplateCardHighlights();
  selectProductionTier("low_cost");
}

function deriveTitleFromInput(text, mode) {
  if (!text) return mode === "youtube" ? "Adaptive Remake" : "Explore Niagara Falls";
  const firstLine = text.split("\n").map(l => l.trim()).find(l => l.length > 0) || text;
  const clean = firstLine.replace(/^(title|theme|idea|script|scene\s*\d*)\s*[:\-]\s*/i, "").trim();
  return clean.length > 40 ? clean.slice(0, 38) + "..." : clean;
}

function quickTestProduceFromPrompt() {
  const promptInput = document.getElementById("youtube-prompt-input");
  const urlInput = document.getElementById("youtube-url-input");
  let userPrompt = (promptInput?.value || "").trim();
  const userUrl = (urlInput?.value || "").trim();

  if (!userPrompt && !userUrl) userPrompt = MODE_STARTERS[currentCreationMode] || "Untamed Rainforests";
  if (promptInput) promptInput.value = "";
  if (urlInput) urlInput.value = "";
  clearTemplateCardHighlights();

  const title = deriveTitleFromInput(userPrompt, currentCreationMode);
  let concept = userPrompt, prodType = "Theme", themeVal = null, ideaVal = null, scriptVal = null, ytUrl = null;

  if (currentCreationMode === "theme") { prodType = "Theme"; themeVal = userPrompt; }
  else if (currentCreationMode === "idea") { prodType = "Idea"; ideaVal = userPrompt; }
  else if (currentCreationMode === "script") { prodType = "Script"; scriptVal = userPrompt; }
  else if (currentCreationMode === "youtube") {
    prodType = "YouTube Reference"; ytUrl = userUrl || null;
    concept = userPrompt ? `${userPrompt} [Referencing: ${userUrl || 'YouTube Reference'}]` : `Transformative adaptation referencing YouTube: ${userUrl}`;
  }

  let vType = "Travel Guide & Doc", fmtType = "Long (16:9)", styType = "Realistic (Photoreal)", fmtStr = "Documentary (16:9)";
  const pLower = userPrompt.toLowerCase();
  if (pLower.includes("comedy") || pLower.includes("satire") || currentCreationMode === "idea") {
    vType = "Comedy Reel"; fmtType = "Short (9:16)"; fmtStr = "Shorts (9:16)";
  } else if (currentCreationMode === "script") { vType = "Web Series"; }

  const tier = PRODUCTION_TIERS[currentTier] || PRODUCTION_TIERS.low_cost;
  currentUser.balance_usd = Math.max(0, currentUser.balance_usd - tier.priceUsd);
  saveUserState();

  const getChk = id => { const el = document.getElementById(id); return el ? el.checked : true; };
  const getVal = (id, fallback) => { const el = document.getElementById(id); return el?.value || fallback; };
  const langVal = getVal("studio-language", "en");
  const durationSec = parseInt(getVal("studio-duration", "10"), 10);

  const newId = `EP-00${studioVideos.length + 1}`;
  const uniqueJobId = `job_${newId.toLowerCase()}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  const newVid = {
    id: newId, jobId: uniqueJobId, title, concept,
    videoType: vType, formatType: fmtType, styleType: styType, productionType: prodType,
    status: "queued", youtubeStatus: "unpublished", youtubeChannel: null, youtubeUrl: null,
    youtubeReferenceUrl: ytUrl, videoUrl: "/static/videos/preview_master.mp4",
    durationSeconds: durationSec, duration: `${durationSec}s`,
    language: langVal === "te" ? "Telugu (te)" : (langVal === "hi" ? "Hindi (hi)" : "English (en)"),
    langCode: langVal, format: fmtStr, style: "Cinematic Photoreal",
    tierKey: tier.key, tierName: `${tier.name} (${tier.priceStr})`,
    cost: tier.priceUsd, costStr: tier.priceStr,
    theme: themeVal, idea: ideaVal, script: scriptVal,
    enableBgm: getChk("studio-toggle-bgm"), enableVoiceOver: getChk("studio-toggle-voice-over"),
    enableTts: document.getElementById("studio-toggle-tts")?.checked || false,
    enableLipsync: document.getElementById("studio-toggle-lipsync")?.checked || false,
    voiceGender: getVal("studio-voice-gender", "female"),
    createdAt: Date.now(), startedAt: null, completedAt: null, publishedAt: null
  };

  studioVideos.unshift(newVid);
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof switchTab === "function") switchTab("ledger");
  document.querySelector("main")?.scrollTo(0, 0);

  renderStudioVideoHistory();
  if (typeof selectLedgerVideo === "function") selectLedgerVideo(newId);

  const banner = document.getElementById("ledger-queued-banner");
  if (banner) {
    document.getElementById("banner-request-id")?.replaceChildren(uniqueJobId);
    const detail = document.getElementById("banner-request-detail");
    if (detail) detail.textContent = `Episode ${newId} ("${title}") is now queued. Production Type: ${prodType} • Billed: ${tier.priceStr}.`;
    banner.classList.remove("hidden");
  }

  showStudioModal({
    title: "Request Queued",
    message: `Request is queued with Request ID: ${uniqueJobId}\n\nEpisode: ${newId} — "${title}"\nProduction Type: ${prodType}\nTier: ${tier.name} (${tier.priceStr})`,
    nextStep: "Redirected to Video Ledger to monitor live synthesis."
  });

  if (typeof startLocalVideoProductionJob === "function") startLocalVideoProductionJob(newVid);
}

document.addEventListener("DOMContentLoaded", () => {
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");
  if (pInput) pInput.addEventListener("input", clearTemplateCardHighlights);
  if (uInput) uInput.addEventListener("input", clearTemplateCardHighlights);
  setCreationMode("theme", false);
});
