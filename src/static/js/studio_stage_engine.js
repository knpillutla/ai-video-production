// CineAI Studio: Progressive Stage-Gate Execution Engine (Live Artifact Polling & Stop/Resume)
let studioAbortController = null;

function stageGateRerollCurrent() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  if (vid.currentStage === 1) {
    startStudioLiveStageProgress(vid, "manual", "script");
  } else if (vid.currentStage === 2) {
    advanceToKeyframesStage(vid, null, true);
  } else if (vid.currentStage === 3) {
    advanceToAudioStage(vid);
  } else if (vid.currentStage === 4) {
    advanceToMotionStage(vid, null, true);
  } else if (vid.currentStage >= 5) {
    advanceToMasterStage(vid, true);
  }
}

function stageGateAdvanceNext() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  if (vid.currentStage === 1) advanceToKeyframesStage(vid);
  else if (vid.currentStage === 2) advanceToAudioStage(vid);
  else if (vid.currentStage === 3) advanceToMotionStage(vid);
  else if (vid.currentStage >= 4) advanceToMasterStage(vid);
}

async function stopStudioProduction(episodeId) {
  if (studioAbortController) {
    studioAbortController.abort();
    studioAbortController = null;
  }
  const ep = typeof findStudioEpisodeById === "function" ? findStudioEpisodeById(episodeId) : null;
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
  let ep = typeof findStudioEpisodeById === "function" ? findStudioEpisodeById(episodeId) : null;
  if (!ep) ep = currentActiveInspectorEpisode;
  if (!ep) return;
  ep.status = "processing";
  if (!ep.durationSeconds) {
    const eff = (typeof getEffectiveProductionDuration === "function") ? getEffectiveProductionDuration() : { durSec: 120, lpHours: 0.0 };
    ep.durationSeconds = eff.durSec;
    ep.longPlayHours = eff.lpHours;
  }
  startStudioLiveStageProgress(ep, ep.pipelineStrategy);
}

