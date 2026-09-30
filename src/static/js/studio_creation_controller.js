// CineAI Studio: Panel 1 Creation Hub Controller (New Production & Channel Archive)
let activeCreationTab = "new";
let channelArchiveEpisodes = [];

function switchCreationTab(tabKey) {
  activeCreationTab = tabKey;
  const btnNew = document.getElementById("btn-tab-creation-new"), btnArch = document.getElementById("btn-tab-creation-archive");
  const viewNew = document.getElementById("view-creation-new"), viewArch = document.getElementById("view-creation-archive");

  if (tabKey === "new") {
    if (btnNew) btnNew.className = "px-2.5 py-0.5 text-[10px] font-bold rounded-lg transition bg-indigo-600 text-white shadow flex items-center gap-1";
    if (btnArch) btnArch.className = "px-2.5 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1";
    if (viewNew) viewNew.classList.remove("hidden");
    if (viewArch) viewArch.classList.add("hidden");
    if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  } else {
    if (btnNew) btnNew.className = "px-2.5 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center gap-1";
    if (btnArch) btnArch.className = "px-2.5 py-0.5 text-[10px] font-bold rounded-lg transition bg-indigo-600 text-white shadow flex items-center gap-1";
    if (viewNew) viewNew.classList.add("hidden");
    if (viewArch) viewArch.classList.remove("hidden");
    fetchAndRenderChannelArchive();
  }
}

function switchNicheGroupView(groupKey) {
  const relGrid = document.getElementById("niche-subgrid-relaxation"), docGrid = document.getElementById("niche-subgrid-docs"), cadContainer = document.getElementById("relaxation-cadence-container");
  if (relGrid) relGrid.classList.toggle("hidden", groupKey !== "relaxation");
  if (docGrid) docGrid.classList.toggle("hidden", groupKey !== "docs");
  if (cadContainer) cadContainer.classList.toggle("hidden", groupKey !== "relaxation");
  const radios = document.querySelectorAll("input[name='niche_group_switch']");
  radios.forEach(r => { if (r.value === groupKey) r.checked = true; });
  if (typeof updateDurationOptionsForNiche === "function") updateDurationOptionsForNiche(groupKey);
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
  if (typeof selectNicheRadio === "function") selectNicheRadio(nicheKey);
  const cadRadios = document.querySelectorAll("input[name='studio_shot_hold']");
  cadRadios.forEach(r => { r.checked = (r.value === "3m"); });
}

async function fetchAndRenderChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  if (!container) return;

  try {
    const res = await fetch("/api/channels/episodes");
    const data = await res.json();
    if (data.status === "ok" && Array.isArray(data.episodes)) {
      channelArchiveEpisodes = data.episodes;
    }
  } catch (e) {
    console.warn("Could not fetch channel archive:", e);
  }

  filterChannelArchive();
}

function filterChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  const badgeCount = document.getElementById("channel-archive-badge-count");
  if (!container) return;

  const search = (document.getElementById("archive-filter-search")?.value || "").toLowerCase().trim();
  const ch = typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "all";

  const allMap = new Map();
  if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
    studioVideos.forEach(v => {
      allMap.set(v.id, {
        episode_id: v.id, channel_id: v.channelId || "earth_serenade",
        title: v.title, story_topic: v.concept || v.title,
        cost_usd: v.cost || 0.14, status: v.status || "completed",
        is_approved: Boolean(v.is_approved || v.approved),
        progress: v.progress || (v.status === "completed" ? 100 : (v.status === "processing" ? 50 : 15)),
        videoUrl: v.videoUrl, keyframes: v.keyframes || [], motion_clips: v.motion_clips || [], audio_stems: v.audio_stems || []
      });
    });
  }

  channelArchiveEpisodes.forEach(ep => {
    if (!allMap.has(ep.episode_id)) {
      allMap.set(ep.episode_id, { ...ep, is_approved: Boolean(ep.is_approved || ep.approved), status: "completed", progress: 100 });
    } else {
      const ex = allMap.get(ep.episode_id);
      if (ep.is_approved || ep.approved) ex.is_approved = true;
    }
  });

  const allEpisodes = Array.from(allMap.values());
  const filtered = allEpisodes.filter(ep => {
    if (ch !== "all" && ep.channel_id !== ch) return false;
    if (search) {
      const match = [ep.title, ep.episode_id, ep.story_topic].some(s => (s || "").toLowerCase().includes(search));
      if (!match) return false;
    }
    return true;
  });

  if (badgeCount) badgeCount.textContent = filtered.length;

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-xs text-gray-500 bg-slate-50 dark:bg-slate-950/40 rounded-xl border border-dashed border-[var(--border)]">No productions found for this channel.</div>`;
    return;
  }

  const activeEpId = (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) ? (currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id) : null;

  container.innerHTML = filtered.map(ep => {
    const isSelected = activeEpId === ep.episode_id;
    const isProcessing = (ep.status === "processing" || ep.status === "queued");
    const isApproved = Boolean(ep.is_approved || ep.approved);
    const progressVal = ep.progress || (isProcessing ? 45 : 100);
    const borderCls = isSelected ? "border-2 border-indigo-500 bg-indigo-50/60 dark:bg-indigo-950/40 ring-1 ring-indigo-500/30" : "border border-slate-200 dark:border-slate-800 hover:border-indigo-400 bg-slate-50 dark:bg-slate-950/80";

    let badge = "";
    if (isProcessing) {
      badge = `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-blue-500/15 text-blue-700 dark:text-blue-400 border border-blue-500/30 font-bold animate-pulse"><i class="fa-solid fa-spinner fa-spin mr-0.5"></i> In Progress</span>`;
    } else if (isApproved) {
      badge = `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 font-bold">✓ Approved</span>`;
    } else {
      badge = `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30 font-bold">⏳ Unapproved</span>`;
    }

    const progressBar = isProcessing
      ? `<div class="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1"><div class="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-300" style="width: ${progressVal}%"></div></div>`
      : "";

    return `
      <div onclick="selectArchiveEpisode('${ep.episode_id}')" class="p-2 ${borderCls} rounded-xl cursor-pointer transition space-y-1 group relative">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5">
            <span class="font-mono font-bold text-xs text-indigo-600 dark:text-indigo-400">${ep.episode_id}</span>
            <button type="button" onclick="event.stopPropagation(); deleteStudioEpisode('${ep.episode_id}', event);" class="p-1 text-slate-400 hover:text-red-600 rounded hover:bg-red-50 dark:hover:bg-red-950/50 transition" title="Delete Episode">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
            </button>
          </div>
          ${badge}
        </div>
        <div class="font-bold text-slate-900 dark:text-white text-xs group-hover:text-indigo-600 dark:group-hover:text-indigo-300 truncate">${ep.title}</div>
        <div class="text-[10px] text-slate-500 dark:text-gray-400 line-clamp-1">${ep.story_topic}</div>
        ${progressBar}
      </div>
    `;
  }).join("");
}

