// CineAI Studio: Panel 2 Controls & Engine Controller (Execution Mode, Cadence & Cost Math)
let activeExecutionMode = "test"; // "test" | "prod"
let activePipelineStrategy = "manual"; // "auto" | "manual"
let activeTestDuration = 5;
let activeShotsCount = 1;
let activeBroadcastHours = 0.0;
let currentNicheGroup = "relaxation";

function setExecutionMode(mode) {
  activeExecutionMode = mode;
  const btnTest = document.getElementById("btn-exec-test");
  const btnProd = document.getElementById("btn-exec-prod");
  const optTest = document.getElementById("exec-options-test");
  const optProd = document.getElementById("exec-options-prod");
  const btnProduceText = document.getElementById("btn-produce-text");

  if (btnTest) btnTest.classList.toggle("active", mode === "test");
  if (btnProd) btnProd.classList.toggle("active", mode === "prod");

  if (mode === "test") {
    if (optTest) optTest.classList.remove("hidden");
    if (optProd) optProd.classList.add("hidden");
    if (btnProduceText) {
      btnProduceText.textContent = activePipelineStrategy === "manual" 
        ? `Run Test (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` 
        : `Run Draft (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})`;
    }
  } else {
    if (optTest) optTest.classList.add("hidden");
    if (optProd) optProd.classList.remove("hidden");
    if (btnProduceText) {
      btnProduceText.textContent = activePipelineStrategy === "manual"
        ? "Produce Video (Gate)"
        : "Produce Master Video";
    }
  }
  syncTravelShotUI();
  calculateLiveCostEstimate();
}

function setPipelineExecutionMode(strat) {
  activePipelineStrategy = strat;
  const btnAuto = document.getElementById("btn-pipe-auto");
  const btnManual = document.getElementById("btn-pipe-manual");
  const btnProduceText = document.getElementById("btn-produce-text");

  if (btnAuto) btnAuto.classList.toggle("active", strat === "auto");
  if (btnManual) btnManual.classList.toggle("active", strat === "manual");

  if (strat === "auto") {
    if (btnProduceText) btnProduceText.textContent = activeExecutionMode === "test" ? `Run Draft (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : "Produce Master Video";
    document.getElementById("studio-stage-controls-dock")?.classList.add("hidden");
  } else {
    if (btnProduceText) btnProduceText.textContent = activeExecutionMode === "test" ? `Run Test (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : "Produce Video (Gate)";
  }

  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    currentActiveInspectorEpisode.pipelineStrategy = strat;
    if (typeof updateStageGateDock === "function") updateStageGateDock(currentActiveInspectorEpisode);
  }
}

function setTestShots(val) {
  activeShotsCount = parseInt(val, 10) || 1;
  activeTestDuration = activeShotsCount * 5;
  const btnProduceText = document.getElementById("btn-produce-text");
  if (activeExecutionMode === "test" && btnProduceText) {
    btnProduceText.textContent = activePipelineStrategy === "manual"
      ? `TEST (MANUAL ${activeShotsCount} Shots)`
      : `TEST DRAFT (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})`;
  }
  calculateLiveCostEstimate();
}

function parseTestDuration(val, isTravel) {
  const v = String(val || "");
  const num = parseFloat(v) || 0.0;
  if (v === "0.0083" || v === "30s" || (num > 0.007 && num < 0.010)) {
    return { durSec: 30.0, lpHours: 0.0083 };
  }
  if (v === "0.0167" || v === "60s" || v === "1m" || (num > 0.015 && num < 0.020)) {
    return { durSec: 60.0, lpHours: 0.0167 };
  }
  if (v === "0.033" || v === "120s" || v === "2m" || (num > 0.030 && num < 0.040)) {
    return { durSec: 120.0, lpHours: 0.033 };
  }
  if (num >= 1.0) {
    return { durSec: Math.round(num * 3600), lpHours: num };
  }
  if (isTravel) {
    return { durSec: 120.0, lpHours: 0.033 };
  }
  return { durSec: (activeShotsCount || 1) * 5.0, lpHours: 0.0 };
}

