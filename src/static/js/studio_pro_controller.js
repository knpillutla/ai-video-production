// CineAI Studio: Next-Gen Studio Pro Split-Deck & Progressive Stage Controller
let currentProEpisode = null;
let currentProAudioMode = "ambient";

function renderStudioProView(vid) {
  currentProEpisode = vid || currentActiveInspectorEpisode;
  const ep = currentProEpisode;
  if (!ep) return;

  const setT = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  const epId = ep.id || ep.episode_id || "EP-001";
  setT("pro-ep-badge", epId);
  setT("pro-story-title", ep.story_topic || ep.title || "4K Master Production");
  setT("pro-channel-name", ep.channel_name || "Earth Serenade");

  const promptInput = document.getElementById("pro-prompt-input");
  if (promptInput && !promptInput.dataset.userEdited && (ep.story_topic || ep.title)) {
    promptInput.value = ep.story_topic || ep.title;
  }

  // Master Video Setup
  const video = document.getElementById("pro-master-video");
  const masterUrl = ep.videoUrl || ep.video_url || ep.editions?.[0]?.url || ep.artifacts?.master_video || "";
  const natureUrl = ep.nature_video_url || ep.editions?.find(e => e.edition_id === "master_nature")?.url || "";

  if (video && masterUrl) {
    const targetUrl = (currentProAudioMode === "nature" && natureUrl) ? natureUrl : masterUrl;
    if (!video.src.endsWith(targetUrl)) video.src = targetUrl;
  }

  renderProStage1Keyframes(ep);
  renderProStage2Motion(ep);
  renderProStage3Audio(ep);
  renderProStage5Masters(ep);
  renderProStage6LongPlay(ep);
}

function proSwitchAudioMode(mode) {
  currentProAudioMode = mode;
  const bAmb = document.getElementById("btn-pro-audio-ambient"), bNat = document.getElementById("btn-pro-audio-nature");
  const isAmb = mode === "ambient";
  if (bAmb) bAmb.className = isAmb ? "px-2.5 py-1 bg-indigo-600/30 border border-indigo-500 text-indigo-200 rounded-lg text-[10px] font-bold transition flex items-center gap-1.5 shadow-sm" : "px-2.5 py-1 bg-slate-900 hover:bg-indigo-950/40 border border-slate-700 text-slate-400 rounded-lg text-[10px] font-bold transition flex items-center gap-1.5";
  if (bNat) bNat.className = !isAmb ? "px-2.5 py-1 bg-cyan-600/30 border border-cyan-500 text-cyan-200 rounded-lg text-[10px] font-bold transition flex items-center gap-1.5 shadow-sm" : "px-2.5 py-1 bg-slate-900 hover:bg-cyan-950/40 border border-slate-700 text-slate-400 rounded-lg text-[10px] font-bold transition flex items-center gap-1.5";
  const badge = document.getElementById("pro-active-master-badge");
  if (badge) badge.textContent = isAmb ? "Ambient BGM Active" : "Pure Nature ASMR Active";

  const ep = currentProEpisode;
  const video = document.getElementById("pro-master-video");
  if (ep && video) {
    const masterUrl = ep.videoUrl || ep.video_url || ep.editions?.[0]?.url || "";
    const natureUrl = ep.nature_video_url || ep.editions?.find(e => e.edition_id === "master_nature")?.url || "";
    const targetUrl = (mode === "nature" && natureUrl) ? natureUrl : masterUrl;
    if (targetUrl) {
      const curTime = video.currentTime;
      video.src = targetUrl;
      video.currentTime = curTime;
      video.play().catch(() => { });
    }
  }
}

function renderProStage1Keyframes(ep) {
  const c = document.getElementById("pro-s1-container");
  if (!c) return;
  const kfs = (ep.keyframes && ep.keyframes.length > 0) ? ep.keyframes : (ep.artifacts?.keyframes || []);
  if (kfs.length === 0) {
    c.innerHTML = `<div class="w-full text-center text-[8px] text-slate-500 font-mono py-4">No Photos Yet</div>`;
    return;
  }
  c.innerHTML = kfs.map((kf, i) => {
    const url = (typeof kf === "object") ? kf.url : kf;
    return `<div class="relative w-14 h-14 rounded-lg overflow-hidden bg-slate-800 shrink-0 border border-slate-700 hover:border-blue-400 cursor-pointer transition shadow" onclick="if (typeof openImagePopup === 'function') openImagePopup('${url}', 'Shot ${i + 1}', 'FLUX 1.1 Pro');" title="Shot ${i + 1}"><img src="${url}" class="w-full h-full object-cover"><span class="absolute bottom-0.5 right-0.5 px-1 bg-black/70 text-[6px] font-mono text-white rounded">P${i + 1}</span></div>`;
  }).join("");
}

