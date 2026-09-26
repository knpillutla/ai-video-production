// CineAI Studio: Master Video Player & Preview Controller
let currentlyPlayingVideo = null;

function openVideoPopup(url, title, meta) {
  const videoEl = document.getElementById("player-modal-video");
  const titleEl = document.getElementById("player-modal-title");
  const metaEl = document.getElementById("player-modal-meta");
  const costEl = document.getElementById("player-modal-cost");
  const downloadBtn = document.getElementById("player-modal-download-btn");

  if (titleEl) titleEl.textContent = title || "Video Master Player";
  if (metaEl) metaEl.textContent = meta || "4K Master Render • Single-Pass Lossless";
  if (costEl) costEl.textContent = "Autonomous AI Production Master";
  if (downloadBtn && url) {
    downloadBtn.href = url;
    downloadBtn.download = (title || "video_master").replace(/[^a-zA-Z0-9_-]/g, "_") + ".mp4";
  }

  if (videoEl && url) {
    if (!videoEl.src.endsWith(url)) {
      videoEl.src = url;
      videoEl.load();
    }
    videoEl.currentTime = 0;
    videoEl.play().catch(() => {});
  }
  openModal("video-player-modal");
}

function playStudioVideo(id) {
  const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === id);
  if (!vid) return;
  currentlyPlayingVideo = vid;

  const targetUrl = vid.videoUrl || vid.editions?.[0]?.url || "/static/videos/preview_master.mp4";
  const title = `${vid.id}: ${vid.title}`;
  const meta = `${vid.format || '16:9'} • ${vid.style || 'Photoreal'} • ${vid.language || 'English'}`;
  
  openVideoPopup(targetUrl, title, meta);

  const costEl = document.getElementById("player-modal-cost");
  if (costEl) costEl.textContent = `Cost: ${vid.costStr || '$1.6400 USD'} • Started: ${formatTimestamp(vid.startedAt)} • Completed: ${formatTimestamp(vid.completedAt)}`;

  const publishBtn = document.getElementById("player-modal-publish-btn");
  if (publishBtn) {
    if (vid.youtubeStatus === "published") {
      publishBtn.className = "px-5 py-2 bg-emerald-700/80 text-white font-bold rounded-xl shadow-lg flex items-center gap-1.5 cursor-default";
      publishBtn.innerHTML = '<i class="fa-solid fa-check"></i> <span>Published to YouTube</span>';
      publishBtn.disabled = true;
    } else {
      publishBtn.className = "px-5 py-2 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-xl shadow-lg flex items-center gap-1.5 transition";
      publishBtn.innerHTML = '<i class="fa-brands fa-youtube"></i> <span>Publish to YouTube</span>';
      publishBtn.disabled = false;
    }
  }
}

function closeVideoPlayerModal() {
  const videoEl = document.getElementById("player-modal-video");
  if (videoEl) videoEl.pause();
  closeModal("video-player-modal");
}

function publishCurrentPlayingVideo() {
  if (currentlyPlayingVideo) {
    publishVideoToYouTube(currentlyPlayingVideo.jobId);
    playStudioVideo(currentlyPlayingVideo.id);
  }
}
