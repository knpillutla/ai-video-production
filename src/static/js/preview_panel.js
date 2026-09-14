// CineAI Studio: Right Preview Panel Controller with Fullscreen & Playback Controls
let selectedLedgerVideoId = "EP-003";

function selectLedgerVideo(id) {
  const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === id);
  if (!vid) return;

  selectedLedgerVideoId = id;
  updateLedgerRowHighlights();

  const panel = document.getElementById("studio-preview-panel");
  if (panel && panel.classList.contains("hidden")) {
    panel.classList.remove("hidden");
  }

  // Header & Title
  const headerTitle = document.getElementById("panel-header-title");
  const vidTitle = document.getElementById("panel-video-title");
  const vidConcept = document.getElementById("panel-video-concept");
  if (headerTitle) headerTitle.textContent = `${vid.id}: ${vid.title}`;
  if (vidTitle) vidTitle.textContent = vid.title;
  if (vidConcept) vidConcept.textContent = vid.concept || "Autonomous multi-agent generative video.";

  // Status Badge
  const statusBadge = document.getElementById("panel-video-status-badge");
  if (statusBadge) {
    statusBadge.textContent = vid.status.toUpperCase();
    statusBadge.className = "px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider shrink-0 ";
    if (vid.status === "completed") {
      statusBadge.className += "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40";
    } else if (vid.status === "processing") {
      statusBadge.className += "bg-blue-500/20 text-blue-400 border border-blue-500/40 animate-pulse";
    } else {
      statusBadge.className += "bg-amber-500/20 text-amber-400 border border-amber-500/40";
    }
  }

  // Metadata pills
  const metaJobId = document.getElementById("panel-meta-jobid");
  const metaVideoType = document.getElementById("panel-meta-videotype");
  const metaFormatStyle = document.getElementById("panel-meta-format-style");
  const metaTierCost = document.getElementById("panel-meta-tier-cost");
  if (metaJobId) metaJobId.textContent = vid.jobId || `job_${vid.id.toLowerCase()}`;
  if (metaVideoType) metaVideoType.textContent = vid.videoType || "Web Series";
  if (metaFormatStyle) metaFormatStyle.textContent = `${vid.formatType || vid.format || "16:9"} • ${vid.styleType || vid.style || "Realistic"}`;
  if (metaTierCost) metaTierCost.textContent = `${vid.tierKey || "Balanced"} • ${vid.costStr || "$0.14 USD"}`;

  // Timestamps
  const tsCreated = document.getElementById("panel-ts-created");
  const tsStarted = document.getElementById("panel-ts-started");
  const tsCompleted = document.getElementById("panel-ts-completed");
  const tsPublished = document.getElementById("panel-ts-published");
  const fmt = typeof formatTimestamp === "function" ? formatTimestamp : (t => t ? new Date(t).toLocaleString() : "—");
  if (tsCreated) tsCreated.textContent = fmt(vid.createdAt);
  if (tsStarted) tsStarted.textContent = fmt(vid.startedAt);
  if (tsCompleted) tsCompleted.textContent = fmt(vid.completedAt);
  if (tsPublished) {
    tsPublished.textContent = vid.publishedAt ? fmt(vid.publishedAt) : "—";
    tsPublished.className = vid.publishedAt ? "text-red-400 font-bold" : "text-gray-500";
  }

  // YouTube action button
  const ytBtn = document.getElementById("panel-btn-youtube");
  const ytText = document.getElementById("panel-btn-youtube-text");
  if (ytBtn && ytText) {
    if (vid.youtubeStatus === "published") {
      ytBtn.className = "flex-1 py-2 bg-red-900/30 border border-red-500/40 text-red-300 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 cursor-default";
      ytText.textContent = "Published to YouTube";
    } else {
      ytBtn.className = "flex-1 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition shadow";
      ytText.textContent = "1-Click Publish";
    }
  }

  // Video Element & Processing Overlay
  const video = document.getElementById("studio-panel-video");
  const overlay = document.getElementById("studio-panel-processing-overlay");
  const playBtn = document.getElementById("btn-panel-play-video");
  const playText = document.getElementById("panel-play-text");
  const playIcon = document.getElementById("panel-play-icon");

  if (video) {
    if (vid.status === "completed") {
      if (overlay) overlay.classList.add("hidden");
      const targetSrc = vid.videoUrl || "/static/videos/preview_master.mp4";
      if (!video.src.endsWith(targetSrc)) {
        video.src = targetSrc;
        video.load();
      }
      if (playBtn) playBtn.disabled = false;
    } else {
      if (overlay) overlay.classList.remove("hidden");
      const title = document.getElementById("studio-panel-processing-title");
      const sub = document.getElementById("studio-panel-processing-subtitle");
      if (title) title.textContent = vid.status === "processing" ? "AI Video Pipeline Synthesizing" : "Job Queued in Producer Engine";
      if (sub) sub.textContent = vid.status === "processing" ? "Generating scenes, TTS stems & composing 1080p master..." : "Waiting for model worker slot...";
      if (playBtn) playBtn.disabled = true;
      video.pause();
    }
  }

  if (playText) playText.textContent = "Play";
  if (playIcon) playIcon.className = "fa-solid fa-play text-[10px]";
}

