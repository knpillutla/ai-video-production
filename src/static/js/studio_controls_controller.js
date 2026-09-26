// CineAI Studio: Panel 2 Controls & Engine Controller (Execution Mode, Cadence & Cost Math)
let activeExecutionMode = "test"; // "test" | "prod"
let activeTestDuration = 10;

function setExecutionMode(mode) {
  activeExecutionMode = mode;
  const btnTest = document.getElementById("btn-exec-test");
  const btnProd = document.getElementById("btn-exec-prod");
  const optTest = document.getElementById("exec-options-test");
  const optProd = document.getElementById("exec-options-prod");
  const btnProduceText = document.getElementById("btn-produce-text");

  if (mode === "test") {
    if (btnTest) btnTest.className = "px-2 py-0.5 text-[10px] font-bold rounded bg-amber-600 text-white shadow";
    if (btnProd) btnProd.className = "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (optTest) optTest.classList.remove("hidden");
    if (optProd) optProd.classList.add("hidden");
    if (btnProduceText) btnProduceText.textContent = `TEST DRAFT (${activeTestDuration}s)`;
  } else {
    if (btnTest) btnTest.className = "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (btnProd) btnProd.className = "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow";
    if (optTest) optTest.classList.add("hidden");
    if (optProd) optProd.classList.remove("hidden");
    if (btnProduceText) btnProduceText.textContent = "PRODUCE MASTER VIDEO";
  }

  calculateLiveCostEstimate();
}

function setTestDuration(sec) {
  activeTestDuration = sec;
  [10, 30, 60].forEach(s => {
    const btn = document.getElementById("btn-test-" + s + "s");
    if (!btn) return;
    if (s === sec) {
      btn.className = "p-1 rounded text-center text-[10px] font-bold bg-amber-600 text-white shadow";
    } else {
      btn.className = "p-1 rounded text-center text-[10px] font-medium text-slate-700 dark:text-gray-300 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800";
    }
  });

  const btnProduceText = document.getElementById("btn-produce-text");
  if (activeExecutionMode === "test" && btnProduceText) {
    btnProduceText.textContent = `TEST DRAFT (${sec}s)`;
  }

  calculateLiveCostEstimate();
}

function calculateLiveCostEstimate() {
  const badge = document.getElementById("studio-live-cost-badge");
  const tierBadge = document.getElementById("tier-active-badge");
  const tier = (typeof PRODUCTION_TIERS !== "undefined" ? PRODUCTION_TIERS[currentTier] : null) || { name: "Balanced", priceUsd: 0.14, priceStr: "$0.14 USD" };

  let durationSec = activeExecutionMode === "test" ? activeTestDuration : parseInt(document.getElementById("studio-duration")?.value || "90", 10);
  let multiplier = durationSec / 60;
  let estimatedCost = Math.max(0.02, tier.priceUsd * (multiplier > 0.5 ? multiplier : 0.5));

  if (activeExecutionMode === "test") {
    estimatedCost = tier.key === "low_cost" ? 0.02 : (tier.key === "balanced" ? 0.05 : 0.12);
    if (badge) badge.textContent = `$${estimatedCost.toFixed(2)} USD (Test ${activeTestDuration}s)`;
  } else {
    if (badge) badge.textContent = `$${estimatedCost.toFixed(2)} USD (Master ${durationSec}s)`;
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
