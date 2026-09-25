// CineAI Studio: Right Preview Panel Controller with 6-Section Artifact Inspector
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
  if (headerTitle) headerTitle.textContent = `${vid.id}: ${vid.title}`;
  if (vidTitle) vidTitle.textContent = vid.title;

  // SECTION 0: MASTER 4K VIDEO PLAYER
  const video = document.getElementById("studio-panel-video");
  const overlay = document.getElementById("studio-panel-processing-overlay");

  if (video) {
    if (vid.status === "completed") {
      if (overlay) overlay.classList.add("hidden");
      const targetSrc = vid.videoUrl || "/static/videos/preview_master.mp4";
      if (!video.src.endsWith(targetSrc)) {
        video.src = targetSrc;
        video.load();
      }
    } else {
      if (overlay) overlay.classList.remove("hidden");
      const title = document.getElementById("studio-panel-processing-title");
      const sub = document.getElementById("studio-panel-processing-subtitle");
      if (title) title.textContent = vid.status === "processing" ? "AI Pipeline Synthesizing" : "Job Queued";
      if (sub) sub.textContent = vid.status === "processing" ? "Rendering 4K Lanczos Master..." : "Waiting in queue...";
      video.pause();
    }
  }

  // SECTION 1: KEYFRAME IMAGES (HORIZONTAL)
  const imagesContainer = document.getElementById("panel-section-images");
  const imagesCountEl = document.getElementById("panel-images-count");
  const defaultKeyframes = [
    "/static/img/defaults/scene_00.jpg",
    "/static/img/defaults/scene_01.jpg",
    "/static/img/defaults/scene_02.jpg",
    "/static/img/defaults/scene_03.jpg"
  ];
  const keyframes = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : defaultKeyframes;

  if (imagesCountEl) imagesCountEl.textContent = `${keyframes.length} Frames`;
  if (imagesContainer) {
    imagesContainer.innerHTML = keyframes.map((kf, i) => `
      <div class="group relative w-32 h-20 rounded-lg overflow-hidden bg-slate-900 border border-slate-800 hover:border-indigo-500/70 shrink-0 cursor-pointer transition shadow" onclick="previewLightboxImage('${kf}')">
        <img src="${kf}" alt="Keyframe ${i}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" onerror="this.src='/static/img/placeholder_frame.jpg'">
        <span class="absolute bottom-1 left-1 px-1.5 py-0.5 rounded bg-black/70 text-[9px] font-mono text-gray-200">Scene ${i}</span>
        <span class="absolute top-1 right-1 w-4 h-4 rounded-full bg-blue-600/80 text-white flex items-center justify-center text-[8px] opacity-0 group-hover:opacity-100 transition"><i class="fa-solid fa-magnifying-glass"></i></span>
      </div>
    `).join("");
  }

  // SECTION 2: RAW MOTION VIDEOS (HORIZONTAL)
  const rawVideosContainer = document.getElementById("panel-section-raw-videos");
  const rawVideosCountEl = document.getElementById("panel-raw-videos-count");
  const defaultClips = [
    { name: "Scene 0 (Wide)", url: vid.videoUrl || "/static/videos/preview_master.mp4", model: "Kling v3 Pro" },
    { name: "Scene 1 (Water)", url: vid.videoUrl || "/static/videos/preview_master.mp4", model: "Wan 2.1" },
    { name: "Scene 2 (Lounge)", url: vid.videoUrl || "/static/videos/preview_master.mp4", model: "Hunyuan 1080p" }
  ];
  const rawClips = (vid.rawVideos && vid.rawVideos.length > 0) ? vid.rawVideos : defaultClips;

  if (rawVideosCountEl) rawVideosCountEl.textContent = `${rawClips.length} Clips`;
  if (rawVideosContainer) {
    rawVideosContainer.innerHTML = rawClips.map((clip, i) => {
      const clipUrl = typeof clip === "string" ? clip : (clip.url || vid.videoUrl);
      const clipName = typeof clip === "string" ? `Clip ${i}` : (clip.name || `Scene ${i}`);
      const modelName = clip.model || (i === 1 ? "Kling v3 Pro" : "Wan 2.1");
      return `
        <div class="relative w-32 h-20 rounded-lg overflow-hidden bg-slate-900 border border-slate-800 hover:border-purple-500/70 shrink-0 group transition shadow">
          <video src="${clipUrl}" class="w-full h-full object-cover" muted preload="metadata" onmouseover="this.play()" onmouseout="this.pause();this.currentTime=0;"></video>
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex flex-col justify-between p-1">
            <span class="px-1 py-0.5 rounded bg-purple-900/60 text-[8px] font-mono text-purple-200 self-start border border-purple-500/30">${modelName}</span>
            <div class="flex items-center justify-between text-[9px] text-gray-200">
              <span class="truncate font-bold">${clipName}</span>
              <i class="fa-solid fa-play text-[8px] text-indigo-400"></i>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  // SECTION 3: AUDIO & FOLEY STEM
  const audioPlayer = document.getElementById("panel-audio-player");
  const audioStemName = document.getElementById("panel-audio-stem-name");
  const audioSrc = vid.foleyUrl || vid.audioUrl || "/static/audio/foley_sample.wav";
  if (audioPlayer) audioPlayer.src = audioSrc;
  if (audioStemName) audioStemName.textContent = vid.foleyName || `${vid.id.toLowerCase()}_foley_48k.wav`;

  // SECTION 4: BGM SOUNDTRACK (SUNO V3.5)
  const bgmPlayer = document.getElementById("panel-bgm-player");
  const bgmStemName = document.getElementById("panel-bgm-stem-name");
  const bgmSrc = vid.bgmUrl || "/static/audio/suno_ambient_master.wav";
  if (bgmPlayer) bgmPlayer.src = bgmSrc;
  if (bgmStemName) bgmStemName.textContent = vid.bgmName || "suno_ambient_waterfall_48k.wav";

  // SECTION 5: TTS NARRATION AUDIO
  const ttsPlayer = document.getElementById("panel-tts-player");
  const ttsStemName = document.getElementById("panel-tts-stem-name");
  const ttsStatusBadge = document.getElementById("panel-tts-status-badge");
  const ttsSrc = vid.ttsUrl || "/static/audio/voice_sample.wav";
  if (ttsPlayer) ttsPlayer.src = ttsSrc;
  if (ttsStemName) ttsStemName.textContent = vid.ttsName || `voice_${vid.langCode || 'en'}_master.wav`;
  if (ttsStatusBadge) ttsStatusBadge.textContent = vid.enableVoiceOver === false ? "Muted" : "Azure Neural HD";

  // SECTION 6: SUBTITLES & CAPTIONS
  const subtitleName = document.getElementById("panel-subtitle-name");
  if (subtitleName) subtitleName.textContent = vid.subtitleName || `${vid.id.toLowerCase()}_subtitles.ass`;
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

function previewLightboxImage(src) {
  const modal = document.createElement("div");
  modal.className = "fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4 cursor-pointer";
  modal.onclick = () => modal.remove();
  modal.innerHTML = `
    <div class="relative max-w-4xl max-h-[90vh] rounded-2xl overflow-hidden border border-slate-700 shadow-2xl">
      <img src="${src}" class="w-full h-full object-contain">
      <div class="absolute top-3 right-3 px-3 py-1 bg-black/60 text-white rounded-lg text-xs font-bold">Click anywhere to close</div>
    </div>
  `;
  document.body.appendChild(modal);
}

function downloadActiveSubtitle() {
  const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === selectedLedgerVideoId);
  const subContent = `[Script Info]\nTitle: ${vid ? vid.title : 'Subtitles'}\nScriptType: v4.00+\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\nDialogue: 0,0:00:00.50,0:00:05.00,Default,,0,0,0,,Welcome to this tranquil nature sanctuary.`;
  const blob = new Blob([subContent], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${selectedLedgerVideoId || 'episode'}_subtitles.ass`;
  a.click();
}

function toggleRightPanelFullscreen() {
  const panel = document.getElementById("studio-preview-panel");
  const icon = document.getElementById("panel-expand-icon");
  const text = document.getElementById("panel-expand-text");
  if (!panel) return;

  const isFullscreen = panel.classList.toggle("panel-fullscreen");
  if (isFullscreen) {
    if (icon) icon.className = "fa-solid fa-compress text-indigo-400";
    if (text) text.textContent = "Exit";
    document.body.style.overflow = "hidden";
  } else {
    if (icon) icon.className = "fa-solid fa-expand text-indigo-400";
    if (text) text.textContent = "Expand";
    document.body.style.overflow = "";
  }
}

function expandVideoFullscreen() {
  const video = document.getElementById("studio-panel-video");
  if (!video) return;
  if (video.requestFullscreen) video.requestFullscreen();
  else if (video.webkitRequestFullscreen) video.webkitRequestFullscreen();
  else if (video.msRequestFullscreen) video.msRequestFullscreen();
}

function toggleRightPanelVisibility() {
  const panel = document.getElementById("studio-preview-panel");
  if (!panel) return;
  panel.classList.toggle("hidden");
}
