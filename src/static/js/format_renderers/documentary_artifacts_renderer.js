/**
 * Documentary Artifacts Renderer (7 Decoupled Stages).
 * Strictly manages Stage 1 (Raw Story - 22 Chapters) to Stage 7 (4K Master).
 * Features live horizontal progress bar during story dossier synthesis.
 */
(function(window) {
  "use strict";

  let isStoryLoading = false;
  let storyLoadingInfo = { msg: "", pct: 25, details: "" };

  function setStoryLoadingState(isLoading, message, pct, details) {
    isStoryLoading = !!isLoading;
    if (isStoryLoading) {
      storyLoadingInfo = {
        msg: message || "Synthesizing 22-Chapter Master Story Dossier...",
        pct: pct !== undefined ? pct : 25,
        details: details || "Compiling Capital, Population, Area, Governance & Living Culture..."
      };
    }

    const el = document.getElementById("panel-section-story");
    const statusEl = document.getElementById("panel-story-status");
    if (!el) return;

    if (isStoryLoading) {
      if (statusEl) {
        statusEl.textContent = "Synthesizing...";
        statusEl.className = "text-sky-500 font-mono text-xs font-bold animate-pulse";
      }
      const existingContainer = document.getElementById("story-progress-container");
      if (existingContainer) {
        document.getElementById("story-progress-title")?.replaceChildren(document.createTextNode(storyLoadingInfo.msg));
        const pctEl = document.getElementById("story-progress-pct"); if (pctEl) pctEl.textContent = `${storyLoadingInfo.pct}%`;
        const fillEl = document.getElementById("story-progress-bar-fill"); if (fillEl) fillEl.style.width = `${storyLoadingInfo.pct}%`;
        const detailsEl = document.getElementById("story-progress-details"); if (detailsEl) detailsEl.textContent = storyLoadingInfo.details;
        return;
      }
      el.innerHTML = `<div id="story-progress-container" class="p-2.5 bg-[var(--card-subtle)] border border-sky-500/30 rounded-xl space-y-2 shadow-sm"><div class="flex items-center justify-between text-xs"><span class="font-bold text-sky-500 flex items-center gap-1.5 truncate"><i class="fa-solid fa-spinner fa-spin text-xs"></i><span id="story-progress-title" class="truncate">${storyLoadingInfo.msg}</span></span><span id="story-progress-pct" class="font-mono text-[10px] text-[var(--accent)] font-bold shrink-0">${storyLoadingInfo.pct}%</span></div><div class="w-full bg-[var(--border)] h-2 rounded-full overflow-hidden relative"><div id="story-progress-bar-fill" class="h-full bg-gradient-to-r from-indigo-500 via-sky-500 to-emerald-500 rounded-full animate-pulse transition-all duration-300" style="width: ${storyLoadingInfo.pct}%;"></div></div><div class="text-[10px] text-[var(--text-muted)] italic flex items-center justify-between"><span id="story-progress-details" class="truncate">${storyLoadingInfo.details}</span><span class="font-mono text-emerald-500 font-bold shrink-0">22 Sovereign Pillars</span></div></div>`;
    }
  }

  function renderEmptyDocumentaryState() {
    isStoryLoading = false;
    const el = document.getElementById("panel-section-story"), statusEl = document.getElementById("panel-story-status");
    if (statusEl) { statusEl.textContent = "Waiting"; statusEl.className = "text-[var(--text-muted)] font-mono text-xs"; }
    if (el) el.innerHTML = `<div class="p-3 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-center space-y-1"><div class="text-xs font-semibold text-[var(--text-muted)]"><i class="fa-solid fa-compass text-xs text-[var(--accent)] mr-1"></i>No 22-Chapter Story Synthesized Yet</div><div class="text-[10px] text-[var(--text-muted)]">Select genre options or type a country prompt, then click <strong>New Video</strong>.</div></div>`;
    const nStat = document.getElementById("panel-narration-status"); if (nStat) nStat.textContent = "Pending";
    const nSec = document.getElementById("panel-section-doc-narration"); if (nSec) nSec.innerHTML = `<div class="p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-[11px] text-[var(--text-muted)] text-center">Narration audio not synthesized yet.</div>`;
    const spStat = document.getElementById("panel-screenplay-status"); if (spStat) spStat.textContent = "Pending";
    const spSec = document.getElementById("panel-section-doc-screenplay"); if (spSec) spSec.innerHTML = `<div class="p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-[11px] text-[var(--text-muted)] text-center">Screenplay awaiting narration timing.</div>`;
  }

  function renderDocumentaryArtifacts(vid) {
    if (!vid || vid.id === "NEW" || vid.status === "idle") {
      renderEmptyDocumentaryState();
      return;
    }
    renderDocStoryStage(vid);
    renderDocNarrationStage(vid);
    renderDocScreenplayStage(vid);
    _syncStageHeaderButtons(vid);
    if (typeof renderKeyframesList === "function") renderKeyframesList(vid);
    if (typeof renderAudioStemsList === "function") renderAudioStemsList(vid);
    if (typeof renderMotionClipsList === "function") renderMotionClipsList(vid);
    if (typeof renderMasterVideosList === "function") renderMasterVideosList(vid);
  }

  function _syncStageHeaderButtons(vid) {
    const sp = vid.screenplay || vid.raw_screenplay || vid.script;
    const hasSp = Boolean(sp && ((sp.chapters && sp.chapters.length > 0) || (sp.scenes && sp.scenes.length > 0)));
    const bgmBtn = document.getElementById("btn-generate-bgm-header");
    if (bgmBtn) {
      const stems = vid.audio_stems || [];
      const hasBgm = stems.some(s => (s.filename && s.filename.includes("soundtrack")) || (s.name && s.name.toLowerCase().includes("suno")));
      bgmBtn.disabled = !hasSp;
      bgmBtn.className = hasSp ? (hasBgm ? "btn-runway-secondary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1" : "btn-runway-primary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1") : "btn-runway-secondary opacity-40 cursor-not-allowed pointer-events-none py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
      bgmBtn.title = hasSp ? (hasBgm ? "Regenerate BGM" : "Synthesize BGM") : "Requires Stage 3 Screenplay";
      bgmBtn.innerHTML = hasBgm ? '<i class="fa-solid fa-arrows-rotate text-[8px] mr-1"></i>Regenerate BGM' : '<i class="fa-solid fa-music text-[9px] mr-1"></i>Suno BGM';
    }
  }

  function renderDocStoryStage(vid) {
    const el = document.getElementById("panel-section-story");
    const statusEl = document.getElementById("panel-story-status");
    if (!el) return;

    if (isStoryLoading && (!vid.story && !vid.raw_story)) return;

    const story = vid.story || vid.raw_story || null;
    const chapters = story?.chapters || [];
    const chCount = chapters.length || (vid.storyboard?.chapters?.length || 22);

    if (story && (chapters.length > 0 || story.synopsis || story.title)) {
      isStoryLoading = false;
      if (statusEl) {
        statusEl.textContent = "✓ Completed (22 Ch)";
        statusEl.className = "text-emerald-500 font-mono text-xs font-bold";
      }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-[var(--border)] rounded-xl flex items-center justify-between text-xs">
          <span class="font-bold text-[var(--text)] flex items-center gap-1.5 truncate">
            <i class="fa-solid fa-scroll text-[10px] text-amber-500"></i>
            <span class="truncate">${story.title || vid.title || "360° Sovereign Dossier"}</span>
          </span>
          <div class="flex items-center gap-1.5 shrink-0">
            <span class="font-mono text-[10px] text-emerald-500 font-bold">✓ Completed (${chCount} Ch)</span>
            <button type="button" onclick="openScriptDrawer('story')" class="btn-runway-secondary py-0.5 px-2 text-[10px] font-bold flex items-center gap-1" title="View Full Story Chapters in Popup Drawer">
              <i class="fa-solid fa-book-open text-[9px]"></i>
              <span>View Story (${chCount} Ch)</span>
            </button>
          </div>
        </div>
      `;
    } else {
      if (statusEl) {
        statusEl.textContent = "Idle";
        statusEl.className = "text-[var(--text-muted)] font-mono text-xs";
      }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl flex items-center justify-between text-xs text-[var(--text-muted)]">
          <span class="flex items-center gap-1.5">
            <i class="fa-solid fa-circle-info text-[10px]"></i>
            <span>No raw story generated yet.</span>
          </span>
          <button type="button" onclick="autoGenerateDocStoryForEpisode(currentActiveInspectorEpisode)" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold">
            Generate Story
          </button>
        </div>
      `;
    }
  }

  function _renderProgressBox(title, sub, pct, color) {
    return `
      <div class="p-2.5 bg-gradient-to-r from-${color}-500/10 via-indigo-500/10 to-blue-500/10 border border-${color}-500/30 rounded-xl space-y-1.5 shadow-sm">
        <div class="flex items-center justify-between text-xs">
          <span class="font-bold text-${color}-700 dark:text-${color}-300 flex items-center gap-1.5 truncate">
            <i class="fa-solid fa-circle-notch fa-spin text-${color}-500 text-xs"></i>
            <span class="truncate">${title}</span>
          </span>
          <span class="font-mono text-[10px] font-bold text-${color}-600 dark:text-${color}-400">${pct}%</span>
        </div>
        <div class="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div class="bg-gradient-to-r from-blue-600 via-indigo-600 to-${color}-600 h-full rounded-full transition-all duration-300" style="width: ${pct}%"></div>
        </div>
        <div class="text-[10px] text-[var(--text-muted)] font-mono truncate">${sub}</div>
      </div>
    `;
  }

  function renderDocNarrationStage(vid) {
    const el = document.getElementById("panel-section-narration");
    const statusEl = document.getElementById("panel-narration-status");
    const headerBtn = document.getElementById("btn-generate-narration-header");
    if (!el) return;

    const audioStems = vid.audio_stems || [];
    const narrationStem = audioStems.find(s => s.stem_type === "narration" || s.role === "narration" || s.type === "azure_speech" || (s.name && s.name.toLowerCase().includes("narration")) || (s.filename && s.filename.includes("narration")));
    const isProcessing = vid.status === "processing" && (vid.currentStage === 2 || vid._isNarrationProcessing);

    if (narrationStem) {
      if (headerBtn) {
        headerBtn.disabled = false;
        headerBtn.className = "btn-runway-secondary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
        headerBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate mr-1 text-[8px]"></i>Regenerate Narration';
        headerBtn.title = "Re-synthesize narration audio";
      }
      if (statusEl) { statusEl.textContent = "Ready (Neural TTS)"; statusEl.className = "text-emerald-500 font-mono text-xs font-bold"; }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-[var(--border)] rounded-xl flex items-center justify-between text-xs">
          <div class="flex items-center gap-2 truncate">
            <i class="fa-solid fa-microphone-lines text-emerald-500 text-sm"></i>
            <div class="truncate">
              <div class="font-bold text-[var(--text)] truncate">Neural Broadcast Narration</div>
              <div class="text-[10px] text-[var(--text-muted)] font-mono">${narrationStem.voice_name || 'en-GB-RyanNeural'} • 48kHz</div>
            </div>
          </div>
          <audio controls src="${narrationStem.url || narrationStem.file_path}" class="h-6 w-32 shrink-0"></audio>
        </div>
      `;
    } else if (isProcessing) {
      if (headerBtn) {
        headerBtn.disabled = true;
        headerBtn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin mr-1"></i>Synthesizing...';
        headerBtn.className = "btn-runway-secondary opacity-70 pointer-events-none py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
      }
      if (statusEl) { statusEl.textContent = "Synthesizing..."; statusEl.className = "text-purple-500 font-mono text-xs font-bold animate-pulse"; }
      el.innerHTML = _renderProgressBox("Synthesizing Voiceover Narration...", "Broadcast Speech • 48kHz Audio • Breathable Chapter Intervals", vid.progress || 30, "purple");
    } else {
      const hasStory = Boolean(vid.story || vid.raw_story);
      if (headerBtn) {
        headerBtn.disabled = !hasStory;
        headerBtn.innerHTML = '<i class="fa-solid fa-bolt mr-1"></i>Generate Narration';
        headerBtn.className = hasStory
          ? "btn-runway-primary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1"
          : "btn-runway-secondary opacity-40 cursor-not-allowed pointer-events-none py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
        headerBtn.title = hasStory ? "Synthesize Voiceover Narration" : "Requires Stage 1 Story Script";
      }
      if (statusEl) { statusEl.textContent = hasStory ? "Ready to Synthesize" : "Awaiting Story"; statusEl.className = hasStory ? "text-amber-500 font-mono text-xs font-bold" : "text-[var(--text-muted)] font-mono text-xs"; }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl flex items-center justify-between text-xs text-[var(--text-muted)]">
          <span class="flex items-center gap-1.5"><i class="fa-solid fa-microphone text-[10px]"></i><span>${hasStory ? "Narration ready to synthesize." : "Narration awaiting story synthesis."}</span></span>
          <button type="button" onclick="advanceToNarrationStage(currentActiveInspectorEpisode)" class="${hasStory ? 'btn-runway-primary' : 'btn-runway-secondary opacity-40 cursor-not-allowed pointer-events-none'} py-0.5 px-2 text-[10px] font-bold shadow-sm" ${hasStory ? '' : 'disabled'}>
            <i class="fa-solid fa-bolt mr-1"></i>Generate Narration
          </button>
        </div>
      `;
    }
  }

  function renderDocScreenplayStage(vid) {
    const el = document.getElementById("panel-section-script");
    const statusEl = document.getElementById("panel-script-status");
    if (!el) return;

    const screenplay = vid.screenplay || vid.raw_screenplay || vid.script || null;
    const rawChapters = screenplay?.chapters || [];
    const shots = rawChapters.flatMap(c => c.shots || []);
    const totalShots = screenplay?.total_shots || shots.length || (rawChapters.length > 0 ? rawChapters.reduce((a, c) => a + (c.shots?.length || 1), 0) : 0);
    const isProcessing = vid.status === "processing" && (vid.currentStage === 3 || vid._isScreenplayProcessing);
    const hdrBtn = document.getElementById("btn-generate-screenplay-header");

    if (screenplay && (shots.length > 0 || totalShots > 0)) {
      if (statusEl) { statusEl.textContent = `${totalShots} Shots Ready`; statusEl.className = "text-emerald-500 font-mono text-xs font-bold"; }
      if (hdrBtn) {
        hdrBtn.disabled = false;
        hdrBtn.textContent = "Regenerate Script";
        hdrBtn.className = "btn-runway-secondary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
        hdrBtn.title = "Regenerate screenplay from narration audio";
      }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-[var(--border)] rounded-xl flex items-center justify-between text-xs">
          <div class="flex items-center gap-2 truncate">
            <i class="fa-solid fa-clapperboard text-[var(--accent)] text-sm"></i>
            <div class="truncate">
              <div class="font-bold text-[var(--text)] truncate">Directorial 3-Shot Screenplay</div>
              <div class="text-[10px] text-[var(--text-muted)] font-mono">${rawChapters.length || 5} Chapters • ${totalShots} Multi-Angle Shots</div>
            </div>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button type="button" onclick="openScriptDrawer('screenplay')" class="btn-runway-secondary py-0.5 px-2 text-[10px] font-bold">View Screenplay</button>
            <button type="button" onclick="advanceToKeyframesStage(currentActiveInspectorEpisode, 'zimage', true)" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold flex items-center gap-1" title="Advance to Stage 4: Keyframe Photos">
              <span>Next: Photos</span>
              <i class="fa-solid fa-arrow-right text-[8px]"></i>
            </button>
          </div>
        </div>
      `;
    } else if (isProcessing) {
      if (statusEl) { statusEl.textContent = "Synthesizing..."; statusEl.className = "text-blue-500 font-mono text-xs font-bold animate-pulse"; }
      el.innerHTML = _renderProgressBox("Formulating 3-Shot Screenplay from Narration (Gemini 2.5)...", "Wide • Medium • Macro Cinematic Triple-Angles • Timing-Locked to Narration", vid.progress || 45, "blue");
    } else {
      const hasNarration = Boolean(vid.audio_stems && vid.audio_stems.some(s => s.role === "narration" || s.filename === "spoken_narration.mp3" || s.stem_type === "narration" || s.type === "azure_speech"));
      if (hdrBtn) {
        hdrBtn.disabled = !hasNarration;
        hdrBtn.textContent = "Generate Script";
        hdrBtn.className = hasNarration
          ? "btn-runway-primary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1"
          : "btn-runway-secondary opacity-40 cursor-not-allowed pointer-events-none py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1";
        hdrBtn.title = hasNarration ? "Generate Screenplay from Narration" : "Requires Stage 2 Narration Audio";
      }
      if (statusEl) { statusEl.textContent = hasNarration ? "Ready to Synthesize" : "Awaiting Narration"; statusEl.className = hasNarration ? "text-amber-500 font-mono text-xs font-bold" : "text-[var(--text-muted)] font-mono text-xs"; }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl flex items-center justify-between text-xs text-[var(--text-muted)]">
          <span class="flex items-center gap-1.5"><i class="fa-solid fa-scroll text-[10px]"></i><span>${hasNarration ? "Screenplay ready to formulate shots." : "Screenplay awaiting narration timing."}</span></span>
          <button type="button" onclick="advanceToScriptStage(currentActiveInspectorEpisode)" class="${hasNarration ? 'btn-runway-primary' : 'btn-runway-secondary opacity-40 cursor-not-allowed pointer-events-none'} py-0.5 px-2 text-[10px] font-bold shadow-sm" ${hasNarration ? '' : 'disabled'}>
            <i class="fa-solid fa-clapperboard mr-1"></i>Generate Shots
          </button>
        </div>
      `;
    }
  }

  // Export to window
  window.DocumentaryArtifactsRenderer = {
    render: renderDocumentaryArtifacts,
    renderEmpty: renderEmptyDocumentaryState,
    renderStory: renderDocStoryStage,
    renderNarration: renderDocNarrationStage,
    renderScreenplay: renderDocScreenplayStage,
    setStoryLoading: setStoryLoadingState,
  };
})(window);
