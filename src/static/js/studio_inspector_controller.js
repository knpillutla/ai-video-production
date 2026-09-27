// CineAI Studio: Panel 3 Master Artifact Inspector Controller (Sequential Stage-Gated)
let activeInspectorTab = "stems", currentActiveInspectorEpisode = null;

function switchInspectorView(tabKey) {
  activeInspectorTab = tabKey;
  const bS = document.getElementById("btn-inspector-view-stems"), bC = document.getElementById("btn-inspector-view-console"), bD = document.getElementById("btn-inspector-view-dist");
  const act = "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow", inact = "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
  if (bS) bS.className = (tabKey === "stems") ? act : inact;
  if (bC) bC.className = (tabKey === "console") ? act : inact;
  if (bD) bD.className = (tabKey === "distribution") ? act : inact;
  document.getElementById("inspector-view-stems")?.classList.toggle("hidden", tabKey !== "stems");
  document.getElementById("inspector-view-console")?.classList.toggle("hidden", tabKey !== "console");
  document.getElementById("inspector-view-distribution")?.classList.toggle("hidden", tabKey !== "distribution");
  if (tabKey === "console" && typeof scrollConsoleToBottom === "function") scrollConsoleToBottom();
}

function selectMasterVideoRender(url, label, cardEl) {
  const video = document.getElementById("studio-panel-video"), badge = document.getElementById("panel-video-res-badge");
  if (video && url) { video.src = url; video.play().catch(() => {}); }
  if (badge && label) badge.textContent = label;
  document.getElementById("panel-section-master-videos")?.querySelectorAll(".group").forEach(el => {
    el.classList.remove("border-emerald-500", "border-2"); el.classList.add("border", "border-slate-300", "dark:border-slate-700");
  });
  if (cardEl) {
    const b = cardEl.querySelector(".group") || cardEl;
    b.classList.remove("border", "border-slate-300", "dark:border-slate-700"); b.classList.add("border-emerald-500", "border-2");
  }
}

function openActiveEpisodeModal() {
  if (currentActiveInspectorEpisode && typeof viewEpisodeArtifacts === "function") {
    viewEpisodeArtifacts(currentActiveInspectorEpisode);
  }
}

function renderInspectorFromVideo(vid) {
  if (!vid) return;
  currentActiveInspectorEpisode = vid;
  const epId = vid.id || vid.episode_id || "EP-001";
  const cost = (vid.cost_usd !== undefined) ? ` • $${Number(vid.cost_usd).toFixed(2)}` : (vid.cost ? ` • $${Number(vid.cost).toFixed(2)}` : "");
  const dur = vid.duration || (vid.durationSeconds ? `${vid.durationSeconds}s` : "5s");
  const genre = vid.genre || vid.videoType || "Relaxation & ASMR";
  const isTest = (vid.executionMode === "test" || vid.tierKey === "test" || dur === "5s" || dur === "10s");
  const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };

  setT("top-ep-badge-id", epId); setT("top-ep-badge-genre", genre); setT("top-ep-title", vid.title || "Master Video");
  setT("top-ep-job-id", vid.jobId || `job_${epId.toLowerCase()}`);
  setT("top-ep-story", vid.story_topic || vid.concept || vid.theme || "Master Episode Production");
  setT("top-ep-duration", isTest ? `${dur} (Test)` : dur);

  const statusBadge = document.getElementById("top-ep-status-badge");
  if (statusBadge) {
    if (vid.status === "completed" || !vid.status) {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white shadow-sm flex items-center gap-1";
      statusBadge.innerHTML = '<i class="fa-solid fa-circle-check text-[8px]"></i><span>Ready</span>';
    } else {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-600 text-white shadow-sm flex items-center gap-1 animate-pulse";
      statusBadge.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-[8px]"></i><span>${vid.pipelineStrategy === 'manual' ? 'Manual Stage ' + (vid.currentStage || 1) : 'Auto In Progress'}</span>`;
    }
  }

  setT("panel-header-ep-id", epId); setT("panel-header-type-badge", genre);
  setT("panel-header-meta", `${vid.format || vid.formatType || "4K UHD"} • ${vid.fps || "24 FPS"}${cost}`);
  setT("panel-header-title", vid.title || "4K Master Inspector");
  setT("panel-header-story", `Story: ${vid.story_topic || vid.concept || vid.theme || "Master Artifacts"}`);

  const video = document.getElementById("studio-panel-video"), overlay = document.getElementById("studio-panel-processing-overlay");
  document.getElementById("studio-panel-empty-overlay")?.classList.add("hidden");
  if (video) {
    if (vid.status === "completed" || !vid.status) {
      overlay?.classList.add("hidden");
      const targetSrc = vid.videoUrl || vid.artifacts?.master_video || vid.artifacts?.master_music || "/static/videos/preview_master.mp4";
      if (!video.src.endsWith(targetSrc)) video.src = targetSrc;
    } else { overlay?.classList.remove("hidden"); }
  }

  renderMasterVideosList(vid); renderKeyframesList(vid); renderMotionClipsList(vid); renderAudioStemsList(vid); updateStageGateDock(vid);

  const ytTitle = document.getElementById("dist-yt-title"), ytDesc = document.getElementById("dist-yt-desc");
  if (ytTitle) ytTitle.value = `${vid.title || 'Master Video'} - 4K UHD`;
  if (ytDesc) ytDesc.value = `Story: ${vid.story_topic || vid.concept || vid.title}\nChannel: ${vid.channel_id || 'CineAI'}\n\n#4K #CineAI`;
}

