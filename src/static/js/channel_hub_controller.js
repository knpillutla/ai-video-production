// CineAI Studio: Channel Management & Video Hub Controller with full CRUD
let allChannelEpisodes = [];
let userChannels = [];
let currentHubChannel = "all";

async function fetchUserChannels() {
  try {
    const res = await fetch("/api/channels");
    const data = await res.json();
    if (Array.isArray(data)) {
      userChannels = data;
      if (typeof updateStudioChannelMetas === "function") updateStudioChannelMetas(userChannels);
      renderChannelManagementShelf();
    }
  } catch (err) {
    console.error("Error fetching channels:", err);
  }
}

function renderChannelManagementShelf() {
  const container = document.getElementById("channel-selector-cards");
  if (!container) return;

  if (userChannels.length === 0) {
    container.innerHTML = `
      <div onclick="openCreateChannelModal()" class="col-span-full p-4 bg-white hover:bg-slate-50 border-2 border-dashed border-indigo-300 hover:border-indigo-500 rounded-2xl cursor-pointer transition flex items-center justify-between gap-4 shadow-sm group">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 group-hover:scale-105 flex items-center justify-center text-base transition border border-indigo-100"><i class="fa-solid fa-tower-broadcast"></i></div>
          <div>
            <div class="text-xs font-bold text-slate-900 flex items-center gap-2"><span>No Channels Created Yet</span><span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-300">Action Required</span></div>
            <p class="text-[11px] text-slate-600 font-medium mt-0.5">Click here to configure your YouTube channel with handle, niche, and isolated storage.</p>
          </div>
        </div>
        <button type="button" onclick="openCreateChannelModal()" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition shrink-0"><i class="fa-solid fa-plus text-[10px]"></i><span>Create Channel</span></button>
      </div>
    `;
    return;
  }

  const totalCount = allChannelEpisodes.length;
  const counts = { all: totalCount };
  userChannels.forEach(c => {
    const slug = c.channel_slug || c.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    counts[slug] = allChannelEpisodes.filter(e => e.channel_id === slug).length;
  });

  const allCard = `
    <div onclick="selectHubChannel('all')" id="hub-channel-card-all" class="p-2.5 ${currentHubChannel === 'all' ? 'bg-indigo-950/40 border-2 border-indigo-500 ring-1 ring-indigo-500/40' : 'bg-[var(--card)] border border-[var(--border)] hover:border-indigo-500/60'} rounded-xl cursor-pointer transition space-y-1.5 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5"><div class="w-6 h-6 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs"><i class="fa-solid fa-network-wired"></i></div><span class="font-bold text-white text-xs">All Channels</span></div>
        <span class="text-[10px] font-mono font-bold text-indigo-300 bg-indigo-900/60 px-1.5 py-0.5 rounded border border-indigo-500/30">${totalCount}</span>
      </div>
      <p class="text-[9px] text-gray-400 truncate">Network-wide overview across all series.</p>
    </div>
  `;

  const channelCards = userChannels.map(ch => {
    const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    const isSelected = currentHubChannel === slug;
    const isStudioActive = selectedStudioChannel === slug;
    const epCount = counts[slug] || 0;
    const cardBorder = isSelected ? "bg-indigo-950/40 border-2 border-indigo-500 ring-1 ring-indigo-500/40" : "bg-[var(--card)] border border-[var(--border)] hover:border-indigo-500/60";

    return `
      <div onclick="selectHubChannel('${slug}')" id="hub-channel-card-${slug}" class="p-2.5 ${cardBorder} rounded-xl cursor-pointer transition space-y-2 relative group shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 min-w-0">
            <div class="w-6 h-6 rounded-md bg-${ch.color || 'indigo'}-500/20 text-${ch.color || 'indigo'}-400 flex items-center justify-center text-xs shrink-0"><i class="fa-solid ${ch.icon || 'fa-clapperboard'}"></i></div>
            <div class="min-w-0"><div class="font-bold text-white text-xs truncate">${ch.channel_name}</div><div class="text-[9px] text-gray-400 font-mono truncate">${ch.channel_handle || '@' + slug}</div></div>
          </div>
          <span class="text-[10px] font-mono font-bold text-emerald-300 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-500/30 shrink-0">${epCount}</span>
        </div>
        <div class="flex items-center justify-between pt-1 border-t border-[var(--border)]/60 text-[10px]">
          <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-gray-300 font-medium">${ch.category || 'General'}</span>
          <div class="flex items-center gap-1" onclick="event.stopPropagation()">
            <button onclick="activateChannelFromHub('${slug}')" class="px-1.5 py-0.5 ${isStudioActive ? 'bg-indigo-600 text-white font-bold' : 'bg-slate-800 hover:bg-slate-700 text-gray-300'} rounded text-[9px] transition" title="Set as Active Studio Channel">${isStudioActive ? '✓ Active' : 'Activate'}</button>
            <button onclick="openEditChannelModal('${ch.id}')" class="p-1 hover:text-indigo-400 text-gray-400 transition" title="Edit"><i class="fa-solid fa-pen-to-square text-[10px]"></i></button>
            <button onclick="deleteChannelConfirm('${ch.id}', '${ch.channel_name}')" class="p-1 hover:text-red-400 text-gray-400 transition" title="Delete"><i class="fa-solid fa-trash-can text-[10px]"></i></button>
          </div>
        </div>
      </div>
    `;
  }).join("");

  const addCard = `
    <div onclick="openCreateChannelModal()" class="p-2.5 bg-slate-900/30 hover:bg-slate-900/60 border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl cursor-pointer transition flex flex-col items-center justify-center text-center space-y-1 group shadow-sm min-h-[85px]">
      <div class="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 group-hover:scale-110 flex items-center justify-center text-xs transition"><i class="fa-solid fa-plus"></i></div>
      <span class="text-xs font-bold text-gray-300 group-hover:text-white transition">New Channel</span>
      <span class="text-[9px] text-gray-500">Add YouTube brand</span>
    </div>
  `;
  container.innerHTML = allCard + channelCards + addCard;
}