async function startStudioLiveStageProgress(vid, strategy, manualPhase) {
  if (!vid) return;
  currentActiveInspectorEpisode = vid;
  const currentGateUi = (typeof activePipelineStrategy !== "undefined" && activePipelineStrategy) ? activePipelineStrategy : "manual";
  const resolvedStrat = (strategy === "auto" || strategy === "autonomous") ? "auto" : ((strategy === "manual") ? "manual" : (vid.pipeline_strategy || vid.pipelineStrategy || currentGateUi));
  vid.pipelineStrategy = resolvedStrat;
  vid.pipeline_strategy = resolvedStrat;
  vid.status = "processing";
  studioAbortController = new AbortController();
  const resynthStartTime = new Date().toISOString();
  const tStartMs = Date.now();
  console.log(`${resynthStartTime}, process name: re-synthesize, step: pipeline execution, status: started, action: re-synthesize started, metadata: [starttime: ${resynthStartTime}, episode_id: ${vid.id || vid.episode_id}, strategy: ${vid.pipelineStrategy}]`);

  const isManual = (vid.pipelineStrategy === "manual");
  let isScriptOnly = false;
  let isPhotosOnly = false;
  let isMotionOnly = false;
  let isAudioOnly = false;
  let isMasterOnly = false;

  if (isManual) {
    if (manualPhase === "photos") {
      isPhotosOnly = true;
      vid.currentStage = 2;
      vid.progress = 25;
    } else if (manualPhase === "audio") {
      isAudioOnly = true;
      vid.currentStage = 3;
      vid.progress = 50;
    } else if (manualPhase === "motion") {
      isMotionOnly = true;
      vid.currentStage = 4;
      vid.progress = 75;
    } else if (manualPhase === "master") {
      isMasterOnly = true;
      vid.currentStage = 5;
      vid.progress = 90;
    } else {
      isScriptOnly = true;
      vid.currentStage = 1;
      vid.progress = 10;
    }
  } else {
    vid.currentStage = vid.currentStage || 1;
    vid.progress = Math.max(10, vid.progress || 10);
  }

  const banner = document.getElementById("studio-queued-banner");
  if (banner) {
    banner.className = "shrink-0 p-2 bg-emerald-50 dark:bg-emerald-950/90 border border-emerald-300 dark:border-emerald-500/50 rounded-xl flex items-center justify-between gap-3 shadow-md transition-all";
    const iconEl = document.getElementById("studio-banner-icon");
    if (iconEl) {
      iconEl.className = "w-6 h-6 rounded-lg bg-emerald-600/15 dark:bg-emerald-500/20 text-emerald-700 dark:text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0 border border-emerald-400/30";
      iconEl.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
    }
    const reqIdEl = document.getElementById("studio-banner-request-id");
    if (reqIdEl) reqIdEl.textContent = vid.jobId || `job_${vid.id || vid.episode_id}`;
    const tEl = document.getElementById("studio-banner-title");
    if (tEl) { tEl.textContent = isManual ? "Manual Stage Pipeline Active" : "Autonomous Pipeline Active (--id)"; tEl.className = "font-black text-emerald-950 dark:text-white"; }
    const dEl = document.getElementById("studio-banner-detail");
    if (dEl) { dEl.textContent = `Episode ${vid.id || vid.episode_id} ("${vid.title || 'Resuming'}"): Synthesizing & Assembling 4K Broadcast Master...`; dEl.className = "text-[10px] text-emerald-900 dark:text-gray-200 font-medium truncate"; }
    const bb = document.getElementById("studio-banner-phase-badge");
    if (bb) {
      bb.classList.remove("hidden");
      if (isScriptOnly) bb.textContent = "Stage 1: Generating Script & Storyboard (Gemini 2.5)";
      else if (isPhotosOnly) {
        const mLabel = (vid.imageModel && (vid.imageModel.includes("pro") || vid.imageModel.includes("ultra"))) ? "FLUX 1.1 Pro Ultra" : ((vid.imageModel && vid.imageModel.includes("zimage")) ? "Z-Image Turbo" : "FLUX.1-dev");
        bb.textContent = `Stage 2: Synthesizing Keyframes (${mLabel})`;
      } else if (isAudioOnly) bb.textContent = "Stage 3: Synthesizing Audio & Vocals (Azure TTS, Suno & 432Hz DSP)";
      else if (isMotionOnly) bb.textContent = "Stage 4: Synthesizing Motion (Wan 2.1 / Kling / Perspective Drone)";
      else bb.textContent = `Stage ${vid.currentStage || 5}: Rendering 4K Master & Long-Play Broadcast`;
      bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-600 text-white animate-pulse";
    }
    banner.classList.remove("hidden");
  }
  renderInspectorFromVideo(vid);
  if (typeof filterChannelArchive === "function") filterChannelArchive();

  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : (vid.channelId || vid.channel_id || "earth_serenade");
  const epId = vid.id || vid.episode_id || "EP-001";
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const durSec = vid.durationSeconds || (vid.duration ? parseInt(vid.duration, 10) : ((typeof getEffectiveProductionDuration === "function") ? getEffectiveProductionDuration().durSec : 120));

  const pollArtifacts = async () => {
    try {
      const fmtQ = encodeURIComponent(vid.format || vid.format_slug || "");
      const prodQ = encodeURIComponent(vid.production_name || "");
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&format=${fmtQ}&production_name=${prodQ}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        let changed = false;
        if (data.script && !vid.script) {
          vid.script = data.script;
          changed = true;
        }
        if (data.screenplay && (!vid.screenplay || JSON.stringify(vid.screenplay) !== JSON.stringify(data.screenplay))) {
          vid.screenplay = data.screenplay;
          changed = true;
        }
        if (data.pipeline_state && (!vid.pipeline_state || JSON.stringify(vid.pipeline_state) !== JSON.stringify(data.pipeline_state))) {
          vid.pipeline_state = data.pipeline_state;
          changed = true;
        }
        if (data.manifest && !vid.manifest) {
          vid.manifest = data.manifest;
          changed = true;
        }
        const sceneCount = data.screenplay?.scenes?.length || data.script?.scenes?.length || data.scenes?.length || vid.screenplay?.scenes?.length || vid.script?.scenes?.length || vid.scenes?.length || 0;
        if (sceneCount > 0 && (vid.numShots !== sceneCount || vid.num_shots !== sceneCount)) {
          vid.numShots = sceneCount;
          vid.num_shots = sceneCount;
          changed = true;
        }
        const reqShots = sceneCount || vid.numShots || vid.num_shots || 1;
        const vFmt = String(vid.format || vid.format_slug || "").toLowerCase().trim();
        if (Array.isArray(data.keyframes)) {
          if (data.keyframes.length > 0) {
            if (!vid.keyframes || vid.keyframes.length !== data.keyframes.length || vid.keyframes[0]?.isGenerating) {
              vid.keyframes = data.keyframes;
              if (!isManual && data.keyframes.length >= reqShots && vid.currentStage < 2) vid.currentStage = 2;
              changed = true;
            }
          } else if (Array.isArray(vid.keyframes) && vid.keyframes.length > 0) {
            const hasContaminated = vid.keyframes.some(kf => {
              const u = String(typeof kf === "object" ? kf.url : kf || "");
              return (u.includes("/relaxation/") && vFmt.includes("documentary")) || (u.includes("/documentary/") && vFmt.includes("relaxation"));
            });
            if (hasContaminated || (vid.status === "processing" && vid.currentStage <= 1)) {
              vid.keyframes = [];
              changed = true;
            }
          }
        }
        if (!isManual && data.stage && data.stage > vid.currentStage) {
          vid.currentStage = data.stage;
          changed = true;
        }
        if (Array.isArray(data.motion_clips)) {
          if (data.motion_clips.length > 0) {
            if (!vid.motion_clips || vid.motion_clips.length !== data.motion_clips.length || vid.motion_clips[0]?.isGenerating) {
              vid.motion_clips = data.motion_clips;
              if (!isManual && data.motion_clips.length >= reqShots && vid.currentStage < 4) vid.currentStage = 4;
              changed = true;
            }
          } else if (Array.isArray(vid.motion_clips) && vid.motion_clips.length > 0) {
            const hasContaminated = vid.motion_clips.some(mc => {
              const u = String(typeof mc === "object" ? mc.url : mc || "");
              return (u.includes("/relaxation/") && vFmt.includes("documentary")) || (u.includes("/documentary/") && vFmt.includes("relaxation"));
            });
            if (hasContaminated || (vid.status === "processing" && vid.currentStage <= 3)) {
              vid.motion_clips = [];
              changed = true;
            }
          }
        }
        if (Array.isArray(data.audio_stems)) {
          if (data.audio_stems.length > 0) {
            if (JSON.stringify(vid.audio_stems || []) !== JSON.stringify(data.audio_stems)) {
              vid.audio_stems = data.audio_stems;
              if (!isManual && data.audio_stems.length > 0 && vid.currentStage < 3) vid.currentStage = 3;
              changed = true;
            }
          } else if (Array.isArray(vid.audio_stems) && vid.audio_stems.length > 0) {
            const hasContaminated = vid.audio_stems.some(as => {
              const u = String(typeof as === "object" ? as.url : as || "");
              return (u.includes("/relaxation/") && vFmt.includes("documentary")) || (u.includes("/documentary/") && vFmt.includes("relaxation"));
            });
            if (hasContaminated || (vid.status === "processing" && vid.currentStage <= 2)) {
              vid.audio_stems = [];
              changed = true;
            }
          }
        }
        if (data.editions && data.editions.length > 0) {
          vid.editions = data.editions;
          changed = true;
        }
        if (data.long_play_editions && data.long_play_editions.length > 0) {
          vid.long_play_editions = data.long_play_editions;
          changed = true;
        }
        if (data.video_url && !vid.videoUrl) {
          vid.videoUrl = data.video_url;
          if (!isManual && vid.currentStage < 5) vid.currentStage = 5;
          changed = true;
        }

        if (changed) {
          renderInspectorFromVideo(vid);
          if (typeof filterChannelArchive === "function") filterChannelArchive();
        }
      }
    } catch (e) {}
  };

  let pulseVal = vid.progress || 10;
  pollArtifacts();
  const pulseTimer = setInterval(() => {
    if (vid.status !== "processing") { clearInterval(pulseTimer); return; }
    pulseVal = Math.min(92, pulseVal + 3);
    vid.progress = pulseVal;
    pollArtifacts();
  }, 2000);

  try {
    const res = await fetch("/api/production/local-produce", {
      method: "POST",
      signal: studioAbortController.signal,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: vid.concept ?? "",
        channel_id: chSlug,
        duration_seconds: durSec,
        episode_id: epId,
        user_id: uEmail,
        tier: (function() {
          const checkedRadio = document.querySelector('input[name="tier_choice"]:checked') || document.querySelector('input[name="production_tier"]:checked');
          if (checkedRadio && checkedRadio.value) return checkedRadio.value;
          const tierSelect = document.getElementById("studio-tier-select");
          if (tierSelect && tierSelect.value) return tierSelect.value;
          if (typeof currentTier !== "undefined" && currentTier) return currentTier;
          if (vid && (vid.tier || vid.tierKey)) return vid.tier || vid.tierKey;
          return "balanced";
        })(),
        motion_model: vid.motionModel || (durSec <= 10 ? "wan" : "auto"),
        image_model: vid.imageModel || "google_imagen3",
        enable_bgm: vid.enableBgm !== false,
        enable_voiceover: Boolean(vid.enableVoiceOver),
        dual_editions: Boolean(vid.dual_editions ?? document.getElementById("studio-toggle-dual-editions")?.checked),
        tts_model: document.getElementById("studio-tts-model")?.value || vid.ttsModel || "gemini",
        allow_fallback: vid.allowFallback || false,
        pipeline_strategy: vid.pipelineStrategy || vid.pipeline_strategy || (typeof activePipelineStrategy !== "undefined" ? activePipelineStrategy : "manual"),
        execution_mode: vid.execution_mode || vid.executionMode || (typeof activeExecutionMode !== "undefined" ? activeExecutionMode : "test"),
        script_only: isScriptOnly,
        photos_only: isPhotosOnly,
        motion_only: isMotionOnly,
        audio_only: isAudioOnly,
        master_only: isMasterOnly,
        num_shots: (function() {
          if (typeof isTravelOrSkylineChannel === "function" && isTravelOrSkylineChannel()) return -1;
          const g = ((document.getElementById("studio-genre-selector")?.value) || vid.genre || "").toLowerCase();
          const subg = ((document.getElementById("studio-subgenre-selector")?.value) || vid.sub_genre || "").toLowerCase();
          const arch = ((document.getElementById("studio-archetype-selector")?.value) || vid.primary_archetype || "").toLowerCase();
          if (
            g === "documentary" || g.startsWith("travel") || g.includes("tour") ||
            subg.includes("tour") || subg.includes("doc_places") ||
            arch.includes("tour") || arch.includes("itinerary") ||
            vid.numShots === -1 || vid.num_shots === -1 ||
            (typeof activeShotsCount !== "undefined" && activeShotsCount === -1)
          ) {
            return -1;
          }
          return (typeof activeExecutionMode !== "undefined" && activeExecutionMode === "prod")
            ? parseInt(document.getElementById("studio-prod-shots")?.value || "-1", 10)
            : (typeof activeShotsCount !== "undefined" ? activeShotsCount : -1);
        })(),
        long_play_hours: (typeof activeExecutionMode !== "undefined" && activeExecutionMode === "prod")
          ? ((typeof getEffectiveProductionDuration === "function") ? getEffectiveProductionDuration().lpHours : (parseFloat(document.getElementById("studio-stretch-hours")?.value) || 0.0))
          : (typeof activeBroadcastHours !== "undefined" ? activeBroadcastHours : (vid.longPlayHours || 0)),
        camera_motion: (function() {
          const g = ((document.getElementById("studio-genre-selector")?.value) || vid.genre || "").toLowerCase();
          const a = ((document.getElementById("studio-archetype-selector")?.value) || vid.primary_archetype || "").toLowerCase();
          if (g.includes("travel_walking") || a.includes("walking")) return "walking_tour_60fps";
          if (g.includes("travel") || a.includes("cit") || a.includes("skylin") || a.includes("wonder") || a.includes("remote") || a.includes("iconic")) return "slow_drone_forward";
          return "locked_tripod";
        })(),
        genre: vid.genre || document.getElementById("studio-genre-selector")?.value || "relax/nature",
        genre_label: (function() {
          const g = vid.genre || document.getElementById("studio-genre-selector")?.value || "relax/nature";
          const genresDict = (typeof ALL_STUDIO_GENRES !== "undefined") ? ALL_STUDIO_GENRES : {};
          return vid.genreLabel || vid.genre_label || genresDict[g] || document.getElementById("studio-genre-selector")?.selectedOptions?.[0]?.textContent?.trim() || "";
        })(),
        sub_genre: vid.sub_genre || vid.subGenre || document.getElementById("studio-subgenre-selector")?.value || null,
        sub_genre_label: (function() {
          const g = vid.genre || document.getElementById("studio-genre-selector")?.value || "relax/nature";
          const sg = vid.sub_genre || vid.subGenre || document.getElementById("studio-subgenre-selector")?.value || null;
          const subMap = (typeof STUDIO_SUBOPTIONS_MAP !== "undefined") ? STUDIO_SUBOPTIONS_MAP : {};
          return vid.subGenreLabel || vid.sub_genre_label || (subMap[g]?.find(x => x.val === sg)?.label) || document.getElementById("studio-subgenre-selector")?.selectedOptions?.[0]?.textContent?.trim() || "";
        })(),
        primary_archetype: vid.primary_archetype || vid.primaryArchetype || document.getElementById("studio-archetype-selector")?.value || null,
        primary_archetype_label: (function() {
          const g = vid.genre || document.getElementById("studio-genre-selector")?.value || "relax/nature";
          const arch = vid.primary_archetype || vid.primaryArchetype || document.getElementById("studio-archetype-selector")?.value || null;
          const archMap = (typeof STUDIO_ARCHETYPES_MAP !== "undefined") ? STUDIO_ARCHETYPES_MAP : {};
          return vid.primaryArchetypeLabel || vid.primary_archetype_label || (archMap[g]?.find(x => x.val === arch)?.label) || document.getElementById("studio-archetype-selector")?.selectedOptions?.[0]?.textContent?.trim() || "";
        })(),
        weather: (document.querySelector('input[name="studio_weather"]:checked')?.value || "normal"),
        production_name: (vid.production_name || document.getElementById("studio-production-name")?.value?.trim() || null),
        format: (vid.format_slug || (vid.format && !["16:9", "9:16"].includes(vid.format) ? vid.format : null) || document.getElementById("studio-active-format-val")?.value || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "documentary")),
        format_slug: (vid.format_slug || (vid.format && !["16:9", "9:16"].includes(vid.format) ? vid.format : null) || document.getElementById("studio-active-format-val")?.value || (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "documentary")),
        aspect_ratio: (vid.aspect_ratio || document.getElementById("studio-selected-format")?.value || "16:9"),
        force_rerun: Boolean(vid.force_rerun)
      })
    });

    clearInterval(pulseTimer);
    const resData = await res.json();

    if (res.ok && resData.success) {
      if (resData.script) {
        vid.script = resData.script;
        if (resData.script.title) vid.title = resData.script.title;
        if (resData.script.story_topic) vid.story_topic = resData.script.story_topic;
        if (resData.script.audio_tags) vid.audio_tags = resData.script.audio_tags;
        const screenplaySceneCount = resData.script.scenes?.length || 0;
        if (screenplaySceneCount > 0) {
          vid.numShots = screenplaySceneCount;
          vid.num_shots = screenplaySceneCount;
        }
      }
      if (resData.keyframes?.length) {
        vid.keyframes = resData.keyframes;
        vid.selectedKeyframeIds = vid.keyframes.map((_, i) => i);
        vid.force_rerun = false;
      }
      if (resData.motion_clips?.length) vid.motion_clips = resData.motion_clips;
      if (resData.audio_stems?.length) vid.audio_stems = resData.audio_stems;
      if (resData.video_url) { vid.videoUrl = resData.video_url; vid.video_url = resData.video_url; }
      if (resData.editions?.length) vid.editions = resData.editions;
      if (resData.cost_usd !== undefined) vid.cost_usd = resData.cost_usd;

      if (isManual && isScriptOnly) {
        vid.status = "ready";
        vid.progress = 20;
        vid.currentStage = 1;
        vid.errorMessage = null;
        vid.failedStage = null;
        const bb = document.getElementById("studio-banner-phase-badge");
        if (bb) {
          bb.textContent = "Stage 1: Script Ready (Approve Photos Below)";
          bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-600 text-white";
        }
        const banner = document.getElementById("studio-queued-banner");
        if (banner) {
          const tEl = document.getElementById("studio-banner-title");
          if (tEl) tEl.textContent = "Director Script Ready";
          const dEl = document.getElementById("studio-banner-detail");
          if (dEl) dEl.textContent = `Episode ${vid.id || vid.episode_id}: Script created. Click "View Script" or Approve & Generate Photos.`;
        }
      } else if (isManual && isPhotosOnly) {
        vid.status = "ready";
        vid.progress = 40;
        vid.currentStage = 2;
        vid.force_rerun = false;
        vid.errorMessage = null;
        vid.failedStage = null;
        const bb = document.getElementById("studio-banner-phase-badge");
        if (bb) {
          bb.textContent = "Stage 2: Keyframe Photos Ready (Approve Audio Below)";
          bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-blue-600 text-white";
        }
        const banner = document.getElementById("studio-queued-banner");
        if (banner) {
          const tEl = document.getElementById("studio-banner-title");
          if (tEl) tEl.textContent = "Keyframe Photos Ready";
          const dEl = document.getElementById("studio-banner-detail");
          if (dEl) dEl.textContent = `Episode ${vid.id || vid.episode_id}: Photos synthesized. Approve below to compose audio.`;
        }
      } else if (isManual && isAudioOnly) {
        vid.status = "ready";
        vid.progress = 60;
        vid.currentStage = 3;
        vid.errorMessage = null;
        vid.failedStage = null;
        const bb = document.getElementById("studio-banner-phase-badge");
        if (bb) {
          bb.textContent = "Stage 3: Audio Stems Ready (Approve Motion Below)";
          bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-cyan-600 text-white";
        }
        const banner = document.getElementById("studio-queued-banner");
        if (banner) {
          const tEl = document.getElementById("studio-banner-title");
          if (tEl) tEl.textContent = "Audio Stems Ready";
          const dEl = document.getElementById("studio-banner-detail");
          if (dEl) dEl.textContent = `Episode ${vid.id || vid.episode_id}: Audio stems ready. Approve below to render video motion.`;
        }
      } else if (isManual && isMotionOnly) {
        vid.status = "ready";
        vid.progress = 80;
        vid.currentStage = 4;
        vid.errorMessage = null;
        vid.failedStage = null;
        const bb = document.getElementById("studio-banner-phase-badge");
        if (bb) {
          bb.textContent = "Stage 4: Video Motion Ready (Approve 4K Master Below)";
          bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-purple-600 text-white";
        }
        const banner = document.getElementById("studio-queued-banner");
        if (banner) {
          const tEl = document.getElementById("studio-banner-title");
          if (tEl) tEl.textContent = "Video Motion Ready";
          const dEl = document.getElementById("studio-banner-detail");
          if (dEl) dEl.textContent = `Episode ${vid.id || vid.episode_id}: Motion clips rendered. Approve below to assemble 4K Master.`;
        }
      } else {
        vid.status = "completed"; vid.progress = 100; vid.currentStage = 5;
        vid.errorMessage = null; vid.failedStage = null;
        const banner = document.getElementById("studio-queued-banner");
        if (banner) {
          const tEl = document.getElementById("studio-banner-title");
          if (tEl) tEl.textContent = "Production Complete!";
          const dEl = document.getElementById("studio-banner-detail");
          if (dEl) dEl.textContent = `Episode ${vid.id || vid.episode_id} 4K Master and stems rendered successfully.`;
          const bb = document.getElementById("studio-banner-phase-badge");
          if (bb) {
            bb.textContent = "✓ Completed";
            bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white";
          }
        }
        if (typeof fetchAndRenderChannelArchive === "function") fetchAndRenderChannelArchive();
        if (typeof fetchChannelHubVideos === "function") fetchChannelHubVideos();
        const resynthEndTime = new Date().toISOString();
        const totalDurSec = ((Date.now() - tStartMs) / 1000).toFixed(2);
        console.log(`${resynthEndTime}, process name: re-synthesize, step: pipeline execution, status: completed, action: re-synthesize ended, metadata: [starttime: ${resynthStartTime}, endtime: ${resynthEndTime}, total_time: ${totalDurSec}s, episode_id: ${vid.id || vid.episode_id}]`);
      }
      renderInspectorFromVideo(vid);
      if (typeof updateStageGateDock === "function") updateStageGateDock(vid);
      if (typeof saveVideosState === "function") saveVideosState();
      if (typeof fetchAndRenderChannelArchive === "function") fetchAndRenderChannelArchive();
      else if (typeof filterChannelArchive === "function") filterChannelArchive();
    } else {
      const errMsg = resData.detail || resData.message || "Synthesis failed.";
      const fStage = detectFailedStage(errMsg, vid.currentStage);
      vid.status = "failed"; vid.progress = 0; vid.failedStage = fStage; vid.errorMessage = errMsg;
      const bb = document.getElementById("studio-banner-phase-badge");
      if (bb) { bb.textContent = `❌ Stage ${fStage} Failed`; bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-red-600 text-white shadow-sm"; }
      const banner = document.getElementById("studio-queued-banner");
      if (banner) {
        banner.classList.remove("hidden");
        banner.className = "shrink-0 p-2.5 bg-red-50 dark:bg-red-950/90 border-2 border-red-500 rounded-xl flex items-center justify-between gap-3 shadow-md transition-all";
        const iconEl = document.getElementById("studio-banner-icon");
        if (iconEl) {
          iconEl.className = "w-6 h-6 rounded-lg bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300 flex items-center justify-center font-bold text-xs shrink-0 border border-red-400";
          iconEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
        }
        const tEl = document.getElementById("studio-banner-title");
        if (tEl) { tEl.textContent = `Stage ${fStage} Error:`; tEl.className = "font-black text-red-700 dark:text-red-300"; }
        const dEl = document.getElementById("studio-banner-detail");
        if (dEl) { dEl.textContent = errMsg; dEl.className = "text-[11px] text-red-700 dark:text-red-300 font-bold font-mono break-all"; }
      }
      renderInspectorFromVideo(vid);
      if (typeof filterChannelArchive === "function") filterChannelArchive();
    }
  } catch (err) {
    clearInterval(pulseTimer);
    if (err.name === "AbortError") return;
    const errMsg = err.message || String(err);
    const fStage = detectFailedStage(errMsg, vid.currentStage);
    vid.status = "failed"; vid.progress = 0; vid.failedStage = fStage; vid.errorMessage = errMsg;
    const bb = document.getElementById("studio-banner-phase-badge");
    if (bb) { bb.textContent = `❌ Stage ${fStage} Error`; bb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-red-600 text-white shadow-sm"; }
    const banner = document.getElementById("studio-queued-banner");
    if (banner) {
      banner.classList.remove("hidden");
      banner.className = "shrink-0 p-2.5 bg-red-50 dark:bg-red-950/90 border-2 border-red-500 rounded-xl flex items-center justify-between gap-3 shadow-md transition-all";
      const iconEl = document.getElementById("studio-banner-icon");
      if (iconEl) {
        iconEl.className = "w-6 h-6 rounded-lg bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-300 flex items-center justify-center font-bold text-xs shrink-0 border border-red-400";
        iconEl.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i>';
      }
      const tEl = document.getElementById("studio-banner-title");
      if (tEl) { tEl.textContent = `Stage ${fStage} Error:`; tEl.className = "font-black text-red-700 dark:text-red-300"; }
      const dEl = document.getElementById("studio-banner-detail");
      if (dEl) { dEl.textContent = errMsg; dEl.className = "text-[11px] text-red-700 dark:text-red-300 font-bold font-mono break-all"; }
    }
    renderInspectorFromVideo(vid);
    if (typeof filterChannelArchive === "function") filterChannelArchive();
  }
}

