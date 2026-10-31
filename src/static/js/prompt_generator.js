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
  const isDoc = (typeof activeStudioFormat !== "undefined" && activeStudioFormat === "documentary");
  setC("studio-toggle-bgm", cfg.bgm); setC("studio-toggle-voice-over", isDoc ? cfg.voice : false); setV("studio-fps", cfg.fps || "24");
  syncCameraAngleVisibility(nicheKey);
}



function clearStudioInputs() {
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  if (pInput) { pInput.value = ""; pInput.focus(); flashPromptInput(pInput); }
  if (uInput) uInput.value = "";
  const prodInput = document.getElementById("studio-production-name");
  if (prodInput) prodInput.value = "";
  const epCode = document.getElementById("studio-episode-code");
  const chId = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel && selectedStudioChannel !== "all") ? selectedStudioChannel : null;
  const fmt = document.getElementById("studio-active-format-val")?.value || "documentary";
  const nextId = (typeof nextEpisodeIdForChannel === "function") ? nextEpisodeIdForChannel(chId, fmt, "") : "EP-001";
  if (epCode) epCode.value = nextId;
  if (typeof currentActiveInspectorEpisode !== "undefined") currentActiveInspectorEpisode = null;
  document.querySelectorAll("input[name='niche_theme_radio']").forEach(r => r.checked = false);
  const setV = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
  const setC = (id, val) => { const el = document.getElementById(id); if (el) el.checked = val; };
  setV("studio-duration", "10"); setC("studio-toggle-bgm", true); setC("studio-toggle-voice-over", false);
  setC("studio-toggle-tts", false); setC("studio-toggle-lipsync", false);
  setV("studio-voice-gender", "female"); setV("studio-language", "en");
  clearTemplateCardHighlights(); selectProductionTier("low_cost");
  if (typeof setProductionControlsViewOnly === "function") setProductionControlsViewOnly(false, null);
  if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
}

function deriveTitleFromInput(text, mode) {
  if (!text) return mode === "youtube" ? "Adaptive Remake" : "Scenic Nature Sanctuary";
  const firstLine = text.split("\n").map(l => l.trim()).find(l => l.length > 0) || text;
  const clean = firstLine.replace(/^(title|theme|idea|script|scene\s*\d*)\s*[:\-]\s*/i, "").trim();
  return clean.length > 40 ? clean.slice(0, 38) + "..." : clean;
}

