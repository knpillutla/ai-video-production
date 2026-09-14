// CineAI Studio: Master Video Player & Preview Controller
let currentlyPlayingVideo = null;

function playStudioVideo(id) {
  const vid = studioVideos.find(v => v.id === id);
  if (!vid) return;
  currentlyPlayingVideo = vid;

  const titleEl = document.getElementById("player-modal-title");
  const metaEl = document.getElementById("player-modal-meta");
  const costEl = document.getElementById("player-modal-cost");
  const publishBtn = document.getElementById("player-modal-publish-btn");
  const videoEl = document.getElementById("player-modal-video");

  if (titleEl) titleEl.textContent = `${vid.id}: ${vid.title}`;
  if (metaEl) metaEl.textContent = `${vid.format} • ${vid.style} • ${vid.language}`;
  if (costEl) costEl.textContent = `Cost: ${vid.costStr} • Started: ${formatTimestamp(vid.startedAt)} • Completed: ${formatTimestamp(vid.completedAt)}`;

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

  if (videoEl) {
    videoEl.currentTime = 0;
    videoEl.play().catch(() => {});
  }
  openModal("video-player-modal");
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
