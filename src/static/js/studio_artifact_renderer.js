// CineAI Studio: Artifact Section Renderers & Deletion Controller
let pendingDeleteAction = null;

function promptDeleteArtifact(type, idx, name, label) {
  pendingDeleteAction = () => executeArtifactDeletion(type, idx);
  const titleEl = document.getElementById("delete-confirm-title"), msgEl = document.getElementById("delete-confirm-message"), nameEl = document.getElementById("delete-confirm-artifact-name");
  if (titleEl) titleEl.textContent = `Delete ${label || type}`;
  if (msgEl) msgEl.textContent = `Are you sure you want to permanently delete this ${type.toLowerCase()} artifact?`;
  if (nameEl) nameEl.textContent = name || `${type} #${idx + 1}`;
  if (typeof openModal === "function") openModal("delete-confirm-modal");
}

function promptDeleteEpisode(epId, channelId, formatSlug, productionName, storagePath, title) {
  const normEpId = String(epId || "").trim().toUpperCase();
  const vid = (typeof findStudioEpisodeById === "function") ? findStudioEpisodeById(normEpId, channelId, formatSlug, productionName) : null;
  const effCh = channelId || vid?.channelId || vid?.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : "nature_rhythms");
  const effFmt = formatSlug || vid?.format || vid?.format_slug || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "Documentary");
  const effProd = productionName || vid?.production_name || "Standalone";
  const effTitle = title || vid?.title || vid?.story_topic || `Episode ${normEpId}`;
  const effPath = storagePath || vid?.storage_path || vid?.storagePath || "";

  pendingDeleteAction = () => executeDeleteEpisodeAction(normEpId, effCh, effFmt, effProd, effPath);

  const titleEl = document.getElementById("delete-confirm-title");
  const msgEl = document.getElementById("delete-confirm-message");
  const fmtEl = document.getElementById("delete-confirm-format");
  const prodEl = document.getElementById("delete-confirm-production");
  const epEl = document.getElementById("delete-confirm-episode-id");
  const nameEl = document.getElementById("delete-confirm-artifact-name");

  if (titleEl) titleEl.textContent = "Confirm Episode Deletion";
  if (msgEl) msgEl.textContent = "Are you sure you want to permanently delete this episode from disk?";
  if (fmtEl) fmtEl.textContent = effFmt.charAt(0).toUpperCase() + effFmt.slice(1);
  if (prodEl) prodEl.textContent = effProd.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  if (epEl) epEl.textContent = normEpId;
  if (nameEl) nameEl.textContent = effTitle;

  if (typeof openModal === "function") openModal("delete-confirm-modal");
}

async function executeDeleteEpisodeAction(epId, channelId, formatSlug, productionName, storagePath) {
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const chSlug = channelId || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : null);
  const normEpId = String(epId || "").toLowerCase().trim();
  const normFmt = String(formatSlug || "").toLowerCase().trim();
  const normProd = String(productionName || "").toLowerCase().trim().replace(/\s+/g, "_");

  let url = `/api/production/episodes/${epId}?user_id=${encodeURIComponent(uEmail)}`;
  if (chSlug) url += `&channel_id=${encodeURIComponent(chSlug)}`;
  if (normFmt) url += `&format=${encodeURIComponent(normFmt)}`;
  if (normProd) url += `&production_name=${encodeURIComponent(normProd)}`;
  if (storagePath) url += `&storage_path=${encodeURIComponent(storagePath)}`;

  try {
    await fetch(url, { method: "DELETE" });
  } catch (e) {
    console.warn("Delete episode request notice:", e);
  }

  const matchesTarget = (x) => {
    if (!x) return false;
    const xId = String(x.id || x.episode_id || "").toLowerCase().trim();
    if (xId !== normEpId) return false;
    const xCh = String(x.channelId || x.channel_id || "").toLowerCase().trim();
    if (chSlug && chSlug !== "all" && xCh && xCh !== chSlug.toLowerCase()) return false;
    if (storagePath) {
      const xPath = String(x.storage_path || x.storagePath || "").replace(/\\/g, "/").toLowerCase();
      const targetPath = String(storagePath).replace(/\\/g, "/").toLowerCase();
      if (xPath && (xPath.includes(targetPath) || targetPath.includes(xPath))) return true;
    }
    if (normProd && normProd !== "standalone") {
      const xProd = String(x.production_name || "").toLowerCase().trim().replace(/[\s_-]+/g, "");
      const targetProd = normProd.replace(/[\s_-]+/g, "");
      if (xProd && targetProd && !xProd.includes(targetProd) && !targetProd.includes(xProd)) return false;
    }
    return true;
  };

  // Immediate optimistic update on active memory lists
  if (Array.isArray(studioVideos)) {
    studioVideos = studioVideos.filter(x => !matchesTarget(x));
  }
  if (typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
    channelArchiveEpisodes = channelArchiveEpisodes.filter(x => !matchesTarget(x));
  }
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
  if (typeof filterChannelArchive === "function") filterChannelArchive();

  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    if (matchesTarget(currentActiveInspectorEpisode)) {
      if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
    }
  }

  // Authoritative live sync from backend (guarantees UI reflects disk without browser reload)
  try {
    if (typeof syncChannelEpisodesFromBackend === "function") {
      await syncChannelEpisodesFromBackend();
    }
    if (typeof fetchAndRenderChannelArchive === "function") {
      await fetchAndRenderChannelArchive();
    }
  } catch (syncErr) {
    console.debug("Post-delete live sync notice:", syncErr);
  }

  if (typeof showProfileStatusToast === "function") {
    showProfileStatusToast(`✓ Episode ${epId} (${formatSlug || 'Episode'}) deleted.`);
  }
}

function closeDeleteConfirmModal() {
  if (typeof closeModal === "function") closeModal("delete-confirm-modal");
  pendingDeleteAction = null;
}

async function executeDeleteConfirmAction() {
  const action = pendingDeleteAction;
  closeDeleteConfirmModal();
  if (typeof action === "function") {
    await action();
  }
}

function executeArtifactDeletion(type, idx) {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  if (type === "Keyframe") {
    if (vid.keyframes) vid.keyframes.splice(idx, 1);
    if (vid.artifacts?.keyframes) vid.artifacts.keyframes.splice(idx, 1);
    vid.selectedKeyframeIds = (vid.keyframes || []).map((_, i) => i);
    renderKeyframesList(vid);
  } else if (type === "Motion") {
    if (vid.motion_clips) vid.motion_clips.splice(idx, 1);
    if (vid.artifacts?.motion_clips) vid.artifacts.motion_clips.splice(idx, 1);
    vid.selectedMotionClipIds = (vid.motion_clips || []).map((_, i) => i);
    renderMotionClipsList(vid);
  } else if (type === "Audio") {
    if (vid.audio_stems) vid.audio_stems.splice(idx, 1);
    if (vid.artifacts?.audio_stems) vid.artifacts.audio_stems.splice(idx, 1);
    renderAudioStemsList(vid);
  } else if (type === "Master") {
    if (vid.editions) vid.editions.splice(idx, 1);
    if (!vid.editions || vid.editions.length === 0) {
      const video = document.getElementById("studio-panel-video");
      if (video) { video.src = ""; video.pause(); }
      document.getElementById("studio-panel-empty-overlay")?.classList.remove("hidden");
    }
    renderMasterVideosList(vid);
  }
  if (typeof updateStageGateDock === "function") updateStageGateDock(vid);
  if (typeof saveVideosState === "function") saveVideosState();
  if (typeof showProfileStatusToast === "function") showProfileStatusToast(`${type} deleted.`);
}

