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

  // Update button highlights
  ["all", "earth_serenade", "silent_hearth", "cineai_docs", "telugu_comedy"].forEach(k => {
    const btn = document.getElementById("studio-ch-" + k);
    if (!btn) return;
    if (k === channelId) {
      btn.className = "px-2.5 py-1 rounded-lg text-xs font-bold transition bg-indigo-600 text-white shadow-sm flex items-center gap-1.5 ring-1 ring-indigo-400";
    } else {
      btn.className = "px-2.5 py-1 rounded-lg text-xs font-medium text-slate-700 dark:text-gray-300 hover:text-white bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:border-indigo-500 transition flex items-center gap-1.5";
    }
  });

  const badge = document.getElementById("studio-channel-meta-badge");
  if (badge) badge.textContent = `${meta.name} (${meta.handle})`;

  // Broadcast channel change to decoupled panels
  if (window.StudioBus) {
    window.StudioBus.emit("channel:changed", { channelId, meta });
  }

  // Pre-filter presets based on channel
  if (channelId === "earth_serenade" || channelId === "silent_hearth") {
    switchNicheGroupView("relaxation");
  } else if (channelId === "cineai_docs") {
    switchNicheGroupView("docs");
  } else if (channelId === "telugu_comedy") {
    if (typeof setCreationMode === "function") setCreationMode("idea", true);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  selectStudioChannel("all");
});
