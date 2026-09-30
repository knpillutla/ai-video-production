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

  if (mode === "test") {
    if (btnTest) btnTest.className = "px-1.5 py-0.2 text-[9px] font-bold rounded bg-amber-600 text-white shadow";
    if (btnProd) btnProd.className = "px-1.5 py-0.2 text-[9px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (optTest) optTest.classList.remove("hidden");
    if (optProd) optProd.classList.add("hidden");
    if (btnProduceText) {
      btnProduceText.textContent = activePipelineStrategy === "manual" 
        ? `TEST (MANUAL ${activeShotsCount} Shots)` 
        : `TEST DRAFT (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})`;
    }
  } else {
    if (btnTest) btnTest.className = "px-1.5 py-0.2 text-[9px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (btnProd) btnProd.className = "px-1.5 py-0.2 text-[9px] font-bold rounded bg-indigo-600 text-white shadow";
    if (optTest) optTest.classList.add("hidden");
    if (optProd) optProd.classList.remove("hidden");
    if (btnProduceText) {
      btnProduceText.textContent = activePipelineStrategy === "manual"
        ? "PRODUCE (MANUAL STAGE-GATE)"
        : "PRODUCE MASTER VIDEO";
    }
  }
  calculateLiveCostEstimate();
}

function setPipelineExecutionMode(strat) {
  activePipelineStrategy = strat;
  const btnAuto = document.getElementById("btn-pipe-auto");
  const btnManual = document.getElementById("btn-pipe-manual");
  const btnProduceText = document.getElementById("btn-produce-text");

  if (strat === "auto") {
    if (btnAuto) btnAuto.className = "px-1.5 py-0.2 text-[9px] font-bold rounded bg-indigo-600 text-white shadow";
    if (btnManual) btnManual.className = "px-1.5 py-0.2 text-[9px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (btnProduceText) btnProduceText.textContent = activeExecutionMode === "test" ? `TEST DRAFT (${activeShotsCount} Shot${activeShotsCount > 1 ? 's' : ''})` : "PRODUCE MASTER VIDEO";
    document.getElementById("studio-stage-controls-dock")?.classList.add("hidden");
  } else {
    if (btnAuto) btnAuto.className = "px-1.5 py-0.2 text-[9px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (btnManual) btnManual.className = "px-1.5 py-0.2 text-[9px] font-bold rounded bg-purple-600 text-white shadow";
    if (btnProduceText) btnProduceText.textContent = activeExecutionMode === "test" ? `TEST (MANUAL ${activeShotsCount} Shots)` : "PRODUCE (MANUAL STAGE-GATE)";
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

function setBroadcastHours(val) {
  activeBroadcastHours = parseFloat(val) || 0;
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
  if (typeof activeExecutionMode === "undefined" || activeExecutionMode !== "prod") {
    return { durSec: (typeof activeShotsCount !== "undefined" ? activeShotsCount * 5.0 : 5.0), lpHours: 0.0 };
  }
  const durVal = document.getElementById("studio-stretch-hours")?.value || "3h";
  if (durVal === "custom") {
    const custNum = parseFloat(document.getElementById("studio-custom-minutes-input")?.value || "20") || 20;
    const unit = document.getElementById("studio-custom-unit-select")?.value || "mins";
    if (unit === "hours") {
      return { durSec: 90.0, lpHours: custNum };
    }
    return { durSec: custNum * 60.0, lpHours: 0.0 };
  }
  if (durVal.endsWith("h")) {
    const hours = parseFloat(durVal) || 3.0;
    return { durSec: 90.0, lpHours: hours };
  }
  if (durVal.endsWith("m")) {
    const mins = parseInt(durVal, 10) || 3;
    return { durSec: mins * 60.0, lpHours: 0.0 };
  }
  if (durVal === "90s" || durVal === "0") {
    return { durSec: 90.0, lpHours: 0.0 };
  }
  const num = parseFloat(durVal) || 3.0;
  return num <= 8 ? { durSec: 90.0, lpHours: num } : { durSec: num * 60.0, lpHours: 0.0 };
}

function calculateLiveCostEstimate() {
  const badge = document.getElementById("studio-live-cost-badge");
  const tierBadge = document.getElementById("tier-active-badge");
  const tier = (typeof PRODUCTION_TIERS !== "undefined" ? PRODUCTION_TIERS[currentTier] : null) || { name: "Draft", priceUsd: 0.02, priceStr: "$0.02 USD" };

  const shots = activeExecutionMode === "test" ? activeShotsCount : parseInt(document.getElementById("studio-prod-shots")?.value || "1", 10);
  const durSelectVal = document.getElementById("studio-stretch-hours")?.value || "3h";

  let baseCost = shots * 0.04;
  let durLabel = "";

  if (activeExecutionMode === "test") {
    durLabel = activeBroadcastHours > 0 ? ` + ${activeBroadcastHours}h 4K Broadcast` : " (Draft)";
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

document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (typeof quickTestProduceFromPrompt === "function") {
      quickTestProduceFromPrompt();
    }
  }
});