function setBroadcastHours(val) {
  const isTravel = (typeof isTravelOrSkylineChannel === "function") && isTravelOrSkylineChannel();
  const parsed = parseTestDuration(val, isTravel);
  activeBroadcastHours = parsed.lpHours;
  activeTestDuration = parsed.durSec;
  calculateLiveCostEstimate();
}

function updateDurationOptionsForNiche(groupKey) {
  currentNicheGroup = groupKey || "relaxation";
  const select = document.getElementById("studio-stretch-hours");
  const customContainer = document.getElementById("studio-custom-duration-container");
  if (!select) return;

  if (currentNicheGroup === "relaxation") {
    let opts = `<option value="90s">Short Master (90s)</option>`;
    for (let m = 2; m <= 15; m++) {
      opts += `<option value="${m}m">${m} min (${m * 60}s)</option>`;
    }
    for (let h = 1; h <= 8; h++) {
      const label = h === 3 ? "3 Hours (4K Broadcast)" : (h === 8 ? "8 Hours (Overnight)" : (h === 1 ? "1 Hour Stream" : `${h} Hours Stream`));
      opts += `<option value="${h}h" ${h === 3 ? 'selected' : ''}>${label}</option>`;
    }
    opts += `<option value="custom">Custom...</option>`;
    select.innerHTML = opts;
    if (customContainer) customContainer.classList.add("hidden");
  } else {
    let opts = "";
    for (let m = 1; m <= 15; m++) {
      opts += `<option value="${m}m" ${m === 3 ? 'selected' : ''}>${m} min (${m * 60}s)</option>`;
    }
    opts += `<option value="custom">Custom...</option>`;
    select.innerHTML = opts;
    if (customContainer) customContainer.classList.add("hidden");
  }
  calculateLiveCostEstimate();
}

function onStudioDurationDropdownChange(val) {
  const customContainer = document.getElementById("studio-custom-duration-container");
  if (customContainer) {
    customContainer.classList.toggle("hidden", val !== "custom");
  }
  calculateLiveCostEstimate();
}

function getEffectiveProductionDuration() {
  const isTravel = (typeof isTravelOrSkylineChannel === "function") && isTravelOrSkylineChannel();
  const isTest = (typeof activeExecutionMode !== "undefined" && activeExecutionMode === "test");

  if (isTest) {
    const testStretchEl = document.getElementById("studio-test-stretch");
    return parseTestDuration(testStretchEl?.value || (isTravel ? "0.033" : "0"), isTravel);
  }

  const durVal = document.getElementById("studio-stretch-hours")?.value || "2m";
  let resolvedDur = { durSec: 120.0, lpHours: 0.0 };

  if (durVal === "custom") {
    const custNum = parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "2") || 2;
    const unit = document.getElementById("studio-custom-unit-select")?.value || "mins";
    if (unit === "hours") {
      resolvedDur = { durSec: 90.0, lpHours: custNum };
    } else {
      resolvedDur = { durSec: custNum * 60.0, lpHours: 0.0 };
    }
  } else if (durVal.endsWith("h")) {
    const hours = parseFloat(durVal) || 3.0;
    resolvedDur = { durSec: 90.0, lpHours: hours };
  } else if (durVal.endsWith("m")) {
    const mins = parseInt(durVal, 10) || 2;
    resolvedDur = { durSec: mins * 60.0, lpHours: 0.0 };
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
  const genreVal = document.getElementById("studio-genre-selector")?.value || "";
  return (
    selChan === "skylinediariesindia4k" ||
    selChan.includes("skyline") ||
    genreVal.startsWith("travel") ||
    (typeof currentChannel !== "undefined" && currentChannel?.genre?.startsWith("travel"))
  );
}