async function approveCurrentEpisode() {
  if (!currentActiveInspectorEpisode) return;
  const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
  if (!epId || epId === "NEW") return;
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : (currentActiveInspectorEpisode.channel_id || "earth_serenade");

  const btn = document.getElementById("btn-studio-approve");
  const btnTxt = document.getElementById("btn-studio-approve-text");
  if (btn) btn.disabled = true;
  if (btnTxt) btnTxt.textContent = "Approving...";

  try {
    const res = await fetch(`/api/production/episodes/${epId}/approve?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      currentActiveInspectorEpisode.is_approved = true;
      currentActiveInspectorEpisode.approved = true;
      if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
        const v = studioVideos.find(x => x.id === epId || x.episode_id === epId);
        if (v) { v.is_approved = true; v.approved = true; }
      }
      const archEp = channelArchiveEpisodes.find(x => x.episode_id === epId);
      if (archEp) { archEp.is_approved = true; archEp.approved = true; }
      if (typeof saveVideosState === "function") saveVideosState();
      if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(currentActiveInspectorEpisode);
      filterChannelArchive();
      if (typeof showProfileStatusToast === "function") showProfileStatusToast(`✓ Episode ${epId} approved successfully!`);
    }
  } catch (e) {
    console.error("Approve episode error:", e);
    if (btn) btn.disabled = false;
    if (btnTxt) btnTxt.textContent = "Approve Master Video";
  }
}

function selectArchiveEpisode(epId) {
  let ep = (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) ? studioVideos.find(x => x.id === epId) : null;
  if (!ep) ep = channelArchiveEpisodes.find(x => x.episode_id === epId);
  if (!ep) return;

  if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(ep);
  if (window.StudioBus) window.StudioBus.emit("episode:selected", ep);
  filterChannelArchive();
}

async function deleteStudioEpisode(epId, event) {
  if (event) event.stopPropagation();
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "earth_serenade";

  try {
    await fetch(`/api/production/episodes/${epId}?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "DELETE" });
  } catch (e) {
    console.warn("Delete episode request notice:", e);
  }

  if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
    const idx = studioVideos.findIndex(x => x.id === epId || x.episode_id === epId);
    if (idx >= 0) studioVideos.splice(idx, 1);
  }
  channelArchiveEpisodes = channelArchiveEpisodes.filter(x => x.episode_id !== epId);

  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
  filterChannelArchive();

  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode && (currentActiveInspectorEpisode.id === epId || currentActiveInspectorEpisode.episode_id === epId)) {
    if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  }

  if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Episode ${epId} deleted.`);
}

function deleteActiveInspectorEpisode() {
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
    if (epId && epId !== "NEW") deleteStudioEpisode(epId);
  }
}

if (window.StudioBus) {
  window.StudioBus.on("channel:changed", () => {
    if (activeCreationTab === "archive") filterChannelArchive();
  });
}