function detectFailedStage(errMsg, currentStage) {
  const msg = String(errMsg || "").toLowerCase();
  if (msg.includes("ffmpeg") || msg.includes("master") || msg.includes("assembly") || msg.includes("concat") || msg.includes("broadcast")) return 5;
  if (msg.includes("diffusion") || msg.includes("kling") || msg.includes("wan") || msg.includes("motion") || msg.includes("video clip") || msg.includes("render_motion")) return 4;
  if (msg.includes("suno") || msg.includes("soundtrack") || msg.includes("binaural") || msg.includes("foley") || msg.includes("audio") || msg.includes("speech") || msg.includes("tts")) return 3;
  if (msg.includes("keyframe") || msg.includes("flux") || msg.includes("photo") || (msg.includes("image") && !msg.includes("imageio"))) return 2;
  if (msg.includes("gemini") || msg.includes("storyboard") || msg.includes("script") || msg.includes("director")) return 1;
  return currentStage || 1;
}

function retryEpisodeWithFallback(epId) {
  const ep = typeof findStudioEpisodeById === "function" ? findStudioEpisodeById(epId) : null;
  if (!ep) return;
  ep.allowFallback = true;
  ep.status = "processing";
  ep.errorMessage = null;
  ep.failedStage = null;
  startStudioLiveStageProgress(ep, ep.pipelineStrategy);
}

