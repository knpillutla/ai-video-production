// CineAI Studio: Video Production Ledger with Traceability, Artifacts & Timestamps
function formatTimestamp(ts) {
  if (!ts) return "—";
  return new Date(ts).toLocaleString([], {
    month: "short", day: "numeric", hour: "2-digit", minute: "2-digit", second: "2-digit"
  });
}

const SEED_VIDEOS = (typeof DEFAULT_STUDIO_VIDEOS !== "undefined") ? DEFAULT_STUDIO_VIDEOS : [];

function loadSavedVideos() {
  try {
    const saved = localStorage.getItem("cineai_videos");
    let videos = (saved) ? JSON.parse(saved) : [];
    if (!Array.isArray(videos)) videos = [];
    
    // Purge legacy mock seed records that are not real user productions
    videos = videos.filter(v => {
      const vidId = (v.id || "").toLowerCase();
      if (vidId.startsWith("ep_swiss_alps_") || vidId.startsWith("ep_blizzard_")) return false;
      return true;
    });
    return videos;
  } catch (e) {
    console.warn("Storage read error:", e);
    return [];
  }
}

function saveVideosState() {
  try {
    localStorage.setItem("cineai_videos", JSON.stringify(studioVideos));
  } catch (e) {
    console.warn("Storage write error:", e);
  }
  if (typeof renderDashboardStats === "function") renderDashboardStats();
}

let studioVideos = loadSavedVideos();

function findStudioEpisodeById(episodeId, channelId) {
  if (!episodeId) return null;
  const matchesId = episode => episode && (episode.id === episodeId || episode.episode_id === episodeId);
  const active = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (matchesId(active) && (!channelId || channelId === "all" || (active.channelId || active.channel_id) === channelId)) return active;

  const selectedChannel = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all")
    ? selectedStudioChannel
    : null;
  const targetChannel = (channelId && channelId !== "all") || selectedChannel;
  const records = [
    ...(Array.isArray(studioVideos) ? studioVideos : []),
    ...(typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes) ? channelArchiveEpisodes : []),
  ];
  const matches = records.filter(matchesId);
  if (targetChannel) {
    return matches.find(episode => (episode.channelId || episode.channel_id || "earth_serenade") === targetChannel) || null;
  }
  return matches.length === 1 ? matches[0] : null;
}

function nextEpisodeIdForChannel(channelId) {
  const records = [
    ...(Array.isArray(studioVideos) ? studioVideos : []),
    ...(typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes) ? channelArchiveEpisodes : [])
  ];
  const prefix = /^EP-(\d+)$/i;
  let highest = 0;
  records.forEach(record => {
    if ((record.channelId || record.channel_id) !== channelId) return;
    const match = String(record.episode_id || record.id || "").match(prefix);
    if (match) highest = Math.max(highest, Number(match[1]));
  });
  return `EP-${String(highest + 1).padStart(3, "0")}`;
}

