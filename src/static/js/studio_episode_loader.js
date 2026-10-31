// CineAI Studio: Episode Loader & Production Controls Auto-Populator
// Populates all Panel 1 and Panel 2 inputs from episode data and enforces View-Only lock on existing episodes.

function populateProductionControlsFromEpisode(rawVid) {
  if (!rawVid) return;

  const epId = rawVid.id || rawVid.episode_id;
  let vid = rawVid;
  if ((!vid.user_inputs || !vid.screenplay) && typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
    const normEpId = String(epId || "").trim().toUpperCase();
    const curFmt = String(rawVid.format || rawVid.format_slug || "").trim().toLowerCase();
    const curProd = String(rawVid.production_name || "").trim().toLowerCase().replace(/\s+/g, "_");
    const curCh = String(rawVid.channelId || rawVid.channel_id || "").trim().toLowerCase();

    const diskRecord = channelArchiveEpisodes.find(x => {
      if (!x) return false;
      const xId = String(x.id || x.episode_id || "").trim().toUpperCase();
      if (xId !== normEpId) return false;
      if (curCh && curCh !== "all") {
        const xCh = String(x.channelId || x.channel_id || "").trim().toLowerCase();
        if (xCh && xCh !== curCh) return false;
      }
      if (curFmt) {
        const xFmt = String(x.format || x.format_slug || "").trim().toLowerCase();
        if (xFmt && !xFmt.includes(curFmt) && !curFmt.includes(xFmt)) return false;
      }
      if (curProd && curProd !== "standalone") {
        const xProd = String(x.production_name || "").trim().toLowerCase().replace(/\s+/g, "_");
        if (xProd && xProd !== curProd) return false;
      }
      return true;
    });
    if (diskRecord) vid = Object.assign({}, diskRecord, rawVid);
  }

  const inputs = vid.user_inputs || {};
  const screenplay = vid.screenplay || vid.script || {};

  // 1. Topic / Prompt Input Box
  const promptInput = document.getElementById("youtube-prompt-input");
  const rawPrompt = inputs.prompt || vid.prompt || vid.story_topic || vid.concept || vid.theme || vid.title || "";
  if (promptInput && rawPrompt) promptInput.value = rawPrompt;

  // 1b. Production Name and Episode Code
  const pInput = document.getElementById("studio-production-name");
  const effProd = vid.production_name || inputs.production_name || vid.series || vid.production || "";
  if (pInput && effProd) pInput.value = effProd;
  const epCodeInput = document.getElementById("studio-episode-code");
  if (epCodeInput && epId) epCodeInput.value = epId;

  // 2. Production Format (documentary, relaxation, etc.) - Must run before genre dropdown
  const effFormatSlug = vid.format_slug || (vid.format && !["16:9", "9:16"].includes(vid.format) ? vid.format : null);
  const effGenre = inputs.genre || vid.genre || vid.videoType || screenplay.genre;
  if (effFormatSlug && typeof selectStudioFormat === "function") {
    selectStudioFormat(effFormatSlug, effGenre);
  }

  // 2b. Genre, Subgenre & Archetype Selectors
  const effSubGenre = inputs.sub_genre || vid.sub_genre || vid.subGenre || screenplay.sub_genre;
  const effArch = inputs.primary_archetype || vid.primary_archetype || vid.primaryArchetype || screenplay.primary_archetype;

  if (effGenre) {
    const gSel = document.getElementById("studio-genre-selector");
    if (gSel) {
      gSel.value = effGenre;
      if (typeof onGenreChange === "function") onGenreChange(effGenre, effSubGenre, effArch);
    }
  }

  if (effSubGenre) {
    const subSel = document.getElementById("studio-subgenre-selector");
    if (subSel) {
      subSel.value = effSubGenre;
      if (typeof onSubGenreChange === "function") onSubGenreChange(effSubGenre);
    }
  }

  if (effArch) {
    const archSel = document.getElementById("studio-archetype-selector");
    if (archSel) {
      archSel.value = effArch;
      if (typeof onArchetypeChange === "function") onArchetypeChange(effArch);
    }
  }

  // 3. Aspect Ratio / Format (16:9 vs 9:16)
  const effAspect = screenplay.aspect_ratio || vid.format || vid.formatType || inputs.aspect_ratio || "16:9";
  const isPortrait = (effAspect === "9:16" || String(effAspect).includes("9:16") || String(effAspect).includes("Short"));
  if (typeof setStudioFormat === "function") setStudioFormat(isPortrait ? "9:16" : "16:9");

  // 4. Production Tier
  const effTier = inputs.tier || vid.tier || vid.tierKey || screenplay.tier || "balanced";
  if (typeof selectProductionTier === "function") {
    const cleanTier = (effTier === "cinematic" || effTier === "4k_master") ? "cinematic" : (effTier === "low_cost" || effTier === "draft" ? "low_cost" : "balanced");
    selectProductionTier(cleanTier);
  }

  // 4b. Weather & Atmosphere
  const effWeather = inputs.weather || inputs.selected_options?.weather?.value || vid.weather || "normal";
  const weatherRadio = document.querySelector(`input[name="studio_weather"][value="${effWeather}"]`);
  if (weatherRadio) {
    weatherRadio.checked = true;
    if (typeof onWeatherChange === "function") onWeatherChange(effWeather);
  }

  // 4c. Production Name & Country
  const effProd = inputs.production_name || vid.production_name || vid.country || vid.destination_entity || screenplay.destination_entity || vid.story?.destination_entity;
  if (effProd) {
    const pInp = document.getElementById("studio-production-name");
    if (pInp) pInp.value = effProd;
    const cSel = document.getElementById("studio-country-selector");
    if (cSel) cSel.value = effProd;
  }

  // 5. Durations & Hours Resolution
  const rawDur = inputs.duration_seconds ?? inputs.duration_secs ?? inputs.requested_duration_seconds ?? vid.duration_seconds ?? vid.durationSeconds;
  const isAuto = (rawDur === -1 || rawDur === "-1" || rawDur === "auto" || rawDur === 0 || rawDur === "0");
  const durSec = isAuto ? -1 : parseFloat(rawDur || screenplay.total_duration_seconds || 120.0);
  const lpHours = parseFloat(inputs.long_play_hours || vid.longPlayHours || vid.long_play_hours || 0);

  // 6. Execution Mode (Test vs Prod)
  let effExecMode = inputs.execution_mode || vid.execution_mode || vid.executionMode;
  if (!effExecMode) effExecMode = (lpHours >= 1.0) ? "prod" : "test";
  if (typeof setExecutionMode === "function") setExecutionMode(effExecMode === "prod" ? "prod" : "test", true);

  // 7. Pipeline Strategy (Auto vs Manual)
  const effStrategy = inputs.pipeline_strategy || vid.pipelineStrategy || vid.pipeline_strategy || "manual";
  if (typeof setPipelineExecutionMode === "function") setPipelineExecutionMode(effStrategy === "auto" ? "auto" : "manual", true);

  // 8. Shot Count
  const isDocOrTour = (typeof isTravelOrSkylineChannel === "function" && isTravelOrSkylineChannel()) ||
                      (vid.genre && (vid.genre === "documentary" || vid.genre.startsWith("travel"))) ||
                      (vid.primary_archetype && vid.primary_archetype.includes("tour"));
  const shotCount = (!isDocOrTour && (inputs.num_shots > 0 ? inputs.num_shots : (vid.numShots > 0 ? vid.numShots : -1))) || -1;
  const shotVal = (isDocOrTour || shotCount === -1 || inputs.num_shots === -1 || vid.num_shots === -1 || vid.numShots === -1) ? "-1" : String(shotCount);
  const testShotsSel = document.getElementById("studio-test-shots"), prodShotsSel = document.getElementById("studio-prod-shots");
  if (testShotsSel) { testShotsSel.value = Array.from(testShotsSel.options).some(o => o.value === shotVal) ? shotVal : "-1"; setTestShots?.(testShotsSel.value); }
  if (prodShotsSel) prodShotsSel.value = Array.from(prodShotsSel.options).some(o => o.value === shotVal) ? shotVal : "-1";

  // 9. Duration & Stretch Hours Selectors (Test & Prod)
  let targetStretchVal = "0";
  const mOptVal = `${Math.round(durSec / 60)}m`;
  if (durSec === -1 || isAuto) targetStretchVal = "-1";
  else if (lpHours >= 1.0) targetStretchVal = String(lpHours);
  else if (durSec % 60 === 0 && durSec >= 60 && durSec <= 900 && document.querySelector(`#studio-stretch-hours option[value="${mOptVal}"]`)) {
    targetStretchVal = mOptVal;
  } else if (durSec >= 110 && durSec <= 130) targetStretchVal = "0.033";
  else if (durSec >= 50 && durSec <= 70) targetStretchVal = "0.0167";
  else if (durSec >= 25 && durSec <= 35) targetStretchVal = "0.0083";
  else if (durSec > 0) {
    targetStretchVal = "custom";
    const customInput = document.getElementById("studio-custom-minutes-input");
    if (customInput) customInput.value = String(Math.round((durSec / 60) * 10) / 10);
    document.getElementById("studio-custom-duration-container")?.classList.remove("hidden");
  }

  const testStretchSel = document.getElementById("studio-test-stretch");
  if (testStretchSel) {
    testStretchSel.value = targetStretchVal;
    if (typeof setBroadcastHours === "function") setBroadcastHours(targetStretchVal);
  }
  const prodStretchSel = document.getElementById("studio-stretch-hours");
  if (prodStretchSel) prodStretchSel.value = targetStretchVal;

  vid.imageModel = inputs.image_model || vid.imageModel || "zimage";
  vid.image_model = vid.imageModel;

  // 10. Audio Stems & Modality Toggles
  const setChk = (id, val) => { const el = document.getElementById(id); if (el) el.checked = Boolean(val); };
  setChk("studio-toggle-bgm", inputs.enable_bgm !== undefined ? inputs.enable_bgm : (vid.enableBgm !== undefined ? vid.enableBgm : !inputs.no_bgm));
  setChk("studio-toggle-voice-over", inputs.enable_voiceover !== undefined ? inputs.enable_voiceover : (vid.enableVoiceOver !== undefined ? vid.enableVoiceOver : Boolean(vid.narration_path || vid.narration_audio)));
  setChk("studio-toggle-tts", inputs.enable_tts !== undefined ? inputs.enable_tts : (vid.enableTts !== undefined ? vid.enableTts : false));
  const hasDual = Boolean(inputs.dual_editions || vid.dual_editions || vid.dualEditions || (vid.editions && vid.editions.some(e => e.edition_id === "master_narration")) || (vid.all_editions && vid.all_editions.some(e => e.edition_id === "master_narration")) || vid.narration_path || vid.narration_audio);
  setChk("studio-toggle-dual-editions", hasDual);
  setChk("studio-toggle-fallback", inputs.allow_fallback !== undefined ? inputs.allow_fallback : (vid.allowFallback !== undefined ? vid.allowFallback : false));

  // 11. Frame Rate (FPS)
  const fpsSel = document.getElementById("studio-fps");
  const effFps = screenplay.recommended_fps || vid.recommended_fps || vid.fps || inputs.fps || 24;
  if (fpsSel && effFps) fpsSel.value = String(effFps);

  // 12. Recalculate Live Cost Estimate
  if (typeof calculateLiveCostEstimate === "function") calculateLiveCostEstimate();

  // 13. Enforce View-Only State to prevent accidental overwrite of produced episode
  setProductionControlsViewOnly(true, epId);
}

