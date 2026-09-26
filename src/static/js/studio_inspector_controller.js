// CineAI Studio: Panel 3 Master Artifact Inspector Controller
let activeInspectorTab = "stems";
let currentActiveInspectorEpisode = {
  id: "EP-001",
  title: "Sub-Zero Mountain Blizzard Outside with Camp Fire ~ Warm Fireplace Inside",
  videoType: "Relaxation & Soundscapes",
  genre: "Relaxation & Soundscapes",
  format: "4K UHD",
  fps: "24 FPS",
  cost_usd: 0.14,
  story_topic: "Extreme mountain blizzard howling outside stone shelter while pine wood crackles in hearth with hot herbal tea steam"
};

function switchInspectorView(tabKey) {
  activeInspectorTab = tabKey;
  const btnStems = document.getElementById("btn-inspector-view-stems");
  const btnDist = document.getElementById("btn-inspector-view-dist");
  const viewStems = document.getElementById("inspector-view-stems");
  const viewDist = document.getElementById("inspector-view-distribution");

  if (tabKey === "stems") {
    if (btnStems) btnStems.className = "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow";
    if (btnDist) btnDist.className = "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (viewStems) viewStems.classList.remove("hidden");
    if (viewDist) viewDist.classList.add("hidden");
  } else {
    if (btnStems) btnStems.className = "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
    if (btnDist) btnDist.className = "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow";
    if (viewStems) viewStems.classList.add("hidden");
    if (viewDist) viewDist.classList.remove("hidden");
  }
}

function selectMasterVideoRender(url, label, cardEl) {
  const video = document.getElementById("studio-panel-video");
  const badge = document.getElementById("panel-video-res-badge");
  if (video && url) {
    video.src = url;
    video.play().catch(() => {});
  }
  if (badge && label) {
    badge.textContent = label;
  }
  const container = document.getElementById("panel-section-master-videos");
  if (container) {
    container.querySelectorAll(".group").forEach(c => {
      c.classList.remove("border-emerald-500", "border-2");
      c.classList.add("border", "border-slate-300", "dark:border-slate-700/80");
    });
  }
  if (cardEl) {
    const cardBox = cardEl.querySelector(".group") || cardEl;
    cardBox.classList.remove("border", "border-slate-300", "dark:border-slate-700/80");
    cardBox.classList.add("border-emerald-500", "border-2");
  }
}

function openActiveEpisodeModal() {
  if (!currentActiveInspectorEpisode) return;
  const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id || "EP-001";

  if (typeof viewEpisodeArtifacts === "function") {
    let found = (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) ? studioVideos.find(v => v.id === epId) : null;
    if (!found) {
      found = {
        id: epId,
        jobId: `job_${epId.toLowerCase().replace(/[^a-z0-9]/g, "_")}`,
        title: currentActiveInspectorEpisode.title || "Master Video",
        videoType: currentActiveInspectorEpisode.videoType || currentActiveInspectorEpisode.genre || "Relaxation & Soundscapes",
        formatType: currentActiveInspectorEpisode.format || "Long (16:9)",
        styleType: currentActiveInspectorEpisode.styleType || "Realistic (Photoreal)",
        tierName: currentActiveInspectorEpisode.tierName || "Balanced ($0.14)",
        language: currentActiveInspectorEpisode.language || "English (en)",
        cost: currentActiveInspectorEpisode.cost_usd || 0.14,
        concept: currentActiveInspectorEpisode.story_topic || currentActiveInspectorEpisode.concept || ""
      };
      if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
        studioVideos.push(found);
      }
    }
    viewEpisodeArtifacts(found.id);
  }
}