function quickTestProduceFromPrompt() {
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode && currentActiveInspectorEpisode.status !== "processing") {
    if (typeof unlockForNewProduction === "function") unlockForNewProduction();
  }
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
  const effective = (typeof getEffectiveProductionDuration === "function")
    ? getEffectiveProductionDuration()
    : { durSec: 120, lpHours: 0.0 };
  const durationSec = effective.durSec;
  const longPlayHours = effective.lpHours;
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
  const isTravelOrSkyline = (chId === "skylinediariesindia4k" || selGenreVal.startsWith("travel") || (typeof currentChannel !== "undefined" && currentChannel?.genre?.startsWith("travel")));
  const numShots = isTravelOrSkyline
    ? -1
    : (isTestMode ? (typeof activeShotsCount !== "undefined" ? activeShotsCount : 1) : parseInt(document.getElementById("studio-prod-shots")?.value || "1", 10));
  const genresDict = (typeof ALL_STUDIO_GENRES !== "undefined") ? ALL_STUDIO_GENRES : {};
  const subMap = (typeof STUDIO_SUBOPTIONS_MAP !== "undefined") ? STUDIO_SUBOPTIONS_MAP : {};
  const archMap = (typeof STUDIO_ARCHETYPES_MAP !== "undefined") ? STUDIO_ARCHETYPES_MAP : {};

  const selGenreLabel = genreEl?.selectedOptions?.[0]?.textContent?.trim() || genresDict[selGenreVal] || selGenreVal;
  const selSubgenreVal = subgenreEl?.value || null;
  const selSubgenreLabel = subgenreEl?.selectedOptions?.[0]?.textContent?.trim() || (subMap[selGenreVal]?.find(x => x.val === selSubgenreVal)?.label) || "";
  const selArchVal = archEl?.value || null;
  const selArchLabel = archEl?.selectedOptions?.[0]?.textContent?.trim() || (archMap[selGenreVal]?.find(x => x.val === selArchVal)?.label) || "";
  const dualEditionsChecked = Boolean(document.getElementById("studio-toggle-dual-editions")?.checked);

  let selProdName = document.getElementById("studio-production-name")?.value?.trim() || null;
  const seriesSelect = document.getElementById("studio-existing-series-select");
  if (!selProdName && seriesSelect?.value) {
    const selOpt = seriesSelect.selectedOptions?.[0];
    const optName = selOpt ? (selOpt.getAttribute("data-name") || selOpt.textContent.split("(")[0].trim()) : seriesSelect.value;
    if (optName && optName !== "standalone") selProdName = optName;
  }
  const isGeoNationsMode = selGenreVal === "doc/nations" || selGenreVal === "nations" || (selSubgenreVal && selSubgenreVal.includes("nations")) || ["cities", "countries", "nations", "city", "nation", "country_dossier", "country_profile", "country_overview", "country_encyclopedia", "tour_itinerary", "top_10_cities", "top_places_to_visit", "top_50_places", "top_cities", "supermarkets_and_grocery_culture", "supermarkets"].includes(selArchVal);
  if (!selProdName || selProdName.toLowerCase() === "standalone") {
    if (isGeoNationsMode) {
      selProdName = null;
    } else {
      selProdName = selSubgenreLabel || selGenreLabel || (typeof currentChannel !== "undefined" && currentChannel?.name ? currentChannel.name : "Standalone");
    }
  }
  const selFormatVal = document.getElementById("studio-active-format-val")?.value || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "documentary");
  const selAspect = document.getElementById("studio-selected-format")?.value || "16:9";

  const epInputVal = document.getElementById("studio-episode-code")?.value?.trim();
  const allRecords = [
    ...(Array.isArray(studioVideos) ? studioVideos : []),
    ...(typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes) ? channelArchiveEpisodes : [])
  ];
  let newId = (epInputVal && /^EP-\d+$/i.test(epInputVal)) ? epInputVal.toUpperCase() : null;
  const isExisting = newId && allRecords.some(r => {
    const rId = String(r.id || r.episode_id || "").trim().toUpperCase();
    const rCh = String(r.channelId || r.channel_id || "").trim().toLowerCase();
    const rProd = String(r.production_name || "standalone").trim().toLowerCase().replace(/\s+/g, "_");
    const myProd = String(selProdName || "standalone").trim().toLowerCase().replace(/\s+/g, "_");
    return rId === newId && (!chId || rCh === chId.toLowerCase()) && rProd === myProd;
  });
  if (!newId || isExisting) {
    newId = nextEpisodeIdForChannel(chId, selFormatVal, selProdName);
  }
  const epInputEl = document.getElementById("studio-episode-code");
  if (epInputEl) epInputEl.value = newId;
  const uniqueJobId = `job_${newId.toLowerCase()}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  const weatherMap = {
    normal: "☀️ Normal",
    rain: "🌧️ Rain",
    snow: "❄️ Snow",
    fog: "🌫️ Mist/Fog",
    sunset: "🌅 Sunset",
    night: "🌌 Starlit"
  };
  const selWeather = document.querySelector('input[name="studio_weather"]:checked')?.value || "normal";
  const selWeatherLabel = weatherMap[selWeather] || "☀️ Normal";

  const newVid = {
    id: newId, episode_id: newId, jobId: uniqueJobId, title, concept, story_topic: concept,
    channel_id: chId, channelId: chId, genre: selGenreVal,
    videoType: selGenreVal, formatType: fmtType, styleType: styType, productionType: prodType,
    production_name: selProdName, format_slug: selFormatVal, format: selFormatVal, aspect_ratio: selAspect,
    sub_genre: selSubgenreVal, subGenre: selSubgenreVal,
    primary_archetype: selArchVal, primaryArchetype: selArchVal,
    genre_label: selGenreLabel, genreLabel: selGenreLabel,
    sub_genre_label: selSubgenreLabel, subGenreLabel: selSubgenreLabel,
    primary_archetype_label: selArchLabel, primaryArchetypeLabel: selArchLabel,
    weather: selWeather, weather_label: selWeatherLabel,
    user_inputs: {
      prompt: concept,
      production_name: selProdName,
      genre: selGenreVal,
      sub_genre: selSubgenreVal,
      primary_archetype: selArchVal,
      weather: selWeather,
      duration_seconds: durationSec,
      duration_secs: durationSec,
      requested_duration_seconds: durationSec,
      selected_options: {
        genre: { value: selGenreVal, label: selGenreLabel },
        sub_genre: { value: selSubgenreVal || "", label: selSubgenreLabel },
        primary_archetype: { value: selArchVal || "", label: selArchLabel },
        weather: { value: selWeather, label: selWeatherLabel }
      },
      execution_mode: isTestMode ? "test" : "prod",
      pipeline_strategy: typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "manual"
    },
    dual_editions: dualEditionsChecked,
    status: "queued", youtubeStatus: "unpublished", youtubeChannel: null, youtubeUrl: null,
    youtubeReferenceUrl: ytUrl, videoUrl: "/static/videos/preview_master.mp4",
    keyframes: [], motion_clips: [], audio_stems: [], editions: [], long_play_editions: [], currentStage: 1, progress: 10,
    durationSeconds: durationSec, duration_seconds: durationSec, duration_secs: durationSec,
    duration: (durationSec <= 0 || durationSec === -1) ? "Auto" : (longPlayHours > 0 ? `${longPlayHours}h` : `${durationSec}s`),
    numShots, num_shots: numShots,
    longPlayHours: longPlayHours, long_play_hours: longPlayHours, executionMode: isTestMode ? "test" : "prod", execution_mode: isTestMode ? "test" : "prod",
    language: langVal === "te" ? "Telugu (te)" : (langVal === "hi" ? "Hindi (hi)" : "English (en)"), langCode: langVal, display_format: fmtStr, style: "Cinematic Photoreal",
    tierKey: tier.key, tierName: `${tier.name} (${tier.priceStr})`, cost: effCost, cost_usd: effCost, costStr: `$${effCost.toFixed(2)} USD`,
    theme: themeVal, idea: ideaVal, script: scriptVal, enableBgm: getChk("studio-toggle-bgm"), enableVoiceOver: getChk("studio-toggle-voice-over"),
    enableTts: document.getElementById("studio-toggle-tts")?.checked || false,
    enableLipsync: document.getElementById("studio-toggle-lipsync")?.checked || false,
    imageModel: "zimage", image_model: "zimage",
    allowFallback: document.getElementById("studio-toggle-fallback")?.checked || false,
    motionModel: isTravelOrSkyline ? "ken_burns" : "wan_4k", voiceGender: getVal("studio-voice-gender", "female"),
    pipelineStrategy: typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "manual",
    pipeline_strategy: typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "manual",
    createdAt: Date.now(), startedAt: null, completedAt: null, publishedAt: null
  };

  studioVideos.unshift(newVid);
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof setArchiveFormatFilter === "function") setArchiveFormatFilter(selFormatVal || "all");
  currentActiveInspectorEpisode = newVid;
  if (typeof setProductionControlsViewOnly === "function") setProductionControlsViewOnly(false, newVid.id);
  if (typeof switchCreationTab === "function") switchCreationTab("archive");
  if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(newVid);
  if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  if (typeof showCreationProgressModal === "function") {
    showCreationProgressModal({
      episodeId: newVid.id,
      title: "Generating Sovereign 22-Chapter Story Script",
      subtitle: "Gemini 2.5 Flash evaluating destination trends and sovereign history...",
    });
  }
  if (typeof startStudioLiveStageProgress === "function") startStudioLiveStageProgress(newVid, newVid.pipelineStrategy);
}

document.addEventListener("DOMContentLoaded", () => {
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  [pInput, uInput].forEach(el => el?.addEventListener("input", clearTemplateCardHighlights));
  setCreationMode("theme", false);
});
