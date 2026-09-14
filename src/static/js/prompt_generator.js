// CineAI Studio: Prompt Hero & Quick Generate Controller
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

  const sidebarSelect = document.getElementById("studio-tier-select");
  const sidebarPill = document.getElementById("sidebar-tier-price-pill");
  const tier = PRODUCTION_TIERS[tierKey] || PRODUCTION_TIERS.balanced;
  if (sidebarSelect) sidebarSelect.value = tierKey;
  if (sidebarPill) sidebarPill.textContent = tier.priceStr;
}

function onStudioTierChange(tierKey) {
  selectProductionTier(tierKey);
}


let currentCreationMode = "theme";

const MODE_STARTERS = {
  theme: "Malaysia Exploration",
  idea: "Delhi techie juggling dual remote jobs comedy satire",
  script: "SCENE 1: EXT. KITCHEN - DAY\nBoiling spiced masala chai heat transfer in 60s",
  youtube: "https://www.youtube.com/watch?v=-BLxlHRYpac"
};

const MODE_CONFIG = {
  theme: { ph: "Describe your theme or documentary topic (e.g., Malaysia Exploration, Niagara Falls)...", hint: "Theme active • Documentary, World & Travel topics" },
  idea: { ph: "Describe your creative story concept, characters, comedic angle...", hint: "Idea active • Narrative concepts, characters & comedy" },
  script: { ph: "Paste your screenplay, dialogue lines, voiceover narration, or scene breakdown...", hint: "Script active • Full screenplay, scene beats or dialogue stems" },
  youtube: { ph: "Enter prompt or styling directions to apply from reference video (e.g. 4K drone cinematography, golden lighting, sitar BGM)...", hint: "YouTube Reference active • Paste video link & prompt to apply reference styling, art & sound" }
};

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
  if (urlContainer && mode === "youtube") {
    urlContainer.classList.add("ring-2", "ring-indigo-500", "rounded-xl");
    setTimeout(() => urlContainer.classList.remove("ring-2", "ring-indigo-500"), 1200);
  }
}

function flashPromptInput(el) {
  if (!el) return;
  el.classList.add("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40");
  setTimeout(() => {
    el.classList.remove("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40");
  }, 1000);
}

function usePresetPrompt(mode, text, url = null) {
  setCreationMode(mode, false);
  const promptInput = document.getElementById("youtube-prompt-input");
  const urlInput = document.getElementById("youtube-url-input");
  if (promptInput) {
    promptInput.value = text;
    flashPromptInput(promptInput);
    promptInput.scrollIntoView({ behavior: "smooth", block: "center" });
    promptInput.focus();
  }
  if (url && urlInput) {
    urlInput.value = url;
    flashPromptInput(urlInput);
  }
}

