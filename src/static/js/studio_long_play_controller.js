// CineAI Studio: Dual Long-Play Master Broadcast Stretcher Controller (Ambient Soundtrack + Pure Nature ASMR)
let longPlayPollingTimer = null;
let activeLongPlayJob = null;

function renderLongPlayStretchSection(vid) {
  const container = document.getElementById("panel-section-longplay-container");
  const approvalCard = document.getElementById("panel-longplay-approval-card");
  const dualGrid = document.getElementById("panel-longplay-dual-grid");
  const statusBadge = document.getElementById("panel-longplay-status-badge");
  const hoursSelect = document.getElementById("panel-longplay-hours-select");

  if (!container || !dualGrid) return;
  // Long-Play stretch is ONLY available after 4K Master Video (Stage 4) has finished rendering
  const hasMaster = Boolean(
    vid &&
    vid.id !== "NEW" &&
    vid.status !== "failed" &&
    vid.status !== "processing" &&
    (vid.currentStage >= 4 || vid.status === "completed") &&
    (vid.videoUrl || vid.video_url || (vid.editions && vid.editions.length > 0))
  const isRelax = Boolean(vid.genre?.includes("relax") || vid.cluster === "nature" || (vid.long_play_hours && parseFloat(vid.long_play_hours) > 0));
  if (!hasMaster || !isRelax) {
    container.classList.add("hidden");
    if (approvalCard) approvalCard.classList.add("hidden");
    dualGrid.innerHTML = "";
    return;
  }
  container.classList.remove("hidden");

  const epId = vid.id || vid.episode_id || "EP-001";
  let lpEditions = (vid.long_play_editions && vid.long_play_editions.length > 0) 
    ? [...vid.long_play_editions] 
    : (vid.all_editions || vid.editions || []).filter(e => e.format?.includes("Long-Play") || e.edition_id?.includes("h_") || e.name?.includes("Hour"));

  const hoursVal = vid.long_play_hours || (vid.longPlayHours ? parseFloat(vid.longPlayHours) : 3.0);
  if (hoursSelect && !hoursSelect.dataset.userModified) {
    hoursSelect.value = hoursVal ? `${parseFloat(hoursVal).toFixed(1)}` : "3.0";
  }

  const posterUrl = vid.thumbnailUrl || (vid.keyframes?.[0]?.url) || (vid.artifacts?.keyframes?.[0]?.url) || "";
  const bgStyle = posterUrl ? `background-image: url('${posterUrl}'); background-size: cover; background-position: center;` : "";

  // Check if live job is active
  if (activeLongPlayJob && activeLongPlayJob.episode_id === epId && activeLongPlayJob.status === "processing") {
    if (approvalCard) approvalCard.classList.add("hidden");
    if (statusBadge) {
      statusBadge.className = "px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-700 dark:text-amber-300 border border-amber-500/40 text-[8px] font-mono font-bold animate-pulse";
      statusBadge.textContent = "Stretching Broadcasts...";
    }
    renderLongPlayProgressBars(activeLongPlayJob, dualGrid);
    return;
  }

  // Completed long-play broadcast editions on disk
  if (lpEditions.length > 0) {
    if (approvalCard) approvalCard.classList.remove("hidden");
    if (statusBadge) {
      statusBadge.className = "px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-700 dark:text-emerald-300 border border-emerald-500/40 text-[8px] font-mono font-bold flex items-center gap-1";
      statusBadge.innerHTML = `<i class="fa-solid fa-circle-check text-[7px]"></i><span>Dual 4K Broadcasts Ready</span>`;
    }
    const btnApprove = document.getElementById("btn-approve-longplay-text");
    if (btnApprove) btnApprove.innerHTML = '<i class="fa-solid fa-arrows-rotate mr-1"></i> Regenerate Dual 4K Broadcasts';

    dualGrid.innerHTML = lpEditions.map(ed => `
      <div class="flex flex-col items-center gap-0.5 cursor-pointer w-full group" onclick="if (typeof selectMasterVideoRender === 'function') selectMasterVideoRender('${ed.url}', '${ed.name}', this); if (typeof openVideoPopup === 'function') openVideoPopup('${ed.url}', '${epId}: ${ed.name}', '${ed.format} • ${ed.audio_mode}');" title="Click to preview full broadcast in 4K popup">
        <div class="relative w-full h-11 rounded-lg overflow-hidden bg-slate-900 border border-indigo-500/40 hover:border-emerald-400 transition shadow flex flex-col justify-between p-1" style="${bgStyle}">
          <div class="absolute inset-0 bg-black/45 group-hover:bg-black/25 transition pointer-events-none"></div>
          <div class="relative z-10 flex items-center justify-between">
            <span class="px-1 py-0.2 rounded bg-indigo-900/90 text-[7px] font-mono font-bold text-indigo-200">${ed.format || '16:9 Long-Play'}</span>
            <span class="text-[7px] font-mono text-emerald-300 font-bold bg-black/70 px-1 py-0.2 rounded">${ed.duration || '3h'}</span>
          </div>
          <div class="relative z-10 flex items-center justify-between">
            <span class="text-[7px] font-mono font-bold text-white bg-black/70 px-1 py-0.2 rounded truncate max-w-[85px]">${ed.audio_mode}</span>
            <div class="w-4 h-4 rounded-full bg-emerald-600/90 group-hover:bg-emerald-500 text-white flex items-center justify-center text-[6px] shadow"><i class="fa-solid fa-play ml-0.5"></i></div>
          </div>
        </div>
        <span class="text-[8px] font-bold text-slate-800 dark:text-gray-300 truncate w-full text-center">${ed.name}</span>
        <span class="text-[7px] font-mono text-slate-500 dark:text-gray-400">${ed.size_str || ''}</span>
      </div>
    `).join("");
    return;
  }

  // Idle state before approval (Prompt user to generate multi-hour broadcasts)
  if (approvalCard) approvalCard.classList.remove("hidden");
  if (statusBadge) {
    statusBadge.className = "px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border border-indigo-500/40 text-[8px] font-mono font-bold";
    statusBadge.textContent = "Awaiting Approval";
  }
  const btnApprove = document.getElementById("btn-approve-longplay-text");
  if (btnApprove) btnApprove.textContent = "Approve & Generate Dual 4K Broadcasts";

  dualGrid.innerHTML = `
    <div class="col-span-2 p-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-dashed border-slate-300 dark:border-slate-800 text-center flex flex-col items-center gap-0.5">
      <i class="fa-solid fa-film text-indigo-400 text-xs"></i>
      <span class="text-[9px] font-bold text-slate-700 dark:text-slate-300">Dual Multi-Hour Masters (Music + Pure Nature)</span>
      <span class="text-[8px] text-slate-500 dark:text-slate-400">Click Approve above to stretch lossless 4K broadcast masters.</span>
    </div>
  `;
}

function renderLongPlayProgressBars(job, container) {
  const ambP = Math.min(100, Math.max(5, job.ambient_progress || 10));
  const natP = Math.min(100, Math.max(5, job.nature_progress || 10));

  container.innerHTML = `
    <div class="p-1.5 bg-slate-900/90 border border-indigo-500/40 rounded-lg flex flex-col gap-1 shadow-sm">
      <div class="flex items-center justify-between text-[8px] font-mono font-bold text-indigo-300">
        <span class="flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> 🎵 Ambient Master</span>
        <span>${ambP}%</span>
      </div>
      <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-300" style="width: ${ambP}%"></div>
      </div>
    </div>
    <div class="p-1.5 bg-slate-900/90 border border-cyan-500/40 rounded-lg flex flex-col gap-1 shadow-sm">
      <div class="flex items-center justify-between text-[8px] font-mono font-bold text-cyan-300">
        <span class="flex items-center gap-1"><i class="fa-solid fa-spinner fa-spin text-[7px]"></i> 🌊 Nature ASMR</span>
        <span>${natP}%</span>
      </div>
      <div class="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-cyan-500 to-emerald-500 rounded-full transition-all duration-300" style="width: ${natP}%"></div>
      </div>
    </div>
  `;
}

async function approveAndGenerateLongPlay() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("No active episode selected.");
    return;
  }
  const epId = vid.id || vid.episode_id || "EP-001";
  const hoursSelect = document.getElementById("panel-longplay-hours-select");
  const hours = hoursSelect ? parseFloat(hoursSelect.value || "3.0") : 3.0;
  const chSlug = vid.channelId || vid.channel_id || "earth_serenade";
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";

  const btnText = document.getElementById("btn-approve-longplay-text");
  if (btnText) btnText.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-1"></i> Launching Dual Broadcast Stretcher...';

  try {
    const res = await fetch(`/api/production/episodes/${epId}/generate-long-play`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ channel_id: chSlug, hours: hours, user_id: uEmail })
    });
    const data = await res.json();
    if (data.success) {
      if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Dual ${hours}h 4K sleep broadcast stretching started!`);
      activeLongPlayJob = { episode_id: epId, hours: hours, status: "processing", ambient_progress: 15, nature_progress: 15 };
      renderLongPlayStretchSection(vid);
      startLongPlayStatusPolling(epId, chSlug, uEmail);
    } else {
      if (typeof showProfileStatusToast === "function") showProfileStatusToast(data.detail || "Failed to start long-play stretch.");
    }
  } catch (err) {
    console.error("Long play stretch request error:", err);
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Network error starting long-play broadcast.");
  }
}

function startLongPlayStatusPolling(epId, chSlug, uEmail) {
  if (longPlayPollingTimer) clearInterval(longPlayPollingTimer);

  longPlayPollingTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/production/episodes/${epId}/long-play-status?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        activeLongPlayJob = data;
        const vid = currentActiveInspectorEpisode;
        if (vid && (vid.id === epId || vid.episode_id === epId)) {
          if (data.status === "completed") {
            clearInterval(longPlayPollingTimer);
            longPlayPollingTimer = null;
            if (typeof syncChannelEpisodesFromBackend === "function") await syncChannelEpisodesFromBackend();
            if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Dual 4K broadcasts completed successfully!`);
          }
          renderLongPlayStretchSection(vid);
        }
      }
    } catch (e) {}
  }, 1200);
}