function updateLedgerRowHighlights() {
  const rows = document.querySelectorAll("#studio-video-history-rows tr");
  rows.forEach(tr => {
    const rowId = tr.getAttribute("data-video-id");
    if (rowId === selectedLedgerVideoId) {
      tr.classList.add("bg-indigo-950/40", "border-l-4", "border-indigo-500", "ring-1", "ring-indigo-500/30");
    } else {
      tr.classList.remove("bg-indigo-950/40", "border-l-4", "border-indigo-500", "ring-1", "ring-indigo-500/30");
    }
  });
}

function toggleRightPanelFullscreen() {
  const panel = document.getElementById("studio-preview-panel");
  const icon = document.getElementById("panel-expand-icon");
  const text = document.getElementById("panel-expand-text");
  if (!panel) return;

  const isFullscreen = panel.classList.toggle("panel-fullscreen");
  if (isFullscreen) {
    if (icon) icon.className = "fa-solid fa-compress text-indigo-400";
    if (text) text.textContent = "Exit Fullscreen";
    document.body.style.overflow = "hidden";
  } else {
    if (icon) icon.className = "fa-solid fa-expand text-indigo-400";
    if (text) text.textContent = "Expand Panel";
    document.body.style.overflow = "";
  }
}

function expandVideoFullscreen() {
  const video = document.getElementById("studio-panel-video");
  if (!video) return;

  if (video.requestFullscreen) {
    video.requestFullscreen();
  } else if (video.webkitRequestFullscreen) {
    video.webkitRequestFullscreen();
  } else if (video.msRequestFullscreen) {
    video.msRequestFullscreen();
  }
}

function togglePanelVideoPlay() {
  const video = document.getElementById("studio-panel-video");
  const playText = document.getElementById("panel-play-text");
  const playIcon = document.getElementById("panel-play-icon");
  if (!video) return;

  if (video.paused) {
    video.play().then(() => {
      if (playText) playText.textContent = "Pause";
      if (playIcon) playIcon.className = "fa-solid fa-pause text-[10px]";
    }).catch(e => console.warn("Autoplay blocked:", e));
  } else {
    video.pause();
    if (playText) playText.textContent = "Play";
    if (playIcon) playIcon.className = "fa-solid fa-play text-[10px]";
  }
}

function toggleRightPanelVisibility() {
  const panel = document.getElementById("studio-preview-panel");
  if (!panel) return;
  panel.classList.toggle("hidden");
}

function publishSelectedPanelVideo() {
  if (typeof publishVideoToYouTube === "function" && selectedLedgerVideoId) {
    const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === selectedLedgerVideoId);
    if (vid) publishVideoToYouTube(vid.jobId);
    selectLedgerVideo(selectedLedgerVideoId);
  }
}

// ESC Key listener to exit panel fullscreen
document.addEventListener("keydown", function(e) {
  if (e.key === "Escape") {
    const panel = document.getElementById("studio-preview-panel");
    if (panel && panel.classList.contains("panel-fullscreen")) {
      toggleRightPanelFullscreen();
    }
  }
});
