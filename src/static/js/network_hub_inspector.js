// CineAI Studio: Channel Episode Inspector & Modal Packaging Controller
function openScriptModal(epId) {
  const ep = (typeof allChannelEpisodes !== "undefined" ? allChannelEpisodes : []).find(x => x.episode_id === epId);
  if (!ep) return;
  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setEl("script-modal-title", `Screenplay & Script: ${ep.title}`);
  setEl("script-modal-subtitle", `${ep.channel_name} (${ep.channel_handle}) • ${ep.episode_id}`);
  setEl("script-modal-topic", ep.story_topic);
  setEl("script-modal-text", ep.script_text || "No script available for this episode.");
  openModal("episode-script-modal");
}

function copyScriptContent() {
  const text = document.getElementById("script-modal-text")?.textContent || "";
  navigator.clipboard.writeText(text);
  showStudioModal({ title: "Screenplay Copied", message: "Full story script and scene breakdown copied to clipboard.", nextStep: "Ready for review or external syndication." });
}

function playEditionVideo(videoUrl, epId, editionName) {
  if (!videoUrl) return;
  openChannelEpisodeInspector(epId);
  switchInspectorTab("player");
  loadInspectorVideo(videoUrl);
}

function openChannelEpisodeInspector(epId) {
  const ep = (typeof allChannelEpisodes !== "undefined" ? allChannelEpisodes : []).find(x => x.episode_id === epId);
  if (!ep) return;
  currentInspectingEpisode = ep;

  document.getElementById("inspector-channel-badge").textContent = `${ep.channel_handle}`;
  document.getElementById("inspector-episode-title").textContent = ep.title;
  document.getElementById("inspector-episode-id").textContent = `${ep.episode_id} • Created ${ep.created_at} • Cost: $${ep.cost_usd.toFixed(2)} USD`;
  document.getElementById("inspector-status-badge").textContent = "READY";

  const streamsDiv = document.getElementById("inspector-stream-buttons");
  if (streamsDiv && ep.editions) {
    streamsDiv.innerHTML = ep.editions.map((s, idx) => `
      <button type="button" onclick="loadInspectorVideo('${s.url}', this)" class="px-2 py-0.8 rounded text-[10px] font-bold transition ${idx === 0 ? 'bg-indigo-600 text-white' : 'bg-slate-900 text-gray-300 hover:text-white border border-slate-800'}">
        ${s.name}
      </button>
    `).join("");
    if (ep.editions.length > 0) loadInspectorVideo(ep.editions[0].url);
  }

  switchPackagingEdition("music");
  const cb = ep.cost_breakdown || {};
  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setEl("inspector-cost-total", `$${ep.cost_usd.toFixed(3)} USD`);
  setEl("inspector-cost-duration", ep.editions?.[0]?.duration || "90s");
  setEl("inspector-cost-per-hour", "$0.20 / hr");

  const stageTbody = document.getElementById("inspector-cost-stage-tbody");
  if (stageTbody) {
    stageTbody.innerHTML = (cb.by_stage || []).map(s => `
      <tr class="hover:bg-slate-800/30">
        <td class="p-2 font-bold text-black dark:text-white text-[11px]">${s.stage}</td>
        <td class="p-2 font-mono text-indigo-900 dark:text-indigo-300 text-[11px] font-bold">${s.model}</td>
        <td class="p-2 text-black dark:text-gray-400 text-[10px] font-medium">${s.unit}</td>
        <td class="p-2 text-right font-mono font-bold text-emerald-800 dark:text-emerald-400 text-[11px]">$${s.cost_usd.toFixed(3)}</td>
      </tr>
    `).join("");
  }

  const modelTbody = document.getElementById("inspector-cost-model-tbody");
  if (modelTbody) {
    modelTbody.innerHTML = (cb.by_model || []).map(m => `
      <tr class="hover:bg-slate-800/30">
        <td class="p-2 font-bold text-black dark:text-white text-[11px]">${m.model}</td>
        <td class="p-2 text-black dark:text-gray-300 text-[11px] font-medium">${m.provider}</td>
        <td class="p-2 text-center font-mono font-bold text-purple-900 dark:text-purple-300 text-[10px]">${m.percentage}</td>
        <td class="p-2 text-right font-mono font-bold text-emerald-800 dark:text-emerald-400 text-[11px]">$${m.cost_usd.toFixed(3)}</td>
      </tr>
    `).join("");
  }

  const modelsGrid = document.getElementById("inspector-models-grid");
  if (modelsGrid) {
    modelsGrid.innerHTML = Object.entries(ep.models_used || {}).map(([stage, model]) => `
      <div class="p-2 bg-slate-100 dark:bg-slate-900/80 border border-slate-300 dark:border-slate-800 rounded-lg">
        <div class="text-[9px] text-black dark:text-gray-400 uppercase font-bold">${stage}</div>
        <div class="font-mono text-[11px] font-bold text-indigo-900 dark:text-indigo-300 mt-0.5">${model}</div>
      </div>
    `).join("");
  }

  const stagesGrid = document.getElementById("inspector-stages-grid");
  if (stagesGrid) {
    stagesGrid.innerHTML = Object.entries(ep.stages || {}).map(([k, ok]) => `
      <div class="p-1.5 bg-slate-100 dark:bg-slate-900 border ${ok ? 'border-emerald-500/40 bg-emerald-50 dark:bg-emerald-950/20' : 'border-slate-300 dark:border-slate-800'} rounded text-center">
        <div class="text-[9px] ${ok ? 'text-emerald-800 dark:text-emerald-400 font-bold' : 'text-slate-600 dark:text-gray-500'}">${ok ? '✓' : '○'} ${k.replace('stage_', 'S').replace(/_/g, ' ')}</div>
      </div>
    `).join("");
  }

  switchInspectorTab("player");
  openModal("channel-episode-inspector-modal");
}

