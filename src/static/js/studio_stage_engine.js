// CineAI Studio: Progressive Stage-Gate Execution Engine (Live Artifact Polling & Stop/Resume)
let studioAbortController = null;

function stageGateRerollCurrent() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  if (vid.currentStage === 1) {
    if (!vid.keyframes) vid.keyframes = [];
    vid.keyframes.push({ name: `Shot ${vid.keyframes.length + 1}: Angle`, url: `/static/img/shot${(vid.keyframes.length % 4) + 1}_wide.jpg`, timing: "3.5s" });
    vid.selectedKeyframeIds = vid.keyframes.map((_, i) => i);
    renderKeyframesList(vid); updateStageGateDock(vid);
  } else if (vid.currentStage === 2) {
    if (!vid.motion_clips) vid.motion_clips = [];
    vid.motion_clips.push({ name: `Motion ${vid.motion_clips.length + 1}: Dynamic Pan`, model: "Wan 2.1", duration: "5s", url: "/static/videos/preview_master.mp4", timing: "12.0s" });
    vid.selectedMotionClipIds = vid.motion_clips.map((_, i) => i);
    renderMotionClipsList(vid); updateStageGateDock(vid);
  }
}

function stageGateAdvanceNext() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  if (vid.currentStage === 1) advanceToMotionStage(vid);
  else if (vid.currentStage === 2) advanceToAudioStage(vid);
  else if (vid.currentStage === 3) advanceToMasterStage(vid);
}

async function stopStudioProduction(episodeId) {
  if (studioAbortController) {
    studioAbortController.abort();
    studioAbortController = null;
  }
  const ep = (typeof studioVideos !== "undefined") ? studioVideos.find(v => v.id === episodeId || v.episode_id === episodeId) : null;
  if (ep) {
    ep.status = "paused";
    if (typeof saveVideosState === "function") saveVideosState();
    if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(ep);
    if (typeof filterChannelArchive === "function") filterChannelArchive();
  }
  try {
    await fetch("/api/production/stop", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ episode_id: episodeId })
    });
  } catch (e) {}

  const bb = document.getElementById("studio-banner-phase-badge");
  if (bb) {
    bb.textContent = `⏸ Paused at Stage ${ep?.currentStage || 1}`;
    bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-600 text-white";
  }
}

async function resumeStudioProduction(episodeId) {
  const ep = (typeof studioVideos !== "undefined") ? studioVideos.find(v => v.id === episodeId || v.episode_id === episodeId) : null;
  if (!ep) return;
  ep.status = "processing";
  startStudioLiveStageProgress(ep, ep.pipelineStrategy);
}