function renderInspectorFromVideo(vid) {
  if (!vid) return;
  currentActiveInspectorEpisode = vid;

  // Multi-line header elements
  const epIdEl = document.getElementById("panel-header-ep-id");
  const typeBadge = document.getElementById("panel-header-type-badge");
  const metaEl = document.getElementById("panel-header-meta");
  const titleEl = document.getElementById("panel-header-title");
  const storyEl = document.getElementById("panel-header-story");

  const epId = vid.id || vid.episode_id || "EP-001";
  const type = vid.videoType || vid.genre || "Relaxation & Soundscapes";
  const cost = (vid.cost_usd !== undefined && vid.cost_usd !== null) ? ` • $${Number(vid.cost_usd).toFixed(2)}` : "";
  const meta = `${vid.format || "4K UHD"} • ${vid.fps || "24 FPS"}${cost}`;
  const title = vid.title || "Master Video";
  const story = vid.story_topic || vid.concept || vid.theme || "High-fidelity cinematic master and synthesized stem artifacts";

  if (epIdEl) epIdEl.textContent = epId;
  if (typeBadge) typeBadge.textContent = type;
  if (metaEl) metaEl.textContent = meta;
  if (titleEl) titleEl.textContent = title;
  if (storyEl) storyEl.textContent = `Story: ${story}`;

  // Section 0: Master 4K Video
  const video = document.getElementById("studio-panel-video");
  const overlay = document.getElementById("studio-panel-processing-overlay");
  if (video) {
    if (vid.status === "completed" || !vid.status) {
      if (overlay) overlay.classList.add("hidden");
      const targetSrc = vid.videoUrl || "/static/videos/preview_master.mp4";
      if (!video.src.endsWith(targetSrc)) video.src = targetSrc;
    } else {
      if (overlay) overlay.classList.remove("hidden");
    }
  }

  // Section 1: Keyframe Photos (Horizontal Thumbnails with Scene Names & Latency)
  const imagesContainer = document.getElementById("panel-section-images");
  const keyframes = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : [];
  const shotNames = ["Shot 1: Wide", "Shot 2: River", "Shot 3: Canopy", "Shot 4: Sunset"];
  const photoTimings = ["3.4s", "3.8s", "3.2s", "4.1s"];

  if (imagesContainer && keyframes.length > 0) {
    imagesContainer.innerHTML = keyframes.map((kf, i) => `
      <div class="flex flex-col items-center gap-0.5 w-full">
        <div class="group relative w-full h-14 rounded-lg overflow-hidden bg-slate-900 border border-slate-300 dark:border-slate-700/80 hover:border-blue-500 cursor-pointer transition shadow" onclick="previewLightboxImage('${kf}')">
          <img src="${kf}" alt="Shot ${i + 1}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
          <span class="absolute top-0.5 right-0.5 px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-blue-300">4K Flux</span>
        </div>
        <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center leading-tight">${shotNames[i] || `Shot ${i + 1}`}</span>
        <span class="text-[8px] font-mono text-blue-600 dark:text-blue-400">⏱ ${photoTimings[i % photoTimings.length]}</span>
      </div>
    `).join("");
  }

  // Section 3: Audio Stems
  const audioPlayer = document.getElementById("panel-audio-player");
  const bgmPlayer = document.getElementById("panel-bgm-player");
  const ttsPlayer = document.getElementById("panel-tts-player");
  if (audioPlayer && vid.audioUrl) audioPlayer.src = vid.audioUrl;
  if (bgmPlayer && vid.bgmUrl) bgmPlayer.src = vid.bgmUrl;
  if (ttsPlayer && vid.ttsUrl) ttsPlayer.src = vid.ttsUrl;

  // Distribution tab
  const ytTitle = document.getElementById("dist-yt-title");
  const ytDesc = document.getElementById("dist-yt-desc");
  if (ytTitle) ytTitle.value = `${vid.title} - 4K Nature & Relaxation Master`;
  if (ytDesc) ytDesc.value = `Experience ${vid.title} in Ultra HD 4K.\n\n00:00 - Introduction\n01:30 - Glacial Stream Ambient\n03:45 - Sunset Horizon\n\n#4K #Nature #Relaxation #CineAI`;
}

function copyActiveScript() {
  const vid = currentActiveInspectorEpisode || ((typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === selectedLedgerVideoId));
  const text = vid ? (vid.script || vid.script_text || vid.concept || vid.title) : "No script available.";
  navigator.clipboard.writeText(text);
  showStudioModal({ title: "Script Copied", message: "Screenplay text copied to clipboard.", nextStep: "Ready for review or external syndication." });
}

if (window.StudioBus) {
  window.StudioBus.on("episode:selected", (ep) => {
    renderInspectorFromVideo({
      id: ep.episode_id,
      title: ep.title,
      genre: ep.genre || "Relaxation & Soundscapes",
      format: ep.format || "4K UHD",
      fps: ep.fps || "24 FPS",
      cost_usd: ep.cost_usd,
      story_topic: ep.story_topic,
      status: "completed",
      videoUrl: ep.artifacts?.master_music || "/static/videos/preview_master.mp4",
      script: ep.script_text
    });
  });
}