function renderMasterVideosList(vid) {
  const c = document.getElementById("panel-section-master-videos");
  if (!c) return;
  const epId = vid?.id || vid?.episode_id || "EP-001";
  const dur = vid?.duration || (vid?.durationSeconds ? `${vid.durationSeconds}s` : "5s");
  const cleanUrl = (u) => (u && typeof u === "string" && !u.includes("preview_master") && !u.includes("placeholder")) ? u : "";
  const masterUrl = cleanUrl(vid?.videoUrl || vid?.video_url || (vid?.editions && vid.editions[0]?.url) || vid?.artifacts?.master_video || "");
  const natureUrl = cleanUrl(vid?.nature_video_url || (vid?.editions && vid.editions.find(e => e.edition_id === "master_nature")?.url) || "");

  let eds = (vid?.editions && vid.editions.length > 0) ? [...vid.editions] : [];
  eds = eds.filter(e => !e.format?.includes("Long-Play") && !e.edition_id?.includes("h_") && !e.name?.includes("Hour") && cleanUrl(e.url));

  const isProc = vid?.status === "processing";
  const stage = vid?.currentStage || 1;
  const isMasterGenerating = Boolean(isProc && stage >= 5);

  const isMasterReady = Boolean(
    vid &&
    !isMasterGenerating &&
    vid.status !== "failed" &&
    (vid.currentStage >= 5 || (vid.status === "completed" && (masterUrl || eds.length > 0))) &&
    (masterUrl || eds.length > 0)
  );

  // CASE 1: Actively Rendering 4K Master -> Glowing Progress Bar
  if (isMasterGenerating) {
    const pVal = Math.min(95, vid.progress || 90);
    c.innerHTML = `<div class="col-span-2 p-2 bg-emerald-50/80 dark:bg-slate-900 border-2 border-emerald-500 rounded-xl flex flex-col justify-between shadow-sm gap-1.5 ring-2 ring-emerald-500/20">
      <div class="flex items-center justify-between">
        <span class="text-[9px] font-mono font-bold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5">
          <i class="fa-solid fa-spinner fa-spin text-[8px]"></i> Assembling Single-Pass 4K Master...
        </span>
        <span class="text-[8px] font-mono font-bold text-emerald-600 dark:text-emerald-400">${pVal}%</span>
      </div>
      <div class="w-full bg-emerald-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full animate-pulse" style="width: ${pVal}%"></div>
      </div>
    </div>`;
    return;
  }

  if (eds.length === 0 && masterUrl && isMasterReady) {
    eds.push({
      edition_id: "master_music",
      name: `🎵 4K Broadcast Master (${dur})`,
      label: `4K UHD Master`,
      format: "4K Master",
      duration: dur,
      url: masterUrl
    });
  }

  // CASE 2: Not yet ready -> Waiting for Approval or Queued
  if (!isMasterReady || eds.length === 0) {
    const rawMot = (vid?.motion_clips && vid.motion_clips.length > 0) ? vid.motion_clips : (vid?.artifacts?.motion_clips || []);
    const rawStems = (vid?.audio_stems && vid.audio_stems.length > 0) ? vid.audio_stems : (vid?.artifacts?.audio_stems || []);
    const hasMot = Boolean(rawMot.length > 0);
    const hasStems = Boolean(rawStems.length > 0);
    if (!isProc && hasMot && hasStems) {
      c.innerHTML = `<div class="col-span-2 p-1.5 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/40 dark:to-teal-950/40 border border-emerald-300 dark:border-emerald-600/50 rounded-xl flex items-center justify-between gap-1.5 shadow-sm">
        <div class="flex items-center gap-1.5"><i class="fa-solid fa-crown text-emerald-600 dark:text-emerald-400 text-xs"></i><div class="flex flex-col"><span class="text-[9px] font-bold text-emerald-950 dark:text-white">Motion &amp; Audio Ready</span><span class="text-[7px] text-emerald-700 dark:text-emerald-300">Ready for Stage 5 4K Master render</span></div></div>
        <button type="button" onclick="advanceToMasterStage(currentActiveInspectorEpisode)" class="px-2 py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95"><i class="fa-solid fa-circle-check text-[7px]"></i><span>Approve &amp; Render 4K Master ➔</span></button>
      </div>`;
    } else if (isProc && stage <= 4) {
      c.innerHTML = `<div class="col-span-2 h-9 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-2 shadow-sm"><i class="fa-solid fa-hourglass-half text-amber-500 text-xs"></i><span class="text-[9px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 5 4K Master</span><span class="text-[7px] text-slate-400 font-mono">(Starts after Motion clips &amp; Audio stems approved)</span></div>`;
    } else {
      c.innerHTML = `<div class="col-span-2 h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-2 shadow-sm"><i class="fa-solid fa-crown text-slate-400 text-xs"></i><span class="text-[9px] font-bold text-slate-700 dark:text-slate-300">No Master Video Yet</span><span class="text-[7px] text-slate-500 font-mono">(Renders in Stage 5)</span></div>`;
    }
    return;
  }

  // CASE 3: Master Videos Ready -> Show with Re-render and Play controls
  const posterUrl = vid.thumbnailUrl || vid.thumbnail_url || (vid.keyframes?.[0]?.url) || (vid.artifacts?.keyframes?.[0]?.url) || "";
  const bgStyle = posterUrl ? `background-image: url('${posterUrl}'); background-size: cover; background-position: center;` : "";
  const activeVideoEl = document.getElementById("studio-panel-video");
  const activeSrc = activeVideoEl?.src || "";

  c.innerHTML = eds.map((ed, i) => {
    const isAct = (activeSrc && activeSrc.includes(ed.url)) || (!activeSrc && i === 0);
    const borderCls = isAct ? "border-2 border-emerald-500 shadow-emerald-500/20 shadow-sm ring-1 ring-emerald-500/30" : "border border-slate-300 dark:border-slate-700 hover:border-emerald-400";
    const modeBadge = ed.audio_mode || (ed.edition_id === 'master_nature' ? '🌊 Pure Nature' : '🎵 Ambient BGM');

    return `
    <div class="flex flex-col items-center gap-0.5 cursor-pointer w-full group" onclick="selectMasterVideoRender('${ed.url}', '${ed.label || ed.name}', this); if (typeof openVideoPopup === 'function') openVideoPopup('${ed.url}', '${epId}: ${ed.name}', '${ed.format || '4K Master'} • Lossless Single-Pass');" title="Click to play ${ed.name}">
      <div class="relative w-full h-11 rounded-lg overflow-hidden bg-gradient-to-br from-emerald-950 to-slate-900 ${borderCls} transition flex flex-col justify-between p-1" style="${bgStyle}">
        ${posterUrl ? '<div class="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition pointer-events-none"></div>' : ''}
        <div class="relative z-10 flex items-center justify-between">
          <span class="px-1 py-0.2 rounded bg-emerald-900/90 text-[7px] font-mono font-bold text-emerald-200">${ed.format || '4K Master'}</span>
          <div class="flex items-center gap-0.5">
            <button type="button" onclick="event.stopPropagation(); advanceToMasterStage(currentActiveInspectorEpisode, true);" class="px-1 py-0.2 rounded bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render 4K Master Assembly">⚡ Re-render</button>
            <span class="px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-emerald-300">${ed.duration || dur}</span>
            <button type="button" onclick="event.stopPropagation(); promptDeleteArtifact('Master', ${i}, '${ed.name}', 'Master Edition');" class="w-3.5 h-3.5 rounded bg-rose-600/90 hover:bg-rose-500 text-white flex items-center justify-center text-[7px] transition shadow font-bold" title="Delete Master Edition">✕</button>
          </div>
        </div>
        <div class="relative z-10 flex items-center justify-between">
          <span class="text-[7px] font-mono font-bold text-white bg-black/70 px-1 py-0.2 rounded truncate max-w-[85px]">${modeBadge}</span>
          <div class="w-4 h-4 rounded-full bg-emerald-600/90 group-hover:bg-emerald-500 text-white flex items-center justify-center text-[6px] shadow"><i class="fa-solid fa-play ml-0.5"></i></div>
        </div>
      </div>
      <span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center">${ed.name}</span>
    </div>`;
  }).join("");
}

