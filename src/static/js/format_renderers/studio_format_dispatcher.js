/**
 * Studio Format Artifacts Dispatcher.
 * Decouples format UI, activates format-specific artifact panels, and coordinates 21-chapter auto-creation.
 */
(function(window) {
  "use strict";

  const FORMAT_STAGE_WORKFLOWS = {
    documentary: {
      format: "documentary",
      createEndpoint: "/api/documentary/create-episode",
      pollEndpoint: "/api/documentary/poll-artifacts",
      stages: [
        { num: 1, key: "story", phase: "story", label: "1. Story (21 Ch)", endpoint: "/api/documentary/stages/story" },
        { num: 2, key: "narration", phase: "narration", label: "2. Narration", endpoint: "/api/documentary/stages/narration" },
        { num: 3, key: "script", phase: "screenplay", label: "3. Screenplay", endpoint: "/api/documentary/stages/screenplay" },
        { num: 4, key: "images", phase: "photos", label: "4. Photos", endpoint: "/api/documentary/stages/photos" },
        { num: 5, key: "audio", phase: "bgm", label: "5. BGM", endpoint: "/api/documentary/stages/bgm" },
        { num: 6, key: "motion", phase: "motion", label: "6. Motion", endpoint: "/api/documentary/stages/motion" },
        { num: 7, key: "master", phase: "master", label: "7. 4K Master", endpoint: "/api/documentary/stages/master" },
      ],
    },
    relaxation: {
      format: "relaxation",
      createEndpoint: "/api/relaxation/create-episode",
      pollEndpoint: "/api/local-production/poll-artifacts",
      stages: [
        { num: 1, key: "script", phase: "script", label: "1. Storyboard", endpoint: "/api/relaxation/stages/script" },
        { num: 2, key: "images", phase: "photos", label: "2. Photos", endpoint: "/api/relaxation/stages/photos" },
        { num: 3, key: "audio", phase: "audio", label: "3. ASMR Audio", endpoint: "/api/relaxation/stages/audio" },
        { num: 4, key: "motion", phase: "motion", label: "4. Motion", endpoint: "/api/relaxation/stages/motion" },
        { num: 5, key: "master", phase: "master", label: "5. Master", endpoint: "/api/relaxation/stages/master" },
        { num: 6, key: "longplay", phase: "longplay", label: "6. Long-Play", endpoint: "/api/long-play/render" },
      ],
    },
    music_video: {
      format: "music_video",
      createEndpoint: "/api/music-video/produce",
      pollEndpoint: "/api/music-video/poll-artifacts",
      stages: [
        { num: 1, key: "script", phase: "script", label: "1. Lyrics", endpoint: "/api/music-video/stages/script" },
        { num: 2, key: "images", phase: "photos", label: "2. Photos", endpoint: "/api/music-video/stages/photos" },
        { num: 3, key: "audio", phase: "audio", label: "3. Song Master", endpoint: "/api/music-video/stages/audio" },
        { num: 4, key: "motion", phase: "motion", label: "4. Lip-Sync", endpoint: "/api/music-video/stages/motion" },
        { num: 5, key: "master", phase: "master", label: "5. 4K Master", endpoint: "/api/music-video/stages/master" },
      ],
    },
  };
  window.FORMAT_STAGE_WORKFLOWS = FORMAT_STAGE_WORKFLOWS;

  function resolveStageEndpoint(fmt, phase) {
    const wf = FORMAT_STAGE_WORKFLOWS[fmt] || FORMAT_STAGE_WORKFLOWS.documentary;
    const p = (phase || "").toLowerCase();
    const match = wf.stages.find(s => s.phase === p || s.key === p);
    if (match && match.endpoint) return match.endpoint;
    if (fmt === "documentary") return `/api/documentary/stages/${p || "screenplay"}`;
    if (fmt === "music_video") return `/api/music-video/stages/${p || "script"}`;
    return `/api/relaxation/stages/${p || "script"}`;
  }

  function resolveEffectiveFormat(vid) {
    if (!vid) return "documentary";
    const rawFmt = (vid.format_slug || vid.format || "").toLowerCase();
    const g = (vid.genre || "").toLowerCase();
    const ch = (vid.channel_id || "").toLowerCase();

    if (rawFmt === "music_video" || g.startsWith("music/") || g.startsWith("dance/")) {
      return "music_video";
    }
    if (rawFmt === "relaxation" || g.includes("relax") || g.includes("ambient") || g.includes("sleep") || g.includes("hearth") || ch.includes("earth_serenade") || ch.includes("silent_hearth")) {
      return "relaxation";
    }
    return "documentary";
  }

  function dispatchFormatArtifacts(vid) {
    if (!vid) return;
    const fmt = resolveEffectiveFormat(vid);

    // 1. Toggle Format-Specific Artifact Panels
    const docPanel = document.getElementById("artifact-panel-documentary");
    const relaxPanel = document.getElementById("artifact-panel-relaxation");
    const mvPanel = document.getElementById("artifact-panel-music_video");

    if (docPanel) docPanel.classList.toggle("hidden", fmt !== "documentary");
    if (relaxPanel) relaxPanel.classList.toggle("hidden", fmt !== "relaxation");
    if (mvPanel) mvPanel.classList.toggle("hidden", fmt !== "music_video");

    // 2. Update Top Horizontal Stage Scroll Pills
    renderFormatStagePills(fmt, vid);

    // 3. Delegate to Format-Specific Renderer
    if (fmt === "documentary") {
      if (window.DocumentaryArtifactsRenderer) {
        window.DocumentaryArtifactsRenderer.render(vid);
      }
    } else if (fmt === "relaxation") {
      if (window.RelaxationArtifactsRenderer) {
        window.RelaxationArtifactsRenderer.render(vid);
      }
    }
  }

  function renderFormatStagePills(fmt, vid) {
    const scrollContainer = document.getElementById("panel-header-stage-scroll");
    if (!scrollContainer) return;

    const wf = FORMAT_STAGE_WORKFLOWS[fmt] || FORMAT_STAGE_WORKFLOWS.documentary;
    const stages = wf.stages || [];
    const curStage = vid.currentStage || 1;
    scrollContainer.innerHTML = stages.map(s => {
      const isPast = curStage > s.num;
      const isCurr = curStage === s.num;
      const cls = isCurr
        ? "px-2 py-0.5 rounded font-bold bg-purple-500/20 text-purple-600 dark:text-purple-300 border border-purple-500/30"
        : (isPast ? "px-2 py-0.5 rounded font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" : "px-2 py-0.5 rounded text-[var(--text-muted)] opacity-60");
      return `<span class="${cls} shrink-0 cursor-pointer" onclick="scrollToStageSection('${s.key}')">${s.label}</span>`;
    }).join("");
  }

  let docEpisodeMutex = false;
  let docProgressTimer = null;

  async function createDocumentaryEpisodeAutoStory(destination, prompt, channelId) {
    if (docEpisodeMutex) {
      console.warn("createDocumentaryEpisode already in progress, skipping duplicate call.");
      return null;
    }
    docEpisodeMutex = true;

    if (docProgressTimer) {
      clearInterval(docProgressTimer);
      docProgressTimer = null;
    }

    const ch = channelId || (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all" ? selectedStudioChannel : "euro_discovery");
    const userPrompt = (prompt || document.getElementById("youtube-prompt-input")?.value || document.getElementById("studio-prompt-input")?.value || "").trim();
    const prodNameInput = (destination || document.getElementById("studio-production-name")?.value || "").trim();
    const gVal = document.getElementById("studio-genre-selector")?.value || "doc/nations";
    const subVal = document.getElementById("studio-subgenre-selector")?.value || "europe_nations";
    const archVal = document.getElementById("studio-archetype-selector")?.value || "countries";
    const uEmail = (typeof currentUser !== "undefined" && currentUser?.email) ? currentUser.email : "knpillutla@gmail.com";
    const labelDest = prodNameInput || userPrompt || "Sovereign Nation";

    // 1. Activate Documentary panel and show smooth horizontal progress bar in Stage 1
    const docPanel = document.getElementById("artifact-panel-documentary");
    if (docPanel) docPanel.classList.remove("hidden");

    let progressPct = 25;
    if (window.DocumentaryArtifactsRenderer && typeof window.DocumentaryArtifactsRenderer.setStoryLoading === "function") {
      window.DocumentaryArtifactsRenderer.setStoryLoading(true, `Synthesizing ${labelDest} 21 Sovereign Chapters...`, progressPct, "Compiling Capital, Demographics, Area & Governance...");
    }

    docProgressTimer = setInterval(() => {
      if (progressPct < 85) {
        progressPct += 15;
        if (window.DocumentaryArtifactsRenderer && typeof window.DocumentaryArtifactsRenderer.setStoryLoading === "function") {
          window.DocumentaryArtifactsRenderer.setStoryLoading(true, `Synthesizing ${labelDest} 21 Sovereign Chapters...`, progressPct, "Narrating Universities, Clean Energy, Ports & Living Culture...");
        }
      }
    }, 400);

    try {
      const res = await fetch("/api/documentary/create-episode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          channel_id: ch,
          destination: prodNameInput || null,
          prompt: userPrompt || null,
          genre: gVal,
          sub_genre: subVal,
          primary_archetype: archVal,
          user_id: uEmail,
        })
      });

      if (docProgressTimer) {
        clearInterval(docProgressTimer);
        docProgressTimer = null;
      }

      const data = await res.json();
      if (res.ok && data.success) {
        const destName = data.destination_entity || labelDest || "Sovereign Nation";
        if (window.DocumentaryArtifactsRenderer && typeof window.DocumentaryArtifactsRenderer.setStoryLoading === "function") {
          window.DocumentaryArtifactsRenderer.setStoryLoading(true, `Synthesizing ${destName} 21 Sovereign Chapters...`, 100, "21 Sovereign Chapters Ready!");
        }

        setTimeout(() => {
          if (window.DocumentaryArtifactsRenderer && typeof window.DocumentaryArtifactsRenderer.setStoryLoading === "function") {
            window.DocumentaryArtifactsRenderer.setStoryLoading(false);
          }
          let target = (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) ? currentActiveInspectorEpisode : null;
          if (!target || (target.id !== data.episode_id && target.episode_id !== data.episode_id)) {
            target = {
              id: data.episode_id,
              episode_id: data.episode_id,
              channel_id: ch,
              format: "documentary",
              format_slug: "documentary",
              title: data.title,
              production_name: data.destination_entity,
              currentStage: 1,
              progress: 20,
              status: "ready",
              story: data.story,
              raw_story: data.story,
              keyframes: [],
              audio_stems: [],
              motion_clips: [],
            };
            if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
              studioVideos.unshift(target);
            }
          } else {
            target.title = data.title;
            target.production_name = data.destination_entity;
            target.story = data.story;
            target.raw_story = data.story;
            target.status = "ready";
            target.currentStage = 1;
            target.progress = 20;
          }

          const pInput = document.getElementById("studio-production-name");
          if (pInput) pInput.value = data.destination_entity;
          const epCode = document.getElementById("studio-episode-code");
          if (epCode) epCode.value = data.episode_id;
          window.currentActiveInspectorEpisode = target;
          dispatchFormatArtifacts(target);
          if (typeof filterChannelArchive === "function") filterChannelArchive();
          if (typeof renderStudioVideoHistory === "function") renderStudioVideoHistory();
        }, 300);

        return data;
      }
    } catch (e) {
      if (docProgressTimer) {
        clearInterval(docProgressTimer);
        docProgressTimer = null;
      }
      console.warn("failed_doc_create_episode_auto_story:", e);
      if (window.DocumentaryArtifactsRenderer && typeof window.DocumentaryArtifactsRenderer.setStoryLoading === "function") {
        window.DocumentaryArtifactsRenderer.setStoryLoading(false);
      }
    } finally {
      docEpisodeMutex = false;
    }
    return null;
  }

  // Hook for button clicks in inspector
  window.autoGenerateDocStoryForEpisode = async function(vid) {
    if (!vid) return;
    const dest = vid.country || vid.destination_entity || null;
    const promptText = vid.concept || vid.title || "";
    return await createDocumentaryEpisodeAutoStory(dest, promptText, vid.channel_id);
  };

  window.StudioFormatDispatcher = {
    dispatch: dispatchFormatArtifacts,
    resolveFormat: resolveEffectiveFormat,
    resolveStageEndpoint: resolveStageEndpoint,
    workflows: FORMAT_STAGE_WORKFLOWS,
    createDocumentaryEpisode: createDocumentaryEpisodeAutoStory,
  };
})(window);
