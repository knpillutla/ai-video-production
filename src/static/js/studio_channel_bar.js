// CineAI Studio: Top Channel Bar & Ledger Channel Chips Controller (Dynamic API integration)
let selectedStudioChannel = null;
let studioChannelMetas = {};

function updateStudioChannelMetas(channelsList) {
  studioChannelMetas = {};
  if (Array.isArray(channelsList) && channelsList.length > 0) {
    channelsList.forEach(ch => {
      const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
      const cachedProf = (typeof cachedChannelProfiles !== "undefined" && cachedChannelProfiles[slug]) ? cachedChannelProfiles[slug] : null;
      const defaultGenres = (typeof DEFAULT_CHANNEL_GENRES !== "undefined" && DEFAULT_CHANNEL_GENRES[slug]) ? DEFAULT_CHANNEL_GENRES[slug] : null;
      const allowed = ch.allowed_genres || cachedProf?.allowed_genres || defaultGenres || (ch.primary_genre ? [ch.primary_genre] : null);

      studioChannelMetas[slug] = {
        id: ch.id,
        slug: slug,
        name: ch.channel_name,
        handle: ch.channel_handle || `@${slug}`,
        desc: ch.description || ch.primary_genre || "",
        icon: ch.icon || "fa-clapperboard",
        color: ch.color || "indigo",
        category: ch.category || "General",
        tag: ch.tag || ch.raw?.tag || "",
        comments: ch.comments || ch.raw?.comments || "",
        allowed_genres: allowed,
        raw: ch
      };
    });
  }
  renderStudioChannelChips();
}

function renderStudioChannelChips() {
  const selectEl = document.getElementById("studio-channel-select");
  const container = document.getElementById("studio-channel-chips");
  const ledgerContainer = document.getElementById("ledger-channel-chips");
  const slugs = Object.keys(studioChannelMetas);

  if (slugs.length === 0) {
    selectedStudioChannel = null;
    if (selectEl) {
      selectEl.innerHTML = `<option value="" disabled selected>No channels available</option>`;
    }
    updateStudioChannelBadge();
    return;
  }

  if (!selectedStudioChannel || !studioChannelMetas[selectedStudioChannel]) {
    selectedStudioChannel = slugs[0];
  }

  // Populate Dropdown
  if (selectEl) {
    selectEl.innerHTML = slugs.map(slug => {
      const meta = studioChannelMetas[slug];
      const isSelected = (slug === selectedStudioChannel) ? "selected" : "";
      const label = meta.tag ? `${meta.name} [${meta.tag}]` : `${meta.name} (${meta.category})`;
      return `<option value="${slug}" ${isSelected}>${label}</option>`;
    }).join("");
    selectEl.value = selectedStudioChannel;
  }

  // Populate Ledger chips if present
  if (ledgerContainer) {
    const isAll = (selectedStudioChannel === "all");
    const activeCls = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-indigo-600 text-white border-2 border-indigo-600 shadow-md flex items-center gap-1.5 ring-2 ring-indigo-500/40";
    const inactiveCls = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all flex items-center gap-1.5 shadow-sm";

    const allChip = `
      <button type="button" onclick="selectStudioChannel('all')" id="ledger-ch-all" class="${isAll ? activeCls : inactiveCls}">
        <i class="fa-solid fa-network-wired text-[11px] text-indigo-400"></i>
        <span>All Channels</span>
      </button>
    `;
    const ledgerChips = slugs.map(slug => {
      const meta = studioChannelMetas[slug];
      const isSelected = slug === selectedStudioChannel;
      const tagBadge = meta.tag ? `<span class="text-[9px] px-1.5 py-0.2 rounded bg-black/40 text-emerald-300 border border-emerald-500/30 font-bold font-mono tracking-tight ml-1">${meta.tag}</span>` : `<span class="text-[9px] font-mono opacity-80">${meta.category}</span>`;
      return `
        <button type="button" onclick="selectStudioChannel('${slug}')" id="ledger-ch-${slug}" class="${isSelected ? activeCls : inactiveCls}">
          <i class="fa-solid ${meta.icon} text-[11px] text-${meta.color}-500"></i>
          <span>${meta.name}</span>
          ${tagBadge}
        </button>
      `;
    }).join("");
    ledgerContainer.innerHTML = allChip + ledgerChips;
  }

  updateStudioChannelBadge();

  if (typeof syncGenreDropdownForChannel === "function") {
    syncGenreDropdownForChannel(selectedStudioChannel);
  }
}

function selectStudioChannel(channelId) {
  const slugs = Object.keys(studioChannelMetas);
  if (slugs.length === 0) {
    selectedStudioChannel = null;
    updateStudioChannelBadge();
    return;
  }
  if (channelId !== "all" && !studioChannelMetas[channelId]) {
    channelId = slugs[0];
  }
  selectedStudioChannel = channelId;
  const meta = (channelId !== "all") ? studioChannelMetas[channelId] : null;

  const selectEl = document.getElementById("studio-channel-select");
  if (selectEl && channelId !== "all") {
    selectEl.value = channelId;
  }

  const activeCls = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-indigo-600 text-white border-2 border-indigo-600 shadow-md flex items-center gap-1.5 ring-2 ring-indigo-500/40";
  const inactiveCls = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all flex items-center gap-1.5 shadow-sm";

  slugs.forEach(k => {
    const lBtn = document.getElementById("ledger-ch-" + k);
    if (lBtn) lBtn.className = (k === channelId) ? activeCls : inactiveCls;
  });
  const allBtn = document.getElementById("ledger-ch-all");
  if (allBtn) allBtn.className = (channelId === "all") ? activeCls : inactiveCls;

  updateStudioChannelBadge();

  if (typeof syncGenreDropdownForChannel === "function") {
    syncGenreDropdownForChannel(channelId);
  }

  if (typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  }

  if (window.StudioBus) {
    window.StudioBus.emit("channel:changed", { channelId, meta });
  }
  if (typeof syncCameraAngleVisibility === "function") {
    syncCameraAngleVisibility(channelId);
  }
}

function updateStudioChannelBadge() {
  const badge = document.getElementById("studio-channel-meta-badge");
  if (!badge) return;
  if (selectedStudioChannel && selectedStudioChannel !== "all" && studioChannelMetas[selectedStudioChannel]) {
    const meta = studioChannelMetas[selectedStudioChannel];
    badge.textContent = `${meta.name} (${meta.handle})`;
  } else if (selectedStudioChannel === "all") {
    badge.textContent = "All Channels";
  } else {
    badge.textContent = "No Active Channel";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderStudioChannelChips();
});