function renderScriptSection(vid) {
  const c = document.getElementById("panel-section-script");
  const btnView = document.getElementById("btn-view-script-drawer");
  const btnJson = document.getElementById("btn-view-screenplay-json");
  const statusEl = document.getElementById("panel-script-status");
  if (!c) return;

  const isProc = vid?.status === "processing";
  const stage = vid?.currentStage || 1;
  const scriptObj = vid?.screenplay || vid?.script;
  const hasScript = Boolean(
    (scriptObj && (scriptObj.scenes?.length > 0 || scriptObj.title || scriptObj.story_topic)) ||
    (vid?.stages_completed?.script === true) ||
    (stage > 1) ||
    (vid?.keyframes && vid.keyframes.length > 0)
  );
  const isSynthesizingScript = Boolean(isProc && !hasScript && stage <= 1);

  if (btnView) btnView.classList.add("hidden");
  if (btnJson) btnJson.classList.add("hidden");

  // CASE 1: Actively Synthesizing Script -> Glowing Progress Bar (Only during Stage 1)
  if (isSynthesizingScript) {
    if (statusEl) {
      statusEl.textContent = "Synthesizing...";
      statusEl.className = "text-amber-500 font-mono text-[9px] animate-pulse font-bold";
    }
    const pVal = Math.min(90, vid.progress || 25);
    c.innerHTML = `
    <div class="h-9 bg-amber-50/70 dark:bg-amber-950/30 border-2 border-amber-500/80 rounded-xl flex items-center justify-between px-3 shadow-sm gap-2">
      <div class="flex items-center gap-2 min-w-0">
        <div class="w-3.5 h-3.5 rounded-full border-2 border-amber-500 border-t-transparent animate-spin shrink-0"></div>
        <span class="text-[9px] font-bold text-amber-700 dark:text-amber-400 truncate">Synthesizing Gemini 2.5 Director Storyboard...</span>
      </div>
      <div class="w-24 bg-amber-200/60 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden shrink-0">
        <div class="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full animate-pulse" style="width: ${pVal}%"></div>
      </div>
    </div>`;
    return;
  }

  // CASE 2: Generated -> Compact Row with Title Snippet on Left + Only Icons on Right
  if (hasScript) {
    if (statusEl) {
      statusEl.textContent = "Ready";
      statusEl.className = "text-emerald-600 dark:text-emerald-400 font-mono text-[9px] font-bold";
    }
    const title = scriptObj.title || vid?.title || "Director Storyboard";

    c.innerHTML = `
    <div class="h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-between px-2.5 shadow-sm gap-2">
      <div class="flex items-center gap-1.5 min-w-0 flex-1 cursor-pointer" onclick="openScriptDrawer('visual')" title="Click to open Director Storyboard & Prompts">
        <i class="fa-solid fa-scroll text-amber-500 text-xs shrink-0"></i>
        <span class="text-[9px] font-bold text-slate-900 dark:text-gray-200 truncate hover:text-indigo-600 dark:hover:text-indigo-400 transition">${title}</span>
      </div>
      <div class="flex items-center gap-1 shrink-0">
        <button type="button" onclick="openScriptDrawer('visual')" class="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 hover:bg-indigo-100 dark:hover:bg-indigo-900/80 text-indigo-700 dark:text-indigo-300 border border-indigo-300 dark:border-indigo-700/60 flex items-center justify-center transition shadow-sm active:scale-95" title="View Visual Storyboard & Scene Prompts">
          <i class="fa-solid fa-note-sticky text-indigo-500 text-[10px]"></i>
        </button>
        <button type="button" onclick="openScriptDrawer('screenplay_json')" class="w-7 h-7 rounded-lg bg-amber-50 dark:bg-amber-950/60 hover:bg-amber-100 dark:hover:bg-amber-900/80 text-amber-700 dark:text-amber-300 border border-amber-300 dark:border-amber-700/60 flex items-center justify-center transition shadow-sm active:scale-95" title="View screenplay.json (Gemini Director Lore)">
          <i class="fa-solid fa-file-code text-amber-500 text-[10px]"></i>
        </button>
        <button type="button" onclick="openScriptDrawer('pipeline_json')" class="w-7 h-7 rounded-lg bg-purple-50 dark:bg-purple-950/60 hover:bg-purple-100 dark:hover:bg-purple-900/80 text-purple-700 dark:text-purple-300 border border-purple-300 dark:border-purple-700/60 flex items-center justify-center transition shadow-sm active:scale-95" title="View pipeline_state.json">
          <i class="fa-solid fa-gears text-purple-500 text-[10px]"></i>
        </button>
        <button type="button" onclick="openScriptDrawer('inputs_json')" class="w-7 h-7 rounded-lg bg-emerald-50 dark:bg-emerald-950/60 hover:bg-emerald-100 dark:hover:bg-emerald-900/80 text-emerald-700 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700/60 flex items-center justify-center transition shadow-sm active:scale-95" title="View user_inputs.json">
          <i class="fa-solid fa-sliders text-emerald-500 text-[10px]"></i>
        </button>
      </div>
    </div>`;
    return;
  }

  // CASE 3: Empty / Not yet synthesized
  if (statusEl) {
    statusEl.textContent = "Empty";
    statusEl.className = "text-slate-400 font-mono text-[9px]";
  }
  c.innerHTML = `
  <div class="h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-between px-3 text-slate-500 dark:text-slate-400 shadow-sm">
    <div class="flex items-center gap-1.5 min-w-0">
      <i class="fa-solid fa-file-lines text-slate-400 text-xs shrink-0"></i>
      <span class="text-[9px] font-medium text-slate-500 dark:text-gray-400 truncate">No Storyboard Synthesized Yet</span>
    </div>
    <span class="text-[8px] font-mono text-slate-400 shrink-0">(Gemini 2.5)</span>
  </div>`;
}

