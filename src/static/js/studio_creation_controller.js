// CineAI Studio: Panel 1 Creation Hub Controller (New Production & Channel Archive)
let activeCreationTab = "new";
let channelArchiveEpisodes = [];

function switchCreationTab(tabKey) {
  activeCreationTab = tabKey;
  const btnNew = document.getElementById("btn-tab-creation-new"), btnArch = document.getElementById("btn-tab-creation-archive");
  const viewNew = document.getElementById("view-creation-new"), viewArch = document.getElementById("view-creation-archive");

  if (btnNew) btnNew.classList.toggle("active", tabKey === "new");
  if (btnArch) btnArch.classList.toggle("active", tabKey === "archive");

  if (tabKey === "new") {
    if (viewNew) viewNew.classList.remove("hidden");
    if (viewArch) viewArch.classList.add("hidden");
    if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  } else {
    if (viewNew) viewNew.classList.add("hidden");
    if (viewArch) viewArch.classList.remove("hidden");
    fetchAndRenderChannelArchive();
  }
}

function syncGenreDropdownForChannel(channelSlug) {
  const gSelector = document.getElementById("studio-genre-selector");
  if (!gSelector) return;

  const genresDict = (typeof ALL_STUDIO_GENRES !== "undefined") ? ALL_STUDIO_GENRES : {};
  const channelGenres = (typeof DEFAULT_CHANNEL_GENRES !== "undefined") ? DEFAULT_CHANNEL_GENRES : {};

  let allowed = null;
  if (typeof cachedChannelProfiles !== "undefined" && cachedChannelProfiles[channelSlug]?.allowed_genres?.length) {
    allowed = cachedChannelProfiles[channelSlug].allowed_genres;
  } else if (typeof studioChannelMetas !== "undefined" && studioChannelMetas[channelSlug]?.allowed_genres?.length) {
    allowed = studioChannelMetas[channelSlug].allowed_genres;
  } else if (typeof studioChannelMetas !== "undefined" && studioChannelMetas[channelSlug]?.raw?.allowed_genres?.length) {
    allowed = studioChannelMetas[channelSlug].raw.allowed_genres;
  } else if (typeof studioChannelMetas !== "undefined" && studioChannelMetas[channelSlug]?.raw?.primary_genre) {
    allowed = [studioChannelMetas[channelSlug].raw.primary_genre];
  } else if (channelGenres[channelSlug]) {
    allowed = channelGenres[channelSlug];
  }

  const genresToShow = (allowed && allowed.length > 0 && channelSlug !== "all") ? allowed : Object.keys(genresDict);

  gSelector.innerHTML = genresToShow.map(k => {
    const label = genresDict[k] || k;
    return `<option value="${k}">${label}</option>`;
  }).join("");

  const first = genresToShow[0] || "relax/nature";
  gSelector.value = first;
  onGenreChange(first);
}

function onGenreChange(genreVal) {
  const subSelector = document.getElementById("studio-subgenre-selector");
  if (!subSelector) return;

  const subMap = (typeof STUDIO_SUBOPTIONS_MAP !== "undefined") ? STUDIO_SUBOPTIONS_MAP : {};
  const list = subMap[genreVal] || subMap["relax/nature"] || [];
  subSelector.innerHTML = list.map(item => `<option value="${item.val}">${item.label}</option>`).join("");
  
  updateArchetypeOptions(genreVal, subSelector.value);
  onSubGenreChange(subSelector.value);

  // Sync active channel BGM default
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  if (bgmToggle) {
    if (genreVal === "documentary" || genreVal === "relax/hearth") {
      bgmToggle.checked = (genreVal !== "relax/hearth" && genreVal !== "documentary");
    } else {
      bgmToggle.checked = true;
    }
  }
}

