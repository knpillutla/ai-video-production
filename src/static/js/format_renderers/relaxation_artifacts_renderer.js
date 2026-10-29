/**
 * Relaxation Artifacts Renderer (6 Decoupled Stages).
 * Strictly manages Stage 1 (Storyboard) to Stage 6 (Long-Play Hours).
 */
(function(window) {
  "use strict";

  function renderRelaxationArtifacts(vid) {
    if (!vid) return;

    // 1. Stage 1: Ambiance Concept & Storyboard
    renderRelaxStoryboardStage(vid);

    // 2. Stage 2: Keyframe Photos
    renderRelaxKeyframesStage(vid);

    // 3. Stage 3: Binaural ASMR & 432Hz Soundscapes
    renderRelaxAudioStage(vid);

    // 4. Stage 4: Procedural Video Motion
    renderRelaxMotionStage(vid);

    // 5. Stage 5: 4K Master Video
    renderRelaxMasterStage(vid);

    // 6. Stage 6: Long-Play Broadcast Hours
    if (typeof updateInspectorLongPlaySection === "function") {
      updateInspectorLongPlaySection(vid);
    }
  }

  function renderRelaxStoryboardStage(vid) {
    const el = document.getElementById("panel-section-relax-script");
    const statusEl = document.getElementById("panel-relax-script-status");
    if (!el) return;

    const sb = vid.storyboard || vid.script || vid.screenplay || null;
    const scenes = sb?.scenes || [];

    if (sb && scenes.length > 0) {
      if (statusEl) {
        statusEl.textContent = `${scenes.length} Scenes Ready`;
        statusEl.className = "text-emerald-500 font-mono text-xs font-bold";
      }
      el.innerHTML = `
        <div class="p-2 bg-[var(--card-subtle)] border border-[var(--border)] rounded-xl flex items-center justify-between text-xs">
          <span class="font-bold text-[var(--text)] flex items-center gap-1.5 truncate">
            <i class="fa-solid fa-mountain-sun text-[10px] text-emerald-500"></i>
            <span class="truncate">${sb.title || vid.title || "Biophilic Soundscape Storyboard"}</span>
          </span>
          <div class="flex items-center gap-1.5 shrink-0">
            <span class="font-mono text-[10px] text-[var(--text-muted)]">${scenes.length} Perspectives</span>
            <button type="button" onclick="openScriptDrawer('visual')" class="btn-runway-secondary py-0.5 px-2 text-[10px] font-bold">
              View Scenes
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
          <span>No ambient storyboard generated yet.</span>
          <button type="button" onclick="advanceToScriptStage(currentActiveInspectorEpisode)" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold">
            Generate Storyboard
          </button>
        </div>
      `;
    }
  }

  function renderRelaxKeyframesStage(vid) {
    const countEl = document.getElementById("panel-relax-images-count");
    const container = document.getElementById("panel-section-relax-images");
    if (!container) return;

    const keyframes = vid.keyframes || vid.images || [];
    if (countEl) countEl.textContent = `${keyframes.length} Shots`;

    if (keyframes.length > 0) {
      container.innerHTML = keyframes.map((k, idx) => `
        <div class="relative group rounded-lg overflow-hidden border border-[var(--border)] bg-black aspect-video">
          <img src="${k.url || k}" alt="Shot ${idx + 1}" class="w-full h-full object-cover">
          <div class="absolute bottom-1 left-1 px-1 py-0.2 rounded bg-black/70 text-[9px] font-mono text-white">Shot ${idx + 1}</div>
        </div>
      `).join("");
    } else {
      container.innerHTML = `
        <div class="col-span-full p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-center text-[11px] text-[var(--text-muted)]">
          Keyframe diffusion photos not rendered yet.
        </div>
      `;
    }
  }

  function renderRelaxAudioStage(vid) {
    const container = document.getElementById("panel-section-relax-audio");
    if (!container) return;
    const stems = vid.audio_stems || vid.audioStems || [];
    if (stems.length > 0) {
      container.innerHTML = stems.map(s => `
        <div class="p-1.5 bg-[var(--card-subtle)] border border-[var(--border)] rounded-lg text-xs space-y-1">
          <div class="flex items-center justify-between text-[11px] font-bold text-[var(--text)]">
            <span class="truncate">${s.name || s.stem_type || 'Ambiance Master'}</span>
            <span class="text-[9px] font-mono text-emerald-500 font-bold">432Hz</span>
          </div>
          <audio controls class="w-full h-6 rounded" src="${s.url}" preload="metadata"></audio>
        </div>
      `).join("");
    } else {
      container.innerHTML = `
        <div class="col-span-full p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-center text-[11px] text-[var(--text-muted)]">
          Procedural ASMR &amp; 432Hz audio stems awaiting synthesis.
        </div>
      `;
    }
  }

  function renderRelaxMotionStage(vid) {
    const container = document.getElementById("panel-section-relax-raw-videos");
    const countEl = document.getElementById("panel-relax-raw-videos-count");
    if (!container) return;
    const clips = vid.raw_videos || vid.motion_clips || vid.motionClips || [];
    if (countEl) countEl.textContent = `${clips.length} Clips`;
    if (clips.length > 0) {
      container.innerHTML = clips.map((c, idx) => `
        <div class="rounded-lg overflow-hidden border border-[var(--border)] bg-black aspect-video relative">
          <video src="${c.url || c}" class="w-full h-full object-cover" muted loop onmouseover="this.play()" onmouseout="this.pause()"></video>
          <div class="absolute bottom-1 left-1 px-1 py-0.2 rounded bg-black/70 text-[9px] font-mono text-white">Clip ${idx + 1}</div>
        </div>
      `).join("");
    } else {
      container.innerHTML = `
        <div class="col-span-full p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-center text-[11px] text-[var(--text-muted)]">
          Procedural drone &amp; diffusion motion clips awaiting rendering.
        </div>
      `;
    }
  }

  function renderRelaxMasterStage(vid) {
    const container = document.getElementById("panel-section-relax-master-videos");
    if (!container) return;
    const vUrl = vid.video_url || vid.videoUrl;
    if (vUrl) {
      container.innerHTML = `
        <div class="col-span-full p-2 bg-[var(--card-subtle)] border border-[var(--border)] rounded-xl flex items-center justify-between text-xs">
          <span class="font-bold text-emerald-500 flex items-center gap-1.5">
            <i class="fa-solid fa-circle-check"></i>
            <span>4K Broadcast Master Rendered</span>
          </span>
          <button type="button" onclick="playMasterVideoInHero('${vUrl}')" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold">
            Play 4K Master
          </button>
        </div>
      `;
    } else {
      container.innerHTML = `
        <div class="col-span-full p-2 bg-[var(--card-subtle)] border border-dashed border-[var(--border)] rounded-xl text-center text-[11px] text-[var(--text-muted)]">
          4K broadcast master not assembled yet.
        </div>
      `;
    }
  }

  window.RelaxationArtifactsRenderer = {
    render: renderRelaxationArtifacts,
  };
})(window);
