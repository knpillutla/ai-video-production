// CineAI Studio: Prompt Hero, Dynamic Niche Radio Groups & Tier Controller
let currentCreationMode = "theme";

function selectProductionTier(tierKey) {
  currentTier = tierKey;
  const tierLabels = {
    low_cost: "Draft ($0.02)",
    balanced: "Balanced ($0.14)",
    cinematic: "4K Master ($0.45)"
  };

  ["low_cost", "balanced", "cinematic"].forEach(t => {
    const card = document.getElementById("tier-card-" + t), radio = document.getElementById("tier-radio-" + t);
    if (!card) return;
    const isSel = (t === tierKey);
    card.classList.toggle("active", isSel);
    if (radio) radio.checked = isSel;
  });

  const badge = document.getElementById("tier-active-badge");
  if (badge) {
    badge.textContent = tierLabels[tierKey] || "4K Master ($0.45)";
  }

  const sel = document.getElementById("studio-tier-select"), pill = document.getElementById("sidebar-tier-price-pill");
  const tier = PRODUCTION_TIERS[tierKey] || PRODUCTION_TIERS.cinematic;
  if (sel) sel.value = tierKey;
  if (pill) pill.textContent = tier.priceStr;
}

function syncCameraAngleVisibility(key) {
  const k = (key || "").toLowerCase();
  const isRelax = k.startsWith("relax_") || ["earth_serenade", "rain_retreat", "healing_relaxation", "zen_studio", "cozy_ambiance", "study_focus_cafe", "default_channel"].includes(k) || k.includes("relax") || k.includes("serenade") || k.includes("retreat");
  const motionWrap = document.getElementById("studio-camera-motion-wrap");
  const motionSelect = document.getElementById("studio-camera-motion");
  const fpsSelect = document.getElementById("studio-fps");
  
  if (motionSelect && (!motionSelect.value || isRelax)) {
    motionSelect.value = "locked_tripod";
  }

  if (isRelax) {
    if (motionWrap) motionWrap.classList.add("hidden");
    if (fpsSelect) fpsSelect.classList.add("col-span-2");
  } else {
    if (motionWrap) motionWrap.classList.remove("hidden");
    if (fpsSelect) fpsSelect.classList.remove("col-span-2");
  }
}

function selectNicheRadio(nicheKey) {
  const cfg = (typeof NICHE_RADIO_CONFIGS !== "undefined" ? NICHE_RADIO_CONFIGS : {})[nicheKey];
  if (!cfg) return;
  const setC = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };
  const setV = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
  setC("studio-toggle-bgm", cfg.bgm); setC("studio-toggle-voice-over", cfg.voice); setV("studio-fps", cfg.fps || "24");
  syncCameraAngleVisibility(nicheKey);
}