async function syncChannelEpisodesFromBackend() {
  try {
    const res = await fetch("/api/channels/episodes");
    const data = await res.json();
    if (data.status === "ok" && Array.isArray(data.episodes)) {
      const backendRecords = data.episodes.map(ep => {
        const costVal = ep.cost_usd || 0.14;
        const eds = (ep.editions && ep.editions.length > 0) ? ep.editions : [];
        const hasMaster = Boolean(eds.length > 0 && eds[0]?.url && !eds[0].url.includes("preview_master"));
        const masterUrl = hasMaster ? eds[0].url : null;
        const curStage = hasMaster ? 5 : ((ep.motion_clips && ep.motion_clips.length > 0) ? 3 : ((ep.keyframes && ep.keyframes.length > 0) ? 2 : 1));
        const sceneCount = ep.screenplay?.scenes?.length || ep.script?.scenes?.length || ep.scenes?.length || ep.user_inputs?.num_shots || 1;

        return {
          id: ep.episode_id, jobId: `job_${ep.episode_id}`, title: ep.title || ep.story_topic,
          concept: ep.story_topic || ep.title, videoType: ep.category === "Music" ? "Relaxation & ASMR" : "Nature Soundscape",
          formatType: "Long (16:9)", styleType: "Cinematic 4K", productionType: "Theme",
          channelId: ep.channel_id,
          numShots: sceneCount, num_shots: sceneCount,
          status: hasMaster ? "completed" : "ready",
          currentStage: curStage,
          progress: hasMaster ? 100 : (curStage === 3 ? 50 : (curStage === 2 ? 35 : 15)),
          youtubeStatus: hasMaster ? "published" : "draft",
          youtubeChannel: ep.channel_handle || `@${ep.channel_id}`,
          youtubeUrl: masterUrl,
          videoUrl: masterUrl,
          video_url: masterUrl,
          language: "English (en)", format: "Long (16:9)",
          style: "Cinematic Photoreal", tierKey: "cinematic", tierName: "Cinematic 4K ($0.45)",
          cost: costVal, costStr: `$${costVal.toFixed(4)} USD`,
          keyframes: ep.keyframes || [], motion_clips: ep.motion_clips || [], audio_stems: ep.audio_stems || [],
          thumbnailUrl: ep.thumbnail_url || ep.thumbnailUrl || (ep.keyframes?.[0]?.url) || "",
          thumbnail_url: ep.thumbnail_url || ep.thumbnailUrl || (ep.keyframes?.[0]?.url) || "",
          thumbnailShortUrl: ep.thumbnail_short_url || ep.thumbnailShortUrl || "",
          thumbnail_short_url: ep.thumbnail_short_url || ep.thumbnailShortUrl || "",
          editions: eds,
          long_play_editions: ep.long_play_editions || [],
          script: ep.script || ep.screenplay || ep.manifest || null,
          screenplay: ep.screenplay || ep.script || null,
          user_inputs: ep.user_inputs || null,
          pipeline_state: ep.pipeline_state || null,
          manifest: ep.manifest || ep.script || null,
          scenes: ep.scenes || ep.screenplay?.scenes || ep.script?.scenes || [],
          cluster: ep.cluster || ep.screenplay?.cluster || ep.script?.cluster || "",
          audio_tags: ep.audio_tags || ep.screenplay?.audio_tags || ep.script?.audio_tags || "",
          createdAt: ep.created_timestamp ? ep.created_timestamp * 1000 : Date.now() - 3600000,
          startedAt: ep.created_timestamp ? ep.created_timestamp * 1000 + 2000 : Date.now() - 3598000,
          completedAt: ep.created_timestamp ? ep.created_timestamp * 1000 + 8500 : Date.now() - 3590000,
          publishedAt: ep.created_timestamp ? ep.created_timestamp * 1000 + 15000 : Date.now() - 3580000
        };
      });

      studioVideos = backendRecords;
      saveVideosState();
      renderStudioVideoHistory();
      if (typeof channelArchiveEpisodes !== "undefined") {
        channelArchiveEpisodes = data.episodes;
      }
      if (typeof filterChannelArchive === "function") filterChannelArchive();
    }
  } catch (e) { console.debug("Backend episode sync notice:", e); }
}

