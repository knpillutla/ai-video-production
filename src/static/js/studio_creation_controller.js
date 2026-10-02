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

function onGenreChange(genreVal) {
  const subSelector = document.getElementById("studio-subgenre-selector");
  if (!subSelector) return;

  const subOptions = {
    "relax/nature": [{ val: "alpine_nature", label: "🏔️ Alpine Nature & Mountain Sanctuaries (Swiss Alps)" }, { val: "glacial_fjord_lake", label: "🛶 Glacial Mirror Lakes & Fjords" }, { val: "temperate_forest", label: "🌲 Temperate Mossy Rainforest & Streams" }],
    "relax/rain": [{ val: "forest_rain", label: "🌧️ Forest River Rainfall & ASMR" }, { val: "veranda_rain", label: "🏡 Biophilic Glass Veranda Rain" }, { val: "droplet_ripples", label: "💧 Water Droplet Ripples & Lake Reflections" }],
    "relax/waterfall": [{ val: "waterfall_gorge", label: "🌊 Monumental Plunge Cataracts (Niagara / Iguazu)" }, { val: "tiered_cascade", label: "🏞️ Multi-Tiered Glacial Cascades (Plitvice)" }],
    "relax/hearth": [{ val: "cozy_hearth", label: "🔥 Open-Air Beach Campfire & Shoreline Hearth" }, { val: "stone_hearth", label: "🪵 Rustic Cabin Stone Fireplace" }],
    "relax/cozy": [{ val: "biophilic_living", label: "🪵 Biophilic Living Space & Terraces" }, { val: "rainy_patio", label: "☕ Rainy Garden Patio & Warm Hearth" }],
    "relax/healing": [{ val: "zen_healing", label: "🪷 Zen Temple Bamboo Grove & 432Hz Bells" }, { val: "lotus_pond", label: "🎋 Sacred Lotus Pond & Water Basin Flow" }],
    "relax/zen": [{ val: "zen_healing", label: "🪷 Zen Temple Bamboo Grove & 432Hz Bells" }, { val: "lotus_pond", label: "🎋 Sacred Lotus Pond & Water Basin Flow" }],
    "relax/ambient": [{ val: "ambient_soundscape", label: "🌌 Velvet Ambient World (14 Ecosystems)" }, { val: "twilight_sanctuary", label: "✨ Twilight Aurora & Velvet Night Sky" }],
    "documentary": [{ val: "cinematic_doc", label: "🦅 BBC-Style 24fps Wildlife & Climate Expedition" }, { val: "volcano_arctic", label: "🌋 Volcanic Landscapes & Glacial Ice" }, { val: "ocean_depths", label: "🐋 Deep Marine Life & Coral Reefs" }],
    "travel_walking": [{ val: "alpine_village_walk", label: "🏡 Swiss Alpine Countryside Walk (1.5 km/h)" }, { val: "city_walk_pov", label: "🏙️ 4K 60fps Historic City & Night Walk" }, { val: "coastal_promenade", label: "🏖️ Secluded Ocean Bluff Walk" }],
    "dance/folk": [{ val: "mass_folk_dance", label: "💃 High-Energy Mass Folk Dance (30fps)" }, { val: "classical_dance", label: "🪘 Cultural Classical Choreography" }],
    "comedy/satire": [{ val: "satirical_short", label: "🎭 Modern Satire & Relatable Comedy Short" }]
  };

  const list = subOptions[genreVal] || subOptions["relax/nature"];
  subSelector.innerHTML = list.map(item => `<option value="${item.val}">${item.label}</option>`).join("");
  onSubGenreChange(subSelector.value);

  // Sync active channel chip & default stems
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  if (genreVal === "documentary") {
    if (bgmToggle) bgmToggle.checked = false;
    if (typeof selectStudioChannel === "function") selectStudioChannel("cineai_docs");
  } else if (genreVal === "relax/hearth") {
    if (typeof selectStudioChannel === "function") selectStudioChannel("silent_hearth");
  } else if (genreVal === "comedy/satire") {
    if (typeof selectStudioChannel === "function") selectStudioChannel("telugu_comedy");
  } else if (typeof selectStudioChannel === "function") {
    if (bgmToggle) bgmToggle.checked = true;
    if (typeof selectedStudioChannel !== "undefined" && ["silent_hearth", "cineai_docs", "telugu_comedy"].includes(selectedStudioChannel)) {
      selectStudioChannel("earth_serenade");
    }
  }
}

function onSubGenreChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const archSelector = document.getElementById("studio-archetype-selector");
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  
  const placeholders = {
    alpine_nature: "e.g. Majestic Swiss Alps panoramic peaks, wildflower valley, and crystal glacial stream...",
    glacial_fjord_lake: "e.g. Glassy mirror-still turquoise glacial lake reflecting towering forested cliffs...",
    temperate_forest: "e.g. Ancient mossy rainforest and gentle babbling river over rounded stones...",
    forest_rain: "e.g. Gentle rain falling on mossy temperate rainforest river and floating leaf ripples...",
    veranda_rain: "e.g. Biophilic glass veranda overlooking misty mountain forest during gentle twilight rainfall...",
    droplet_ripples: "e.g. Ultra-macro 4K raindrops creating concentric ripples on mirror-still mountain pond...",
    waterfall_gorge: "e.g. Monumental cascading cataract with heavy rising mist and turquoise plunge pool...",
    tiered_cascade: "e.g. Multi-tiered emerald forest cascades flowing gently over moss-covered limestone ledges...",
    cozy_hearth: "e.g. Gentle night rain on cozy stone campfire burning on wet pebble beach by ocean surf...",
    stone_hearth: "e.g. Glowing cedar log hearth in rustic mountain stone lodge with snowy forest view...",
    biophilic_living: "e.g. Modern biophilic living terrace with warm glowing fire and lush interior plants...",
    rainy_patio: "e.g. Cozy sheltered patio with amber lanterns and rain pattering softly on foliage...",
    zen_healing: "e.g. Tranquil Kyoto bamboo grove, stone lanterns, and soothing 432Hz meditation soundscape...",
    lotus_pond: "e.g. Sacred Kyoto temple lotus pond with blooming water lilies and gentle bamboo fountain...",
    ambient_soundscape: "e.g. Majestic 4K nature living wallpaper with tranquil mountain valley morning glow...",
    twilight_sanctuary: "e.g. Ethereal twilight mountain sanctuary under soft purple skies and velvet stars...",
    cinematic_doc: "e.g. BBC-style 24fps cinematic wildlife documentary across rugged alpine peaks...",
    volcano_arctic: "e.g. Dramatic volcanic black sand coast meets glacial blue ice caves...",
    ocean_depths: "e.g. Deep marine coral reefs with schools of luminous fish in crystal blue waters...",
    alpine_village_walk: "e.g. Ultra-slow 1.5 km/h human walking tour through Swiss alpine village and meadow path...",
    city_walk_pov: "e.g. 4K 60fps tranquil historic European cobblestone street walk at twilight...",
    mass_folk_dance: "e.g. High-energy festive village celebration with dynamic troupe choreography...",
    satirical_short: "e.g. Relatable everyday comedy satire with sharp comedic timing and witty dialogue..."
  };

  if (promptInput && placeholders[val]) promptInput.placeholder = placeholders[val];

  if (archSelector) {
    if (["waterfall_gorge", "tiered_cascade"].includes(val)) archSelector.value = "waterfall_gorge";
    else if (["alpine_nature", "alpine_village_walk"].includes(val)) archSelector.value = "alpine_mountains";
    else if (["cozy_hearth", "stone_hearth"].includes(val)) archSelector.value = "coastal_ocean";
    else if (["zen_healing", "lotus_pond"].includes(val)) archSelector.value = "zen_garden";
    else if (["forest_rain", "veranda_rain", "biophilic_living", "rainy_patio"].includes(val)) archSelector.value = "temperate_forest";
    else if (["glacial_fjord_lake", "droplet_ripples"].includes(val)) archSelector.value = "glacial_fjord_lake";
  }

  if (val === "cozy_hearth") {
    if (typeof selectStudioChannel === "function") selectStudioChannel("silent_hearth");
  } else if (val === "cinematic_doc" || val === "volcano_arctic" || val === "ocean_depths") {
    if (bgmToggle) bgmToggle.checked = false;
    if (typeof selectStudioChannel === "function") selectStudioChannel("cineai_docs");
  }
}

function onArchetypeChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const hints = {
    alpine_mountains: "e.g. Towering Swiss Alps snow-capped jagged peaks, lush wildflower meadows, and crystal mountain stream...",
    waterfall_gorge: "e.g. Colossal plunging waterfall wall with roaring turquoise basin and dense vapor mist...",
    coastal_ocean: "e.g. Open-air natural pebble beach shore with glowing campfire logs and rolling ocean surf...",
    glacial_fjord_lake: "e.g. Glassy mirror-still turquoise glacial lake reflecting towering forested mountain cliffs...",
    temperate_forest: "e.g. Ancient mossy rainforest and gentle babbling river over rounded river stones...",
    zen_garden: "e.g. Serene Japanese bamboo grove, stone lanterns, and floating lotus blossoms..."
  };
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