async function startStudioLiveStageProgress(vid, strategy) {
  if (!vid) return;
  currentActiveInspectorEpisode = vid;
  vid.pipelineStrategy = strategy || (typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "auto");
  vid.currentStage = 1; vid.status = "processing"; vid.progress = 10;
  studioAbortController = new AbortController();

  const banner = document.getElementById("studio-queued-banner");
  if (banner) {
    const reqIdEl = document.getElementById("studio-banner-request-id");
    if (reqIdEl) reqIdEl.textContent = vid.jobId || `job_${vid.id}`;
    const tEl = document.getElementById("studio-banner-title");
    if (tEl) tEl.textContent = "Autonomous Pipeline Active";
    const dEl = document.getElementById("studio-banner-detail");
    if (dEl) dEl.textContent = `Episode ${vid.id} ("${vid.title}"): Executing real AI generation pipeline...`;
    const bb = document.getElementById("studio-banner-phase-badge");
    if (bb) {
      bb.classList.remove("hidden");
      bb.textContent = "Stage 1: Synthesizing Keyframes (FLUX 1.1 Pro)";
      bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-600 text-white animate-pulse";
    }
    banner.classList.remove("hidden");
  }
  renderInspectorFromVideo(vid);
  if (typeof filterChannelArchive === "function") filterChannelArchive();

  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : (vid.channelId || vid.channel_id || "earth_serenade");
  const epId = vid.id || vid.episode_id || "EP-001";
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";

  const pollArtifacts = async () => {
    try {
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        let changed = false;
        if (data.keyframes && data.keyframes.length > 0 && (!vid.keyframes || vid.keyframes.length !== data.keyframes.length || vid.keyframes[0]?.isGenerating)) {
          vid.keyframes = data.keyframes;
          if (data.keyframes.length >= 4 && vid.currentStage < 2) vid.currentStage = 2;
          changed = true;
        }
        if (data.motion_clips && data.motion_clips.length > 0 && (!vid.motion_clips || vid.motion_clips.length !== data.motion_clips.length || vid.motion_clips[0]?.isGenerating)) {
          vid.motion_clips = data.motion_clips;
          if (vid.currentStage < 3) vid.currentStage = 3;
          changed = true;
        }
        if (data.audio_stems && data.audio_stems.length > 0 && (!vid.audio_stems || vid.audio_stems.length !== data.audio_stems.length)) {
          vid.audio_stems = data.audio_stems;
          changed = true;
        }
        if (changed) {
          renderInspectorFromVideo(vid);
          if (typeof filterChannelArchive === "function") filterChannelArchive();
        }
      }
    } catch (e) {}
  };

  let pulseVal = 10;
  const pulseTimer = setInterval(() => {
    if (vid.status !== "processing") { clearInterval(pulseTimer); return; }
    pulseVal = Math.min(92, pulseVal + 3);
    vid.progress = pulseVal;
    pollArtifacts();
    renderInspectorFromVideo(vid);
    if (typeof filterChannelArchive === "function") filterChannelArchive();
  }, 1500);

  try {
    const res = await fetch("/api/production/local-produce", {
      method: "POST",
      signal: studioAbortController.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: vid.concept || vid.title || vid.story_topic || "4K Scenic Nature Sanctuary",
        channel_id: chSlug,
        duration_seconds: vid.durationSeconds || 10,
        episode_id: epId,
        user_id: uEmail,
        enable_bgm: vid.enableBgm !== false,
        allow_fallback: vid.allowFallback || false
      })
    });

    clearInterval(pulseTimer);
    const resData = await res.json();

    if (res.ok && resData.success) {
      vid.status = "completed"; vid.progress = 100; vid.currentStage = 4;
      if (resData.keyframes?.length) vid.keyframes = resData.keyframes;
      if (resData.motion_clips?.length) vid.motion_clips = resData.motion_clips;
      if (resData.audio_stems?.length) vid.audio_stems = resData.audio_stems;
      if (resData.video_url) { vid.videoUrl = resData.video_url; vid.video_url = resData.video_url; }
      if (resData.cost_usd) vid.cost_usd = resData.cost_usd;

      advanceToMasterStage(vid);
      if (typeof fetchAndRenderChannelArchive === "function") fetchAndRenderChannelArchive();
      if (typeof fetchChannelHubVideos === "function") fetchChannelHubVideos();
    } else {
      vid.status = "failed"; vid.progress = 0;
      const dEl = document.getElementById("studio-banner-detail");
      if (dEl) dEl.textContent = `Production notice: ${resData.detail || 'Synthesis aborted or completed'}`;
      renderInspectorFromVideo(vid);
    }
  } catch (err) {
    clearInterval(pulseTimer);
    if (err.name === "AbortError") return;
    vid.status = "failed";
    const dEl = document.getElementById("studio-banner-detail");
    if (dEl) dEl.textContent = `Network error: ${err.message || err}`;
    renderInspectorFromVideo(vid);
  }
}

function advanceToMotionStage(vid) {
  vid.currentStage = 2; vid.progress = 50;
  renderInspectorFromVideo(vid);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
}

function advanceToAudioStage(vid) {
  vid.currentStage = 3; vid.progress = 75;
  renderInspectorFromVideo(vid);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
}

function advanceToMasterStage(vid) {
  vid.currentStage = 4; vid.status = "completed"; vid.progress = 100;
  const banner = document.getElementById("studio-queued-banner");
  if (banner) {
    const tEl = document.getElementById("studio-banner-title");
    if (tEl) tEl.textContent = "Production Complete!";
    const dEl = document.getElementById("studio-banner-detail");
    if (dEl) dEl.textContent = `Episode ${vid.id} 4K Master and stems rendered successfully.`;
    const bb = document.getElementById("studio-banner-phase-badge");
    if (bb) {
      bb.textContent = "✓ Completed";
      bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white";
    }
  }
  renderInspectorFromVideo(vid);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
}