function advanceToKeyframesStage(vid, imageModelOverride, forceRerun = false) {
  let target = vid || currentActiveInspectorEpisode;
  if (!target) return;
  target.currentStage = 2;
  target.status = "processing";
  target.progress = 25;
  target.force_rerun = Boolean(forceRerun);
  if (imageModelOverride) {
    target.imageModel = imageModelOverride;
  } else if (!target.imageModel) {
    target.imageModel = "flux_dev";
  }
  currentActiveInspectorEpisode = target;
  renderInspectorFromVideo(target);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  startStudioLiveStageProgress(target, "manual", "photos");
}

function advanceToAudioStage(vid, ttsModelOverride, forceRerun = false) {
  let target = vid || currentActiveInspectorEpisode;
  if (!target) return;
  target.currentStage = 3;
  target.status = "processing";
  target.progress = 50;
  target.force_rerun = Boolean(forceRerun);
  if (ttsModelOverride) {
    target.ttsModel = ttsModelOverride;
    const ttsSelect = document.getElementById("studio-tts-model");
    if (ttsSelect) ttsSelect.value = ttsModelOverride;
  }
  currentActiveInspectorEpisode = target;
  renderInspectorFromVideo(target);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  startStudioLiveStageProgress(target, "manual", "audio");
}

function advanceToMotionStage(vid, motionModelOverride, forceRerun = false) {
  let target = vid || currentActiveInspectorEpisode;
  if (!target) return;
  target.currentStage = 4;
  target.status = "processing";
  target.progress = 75;
  target.force_rerun = Boolean(forceRerun);
  if (motionModelOverride) {
    target.motionModel = motionModelOverride;
  }
  const checkedWeather = document.querySelector('input[name="studio_weather"]:checked')?.value;
  if (checkedWeather) {
    target.weather = checkedWeather;
  }
  currentActiveInspectorEpisode = target;
  renderInspectorFromVideo(target);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  startStudioLiveStageProgress(target, "manual", "motion");
}