function renderEmptyInspectorState() {
  currentActiveInspectorEpisode = null;
  const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setT("top-ep-badge-id", "NEW"); setT("top-ep-badge-genre", "New Production"); setT("top-ep-title", "Ready for Synthesis");
  setT("top-ep-job-id", "Pending"); setT("top-ep-story", "Select channel preset, configure parameters, and click Produce Video.");
  setT("top-ep-duration", "5s (Draft)"); setT("panel-header-ep-id", "NEW"); setT("panel-header-type-badge", "Ready");
  setT("panel-header-meta", "4K UHD • 24 FPS"); setT("panel-header-title", "4K Master Inspector");
  setT("panel-header-story", "No episode synthesized yet. Click Produce Video to begin.");

  const sb = document.getElementById("top-ep-status-badge");
  if (sb) { sb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-slate-700 text-white"; sb.innerHTML = '<span>Idle</span>'; }
  const video = document.getElementById("studio-panel-video");
  if (video) { video.src = ""; video.pause(); }
  document.getElementById("studio-panel-empty-overlay")?.classList.remove("hidden");
  document.getElementById("studio-panel-processing-overlay")?.classList.add("hidden");

  const iC = document.getElementById("panel-section-images"), mC = document.getElementById("panel-section-raw-videos"), aC = document.getElementById("panel-section-audio");
  if (iC) iC.innerHTML = `<div class="col-span-4 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Keyframe Photos Yet</span><span class="text-[8px] text-slate-500 font-mono">(1 Shot via FLUX 1.1 Pro)</span></div>`;
  if (mC) mC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Motion Clips Yet</span><span class="text-[8px] text-slate-500 font-mono">(Kling v3 / Wan 2.1)</span></div>`;
  if (aC) aC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Audio Stems Yet</span><span class="text-[8px] text-slate-500 font-mono">(Suno v3.5 &amp; 3D Velvet DSP)</span></div>`;
  document.getElementById("studio-stage-controls-dock")?.classList.add("hidden");
}

function renderMasterVideosList(vid) {
  const c = document.getElementById("panel-section-master-videos");
  if (!c) return;
  const dur = vid.duration || (vid.durationSeconds ? `${vid.durationSeconds}s` : "5s");
  const eds = vid.editions || [
    { name: `Master (${dur})`, label: `4K Master (${dur})`, format: "4K Master", duration: dur, url: vid.videoUrl || "/static/videos/preview_master.mp4" },
    { name: "Clean Audio", label: "Clean Stems Loop", format: "Audio", duration: dur, url: vid.videoUrl || "/static/videos/preview_master.mp4" }
  ];
  c.innerHTML = eds.map((ed, i) => `
    <div class="flex flex-col items-center gap-0.5 cursor-pointer w-full" onclick="selectMasterVideoRender('${ed.url}', '${ed.label || ed.name}', this)">
      <div class="group relative w-full h-12 rounded-lg overflow-hidden bg-gradient-to-br from-emerald-950 to-slate-900 ${i === 0 ? 'border-2 border-emerald-500' : 'border border-slate-300 dark:border-slate-700'} hover:border-emerald-400 transition shadow flex flex-col justify-between p-1">
        <div class="flex items-center justify-between"><span class="px-1 py-0.2 rounded bg-emerald-900/90 text-[7px] font-mono text-emerald-200">${ed.format || '4K'}</span><span class="text-[7px] font-mono text-emerald-300">${ed.duration || dur}</span></div>
        <div class="flex items-center justify-end"><i class="fa-solid fa-play text-[8px] text-emerald-400"></i></div>
      </div>
      <span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center">${ed.name}</span>
    </div>`).join("");
}

function renderKeyframesList(vid) {
  const c = document.getElementById("panel-section-images"), countEl = document.getElementById("panel-images-count");
  if (!c) return;
  const isProc = vid.status === "processing", stage = vid.currentStage || 1;
  const numShots = vid.numShots || vid.num_shots || (vid.durationSeconds <= 5 ? 1 : (vid.durationSeconds <= 10 ? 2 : 4));
  let kfs = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : (vid.artifacts?.keyframes || []);

  if (kfs.length === 0 && isProc) {
    const isStage1Active = (stage === 1), p = vid.progress || 20;
    const names = ["Shot 1: Wide", "Shot 2: Sensory", "Shot 3: Setting", "Shot 4: Twilight"];
    kfs = Array.from({ length: numShots }, (_, i) => ({
      name: names[i] || `Shot ${i + 1}`,
      model: "FLUX 1.1 Pro",
      progress: isStage1Active ? Math.min(95, p + (numShots === 1 ? 40 : (i === 0 ? 30 : 15))) : 100,
      isGenerating: isStage1Active
    }));
  }
  if (countEl) countEl.textContent = `${kfs.length} Shots`;
  if (kfs.length === 0) {
    c.innerHTML = `<div class="col-span-4 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Keyframe Photos Yet</span><span class="text-[8px] text-slate-500 font-mono">(${numShots} Shot${numShots > 1 ? 's' : ''} via FLUX 1.1 Pro)</span></div>`;
    return;
  }
  if (!vid.selectedKeyframeIds) vid.selectedKeyframeIds = kfs.map((_, i) => i);
  const isManual = vid.pipelineStrategy === "manual", genIdx = vid.generatingPhotoIndex ?? -1;

  c.innerHTML = kfs.map((kf, i) => {
    const url = (typeof kf === "object") ? kf.url : kf, name = (typeof kf === "object") ? kf.name : `Shot ${i + 1}`, isSel = vid.selectedKeyframeIds.includes(i);
    const isGen = kf.isGenerating || (stage === 1 && (genIdx === i || (isProc && !url))), pVal = kf.progress || (vid.progress ? Math.min(95, vid.progress + 10) : 60);

    if (isGen) {
      return `<div class="flex flex-col items-center gap-0.5 w-full"><div class="relative w-full h-12 rounded-lg bg-white dark:bg-slate-900 border-2 border-blue-500 shadow-sm flex flex-col justify-between p-1.5"><div class="flex items-center justify-between w-full"><span class="text-[8px] font-mono font-bold text-blue-600 dark:text-blue-400 flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> FLUX 1.1</span><span class="text-[7px] font-mono text-blue-600 dark:text-blue-400 font-bold">${pVal}%</span></div><div class="w-full bg-blue-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-blue-600 to-cyan-400 rounded-full animate-pulse" style="width: ${pVal}%"></div></div></div><span class="text-[8px] font-bold text-blue-600 dark:text-blue-400 truncate w-full text-center">${name}</span></div>`;
    }
    const borderCls = isSel ? "border-2 border-emerald-500 ring-1 ring-emerald-500/50" : "border border-slate-300 dark:border-slate-800 opacity-40 grayscale";
    const hasImage = url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
    const fallbackBox = `<div class=\\'w-full h-full flex flex-col justify-between p-1 bg-white dark:bg-slate-900\\'><div class=\\'flex items-center justify-between text-[7px] font-mono font-bold text-emerald-600\\'><span>✓ Ready</span><span>100%</span></div><div class=\\'w-full bg-emerald-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden\\'><div class=\\'h-full bg-emerald-500 rounded-full\\' style=\\'width: 100%\\'></div></div></div>`;
    const innerCard = hasImage
      ? `<img src="${url}" alt="${name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" onerror="this.onerror=null;this.parentElement.innerHTML='${fallbackBox}'"><span class="absolute top-0.5 right-0.5 px-1 py-0.2 rounded bg-black/80 text-[7px] font-mono ${isSel ? 'text-emerald-300' : 'text-gray-400'}">${isSel ? '✓' : 'Off'}</span>`
      : `<div class="w-full h-full flex flex-col justify-between p-1 bg-white dark:bg-slate-900"><div class="flex items-center justify-between text-[7px] font-mono font-bold text-emerald-600 dark:text-emerald-400"><span>✓ Ready</span><span>100%</span></div><div class="w-full bg-emerald-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-emerald-500 rounded-full" style="width: 100%"></div></div></div>`;

    return `<div class="flex flex-col items-center gap-0.5 w-full relative group"><div class="relative w-full h-12 rounded-lg overflow-hidden bg-white dark:bg-slate-900 ${borderCls} cursor-pointer transition shadow-sm" onclick="toggleKeyframeSelection(${i})">${innerCard}${isManual ? `<button type="button" onclick="event.stopPropagation(); deleteKeyframe(${i});" class="hidden group-hover:flex absolute top-0.5 left-0.5 w-4 h-4 bg-red-600/90 text-white rounded items-center justify-center text-[7px]" title="Delete"><i class="fa-solid fa-trash"></i></button>` : ''}</div><div class="flex items-center justify-between w-full px-0.5"><span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate">${name}</span>${isManual ? `<button type="button" onclick="rerollKeyframe(${i});" class="text-[7px] text-indigo-500 hover:text-indigo-400 font-mono">🔄</button>` : ''}</div></div>`;
  }).join("");
}

function renderMotionClipsList(vid) {
  const c = document.getElementById("panel-section-raw-videos"), countEl = document.getElementById("panel-raw-videos-count");
  if (!c) return;
  const isProc = vid.status === "processing", stage = vid.currentStage || 1;
  const numClips = vid.numShots || vid.num_shots || (vid.durationSeconds <= 5 ? 1 : (vid.durationSeconds <= 10 ? 2 : 3));
  let clips = (vid.motion_clips && vid.motion_clips.length > 0) ? vid.motion_clips : (vid.artifacts?.motion_clips || []);

  if (clips.length === 0) {
    if (isProc && stage === 1) {
      if (countEl) countEl.textContent = "0 Clips";
      c.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-3 shadow-sm"><i class="fa-solid fa-hourglass-half text-amber-500 text-xs"></i><span class="text-[10px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 2 Motion</span><span class="text-[8px] text-slate-400 font-mono">(Starts after Keyframe images complete)</span></div>`;
      return;
    }
    if (isProc && stage >= 2) {
      const p = vid.progress || 50, mList = [{ name: "Motion 1: Aerial", model: "Kling v3" }, { name: "Motion 2: Fluid", model: "Wan 2.1" }, { name: "Motion 3: Depth", model: "Kling v3" }];
      clips = Array.from({ length: Math.min(numClips, 3) }, (_, i) => ({
        name: mList[i]?.name || `Motion ${i + 1}`, model: mList[i]?.model || "Kling v3",
        progress: stage === 2 ? Math.min(95, p + (i === 0 ? 10 : 0)) : 100, isGenerating: stage === 2
      }));
    }
  }

  if (countEl) countEl.textContent = `${clips.length} Clips`;
  if (clips.length === 0) {
    c.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Motion Clips Yet</span><span class="text-[8px] text-slate-500 font-mono">(Kling v3 / Wan 2.1)</span></div>`;
    return;
  }
  if (!vid.selectedMotionClipIds) vid.selectedMotionClipIds = clips.map((_, i) => i);
  const genIdx = vid.generatingMotionIndex ?? -1;

  c.innerHTML = clips.map((m, i) => {
    const url = (typeof m === "object") ? m.url : m, name = (typeof m === "object") ? m.name : `Motion ${i + 1}`, model = (typeof m === "object") ? (m.model || "Kling Pro") : "Kling Pro", isSel = vid.selectedMotionClipIds.includes(i);
    const isGen = m.isGenerating || (stage === 2 && (genIdx === i || (isProc && !url))), pVal = m.progress || (vid.progress ? Math.min(95, vid.progress) : 50);

    if (isGen) {
      return `<div class="flex flex-col items-center gap-0.5 w-full"><div class="relative w-full h-12 rounded-lg bg-white dark:bg-slate-900 border-2 border-purple-500 shadow-sm flex flex-col justify-between p-1.5"><div class="flex items-center justify-between w-full"><span class="text-[8px] font-mono font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> ${model}</span><span class="text-[7px] font-mono text-purple-600 dark:text-purple-400 font-bold">${pVal}%</span></div><div class="w-full bg-purple-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-gradient-to-r from-purple-600 to-pink-500 rounded-full animate-pulse" style="width: ${pVal}%"></div></div></div><span class="text-[8px] font-bold text-purple-600 dark:text-purple-400 truncate w-full text-center">${name}</span></div>`;
    }
    const borderCls = isSel ? "border-2 border-purple-500 ring-1 ring-purple-500/50" : "border border-slate-300 dark:border-slate-800 opacity-40 grayscale";
    return `<div class="flex flex-col items-center gap-0.5 w-full relative group cursor-pointer" onclick="selectMasterVideoRender('${url}', '${name}', this)"><div class="relative w-full h-12 rounded-lg overflow-hidden bg-white dark:bg-slate-900 ${borderCls} shadow-sm flex flex-col justify-between p-1.5"><div class="flex items-center justify-between w-full"><span class="text-[8px] font-mono font-bold text-purple-600 dark:text-purple-400 flex items-center gap-1"><i class="fa-solid fa-play text-[6px]"></i> ${model}</span><span class="text-[7px] font-mono font-bold text-purple-600 dark:text-purple-400">100%</span></div><div class="w-full bg-purple-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden"><div class="h-full bg-purple-600 rounded-full" style="width: 100%"></div></div></div><span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center">${name}</span></div>`;
  }).join("");
}

function renderAudioStemsList(vid) {
  const c = document.getElementById("panel-section-audio");
  if (!c) return;
  const isProc = vid.status === "processing", stage = vid.currentStage || 1;
  let stems = (vid.audio_stems && vid.audio_stems.length > 0) ? vid.audio_stems : (vid.artifacts?.audio_stems || []);

  if (stems.length === 0) {
    if (isProc && stage < 3) {
      c.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-dashed border-slate-300 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-500 dark:text-slate-400 px-3 shadow-sm"><i class="fa-solid fa-hourglass-half text-slate-400 text-xs"></i><span class="text-[10px] font-semibold text-slate-700 dark:text-slate-300">Queued for Stage 3 Audio</span><span class="text-[8px] text-slate-400 font-mono">(Suno v3.5 &amp; 3D Velvet DSP)</span></div>`;
      return;
    }
    if (isProc && stage >= 3) {
      stems = [
        { name: "Suno Soundtrack", model: "Suno v3.5", duration: "10s", isGenerating: true, color: "cyan" },
        { name: "Velvet 432Hz Master", model: "Spatial DSP", duration: "10s", isGenerating: true, color: "emerald" }
      ];
    }
  }

  if (stems.length === 0) {
    c.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Audio Stems Yet</span><span class="text-[8px] text-slate-500 font-mono">(Suno v3.5 &amp; 3D Velvet DSP)</span></div>`;
    return;
  }
  c.innerHTML = stems.map(s => {
    if (s.isGenerating) {
      return `<div class="px-2 py-1 bg-slate-50 dark:bg-slate-950/70 rounded-lg border border-cyan-500/40 flex flex-col gap-0.5"><div class="flex items-center justify-between text-[9px]"><span class="font-mono truncate text-cyan-600 dark:text-cyan-400 font-bold flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> ${s.name}</span><span class="text-[8px] font-mono text-cyan-500">Synthesizing...</span></div><div class="w-full bg-slate-200 dark:bg-slate-800 h-1 rounded-full overflow-hidden"><div class="h-full bg-cyan-500 rounded-full animate-pulse" style="width: 70%"></div></div></div>`;
    }
    return `<div class="px-2 py-1 bg-slate-50 dark:bg-slate-950/70 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col gap-0.5"><div class="flex items-center justify-between text-[9px]"><span class="font-mono truncate text-${s.color || 'cyan'}-600 dark:text-${s.color || 'cyan'}-400">${s.name || s.filename}</span><span class="text-[8px] font-mono">⏱ ${s.duration || '2.0s'}</span></div><audio controls preload="none" src="${s.url}" class="h-3.5 w-full scale-95 origin-center"></audio></div>`;
  }).join("");
}

function updateStageGateDock(vid) {
  const dock = document.getElementById("studio-stage-controls-dock");
  if (!dock) return;
  const isManual = (vid && vid.pipelineStrategy === "manual") && (typeof activePipelineStrategy === "undefined" || activePipelineStrategy === "manual");
  const isGenerating = vid && ((vid.generatingPhotoIndex !== undefined && vid.generatingPhotoIndex >= 0) || (vid.generatingMotionIndex !== undefined && vid.generatingMotionIndex >= 0));
  if (!isManual || (vid && vid.status === "completed") || isGenerating || !vid || !vid.currentStage) {
    dock.classList.add("hidden"); return;
  }
  dock.classList.remove("hidden");
  const title = document.getElementById("dock-stage-title"), counter = document.getElementById("dock-stage-counter");
  const rerollBtn = document.getElementById("btn-dock-reroll-text"), advBtn = document.getElementById("btn-dock-advance-text");

  if (vid.currentStage === 1) {
    if (title) title.innerHTML = '<i class="fa-solid fa-images text-blue-500"></i><span>Stage 1: Keyframe Photo Review</span>';
    const selCount = (vid.selectedKeyframeIds || []).length, total = (vid.keyframes || []).length;
    if (counter) counter.textContent = `${selCount}/${total} Selected`;
    if (rerollBtn) rerollBtn.textContent = "+ Add Variant Shot";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Video Motion (${selCount} Photos) ➔`;
  } else if (vid.currentStage === 2) {
    if (title) title.innerHTML = '<i class="fa-solid fa-film text-purple-500"></i><span>Stage 2: Video Motion Curation</span>';
    if (counter) counter.textContent = `${(vid.selectedMotionClipIds || []).length} Clips Active`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Motion";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Compose Audio & Stems ➔`;
  } else if (vid.currentStage === 3) {
    if (title) title.innerHTML = '<i class="fa-solid fa-wave-square text-cyan-500"></i><span>Stage 3: Audio & Vocals Review</span>';
    if (counter) counter.textContent = `Stems Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Audio";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Render Final 4K Master ➔`;
  }
}

function toggleKeyframeSelection(idx) {
  const vid = currentActiveInspectorEpisode;
  if (!vid || !vid.selectedKeyframeIds) return;
  const pos = vid.selectedKeyframeIds.indexOf(idx);
  if (pos >= 0) { if (vid.selectedKeyframeIds.length > 1) vid.selectedKeyframeIds.splice(pos, 1); }
  else { vid.selectedKeyframeIds.push(idx); }
  renderKeyframesList(vid); updateStageGateDock(vid);
}

function deleteKeyframe(idx) {
  const vid = currentActiveInspectorEpisode;
  if (!vid || !vid.keyframes || vid.keyframes.length <= 1) return;
  vid.keyframes.splice(idx, 1); vid.selectedKeyframeIds = vid.keyframes.map((_, i) => i);
  renderKeyframesList(vid); updateStageGateDock(vid);
}

function rerollKeyframe(idx) {
  const vid = currentActiveInspectorEpisode;
  if (!vid || !vid.keyframes) return;
  vid.keyframes[idx].name = `${vid.keyframes[idx].name.split(" (v")[0]} (v${Math.floor(Math.random() * 9 + 2)})`;
  renderKeyframesList(vid);
}

if (window.StudioBus) {
  window.StudioBus.on("episode:selected", (ep) => { renderInspectorFromVideo(ep); });
}