function renderProStage2Motion(ep) {
  const c = document.getElementById("pro-s2-container");
  if (!c) return;
  const clips = (ep.motion_clips && ep.motion_clips.length > 0) ? ep.motion_clips : (ep.artifacts?.motion_clips || []);
  if (clips.length === 0) {
    c.innerHTML = `<div class="w-full text-center text-[8px] text-slate-500 font-mono py-4">No Clips Yet</div>`;
    return;
  }
  c.innerHTML = clips.map((cl, i) => {
    const url = (typeof cl === "object") ? cl.url : cl;
    return `<div class="relative w-14 h-14 rounded-lg overflow-hidden bg-slate-800 shrink-0 border border-slate-700 hover:border-purple-400 cursor-pointer transition shadow flex items-center justify-center group" onclick="const v = document.getElementById('pro-master-video'); if (v) { v.src = '${url}'; v.play().catch(()=>{}); }" title="Preview Motion ${i + 1}"><video src="${url}" class="w-full h-full object-cover" muted loop></video><div class="absolute inset-0 bg-black/40 group-hover:bg-black/10 transition flex items-center justify-center"><i class="fa-solid fa-play text-[8px] text-white drop-shadow"></i></div><span class="absolute bottom-0.5 right-0.5 px-1 bg-black/70 text-[6px] font-mono text-purple-300 rounded">M${i + 1}</span></div>`;
  }).join("");
}

function renderProStage3Audio(ep) {
  const c = document.getElementById("pro-s3-container");
  if (!c) return;
  const stems = (ep.audio_stems && ep.audio_stems.length > 0) ? ep.audio_stems : (ep.artifacts?.audio_stems || []);
  if (stems.length === 0) {
    c.innerHTML = `<div class="w-full text-center text-[8px] text-slate-500 font-mono py-4">No Audio Stems</div>`;
    return;
  }
  c.innerHTML = stems.map(s => `
    <div class="px-1.5 py-0.5 bg-slate-950/80 rounded border border-slate-800 flex items-center justify-between text-[8px]">
      <span class="font-mono text-cyan-300 truncate max-w-[80px]">${s.name || 'Soundtrack'}</span>
      <audio controls src="${s.url}" class="h-3 w-16 scale-90 origin-right"></audio>
    </div>
  `).join("");
}

function renderProStage5Masters(ep) {
  const c = document.getElementById("pro-s5-container");
  if (!c) return;
  const masterUrl = ep.videoUrl || ep.video_url || ep.editions?.[0]?.url || "";
  const natureUrl = ep.nature_video_url || ep.editions?.find(e => e.edition_id === "master_nature")?.url || "";
  if (!masterUrl && !natureUrl) {
    c.innerHTML = `<div class="w-full text-center text-[8px] text-slate-500 font-mono py-4">Awaiting Render</div>`;
    return;
  }
  c.innerHTML = `
    ${masterUrl ? `<button type="button" onclick="proSwitchAudioMode('ambient')" class="w-full px-1.5 py-1 bg-indigo-950/60 hover:bg-indigo-900/80 border border-indigo-500/40 text-indigo-200 rounded text-[8px] font-bold transition flex items-center justify-between"><span>🎵 Ambient BGM</span><i class="fa-solid fa-play text-[6px]"></i></button>` : ''}
    ${natureUrl ? `<button type="button" onclick="proSwitchAudioMode('nature')" class="w-full px-1.5 py-1 bg-cyan-950/60 hover:bg-cyan-900/80 border border-cyan-500/40 text-cyan-200 rounded text-[8px] font-bold transition flex items-center justify-between"><span>🌊 Nature ASMR</span><i class="fa-solid fa-play text-[6px]"></i></button>` : ''}
  `;
}