function activateChannelFromHub(slug) {
  if (typeof selectStudioChannel === "function") selectStudioChannel(slug);
  selectHubChannel(slug);
}

function selectHubChannel(chId) {
  currentHubChannel = chId;
  renderChannelManagementShelf();
  filterChannelHubVideos();
}

function openCreateChannelModal() {
  document.getElementById("crud-is-edit").value = "false";
  document.getElementById("crud-channel-id").value = "";
  document.getElementById("crud-modal-title").textContent = "Create Distribution Channel";
  document.getElementById("crud-channel-slug").disabled = false;
  document.getElementById("crud-submit-btn").innerHTML = '<i class="fa-solid fa-plus text-[10px]"></i><span>Create Channel</span>';
  document.getElementById("channel-crud-form").reset();
  openModal("channel-crud-modal");
}

function openEditChannelModal(channelId) {
  const ch = userChannels.find(c => String(c.id) === String(channelId) || c.channel_slug === channelId);
  if (!ch) return;
  document.getElementById("crud-is-edit").value = "true";
  document.getElementById("crud-channel-id").value = ch.id;
  document.getElementById("crud-modal-title").textContent = `Edit Channel: ${ch.channel_name}`;
  document.getElementById("crud-channel-slug").value = ch.channel_slug || "";
  document.getElementById("crud-channel-slug").disabled = true;
  document.getElementById("crud-channel-name").value = ch.channel_name || "";
  document.getElementById("crud-channel-handle").value = (ch.channel_handle || "").replace(/^@/, "");
  document.getElementById("crud-channel-category").value = ch.category || "General";
  document.getElementById("crud-channel-lang").value = ch.primary_language || "en";
  document.getElementById("crud-channel-icon").value = ch.icon || "fa-clapperboard";
  document.getElementById("crud-channel-color").value = ch.color || "indigo";
  document.getElementById("crud-channel-desc").value = ch.description || "";
  document.getElementById("crud-channel-tags").value = (ch.default_tags || []).join(", ");
  document.getElementById("crud-submit-btn").innerHTML = '<i class="fa-solid fa-floppy-disk text-[10px]"></i><span>Update Channel</span>';
  openModal("channel-crud-modal");
}