function updateArchetypeOptions(genreVal, subGenreVal) {
  const archSelector = document.getElementById("studio-archetype-selector");
  if (!archSelector) return;

  const archMap = (typeof STUDIO_ARCHETYPES_MAP !== "undefined") ? STUDIO_ARCHETYPES_MAP : {};
  const list = archMap[genreVal] || archMap["relax/nature"] || [];
  
  archSelector.innerHTML = list.map(item => `<option value="${item.val}">${item.label}</option>`).join("");
  
  if (subGenreVal && (subGenreVal.includes("bedroom") || subGenreVal.includes("cabin"))) {
    const match = list.find(x => x.val.includes("bedroom") || x.val.includes("cabin"));
    if (match) archSelector.value = match.val;
  } else {
    archSelector.value = list[0]?.val || "";
  }
  onArchetypeChange(archSelector.value);
}

function onSubGenreChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const gSelector = document.getElementById("studio-genre-selector");
  const genreVal = gSelector ? gSelector.value : "relax/nature";
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  
  const placeholders = (typeof STUDIO_SUBGENRE_PLACEHOLDERS !== "undefined") ? STUDIO_SUBGENRE_PLACEHOLDERS : {};
  if (promptInput && placeholders[val]) promptInput.placeholder = placeholders[val];

  updateArchetypeOptions(genreVal, val);

  if (val === "cozy_hearth") {
    if (typeof selectStudioChannel === "function") selectStudioChannel("silent_hearth");
  } else if (val === "cinematic_doc" || val === "volcano_arctic" || val === "ocean_depths") {
    if (bgmToggle) bgmToggle.checked = false;
    if (typeof selectStudioChannel === "function") selectStudioChannel("cineai_docs");
  }
}

function onArchetypeChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const hints = (typeof STUDIO_ARCHETYPE_HINTS !== "undefined") ? STUDIO_ARCHETYPE_HINTS : {};
  if (promptInput && hints[val]) promptInput.placeholder = hints[val];
}