function quickTestProduceFromPrompt() {
  const promptInput = document.getElementById("youtube-prompt-input");
  const urlInput = document.getElementById("youtube-url-input");
  let prompt = (promptInput?.value || "").trim();
  const url = (urlInput?.value || "").trim();

  if (!prompt && !url) {
    prompt = MODE_STARTERS[currentCreationMode] || "Malaysia Exploration";
  }

  // Clear prompt and url inputs immediately as requested
  if (promptInput) promptInput.value = "";
  if (urlInput) urlInput.value = "";

  let title = "";
  let concept = "";
  let prodType = currentCreationMode === "theme" ? "Theme" : (currentCreationMode === "script" ? "Script" : (currentCreationMode === "youtube" ? "YouTube Reference" : "Idea"));
  let vType = "Travel Guide & Doc";
  let fmtType = "Long (16:9)";
  let styType = "Realistic (Photoreal)";
  let fmtStr = "Documentary (16:9)";

  const pLower = prompt.toLowerCase();
  const isDoc = pLower.includes("niagara") || pLower.includes("malaysia") || pLower.includes("explore") || pLower.includes("travel") || pLower.includes("doc") || pLower.includes("ocean") || pLower.includes("india");

  if (url || currentCreationMode === "youtube") {
    prodType = "YouTube Reference";
    title = prompt ? (prompt.length > 36 ? prompt.slice(0, 36) + "..." : prompt) : "Adaptive Remake";
    concept = prompt ? `${prompt} [Referencing: ${url || 'YouTube Reference'}]` : `Transformative adaptation referencing YouTube: ${url}`;
    vType = isDoc ? "Travel Guide & Doc" : "Culture & Heritage";
  } else if (prompt) {
    if (pLower.includes("malaysia")) {
      title = "Malaysia Exploration";
      concept = "Immersive travel guide across Malaysia's tropical rainforests, cultural heritage and modern Petronas towers.";
      vType = "Travel Guide & Doc";
    } else if (pLower.includes("niagara")) {
      title = "Explore Niagara Falls";
      concept = "Immersive cinematic exploration of Niagara Falls with geological history and aerial drone vistas.";
      vType = "Travel Guide & Doc";
    } else {
      title = prompt.length > 36 ? prompt.slice(0, 36) + "..." : prompt;
      concept = prompt;
      vType = isDoc ? "Travel Guide & Doc" : (currentCreationMode === "theme" ? "Web Series" : "Comedy Reel");
      if (vType === "Comedy Reel") { fmtType = "Short (9:16)"; fmtStr = "Shorts (9:16)"; }
    }
  } else {
    title = "Malaysia Exploration";
    concept = "Malaysia Exploration travel documentary and cultural showcase";
  }

  const tier = PRODUCTION_TIERS[currentTier] || PRODUCTION_TIERS.low_cost;
  currentUser.balance_usd = Math.max(0, currentUser.balance_usd - tier.priceUsd);
  saveUserState();

  const enableBgm = document.getElementById("studio-toggle-bgm") ? document.getElementById("studio-toggle-bgm").checked : true;
  const enableVoiceOver = document.getElementById("studio-toggle-voice-over") ? document.getElementById("studio-toggle-voice-over").checked : true;
  const enableTts = document.getElementById("studio-toggle-tts") ? document.getElementById("studio-toggle-tts").checked : false;
  const enableLipsync = document.getElementById("studio-toggle-lipsync") ? document.getElementById("studio-toggle-lipsync").checked : false;
  const voiceGender = document.getElementById("studio-voice-gender") ? document.getElementById("studio-voice-gender").value : "female";
  const langVal = document.getElementById("studio-language") ? document.getElementById("studio-language").value : "en";
  const durationSelect = document.getElementById("studio-duration");
  const durationSec = durationSelect ? parseInt(durationSelect.value, 10) : 10;

  const newId = `EP-00${studioVideos.length + 1}`;
  const uniqueJobId = `job_${newId.toLowerCase()}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  const newVid = {
    id: newId, jobId: uniqueJobId, title, concept,
    videoType: vType, formatType: fmtType, styleType: styType, productionType: prodType,
    status: "queued", youtubeStatus: "unpublished", youtubeChannel: null, youtubeUrl: null,
    youtubeReferenceUrl: url || null, videoUrl: "/static/videos/preview_master.mp4",
    durationSeconds: durationSec, duration: `${durationSec}s`,
    language: langVal === "en" ? "English (en)" : (langVal === "te" ? "Telugu (te)" : (langVal === "hi" ? "Hindi (hi)" : "English (en)")),
    langCode: langVal, format: fmtStr, style: "Cinematic Photoreal",
    tierKey: tier.key, tierName: `${tier.name} (${tier.priceStr})`,
    cost: tier.priceUsd, costStr: tier.priceStr,
    enableBgm, enableVoiceOver, enableTts, enableLipsync, voiceGender,
    createdAt: Date.now(), startedAt: null, completedAt: null, publishedAt: null
  };

  studioVideos.unshift(newVid);
  if (typeof saveVideosState === "function") saveVideosState();

  // Switch to the Video Ledger screen
  if (typeof switchTab === "function") switchTab("ledger");
  const mainEl = document.querySelector("main");
  if (mainEl) mainEl.scrollTop = 0;

  renderStudioVideoHistory();
  if (typeof selectLedgerVideo === "function") selectLedgerVideo(newId);

  // Update real-time banner on Ledger screen
  const banner = document.getElementById("ledger-queued-banner");
  const bannerId = document.getElementById("banner-request-id");
  const bannerDetail = document.getElementById("banner-request-detail");
  if (banner) {
    if (bannerId) bannerId.textContent = uniqueJobId;
    if (bannerDetail) bannerDetail.textContent = `Episode ${newId} ("${title}") is now queued. Production Type: ${prodType} • Billed: ${tier.priceStr}. Track live progress below.`;
    banner.classList.remove("hidden");
  }

  // Display explicit modal notification stating request is queued with Request ID
  showStudioModal({
    title: "Request Queued",
    message: `Request is queued with Request ID: ${uniqueJobId}\n\nEpisode: ${newId} — "${title}"\nProduction Type: ${prodType}\nTier: ${tier.name} (${tier.priceStr})`,
    nextStep: "Redirected to Video Ledger to monitor live synthesis."
  });

  if (typeof startLocalVideoProductionJob === "function") {
    startLocalVideoProductionJob(newVid);
  }
}
