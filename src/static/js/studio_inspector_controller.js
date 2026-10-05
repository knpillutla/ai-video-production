// CineAI Studio: Panel 3 Master Artifact Inspector Controller (Sequential Stage-Gated)
let activeInspectorTab = "stems", currentActiveInspectorEpisode = null;

function switchInspectorView(tabKey) {
  activeInspectorTab = tabKey;
  const bS = document.getElementById("btn-inspector-view-stems"), bC = document.getElementById("btn-inspector-view-console"), bD = document.getElementById("btn-inspector-view-dist");

  if (bS) bS.classList.toggle("active", tabKey === "stems");
  if (bC) bC.classList.toggle("active", tabKey === "console");
  if (bD) bD.classList.toggle("active", tabKey === "distribution");

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
  if (currentActiveInspectorEpisode && typeof viewEpisodeArtifacts === "function") viewEpisodeArtifacts(currentActiveInspectorEpisode);
}

function openActiveMasterVideoInPopup() {
  const vid = currentActiveInspectorEpisode, videoEl = document.getElementById("studio-panel-video");
  const targetUrl = (videoEl && videoEl.src && !videoEl.src.endsWith("/ui") && !videoEl.src.endsWith("/")) ? videoEl.src : (vid?.videoUrl || vid?.video_url || vid?.editions?.[0]?.url || vid?.artifacts?.master_video || "");
  const epId = vid?.id || vid?.episode_id || "EP-001", title = vid?.title ? `${epId}: ${vid.title}` : `${epId}: 4K Master Video`;
  const meta = `${vid?.format || "4K UHD (16:9)"} • ${vid?.fps || "24 FPS"} • Lossless CRF 22 Broadcast Master`;
  if (typeof openVideoPopup === "function" && targetUrl) openVideoPopup(targetUrl, title, meta);
}

