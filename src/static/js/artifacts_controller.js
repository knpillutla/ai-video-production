// CineAI Studio: Artifacts & Traceability Inspector Controller
function viewEpisodeArtifacts(id) {
  const vid = studioVideos.find(v => v.id === id);
  if (!vid) return;

  const titleEl = document.getElementById("artifacts-modal-title");
  const jobEl = document.getElementById("artifacts-modal-job-id");
  const badgesEl = document.getElementById("artifacts-meta-badges");
  const listEl = document.getElementById("artifacts-file-list");

  if (titleEl) titleEl.textContent = `${vid.id}: ${vid.title}`;
  if (jobEl) jobEl.textContent = `Traceability Job UUID: ${vid.jobId}`;

  if (badgesEl) {
    badgesEl.innerHTML = `
      <span class="px-2.5 py-1 rounded-lg font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40">${vid.videoType || "Web Series"}</span>
      <span class="px-2.5 py-1 rounded-lg font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40">${vid.formatType || "Long (16:9)"}</span>
      <span class="px-2.5 py-1 rounded-lg font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40">${vid.styleType || "Realistic (Photoreal)"}</span>
      <span class="px-2.5 py-1 rounded-lg font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">${vid.tierName || "Balanced"}</span>
      <span class="px-2.5 py-1 rounded-lg font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">${vid.language}</span>
    `;
  }

  const defaultArtifacts = [
    { name: "project_manifest.json", size: "2.4 KB", type: "JSON", icon: "fa-code", desc: "Configuration, prompt hashing, and model selector routing manifest" },
    { name: "script_transcreation.json", size: "14.8 KB", type: "JSON", icon: "fa-file-lines", desc: "Telugu/Hindi cultural transcreation with timestamps & punchlines" },
    { name: "storyboard_keyframes.zip", size: "8.2 MB", type: "ZIP", icon: "fa-images", desc: "Single-pass image keyframes rendered via FLUX engine" },
    { name: "dialogue_audio_stems.wav", size: "4.1 MB", type: "Audio", icon: "fa-waveform-lines", desc: "48kHz Azure Neural TTS synchronized dialogue stems" },
    { name: "bgm_ducked_mix.mp3", size: "3.6 MB", type: "Audio", icon: "fa-music", desc: "Sidechain-ducked background score with sound effects" },
    { name: "master_1080p_render.mp4", size: "28.4 MB", type: "Video", icon: "fa-film", desc: "Single-pass FFmpeg combined master render", url: "/static/videos/preview_master.mp4" },
    { name: "youtube_syndication_seo.json", size: "1.9 KB", type: "JSON", icon: "fa-hashtag", desc: "Optimized title, description, tags, and category metadata" }
  ];

  const artifacts = vid.artifacts || defaultArtifacts;

  if (listEl) {
    listEl.innerHTML = artifacts.map(art => `
      <div class="p-3 bg-slate-900/80 border border-[var(--border)] hover:border-indigo-500/50 rounded-xl flex items-center justify-between transition">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded-lg bg-slate-800 text-indigo-400 flex items-center justify-center text-sm">
            <i class="fa-solid ${art.icon || 'fa-file'}"></i>
          </div>
          <div>
            <div class="font-bold text-white text-xs font-mono">${art.name}</div>
            <div class="text-[10px] text-gray-400">${art.desc} • <span class="font-mono text-gray-300">${art.size}</span></div>
          </div>
        </div>
        <div class="flex items-center gap-2">
          ${art.url ? `<a href="${art.url}" download class="px-2.5 py-1 bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/40 text-indigo-300 rounded-lg text-[10px] font-bold inline-flex items-center gap-1 transition"><i class="fa-solid fa-download"></i> Download</a>` : '<span class="px-2 py-0.5 bg-slate-800 text-gray-400 rounded text-[9px] font-mono">Vault Stored</span>'}
        </div>
      </div>
    `).join("");
  }

  openModal("artifacts-modal");
}

function closeArtifactsModal() {
  closeModal("artifacts-modal");
}
