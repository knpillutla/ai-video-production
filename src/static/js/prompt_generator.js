// CineAI Studio: Prompt Hero, Dynamic Mode Templates & Clear Controller
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

function onStudioTierChange(tierKey) { selectProductionTier(tierKey); }

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
  theme: { ph: "Describe your theme (e.g., Walking in the Rain, Nature & Waterfalls, Wildlife, Oceans)...", hint: "Theme active • World Cities, Villages, Mountains, Oceans & Architecture" },
  idea: { ph: "Describe your creative story concept, characters, comedic angle...", hint: "Idea active • Narrative concepts, characters & comedy" },
  script: { ph: "Paste your screenplay, dialogue lines, voiceover narration, or scene breakdown...", hint: "Script active • Full screenplay, scene beats or dialogue stems" },
  youtube: { ph: "Enter prompt or styling directions to apply from reference video...", hint: "YouTube Reference active • Paste video link & prompt to apply reference styling, art & sound" }
};

function clearTemplateCardHighlights() {
  document.querySelectorAll("[id^='creative-card-']").forEach(c => c.classList.remove("ring-2", "ring-indigo-500"));
}

const MODE_TITLES = {
  theme: "Theme Presets (Nature, Animals, Heritage, Travel)",
  idea: "Story & Angle Ideas (Comedy, Sci-Fi, Street Food, Drama)",
  script: "Screenplay & Dialogue Stems (Voiceover, Dialogue, Explainer)",
  youtube: "YouTube Reference Styling (Drone, Vlog, Macro ASMR, Fast Cuts)"
};

function renderTemplatesForMode(mode) {
  const container = document.getElementById("creative-templates-container");
  if (!container) return;
  const templates = TEMPLATES_BY_MODE[mode] || TEMPLATES_BY_MODE.theme;
  const titleEl = document.getElementById("creative-presets-title");
  if (titleEl) titleEl.textContent = MODE_TITLES[mode] || "Creative Templates";

  container.innerHTML = templates.map((t, idx) => `
    <div id="creative-card-${t.id}" onclick="applyTemplate('${mode}', ${idx})" class="p-3.5 bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] hover:border-indigo-500/50 rounded-xl cursor-pointer transition space-y-1 group active:scale-95 shadow-sm">
      <div class="flex items-center justify-between">
        <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">${t.badge}</span>
        <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-gray-500 group-hover:text-indigo-400"></i>
      </div>
      <div class="font-bold text-white text-xs group-hover:text-indigo-300">${t.title}</div>
      <div class="text-[10px] text-gray-400 leading-tight">${t.desc}</div>
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

function selectCreativeTopic(topicKey) {
  for (const list of Object.values(TEMPLATES_BY_MODE)) {
    const found = list.find(t => t.id.includes(topicKey) || t.title.toLowerCase().includes(topicKey.toLowerCase()) || t.prompt.toLowerCase().includes(topicKey.toLowerCase()));
    if (found) { applyTemplate(currentCreationMode, found); return; }
  }
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

  // Strictly remove / hide YouTube reference container in Theme, Idea & Script modes
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

function usePresetPrompt(mode, text, url = null) {
  if (mode && mode !== currentCreationMode) setCreationMode(mode);
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");
  if (currentCreationMode === "youtube") {
    if (uInput && url) uInput.value = url;
    if (pInput) pInput.value = text;
  } else {
    if (uInput) uInput.value = "";
    if (pInput) pInput.value = text;
  }
  if (pInput) flashPromptInput(pInput);
  clearTemplateCardHighlights();
}

function clearStudioInputs() {
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");
  if (pInput) { pInput.value = ""; pInput.focus(); flashPromptInput(pInput); }
  if (uInput) uInput.value = "";
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

// Authoritative user inputs: Always uses current input values (user edits override templates)
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

// When user manually types into input fields, remove template preset card selection highlight
document.addEventListener("DOMContentLoaded", () => {
  const pInput = document.getElementById("youtube-prompt-input");
  const uInput = document.getElementById("youtube-url-input");
  if (pInput) pInput.addEventListener("input", clearTemplateCardHighlights);
  if (uInput) uInput.addEventListener("input", clearTemplateCardHighlights);
  // Initialize mode templates on startup (defaults to theme, YouTube URL hidden)
  setCreationMode("theme", false);
});