function renderKeyframesList(vid) {
  const c = document.getElementById("panel-section-images"), countEl = document.getElementById("panel-images-count");
  if (!c) return;
  const isProc = vid.status === "processing", isFailed = vid.status === "failed", stage = vid.currentStage || 1;
  const rawKfs = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : (vid.artifacts?.keyframes || []);
  const screenplaySceneCount = vid.screenplay?.scenes?.length || vid.script?.scenes?.length || vid.scenes?.length || 0;
  const requestedShotCount = parseInt(vid.numShots || vid.num_shots || 1, 10) || 1;
  const numShots = Math.max(screenplaySceneCount || requestedShotCount, rawKfs.length);
  const completedKfs = rawKfs.filter(kf => {
    const url = (typeof kf === "object") ? kf.url : kf;
    return url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
  });

  if (isFailed && (vid.failedStage === 1 || !rawKfs.length)) {
    if (countEl) countEl.textContent = "Error";
    c.innerHTML = `<div class="col-span-4 p-3 bg-white border-2 border-red-500 rounded-xl flex flex-col gap-2 shadow-md">
      <div class="flex items-center justify-between">
        <span class="text-xs font-black text-red-700 flex items-center gap-1.5"><i class="fa-solid fa-triangle-exclamation text-red-600"></i> Stage 1 Keyframe Error</span>
        <button type="button" onclick="retryEpisodeWithFallback('${vid.id || vid.episode_id}')" class="px-2.5 py-1 text-[10px] font-bold rounded-lg bg-red-600 hover:bg-red-700 text-white transition flex items-center gap-1 shadow-sm">🔄 Retry Fallback</button>
      </div>
      <div class="text-[11px] font-mono font-semibold text-red-600 leading-normal break-words">${vid.errorMessage || 'Keyframe synthesis failed.'}</div>
    </div>`;
    return;
  }

  const isGeneratingPhotos = Boolean(
    isProc && (stage === 2 || (vid.pipelineStrategy === "autonomous" && stage >= 2 && completedKfs.length < numShots))
  );

  if (countEl) {
    if (isGeneratingPhotos) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-900 dark:text-blue-200 font-bold font-mono text-[10px] border border-blue-300 dark:border-blue-700 animate-pulse inline-flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[8px]"></i>Generating ${completedKfs.length + 1}/${numShots}...</span>`;
    } else if (completedKfs.length > 0) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-900 dark:text-emerald-300 font-bold font-mono text-[10px] border border-emerald-300 dark:border-emerald-700 inline-flex items-center gap-1"><i class="fa-solid fa-check text-[8px]"></i>${completedKfs.length}/${numShots} Ready</span>`;
    } else if (isProc && stage === 1) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-amber-100 dark:bg-amber-950 text-amber-900 dark:text-amber-300 font-bold font-mono text-[10px] border border-amber-300 dark:border-amber-700">Queued</span>`;
    } else {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-bold font-mono text-[10px] border border-slate-300 dark:border-slate-700">${numShots} Shot${numShots > 1 ? 's' : ''}</span>`;
    }
  }

  // If Stage 1 is actively processing, photos are queued waiting for script approval
  if (isProc && stage === 1 && completedKfs.length === 0 && rawKfs.length === 0) {
    c.innerHTML = `<div class="col-span-4 h-9 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-2 shadow-sm"><i class="fa-solid fa-hourglass-half text-amber-500 text-xs"></i><span class="text-[9px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 2 Photos</span><span class="text-[7px] text-slate-400 font-mono">(Starts after Script approved)</span></div>`;
    return;
  }

  if (!isProc && completedKfs.length === 0 && rawKfs.length === 0) {
    const hasScript = Boolean(vid.script || vid.story_topic || vid.title || vid.screenplay);
    if (hasScript) {
      c.innerHTML = `<div class="col-span-4 p-1.5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/40 dark:to-indigo-950/40 border border-blue-300 dark:border-blue-600/50 rounded-xl flex items-center justify-between gap-1.5 shadow-sm">
        <div class="flex items-center gap-1.5"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><div class="flex flex-col"><span class="text-[9px] font-bold text-blue-950 dark:text-white">Stage 1 Script Ready</span><span class="text-[7px] text-blue-700 dark:text-blue-300">Choose image engine:</span></div></div>
        <div class="flex items-center gap-1">
          <button type="button" onclick="advanceToKeyframesStage(currentActiveInspectorEpisode, 'gemini', true)" class="px-1.5 py-1 bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-400 hover:to-emerald-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow-sm active:scale-95" title="Generate with Google Imagen 3 (Gemini)"><i class="fa-solid fa-sparkles text-[7px]"></i><span>Gemini (Imagen 3)</span></button>
          <button type="button" onclick="advanceToKeyframesStage(currentActiveInspectorEpisode, 'flux_dev', true)" class="px-1.5 py-1 bg-white dark:bg-slate-900 hover:bg-slate-100 text-slate-800 dark:text-gray-200 rounded-lg text-[8px] font-bold border border-slate-300 dark:border-slate-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Generate with FLUX.1-dev (Test Mode)"><i class="fa-solid fa-vial text-blue-500 text-[7px]"></i><span>Test (FLUX Dev)</span></button>
          <button type="button" onclick="advanceToKeyframesStage(currentActiveInspectorEpisode, 'zimage', true)" class="px-1.5 py-1 bg-amber-50 dark:bg-amber-950/50 hover:bg-amber-100 text-amber-900 dark:text-amber-200 rounded-lg text-[8px] font-bold border border-amber-300 dark:border-amber-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Generate with Z-Image Turbo (Sub-second)"><i class="fa-solid fa-bolt text-amber-500 text-[7px]"></i><span>Z-Image Turbo</span></button>
          <button type="button" onclick="advanceToKeyframesStage(currentActiveInspectorEpisode, 'flux_pro', true)" class="px-2 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Render with FLUX 1.1 Pro Ultra"><i class="fa-solid fa-wand-magic-sparkles text-[7px]"></i><span>Render with FLUX Pro (Prod) ➔</span></button>
        </div>
      </div>`;
    } else {
      c.innerHTML = `<div class="col-span-4 h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-2 shadow-sm"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><span class="text-[9px] font-bold text-slate-900 dark:text-white">No Keyframe Photos Yet</span><span class="text-[7px] text-slate-500 font-mono">(${numShots} Shot${numShots > 1 ? 's' : ''} via FLUX Dev / Pro / Z-Image)</span></div>`;
    }
    return;
  }

  const names = ["Shot 1: Wide", "Shot 2: Sensory", "Shot 3: Setting", "Shot 4: Twilight"];
  const epId = vid.id || vid.episode_id || "EP-001";
  if (!vid.selectedKeyframeIds) vid.selectedKeyframeIds = Array.from({ length: numShots }, (_, i) => i);
  const activeGenIdx = isGeneratingPhotos ? completedKfs.length : -1;
  const pVal = Math.min(95, vid.progress ? (vid.progress + 15) : 45);

  c.innerHTML = Array.from({ length: numShots }, (_, i) => {
    const existing = rawKfs[i];
    let url = existing ? ((typeof existing === "object") ? existing.url : existing) : null;
    const hasImage = url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
    const name = (existing && typeof existing === "object" && existing.name) ? existing.name : (names[i] || `Shot ${i + 1}`);
    const isSel = vid.selectedKeyframeIds.includes(i);

    const isThisKeyframeGenerating = Boolean(
      isGeneratingPhotos && !hasImage && (i === activeGenIdx || (numShots === 1 && isProc && stage === 2))
    );

    const activeImgLabel = (vid.imageModel && (vid.imageModel.includes("imagen") || vid.imageModel.includes("gemini"))) ? "Gemini Imagen 3" : ((vid.imageModel && (vid.imageModel.includes("pro") || vid.imageModel.includes("ultra"))) ? "FLUX Pro" : ((vid.imageModel && vid.imageModel.includes("zimage")) ? "Z-Image" : "FLUX Dev"));

    if (isThisKeyframeGenerating) {
      return `<div class="flex flex-col items-center gap-0.5 w-full"><div class="relative w-full h-12 rounded-lg bg-blue-50/80 dark:bg-slate-900 border-2 border-blue-500 shadow-sm flex flex-col justify-between p-1.5 ring-2 ring-blue-500/20"><div class="flex items-center justify-between w-full"><span class="text-[8px] font-mono font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> ${activeImgLabel}</span><span class="text-[7px] font-mono text-blue-600 dark:text-blue-400 font-bold">${pVal}%</span></div><div class="w-full bg-blue-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full animate-pulse" style="width: ${pVal}%"></div></div></div><span class="text-[8px] font-bold text-blue-600 dark:text-blue-400 truncate w-full text-center">${name}</span></div>`;
    }

    if (hasImage && (!vid.force_rerun || !isGeneratingPhotos)) {
      const liveUrl = url;
      const borderCls = isSel ? "border-2 border-emerald-500 ring-1 ring-emerald-500/50" : "border border-slate-300 dark:border-slate-800 opacity-40 grayscale";
      const clickAction = `openImagePopup('${liveUrl}', '${epId}: ${name}', '${activeImgLabel} • 4K UHD Keyframe Photo')`;
      return `<div class="flex flex-col items-center gap-0.5 w-full relative group"><div class="relative w-full h-12 rounded-lg overflow-hidden bg-white dark:bg-slate-900 ${borderCls} cursor-pointer transition shadow-sm" onclick="${clickAction}" title="Click to view photo in popup"><img src="${liveUrl}" alt="${name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300"><div class="absolute top-0.5 right-0.5 flex items-center gap-0.5 z-10"><button type="button" onclick="event.stopPropagation(); regenerateSingleKeyframe(currentActiveInspectorEpisode, ${i + 1}, 'gemini');" class="px-1 py-0.2 rounded bg-gradient-to-r from-teal-600 to-emerald-600 hover:from-teal-500 hover:to-emerald-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with Google Imagen 3 (Gemini)">⚡ Gemini</button><button type="button" onclick="event.stopPropagation(); regenerateSingleKeyframe(currentActiveInspectorEpisode, ${i + 1}, 'flux_pro');" class="px-1 py-0.2 rounded bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with FLUX 1.1 Pro Ultra">⚡ Pro</button><button type="button" onclick="event.stopPropagation(); regenerateSingleKeyframe(currentActiveInspectorEpisode, ${i + 1}, 'zimage');" class="px-1 py-0.2 rounded bg-gradient-to-r from-amber-600 to-yellow-600 hover:from-amber-500 hover:to-yellow-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with Z-Image Turbo">⚡ Z-Img</button><button type="button" onclick="event.stopPropagation(); promptDeleteArtifact('Keyframe', ${i}, '${name}', 'Keyframe Shot');" class="w-3.5 h-3.5 rounded bg-rose-600/90 hover:bg-rose-500 text-white flex items-center justify-center text-[7px] font-bold" title="Delete Keyframe">✕</button><button type="button" onclick="event.stopPropagation(); toggleKeyframeSelection(${i});" class="px-1 py-0.2 rounded bg-black/80 text-[7px] font-mono hover:bg-emerald-600 ${isSel ? 'text-emerald-300' : 'text-gray-400'}">${isSel ? '✓' : 'Off'}</button></div></div><span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate cursor-pointer" onclick="${clickAction}">${name}</span></div>`;
    }

    return `<div class="flex flex-col items-center gap-0.5 w-full opacity-60"><div class="relative w-full h-12 rounded-lg bg-slate-50 dark:bg-slate-950 border border-dashed border-slate-300 dark:border-slate-800 flex flex-col items-center justify-center p-1"><span class="text-[8px] font-mono text-slate-400 dark:text-slate-500 flex items-center gap-1"><i class="fa-solid fa-hourglass text-[7px]"></i> Queued</span></div><span class="text-[8px] text-slate-400 dark:text-slate-500 truncate w-full text-center">${name}</span></div>`;
  }).join("");
}

