// CineAI Studio: Global State & Production Tier Definitions
const PRODUCTION_TIERS = {
  low_cost: {
    key: "low_cost",
    name: "Draft",
    priceUsd: 0.02,
    priceStr: "$0.02 USD",
    models: "Fal FLUX.1-dev • 10s Draft Test • Azure TTS",
    targetDuration: 10
  },
  balanced: {
    key: "balanced",
    name: "Balanced",
    priceUsd: 0.14,
    priceStr: "$0.14 USD",
    models: "FLUX Dev • Azure Speech • YouTube Ready",
    targetDuration: 30
  },
  cinematic: {
    key: "cinematic",
    name: "4K Master",
    priceUsd: 0.45,
    priceStr: "$0.45 USD",
    models: "FLUX Pro • Suno BGM • 4K Master",
    targetDuration: 60
  }
};

let currentTier = "cinematic";
let activeTab = "studio";

let currentUser = {
  id: "knpillutla_gmail_com",
  display_name: "Krishna Pillutla",
  email: "knpillutla@gmail.com",
  avatar_url: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80",
  balance_usd: 100.00,
  container_id: "user-knpillutla-gmail-com",
  theme: "dark"
};

function switchTab(tabId) {
  activeTab = tabId;
  const tabs = ["studio", "studio-pro", "ledger", "apps", "dashboard", "channels", "analytics"];
  tabs.forEach(t => {
    const el = document.getElementById("tab-" + t);
    const btn = document.getElementById("tab-btn-" + t);
    if (el) el.classList.toggle("hidden", t !== tabId);
    if (btn) {
      if (t === tabId) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
    }
  });
  if (tabId === "studio-pro" && typeof renderStudioProView === "function") {
    renderStudioProView(typeof currentActiveInspectorEpisode !== "undefined" ? currentActiveInspectorEpisode : null);
  } else if ((tabId === "studio" || tabId === "ledger") && typeof renderStudioVideoHistory === "function") {
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
