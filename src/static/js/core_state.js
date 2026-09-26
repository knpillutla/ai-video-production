// CineAI Studio: Global State & Production Tier Definitions
const PRODUCTION_TIERS = {
  low_cost: {
    key: "low_cost",
    name: "Low-Cost Test",
    priceUsd: 0.02,
    priceStr: "$0.02 USD",
    models: "Fal FLUX.1-dev • 10s Draft Test • Azure TTS",
    targetDuration: 10
  },
  balanced: {
    key: "balanced",
    name: "Balanced Creator",
    priceUsd: 0.14,
    priceStr: "$0.14 USD",
    models: "FLUX Dev • Azure Speech • YouTube Ready",
    targetDuration: 30
  },
  cinematic: {
    key: "cinematic",
    name: "Cinematic 4K",
    priceUsd: 0.45,
    priceStr: "$0.45 USD",
    models: "FLUX Pro • Suno BGM • 4K Master",
    targetDuration: 60
  }
};

let currentTier = "balanced";
let activeTab = "studio";

let currentUser = {
  id: "user_krishna_01",
  display_name: "Krishna P.",
  email: "creator@cineai.studio",
  avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80",
  balance_usd: 10.00,
  container_id: "user-c4b8e28f",
  theme: "dark"
};

function switchTab(tabId) {
  activeTab = tabId;
  const tabs = ["studio", "ledger", "apps", "dashboard", "channels", "analytics"];
  tabs.forEach(t => {
    const el = document.getElementById("tab-" + t);
    const btn = document.getElementById("tab-btn-" + t);
    if (el) el.classList.toggle("hidden", t !== tabId);
    if (btn) {
      if (t === tabId) {
        btn.classList.add("text-white", "bg-indigo-600/20", "border-r-2", "border-indigo-500");
        btn.classList.remove("text-gray-400");
      } else {
        btn.classList.remove("text-white", "bg-indigo-600/20", "border-r-2", "border-indigo-500");
        btn.classList.add("text-gray-400");
      }
    }
  });
  if ((tabId === "studio" || tabId === "ledger") && typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  } else if (tabId === "dashboard" && typeof renderDashboardStats === "function") {
    renderDashboardStats();
  } else if (tabId === "apps" && typeof renderAppsCatalog === "function") {
    renderAppsCatalog();
  } else if (tabId === "channels" && typeof fetchChannelHubVideos === "function") {
    fetchChannelHubVideos();
  }
}

function openModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.remove("hidden");
}

function closeModal(id) {
  const m = document.getElementById(id);
  if (m) m.classList.add("hidden");
}