function autoPopulateSlug(name) {
  if (document.getElementById("crud-is-edit").value === "true") return;
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 32);
  document.getElementById("crud-channel-slug").value = slug;
  const handleInput = document.getElementById("crud-channel-handle");
  if (handleInput && (!handleInput.value || handleInput.value.length < 3)) {
    handleInput.value = name.replace(/[^a-zA-Z0-9]/g, "");
  }
}

async function saveChannelForm(event) {
  if (event) event.preventDefault();
  const submitBtn = document.getElementById("crud-submit-btn");
  const origBtnHtml = submitBtn ? submitBtn.innerHTML : "";
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-[10px]"></i><span>Saving...</span>';
  }

  const isEdit = document.getElementById("crud-is-edit").value === "true";
  const chId = document.getElementById("crud-channel-id").value;
  const tagsStr = document.getElementById("crud-channel-tags").value;
  const handleRaw = document.getElementById("crud-channel-handle").value.trim();
  const handleClean = handleRaw.startsWith("@") ? handleRaw : `@${handleRaw}`;

  const payload = {
    channel_name: document.getElementById("crud-channel-name").value.trim(),
    channel_slug: document.getElementById("crud-channel-slug").value.trim(),
    channel_handle: handleClean,
    category: document.getElementById("crud-channel-category").value,
    primary_language: document.getElementById("crud-channel-lang").value,
    icon: document.getElementById("crud-channel-icon").value,
    color: document.getElementById("crud-channel-color").value,
    description: document.getElementById("crud-channel-desc").value.trim(),
    default_tags: tagsStr ? tagsStr.split(",").map(t => t.trim()).filter(Boolean) : [],
    platform: "youtube"
  };

  try {
    const res = await fetch(isEdit ? `/api/channels/${chId}` : "/api/channels", {
      method: isEdit ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const errData = await res.json().catch(() => ({}));
      alert(`Error saving channel: ${errData.detail || ('HTTP ' + res.status)}`);
      return;
    }
    closeModal("channel-crud-modal");
    await fetchUserChannels();
    await fetchChannelHubVideos();
    if (!isEdit && payload.channel_slug) {
      activateChannelFromHub(payload.channel_slug);
    }
  } catch (err) {
    console.error("Save channel failure:", err);
    alert(`Failed to save channel: ${err.message || err}`);
  } finally {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = origBtnHtml;
    }
  }
}

async function deleteChannelConfirm(chId, chName) {
  if (!confirm(`Are you sure you want to delete "${chName}"? Existing video files will remain safe in storage.`)) return;
  try {
    const res = await fetch(`/api/channels/${chId}`, { method: "DELETE" });
    if (!res.ok) {
      const err = await res.json();
      alert(`Error deleting channel: ${err.detail || 'Unknown'}`);
      return;
    }
    await fetchUserChannels();
    await fetchChannelHubVideos();
  } catch (err) {
    console.error("Delete channel error:", err);
  }
}

