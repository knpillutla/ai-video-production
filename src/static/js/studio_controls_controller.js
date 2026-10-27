// CineAI Studio: Panel 2 Controls & Engine Controller (Execution Mode, Cadence & Cost Math)
let activeExecutionMode = "test"; // "test" | "prod"
let activePipelineStrategy = "manual"; // "auto" | "manual"
let activeTestDuration = 60, activeShotsCount = -1, activeBroadcastHours = 0.0167, currentNicheGroup = "relaxation";

function persistCurrentEpisodeInputs(patch) {
  const ep = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!ep) return;
  const epId = ep.id || ep.episode_id;
  if (!epId) return;
  Object.assign(ep, patch);
  if (patch.pipeline_strategy) { ep.pipelineStrategy = patch.pipeline_strategy; ep.pipeline_strategy = patch.pipeline_strategy; }
  if (patch.execution_mode) { ep.executionMode = patch.execution_mode; ep.execution_mode = patch.execution_mode; }
  if (ep.user_inputs) Object.assign(ep.user_inputs, patch);
  const ch = ep.channelId || ep.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : "");
  const fmt = ep.format || ep.format_slug || "";
  const prod = ep.production_name || "";
  const user = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  fetch(`/api/production/episodes/${encodeURIComponent(epId)}/update-inputs?channel_id=${encodeURIComponent(ch)}&format=${encodeURIComponent(fmt)}&production_name=${encodeURIComponent(prod)}&user_id=${encodeURIComponent(user)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch)
  }).catch(e => console.warn("Failed to persist episode inputs:", e));
}

function setExecutionMode(mode, skipPersist = false) {
  activeExecutionMode = mode;
  document.getElementById("btn-exec-test")?.classList.toggle("active", mode === "test");
  document.getElementById("btn-exec-prod")?.classList.toggle("active", mode === "prod");
  document.getElementById("exec-options-test")?.classList.toggle("hidden", mode !== "test");
  document.getElementById("exec-options-prod")?.classList.toggle("hidden", mode !== "prod");

  const shotsLabel = activeShotsCount === -1 ? "Auto" : `${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''}`;
  const btnProduceText = document.getElementById("btn-produce-text");
  if (btnProduceText) {
    btnProduceText.textContent = mode === "test"
      ? (activePipelineStrategy === "manual" ? `Run Test (${shotsLabel})` : `Run Draft (${shotsLabel})`)
      : (activePipelineStrategy === "manual" ? "Produce Video (Gate)" : "Produce Master Video");
  }
  const isCust = (mode === "test" ? document.getElementById("studio-test-stretch") : document.getElementById("studio-stretch-hours"))?.value === "custom";
  document.getElementById("studio-custom-duration-container")?.classList.toggle("hidden", !isCust);
  syncTravelShotUI();
  calculateLiveCostEstimate();

  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    currentActiveInspectorEpisode.executionMode = mode;
    currentActiveInspectorEpisode.execution_mode = mode;
    if (!currentActiveInspectorEpisode.imageModel) {
      currentActiveInspectorEpisode.imageModel = "zimage";
      currentActiveInspectorEpisode.image_model = "zimage";
    }
  }
  if (!skipPersist) persistCurrentEpisodeInputs({ execution_mode: mode });
}

function setPipelineExecutionMode(strat, skipPersist = false) {
  activePipelineStrategy = strat;
  document.getElementById("btn-pipe-auto")?.classList.toggle("active", strat === "auto");
  document.getElementById("btn-pipe-manual")?.classList.toggle("active", strat === "manual");
  const btnProduceText = document.getElementById("btn-produce-text");
  if (btnProduceText) {
    btnProduceText.textContent = strat === "auto"
      ? (activeExecutionMode === "test" ? `Run Draft (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : "Produce Master Video")
      : (activeExecutionMode === "test" ? `Run Test (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : "Produce Video (Gate)");
  }
  document.getElementById("studio-stage-controls-dock")?.classList.toggle("hidden", strat === "auto");
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    currentActiveInspectorEpisode.pipelineStrategy = strat;
    currentActiveInspectorEpisode.pipeline_strategy = strat;
    if (typeof updateStageGateDock === "function") updateStageGateDock(currentActiveInspectorEpisode);
  }
  if (!skipPersist) persistCurrentEpisodeInputs({ pipeline_strategy: strat });
}

function setTestShots(val) {
  const parsedInt = parseInt(val, 10);
  activeShotsCount = (isNaN(parsedInt) || parsedInt === -1) ? -1 : parsedInt;
  const testStretchSel = document.getElementById("studio-test-stretch");
  if (activeShotsCount === 1 && testStretchSel) {
    testStretchSel.value = "0.0083";
    activeBroadcastHours = 0.0083;
    activeTestDuration = 30.0;
  } else if (testStretchSel) {
    const isTravel = (typeof isTravelOrSkylineChannel === "function") && isTravelOrSkylineChannel();
    const parsed = parseTestDuration(testStretchSel.value, isTravel);
    activeBroadcastHours = parsed.lpHours;
    activeTestDuration = parsed.durSec;
  } else {
    activeTestDuration = activeShotsCount === -1 ? 60.0 : (activeShotsCount * 5.0);
  }

  const btnProduceText = document.getElementById("btn-produce-text");
  if (activeExecutionMode === "test" && btnProduceText) {
    const shotsLabel = activeShotsCount === -1 ? "Auto" : `${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''}`;
    btnProduceText.textContent = activePipelineStrategy === "manual" ? `TEST (MANUAL ${shotsLabel})` : `TEST DRAFT (${shotsLabel})`;
  }
  calculateLiveCostEstimate();
}

function parseTestDuration(val, isTravel) {
  const v = String(val || ""), num = parseFloat(v) || 0.0;
  if (v === "custom") {
    const custNum = Math.max(0.1, parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2);
    return { durSec: custNum * 60.0, lpHours: 0.0 };
  }
  if (v === "0.0083" || v === "30s" || (num > 0.007 && num < 0.010)) return { durSec: 30.0, lpHours: 0.0083 };
  if (v === "0.0167" || v === "60s" || v === "1m" || (num > 0.015 && num < 0.020)) return { durSec: 60.0, lpHours: 0.0167 };
  if (v === "0.033" || v === "120s" || v === "2m" || (num > 0.030 && num < 0.040)) return { durSec: 120.0, lpHours: 0.033 };
  if (num >= 1.0) return { durSec: Math.round(num * 3600), lpHours: num };
  if (isTravel) return { durSec: 120.0, lpHours: 0.033 };
  return { durSec: (activeShotsCount || 1) * 5.0, lpHours: 0.0 };
}

function setBroadcastHours(val) {
  const isTravel = (typeof isTravelOrSkylineChannel === "function") && isTravelOrSkylineChannel();
  const parsed = parseTestDuration(val, isTravel);
  activeBroadcastHours = parsed.lpHours;
  activeTestDuration = parsed.durSec;
  document.getElementById("studio-custom-duration-container")?.classList.toggle("hidden", val !== "custom");
  calculateLiveCostEstimate();
}

function updateDurationOptionsForNiche(groupKey) {
  currentNicheGroup = groupKey || "relaxation";
  const select = document.getElementById("studio-stretch-hours");
  if (!select) return;
  const prevVal = select.value;
  let opts = (currentNicheGroup === "relaxation") ? `<option value="90s">Short Master (90s)</option>` : "";
  for (let m = (currentNicheGroup === "relaxation" ? 2 : 1); m <= 15; m++) opts += `<option value="${m}m">${m} min (${m * 60}s)</option>`;
  if (currentNicheGroup === "relaxation") {
    for (let h = 1; h <= 8; h++) opts += `<option value="${h}h" ${h === 3 && !prevVal ? 'selected' : ''}>${h === 3 ? "3 Hours (4K Broadcast)" : (h === 8 ? "8 Hours (Overnight)" : `${h} Hour${h > 1 ? 's' : ''} Stream`)}</option>`;
  }
  opts += `<option value="custom">Custom (Minutes)...</option>`;
  select.innerHTML = opts;
  if (prevVal && select.querySelector(`option[value="${prevVal}"]`)) select.value = prevVal;
  document.getElementById("studio-custom-duration-container")?.classList.toggle("hidden", select.value !== "custom");
  calculateLiveCostEstimate();
}

function onStudioDurationDropdownChange(val) {
  document.getElementById("studio-custom-duration-container")?.classList.toggle("hidden", val !== "custom");
  calculateLiveCostEstimate();
}

function onCustomMinutesInput(val) {
  const mins = Math.max(0.1, parseFloat(val) || 2);
  activeTestDuration = mins * 60.0;
  calculateLiveCostEstimate();
}

function getEffectiveProductionDuration() {
  const isTravel = (typeof isTravelOrSkylineChannel === "function") && isTravelOrSkylineChannel();
  const isTest = (typeof activeExecutionMode !== "undefined" && activeExecutionMode === "test");

  if (isTest) {
    const testStretchEl = document.getElementById("studio-test-stretch");
    const testVal = testStretchEl?.value || (isTravel ? "0.033" : "0");
    if (testVal === "custom") {
      const custNum = Math.max(0.1, parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2);
      return { durSec: custNum * 60.0, lpHours: 0.0 };
    }
    return parseTestDuration(testVal, isTravel);
  }

  const durVal = document.getElementById("studio-stretch-hours")?.value || "2m";
  let resolvedDur = { durSec: 120.0, lpHours: 0.0 };

  if (durVal === "custom") {
    const custNum = Math.max(0.1, parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2);
    resolvedDur = { durSec: custNum * 60.0, lpHours: (custNum >= 60 ? custNum / 60.0 : 0.0) };
  } else if (durVal.endsWith("h")) {
    resolvedDur = { durSec: 90.0, lpHours: parseFloat(durVal) || 3.0 };
  } else if (durVal.endsWith("m")) {
    resolvedDur = { durSec: (parseInt(durVal, 10) || 2) * 60.0, lpHours: 0.0 };
  } else if (durVal === "90s" || durVal === "0") {
    resolvedDur = { durSec: 90.0, lpHours: 0.0 };
  } else {
    const num = parseFloat(durVal) || 2.0;
    resolvedDur = num <= 8 ? { durSec: 90.0, lpHours: num } : { durSec: num * 60.0, lpHours: 0.0 };
  }
  return resolvedDur;
}

function isTravelOrSkylineChannel() {
  const selChan = (typeof currentChannel !== "undefined" && currentChannel?.id) || document.getElementById("studio-channel-select")?.value || "";
  const genreVal = (document.getElementById("studio-genre-selector")?.value || "").toLowerCase();
  const subgVal = (document.getElementById("studio-subgenre-selector")?.value || "").toLowerCase();
  const archVal = (document.getElementById("studio-archetype-selector")?.value || "").toLowerCase();
  const fmtVal = (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "").toLowerCase();
  return (
    selChan.includes("skyline") || genreVal.startsWith("travel") || genreVal === "documentary" ||
    genreVal.includes("doc_places") || subgVal.includes("doc_places") || subgVal.includes("tour") ||
    archVal.includes("tour") || archVal.includes("itinerary") || fmtVal === "documentary" || fmtVal === "walking_tour" ||
    (typeof currentChannel !== "undefined" && (currentChannel?.genre?.startsWith("travel") || currentChannel?.genre === "documentary"))
  );
}

function syncTravelShotUI() {
  const fmt = (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "relaxation").toLowerCase();
  const genreVal = (document.getElementById("studio-genre-selector")?.value || "").toLowerCase();
  const isRelax = (fmt === "relaxation" || fmt.startsWith("relax") || genreVal.startsWith("relax") || genreVal.includes("relax/")), isDocOrTour = !isRelax && isTravelOrSkylineChannel();
  const testShotsEl = document.getElementById("studio-test-shots"), prodShotsEl = document.getElementById("studio-prod-shots");
  const testStretchEl = document.getElementById("studio-test-stretch"), prodStretchEl = document.getElementById("studio-stretch-hours");
  const cadenceCont = document.getElementById("relaxation-cadence-container"), btnProduceText = document.getElementById("btn-produce-text");

  if (cadenceCont) cadenceCont.style.display = (isRelax || isDocOrTour) ? "none" : "";
  if (isRelax) {
    if (testShotsEl) { testShotsEl.style.display = ""; testShotsEl.value = "1"; testShotsEl.disabled = true; activeShotsCount = 1; }
    if (prodShotsEl) { prodShotsEl.style.display = ""; prodShotsEl.value = "1"; prodShotsEl.disabled = true; }
    if (testStretchEl) { testStretchEl.disabled = false; }
    if (prodStretchEl) { prodStretchEl.disabled = false; }
  } else if (isDocOrTour) {
    if (testShotsEl) { testShotsEl.style.display = "none"; testShotsEl.disabled = false; testShotsEl.value = "-1"; activeShotsCount = -1; }
    if (prodShotsEl) { prodShotsEl.style.display = "none"; prodShotsEl.disabled = false; prodShotsEl.value = "-1"; }
    if (testStretchEl) testStretchEl.disabled = false;
    if (prodStretchEl) prodStretchEl.disabled = false;
  } else {
    if (testShotsEl) { testShotsEl.style.display = ""; testShotsEl.disabled = false; }
    if (prodShotsEl) { prodShotsEl.style.display = ""; prodShotsEl.disabled = false; }
    if (testStretchEl) testStretchEl.disabled = false;
    if (prodStretchEl) prodStretchEl.disabled = false;
  }

  if (testStretchEl?.parentElement) testStretchEl.parentElement.className = isDocOrTour ? "grid grid-cols-1 gap-1.5" : "grid grid-cols-2 gap-1.5";
  if (prodStretchEl?.parentElement) prodStretchEl.parentElement.className = isDocOrTour ? "grid grid-cols-1 gap-1.5" : "grid grid-cols-2 gap-1.5";
  if (isDocOrTour && typeof selectProductionTier === "function" && typeof currentTier !== "undefined" && currentTier !== "balanced") selectProductionTier("balanced");

  if (btnProduceText) {
    if (activeExecutionMode === "test") {
      const shotsLbl = isRelax ? "1 Shot" : (activeShotsCount === -1 ? "Auto Cadence" : `${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''}`);
      btnProduceText.textContent = isDocOrTour ? (activePipelineStrategy === "manual" ? "Run Test (Auto Cadence)" : "Run Draft (Auto Cadence)") : (activePipelineStrategy === "manual" ? `Run Test (${shotsLbl})` : `Run Draft (${shotsLbl})`);
    } else {
      btnProduceText.textContent = activePipelineStrategy === "manual" ? "Produce Video (Gate)" : "Produce Master Video";
    }
  }
}

function calculateLiveCostEstimate() {
  const badge = document.getElementById("studio-live-cost-badge");
  const tierBadge = document.getElementById("tier-active-badge");
  const tier = (typeof PRODUCTION_TIERS !== "undefined" ? PRODUCTION_TIERS[currentTier] : null) || { name: "Draft", priceUsd: 0.02, priceStr: "$0.02 USD" };
  syncTravelShotUI();

  const isTravel = isTravelOrSkylineChannel();
  const effective = (typeof getEffectiveProductionDuration === "function") ? getEffectiveProductionDuration() : { durSec: 120, lpHours: 0.0 };
  const durSec = effective.durSec;
  const shots = isTravel ? Math.max(2, Math.round(durSec / 12.5)) : (activeExecutionMode === "test" ? activeShotsCount : parseInt(document.getElementById("studio-prod-shots")?.value || "1", 10));
  const durSelectVal = document.getElementById("studio-stretch-hours")?.value || "3h";
  const testSelectVal = document.getElementById("studio-test-stretch")?.value || "0.0167";

  let baseCost = shots * 0.04, durLabel = "";
  if (isTravel) {
    const pace = shots > 0 ? Math.round(durSec / shots) : 12;
    durLabel = ` • ${durSec}s (${shots} Landmarks @ ${pace}s)`;
  } else if (activeExecutionMode === "test") {
    if (testSelectVal === "custom") {
      const custNum = parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2;
      durLabel = ` (${custNum}m Custom Preview)`;
    } else {
      durLabel = activeBroadcastHours >= 1.0 ? ` + ${activeBroadcastHours}h 4K Broadcast` : (activeTestDuration > 10 ? ` (${activeTestDuration}s Preview)` : " (Draft)");
    }
  } else if (durSelectVal === "custom") {
    const custNum = parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2;
    durLabel = ` • ${custNum} min Master`;
  } else if (durSelectVal.endsWith("h")) {
    durLabel = ` + ${parseFloat(durSelectVal)}h 4K Broadcast`;
  } else if (durSelectVal.endsWith("m")) {
    durLabel = ` • ${parseInt(durSelectVal, 10)} min Master`;
  } else if (durSelectVal === "90s" || durSelectVal === "0") {
    durLabel = " (Short Master 90s)";
  } else {
    durLabel = ` • ${durSelectVal}`;
  }

  if (badge) badge.textContent = `$${baseCost.toFixed(2)} USD (${shots} Shot${shots > 1 ? 's' : ''}${durLabel})`;
  if (tierBadge) tierBadge.textContent = `${tier.name} (${tier.priceStr})`;
}

document.addEventListener("DOMContentLoaded", () => {
  syncTravelShotUI();
  calculateLiveCostEstimate();
  ["studio-channel-select", "studio-genre-selector"].forEach(id => {
    document.getElementById(id)?.addEventListener("change", () => { syncTravelShotUI(); calculateLiveCostEstimate(); });
  });
});

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (typeof quickTestProduceFromPrompt === "function") quickTestProduceFromPrompt();
  }
});