const MODE_CONFIG = {
  theme: {
    labelHtml: '<i class="fa-solid fa-compass text-[var(--text-muted)] text-xs"></i> <span>Theme / Topic Description (Optional):</span>',
    sublabel: "World Cities, Nature, Mountains, Oceans & Architecture",
    ph: "Optional example: A quiet rainforest stream beneath an old-growth canopy...",
    hint: "Theme active • World Cities, Villages, Mountains, Oceans & Architecture"
  },
  idea: {
    labelHtml: '<i class="fa-solid fa-lightbulb text-[var(--text-muted)] text-xs"></i> <span>Story Idea / Concept (Optional):</span>',
    sublabel: "Character arcs, satirical situations, narrative premise",
    ph: "Optional: Describe story concept, characters, comedic angle, or leave empty...",
    hint: "Idea active • Narrative concepts, characters & comedy"
  },
  script: {
    labelHtml: '<i class="fa-solid fa-scroll text-[var(--text-muted)] text-xs"></i> <span>Script / Screenplay (Optional):</span>',
    sublabel: "Full scene screenplay, voiceover narration, dialogue beats",
    ph: "Optional: Paste screenplay, dialogue lines, or leave empty...",
    hint: "Script active • Full screenplay, scene beats or dialogue stems"
  },
  youtube: {
    labelHtml: '<i class="fa-brands fa-youtube text-red-500 text-xs"></i> <span>Reference Adaptation Styling (Optional):</span>',
    sublabel: "Styling directions, camera motion, cinematic treatment",
    ph: "Optional: Enter styling directions to apply from reference video...",
    hint: "YouTube Reference active • Paste video link & prompt to apply reference styling"
  }
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
    <div id="creative-card-${t.id}" onclick="applyTemplate('${mode}', ${idx})" class="p-3 bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] rounded-xl cursor-pointer transition space-y-1 group active:scale-95 shadow-sm">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold px-2 py-0.5 rounded bg-[var(--card-subtle)] text-[var(--text)] border border-[var(--border)]">${t.badge}</span>
        <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text)]"></i>
      </div>
      <div class="font-bold text-[var(--text)] text-xs">${t.title}</div>
      <div class="text-xs text-[var(--text-muted)] leading-tight">${t.desc}</div>
    </div>`).join("");
}

function applyTemplate(mode, idxOrObj) {
  const list = TEMPLATES_BY_MODE[mode] || TEMPLATES_BY_MODE.theme;
  const t = typeof idxOrObj === "number" ? list[idxOrObj] : idxOrObj;
  if (!t) return;
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  if (mode === "youtube") { if (uInput) { uInput.value = t.url || ""; flashPromptInput(uInput); } } else if (uInput) { uInput.value = ""; }
  if (pInput) { pInput.value = t.prompt; flashPromptInput(pInput); }
  clearTemplateCardHighlights();
  document.getElementById("creative-card-" + t.id)?.classList.add("ring-2", "ring-[var(--accent)]");
}

function setCreationMode(mode, autoPopulate = false) {
  currentCreationMode = mode;
  ["theme", "idea", "script", "youtube"].forEach(m => {
    const btn = document.getElementById("mode-pill-" + m);
    if (btn) btn.classList.toggle("active", m === mode);
  });

  const textarea = document.getElementById("youtube-prompt-input"), urlInput = document.getElementById("youtube-url-input");
  const urlContainer = document.getElementById("youtube-url-container"), genreShelf = document.getElementById("theme-genre-shelf");
  const hint = document.getElementById("creation-mode-hint"), labelEl = document.getElementById("prompt-input-label"), sublabelEl = document.getElementById("prompt-input-sublabel");
  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.theme;

  if (labelEl && cfg.labelHtml) labelEl.innerHTML = cfg.labelHtml;
  if (sublabelEl && cfg.sublabel) sublabelEl.textContent = cfg.sublabel;
  if (textarea) { textarea.placeholder = cfg.ph; if (hint) hint.textContent = cfg.hint; }
  if (genreShelf) genreShelf.classList.toggle("hidden", mode !== "theme");
  if (urlContainer) {
    urlContainer.classList.toggle("hidden", mode !== "youtube");
    if (mode !== "youtube" && urlInput) urlInput.value = "";
  }
  renderTemplatesForMode(mode);
}

function flashPromptInput(el) {
  if (!el) return;
  el.classList.add("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40");
  setTimeout(() => el.classList.remove("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40"), 1000);
}

function clearStudioInputs() {
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  if (pInput) { pInput.value = ""; pInput.focus(); flashPromptInput(pInput); }
  if (uInput) uInput.value = "";
  document.querySelectorAll("input[name='niche_theme_radio']").forEach(r => r.checked = false);
  const setV = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
  const setC = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };
  setV("studio-duration", "10"); setC("studio-toggle-bgm", true); setC("studio-toggle-voice-over", false);
  setC("studio-toggle-tts", false); setC("studio-toggle-lipsync", false);
  setV("studio-voice-gender", "female"); setV("studio-language", "en");
  clearTemplateCardHighlights(); selectProductionTier("low_cost");
}

function deriveTitleFromInput(text, mode) {
  if (!text) return mode === "youtube" ? "Adaptive Remake" : "Scenic Nature Sanctuary";
  const firstLine = text.split("\n").map(l => l.trim()).find(l => l.length > 0) || text;
  const clean = firstLine.replace(/^(title|theme|idea|script|scene\s*\d*)\s*[:\-]\s*/i, "").trim();
  return clean.length > 40 ? clean.slice(0, 38) + "..." : clean;
}

function quickTestProduceFromPrompt() {
  const promptInput = document.getElementById("youtube-prompt-input"), urlInput = document.getElementById("youtube-url-input");
  const userPrompt = (promptInput?.value || "").trim();
  const userUrl = (urlInput?.value || "").trim();

  const selChan = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel && selectedStudioChannel !== "all")
    ? selectedStudioChannel
    : ((typeof currentActiveChannelId !== "undefined" && currentActiveChannelId && currentActiveChannelId !== "all") ? currentActiveChannelId : null);

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
  const isTestMode = (typeof activeExecutionMode !== "undefined" && activeExecutionMode === "test");
  const effCost = isTestMode ? 0.02 : tier.priceUsd;
  currentUser.balance_usd = Math.max(0, currentUser.balance_usd - effCost);
  saveUserState();

  const getChk = id => { const el = document.getElementById(id); return el ? el.checked : true; };
  const getVal = (id, fallback) => { const el = document.getElementById(id); return el?.value || fallback; };
  const numShots = isTestMode
    ? (typeof activeShotsCount !== "undefined" ? activeShotsCount : 1)
    : parseInt(document.getElementById("studio-prod-shots")?.value || "1", 10);
  const effective = (typeof getEffectiveProductionDuration === "function")
    ? getEffectiveProductionDuration()
    : { durSec: isTestMode ? (activeTestDuration || 5) : 90, lpHours: isTestMode ? (activeBroadcastHours || 0) : 3.0 };
  const durationSec = isTestMode ? (activeTestDuration || 5) : effective.durSec;
  const longPlayHours = isTestMode ? (activeBroadcastHours || 0) : effective.lpHours;
  const langVal = getVal("studio-language", "en");

  if (!selChan) {
    alert("⚠️ Action Required: You must create and select a YouTube channel before producing or testing a video.\n\nPlease click '+ Create Channel' in the top bar to set up your channel handle and isolated storage.");
    if (typeof openChannelInspectorModal === "function") openChannelInspectorModal();
    else if (typeof switchTab === "function") switchTab("channels");
    return;
  }

  const chId = selChan;
  const genreEl = document.getElementById("studio-genre-selector");
  const subgenreEl = document.getElementById("studio-subgenre-selector");
  const archEl = document.getElementById("studio-archetype-selector");
  const chGenre = (chId === "silent_hearth") ? "Fireplace & ASMR" : (chId === "earth_serenade" ? "4K Nature Ambiance" : (chId === "cineai_docs" ? "24fps BBC Nature Doc" : (chId === "telugu_comedy" ? "Comedy Satire Shorts" : vType)));
  const selGenreVal = genreEl?.value || chGenre;
  const selGenreLabel = genreEl?.selectedOptions?.[0]?.textContent?.trim() || "";
  const selSubgenreVal = subgenreEl?.value || null;
  const selSubgenreLabel = subgenreEl?.selectedOptions?.[0]?.textContent?.trim() || "";
  const selArchVal = archEl?.value || null;
  const selArchLabel = archEl?.selectedOptions?.[0]?.textContent?.trim() || "";
  const dualEditionsChecked = Boolean(document.getElementById("studio-toggle-dual-editions")?.checked);

  const newId = nextEpisodeIdForChannel(chId);
  const uniqueJobId = `job_${newId.toLowerCase()}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  const newVid = {
    id: newId, episode_id: newId, jobId: uniqueJobId, title, concept, story_topic: concept,
    channel_id: chId, channelId: chId, genre: selGenreVal,
    videoType: selGenreVal, formatType: fmtType, styleType: styType, productionType: prodType,
    sub_genre: selSubgenreVal, subGenre: selSubgenreVal,
    primary_archetype: selArchVal, primaryArchetype: selArchVal,
    genre_label: selGenreLabel, genreLabel: selGenreLabel,
    sub_genre_label: selSubgenreLabel, subGenreLabel: selSubgenreLabel,
    primary_archetype_label: selArchLabel, primaryArchetypeLabel: selArchLabel,
    dual_editions: dualEditionsChecked,
    status: "queued", youtubeStatus: "unpublished", youtubeChannel: null, youtubeUrl: null,
    youtubeReferenceUrl: ytUrl, videoUrl: "/static/videos/preview_master.mp4",
    durationSeconds: durationSec, duration: longPlayHours > 0 ? `${longPlayHours}h` : `${durationSec}s`, numShots, num_shots: numShots,
    longPlayHours: longPlayHours, long_play_hours: longPlayHours, executionMode: isTestMode ? "test" : "prod",
    language: langVal === "te" ? "Telugu (te)" : (langVal === "hi" ? "Hindi (hi)" : "English (en)"),
    langCode: langVal, format: fmtStr, style: "Cinematic Photoreal",
    tierKey: tier.key, tierName: `${tier.name} (${tier.priceStr})`,
    cost: effCost, cost_usd: effCost, costStr: `$${effCost.toFixed(2)} USD`,
    theme: themeVal, idea: ideaVal, script: scriptVal,
    enableBgm: getChk("studio-toggle-bgm"), enableVoiceOver: getChk("studio-toggle-voice-over"),
    enableTts: document.getElementById("studio-toggle-tts")?.checked || false,
    enableLipsync: document.getElementById("studio-toggle-lipsync")?.checked || false,
    allowFallback: document.getElementById("studio-toggle-fallback")?.checked || false,
    motionModel: isTestMode ? "wan" : "auto",
    voiceGender: getVal("studio-voice-gender", "female"),
    pipelineStrategy: typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "auto",
    createdAt: Date.now(), startedAt: null, completedAt: null, publishedAt: null
  };

  studioVideos.unshift(newVid);
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof switchCreationTab === "function") switchCreationTab("archive");
  if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
  if (typeof startStudioLiveStageProgress === "function") startStudioLiveStageProgress(newVid, newVid.pipelineStrategy);
}

document.addEventListener("DOMContentLoaded", () => {
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  if (pInput) pInput.addEventListener("input", clearTemplateCardHighlights);
  if (uInput) uInput.addEventListener("input", clearTemplateCardHighlights);
  setCreationMode("theme", false);
});
