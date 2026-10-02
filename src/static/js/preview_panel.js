// CineAI Studio: Video Production Ledger Right Inspector Panel Controller
let selectedLedgerVideoId = null;
let selectedLedgerVideoChannelId = null;
let activeLedgerInspectorTab = "stems";
let activePlayingAudioStemId = null;

function switchLedgerInspectorView(tabKey) {
  activeLedgerInspectorTab = tabKey;
  const isStems = (tabKey === "stems");
  const btnStems = document.getElementById("btn-ledger-inspector-stems");
  const btnDist = document.getElementById("btn-ledger-inspector-dist");
  const viewStems = document.getElementById("ledger-inspector-view-stems");
  const viewDist = document.getElementById("ledger-inspector-view-distribution");

  if (btnStems) btnStems.className = isStems ? "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow" : "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
  if (btnDist) btnDist.className = !isStems ? "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white shadow" : "px-2 py-0.5 text-[10px] font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded";
  if (viewStems) viewStems.classList.toggle("hidden", !isStems);
  if (viewDist) viewDist.classList.toggle("hidden", isStems);
}

function selectLedgerMasterVideoRender(url, label, cardEl) {
  const video = document.getElementById("studio-panel-video");
  const badge = document.getElementById("ledger-panel-video-badge");
  if (video && url) {
    video.src = url;
    video.play().catch(() => { });
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

function openActiveVideoInPopup() {
  const video = document.getElementById("studio-panel-video");
  const vid = findStudioEpisodeById(selectedLedgerVideoId, selectedLedgerVideoChannelId);
  const src = (video && video.src) ? video.src : (vid?.videoUrl || "/static/videos/preview_master.mp4");
  const title = vid ? `${vid.id}: ${vid.title}` : "Master Video";
  const meta = vid ? `${vid.format || '4K UHD'} • ${vid.style || 'Cinematic'}` : "4K Master Render";
  if (typeof openVideoPopup === "function") openVideoPopup(src, title, meta);
}

function toggleAudioStemPlay(audioId, btnEl) {
  const audio = document.getElementById(audioId);
  if (!audio) return;
  if (activePlayingAudioStemId && activePlayingAudioStemId !== audioId) {
    stopAudioStemPlay(activePlayingAudioStemId);
  }
  const mainVideo = document.getElementById("studio-panel-video");
  if (mainVideo) mainVideo.pause();

  if (audio.paused) {
    audio.play().then(() => {
      activePlayingAudioStemId = audioId;
      if (btnEl) btnEl.innerHTML = '<i class="fa-solid fa-pause text-amber-500"></i> Pause';
    }).catch(() => { });
  } else {
    audio.pause();
    if (btnEl) btnEl.innerHTML = '<i class="fa-solid fa-play text-amber-500"></i> Play';
  }
}

function stopAudioStemPlay(audioId) {
  const audio = document.getElementById(audioId);
  if (audio) { audio.pause(); audio.currentTime = 0; }
  const btn = document.querySelector(`button[data-audio-id="${audioId}"]`);
  if (btn) btn.innerHTML = '<i class="fa-solid fa-play text-amber-500"></i> Play';
  if (activePlayingAudioStemId === audioId) activePlayingAudioStemId = null;
}

function clearLedgerInspector() {
  selectedLedgerVideoId = null;
  selectedLedgerVideoChannelId = null;
  updateLedgerRowHighlights();
  const epIdEl = document.getElementById("ledger-header-ep-id");
  const typeBadge = document.getElementById("ledger-header-type-badge");
  const metaEl = document.getElementById("ledger-header-meta");
  const titleEl = document.getElementById("ledger-header-title");
  const storyEl = document.getElementById("ledger-header-story");
  if (epIdEl) epIdEl.textContent = "—";
  if (typeBadge) typeBadge.textContent = "No Episodes";
  if (metaEl) metaEl.textContent = "0 Videos";
  if (titleEl) titleEl.textContent = "No Episode Selected";
  if (storyEl) storyEl.textContent = "Select a channel or video from the ledger on the left to inspect master artifacts.";

  const video = document.getElementById("studio-panel-video");
  if (video) { video.src = ""; video.pause(); }

  const masterGrid = document.getElementById("ledger-panel-master-videos");
  if (masterGrid) masterGrid.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No master video renders available.</div>`;

  const imagesContainer = document.getElementById("panel-section-images");
  if (imagesContainer) imagesContainer.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No keyframe artifacts.</div>`;

  const rawVideosContainer = document.getElementById("panel-section-raw-videos");
  if (rawVideosContainer) rawVideosContainer.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No raw motion clips.</div>`;

  const audioStemsContainer = document.getElementById("panel-section-audio-stems");
  if (audioStemsContainer) audioStemsContainer.innerHTML = `<div class="col-span-full py-2.5 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No audio stems available.</div>`;
}

function selectLedgerVideo(id, channelId) {
  if (!id) { clearLedgerInspector(); return; }
  const vid = findStudioEpisodeById(id, channelId);
  if (!vid) { clearLedgerInspector(); return; }

  selectedLedgerVideoId = id;
  selectedLedgerVideoChannelId = vid.channelId || vid.channel_id || channelId || null;
  updateLedgerRowHighlights();

  const panel = document.getElementById("studio-preview-panel");
  if (panel && panel.classList.contains("hidden")) panel.classList.remove("hidden");

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

  const video = document.getElementById("studio-panel-video");
  const overlay = document.getElementById("studio-panel-processing-overlay");
  const targetSrc = vid.videoUrl || (vid.editions?.[0]?.url) || "/static/videos/preview_master.mp4";
  if (video) {
    if (vid.status === "completed" || !vid.status) {
      if (overlay) overlay.classList.add("hidden");
      if (!video.src.endsWith(targetSrc)) { video.src = targetSrc; video.load(); }
    } else {
      if (overlay) overlay.classList.remove("hidden");
      video.pause();
    }
  }

  const masterGrid = document.getElementById("ledger-panel-master-videos");
  if (masterGrid) {
    let eds = (vid.editions && vid.editions.length > 0) ? [...vid.editions] : [];
    if (eds.length === 0 && vid.videoUrl) {
      eds.push({ edition_id: "m_primary", name: "🎵 Ambient Soundtrack (4K)", duration: vid.duration || "60s", format: "16:9 Master", url: vid.videoUrl, size_str: "⏱ 4K UHD" });
      if (vid.nature_video_url) {
        eds.push({ edition_id: "m_nature", name: "🌊 Pure Nature ASMR (4K)", duration: vid.duration || "60s", format: "16:9 Nature", url: vid.nature_video_url, size_str: "⏱ Pure Nature" });
      }
    }
    if (vid.long_play_editions && vid.long_play_editions.length > 0) {
      vid.long_play_editions.forEach(lp => {
        if (!eds.find(e => e.url === lp.url)) eds.push(lp);
      });
    }
    if (eds.length > 0) {
      masterGrid.innerHTML = eds.map((ed, i) => `
        <div class="flex flex-col items-center gap-0.5 cursor-pointer w-full" onclick="selectLedgerMasterVideoRender('${ed.url}', '${ed.name}', this)">
          <div class="group relative w-full h-14 rounded-lg overflow-hidden bg-gradient-to-br from-emerald-950 to-slate-900 border ${i === 0 ? 'border-2 border-emerald-500' : 'border border-slate-300 dark:border-slate-700/80'} hover:border-emerald-400 transition shadow flex flex-col justify-between p-1">
            <div class="flex items-center justify-between">
              <span class="px-1 py-0.2 rounded bg-emerald-900/90 text-[7px] font-mono text-emerald-200">${ed.format || '16:9'}</span>
              <button type="button" onclick="event.stopPropagation(); openVideoPopup('${ed.url}', '${ed.name}', '${ed.audio_mode || '4K Master'}');" class="p-0.5 rounded bg-black/60 hover:bg-emerald-600 text-white text-[8px] transition" title="Open in Popup"><i class="fa-solid fa-up-right-from-square"></i></button>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[7px] font-mono font-bold text-white bg-black/60 px-1 py-0.2 rounded truncate max-w-[85px]">${ed.audio_mode || 'Master'}</span>
              <i class="fa-solid fa-play text-[8px] text-emerald-400"></i>
            </div>
          </div>
          <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center leading-tight">${ed.name}</span>
          <span class="text-[8px] font-mono text-emerald-600 dark:text-emerald-400">${ed.size_str || ed.duration || '⏱ 4K Master'}</span>
        </div>
      `).join("");
    } else {
      masterGrid.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No master video renders available.</div>`;
    }
  }

  const imagesContainer = document.getElementById("panel-section-images");
  const imagesCountEl = document.getElementById("panel-images-count");
  const keyframes = (vid.keyframes && Array.isArray(vid.keyframes)) ? vid.keyframes : [];
  if (imagesCountEl) imagesCountEl.textContent = `${keyframes.length} Shots`;
  if (imagesContainer) {
    if (keyframes.length > 0) {
      imagesContainer.innerHTML = keyframes.map((kf, i) => {
        const url = (typeof kf === "object") ? kf.url : kf;
        const name = (typeof kf === "object") ? (kf.name || `Shot ${i + 1}`) : `Shot ${i + 1}`;
        return `
          <div class="flex flex-col items-center gap-0.5 w-full">
            <div class="group relative w-full h-14 rounded-lg overflow-hidden bg-slate-900 border border-slate-300 dark:border-slate-700/80 hover:border-blue-500 cursor-pointer transition shadow" onclick="previewLightboxImage('${url}')">
              <img src="${url}" alt="${name}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'w-full h-full flex items-center justify-center bg-slate-800 text-[10px] text-blue-400\\'><i class=\\'fa-solid fa-mountain-sun\\'></i></div>'">
              <span class="absolute top-0.5 right-0.5 px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-blue-300">4K Flux</span>
            </div>
            <span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center leading-tight">${name}</span>
            <span class="text-[8px] font-mono text-blue-600 dark:text-blue-400">⏱ ${(3.2 + (i * 0.3)).toFixed(1)}s</span>
          </div>
        `;
      }).join("");
    } else {
      imagesContainer.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No keyframe artifacts generated.</div>`;
    }
  }

  const rawVideosContainer = document.getElementById("panel-section-raw-videos");
  const rawCountEl = document.getElementById("panel-raw-videos-count");
  const motionClips = (vid.motion_clips && Array.isArray(vid.motion_clips)) ? vid.motion_clips : (vid.motionClips || []);
  if (rawCountEl) rawCountEl.textContent = `${motionClips.length} Clips`;
  if (rawVideosContainer) {
    if (motionClips.length > 0) {
      rawVideosContainer.innerHTML = motionClips.map((m, i) => {
        const url = (typeof m === "object") ? m.url : m, name = (typeof m === "object") ? (m.name || `Motion ${i + 1}`) : `Motion ${i + 1}`, model = (typeof m === "object") ? (m.model || (i === 0 ? "Kling Pro" : "Wan 2.1")) : "Kling Pro";
        const kf = (vid.keyframes && vid.keyframes[i]) ? vid.keyframes[i] : (vid.artifacts?.keyframes?.[i] || null);
        const kfUrl = (typeof kf === "object" && kf !== null) ? kf.url : (typeof kf === "string" ? kf : "");
        const posterUrl = (kfUrl && (kfUrl.startsWith("http") || kfUrl.startsWith("/static/") || kfUrl.startsWith("/storage/"))) ? kfUrl : (vid.thumbnailUrl || "");
        const bgStyle = posterUrl ? `background-image: url('${posterUrl}'); background-size: cover; background-position: center;` : "";
        return `<div class="flex flex-col items-center gap-0.5 w-full cursor-pointer group" onclick="selectLedgerMasterVideoRender('${url}', '${name}', this); if (typeof openVideoPopup === 'function') openVideoPopup('${url}', '${name} (${model})', '${model} 4K Motion Clip');" title="Click to play in Full Screen modal & preview"><div class="relative w-full h-14 rounded-lg overflow-hidden bg-gradient-to-br from-purple-950 to-slate-900 border border-slate-300 dark:border-slate-700/80 hover:border-purple-500 transition shadow flex flex-col justify-between p-1" style="${bgStyle}">${posterUrl ? '<div class="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition pointer-events-none"></div>' : ''}<div class="relative z-10 flex items-center justify-between"><span class="px-1 py-0.2 rounded bg-slate-900/90 text-[7px] font-mono text-purple-200 border border-slate-700">${model}</span><span class="px-1 py-0.2 rounded bg-black/70 text-[7px] font-mono text-purple-300">⏱ ${(11.2 + (i * 3.5)).toFixed(1)}s</span></div><div class="relative z-10 flex items-center justify-end"><div class="w-5 h-5 rounded-full bg-purple-600/90 hover:bg-purple-500 text-white flex items-center justify-center text-[7px] shadow transition transform group-hover:scale-110"><i class="fa-solid fa-play ml-0.5"></i></div></div></div><span class="text-[9px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center leading-tight">${name}</span></div>`;
      }).join("");
    } else {
      rawVideosContainer.innerHTML = `<div class="col-span-full py-3 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No raw motion clips generated.</div>`;
    }
  }

  const audioStemsContainer = document.getElementById("panel-section-audio-stems");
  const audioStems = (vid.audio_stems && Array.isArray(vid.audio_stems)) ? vid.audio_stems : [];
  if (audioStemsContainer) {
    if (audioStems.length > 0) {
      audioStemsContainer.innerHTML = audioStems.map((s, i) => {
        const audioId = `audio-stem-${i}`, iconCls = s.type === 'binaural_nature' ? 'fa-leaf text-emerald-500' : 'fa-music text-amber-500';
        return `<div class="p-2 bg-slate-50 dark:bg-slate-950/70 rounded-xl border border-slate-200 dark:border-slate-800 flex flex-col gap-1.5 shadow-sm"><div class="flex items-center justify-between gap-1 min-w-0"><div class="flex items-center gap-1.5 min-w-0"><i class="fa-solid ${iconCls} text-[11px] shrink-0"></i><span class="text-[10px] font-bold text-slate-800 dark:text-gray-200 truncate font-mono">${s.name || s.filename}</span></div><div class="flex items-center gap-1 shrink-0"><button type="button" data-audio-id="${audioId}" onclick="toggleAudioStemPlay('${audioId}', this)" class="px-2 py-0.5 bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-700 dark:text-amber-300 rounded text-[9px] font-bold inline-flex items-center gap-1 transition"><i class="fa-solid fa-play text-amber-500"></i> Play</button><button type="button" onclick="stopAudioStemPlay('${audioId}')" class="px-1.5 py-0.5 bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-700 dark:text-rose-300 rounded text-[9px] font-bold inline-flex items-center gap-1 transition" title="Stop audio"><i class="fa-solid fa-stop text-rose-500"></i> Stop</button></div></div><audio id="${audioId}" onended="stopAudioStemPlay('${audioId}')" controls preload="none" src="${s.url}" class="h-6 w-full rounded"></audio></div>`;
      }).join("");
    } else {
      audioStemsContainer.innerHTML = `<div class="col-span-full py-2.5 text-center text-xs text-slate-400 dark:text-gray-500 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-dashed border-slate-200 dark:border-slate-800">No audio stems available for this episode.</div>`;
    }
  }

  const ytTitle = document.getElementById("ledger-dist-yt-title");
  const ytDesc = document.getElementById("ledger-dist-yt-desc");
  if (ytTitle) ytTitle.value = `${vid.title} - 4K Master`;
  if (ytDesc) ytDesc.value = `Experience ${vid.title} in Ultra HD 4K.\n\n#4K #CineAI`;
}

function updateLedgerRowHighlights() {
  document.querySelectorAll("#studio-video-history-rows tr").forEach(tr => {
    const selected = tr.getAttribute("data-video-id") === selectedLedgerVideoId && tr.getAttribute("data-video-channel") === selectedLedgerVideoChannelId;
    tr.classList.toggle("bg-indigo-950/40", selected);
    tr.classList.toggle("border-l-4", selected);
    tr.classList.toggle("border-indigo-500", selected);
  });
}

function previewLightboxImage(src) {
  const modal = document.createElement("div");
  modal.className = "fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4 cursor-pointer";
  modal.onclick = () => modal.remove();
  modal.innerHTML = `<div class="relative max-w-4xl max-h-[90vh] rounded-2xl overflow-hidden border border-slate-700 shadow-2xl"><img src="${src}" class="w-full h-full object-contain"><div class="absolute top-3 right-3 px-3 py-1 bg-black/60 text-white rounded-lg text-xs font-bold">Click to close</div></div>`;
  document.body.appendChild(modal);
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
  if (panel) panel.classList.toggle("hidden");
}