function applyGenreNichePreset() {
  const gSelector = document.getElementById("studio-genre-selector");
  if (gSelector) {
    gSelector.value = "relax/nature";
    onGenreChange("relax/nature");
  }
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
      const cId = v.channelId || v.channel_id || "earth_serenade";
      const eId = v.id || v.episode_id;
      allMap.set(`${cId}_${eId}`, {
        episode_id: eId, channel_id: cId,
        title: v.title, story_topic: v.concept || v.story_topic || v.title,
        cost_usd: v.cost || v.cost_usd || 0.14, status: v.status || "completed",
        is_approved: Boolean(v.is_approved || v.approved),
        progress: v.progress || (v.status === "completed" ? 100 : (v.status === "processing" ? 50 : 15)),
        videoUrl: v.videoUrl || v.video_url, keyframes: v.keyframes || [], motion_clips: v.motion_clips || [], audio_stems: v.audio_stems || []
      });
    });
  }

  channelArchiveEpisodes.forEach(ep => {
    const key = `${ep.channel_id || "earth_serenade"}_${ep.episode_id}`;
    if (!allMap.has(key)) {
      allMap.set(key, { ...ep, is_approved: Boolean(ep.is_approved || ep.approved), status: "completed", progress: 100 });
    } else {
      const ex = allMap.get(key);
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

  const activeEpisode = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  const activeEpId = activeEpisode ? (activeEpisode.id || activeEpisode.episode_id) : null;
  const activeChannelId = activeEpisode ? (activeEpisode.channelId || activeEpisode.channel_id) : null;

  container.innerHTML = filtered.map(ep => {
    const isSel = activeEpId === ep.episode_id && activeChannelId === ep.channel_id;
    const isProc = (ep.status === "processing" || ep.status === "queued");
    const isApp = Boolean(ep.is_approved || ep.approved);
    const bCls = isSel ? "border-2 border-indigo-500 bg-indigo-50/60 dark:bg-indigo-950/40 ring-1 ring-indigo-500/30" : "border border-slate-200 dark:border-slate-800 hover:border-indigo-400 bg-slate-50 dark:bg-slate-950/80";
    const badge = isProc ? `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-blue-500/15 text-blue-700 dark:text-blue-400 border border-blue-500/30 font-bold animate-pulse"><i class="fa-solid fa-spinner fa-spin mr-0.5"></i> In Progress</span>` : (isApp ? `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 font-bold">✓ Approved</span>` : `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30 font-bold">⏳ Unapproved</span>`);
    const pBar = isProc ? `<div class="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1"><div class="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-300" style="width: ${ep.progress || 45}%"></div></div>` : "";
    return `<div onclick="selectArchiveEpisode('${ep.episode_id}', '${ep.channel_id}')" class="p-2 ${bCls} rounded-xl cursor-pointer transition space-y-1 group relative"><div class="flex items-center justify-between"><div class="flex items-center gap-1.5"><span class="font-mono font-bold text-xs text-indigo-600 dark:text-indigo-400">${ep.episode_id}</span><button type="button" onclick="event.stopPropagation(); deleteStudioEpisode('${ep.episode_id}', event, '${ep.channel_id}');" class="p-1 text-slate-400 hover:text-red-600 rounded transition" title="Delete Episode"><i class="fa-solid fa-trash-can text-[10px]"></i></button></div>${badge}</div><div class="font-bold text-slate-900 dark:text-white text-xs group-hover:text-indigo-600 dark:group-hover:text-indigo-300 truncate">${ep.title}</div><div class="text-[10px] text-slate-500 dark:text-gray-400 line-clamp-1">${ep.story_topic}</div>${pBar}</div>`;
  }).join("");
}

async function approveCurrentEpisode() {
  if (!currentActiveInspectorEpisode) return;
  const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
  if (!epId || epId === "NEW") return;
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const chSlug = currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : "earth_serenade");

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
        const v = findStudioEpisodeById(epId, chSlug);
        if (v) { v.is_approved = true; v.approved = true; }
      }
      const archEp = channelArchiveEpisodes.find(x => x.episode_id === epId && x.channel_id === chSlug);
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

function selectArchiveEpisode(epId, chId) {
  const ch = chId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  if (ch && ch !== "all" && typeof selectStudioChannel === "function" && selectedStudioChannel !== ch) selectStudioChannel(ch);
  let ep = (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) ? studioVideos.find(x => (x.id === epId || x.episode_id === epId) && (ch === "all" || (x.channelId || x.channel_id) === ch)) : null;
  if (!ep) ep = channelArchiveEpisodes.find(x => x.episode_id === epId && (ch === "all" || x.channel_id === ch));
  if (!ep) return;
  if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(ep);
  if (window.StudioBus) window.StudioBus.emit("episode:selected", ep);
  filterChannelArchive();
}

async function deleteStudioEpisode(epId, event, channelId) {
  if (event) event.stopPropagation();
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const vid = findStudioEpisodeById(epId, channelId);
  const chSlug = channelId || vid?.channelId || vid?.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : null);
  if (!chSlug) return;
  try {
    await fetch(`/api/production/episodes/${epId}?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "DELETE" });
  } catch (e) { console.warn("Delete episode request notice:", e); }
  if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
    const idx = studioVideos.findIndex(x => (x.id === epId || x.episode_id === epId) && (x.channelId || x.channel_id || "earth_serenade") === chSlug);
    if (idx >= 0) studioVideos.splice(idx, 1);
  }
  channelArchiveEpisodes = channelArchiveEpisodes.filter(x => x.episode_id !== epId || x.channel_id !== chSlug);
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
  filterChannelArchive();
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode && (currentActiveInspectorEpisode.id === epId || currentActiveInspectorEpisode.episode_id === epId) && (currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id) === chSlug) {
    if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  }
  if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Episode ${epId} deleted.`);
}

function deleteActiveInspectorEpisode() {
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
    if (epId && epId !== "NEW") deleteStudioEpisode(epId, null, currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id);
  }
}

if (window.StudioBus) {
  window.StudioBus.on("channel:changed", () => {
    if (activeCreationTab === "archive") filterChannelArchive();
  });
}