function setProductionControlsViewOnly(isViewOnly, episodeId) {
  const panel = document.getElementById("studio-production-controls-panel");
  const banner = document.getElementById("studio-view-only-banner");
  const bannerText = document.getElementById("studio-view-only-text");
  const btnProduce = document.getElementById("btn-guided-generate");
  const btnProduceText = document.getElementById("btn-produce-text");
  const btnReset = document.getElementById("btn-studio-reset");
  const btnStop = document.getElementById("btn-studio-stop");

  if (banner) {
    banner.classList.toggle("hidden", !isViewOnly);
    if (isViewOnly && bannerText) bannerText.textContent = `Episode ${episodeId || ''} Selected (Controls Locked)`;
  }

  // Configure Action Buttons in Production Controls
  [btnReset, btnStop, btnProduce].forEach(btn => {
    if (btn) {
      btn.disabled = isViewOnly;
      btn.classList.toggle("opacity-40", isViewOnly);
      btn.classList.toggle("cursor-not-allowed", isViewOnly);
      btn.classList.toggle("pointer-events-none", isViewOnly);
    }
  });
  if (btnProduce) {
    btnProduce.title = isViewOnly ? "Controls locked while viewing an episode. Click New Video to create new content." : "Produce / Test Video";
    if (btnProduceText) {
      btnProduceText.textContent = isViewOnly ? "Controls Locked" : ((typeof activeExecutionMode !== "undefined" && activeExecutionMode === "test") ? `Run Test (${typeof activeShotsCount !== "undefined" ? activeShotsCount : 1} Shots)` : "Produce Master Video");
    }
  }

  // Disable/Enable all panel input and dropdown fields
  const controlIds = [
    "studio-test-shots", "studio-test-stretch", "studio-prod-shots", "studio-stretch-hours",
    "studio-custom-minutes-input", "studio-toggle-bgm", "studio-toggle-voice-over",
    "studio-toggle-tts", "studio-toggle-dual-editions", "studio-toggle-fallback", "studio-fps",
    "studio-profile-selector", "studio-tts-model", "btn-studio-save-pref", "btn-studio-reset-pref"
  ];
  controlIds.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.disabled = isViewOnly;
      el.classList.toggle("opacity-50", isViewOnly);
      el.classList.toggle("cursor-not-allowed", isViewOnly);
    }
  });

  // Segmented mode, strategy, and tier buttons
  ["btn-exec-test", "btn-exec-prod", "btn-pipe-auto", "btn-pipe-manual", "tier-card-low_cost", "tier-card-balanced", "tier-card-cinematic"].forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.style.pointerEvents = isViewOnly ? "none" : "auto";
      el.style.opacity = isViewOnly ? "0.45" : "1.0";
      el.classList.toggle("cursor-not-allowed", isViewOnly);
    }
  });

  // Panel 1 Inputs (Read-only while viewing existing episode)
  const promptInput = document.getElementById("youtube-prompt-input");
  if (promptInput) {
    promptInput.readOnly = isViewOnly;
    promptInput.classList.toggle("bg-[var(--card-subtle)]", isViewOnly);
    promptInput.classList.toggle("cursor-not-allowed", isViewOnly);
  }

  ["studio-genre-selector", "studio-subgenre-selector", "studio-archetype-selector"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.disabled = isViewOnly;
  });
}

async function unlockForNewProduction() {
  currentActiveInspectorEpisode = null;
  setProductionControlsViewOnly(false, null);
  const pInput = document.getElementById("studio-production-name");
  if (pInput) pInput.value = "";
  const epCode = document.getElementById("studio-episode-code");
  const chId = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel && selectedStudioChannel !== "all") ? selectedStudioChannel : "euro_discovery";
  const fmt = document.getElementById("studio-active-format-val")?.value || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "documentary");
  const nextId = (typeof nextEpisodeIdForChannel === "function") ? nextEpisodeIdForChannel(chId, fmt, "") : "ep-001";
  if (epCode) epCode.value = nextId;
  if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  if (typeof switchCreationTab === "function" && typeof activeCreationTab !== "undefined" && activeCreationTab !== "new") switchCreationTab("new");
}

// Hook into StudioBus episode selection event
if (typeof window !== "undefined") {
  if (window.StudioBus) {
    window.StudioBus.on("episode:selected", ep => { populateProductionControlsFromEpisode(ep); });
  } else {
    window.addEventListener("DOMContentLoaded", () => {
      if (window.StudioBus) {
        window.StudioBus.on("episode:selected", ep => { populateProductionControlsFromEpisode(ep); });
      }
    });
  }
}