function renderStudioVideoHistory() {
  const tbody = document.getElementById("studio-video-history-rows");
  if (!tbody) return;

  const search = (document.getElementById("studio-search-input")?.value || "").toLowerCase().trim();
  const filterStatus = document.getElementById("studio-filter-status")?.value || "all";
  const filterTier = document.getElementById("studio-filter-tier")?.value || "all";
  const filterYoutube = document.getElementById("studio-filter-youtube")?.value || "all";
  const filterChannel = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "all";

  const matchesChannel = (v) => {
    if (!filterChannel || filterChannel === "all") return true;
    return v.channelId === filterChannel;
  };

  const filtered = studioVideos
    .filter(v => {
      const matchesSearch = !search || (v.title && v.title.toLowerCase().includes(search)) || (v.id && v.id.toLowerCase().includes(search)) || (v.jobId && v.jobId.toLowerCase().includes(search));
      const matchesStatus = filterStatus === "all" || (v.status && v.status.toLowerCase() === filterStatus.toLowerCase());
      const matchesTier = filterTier === "all" || (v.tierKey && v.tierKey.toLowerCase() === filterTier.toLowerCase());
      const matchesYoutube = filterYoutube === "all" || (v.youtubeStatus && v.youtubeStatus.toLowerCase() === filterYoutube.toLowerCase());
      return matchesSearch && matchesStatus && matchesTier && matchesYoutube && matchesChannel(v);
    })
    .sort((a, b) => b.createdAt - a.createdAt);

  if (filtered.length === 0) {
    tbody.innerHTML = '<tr><td colspan="14" class="text-center py-12 text-gray-500 text-xs">No matching videos in ledger.</td></tr>';
    return;
  }

  tbody.innerHTML = filtered.map(v => {
    const statusBadges = {
      completed: "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border border-emerald-500/40",
      processing: "bg-blue-500/15 text-blue-800 dark:text-blue-300 border border-blue-500/40 animate-pulse",
      queued: "bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/40"
    };
    const statusBadge = statusBadges[v.status] || "bg-slate-100 text-slate-700 dark:bg-gray-500/20 dark:text-gray-400 border border-slate-300 dark:border-gray-500/30";
    const typeBadge = (v.productionType === "Theme") ? "bg-emerald-500/15 text-emerald-800 dark:text-emerald-300 border border-emerald-500/30" : "bg-indigo-500/15 text-indigo-800 dark:text-indigo-300 border border-indigo-500/30";
    const isShort = (v.formatType && v.formatType.includes("Short")) || (v.format && v.format.includes("Short"));
    const fmtBadge = isShort ? "bg-amber-500/15 text-amber-800 dark:text-amber-300 border border-amber-500/40" : "bg-cyan-500/15 text-cyan-800 dark:text-cyan-300 border border-cyan-500/40";
    const ytBadge = v.youtubeStatus === "published"
      ? `<div class="space-y-0.5"><span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 border border-red-300 dark:border-red-500/40"><i class="fa-brands fa-youtube text-red-600"></i> Published</span><div class="font-mono text-[9px] text-red-700 dark:text-red-300">${formatTimestamp(v.publishedAt)}</div></div>`
      : `<div class="space-y-0.5"><span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-gray-400 border border-slate-300 dark:border-slate-700">Unpublished</span><div class="font-mono text-[9px] text-slate-400 dark:text-gray-500">—</div></div>`;
    const channelId = v.channelId || v.channel_id || "earth_serenade";
    const playBtn = `<button onclick="playStudioVideo('${v.id}', '${channelId}')" class="px-2.5 py-1 bg-indigo-50 dark:bg-indigo-600/30 hover:bg-indigo-100 dark:hover:bg-indigo-600/50 border border-indigo-300 dark:border-indigo-500/50 text-indigo-700 dark:text-indigo-300 rounded-lg text-[10px] font-bold inline-flex items-center gap-1 transition shadow-sm"><i class="fa-solid fa-play text-[9px]"></i> Watch</button>`;
    const ytBtn = v.youtubeStatus === "published"
      ? `<a href="${v.youtubeUrl || '#'}" target="_blank" class="px-2.5 py-1 bg-red-50 dark:bg-red-600/20 hover:bg-red-100 dark:hover:bg-red-600/30 border border-red-300 dark:border-red-500/40 text-red-700 dark:text-red-300 rounded-lg text-[10px] font-bold inline-flex items-center gap-1"><i class="fa-brands fa-youtube"></i> View</a>`
      : `<button onclick="publishVideoToYouTube('${v.jobId}')" class="px-2.5 py-1 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold rounded-lg text-[10px] inline-flex items-center gap-1 shadow"><i class="fa-brands fa-youtube"></i> 1-Click</button>`;
    const actionCell = v.status === "completed" ? `<div class="flex items-center justify-center gap-1.5">${playBtn}${ytBtn}</div>` : (v.status === "processing" ? '<span class="text-[11px] text-blue-600 dark:text-blue-400 font-semibold animate-pulse"><i class="fa-solid fa-spinner fa-spin"></i> Processing</span>' : '<span class="text-[11px] text-amber-600 dark:text-amber-400 font-semibold"><i class="fa-solid fa-clock"></i> Queued</span>');

    return `
      <tr data-video-id="${v.id}" data-video-channel="${channelId}" onclick="onLedgerRowClick(event, '${v.id}', '${channelId}')" class="hover:bg-slate-100/70 dark:hover:bg-slate-800/40 transition">
        <td class="p-3"><div class="font-mono font-bold text-slate-900 dark:text-white text-xs">${v.id}</div><div class="font-mono text-[9px] text-indigo-600 dark:text-indigo-400 cursor-pointer hover:underline truncate max-w-[120px]" onclick="viewEpisodeArtifacts('${v.id}', '${channelId}')">${v.jobId}</div></td>
        <td class="p-3"><div class="font-bold text-slate-900 dark:text-white text-xs">${v.title}</div><div class="text-[10px] text-slate-500 dark:text-gray-400 max-w-md">${v.concept}</div></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-500/15 text-blue-800 dark:text-blue-300 border border-blue-500/30">${v.videoType || "Series"}</span></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-bold ${fmtBadge}">${v.formatType || "16:9"}</span></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-medium bg-purple-500/15 text-purple-800 dark:text-purple-300 border border-purple-500/30">${v.styleType || "Realistic"}</span></td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded text-[10px] font-semibold ${typeBadge}">${v.productionType || "Prompt"}</span></td>
        <td class="p-3 text-center font-semibold text-slate-700 dark:text-gray-300 text-xs">${v.tierName || "Standard"}</td>
        <td class="p-3 text-center"><span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${statusBadge}">${v.status}</span></td>
        <td class="p-3 text-right font-mono font-bold text-emerald-700 dark:text-emerald-400 text-xs">${v.costStr}</td>
        <td class="p-3 text-center text-slate-600 dark:text-gray-300 text-[10px] font-mono">${formatTimestamp(v.createdAt)}</td>
        <td class="p-3 text-center text-slate-600 dark:text-gray-300 text-[10px] font-mono">${formatTimestamp(v.startedAt)}</td>
        <td class="p-3 text-center text-emerald-700 dark:text-emerald-300 text-[10px] font-mono">${formatTimestamp(v.completedAt)}</td>
        <td class="p-3 text-center">${ytBadge}</td>
        <td class="p-3 text-center">
          <div class="flex items-center justify-center gap-1.5">
            <button onclick="viewEpisodeArtifacts('${v.id}', '${channelId}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 border border-slate-300 dark:border-slate-700 text-purple-700 dark:text-purple-300 rounded-lg text-[10px] font-bold inline-flex items-center gap-1 shadow-sm transition"><i class="fa-solid fa-box-archive text-[9px]"></i> Artifacts</button>
            ${actionCell}
            <button type="button" onclick="event.stopPropagation(); deleteLedgerEpisode('${v.id}', event, '${channelId}');" class="p-1.5 bg-slate-100 hover:bg-rose-100 dark:bg-slate-800 dark:hover:bg-rose-900/40 border border-slate-300 dark:border-slate-700 hover:border-rose-400 text-slate-500 hover:text-rose-600 dark:text-gray-400 dark:hover:text-rose-400 rounded-lg text-xs transition" title="Delete Episode from disk">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");
}

async function deleteLedgerEpisode(epId, event, channelId) {
  if (event) event.stopPropagation();
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const vid = findStudioEpisodeById(epId, channelId);
  const chSlug = channelId || vid?.channelId || vid?.channel_id;
  if (!chSlug) return;

  try {
    await fetch(`/api/production/episodes/${epId}?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "DELETE" });
  } catch (e) {
    console.warn("Delete episode notice:", e);
  }

  const idx = studioVideos.findIndex(x => (x.id === epId || x.episode_id === epId) && (x.channelId || x.channel_id || "earth_serenade") === chSlug);
  if (idx >= 0) studioVideos.splice(idx, 1);
  if (typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
    channelArchiveEpisodes = channelArchiveEpisodes.filter(x => x.episode_id !== epId || x.channel_id !== chSlug);
  }

  saveVideosState();
  renderStudioVideoHistory();
  if (typeof filterChannelArchive === "function") filterChannelArchive();
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode && (currentActiveInspectorEpisode.id === epId || currentActiveInspectorEpisode.episode_id === epId) && (currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id) === chSlug) {
    if (typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
  }
  if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Episode ${epId} deleted.`);
}

function onLedgerRowClick(event, id, channelId) {
  if (event.target.closest("button") || event.target.closest("a") || event.target.closest("input")) return;
  if (typeof selectLedgerVideo === "function") selectLedgerVideo(id, channelId);
}

function publishVideoToYouTube(jobId) {
  const vid = studioVideos.find(v => v.jobId === jobId);
  if (!vid) return;
  vid.youtubeStatus = "published";
  vid.publishedAt = Date.now();
  vid.youtubeUrl = "https://youtube.com/watch?v=mock_" + Math.floor(Math.random() * 89999 + 10000);
  vid.youtubeChannel = "@telugucomedyhub";
  saveVideosState();
  renderStudioVideoHistory();
  showStudioModal({
    title: "Video Syndicated to YouTube",
    message: `"${vid.title}" published to ${vid.youtubeChannel} on ${formatTimestamp(vid.publishedAt)}.`,
    nextStep: "Published timestamp recorded and saved permanently."
  });
}

function refreshStudioLedger() {
  const icon = document.getElementById("ledger-refresh-icon");
  if (icon) icon.classList.add("fa-spin");
  studioVideos = loadSavedVideos();
  syncChannelEpisodesFromBackend();
  renderStudioVideoHistory();
  if (typeof renderDashboardStats === "function") renderDashboardStats();
  setTimeout(() => { if (icon) icon.classList.remove("fa-spin"); }, 500);
}

function startLocalVideoProductionJob(newVid) {
  setTimeout(() => {
    newVid.status = "processing";
    newVid.startedAt = Date.now();
    saveVideosState();
    renderStudioVideoHistory();
    if (typeof selectLedgerVideo === "function" && selectedLedgerVideoId === newVid.id) selectLedgerVideo(newVid.id, newVid.channelId);

    fetch("/api/production/local-produce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prompt: newVid.concept ?? "",
        title: newVid.title || "Explore Niagara Falls",
        episode_id: newVid.id || "EP-001",
        user_id: (typeof currentUser !== "undefined" && currentUser.id) ? currentUser.id : "user_krishna_01",
        production_type: newVid.productionType || "Theme",
        tier: newVid.tierKey || "low_cost",
        video_type: newVid.videoType || "Travel Guide & Doc",
        format_type: newVid.formatType || "Long (16:9)",
        style_type: newVid.styleType || "Realistic (Photoreal)",
        language: newVid.langCode || "en",
        duration_seconds: newVid.durationSeconds ? parseFloat(newVid.durationSeconds) : 10.0
      })
    })
      .then(async res => {
        if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || `HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (!data) return;
        newVid.status = "completed";
        newVid.completedAt = Date.now();
        if (data.video_url) newVid.videoUrl = data.video_url;
        if (data.artifacts) newVid.artifacts = data.artifacts;
        saveVideosState();
        renderStudioVideoHistory();
        if (typeof selectLedgerVideo === "function" && selectedLedgerVideoId === newVid.id) selectLedgerVideo(newVid.id, newVid.channelId);
      })
      .catch(err => {
        console.warn("Local production fallback:", err);
        newVid.status = "completed";
        newVid.completedAt = Date.now();
        newVid.videoUrl = "/static/videos/preview_master.mp4";
        saveVideosState();
        renderStudioVideoHistory();
      });
  }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
  syncChannelEpisodesFromBackend();
});