function renderInspectorFromVideo(vid) {
  if (!vid) return;
  currentActiveInspectorEpisode = vid;
  const epId = vid.id || vid.episode_id || "EP-001", cost = (vid.cost_usd !== undefined) ? ` • $${Number(vid.cost_usd).toFixed(2)}` : (vid.cost ? ` • $${Number(vid.cost).toFixed(2)}` : "");
  const dur = vid.duration || (vid.durationSeconds ? `${vid.durationSeconds}s` : "5s"), genre = vid.genre || vid.videoType || "Relaxation & ASMR";
  const isTest = (vid.executionMode === "test" || vid.tierKey === "test" || dur === "5s" || dur === "10s");
  const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };

  setT("top-ep-badge-id", epId); setT("top-ep-badge-genre", genre); setT("top-ep-title", vid.title || "Master Video");
  setT("top-ep-job-id", vid.jobId || `job_${epId.toLowerCase()}`); setT("top-ep-story", vid.story_topic || vid.concept || vid.theme || "Master Episode Production");
  setT("top-ep-duration", isTest ? `${dur} (Test)` : dur); setT("panel-header-ep-id", epId);
  const typeBadge = document.getElementById("panel-header-type-badge");
  if (typeBadge) {
    if (vid.status === "failed") {
      typeBadge.textContent = "Failed";
      typeBadge.className = "text-[9px] px-1.5 py-0.2 rounded-full font-bold bg-white text-red-600 border-2 border-red-500 shadow-sm";
    } else {
      typeBadge.textContent = genre;
      typeBadge.className = "text-[9px] px-1.5 py-0.2 rounded-full font-bold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30";
    }
  }
  setT("panel-header-meta", `${vid.format || vid.formatType || "4K UHD"} • ${vid.fps || "24 FPS"}${cost}`);
  setT("panel-header-title", vid.title || "4K Master Inspector"); setT("panel-header-story", `Story: ${vid.story_topic || vid.concept || vid.theme || "Master Artifacts"}`);

  if (vid.genre) {
    const gSel = document.getElementById("studio-genre-selector");
    if (gSel && gSel.value !== vid.genre) {
      gSel.value = vid.genre;
      if (typeof onGenreChange === "function") onGenreChange(vid.genre);
    }
    if (vid.sub_genre) {
      const subSel = document.getElementById("studio-subgenre-selector");
      if (subSel) subSel.value = vid.sub_genre;
    }
    if (vid.primary_archetype) {
      const archSel = document.getElementById("studio-archetype-selector");
      if (archSel) archSel.value = vid.primary_archetype;
    }
  }

  const statusBadge = document.getElementById("top-ep-status-badge");
  if (statusBadge) {
    if (vid.status === "failed") {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-rose-600 text-white shadow-sm flex items-center gap-1";
      statusBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-[8px]"></i><span>Failed at Stage ${vid.failedStage || vid.currentStage || 1}</span>`;
    } else if (vid.status === "completed" || !vid.status) {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white shadow-sm flex items-center gap-1";
      statusBadge.innerHTML = '<i class="fa-solid fa-circle-check text-[8px]"></i><span>Ready</span>';
    } else {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-600 text-white shadow-sm flex items-center gap-1 animate-pulse";
      statusBadge.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-[8px]"></i><span>${vid.pipelineStrategy === 'manual' ? 'Manual Stage ' + (vid.currentStage || 1) : 'Re-rendering (--id)...'}</span>`;
    }
  }

  const reprocessBtn = document.getElementById("btn-header-reprocess-ep");
  if (reprocessBtn) {
    if (vid.status === "processing") {
      reprocessBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin text-[8px]"></i><span>Re-Synthesizing (--id)...</span>';
      reprocessBtn.classList.add("opacity-80", "pointer-events-none");
    } else {
      reprocessBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate text-[8px]"></i><span>Re-Synthesize</span>';
      reprocessBtn.classList.remove("opacity-80", "pointer-events-none");
    }
  }

  const video = document.getElementById("studio-panel-video"), overlay = document.getElementById("studio-panel-processing-overlay");
  const playerBadge = document.getElementById("panel-player-status-badge");
  document.getElementById("studio-panel-empty-overlay")?.classList.add("hidden");
  
  if (video) {
    const cleanMaster = (vid.videoUrl && !vid.videoUrl.includes("preview_master")) ? vid.videoUrl : (vid.video_url && !vid.video_url.includes("preview_master") ? vid.video_url : null);
    if (vid.status === "completed" && vid.currentStage >= 5 && cleanMaster) {
      overlay?.classList.add("hidden");
      if (playerBadge) {
        playerBadge.textContent = "Ready";
        playerBadge.className = "px-2 py-0.5 rounded-md text-xs font-mono font-bold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30";
      }
      if (!video.src.endsWith(cleanMaster)) video.src = cleanMaster;
    } else {
      overlay?.classList.remove("hidden");
      if (playerBadge) {
        playerBadge.textContent = "Processing";
        playerBadge.className = "px-2 py-0.5 rounded-md text-xs font-mono font-bold bg-purple-500/15 text-purple-700 dark:text-purple-400 border border-purple-500/30 animate-pulse";
      }
      const titleEl = document.getElementById("studio-panel-processing-title");
      const subTitle = document.getElementById("studio-panel-processing-subtitle");
      const barEl = document.getElementById("studio-panel-progress-bar");
      const stepEl = document.getElementById("studio-panel-stage-step");
      const pctEl = document.getElementById("studio-panel-stage-pct");
      
      const stage = vid.currentStage || 1;
      const stageData = {
        1: { title: "Generating Screenplay & Storyboard", subtitle: "Gemini 2.5 Flash • Context & beat formulation", pct: "20%", step: "Stage 1 of 5" },
        2: { title: "Synthesizing 4K Keyframe Photos", subtitle: "FLUX 1.1 Pro Ultra • Hasselblad 8K cinematography", pct: "40%", step: "Stage 2 of 5" },
        3: { title: "Rendering Diffusion Video Motion", subtitle: "Wan 2.1 / Kling v3 • Living wallpaper cinemagraph", pct: "65%", step: "Stage 3 of 5" },
        4: { title: "Mastering Spatial Binaural Audio", subtitle: "Suno v3.5 & Velvet DSP • 48kHz -14 LUFS soundscape", pct: "85%", step: "Stage 4 of 5" },
        5: { title: "Assembling 4K Master Deliverables", subtitle: "Single-pass FFmpeg • Dual-aspect broadcast stretch", pct: "95%", step: "Stage 5 of 5" }
      };

      const cur = stageData[stage] || stageData[1];
      if (titleEl) titleEl.textContent = cur.title;
      if (subTitle) subTitle.textContent = cur.subtitle;
      if (barEl) barEl.style.width = cur.pct;
      if (stepEl) stepEl.textContent = cur.step;
      if (pctEl) pctEl.textContent = cur.pct;
    }
  }

  if (typeof renderScriptSection === "function") renderScriptSection(vid);
  if (typeof renderMasterVideosList === "function") renderMasterVideosList(vid);
  if (typeof renderLongPlayStretchSection === "function") renderLongPlayStretchSection(vid);
  if (typeof renderKeyframesList === "function") renderKeyframesList(vid);
  if (typeof renderMotionClipsList === "function") renderMotionClipsList(vid);
  if (typeof renderAudioStemsList === "function") renderAudioStemsList(vid);
  updateStageGateDock(vid);

  const ytTitle = document.getElementById("dist-yt-title"), ytDesc = document.getElementById("dist-yt-desc");
  if (ytTitle) ytTitle.value = `${vid.title || 'Master Video'} - 4K UHD`;
  if (ytDesc) ytDesc.value = `Story: ${vid.story_topic || vid.concept || vid.title}\nChannel: ${vid.channel_id || 'CineAI'}\n\n#4K #CineAI`;

  const appContainer = document.getElementById("studio-approval-container");
  if (appContainer) {
    const isMasterReady = (vid.status === "completed" && vid.currentStage >= 4 && (vid.videoUrl || vid.video_url));
    if (isMasterReady && vid.status !== "failed" && vid.status !== "processing") {
      appContainer.classList.remove("hidden");
      const appTag = document.getElementById("studio-approval-tag");
      const appBtn = document.getElementById("btn-studio-approve");
      const appBtnTxt = document.getElementById("btn-studio-approve-text");
      const isApproved = Boolean(vid.is_approved || vid.approved);

      if (isApproved) {
        if (appTag) {
          appTag.className = "text-[9px] font-mono font-bold px-1.5 py-0.2 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30";
          appTag.textContent = "✓ Approved";
        }
        if (appBtn) {
          appBtn.disabled = true;
          appBtn.className = "px-2.5 py-1 bg-emerald-700/60 text-emerald-200 cursor-not-allowed font-bold rounded-lg text-[10px] flex items-center gap-1 opacity-80";
        }
        if (appBtnTxt) appBtnTxt.textContent = "Approved";
      } else {
        if (appTag) {
          appTag.className = "text-[9px] font-mono font-bold px-1.5 py-0.2 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30";
          appTag.textContent = "⏳ Unapproved";
        }
        if (appBtn) {
          appBtn.disabled = false;
          appBtn.className = "px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg text-[10px] flex items-center gap-1 transition shadow-sm active:scale-95";
        }
        if (appBtnTxt) appBtnTxt.textContent = "Approve Master Video";
      }
    } else {
      appContainer.classList.add("hidden");
    }
  }

  if (typeof renderStudioProView === "function") {
    renderStudioProView(vid);
  }
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
  document.getElementById("studio-approval-container")?.classList.add("hidden");
  document.getElementById("panel-section-longplay-container")?.classList.add("hidden");
  document.getElementById("panel-longplay-approval-card")?.classList.add("hidden");

  const iC = document.getElementById("panel-section-images"), mC = document.getElementById("panel-section-raw-videos"), aC = document.getElementById("panel-section-audio");
  if (iC) iC.innerHTML = `<div class="col-span-4 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Keyframe Photos Yet</span><span class="text-[8px] text-slate-500 font-mono">(FLUX Dev / Pro / Z-Image)</span></div>`;
  if (mC) mC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Motion Clips Yet</span><span class="text-[8px] text-slate-500 font-mono">(Kling v3 / Wan 2.1)</span></div>`;
  if (aC) aC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Audio Stems Yet</span><span class="text-[8px] text-slate-500 font-mono">(Suno v3.5 &amp; 3D Velvet DSP)</span></div>`;
  if (typeof renderScriptSection === "function") renderScriptSection(null);
  if (typeof renderMasterVideosList === "function") renderMasterVideosList(null);
  if (typeof renderLongPlayStretchSection === "function") renderLongPlayStretchSection(null);
  document.getElementById("studio-stage-controls-dock")?.classList.add("hidden");
}

