// CineAI Studio: Top Channel Bar Controller
let selectedStudioChannel = "all";

const CHANNEL_METAS = {
  all: { name: "All Channels", handle: "@Universal", desc: "Universal Multi-Channel Production Mode" },
  earth_serenade: { name: "Earth Serenade", handle: "@EarthSerenade4K", desc: "4K Nature Soundscapes & Ambient Rain Retreats" },
  silent_hearth: { name: "Silent Hearth", handle: "@SilentHearth4K", desc: "Fireplace Terraces, Cozy Cabins & 432Hz ASMR" },
  cineai_docs: { name: "CineAI Docs", handle: "@CineAIDocs4K", desc: "Blue-Chip 24fps BBC & NatGeo Style Documentaries" },
  telugu_comedy: { name: "Comedy Satire", handle: "@CineAIComedy", desc: "Telugu & Hindi Satirical 9:16 Shorts & Web Drama" }
};

function selectStudioChannel(channelId) {
  selectedStudioChannel = channelId;
  const meta = CHANNEL_METAS[channelId] || CHANNEL_METAS.all;

  // Update button highlights for studio and ledger bars
  ["all", "earth_serenade", "silent_hearth", "cineai_docs", "telugu_comedy"].forEach(k => {
    const activeCls = "px-3 py-1.5 rounded-xl text-xs font-bold transition-all bg-slate-950 text-white dark:bg-white dark:text-slate-950 border border-slate-950 dark:border-white shadow-sm flex items-center gap-1.5 ring-1 ring-black/20 dark:ring-white/20";
    const inactiveCls = "px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-900 dark:text-slate-100 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 hover:border-slate-400 dark:hover:border-slate-600 transition-all flex items-center gap-1.5 shadow-sm";
    const btn = document.getElementById("studio-ch-" + k);
    const ledgerBtn = document.getElementById("ledger-ch-" + k);
    if (btn) btn.className = (k === channelId) ? activeCls : inactiveCls;
    if (ledgerBtn) ledgerBtn.className = (k === channelId) ? activeCls : inactiveCls;
  });

  const badge = document.getElementById("studio-channel-meta-badge");
  if (badge) badge.textContent = `${meta.name} (${meta.handle})`;

  if (typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  }

  // Broadcast channel change to decoupled panels
  if (window.StudioBus) {
    window.StudioBus.emit("channel:changed", { channelId, meta });
  }

  // Pre-filter presets based on channel if functions exist
  try {
    if (typeof switchNicheGroupView === "function") {
      if (channelId === "earth_serenade" || channelId === "silent_hearth") {
        switchNicheGroupView("relaxation");
      } else if (channelId === "cineai_docs") {
        switchNicheGroupView("docs");
      }
    }
    if (channelId === "telugu_comedy" && typeof setCreationMode === "function") {
      setCreationMode("idea", true);
    }
  } catch (err) {
    console.debug("Preset filter notice:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  selectStudioChannel("all");
});
