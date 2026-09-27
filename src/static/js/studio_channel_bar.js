// CineAI Studio: Top Channel Bar Controller (Dynamic multi-tenant channels)
let selectedStudioChannel = null;
let studioChannelMetas = {};

function updateStudioChannelMetas(channelsList) {
  studioChannelMetas = {};
  if (Array.isArray(channelsList) && channelsList.length > 0) {
    channelsList.forEach(ch => {
      const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
      studioChannelMetas[slug] = {
        id: ch.id,
        slug: slug,
        name: ch.channel_name,
        handle: ch.channel_handle || `@${slug}`,
        desc: ch.description || ch.primary_genre || "",
        icon: ch.icon || "fa-clapperboard",
        color: ch.color || "indigo",
        category: ch.category || "General",
        raw: ch
      };
    });
  }
  renderStudioChannelChips();
}

function renderStudioChannelChips() {
  const container = document.getElementById("studio-channel-chips");
  if (!container) return;

  const slugs = Object.keys(studioChannelMetas);
  if (slugs.length === 0) {
    selectedStudioChannel = null;
    container.innerHTML = `
      <div class="flex items-center gap-2">
        <span class="text-xs text-slate-500 dark:text-gray-400 italic">No channels created yet</span>
        <button type="button" onclick="openCreateChannelModal()" class="px-2.5 py-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold rounded-lg text-xs flex items-center gap-1 shadow transition active:scale-95">
          <i class="fa-solid fa-plus text-[10px]"></i>
          <span>Create Channel</span>
        </button>
      </div>
    `;
    updateStudioChannelBadge();
    return;
  }

  if (!selectedStudioChannel || !studioChannelMetas[selectedStudioChannel]) {
    selectedStudioChannel = slugs[0];
  }

  const html = slugs.map(slug => {
    const meta = studioChannelMetas[slug];
    const isSelected = slug === selectedStudioChannel;
    const activeCls = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-indigo-600 text-white border-2 border-indigo-600 shadow-md flex items-center gap-1.5 ring-2 ring-indigo-500/40";
    const inactiveCls = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all flex items-center gap-1.5 shadow-sm";

    return `
      <button type="button" onclick="selectStudioChannel('${slug}')" id="studio-ch-${slug}" class="${isSelected ? activeCls : inactiveCls}">
        <i class="fa-solid ${meta.icon} text-[11px] text-${meta.color}-500"></i>
        <span>${meta.name}</span>
        <span class="text-[9px] font-mono opacity-80">${meta.category}</span>
      </button>
    `;
  }).join("");

  container.innerHTML = html;
  updateStudioChannelBadge();
}

function selectStudioChannel(channelId) {
  const slugs = Object.keys(studioChannelMetas);
  if (slugs.length === 0) {
    selectedStudioChannel = null;
    updateStudioChannelBadge();
    return;
  }
  if (!studioChannelMetas[channelId]) {
    channelId = slugs[0];
  }
  selectedStudioChannel = channelId;
  const meta = studioChannelMetas[channelId];

  slugs.forEach(k => {
    const activeCls = "px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all bg-indigo-600 text-white border-2 border-indigo-600 shadow-md flex items-center gap-1.5 ring-2 ring-indigo-500/40";
    const inactiveCls = "px-3.5 py-1.5 rounded-xl text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 hover:border-indigo-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-all flex items-center gap-1.5 shadow-sm";
    const btn = document.getElementById("studio-ch-" + k);
    if (btn) btn.className = (k === channelId) ? activeCls : inactiveCls;
  });

  updateStudioChannelBadge();

  if (typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  }

  if (window.StudioBus) {
    window.StudioBus.emit("channel:changed", { channelId, meta });
  }
}

function updateStudioChannelBadge() {
  const badge = document.getElementById("studio-channel-meta-badge");
  if (!badge) return;
  if (selectedStudioChannel && studioChannelMetas[selectedStudioChannel]) {
    const meta = studioChannelMetas[selectedStudioChannel];
    badge.textContent = `${meta.name} (${meta.handle})`;
  } else {
    badge.textContent = "No Active Channel";
  }
}

document.addEventListener("DOMContentLoaded", () => {
  renderStudioChannelChips();
});