function syncTravelShotUI() {
  const isTravel = isTravelOrSkylineChannel();
  const testShotsEl = document.getElementById("studio-test-shots");
  const prodShotsEl = document.getElementById("studio-prod-shots");
  const testStretchEl = document.getElementById("studio-test-stretch");
  const prodStretchEl = document.getElementById("studio-stretch-hours");
  const cadenceCont = document.getElementById("relaxation-cadence-container");
  const btnProduceText = document.getElementById("btn-produce-text");

  if (cadenceCont) {
    cadenceCont.style.display = isTravel ? "none" : "";
  }
  if (testShotsEl) {
    testShotsEl.style.display = isTravel ? "none" : "";
  }
  if (prodShotsEl) {
    prodShotsEl.style.display = isTravel ? "none" : "";
  }
  if (testStretchEl && testStretchEl.parentElement) {
    testStretchEl.parentElement.className = isTravel ? "grid grid-cols-1 gap-1.5" : "grid grid-cols-2 gap-1.5";
    if (isTravel && (!testStretchEl.value || testStretchEl.value === "0")) {
      testStretchEl.value = "0.033";
      activeBroadcastHours = 0.033;
      activeTestDuration = 120;
    }
  }
  if (prodStretchEl && prodStretchEl.parentElement) {
    prodStretchEl.parentElement.className = isTravel ? "grid grid-cols-1 gap-1.5" : "grid grid-cols-2 gap-1.5";
  }

  if (isTravel && typeof selectProductionTier === "function" && typeof currentTier !== "undefined" && currentTier !== "balanced") {
    selectProductionTier("balanced");
  }

  if (btnProduceText) {
    if (activeExecutionMode === "test") {
      btnProduceText.textContent = isTravel
        ? "Run Preview (Autonomous Cadence)"
        : (activePipelineStrategy === "manual" ? `Run Test (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : `Run Draft (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})`);
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

  let baseCost = shots * 0.04;
  let durLabel = "";

  if (isTravel) {
    const pace = shots > 0 ? Math.round(durSec / shots) : 12;
    durLabel = ` • ${durSec}s (${shots} Landmarks @ ${pace}s)`;
  } else if (activeExecutionMode === "test") {
    durLabel = activeBroadcastHours >= 1.0 ? ` + ${activeBroadcastHours}h 4K Broadcast` : (activeTestDuration > 10 ? ` (${activeTestDuration}s Preview)` : " (Draft)");
  } else if (durSelectVal === "custom") {
    const custNum = parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "20") || 20;
    const unit = document.getElementById("studio-custom-unit-select")?.value || "mins";
    durLabel = unit === "hours" ? ` + ${custNum}h 4K Broadcast` : ` • ${custNum} min Master`;
  } else if (durSelectVal.endsWith("h")) {
    const hours = parseFloat(durSelectVal);
    durLabel = ` + ${hours}h 4K Broadcast`;
  } else if (durSelectVal.endsWith("m")) {
    const mins = parseInt(durSelectVal, 10);
    durLabel = ` • ${mins} min Master`;
  } else if (durSelectVal === "90s" || durSelectVal === "0") {
    durLabel = " (Short Master 90s)";
  } else {
    durLabel = ` • ${durSelectVal}`;
  }

  if (badge) {
    badge.textContent = `$${baseCost.toFixed(2)} USD (${shots} Shot${shots > 1 ? 's' : ''}${durLabel})`;
  }
  if (tierBadge) tierBadge.textContent = `${tier.name} (${tier.priceStr})`;
}

document.addEventListener("DOMContentLoaded", () => {
  syncTravelShotUI();
  calculateLiveCostEstimate();
  ["studio-channel-select", "studio-genre-selector"].forEach(id => {
    document.getElementById(id)?.addEventListener("change", () => {
      syncTravelShotUI();
      calculateLiveCostEstimate();
    });
  });
});

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (typeof quickTestProduceFromPrompt === "function") quickTestProduceFromPrompt();
  }
});