async function fetchChannelHubVideos() {
  const icon = document.getElementById("channel-hub-refresh-icon");
  if (icon) icon.classList.add("fa-spin");
  try {
    const url = currentHubChannel === "all" ? "/api/channels/episodes" : `/api/channels/episodes?channel_id=${currentHubChannel}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === "ok") {
      allChannelEpisodes = data.episodes || [];
      renderChannelManagementShelf();
      renderChannelHubTable();
    }
  } catch (err) {
    console.error("Error fetching channel episodes:", err);
  } finally {
    if (icon) icon.classList.remove("fa-spin");
  }
}

function filterChannelHubVideos() {
  const query = (document.getElementById("channel-hub-search")?.value || "").toLowerCase().trim();
  const statusFilter = document.getElementById("channel-hub-filter-status")?.value || "all";
  const audioFilter = document.getElementById("channel-hub-filter-audio")?.value || "all";
  const formatFilter = document.getElementById("channel-hub-filter-format")?.value || "all";

  const filtered = allChannelEpisodes.filter(ep => {
    if (currentHubChannel !== "all" && ep.channel_id !== currentHubChannel) return false;
    if (statusFilter !== "all" && ep.editions?.every(ed => ed.status !== statusFilter)) return false;
    if (audioFilter === "music" && ep.editions?.every(ed => !ed.audio_mode.includes("Music"))) return false;
    if (audioFilter === "nature" && ep.editions?.every(ed => !ed.audio_mode.includes("Pure Nature"))) return false;
    if (formatFilter === "long" && ep.editions?.every(ed => !ed.format.includes("Long-Play"))) return false;
    if (formatFilter === "short" && ep.editions?.every(ed => !ed.format.includes("Short"))) return false;
    if (query) {
      return [ep.title, ep.story_topic, ep.episode_id, ep.channel_handle, JSON.stringify(ep.models_used)].some(s => (s || "").toLowerCase().includes(query));
    }
    return true;
  });
  renderChannelHubTable(filtered);
}

function renderChannelHubTable(episodes = allChannelEpisodes) {
  const tbody = document.getElementById("channel-hub-tbody");
  if (!tbody) return;
  if (episodes.length === 0) {
    tbody.innerHTML = `<tr><td colspan="13" class="p-6 text-center text-black dark:text-gray-400 text-xs font-medium">No episodes found.</td></tr>`;
    return;
  }

  const rowsHtml = [];
  episodes.forEach((ep, epIdx) => {
    const editions = (ep.editions && ep.editions.length > 0) ? ep.editions : [
      { edition_id: "default", name: "4K Master Video", icon: "fa-film text-indigo-500", audio_mode: "Music Master", duration: "90s", format: "16:9 Master", status: "completed", url: ep.artifacts?.master_music || "" }
    ];
    const spanCount = editions.length;
    const stagePill = (ok, label) => `<span class="px-1 py-0.2 ${ok ? 'bg-emerald-100 dark:bg-emerald-950/80 text-emerald-950 dark:text-emerald-300 border-emerald-400 font-bold' : 'bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-gray-500 border-slate-300'} border rounded text-[8px] font-mono">${ok ? '✓' : '○'} ${label}</span>`;
    const stagesHtml = `<div class="flex items-center gap-0.5 justify-center flex-wrap">${stagePill(ep.stages?.stage_1_keyframes, "S1")}${stagePill(ep.stages?.stage_2_cineloop_masters, "S2")}${stagePill(ep.stages?.stage_3_crf22_compression, "S3")}${stagePill(ep.stages?.stage_4_long_play_stretch, "S4")}</div>`;
    const modelsHtml = `<div class="flex flex-col text-[9px] text-black dark:text-gray-300 leading-tight"><span class="font-mono font-bold text-indigo-900 dark:text-indigo-300">🧠 ${ep.models_used?.scripting || 'Gemini'}</span><span class="font-mono font-bold text-purple-900 dark:text-purple-300">🎨 ${ep.models_used?.visuals?.split(' ')[0] || 'FLUX'} + 🎬 ${ep.models_used?.motion?.split(' ')[0] || 'Kling'}</span></div>`;
    const epBg = epIdx % 2 === 0 ? "bg-slate-50/70 dark:bg-slate-900/10" : "bg-white dark:bg-slate-800/10";

    editions.forEach((ed, edIdx) => {
      const isFirst = edIdx === 0, rowBorder = (edIdx === spanCount - 1) ? "border-b-2 border-indigo-400 dark:border-indigo-500/40" : "border-b border-slate-200 dark:border-slate-800/40";
      const sBadge = `<span class="px-1.5 py-0.2 ${ed.status === 'published' ? 'bg-emerald-100 dark:bg-emerald-500/20 text-emerald-950 dark:text-emerald-400 border-emerald-400' : 'bg-blue-100 dark:bg-blue-500/20 text-blue-950 dark:text-blue-400 border-blue-400'} border rounded font-bold text-[9px]">${ed.status === 'published' ? 'Published' : 'Ready'}</span>`;
      let rowHtml = `<tr class="hover:bg-indigo-50/70 dark:hover:bg-indigo-950/20 transition ${rowBorder} ${epBg}">`;
      if (isFirst) {
        rowHtml += `<td rowspan="${spanCount}" class="px-2.5 py-2 align-middle border-r border-slate-200 dark:border-[var(--border)]"><div class="text-[11px] font-bold text-black dark:text-white flex items-center gap-1.5"><i class="fa-solid ${ep.channel_icon} text-${ep.channel_color}-600 dark:text-${ep.channel_color}-400 text-[10px]"></i><span>${ep.channel_name}</span></div><div class="text-[9px] text-black dark:text-gray-400 font-mono font-medium mt-0.5">${ep.channel_handle}</div></td><td rowspan="${spanCount}" class="px-2.5 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]"><div class="font-mono font-bold text-black dark:text-indigo-300 text-[11px] select-all whitespace-nowrap">${ep.episode_id}</div></td>`;
      }
      rowHtml += `<td class="px-2.5 py-1.5"><div class="flex items-center gap-1.5"><i class="fa-solid ${ed.icon} text-[11px]"></i><span class="font-bold text-black dark:text-white text-[11px]">${ed.name}</span></div><div class="text-[9px] text-slate-800 dark:text-gray-400 font-mono font-medium mt-0.5">${ed.format} • ${ed.size_str || ''}</div></td>`;
      if (isFirst) {
        rowHtml += `<td rowspan="${spanCount}" class="px-2.5 py-2 align-middle max-w-[170px] border-r border-slate-200 dark:border-[var(--border)]"><div class="font-bold text-black dark:text-white text-[11px] leading-tight" title="${ep.title}">${ep.title}</div><div class="text-[9px] text-slate-800 dark:text-gray-400 mt-0.5 font-medium">${ep.category}</div></td><td rowspan="${spanCount}" class="px-2.5 py-2 align-middle max-w-[190px] border-r border-slate-200 dark:border-[var(--border)]"><a href="javascript:void(0)" onclick="openScriptModal('${ep.episode_id}')" class="text-black dark:text-sky-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-bold text-[11px] underline underline-offset-2 flex items-start gap-1 leading-snug cursor-pointer group" title="Click to view script"><i class="fa-solid fa-scroll text-indigo-700 dark:text-indigo-400 text-[10px] mt-0.5 shrink-0 group-hover:scale-110 transition-transform"></i><span class="line-clamp-2">${ep.story_topic}</span></a></td>`;
      }
      rowHtml += `<td class="px-2 py-1.5 text-center">${sBadge}</td><td class="px-2 py-1.5 text-center"><span class="px-1.5 py-0.2 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded text-[9px] font-bold text-black dark:text-gray-300">${ed.audio_mode}</span></td><td class="px-2 py-1.5 text-center font-mono font-bold text-black dark:text-white text-[11px] whitespace-nowrap">${ed.duration}</td>`;
      if (isFirst) {
        rowHtml += `<td rowspan="${spanCount}" class="px-2.5 py-2 align-middle text-right font-mono font-bold text-emerald-800 dark:text-emerald-400 text-[11px] border-r border-slate-200 dark:border-[var(--border)] whitespace-nowrap">$${ep.cost_usd.toFixed(2)}</td><td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]">${stagesHtml}</td><td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]">${modelsHtml}</td><td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center font-mono text-[9px] text-black dark:text-gray-400 font-medium leading-tight border-r border-slate-200 dark:border-[var(--border)] whitespace-nowrap"><div>${ep.created_at}</div><div class="text-[8px] text-slate-800 dark:text-gray-500">Upd: ${ep.updated_at}</div></td>`;
      }
      rowHtml += `<td class="px-2 py-1.5 text-center"><div class="flex items-center gap-1 justify-center"><button onclick="playEditionVideo('${ed.url}', '${ep.episode_id}', '${ed.name}')" class="p-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[10px]" title="Play"><i class="fa-solid fa-play text-[9px]"></i></button><button onclick="openScriptModal('${ep.episode_id}')" class="p-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-[10px]" title="Script"><i class="fa-solid fa-scroll text-[9px]"></i></button><button onclick="openChannelEpisodeInspector('${ep.episode_id}'); switchInspectorTab('youtube');" class="p-1 bg-red-600 hover:bg-red-500 text-white rounded text-[10px]" title="YouTube"><i class="fa-brands fa-youtube text-[9px]"></i></button></div></td></tr>`;
      rowsHtml.push(rowHtml);
    });
  });
  tbody.innerHTML = rowsHtml.join("");
}

document.addEventListener("DOMContentLoaded", () => {
  fetchUserChannels();
  fetchChannelHubVideos();
});