// Note: Script drawer & screenplay JSON actions are managed in studio_script_drawer.js


function updateStageGateDock(vid) {
  const dock = document.getElementById("studio-stage-controls-dock");
  if (!dock) return;
  const isManual = (vid?.pipelineStrategy === "manual") && (typeof activePipelineStrategy === "undefined" || activePipelineStrategy === "manual");
  const isGenerating = vid && ((vid.generatingPhotoIndex ?? -1) >= 0 || (vid.generatingMotionIndex ?? -1) >= 0);
  if (!isManual || vid?.status === "completed" || isGenerating || !vid?.currentStage) { dock.classList.add("hidden"); return; }
  dock.classList.remove("hidden");
  const title = document.getElementById("dock-stage-title"), counter = document.getElementById("dock-stage-counter");
  const rerollBtn = document.getElementById("btn-dock-reroll-text"), advBtn = document.getElementById("btn-dock-advance-text");
  if (vid.currentStage === 1) {
    if (title) title.innerHTML = '<i class="fa-solid fa-scroll text-amber-500"></i><span>Stage 1: Script &amp; Storyboard Review</span>';
    if (counter) counter.textContent = `Script Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Script";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Keyframe Photos ➔`;
  } else if (vid.currentStage === 2) {
    if (title) title.innerHTML = '<i class="fa-solid fa-images text-blue-500"></i><span>Stage 2: Keyframe Photo Review</span>';
    const selCount = (vid.selectedKeyframeIds || []).length || (vid.keyframes || []).length;
    if (counter) counter.textContent = `${selCount}/${(vid.keyframes || []).length} Photos Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Photos";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Video Motion (${selCount} Photos) ➔`;
  } else if (vid.currentStage === 3) {
    if (title) title.innerHTML = '<i class="fa-solid fa-film text-purple-500"></i><span>Stage 3: Video Motion Curation</span>';
    if (counter) counter.textContent = `${(vid.selectedMotionClipIds || []).length || (vid.motion_clips || []).length} Clips Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Motion";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Compose Audio & Stems ➔`;
  } else if (vid.currentStage === 4) {
    if (title) title.innerHTML = '<i class="fa-solid fa-wave-square text-cyan-500"></i><span>Stage 4: Audio &amp; Vocals Review</span>';
    if (counter) counter.textContent = `Stems Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Audio";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Render Final 4K Master ➔`;
  }
}

function toggleKeyframeSelection(idx) {
  const vid = currentActiveInspectorEpisode;
  if (!vid?.selectedKeyframeIds) return;
  const pos = vid.selectedKeyframeIds.indexOf(idx);
  if (pos >= 0) { if (vid.selectedKeyframeIds.length > 1) vid.selectedKeyframeIds.splice(pos, 1); }
  else { vid.selectedKeyframeIds.push(idx); }
  if (typeof renderKeyframesList === "function") renderKeyframesList(vid);
  updateStageGateDock(vid);
}

if (window.StudioBus) {
  window.StudioBus.on("episode:selected", (ep) => { renderInspectorFromVideo(ep); });
}