function renderMotionClipsList(vid) {
  const c = document.getElementById("panel-section-raw-videos"), countEl = document.getElementById("panel-raw-videos-count");
  if (!c) return;
  const isProc = vid.status === "processing", isFailed = vid.status === "failed", stage = vid.currentStage || 1;
  const numClips = parseInt(vid.numShots || vid.num_shots || 1, 10);
  const rawClips = (vid.motion_clips && vid.motion_clips.length > 0) ? vid.motion_clips : (vid.artifacts?.motion_clips || []);
  const defModel = (vid.motionModel === "wan" || vid.executionMode === "test" || vid.durationSeconds <= 10 || !vid.durationSeconds) ? "Wan 2.1" : "Kling v3";
  const completedClips = rawClips.filter(m => {
    const url = (typeof m === "object") ? m.url : m;
    return url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
  });

  if (isFailed && (vid.failedStage === 4 || (!rawClips.length && vid.failedStage !== 1 && vid.failedStage !== 2 && vid.failedStage !== 3))) {
    if (countEl) countEl.textContent = "Error";
    c.innerHTML = `<div class="col-span-3 p-3 bg-white dark:bg-slate-950 border-2 border-red-500 rounded-xl flex flex-col gap-2 shadow-md">
      <div class="flex items-center justify-between flex-wrap gap-1">
        <span class="text-xs font-black text-red-700 dark:text-red-400 flex items-center gap-1.5"><i class="fa-solid fa-triangle-exclamation text-red-600"></i> Video Motion Status / Timeout</span>
        <div class="flex items-center gap-1">
          <button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'ken_burns', true)" class="px-2.5 py-1 text-[10px] font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1 shadow-sm active:scale-95" title="Retry with Local 4K Perspective Drone ($0.00)"><i class="fa-solid fa-plane-up text-[8px]"></i> ⚡ Local Drone ($0)</button>
          <button type="button" onclick="reprocessActiveEpisodeId('${vid.id || vid.episode_id}', 'ken_burns', true)" class="px-2 py-1 text-[9px] font-bold rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition flex items-center gap-1 shadow-sm active:scale-95" title="Re-Synthesize (--id) — Resumes pipeline with Local Motion">Resume</button>
        </div>
      </div>
      <div class="text-[11px] font-mono font-semibold text-red-600 dark:text-red-400 leading-normal break-words">${vid.errorMessage || 'Video Diffusion in-progress or timed out.'}</div>
    </div>`;
    return;
  }

  const isGeneratingMotion = Boolean(
    isProc && (stage === 4 || (vid.pipelineStrategy === "autonomous" && stage >= 4 && (completedClips.length < numClips || vid.force_rerun)))
  );

  if (countEl) {
    if (isGeneratingMotion) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-purple-100 dark:bg-purple-950 text-purple-900 dark:text-purple-200 font-bold font-mono text-[10px] border border-purple-300 dark:border-purple-700 animate-pulse inline-flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[8px]"></i>Rendering ${completedClips.length + 1}/${numClips}...</span>`;
    } else if (completedClips.length > 0) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-950 text-emerald-900 dark:text-emerald-300 font-bold font-mono text-[10px] border border-emerald-300 dark:border-emerald-700 inline-flex items-center gap-1"><i class="fa-solid fa-check text-[8px]"></i>${completedClips.length}/${numClips} Ready</span>`;
    } else if (isProc && stage < 4) {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-bold font-mono text-[10px] border border-slate-300 dark:border-slate-700">Queued</span>`;
    } else {
      countEl.innerHTML = `<span class="px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 font-bold font-mono text-[10px] border border-slate-300 dark:border-slate-700">${numClips} Clip${numClips > 1 ? 's' : ''}</span>`;
    }
  }

  if (!isProc && completedClips.length === 0) {
    const rawStems = (vid.audio_stems && vid.audio_stems.length > 0) ? vid.audio_stems : (vid.artifacts?.audio_stems || []);
    const hasAudio = Boolean(rawStems.length > 0);
    const hasKfs = Boolean((vid.keyframes && vid.keyframes.length > 0) || (vid.artifacts?.keyframes && vid.artifacts.keyframes.length > 0));

    if (hasAudio) {
      const scenes = vid.screenplay?.scenes || vid.script?.scenes || vid.scenes || [];
      const shot1 = scenes[0] || {};
      const mType = (shot1.motion_type || shot1.motion || "").toLowerCase();
      const isLocalDroneShot = mType.includes("ken_burns") || mType.includes("local") || mType.includes("drone") || mType.includes("zoompan");

      const localBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'ken_burns', true)" class="px-1.5 py-1 ${isLocalDroneShot ? 'bg-emerald-600 text-white font-black shadow-md ring-2 ring-emerald-400/50' : 'bg-emerald-50 dark:bg-emerald-950/50 hover:bg-emerald-100 text-emerald-900 dark:text-emerald-200 border border-emerald-300 dark:border-emerald-700'} rounded-lg text-[8px] font-bold transition flex items-center gap-1 active:scale-95" title="Render with Local 4K Perspective Drone & Micro-Kinetics ($0.00)"><i class="fa-solid fa-plane-up ${isLocalDroneShot ? 'text-white' : 'text-emerald-600'} text-[7px]"></i><span>Local Drone ($0)</span></button>`;

      const minimaxBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'h3_max', true)" class="px-1.5 py-1 bg-teal-50 dark:bg-teal-950/50 hover:bg-teal-100 text-teal-900 dark:text-teal-200 rounded-lg text-[8px] font-bold border border-teal-300 dark:border-teal-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Render with MiniMax H3 Max Turbo (~$0.015/sec, Subtle Atmospheric)"><i class="fa-solid fa-wind text-teal-600 text-[7px]"></i><span>MiniMax H3</span></button>`;

      const wanBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'wan', true)" class="px-1.5 py-1 bg-white dark:bg-slate-900 hover:bg-slate-100 text-slate-800 dark:text-gray-200 rounded-lg text-[8px] font-bold border border-slate-300 dark:border-slate-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Test with Wan 2.1 1080p ($0.40)"><i class="fa-solid fa-vial text-amber-500 text-[7px]"></i><span>Wan 2.1</span></button>`;

      const wan4kBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'wan_4k', true)" class="px-1.5 py-1 bg-amber-50 dark:bg-amber-950/50 hover:bg-amber-100 text-amber-900 dark:text-amber-200 rounded-lg text-[8px] font-bold border border-amber-300 dark:border-amber-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Wan 2.1 + AI 4K Super-Resolution ($0.55)"><i class="fa-solid fa-wand-magic-sparkles text-amber-600 text-[7px]"></i><span>Wan 4K</span></button>`;

      const klingProBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'kling_pro', true)" class="px-1.5 py-1 bg-purple-50 dark:bg-purple-950/50 hover:bg-purple-100 text-purple-900 dark:text-purple-200 rounded-lg text-[8px] font-bold border border-purple-300 dark:border-purple-700 transition flex items-center gap-1 shadow-sm active:scale-95" title="Render with Kling 1.6 Pro ($0.95)"><i class="fa-solid fa-gem text-purple-600 text-[7px]"></i><span>Kling Pro</span></button>`;

      const kling4kBtn = `<button type="button" onclick="advanceToMotionStage(currentActiveInspectorEpisode, 'kling_v3', true)" class="px-2 py-1 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Render with Kling v3 4K Native ($1.40)"><i class="fa-solid fa-crown text-[7px]"></i><span>Kling v3 4K (Prod) ➔</span></button>`;

      c.innerHTML = `<div class="col-span-3 p-1.5 bg-gradient-to-r from-purple-50 to-indigo-50 dark:from-purple-950/40 dark:to-indigo-950/40 border border-purple-300 dark:border-purple-600/50 rounded-xl flex items-center justify-between gap-1.5 shadow-sm">
        <div class="flex items-center gap-1.5"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><div class="flex flex-col"><span class="text-[9px] font-bold text-purple-950 dark:text-white">Stage 3 Audio Ready</span><span class="text-[7px] text-purple-700 dark:text-purple-300">${isLocalDroneShot ? '🎬 Director locked to Local Drone' : 'Choose motion engine:'}</span></div></div>
        <div class="flex items-center gap-1 flex-wrap">
          ${localBtn}
          ${minimaxBtn}
          ${wanBtn}
          ${wan4kBtn}
          ${klingProBtn}
          ${kling4kBtn}
        </div>
      </div>`;
    } else if (hasKfs) {
      c.innerHTML = `<div class="col-span-3 h-9 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-2 shadow-sm"><i class="fa-solid fa-hourglass-half text-amber-500 text-xs"></i><span class="text-[9px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 4 Motion</span><span class="text-[7px] text-slate-400 font-mono">(Starts after Stage 3 Audio approved)</span></div>`;
    } else {
      c.innerHTML = `<div class="col-span-3 h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-2 shadow-sm"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><span class="text-[9px] font-bold text-slate-900 dark:text-white">No Motion Clips Yet</span><span class="text-[7px] text-slate-500 font-mono">(${defModel})</span></div>`;
    }
    return;
  }

  if (isProc && stage < 4 && !isGeneratingMotion) {
    c.innerHTML = `<div class="col-span-3 h-9 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-2 shadow-sm"><i class="fa-solid fa-hourglass-half text-amber-500 text-xs"></i><span class="text-[9px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 4 Motion</span><span class="text-[7px] text-slate-400 font-mono">(Starts after Stage 3 Audio approved)</span></div>`;
    return;
  }

  const epId = vid.id || vid.episode_id || "EP-001", dur = vid.duration || (vid.durationSeconds ? `${vid.durationSeconds}s` : "5s");
  if (!vid.selectedMotionClipIds) vid.selectedMotionClipIds = Array.from({ length: numClips }, (_, i) => i);
  const activeGenIdx = isGeneratingMotion ? (vid.force_rerun ? 0 : completedClips.length) : -1;
  const pVal = Math.min(95, vid.progress || 50);

  const scenes = vid.screenplay?.scenes || vid.script?.scenes || vid.scenes || [];

  c.innerHTML = Array.from({ length: numClips }, (_, i) => {
    const existing = rawClips[i];
    const url = existing ? ((typeof existing === "object") ? existing.url : existing) : null;
    const hasVid = url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
    const name = (existing && typeof existing === "object" && existing.name) ? existing.name : `Motion ${i + 1}`;
    let model = (existing && typeof existing === "object" && existing.model) ? existing.model : defModel;
    if (vid.motionModel) {
      if (vid.motionModel === "ken_burns" || vid.motionModel === "local_drone") model = "Local Drone";
      else if (vid.motionModel === "kling_v3" || vid.motionModel === "kling_4k") model = "Kling v3 4K";
      else if (vid.motionModel === "kling_pro" || vid.motionModel === "kling") model = "Kling Pro";
      else if (vid.motionModel === "wan_4k") model = "Wan 2.1 + 4K AI";
      else if (vid.motionModel.includes("wan")) model = "Wan 2.1";
    }
    const isSel = vid.selectedMotionClipIds.includes(i);

    const shotScene = scenes[i] || {};
    const shotMotionType = (shotScene.motion_type || shotScene.motion || "").toLowerCase();
    const isShotLocalDrone = shotMotionType.includes("ken_burns") || shotMotionType.includes("local") || shotMotionType.includes("drone") || shotMotionType.includes("zoompan");

    const isThisClipGenerating = Boolean(
      isGeneratingMotion && (!hasVid || vid.force_rerun) && (i === activeGenIdx || (numClips === 1 && isProc && stage === 4))
    );

    if (isThisClipGenerating) {
      const activeModelLabel = (vid.motionModel === "ken_burns" || vid.motionModel === "local_drone") ? "Local Drone ($0)" : ((vid.motionModel === "kling_v3" || vid.motionModel === "kling_4k") ? "Kling v3 4K" : ((vid.motionModel === "kling_pro" || vid.motionModel === "kling") ? "Kling Pro" : ((vid.motionModel === "wan_4k") ? "Wan 2.1 + 4K AI" : ((vid.motionModel && vid.motionModel.includes("wan")) ? "Wan 2.1" : model))));
      return `<div class="flex flex-col items-center gap-0.5 w-full"><div class="relative w-full h-11 rounded-lg bg-purple-50/80 dark:bg-slate-900 border-2 border-purple-500 shadow-sm flex flex-col justify-between p-1 ring-2 ring-purple-500/20"><div class="flex items-center justify-between w-full"><span class="text-[8px] font-mono font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> ${activeModelLabel}</span><span class="text-[7px] font-mono text-purple-600 dark:text-purple-400 font-bold">${pVal}%</span></div><div class="w-full bg-purple-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-purple-600 to-pink-500 rounded-full animate-pulse" style="width: ${pVal}%"></div></div></div><span class="text-[8px] font-bold text-purple-600 dark:text-purple-400 truncate w-full text-center">${name}</span></div>`;
    }

    if (hasVid && (!vid.force_rerun || !isGeneratingMotion)) {
      const borderCls = isSel ? "border-2 border-purple-500" : "border border-slate-300 dark:border-slate-700";
      const kf = (vid.keyframes && vid.keyframes[i]) ? vid.keyframes[i] : (vid.artifacts?.keyframes?.[i] || null);
      const kfUrl = (typeof kf === "object" && kf !== null) ? kf.url : (typeof kf === "string" ? kf : "");
      const posterUrl = (kfUrl && (kfUrl.startsWith("http") || kfUrl.startsWith("/static/") || kfUrl.startsWith("/storage/"))) ? kfUrl : (vid.thumbnailUrl || vid.thumbnail_url || "");
      const bgStyle = posterUrl ? `background-image: url('${posterUrl}'); background-size: cover; background-position: center;` : "";
      const playAction = `selectMasterVideoRender('${url}', '${name} (${model})', this); if (typeof openVideoPopup === 'function') openVideoPopup('${url}', '${epId}: ${name}', '${model} • Raw Video Motion Clip');`;

      const cardLocalBtn = `<button type="button" onclick="event.stopPropagation(); regenerateSingleMotionClip(currentActiveInspectorEpisode, ${i + 1}, 'local_drone');" class="px-1 py-0.2 rounded bg-emerald-700 hover:bg-emerald-500 text-white flex items-center justify-center text-[7px] font-mono transition shadow font-bold" title="Re-render this shot only with Local 4K Perspective Drone ($0.00)">⚡ Local</button>`;
      const cardH3Btn = `<button type="button" onclick="event.stopPropagation(); regenerateSingleMotionClip(currentActiveInspectorEpisode, ${i + 1}, 'h3_max');" class="px-1 py-0.2 rounded bg-teal-700 hover:bg-teal-500 text-white flex items-center justify-center text-[7px] font-mono transition shadow font-bold" title="Re-render this shot only with MiniMax H3 Max Turbo (~$0.015/sec)">⚡ H3</button>`;
      const cardWanBtn = `<button type="button" onclick="event.stopPropagation(); regenerateSingleMotionClip(currentActiveInspectorEpisode, ${i + 1}, 'wan_4k');" class="px-1 py-0.2 rounded bg-amber-600 hover:bg-amber-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with Wan 2.1 + 4K AI ($0.55)">⚡ Wan4K</button>`;
      const cardProBtn = `<button type="button" onclick="event.stopPropagation(); regenerateSingleMotionClip(currentActiveInspectorEpisode, ${i + 1}, 'kling_pro');" class="px-1 py-0.2 rounded bg-purple-600 hover:bg-purple-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with Kling 1.6 Pro ($0.95)">⚡ Pro</button>`;
      const cardKlingBtn = `<button type="button" onclick="event.stopPropagation(); regenerateSingleMotionClip(currentActiveInspectorEpisode, ${i + 1}, 'kling_v3');" class="px-1 py-0.2 rounded bg-gradient-to-r from-pink-600 to-rose-600 hover:from-pink-500 hover:to-rose-500 text-white flex items-center justify-center text-[7px] font-mono font-bold transition shadow" title="Re-render this shot only with Kling v3 4K Native ($1.40)">⚡ 4K</button>`;

      return `<div class="flex flex-col items-center gap-0.5 cursor-pointer w-full group" onclick="${playAction}" title="Click to play in Full Screen modal & master preview">
        <div class="relative w-full h-11 rounded-lg overflow-hidden bg-gradient-to-br from-purple-950 to-slate-900 ${borderCls} hover:border-purple-400 transition shadow flex flex-col justify-between p-1" style="${bgStyle}">
          ${posterUrl ? '<div class="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition pointer-events-none"></div>' : ''}
          <div class="relative z-10 flex items-center justify-between">
            <span class="px-1 py-0.2 rounded bg-purple-900/90 text-[7px] font-mono text-purple-200 border border-purple-500/30">${model}</span>
            <div class="flex items-center gap-0.5">
              ${cardLocalBtn}
              ${cardH3Btn}
              ${cardWanBtn}
              ${cardProBtn}
              ${cardKlingBtn}
              <span class="px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-purple-300">${dur}</span>
              <button type="button" onclick="event.stopPropagation(); promptDeleteArtifact('Motion', ${i}, '${name}', 'Motion Clip');" class="w-3.5 h-3.5 rounded bg-rose-600/90 hover:bg-rose-500 text-white flex items-center justify-center text-[7px] transition shadow font-bold" title="Delete Motion Clip">✕</button>
            </div>
          </div>
          <div class="relative z-10 flex items-center justify-end"><div class="w-4 h-4 rounded-full bg-purple-600/90 hover:bg-purple-500 text-white flex items-center justify-center text-[6px] shadow transition transform group-hover:scale-110"><i class="fa-solid fa-play ml-0.5"></i></div></div>
        </div>
        <span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center">${name}</span>
      </div>`;
    }

    return `<div class="flex flex-col items-center gap-0.5 w-full opacity-60"><div class="relative w-full h-11 rounded-lg bg-slate-50 dark:bg-slate-950 border border-dashed border-slate-300 dark:border-slate-800 flex flex-col items-center justify-center p-1"><span class="text-[7px] font-mono text-slate-400 dark:text-slate-500 flex items-center gap-1"><i class="fa-solid fa-hourglass text-[6px]"></i> Queued</span></div><span class="text-[8px] text-slate-400 dark:text-slate-500 truncate w-full text-center">${name}</span></div>`;
  }).join("");
}

