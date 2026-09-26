// CineAI Studio: Panel 1 Creation Hub Controller (New Production & Channel Archive)
let activeCreationTab = "new";
let channelArchiveEpisodes = [];

function switchCreationTab(tabKey) {
  activeCreationTab = tabKey;
  const btnNew = document.getElementById("btn-tab-creation-new");
  const btnArch = document.getElementById("btn-tab-creation-archive");
  const viewNew = document.getElementById("view-creation-new");
  const viewArch = document.getElementById("view-creation-archive");

  if (tabKey === "new") {
    if (btnNew) btnNew.className = "px-3 py-1 text-xs font-bold rounded-lg transition bg-indigo-600 text-white shadow flex items-center gap-1.5";
    if (btnArch) btnArch.className = "px-3 py-1 text-xs font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5";
    if (viewNew) viewNew.classList.remove("hidden");
    if (viewArch) viewArch.classList.add("hidden");
  } else {
    if (btnNew) btnNew.className = "px-3 py-1 text-xs font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1.5";
    if (btnArch) btnArch.className = "px-3 py-1 text-xs font-bold rounded-lg transition bg-indigo-600 text-white shadow flex items-center gap-1.5";
    if (viewNew) viewNew.classList.add("hidden");
    if (viewArch) viewArch.classList.remove("hidden");
    fetchAndRenderChannelArchive();
  }
}

function switchNicheGroupView(groupKey) {
  const relGrid = document.getElementById("niche-subgrid-relaxation");
  const docGrid = document.getElementById("niche-subgrid-docs");
  const cadContainer = document.getElementById("relaxation-cadence-container");
  if (relGrid) relGrid.classList.toggle("hidden", groupKey !== "relaxation");
  if (docGrid) docGrid.classList.toggle("hidden", groupKey !== "docs");
  if (cadContainer) cadContainer.classList.toggle("hidden", groupKey !== "relaxation");

  const radios = document.querySelectorAll("input[name='niche_group_switch']");
  radios.forEach(r => { if (r.value === groupKey) r.checked = true; });
}

function applyGenreNichePreset() {
  const checkedRadio = document.querySelector("input[name='niche_theme_radio']:checked");
  let nicheKey = checkedRadio ? checkedRadio.value : null;
  if (!nicheKey) {
    const activeGroup = document.querySelector("input[name='niche_group_switch']:checked")?.value || "relaxation";
    nicheKey = activeGroup === "relaxation" ? "relax_ocean" : "doc_wildlife";
    const targetRadio = document.querySelector(`input[name='niche_theme_radio'][value='${nicheKey}']`);
    if (targetRadio) targetRadio.checked = true;
  }
  if (typeof selectNicheRadio === "function") {
    selectNicheRadio(nicheKey);
  }
  // Ensure default shot cadence is 3m
  const cadRadios = document.querySelectorAll("input[name='studio_shot_hold']");
  cadRadios.forEach(r => { r.checked = (r.value === "3m"); });
}

async function fetchAndRenderChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  if (!container) return;

  if (channelArchiveEpisodes.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-xs text-gray-500 font-mono"><i class="fa-solid fa-spinner fa-spin mr-1.5"></i> Loading channel episodes...</div>`;
    try {
      const res = await fetch("/api/channels/episodes");
      const data = await res.json();
      if (data.status === "ok") {
        channelArchiveEpisodes = data.episodes || [];
      }
    } catch (e) {
      console.warn("Could not fetch channel archive:", e);
    }
  }

  filterChannelArchive();
}

function filterChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  const badgeCount = document.getElementById("channel-archive-badge-count");
  if (!container) return;

  const search = (document.getElementById("archive-filter-search")?.value || "").toLowerCase().trim();
  const ch = typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "all";

  const filtered = channelArchiveEpisodes.filter(ep => {
    if (ch !== "all" && ep.channel_id !== ch) return false;
    if (search) {
      const match = [ep.title, ep.episode_id, ep.story_topic].some(s => (s || "").toLowerCase().includes(search));
      if (!match) return false;
    }
    return true;
  });

  if (badgeCount) badgeCount.textContent = filtered.length;

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-xs text-gray-500 bg-slate-50 dark:bg-slate-950/40 rounded-xl border border-dashed border-[var(--border)]">No past productions found for this channel.</div>`;
    return;
  }

  container.innerHTML = filtered.map(ep => `
    <div onclick="selectArchiveEpisode('${ep.episode_id}')" class="p-2.5 bg-slate-50 dark:bg-slate-950/80 hover:bg-indigo-950/30 border border-slate-200 dark:border-slate-800 hover:border-indigo-500 rounded-xl cursor-pointer transition space-y-1 group">
      <div class="flex items-center justify-between">
        <span class="font-mono font-bold text-xs text-indigo-600 dark:text-indigo-400">${ep.episode_id}</span>
        <span class="text-[9px] font-mono px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 font-bold">$${ep.cost_usd.toFixed(2)} USD</span>
      </div>
      <div class="font-bold text-slate-900 dark:text-white text-xs group-hover:text-indigo-300 truncate">${ep.title}</div>
      <div class="text-[10px] text-slate-500 dark:text-gray-400 line-clamp-1">${ep.story_topic}</div>
    </div>
  `).join("");
}

function selectArchiveEpisode(epId) {
  const ep = channelArchiveEpisodes.find(x => x.episode_id === epId);
  if (!ep) return;
  if (window.StudioBus) {
    window.StudioBus.emit("episode:selected", ep);
  }
}

if (window.StudioBus) {
  window.StudioBus.on("channel:changed", () => {
    if (activeCreationTab === "archive") filterChannelArchive();
  });
}
