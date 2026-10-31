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
  if (tabKey === "distribution" && typeof renderDistributionPackaging === "function") renderDistributionPackaging(currentActiveInspectorEpisode);
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

async function refreshArtifactsPanel() {
  const icon = document.getElementById("icon-refresh-artifacts");
  if (icon) icon.classList.add("fa-spin");
  try {
    const vid = currentActiveInspectorEpisode;
    if (!vid) return;
    const epId = vid.id || vid.episode_id || "EP-001";
    if (epId === "NEW") return;
    const vFmt = String(vid.format || vid.format_slug || "").toLowerCase().trim();
    const isDoc = vFmt.includes("documentary") || String(vid.genre || "").toLowerCase().startsWith("doc");
    const isMv = vFmt.includes("music_video") || String(vid.genre || "").toLowerCase().startsWith("music/") || String(vid.genre || "").toLowerCase().startsWith("dance/");
    const chSlug = vid.channelId || vid.channel_id || (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all" ? selectedStudioChannel : (isDoc ? "euro_discovery" : "nature_rhythms"));
    const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
    const fmtQ = encodeURIComponent(vid.format || vid.format_slug || "");
    const prodQ = encodeURIComponent(vid.production_name || vid.country || vid.location_hub || "");

    const pollEndpoint = isMv ? "/api/music-video/poll-artifacts" : (isDoc ? "/api/documentary/poll-artifacts" : "/api/production/poll-artifacts");
    const res = await fetch(`${pollEndpoint}?channel_id=${chSlug}&episode_id=${epId}&format=${fmtQ}&production_name=${prodQ}&user_id=${encodeURIComponent(uEmail)}&_t=${Date.now()}`);
    if (res.ok) {
      const data = await res.json();
      if (data) {
        if (Array.isArray(data.keyframes)) vid.keyframes = data.keyframes;
        if (Array.isArray(data.motion_clips)) vid.motion_clips = data.motion_clips;
        if (Array.isArray(data.audio_stems)) vid.audio_stems = data.audio_stems;
        if (data.story) vid.story = data.story;
        if (data.video_url) { vid.video_url = data.video_url; vid.videoUrl = data.video_url; }
        if (data.nature_video_url) vid.nature_video_url = data.nature_video_url;
        if (Array.isArray(data.editions) && data.editions.length) vid.editions = data.editions;
        if (data.screenplay) vid.screenplay = data.screenplay;
        if (data.pipeline_state) vid.pipeline_state = data.pipeline_state;
        if (data.status) vid.status = data.status;
        if (data.currentStage) vid.currentStage = data.currentStage;
        if (data.stage) vid.stage = data.stage;
        vid._artifactsChecked = true;
      }
    }
    renderInspectorFromVideo(vid);
    if (typeof filterChannelArchive === "function") filterChannelArchive();
  } catch (err) {
    console.warn("refreshArtifactsPanel error:", err);
  } finally {
    if (icon) icon.classList.remove("fa-spin");
  }
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

  // Cross-format artifact bleeding guard
  const vFmt = String(vid.format || vid.format_slug || "").toLowerCase().trim();
  if (vFmt && Array.isArray(vid.keyframes)) {
    vid.keyframes = vid.keyframes.filter(kf => {
      const u = String(typeof kf === "object" ? kf.url : kf || "");
      if (u.includes("/relaxation/") && vFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && vFmt.includes("relaxation")) return false;
      return true;
    });
  }
  if (vFmt && Array.isArray(vid.motion_clips)) {
    vid.motion_clips = vid.motion_clips.filter(mc => {
      const u = String(typeof mc === "object" ? mc.url : mc || "");
      if (u.includes("/relaxation/") && vFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && vFmt.includes("relaxation")) return false;
      return true;
    });
  }
  if (vFmt && Array.isArray(vid.audio_stems)) {
    vid.audio_stems = vid.audio_stems.filter(as => {
      const u = String(typeof as === "object" ? as.url : as || "");
      if (u.includes("/relaxation/") && vFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && vFmt.includes("relaxation")) return false;
      return true;
    });
  }

  // Fetch fresh disk artifacts from server to ensure accurate, up-to-date representation (debounced with lock)
  if (epId && epId !== "NEW" && !vid._isInspectorPolling) {
    vid._isInspectorPolling = true;
    const isDoc = vFmt.includes("documentary") || String(vid.genre || "").toLowerCase().startsWith("doc");
    const isMv = vFmt.includes("music_video") || String(vid.genre || "").toLowerCase().startsWith("music/") || String(vid.genre || "").toLowerCase().startsWith("dance/");
    const chSlug = vid.channelId || vid.channel_id || (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all" ? selectedStudioChannel : (isDoc ? "euro_discovery" : "nature_rhythms"));
    const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
    const fmtQ = encodeURIComponent(vid.format || vid.format_slug || "");
    const prodQ = encodeURIComponent(vid.production_name || vid.country || vid.location_hub || "");
    const pollEndpoint = isMv ? "/api/music-video/poll-artifacts" : (isDoc ? "/api/documentary/poll-artifacts" : "/api/production/poll-artifacts");

    fetch(`${pollEndpoint}?channel_id=${chSlug}&episode_id=${epId}&format=${fmtQ}&production_name=${prodQ}&user_id=${encodeURIComponent(uEmail)}&_t=${Date.now()}`)
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (!data || !currentActiveInspectorEpisode) return;
        const curEpId = String(currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id || "").toUpperCase();
        const curProd = String(currentActiveInspectorEpisode.production_name || "standalone").toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "");
        const polledEpId = String(epId).toUpperCase();
        const polledProd = String(vid.production_name || "standalone").toLowerCase().replace(/[^a-z0-9_-]+/g, "_").replace(/^_+|_+$/g, "");

        if (curEpId === polledEpId && curProd === polledProd) {
          let hasChanged = false;
          const newKfs = data.keyframes || [];
          if (JSON.stringify(currentActiveInspectorEpisode.keyframes || []) !== JSON.stringify(newKfs)) {
            currentActiveInspectorEpisode.keyframes = newKfs;
            hasChanged = true;
          }
          const newMcs = data.motion_clips || [];
          if (JSON.stringify(currentActiveInspectorEpisode.motion_clips || []) !== JSON.stringify(newMcs)) {
            currentActiveInspectorEpisode.motion_clips = newMcs;
            hasChanged = true;
          }
          const newStems = data.audio_stems || [];
          if (JSON.stringify(currentActiveInspectorEpisode.audio_stems || []) !== JSON.stringify(newStems)) {
            currentActiveInspectorEpisode.audio_stems = newStems;
            hasChanged = true;
          }
          const polledDest = data.production_name || data.story?.destination_entity || data.script?.destination_entity;
          if (polledDest && (!currentActiveInspectorEpisode.production_name || currentActiveInspectorEpisode.production_name === "standalone")) {
            currentActiveInspectorEpisode.production_name = polledDest;
            currentActiveInspectorEpisode.country = polledDest;
            hasChanged = true;
          }
          if (data.story && JSON.stringify(currentActiveInspectorEpisode.story || {}) !== JSON.stringify(data.story)) {
            currentActiveInspectorEpisode.story = data.story;
            hasChanged = true;
          }
          if (data.screenplay && JSON.stringify(currentActiveInspectorEpisode.screenplay || {}) !== JSON.stringify(data.screenplay)) {
            currentActiveInspectorEpisode.screenplay = data.screenplay;
            hasChanged = true;
          }
          if (data.script && JSON.stringify(currentActiveInspectorEpisode.script || {}) !== JSON.stringify(data.script)) {
            currentActiveInspectorEpisode.script = data.script;
            hasChanged = true;
          }
          if (data.video_url && currentActiveInspectorEpisode.video_url !== data.video_url) {
            currentActiveInspectorEpisode.video_url = data.video_url;
            currentActiveInspectorEpisode.videoUrl = data.video_url;
            hasChanged = true;
          }
          if (data.status && currentActiveInspectorEpisode.status !== data.status) {
            if (currentActiveInspectorEpisode.status === "processing" && (data.status === "ready" || data.status === "idle")) {
              // Preserve active processing state during live synthesis
            } else {
              currentActiveInspectorEpisode.status = data.status;
              hasChanged = true;
            }
          }

          if (hasChanged) {
            if (window.StudioFormatDispatcher?.dispatch) {
              window.StudioFormatDispatcher.dispatch(currentActiveInspectorEpisode);
            } else {
              if (typeof updateFormatStageLayout === "function") updateFormatStageLayout(currentActiveInspectorEpisode);
              if (typeof updateStagePillsForFormat === "function") updateStagePillsForFormat(currentActiveInspectorEpisode);
              if (typeof renderStorySection === "function") renderStorySection(currentActiveInspectorEpisode);
              if (typeof renderNarrationSection === "function") renderNarrationSection(currentActiveInspectorEpisode);
              if (typeof renderScriptSection === "function") renderScriptSection(currentActiveInspectorEpisode);
              if (typeof renderKeyframesList === "function") renderKeyframesList(currentActiveInspectorEpisode);
              if (typeof renderAudioStemsList === "function") renderAudioStemsList(currentActiveInspectorEpisode);
              if (typeof renderMotionClipsList === "function") renderMotionClipsList(currentActiveInspectorEpisode);
              if (typeof renderMasterVideosList === "function") renderMasterVideosList(currentActiveInspectorEpisode);
              if (typeof renderLongPlayStretchSection === "function") renderLongPlayStretchSection(currentActiveInspectorEpisode);
            }
            if (typeof updateStageGateDock === "function") updateStageGateDock(currentActiveInspectorEpisode);
          }
        }
      })
      .catch(() => {})
      .finally(() => {
        vid._isInspectorPolling = false;
      });
  }

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

  if (typeof populateProductionControlsFromEpisode === "function") {
    populateProductionControlsFromEpisode(vid);
  }

  const statusBadge = document.getElementById("top-ep-status-badge");
  if (statusBadge) {
    if (vid.status === "failed") {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-rose-600 text-white shadow-sm flex items-center gap-1";
      statusBadge.innerHTML = `<i class="fa-solid fa-triangle-exclamation text-[8px]"></i><span>Failed at Stage ${vid.failedStage || vid.currentStage || 1}</span>`;
    } else if (vid.is_published || vid.published || vid.youtube_published?.published) {
      statusBadge.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white shadow-sm flex items-center gap-1";
      statusBadge.innerHTML = '<i class="fa-brands fa-youtube text-[10px]"></i><span>Published</span>';
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
  const heroResult = document.getElementById("panel-hero-result-section");
  const headerProgWrap = document.getElementById("panel-header-progress-wrap");
  const headerProgStage = document.getElementById("panel-header-progress-stage");
  const headerProgSub = document.getElementById("panel-header-progress-sub");
  const headerProgPct = document.getElementById("panel-header-progress-pct");
  const headerProgBar = document.getElementById("panel-header-progress-bar");
  document.getElementById("studio-panel-empty-overlay")?.classList.add("hidden");

  const cleanMaster = (vid.videoUrl && !vid.videoUrl.includes("preview_master")) ? vid.videoUrl : (vid.video_url && !vid.video_url.includes("preview_master") ? vid.video_url : null);
  const isDoc = vFmt.includes("documentary") || String(vid.genre || "").toLowerCase().startsWith("doc");
  const stage = vid.currentStage || 1;
  const stageData = isDoc ? {
    1: { title: "Formulating Raw Story & Chapters", subtitle: "Gemini 2.5 Flash • 22-Chapter sovereign dossier", pct: "15%", step: "Stage 1 of 7" },
    2: { title: "Synthesizing Spoken Narration", subtitle: "Azure Speech / Edge HD • 48kHz broadcast audio clock", pct: "30%", step: "Stage 2 of 7" },
    3: { title: "Formulating Directorial Screenplay", subtitle: "Gemini 2.5 Flash • Multi-angle cinematic shots", pct: "45%", step: "Stage 3 of 7" },
    4: { title: "Synthesizing 4K Keyframe Photos", subtitle: "FLUX 1.1 Pro Ultra / Z-Image • Hasselblad 8K cinematography", pct: "60%", step: "Stage 4 of 7" },
    5: { title: "Mastering Soundtrack & Spatial BGM", subtitle: "Suno v3.5 & 432Hz Velvet DSP • -14 LUFS stereo master", pct: "75%", step: "Stage 5 of 7" },
    6: { title: "Rendering 4K Video Motion", subtitle: "Wan 2.1 / Kling v3 / Perspective Drone", pct: "85%", step: "Stage 6 of 7" },
    7: { title: "Assembling 4K Broadcast Master", subtitle: "Single-pass FFmpeg • 4K 24fps master & 9:16 Short", pct: "95%", step: "Stage 7 of 7" }
  } : {
    1: { title: "Generating Screenplay & Storyboard", subtitle: "Gemini 2.5 Flash • Context & beat formulation", pct: "20%", step: "Stage 1 of 5" },
    2: { title: "Synthesizing 4K Keyframe Photos", subtitle: "FLUX 1.1 Pro Ultra • Hasselblad 8K cinematography", pct: "40%", step: "Stage 2 of 5" },
    3: { title: "Mastering Voiceover & Audio Stems", subtitle: "Azure TTS & Velvet DSP • 48kHz -14 LUFS soundscape", pct: "65%", step: "Stage 3 of 5" },
    4: { title: "Rendering Diffusion Video Motion", subtitle: "Wan 2.1 / Kling v3 • Living wallpaper cinemagraph", pct: "85%", step: "Stage 4 of 5" },
    5: { title: "Assembling 4K Master Deliverables", subtitle: "Single-pass FFmpeg • Dual-aspect broadcast stretch", pct: "95%", step: "Stage 5 of 5" }
  };
  const cur = stageData[stage] || stageData[1];

  if (vid.status === "processing") {
    // Show compact horizontal progress bar directly below title in header section
    if (headerProgWrap) {
      headerProgWrap.classList.remove("hidden");
      if (headerProgStage) headerProgStage.textContent = `${cur.step}: ${cur.title}`;
      if (headerProgSub) headerProgSub.textContent = cur.subtitle;
      if (headerProgPct) headerProgPct.textContent = cur.pct;
      if (headerProgBar) headerProgBar.style.width = cur.pct;
    }
    if (typeof updateStagePillsForFormat === "function") updateStagePillsForFormat(vid);
    // Update the 5 horizontal stage pills
    const sNames = ['Script', 'Photos', 'Audio', 'Motion', 'Master'];
    for (let sNum = 1; sNum <= 5; sNum++) {
      const pill = document.getElementById(`stage-pill-${sNum}`);
      if (pill) {
        if (sNum < stage) {
          pill.className = "stage-pill cursor-pointer px-2 py-0.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 whitespace-nowrap shrink-0 transition font-bold";
          pill.innerHTML = `✓ ${sNum}. ${sNames[sNum - 1]}`;
        } else if (sNum === stage) {
          pill.className = "stage-pill cursor-pointer px-2 py-0.5 rounded-full border border-purple-500/40 bg-purple-500/20 text-purple-700 dark:text-purple-300 whitespace-nowrap shrink-0 transition font-bold shadow-sm animate-pulse";
          pill.innerHTML = `<i class="fa-solid fa-circle-notch fa-spin text-[8px] mr-1"></i>${sNum}. ${sNames[sNum - 1]} (${cur.pct})`;
        } else {
          pill.className = "stage-pill cursor-pointer px-2 py-0.5 rounded-full border border-[var(--border)] bg-[var(--card)] text-[var(--text-muted)] whitespace-nowrap shrink-0 transition opacity-70";
          pill.innerHTML = `${sNum}. ${sNames[sNum - 1]}`;
        }
      }
    }
    // Collapse giant 220px video container while processing without master video
    if (heroResult) {
      if (cleanMaster) {
        heroResult.classList.remove("hidden");
        overlay?.classList.add("hidden");
      } else {
        heroResult.classList.add("hidden");
      }
    }
    if (playerBadge) {
      playerBadge.textContent = "Processing";
      playerBadge.className = "px-2 py-0.5 rounded-md text-xs font-mono font-bold bg-purple-500/15 text-purple-700 dark:text-purple-400 border border-purple-500/30 animate-pulse";
    }
  } else if (vid.status === "completed" && cleanMaster) {
    if (headerProgWrap) headerProgWrap.classList.add("hidden");
    if (heroResult) heroResult.classList.remove("hidden");
    overlay?.classList.add("hidden");
    if (playerBadge) {
      playerBadge.textContent = "Ready";
      playerBadge.className = "px-2 py-0.5 rounded-md text-xs font-mono font-bold bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30";
    }
    if (video && !video.src.endsWith(cleanMaster)) video.src = cleanMaster;
  } else {
    // Idle or failed
    if (headerProgWrap) headerProgWrap.classList.add("hidden");
    if (cleanMaster && heroResult) {
      heroResult.classList.remove("hidden");
      overlay?.classList.add("hidden");
      if (video && !video.src.endsWith(cleanMaster)) video.src = cleanMaster;
    } else if (heroResult) {
      heroResult.classList.add("hidden");
    }
  }

  // Also update legacy overlay elements if present
  const titleEl = document.getElementById("studio-panel-processing-title");
  const subTitle = document.getElementById("studio-panel-processing-subtitle");
  const barEl = document.getElementById("studio-panel-progress-bar");
  const stepEl = document.getElementById("studio-panel-stage-step");
  const pctEl = document.getElementById("studio-panel-stage-pct");
  if (titleEl) titleEl.textContent = cur.title;
  if (subTitle) subTitle.textContent = cur.subtitle;
  if (barEl) barEl.style.width = cur.pct;
  if (stepEl) stepEl.textContent = cur.step;
  if (pctEl) pctEl.textContent = cur.pct;

  if (window.StudioFormatDispatcher?.dispatch) {
    window.StudioFormatDispatcher.dispatch(vid);
  } else {
    if (typeof updateFormatStageLayout === "function") updateFormatStageLayout(vid);
    if (typeof updateStagePillsForFormat === "function") updateStagePillsForFormat(vid);
    if (typeof renderStorySection === "function") renderStorySection(vid);
    if (typeof renderNarrationSection === "function") renderNarrationSection(vid);
    if (typeof renderScriptSection === "function") renderScriptSection(vid);
    if (typeof renderMasterVideosList === "function") renderMasterVideosList(vid);
    if (typeof renderLongPlayStretchSection === "function") renderLongPlayStretchSection(vid);
    if (typeof renderKeyframesList === "function") renderKeyframesList(vid);
    if (typeof renderAudioStemsList === "function") renderAudioStemsList(vid);
    if (typeof renderMotionClipsList === "function") renderMotionClipsList(vid);
  }
  updateStageGateDock(vid);

  if (typeof renderDistributionPackaging === "function") renderDistributionPackaging(vid);

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
  document.getElementById("panel-header-progress-wrap")?.classList.add("hidden");
  document.getElementById("panel-hero-result-section")?.classList.add("hidden");
  document.getElementById("studio-approval-container")?.classList.add("hidden");
  document.getElementById("studio-queued-banner")?.classList.add("hidden");

  const iC = document.getElementById("panel-section-images"), mC = document.getElementById("panel-section-raw-videos"), aC = document.getElementById("panel-section-audio");
  if (iC) iC.innerHTML = `<div class="col-span-4 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-images text-blue-600 dark:text-blue-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Keyframe Photos Yet</span><span class="text-[8px] text-slate-500 font-mono">(FLUX Dev / Pro / Z-Image)</span></div>`;
  if (mC) mC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-film text-purple-600 dark:text-purple-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Motion Clips Yet</span><span class="text-[8px] text-slate-500 font-mono">(Kling v3 / Wan 2.1)</span></div>`;
  if (aC) aC.innerHTML = `<div class="col-span-3 h-12 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-center gap-2 text-slate-700 dark:text-slate-300 px-3 shadow-sm"><i class="fa-solid fa-wave-square text-cyan-600 dark:text-cyan-400 text-xs"></i><span class="text-[10px] font-bold text-slate-900 dark:text-white">No Audio Stems Yet</span><span class="text-[8px] text-slate-500 font-mono">(Suno v3.5 &amp; 3D Velvet DSP)</span></div>`;
  if (typeof renderScriptSection === "function") renderScriptSection(null);
  if (typeof renderMasterVideosList === "function") renderMasterVideosList(null);
  if (typeof renderLongPlayStretchSection === "function") renderLongPlayStretchSection({ id: "NEW" });
  if (window.DocumentaryArtifactsRenderer?.renderEmpty) window.DocumentaryArtifactsRenderer.renderEmpty();
  document.getElementById("studio-stage-controls-dock")?.classList.add("hidden");
}

function scrollToStage(sectionId) {
  const el = document.getElementById(sectionId);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}
window.scrollToStage = scrollToStage;

// Note: Script drawer & screenplay JSON actions are managed in studio_script_drawer.js


function updateStageGateDock(vid) {
  const dock = document.getElementById("studio-stage-controls-dock");
  if (!dock) return;
  const isManual = (vid?.pipelineStrategy === "manual") && (typeof activePipelineStrategy === "undefined" || activePipelineStrategy === "manual");
  const isGenerating = vid && ((vid.generatingPhotoIndex ?? -1) >= 0 || (vid.generatingMotionIndex ?? -1) >= 0);

  const genreSel = document.getElementById("studio-genre-selector")?.value || "";
  const fSelector = document.getElementById("studio-active-format-val")?.value || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "");
  const effFmt = String(vid?.format_slug || vid?.format || fSelector || "").toLowerCase();
  const effGenre = String(vid?.genre || vid?.subgenre || vid?.sub_genre || genreSel || "").toLowerCase();
  const isRelax = effGenre.startsWith("relax") || effGenre.includes("relax/") || effFmt === "relaxation" || effFmt.startsWith("relax");
  const lpEds = (vid?.long_play_editions || []).filter(e => e.format?.includes("Long-Play") || e.name?.includes("Hour"));
  const hasMaster = Boolean(vid?.videoUrl || vid?.video_url || (vid?.editions && vid.editions.length > 0));

  if (!isManual || isGenerating || !vid?.currentStage) { dock.classList.add("hidden"); return; }

  // If already completed and has long play, or non-relax completed, hide dock
  if (vid?.status === "completed" && (!isRelax || lpEds.length > 0 || !hasMaster)) {
    dock.classList.add("hidden");
    return;
  }

  dock.classList.remove("hidden");
  const title = document.getElementById("dock-stage-title"), counter = document.getElementById("dock-stage-counter");
  const rerollBtn = document.getElementById("btn-dock-reroll-text"), advBtn = document.getElementById("btn-dock-advance-text");
  const isDoc = !isRelax;
  if (isDoc) {
    if (vid.currentStage === 1) {
      if (title) title.innerHTML = `<i class="fa-solid fa-scroll text-amber-500"></i><span>Stage 1: Raw Story Dossier</span>`;
      if (counter) counter.textContent = `${vid.story?.chapters?.length || 21} Chapters Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Story";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Narration ➔`;
    } else if (vid.currentStage === 2) {
      if (title) title.innerHTML = `<i class="fa-solid fa-microphone-lines text-emerald-500"></i><span>Stage 2: Spoken Narration Review</span>`;
      if (counter) counter.textContent = `Narration Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Narration";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Formulate Screenplay ➔`;
    } else if (vid.currentStage === 3) {
      const shCount = vid.screenplay?.total_shots || (vid.screenplay?.chapters ? vid.screenplay.chapters.reduce((a, c) => a + (c.shots?.length || 0), 0) : 0);
      if (title) title.innerHTML = `<i class="fa-solid fa-clapperboard text-indigo-500"></i><span>Stage 3: 3-Shot Screenplay Review</span>`;
      if (counter) counter.textContent = `${shCount || 63} Shots Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Screenplay";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Keyframes ➔`;
    } else if (vid.currentStage === 4) {
      if (title) title.innerHTML = '<i class="fa-solid fa-images text-blue-500"></i><span>Stage 4: Keyframe Photo Review</span>';
      const selCount = (vid.selectedKeyframeIds || []).length || (vid.keyframes || []).length;
      if (counter) counter.textContent = `${selCount}/${(vid.keyframes || []).length} Photos Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Photos";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Synthesize BGM ➔`;
    } else if (vid.currentStage === 5) {
      if (title) title.innerHTML = '<i class="fa-solid fa-music text-cyan-500"></i><span>Stage 5: BGM Soundtrack Review</span>';
      if (counter) counter.textContent = `BGM Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll BGM";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Video Motion ➔`;
    } else if (vid.currentStage === 6) {
      if (title) title.innerHTML = '<i class="fa-solid fa-film text-purple-500"></i><span>Stage 6: Video Motion Curation</span>';
      if (counter) counter.textContent = `${(vid.selectedMotionClipIds || []).length || (vid.motion_clips || []).length} Clips Ready`;
      if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Motion";
      if (advBtn) advBtn.textContent = `➡️ Next Stage: Render Final 4K Master ➔`;
    } else {
      dock.classList.add("hidden");
    }
    return;
  }
  if (vid.currentStage === 1) {
    if (title) title.innerHTML = `<i class="fa-solid fa-scroll text-amber-500"></i><span>Stage 1: Script &amp; Storyboard Review</span>`;
    if (counter) counter.textContent = `Script Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Script";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Keyframes ➔`;
  } else if (vid.currentStage === 2) {
    if (title) title.innerHTML = '<i class="fa-solid fa-images text-blue-500"></i><span>Stage 2: Keyframe Photo Review</span>';
    const selCount = (vid.selectedKeyframeIds || []).length || (vid.keyframes || []).length;
    if (counter) counter.textContent = `${selCount}/${(vid.keyframes || []).length} Photos Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Photos";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Synthesize Audio & BGM ➔`;
  } else if (vid.currentStage === 3) {
    if (title) title.innerHTML = '<i class="fa-solid fa-wave-square text-cyan-500"></i><span>Stage 3: Audio &amp; BGM Stems Review</span>';
    const sCount = (vid.audio_stems || []).length;
    if (counter) counter.textContent = sCount > 0 ? `${sCount} Stems Ready` : `Stems Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Audio & BGM";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Generate Video Motion ➔`;
  } else if (vid.currentStage === 4) {
    if (title) title.innerHTML = '<i class="fa-solid fa-film text-purple-500"></i><span>Stage 4: Video Motion Curation</span>';
    if (counter) counter.textContent = `${(vid.selectedMotionClipIds || []).length || (vid.motion_clips || []).length} Clips Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-roll Motion";
    if (advBtn) advBtn.textContent = `➡️ Next Stage: Render Final 4K Master ➔`;
  } else if (isRelax && hasMaster && lpEds.length === 0) {
    if (title) title.innerHTML = '<i class="fa-solid fa-hourglass-half text-indigo-400"></i><span>Stage 6: 3-Hour Broadcast Master</span>';
    if (counter) counter.textContent = `4K Master Ready`;
    if (rerollBtn) rerollBtn.textContent = "🔄 Re-render Master";
    if (advBtn) {
      advBtn.innerHTML = `<span>⚡ Approve &amp; Generate 3-Hour Broadcast ➔</span>`;
      const btn = document.getElementById("btn-dock-advance");
      if (btn) btn.onclick = () => { if (typeof approveAndGenerateLongPlay === "function") approveAndGenerateLongPlay(); };
    }
  } else {
    dock.classList.add("hidden");
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