function advanceToMasterStage(vid, forceRerun = false) {
  let target = vid || currentActiveInspectorEpisode;
  if (!target) return;
  target.currentStage = 5;
  target.status = "processing";
  target.progress = 90;
  target.force_rerun = Boolean(forceRerun);
  currentActiveInspectorEpisode = target;
  renderInspectorFromVideo(target);
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  startStudioLiveStageProgress(target, "manual", "master");
}

async function reprocessActiveEpisodeId(episodeId, motionModelOverride, forceRerun = false) {
  let ep = currentActiveInspectorEpisode;
  const targetId = episodeId || (ep ? (ep.id || ep.episode_id) : "EP-001");
  const curCh = ep?.channelId || ep?.channel_id;
  const curFmt = ep?.format || ep?.format_slug;
  const curProd = ep?.production_name;
  if (!ep && typeof studioVideos !== "undefined") {
    const found = typeof findStudioEpisodeById === "function" ? findStudioEpisodeById(targetId, curCh, curFmt, curProd) : null;
    if (found) ep = found;
  }
  if (!ep && typeof channelArchiveEpisodes !== "undefined") {
    const found = typeof findStudioEpisodeById === "function" ? findStudioEpisodeById(targetId, curCh, curFmt, curProd) : null;
    if (found) ep = found;
  }
  const activeStrat = (typeof activePipelineStrategy !== "undefined" && activePipelineStrategy) ? activePipelineStrategy : (ep?.pipeline_strategy || ep?.pipelineStrategy || "manual");
  const activeExec = (typeof activeExecutionMode !== "undefined" && activeExecutionMode) ? activeExecutionMode : (ep?.execution_mode || ep?.executionMode || "test");
  if (!ep) {
    ep = {
      id: targetId,
      episode_id: targetId,
      title: `Episode ${targetId}`,
      status: "processing",
      pipelineStrategy: activeStrat,
      pipeline_strategy: activeStrat,
      executionMode: activeExec,
      execution_mode: activeExec
    };
  }
  ep.id = targetId;
  ep.episode_id = targetId;
  ep.status = "processing";
  ep.pipelineStrategy = activeStrat;
  ep.pipeline_strategy = activeStrat;
  ep.executionMode = activeExec;
  ep.execution_mode = activeExec;
  ep.is_approved = true;
  ep.errorMessage = null;
  ep.failedStage = null;
  ep.force_rerun = Boolean(forceRerun);
  if (motionModelOverride) {
    ep.motionModel = motionModelOverride;
  }
  currentActiveInspectorEpisode = ep;
  renderInspectorFromVideo(ep);
  if (typeof filterChannelArchive === "function") filterChannelArchive();

  const chSlug = ep.channelId || ep.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : "skylinediariesindia4k");
  ep.channelId = chSlug;
  ep.channel_id = chSlug;
  console.log(`[REPROCESS] Reprocessing episode ${targetId} for channel ${chSlug} (${activeStrat} mode, ${activeExec})`);

  // Persist disk approval and user inputs
  try {
    const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
    fetch(`/api/production/episodes/${targetId}/approve?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "POST" }).catch(() => {});
    const fmt = ep.format || ep.format_slug || "";
    const prod = ep.production_name || "";
    fetch(`/api/production/episodes/${encodeURIComponent(targetId)}/update-inputs?channel_id=${encodeURIComponent(chSlug)}&format=${encodeURIComponent(fmt)}&production_name=${encodeURIComponent(prod)}&user_id=${encodeURIComponent(uEmail)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ pipeline_strategy: activeStrat, execution_mode: activeExec })
    }).catch(() => {});
  } catch (e) {}

  // Resumes pipeline respecting user Gate setting (Manual: resumes current pending phase and stops; Auto: end-to-end)
  let targetPhase = null;
  if (activeStrat === "manual") {
    const hasScript = Boolean(ep.script || ep.storyboard || ep.screenplay);
    const rawKfs = (ep.keyframes && ep.keyframes.length > 0) ? ep.keyframes : (ep.artifacts?.keyframes || []);
    const completedKfs = rawKfs.filter(kf => {
      const url = (typeof kf === "object") ? kf.url : kf;
      return url && (url.startsWith("http") || url.startsWith("/static/") || url.startsWith("/storage/")) && !url.includes("placeholder_");
    });
    const hasPhotos = Boolean(completedKfs.length > 0);
    const rawStems = (ep.audio_stems && ep.audio_stems.length > 0) ? ep.audio_stems : (ep.artifacts?.audio_stems || []);
    const completedStems = rawStems.filter(st => {
      const url = (typeof st === "object") ? st.url : st;
      return url && !String(url).includes("placeholder_");
    });
    const hasAudio = Boolean(completedStems.length > 0);
    const rawClips = (ep.motion_clips && ep.motion_clips.length > 0) ? ep.motion_clips : (ep.artifacts?.motion_clips || []);
    const completedClips = rawClips.filter(mc => {
      const url = (typeof mc === "object") ? mc.url : mc;
      return url && !String(url).includes("placeholder_");
    });
    const hasMotion = Boolean(completedClips.length > 0);

    if (!hasScript) targetPhase = "script";
    else if (!hasPhotos) targetPhase = "photos";
    else if (!hasAudio) targetPhase = "audio";
    else if (!hasMotion) targetPhase = "motion";
    else targetPhase = "master";
  }
  startStudioLiveStageProgress(ep, activeStrat, targetPhase);
}