function renderAudioStemsList(vid) {
  const c = document.getElementById("panel-section-audio");
  if (!c) return;
  const isProc = vid.status === "processing", isFailed = vid.status === "failed", stage = vid.currentStage || 1;
  const rawStems = (vid.audio_stems && vid.audio_stems.length > 0) ? vid.audio_stems : (vid.artifacts?.audio_stems || []);

  if (isFailed && vid.failedStage === 3) {
    c.innerHTML = `<div class="col-span-3 p-2.5 bg-white dark:bg-slate-950 border-2 border-red-500 rounded-xl flex flex-col gap-1.5 shadow-md">
      <div class="flex items-center justify-between flex-wrap gap-1">
        <span class="text-xs font-black text-red-700 dark:text-red-400 flex items-center gap-1.5"><i class="fa-solid fa-triangle-exclamation text-red-600"></i> Stage 3 Audio Error</span>
        <div class="flex items-center gap-1 flex-wrap">
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'azure_speech', true)" class="px-2 py-1 text-[9px] font-bold rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition flex items-center gap-1 shadow-sm active:scale-95" title="Retry with Azure Speech / Edge Neural TTS">🎙️ Azure/Edge</button>
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'gemini', true)" class="px-2 py-1 text-[9px] font-bold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white transition flex items-center gap-1 shadow-sm active:scale-95" title="Retry with Gemini 2.5 Flash Audio">✨ Gemini Audio</button>
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'kokoro', true)" class="px-2 py-1 text-[9px] font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white transition flex items-center gap-1 shadow-sm active:scale-95" title="Retry with Kokoro-82M Local CPU ($0.00)">⚡ Kokoro ($0)</button>
        </div>
      </div>
      <div class="text-[10px] font-mono font-semibold text-red-600 dark:text-red-400 leading-normal break-words">${vid.errorMessage || 'Audio stem synthesis failed.'}</div>
    </div>`;
    return;
  }

  // If Stage < 3 and not processing Stage 3
  if (isProc && stage < 3 && rawStems.length === 0) {
    c.innerHTML = `<div class="col-span-3 h-9 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-2 shadow-sm"><i class="fa-solid fa-hourglass-half text-slate-400 text-xs"></i><span class="text-[9px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 3 Audio</span><span class="text-[7px] text-slate-400 font-mono">(Starts after Keyframe Photos approved)</span></div>`;
    return;
  }

  // If not processing and no stems yet
  if (!isProc && rawStems.length === 0) {
    const rawKfs = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : (vid.artifacts?.keyframes || []);
    const completedKfs = rawKfs.filter(kf => {
      const url = (typeof kf === "object") ? kf.url : kf;
      return url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
    });
    const hasKfs = Boolean(completedKfs.length > 0 || rawKfs.length > 0);
    if (hasKfs) {
      c.innerHTML = `<div class="col-span-3 p-1.5 bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950/40 dark:to-blue-950/40 border border-cyan-300 dark:border-cyan-600/50 rounded-xl flex items-center justify-between gap-1.5 shadow-sm">
        <div class="flex items-center gap-1.5"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><div class="flex flex-col"><span class="text-[9px] font-bold text-cyan-950 dark:text-white">Stage 2 Photos Ready</span><span class="text-[7px] text-cyan-700 dark:text-cyan-300">Choose voiceover engine:</span></div></div>
        <div class="flex items-center gap-1 flex-wrap">
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'azure_speech')" class="px-2 py-1 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-500 hover:to-cyan-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Approve with Azure Speech / Edge Neural TTS">🎙️ Azure/Edge (Def)</button>
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'gemini')" class="px-2 py-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Approve with Gemini 2.5 Flash Audio">✨ Gemini Audio</button>
          <button type="button" onclick="advanceToAudioStage(currentActiveInspectorEpisode, 'kokoro')" class="px-2 py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Approve with Kokoro Local ($0.00)">⚡ Kokoro ($0)</button>
        </div>
      </div>`;
    } else {
      c.innerHTML = `<div class="col-span-3 h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-2 shadow-sm"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><span class="text-[9px] font-bold text-slate-900 dark:text-white">No Audio Stems Yet</span><span class="text-[7px] text-slate-500 font-mono">(Azure TTS, Gemini Audio, Kokoro, Suno &amp; 3D Velvet DSP)</span></div>`;
    }
    return;
  }

  // Find Suno stem, Velvet stem, and Spoken Narration stem
  const sunoStem = rawStems.find(s => (s.filename && s.filename.includes("raw_soundtrack")) || (s.name && (s.name.toLowerCase().includes("suno") || s.name.toLowerCase().includes("soundtrack"))));
  const velvetStem = rawStems.find(s => (s.filename && s.filename.includes("velvet")) || (s.name && (s.name.toLowerCase().includes("velvet") || s.name.toLowerCase().includes("binaural") || s.name.toLowerCase().includes("432hz"))));
  const narrStem = rawStems.find(s => (s.filename && (s.filename.includes("spoken_narration") || s.filename.includes("narration"))) || (s.name && (s.name.toLowerCase().includes("narration") || s.name.toLowerCase().includes("voiceover"))));

  const isAudioActive = Boolean(isProc && stage === 3);
  const items = [
    {
      name: "Suno Soundtrack",
      stem: sunoStem,
      color: "cyan",
      model: "Suno v3.5",
      isGenerating: Boolean(isAudioActive && !sunoStem),
    },
    {
      name: "Velvet 432Hz Master",
      stem: velvetStem,
      color: "emerald",
      model: "Spatial DSP",
      isGenerating: Boolean(isAudioActive && sunoStem && !velvetStem),
    },
    {
      name: "Spoken Narration",
      stem: narrStem,
      color: "indigo",
      model: "TTS Voice",
      isGenerating: Boolean(isAudioActive && (vid.enableVoiceOver || vid.enable_voiceover) && !narrStem),
    }
  ];

  c.innerHTML = items.map((item, i) => {
    if (item.stem && item.stem.url) {
      return `
      <div class="px-2 py-1 bg-white dark:bg-slate-950/70 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col gap-0.5 shadow-sm">
        <div class="flex items-center justify-between text-[9px]">
          <span class="font-mono truncate text-${item.color}-600 dark:text-${item.color}-400 font-bold flex items-center gap-1">
            <i class="fa-solid fa-circle-check text-emerald-500 text-[8px]"></i> ${item.name}
          </span>
          <div class="flex items-center gap-1">
            <span class="text-[8px] font-mono text-slate-500 dark:text-slate-400">⏱ ${item.stem.duration || 'Ready'}</span>
            <button type="button" onclick="promptDeleteArtifact('Audio', ${i}, '${item.name}', 'Audio Stem');" class="text-slate-400 hover:text-rose-500 text-[9px] px-0.5 font-bold" title="Delete Stem">✕</button>
          </div>
        </div>
        <audio controls preload="none" src="${item.stem.url}" class="h-4 w-full scale-95 origin-center"></audio>
      </div>`;
    }

    if (item.isGenerating) {
      return `
      <div class="px-2 py-1 bg-slate-50 dark:bg-slate-950/70 rounded-lg border border-${item.color}-500/40 flex flex-col gap-0.5 shadow-sm">
        <div class="flex items-center justify-between text-[9px]">
          <span class="font-mono truncate text-${item.color}-600 dark:text-${item.color}-400 font-bold flex items-center gap-1">
            <div class="w-2.5 h-2.5 rounded-full border-2 border-${item.color}-500 border-t-transparent animate-spin shrink-0"></div> ${item.name}
          </span>
          <span class="text-[8px] font-mono text-${item.color}-500 font-semibold animate-pulse">Synthesizing...</span>
        </div>
        <div class="w-full bg-slate-200 dark:bg-slate-800 h-1 rounded-full overflow-hidden">
          <div class="h-full bg-${item.color}-500 rounded-full animate-pulse" style="width: 75%"></div>
        </div>
      </div>`;
    }

    return `
    <div class="px-2 py-1 bg-slate-50 dark:bg-slate-950 border border-dashed border-slate-300 dark:border-slate-800 rounded-lg flex items-center justify-between text-slate-400 text-[9px] opacity-70">
      <span class="font-mono flex items-center gap-1"><i class="fa-solid fa-hourglass text-[7px]"></i> ${item.name}</span>
      <span class="text-[7px] font-mono">Queued</span>
    </div>`;
  }).join("");
}
