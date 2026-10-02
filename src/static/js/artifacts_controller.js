// CineAI Studio: Artifacts & Episode Details Inspector Controller
function viewEpisodeArtifacts(epOrId, channelId) {
  let vid = null;
  if (typeof epOrId === "object" && epOrId !== null) vid = epOrId;
  else if (typeof epOrId === "string") {
    if (typeof findStudioEpisodeById === "function") vid = findStudioEpisodeById(epOrId, channelId);
    if (!vid && typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
      const matches = channelArchiveEpisodes.filter(v => v.episode_id === epOrId);
      vid = channelId
        ? matches.find(v => v.channel_id === channelId)
        : (matches.length === 1 ? matches[0] : null);
    }
  }
  if (!vid && typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode &&
      (typeof epOrId !== "string" || currentActiveInspectorEpisode.id === epOrId || currentActiveInspectorEpisode.episode_id === epOrId)) {
    vid = currentActiveInspectorEpisode;
  }
  if (!vid) return;

  const epId = vid.id || vid.episode_id || "EP-001";
  const setEl = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };

  setEl("artifacts-modal-ep-id", epId);
  setEl("artifacts-modal-title", vid.title || "Master Episode");
  setEl("artifacts-modal-job-id", `Traceability UUID: ${vid.jobId || ('job_' + epId.toLowerCase() + '_prod')}`);
  setEl("artifacts-modal-story", vid.story_topic || vid.concept || vid.theme || vid.title || "Master production story beat.");
  setEl("artifacts-modal-lang", vid.language || "English (en)");
  setEl("artifacts-spec-duration", `${vid.duration || (vid.durationSeconds ? vid.durationSeconds + 's' : '10s')} • ${vid.fps || '24 FPS'}`);
  setEl("artifacts-spec-format", vid.format || "4K UHD (CRF 22)");
  setEl("artifacts-spec-cost", `$${Number(vid.cost_usd || vid.cost || 0.02).toFixed(2)} USD`);

  const badgesEl = document.getElementById("artifacts-meta-badges");
  if (badgesEl) {
    const chName = (vid.channel_id === "silent_hearth" || vid.channelId === "silent_hearth") ? "Silent Hearth" : ((vid.channel_id === "earth_serenade" || vid.channelId === "earth_serenade") ? "Earth Serenade" : "CineAI Docs");
    badgesEl.innerHTML = `
      <span class="px-2 py-0.5 rounded-md font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">${chName}</span>
      <span class="px-2 py-0.5 rounded-md font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40">${vid.genre || vid.videoType || "Relaxation & ASMR"}</span>
      <span class="px-2 py-0.5 rounded-md font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">${vid.executionMode === 'test' ? '⚡ Test Draft' : 'Master Broadcast'}</span>
      <span class="px-2 py-0.5 rounded-md font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">${vid.pipelineStrategy === 'manual' ? '🛠️ Manual Stage-Gate' : '⚡ Auto Pipeline'}</span>
      <span class="px-2 py-0.5 rounded-md font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">${vid.status === 'completed' || !vid.status ? '✓ Completed' : 'In Progress'}</span>
    `;
  }

  const defaultArtifacts = [
    { name: "project_manifest.json", size: "2.4 KB", desc: "Pipeline config, model routing manifest & SHA-256 tokens", icon: "fa-code" },
    { name: "flux_keyframes_4k.zip", size: "8.4 MB", desc: "FLUX.1 Pro 4K HDR photoreal cinematic keyframes", icon: "fa-images" },
    { name: "video_motion_clips.zip", size: "19.2 MB", desc: "Wan 2.1 & Kling Pro dynamic motion renders", icon: "fa-film" },
    { name: "foley_soundscape_48k.wav", size: "3.8 MB", desc: "48,000 Hz 24-bit procedural binaural soundscape stem", icon: "fa-wave-square" },
    { name: "suno_bgm_master.wav", size: "4.6 MB", desc: "Suno v3.5 Pro commercial acoustic master arrangement", icon: "fa-music" },
    { name: "master_4k_render.mp4", size: "32.1 MB", desc: "Single-pass FFmpeg combined 4K UHD master broadcast", icon: "fa-video", url: vid.videoUrl || "/static/videos/preview_master.mp4" }
  ];

  const listEl = document.getElementById("artifacts-file-list");
  if (listEl) {
    const arts = vid.artifacts_list || defaultArtifacts;
    document.getElementById("artifacts-file-count") && (document.getElementById("artifacts-file-count").textContent = `${arts.length} Artifacts`);
    listEl.innerHTML = arts.map(art => `
      <div class="p-2.5 bg-slate-50 dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 hover:border-indigo-500/50 rounded-xl flex items-center justify-between transition">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-7 h-7 rounded-lg bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 flex items-center justify-center text-xs shrink-0 border border-indigo-200 dark:border-indigo-800/40">
            <i class="fa-solid ${art.icon || 'fa-file'}"></i>
          </div>
          <div class="min-w-0">
            <div class="font-bold text-slate-900 dark:text-white text-xs font-mono truncate">${art.name}</div>
            <div class="text-[10px] text-slate-500 dark:text-gray-400 truncate">${art.desc} • <span class="font-mono text-slate-700 dark:text-gray-300 font-semibold">${art.size}</span></div>
          </div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          ${art.url ? `<a href="${art.url}" download class="px-2 py-0.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-[9px] font-bold inline-flex items-center gap-1 transition"><i class="fa-solid fa-download text-[8px]"></i> Download</a>` : '<span class="px-1.5 py-0.2 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-gray-400 rounded text-[8px] font-mono">Vault Stored</span>'}
        </div>
      </div>
    `).join("");
  }

  if (typeof openModal === "function") openModal("artifacts-modal");
}

function closeArtifactsModal() {
  if (typeof closeModal === "function") closeModal("artifacts-modal");
}
