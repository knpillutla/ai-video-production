// CineAI Studio: Master Video & Photo Artifact Player Controller (With Fullscreen Support)
let currentlyPlayingVideo = null;

function openArtifactMediaPopup(type, url, title, meta, badge) {
  const videoEl = document.getElementById("player-modal-video");
  const imgEl = document.getElementById("player-modal-image");
  const titleEl = document.getElementById("player-modal-title");
  const metaEl = document.getElementById("player-modal-meta");
  const badgeEl = document.getElementById("player-modal-badge");
  const costEl = document.getElementById("player-modal-cost");
  const downloadBtn = document.getElementById("player-modal-download-btn");
  const iconEl = document.getElementById("player-modal-icon");
  const publishBtn = document.getElementById("player-modal-publish-btn");

  if (titleEl) titleEl.textContent = title || "Artifact Viewer";
  if (metaEl) metaEl.textContent = meta || "4K Master Render • Single-Pass Lossless";
  if (badgeEl) badgeEl.textContent = badge || (type === "image" ? "FLUX 1.1 Pro (4K)" : "4K UHD");
  if (costEl) costEl.textContent = "Autonomous AI Studio Production Artifact";

  if (downloadBtn && url) {
    downloadBtn.href = url;
    const ext = type === "image" ? ".jpg" : ".mp4";
    downloadBtn.download = (title || "artifact_media").replace(/[^a-zA-Z0-9_-]/g, "_") + ext;
  }

  if (type === "image") {
    if (videoEl) { videoEl.pause(); videoEl.classList.add("hidden"); }
    if (imgEl) { imgEl.src = url; imgEl.classList.remove("hidden"); }
    if (iconEl) iconEl.className = "fa-solid fa-image text-blue-400";
    if (publishBtn) publishBtn.classList.add("hidden");
  } else {
    if (imgEl) { imgEl.classList.add("hidden"); imgEl.src = ""; }
    if (videoEl) {
      videoEl.classList.remove("hidden");
      if (!videoEl.src.endsWith(url)) {
        videoEl.src = url;
        videoEl.load();
      }
      videoEl.currentTime = 0;
      videoEl.play().catch(() => {});
    }
    if (iconEl) iconEl.className = "fa-solid fa-play text-indigo-400";
    if (publishBtn) publishBtn.classList.remove("hidden");
  }

  openModal("video-player-modal");
}

function openVideoPopup(url, title, meta) {
  openArtifactMediaPopup("video", url, title, meta, "4K Video");
}

function openImagePopup(url, title, meta) {
  openArtifactMediaPopup("image", url, title, meta, "4K Photo");
}

function toggleModalMediaFullscreen() {
  const container = document.getElementById("player-modal-media-container");
  if (!container) return;
  if (!document.fullscreenElement) {
    if (container.requestFullscreen) {
      container.requestFullscreen();
    } else if (container.webkitRequestFullscreen) {
      container.webkitRequestFullscreen();
    }
  } else {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    }
  }
}

function playStudioVideo(id, channelId) {
  const vid = findStudioEpisodeById(id, channelId);
  if (!vid) return;
  currentlyPlayingVideo = vid;

  const targetUrl = vid.videoUrl || vid.editions?.[0]?.url || "/static/videos/preview_master.mp4";
  const title = `${vid.id}: ${vid.title}`;
  const meta = `${vid.format || '16:9'} • ${vid.style || 'Photoreal'} • ${vid.language || 'English'}`;
  
  openVideoPopup(targetUrl, title, meta);

  const costEl = document.getElementById("player-modal-cost");
  if (costEl) costEl.textContent = `Cost: ${vid.costStr || '$0.02 USD'} • Channel: ${vid.channelId || vid.channel_id || 'CineAI'}`;
}

function closeVideoPlayerModal() {
  const videoEl = document.getElementById("player-modal-video");
  if (videoEl) videoEl.pause();
  closeModal("video-player-modal");
}

function publishCurrentPlayingVideo() {
  if (!currentlyPlayingVideo) return;
  const epId = currentlyPlayingVideo.episode_id || currentlyPlayingVideo.id || "EP-001";
  const chSlug = currentlyPlayingVideo.channel_id || currentlyPlayingVideo.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  const title = currentlyPlayingVideo.title || "4K Master Experience";
  if (typeof openPublishModal === "function") {
    openPublishModal(epId, chSlug, title);
  }
}