function loadInspectorVideo(url, btnEl) {
  const vid = document.getElementById("inspector-video-player");
  if (vid) { vid.src = url; vid.play().catch(() => {}); }
  if (btnEl) {
    Array.from(btnEl.parentElement.children).forEach(c => {
      c.className = "px-2 py-0.8 rounded text-[10px] font-bold transition bg-slate-900 text-gray-300 hover:text-white border border-slate-800";
    });
    btnEl.className = "px-2 py-0.8 rounded text-[10px] font-bold transition bg-indigo-600 text-white shadow";
  }
}

function switchInspectorTab(tabKey) {
  ["player", "youtube", "cost", "models", "artifacts"].forEach(t => {
    const tabEl = document.getElementById("inspector-tab-" + t);
    const btnEl = document.getElementById("inspector-tab-btn-" + t);
    if (tabEl) tabEl.classList.toggle("hidden", t !== tabKey);
    if (btnEl) {
      btnEl.className = (t === tabKey)
        ? "px-2.5 py-1 font-bold text-white bg-indigo-600 rounded-lg shadow flex items-center gap-1 text-[11px]"
        : "px-2.5 py-1 font-medium text-gray-400 hover:text-white rounded-lg flex items-center gap-1 text-[11px]";
    }
  });
}

function switchPackagingEdition(edition) {
  if (!currentInspectingEpisode) return;
  const pMusic = document.getElementById("btn-pack-music");
  const pNature = document.getElementById("btn-pack-nature");
  const pack = (edition === "nature" && currentInspectingEpisode.youtube_packaging_nature_only?.title)
    ? currentInspectingEpisode.youtube_packaging_nature_only
    : currentInspectingEpisode.youtube_packaging || {};

  if (pMusic) pMusic.className = edition === "music" ? "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white" : "px-2 py-0.5 text-[10px] font-medium text-gray-400 hover:text-white";
  if (pNature) pNature.className = edition === "nature" ? "px-2 py-0.5 text-[10px] font-bold rounded bg-indigo-600 text-white" : "px-2 py-0.5 text-[10px] font-medium text-gray-400 hover:text-white";

  const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val || ''; };
  setVal("inspector-yt-title", pack.title);
  setVal("inspector-yt-desc", pack.description);
  setVal("inspector-yt-tags", Array.isArray(pack.tags) ? pack.tags.join(", ") : pack.tags);
  setVal("inspector-yt-pinned", pack.pinned_comment);
}
