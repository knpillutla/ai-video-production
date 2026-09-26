// CineAI Studio: Video Production Ledger Right Inspector Panel Controller
let selectedLedgerVideoId = "EP-001";
let activeLedgerInspectorTab = "stems";

function switchLedgerInspectorView(tabKey) {
  activeLedgerInspectorTab = tabKey;
  const btnStems = document.getElementById("btn-ledger-inspector-stems");
  const btnDist = document.getElementById("btn-ledger-inspector-dist");
  const viewStems = document.getElementById("ledger-inspector-view-stems");
  const viewDist = document.getElementById("ledger-inspector-view-distribution");

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

function selectLedgerMasterVideoRender(url, label, cardEl) {
  const video = document.getElementById("studio-panel-video");
  const badge = document.getElementById("ledger-panel-video-badge");
  if (video && url) {
    video.src = url;
    video.play().catch(() => {});
  }
  if (badge && label) badge.textContent = label;

  const container = document.getElementById("ledger-panel-master-videos");
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

function openLedgerEpisodeModal() {
  if (typeof viewEpisodeArtifacts === "function" && selectedLedgerVideoId) {
    viewEpisodeArtifacts(selectedLedgerVideoId);
  }
}

function selectLedgerVideo(id) {
  const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === id);
  if (!vid) return;

  selectedLedgerVideoId = id;
  updateLedgerRowHighlights();

  const panel = document.getElementById("studio-preview-panel");
  if (panel && panel.classList.contains("hidden")) panel.classList.remove("hidden");

  // Multi-Line Header Population
  const epIdEl = document.getElementById("ledger-header-ep-id");
  const typeBadge = document.getElementById("ledger-header-type-badge");
  const metaEl = document.getElementById("ledger-header-meta");
  const titleEl = document.getElementById("ledger-header-title");
  const storyEl = document.getElementById("ledger-header-story");

  const cost = (vid.cost !== undefined) ? ` • $${Number(vid.cost).toFixed(2)}` : (vid.cost_usd ? ` • $${Number(vid.cost_usd).toFixed(2)}` : "");
  if (epIdEl) epIdEl.textContent = vid.id || "EP-001";
  if (typeBadge) typeBadge.textContent = vid.videoType || vid.genre || "Relaxation & Soundscapes";
  if (metaEl) metaEl.textContent = `${vid.format || vid.formatType || "4K UHD"} • ${vid.fps || "24 FPS"}${cost}`;
  if (titleEl) titleEl.textContent = vid.title || "Master Video";
  if (storyEl) storyEl.textContent = `Story: ${vid.concept || vid.story_topic || vid.theme || "High-fidelity cinematic master and synthesized stem artifacts"}`;

  // Section 0: Master 4K Video Player
  const video = document.getElementById("studio-panel-video");
  const overlay = document.getElementById("studio-panel-processing-overlay");
  if (video) {
    if (vid.status === "completed" || !vid.status) {
      if (overlay) overlay.classList.add("hidden");
      const targetSrc = vid.videoUrl || "/static/videos/preview_master.mp4";
      if (!video.src.endsWith(targetSrc)) { video.src = targetSrc; video.load(); }
    } else {
      if (overlay) overlay.classList.remove("hidden");
      video.pause();
    }
  }

  // Section 1: Keyframe Photos (Horizontal)
  const imagesContainer = document.getElementById("panel-section-images");
  const imagesCountEl = document.getElementById("panel-images-count");
  const keyframes = (vid.keyframes && vid.keyframes.length > 0) ? vid.keyframes : [];
  const shotNames = ["Shot 1: Wide", "Shot 2: River", "Shot 3: Canopy", "Shot 4: Sunset"];
  const photoTimings = ["3.4s", "3.8s", "3.2s", "4.1s"];

  if (imagesCountEl) imagesCountEl.textContent = keyframes.length > 0 ? `${keyframes.length} Shots` : "4 Shots";
  if (imagesContainer) {
    if (keyframes.length > 0) {
      imagesContainer.innerHTML = keyframes.map((kf, i) => `
        <div class="flex flex-col items-center gap-0.5 shrink-0">
          <div class="group relative w-20 h-14 rounded-lg overflow-hidden bg-slate-900 border border-slate-300 dark:border-slate-700/80 hover:border-blue-500 cursor-pointer transition shadow" onclick="previewLightboxImage('${kf}')">
            <img src="${kf}" alt="Shot ${i + 1}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
            <span class="absolute top-0.5 right-0.5 px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-blue-300">4K Flux</span>
          </div>
          <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate max-w-[80px] text-center leading-tight">${shotNames[i] || `Shot ${i + 1}`}</span>
          <span class="text-[8px] font-mono text-blue-600 dark:text-blue-400">⏱ ${photoTimings[i % photoTimings.length]}</span>
        </div>
      `).join("");
    } else {
      imagesContainer.innerHTML = [
        { icon: "fa-mountain-sun", text: "text-blue-400", bg: "from-blue-900 to-indigo-950", name: "Shot 1: Wide", time: "3.4s" },
        { icon: "fa-water", text: "text-emerald-400", bg: "from-emerald-900 to-teal-950", name: "Shot 2: River", time: "3.8s" },
        { icon: "fa-tree", text: "text-amber-400", bg: "from-amber-900 to-emerald-950", name: "Shot 3: Canopy", time: "3.2s" },
        { icon: "fa-sun", text: "text-rose-400", bg: "from-rose-900 to-purple-950", name: "Shot 4: Sunset", time: "4.1s" }
      ].map(s => `
        <div class="flex flex-col items-center gap-0.5 shrink-0">
          <div class="group relative w-20 h-14 rounded-lg overflow-hidden bg-gradient-to-br ${s.bg} border border-slate-300 dark:border-slate-700/80 hover:border-blue-500 cursor-pointer transition shadow flex items-center justify-center">
            <i class="fa-solid ${s.icon} ${s.text} text-sm"></i>
            <span class="absolute top-0.5 right-0.5 px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-blue-300">4K Flux</span>
          </div>
          <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate max-w-[80px] text-center leading-tight">${s.name}</span>
          <span class="text-[8px] font-mono text-blue-600 dark:text-blue-400">⏱ ${s.time}</span>
        </div>
      `).join("");
    }
  }

  // Section 2: Raw Motion Video Clips (Horizontal)
  const rawVideosContainer = document.getElementById("panel-section-raw-videos");
  const motionShots = [
    { name: "Shot 1: Aerial", model: "Kling Pro", dur: "5s", gradient: "from-purple-950 to-slate-900", border: "hover:border-purple-500", text: "text-purple-400", time: "14.5s" },
    { name: "Shot 2: Water", model: "Wan 2.1", dur: "10s", gradient: "from-cyan-950 to-slate-900", border: "hover:border-cyan-500", text: "text-cyan-400", time: "22.8s" },
    { name: "Shot 3: Canopy", model: "Hunyuan", dur: "5s", gradient: "from-indigo-950 to-slate-900", border: "hover:border-indigo-500", text: "text-indigo-400", time: "11.2s" }
  ];
  if (rawVideosContainer) {
    rawVideosContainer.innerHTML = motionShots.map((m) => `
      <div class="flex flex-col items-center gap-0.5 shrink-0">
        <div class="relative w-20 h-14 rounded-lg overflow-hidden bg-gradient-to-br ${m.gradient} border border-slate-300 dark:border-slate-700/80 ${m.border} transition shadow flex flex-col justify-between p-1">
          <div class="flex items-center justify-between">
            <span class="px-1 py-0.2 rounded bg-slate-900/90 text-[7px] font-mono text-purple-200 border border-slate-700">${m.model}</span>
            <span class="text-[7px] font-mono text-gray-300">${m.dur}</span>
          </div>
          <div class="flex items-center justify-end"><i class="fa-solid fa-play text-[8px] ${m.text}"></i></div>
        </div>
        <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate max-w-[80px] text-center leading-tight">${m.name}</span>
        <span class="text-[8px] font-mono text-purple-600 dark:text-purple-400">⏱ ${m.time}</span>
      </div>
    `).join("");
  }

  // Section 3: Audio & Vocal Stems
  const audioPlayer = document.getElementById("panel-audio-player");
  const bgmPlayer = document.getElementById("panel-bgm-player");
  const ttsPlayer = document.getElementById("panel-tts-player");
  if (audioPlayer && vid.audioUrl) audioPlayer.src = vid.audioUrl;
  if (bgmPlayer && vid.bgmUrl) bgmPlayer.src = vid.bgmUrl;
  if (ttsPlayer && vid.ttsUrl) ttsPlayer.src = vid.ttsUrl;

  // Distribution tab
  const ytTitle = document.getElementById("ledger-dist-yt-title");
  const ytDesc = document.getElementById("ledger-dist-yt-desc");
  if (ytTitle) ytTitle.value = `${vid.title} - 4K Nature & Relaxation Master`;
  if (ytDesc) ytDesc.value = `Experience ${vid.title} in Ultra HD 4K.\n\n00:00 - Introduction\n01:30 - Glacial Stream Ambient\n03:45 - Sunset Horizon\n\n#4K #Nature #Relaxation #CineAI`;
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

function copyLedgerScript() {
  const vid = (typeof studioVideos !== "undefined" ? studioVideos : []).find(v => v.id === selectedLedgerVideoId);
  const text = vid ? (vid.script || vid.concept || vid.title) : "No script available.";
  navigator.clipboard.writeText(text);
  if (typeof showStudioModal === "function") {
    showStudioModal({ title: "Script Copied", message: "Screenplay text copied to clipboard.", nextStep: "Ready for review or external syndication." });
  }
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
  if (!panel) return;
  const isFullscreen = panel.classList.toggle("panel-fullscreen");
  if (icon) icon.className = isFullscreen ? "fa-solid fa-compress text-xs text-indigo-400" : "fa-solid fa-expand text-xs";
}

function toggleRightPanelVisibility() {
  const panel = document.getElementById("studio-preview-panel");
  if (!panel) return;
  panel.classList.toggle("hidden");
}