function renderProStage6LongPlay(ep) {
  const c = document.getElementById("pro-s6-container");
  if (!c) return;
  const hasMaster = Boolean(ep && ep.id !== "NEW" && ep.status !== "failed" && (ep.videoUrl || ep.video_url || (ep.editions && ep.editions.length > 0) || ep.status === "completed"));
  if (!hasMaster) {
    c.innerHTML = `<div class="w-full text-center text-[8px] text-slate-500 font-mono py-4">Awaiting Master</div>`;
    return;
  }
  const lpEds = (ep.long_play_editions && ep.long_play_editions.length > 0)
    ? ep.long_play_editions
    : (ep.all_editions || ep.editions || []).filter(e => e.format?.includes("Long-Play") || e.edition_id?.includes("h_") || e.name?.includes("Hour"));

  if (lpEds.length > 0) {
    c.innerHTML = lpEds.map(ed => `
      <button type="button" onclick="const v = document.getElementById('pro-master-video'); if (v) { v.src = '${ed.url}'; v.play().catch(()=>{}); }" class="w-full px-1.5 py-0.5 bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-500/40 text-emerald-200 rounded text-[8px] font-bold transition truncate text-left" title="${ed.name}">
        ✓ ${ed.name.substring(0, 14)}...
      </button>
    `).join("");
    return;
  }
  c.innerHTML = `<button type="button" onclick="proApproveLongPlay()" class="w-full py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white rounded text-[8px] font-bold transition shadow">Approve &amp; Stretch</button>`;
}

function proSelectNiche(type) {
  const prompts = {
    nature: "Lush alpine forest stream with crystal clear turquoise water cascading over mossy rocks, 4K UHD photoreal.",
    rain: "Gentle rain ripples falling on calm mountain lake, surrounded by misty pine forests and soft distant thunder.",
    fireplace: "Warm crackling stone fireplace inside a rustic timber cabin during heavy snowfall, glowing amber embers.",
    healing: "Tranquil Japanese Zen garden with smooth river stones, trickling bamboo fountain, and blossoming lotus petals."
  };
  const input = document.getElementById("pro-prompt-input");
  if (input && prompts[type]) {
    input.value = prompts[type];
    input.dataset.userEdited = "true";
  }
}

async function proTriggerProduction() {
  const promptInput = document.getElementById("pro-prompt-input");
  const prompt = promptInput?.value?.trim() || "";
  const motionModel = document.getElementById("pro-motion-model")?.value || "wan";
  const durationSec = parseFloat(document.getElementById("pro-duration-mode")?.value || "60");
  const chSlug = currentProEpisode?.channelId || currentProEpisode?.channel_id || "earth_serenade";
  const uEmail = currentUser?.email || "knpillutla@gmail.com";

  const btnText = document.getElementById("btn-pro-produce-text");
  if (btnText) btnText.textContent = "Synthesizing Stages 1-5...";

  try {
    const res = await fetch("/api/production/local-produce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: prompt,
        channel_id: chSlug,
        motion_model: motionModel,
        duration_seconds: durationSec,
        user_id: uEmail
      })
    });
    const data = await res.json();
    if (data.success) {
      if (typeof showProfileStatusToast === "function") showProfileStatusToast("Video production complete!");
      renderStudioProView(data);
      if (typeof syncChannelEpisodesFromBackend === "function") await syncChannelEpisodesFromBackend();
    }
  } catch (err) {
    console.error("Pro production failed:", err);
  } finally {
    if (btnText) btnText.textContent = "Produce 4K Video Masters ⚡";
  }
}

async function proApproveLongPlay() {
  const ep = currentProEpisode;
  if (!ep) return;
  const epId = ep.id || ep.episode_id || "EP-001";
  const hours = parseFloat(document.getElementById("pro-lp-hours")?.value || "3.0");
  const chSlug = ep.channelId || ep.channel_id || "earth_serenade";

  const c = document.getElementById("pro-s6-container");
  if (c) c.innerHTML = `<div class="text-[8px] font-mono text-amber-400 animate-pulse text-center"><i class="fa-solid fa-spinner fa-spin mr-1"></i> Stretching ${hours}h...</div>`;

  if (typeof approveAndGenerateLongPlay === "function") {
    const hoursSel = document.getElementById("panel-longplay-hours-select");
    if (hoursSel) hoursSel.value = `${hours.toFixed(1)}`;
    await approveAndGenerateLongPlay();
  }
}

function openActiveProVideoPopup() {
  const video = document.getElementById("pro-master-video");
  const src = video?.src;
  if (src && typeof openVideoPopup === "function") {
    const ep = currentProEpisode;
    openVideoPopup(src, ep?.title || "Master 4K Video", `${currentProAudioMode === 'nature' ? 'Pure Nature ASMR' : 'Ambient Music'} • Lossless CRF 22`);
  }
}
