// CineAI Studio: Channel Video Production Hub Controller (Rowspan, Pure Black Links, No Capsules)
let allChannelEpisodes = [];
let currentHubChannel = "all";
let currentInspectingEpisode = null;

async function fetchChannelHubVideos() {
  const icon = document.getElementById("channel-hub-refresh-icon");
  if (icon) icon.classList.add("fa-spin");
  try {
    const url = currentHubChannel === "all" ? "/api/channels/episodes" : `/api/channels/episodes?channel_id=${currentHubChannel}`;
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === "ok") {
      allChannelEpisodes = data.episodes || [];
      updateChannelHubCounts();
      renderChannelHubTable();
    }
  } catch (err) {
    console.error("Error fetching channel episodes:", err);
  } finally {
    if (icon) icon.classList.remove("fa-spin");
  }
}

function updateChannelHubCounts() {
  const counts = { all: allChannelEpisodes.length, earth_serenade: 0, silent_hearth: 0, telugu_comedy: 0, cineai_docs: 0 };
  allChannelEpisodes.forEach(ep => { if (counts[ep.channel_id] !== undefined) counts[ep.channel_id]++; });
  Object.keys(counts).forEach(k => {
    const el = document.getElementById("stat-count-" + k);
    if (el) el.textContent = counts[k];
  });
}

function selectHubChannel(chId) {
  currentHubChannel = chId;
  ["all", "earth_serenade", "silent_hearth", "telugu_comedy", "cineai_docs"].forEach(k => {
    const card = document.getElementById("hub-channel-card-" + k);
    if (!card) return;
    card.className = (k === chId)
      ? "p-2 bg-indigo-950/40 border-2 border-indigo-500 rounded-xl cursor-pointer transition ring-1 ring-indigo-500/40 space-y-1"
      : "p-2 bg-[var(--card)] border border-[var(--border)] hover:border-indigo-500/60 rounded-xl cursor-pointer transition space-y-1";
  });
  filterChannelHubVideos();
}

function filterChannelHubVideos() {
  const query = (document.getElementById("channel-hub-search")?.value || "").toLowerCase().trim();
  const statusFilter = document.getElementById("channel-hub-filter-status")?.value || "all";
  const audioFilter = document.getElementById("channel-hub-filter-audio")?.value || "all";
  const formatFilter = document.getElementById("channel-hub-filter-format")?.value || "all";

  const filtered = allChannelEpisodes.filter(ep => {
    if (currentHubChannel !== "all" && ep.channel_id !== currentHubChannel) return false;
    if (statusFilter !== "all" && ep.editions?.every(ed => ed.status !== statusFilter)) return false;
    if (audioFilter === "music" && ep.editions?.every(ed => !ed.audio_mode.includes("Music"))) return false;
    if (audioFilter === "nature" && ep.editions?.every(ed => !ed.audio_mode.includes("Pure Nature"))) return false;
    if (formatFilter === "long" && ep.editions?.every(ed => !ed.format.includes("Long-Play"))) return false;
    if (formatFilter === "short" && ep.editions?.every(ed => !ed.format.includes("Short"))) return false;
    if (query) {
      const match = [ep.title, ep.story_topic, ep.episode_id, ep.channel_handle, JSON.stringify(ep.models_used)].some(
        s => (s || "").toLowerCase().includes(query)
      );
      if (!match) return false;
    }
    return true;
  });

  renderChannelHubTable(filtered);
}

function renderChannelHubTable(episodes = allChannelEpisodes) {
  const tbody = document.getElementById("channel-hub-tbody");
  if (!tbody) return;

  if (episodes.length === 0) {
    tbody.innerHTML = `<tr><td colspan="13" class="p-6 text-center text-black dark:text-gray-400 text-xs font-medium">No episodes found matching selected filters.</td></tr>`;
    return;
  }

  const rowsHtml = [];
  episodes.forEach((ep, epIdx) => {
    const editions = (ep.editions && ep.editions.length > 0) ? ep.editions : [
      { edition_id: "default", name: "4K Master Video", icon: "fa-film text-indigo-500", audio_mode: "Music Master", duration: "90s", format: "16:9 Master", status: "completed", url: ep.artifacts?.master_music || "" }
    ];
    const spanCount = editions.length;

    const stagePill = (ok, label) => ok
      ? `<span class="px-1 py-0.2 bg-emerald-100 dark:bg-emerald-950/80 text-emerald-950 dark:text-emerald-300 border border-emerald-400 dark:border-emerald-500/40 rounded text-[8px] font-mono font-bold">✓ ${label}</span>`
      : `<span class="px-1 py-0.2 bg-slate-100 dark:bg-slate-900 text-slate-700 dark:text-gray-500 border border-slate-300 dark:border-slate-800 rounded text-[8px] font-mono">○ ${label}</span>`;

    const stagesHtml = `
      <div class="flex items-center gap-0.5 justify-center flex-wrap">
        ${stagePill(ep.stages?.stage_1_keyframes, "S1:Key")}
        ${stagePill(ep.stages?.stage_2_cineloop_masters, "S2:60s")}
        ${stagePill(ep.stages?.stage_3_crf22_compression, "S3:CRF")}
        ${stagePill(ep.stages?.stage_4_long_play_stretch, "S4:Str")}
      </div>
    `;

    const modelsHtml = `
      <div class="flex flex-col gap-0 text-[9px] text-black dark:text-gray-300 leading-tight">
        <span class="font-mono font-bold text-indigo-900 dark:text-indigo-300">🧠 ${ep.models_used?.scripting || 'Gemini'}</span>
        <span class="font-mono font-bold text-purple-900 dark:text-purple-300">🎨 ${ep.models_used?.visuals?.split(' ')[0] || 'FLUX'} + 🎬 ${ep.models_used?.motion?.split(' ')[0] || 'Kling'}</span>
      </div>
    `;

    const epBg = epIdx % 2 === 0 ? "bg-slate-50/70 dark:bg-slate-900/10" : "bg-white dark:bg-slate-800/10";

    editions.forEach((ed, edIdx) => {
      const isFirst = edIdx === 0;
      const isLast = edIdx === spanCount - 1;
      const rowBorder = isLast ? "border-b-2 border-indigo-400 dark:border-indigo-500/40" : "border-b border-slate-200 dark:border-slate-800/40";

      const statusBadges = {
        published: `<span class="px-1.5 py-0.2 bg-emerald-100 dark:bg-emerald-500/20 text-emerald-950 dark:text-emerald-400 border border-emerald-400 dark:border-emerald-500/30 rounded font-bold text-[9px]">Published</span>`,
        completed: `<span class="px-1.5 py-0.2 bg-blue-100 dark:bg-blue-500/20 text-blue-950 dark:text-blue-400 border border-blue-400 dark:border-blue-500/30 rounded font-bold text-[9px]">Ready</span>`,
        pending_review: `<span class="px-1.5 py-0.2 bg-amber-100 dark:bg-amber-500/20 text-amber-950 dark:text-amber-400 border border-amber-400 dark:border-amber-500/30 rounded font-bold text-[9px]">Review</span>`,
        processing: `<span class="px-1.5 py-0.2 bg-indigo-100 dark:bg-indigo-500/20 text-indigo-950 dark:text-indigo-400 border border-indigo-400 dark:border-indigo-500/30 rounded font-bold text-[9px] animate-pulse">Running</span>`,
        queued: `<span class="px-1.5 py-0.2 bg-blue-100 dark:bg-blue-500/20 text-blue-950 dark:text-blue-400 border border-blue-400 dark:border-blue-500/30 rounded font-bold text-[9px]">Queued</span>`,
        not_started: `<span class="px-1.5 py-0.2 bg-gray-100 dark:bg-gray-500/20 text-gray-950 dark:text-gray-400 border border-gray-400 dark:border-gray-500/30 rounded font-bold text-[9px]">Draft</span>`
      };
      const sBadge = statusBadges[ed.status] || statusBadges.completed;

      let rowHtml = `<tr class="hover:bg-indigo-50/70 dark:hover:bg-indigo-950/20 transition ${rowBorder} ${epBg}">`;

      if (isFirst) {
        rowHtml += `
          <!-- 1. Channel (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2.5 py-2 align-middle border-r border-slate-200 dark:border-[var(--border)]">
            <div class="text-[11px] font-bold text-black dark:text-white flex items-center gap-1.5">
              <i class="fa-solid ${ep.channel_icon} text-${ep.channel_color}-600 dark:text-${ep.channel_color}-400 text-[10px]"></i>
              <span>${ep.channel_name}</span>
            </div>
            <div class="text-[9px] text-black dark:text-gray-400 font-mono font-medium mt-0.5">${ep.channel_handle}</div>
          </td>

          <!-- 2. Episode ID (Centered Rowspan, No Capsule, Pure Bold Black Text) -->
          <td rowspan="${spanCount}" class="px-2.5 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]">
            <div class="font-mono font-bold text-black dark:text-indigo-300 text-[11px] select-all whitespace-nowrap">${ep.episode_id}</div>
          </td>
        `;
      }

      // 3. Video Edition Column (Distinct per row)
      rowHtml += `
        <td class="px-2.5 py-1.5">
          <div class="flex items-center gap-1.5">
            <i class="fa-solid ${ed.icon} text-[11px]"></i>
            <span class="font-bold text-black dark:text-white text-[11px]">${ed.name}</span>
          </div>
          <div class="text-[9px] text-slate-800 dark:text-gray-400 font-mono font-medium mt-0.5">${ed.format} • ${ed.size_str || ''}</div>
        </td>
      `;

      if (isFirst) {
        rowHtml += `
          <!-- 4. Title (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2.5 py-2 align-middle max-w-[170px] border-r border-slate-200 dark:border-[var(--border)]">
            <div class="font-bold text-black dark:text-white text-[11px] leading-tight" title="${ep.title}">${ep.title}</div>
            <div class="text-[9px] text-slate-800 dark:text-gray-400 mt-0.5 font-medium">${ep.category}</div>
          </td>

          <!-- 5. Story Topic (Centered Rowspan, Clean Hyperlink Popup, Pure Black Text) -->
          <td rowspan="${spanCount}" class="px-2.5 py-2 align-middle max-w-[190px] border-r border-slate-200 dark:border-[var(--border)]">
            <a href="javascript:void(0)" onclick="openScriptModal('${ep.episode_id}')" class="text-black dark:text-sky-300 hover:text-indigo-600 dark:hover:text-indigo-400 font-bold text-[11px] underline underline-offset-2 decoration-slate-900 dark:decoration-sky-400 hover:decoration-indigo-600 transition flex items-start gap-1 leading-snug cursor-pointer group" title="Click to open popup screenplay & story script">
              <i class="fa-solid fa-scroll text-indigo-700 dark:text-indigo-400 text-[10px] mt-0.5 shrink-0 group-hover:scale-110 transition-transform"></i>
              <span class="line-clamp-2">${ep.story_topic}</span>
            </a>
          </td>
        `;
      }

      // 6. Status, 7. Audio Mode, 8. Duration (Distinct per row)
      rowHtml += `
        <td class="px-2 py-1.5 text-center">${sBadge}</td>
        <td class="px-2 py-1.5 text-center">
          <span class="px-1.5 py-0.2 bg-slate-100 dark:bg-slate-900 border border-slate-300 dark:border-slate-700/60 rounded text-[9px] font-bold text-black dark:text-gray-300">${ed.audio_mode}</span>
        </td>
        <td class="px-2 py-1.5 text-center font-mono font-bold text-black dark:text-white text-[11px] whitespace-nowrap">${ed.duration}</td>
      `;

      if (isFirst) {
        rowHtml += `
          <!-- 9. Cost (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2.5 py-2 align-middle text-right font-mono font-bold text-emerald-800 dark:text-emerald-400 text-[11px] border-r border-slate-200 dark:border-[var(--border)] whitespace-nowrap" title="Click inspector to view itemized stage/model spend">
            $${ep.cost_usd.toFixed(2)}
          </td>

          <!-- 10. Stages Built (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]">
            ${stagesHtml}
          </td>

          <!-- 11. Models Used (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center border-r border-slate-200 dark:border-[var(--border)]">
            ${modelsHtml}
          </td>

          <!-- 12. Timestamps (Centered Rowspan) -->
          <td rowspan="${spanCount}" class="px-2 py-2 align-middle text-center font-mono text-[9px] text-black dark:text-gray-400 font-medium leading-tight border-r border-slate-200 dark:border-[var(--border)] whitespace-nowrap">
            <div>${ep.created_at}</div>
            <div class="text-[8px] text-slate-800 dark:text-gray-500">Upd: ${ep.updated_at}</div>
          </td>
        `;
      }

      // 13. Actions (Distinct per row)
      rowHtml += `
        <td class="px-2 py-1.5 text-center">
          <div class="flex items-center gap-1 justify-center">
            <button onclick="playEditionVideo('${ed.url}', '${ep.episode_id}', '${ed.name}')" class="p-1 bg-indigo-600 hover:bg-indigo-500 text-white rounded text-[10px]" title="Play this edition">
              <i class="fa-solid fa-play text-[9px]"></i>
            </button>
            <button onclick="openScriptModal('${ep.episode_id}')" class="p-1 bg-purple-600 hover:bg-purple-500 text-white rounded text-[10px]" title="View Script">
              <i class="fa-solid fa-scroll text-[9px]"></i>
            </button>
            <button onclick="openChannelEpisodeInspector('${ep.episode_id}'); switchInspectorTab('youtube');" class="p-1 bg-red-600 hover:bg-red-500 text-white rounded text-[10px]" title="YouTube Info">
              <i class="fa-brands fa-youtube text-[9px]"></i>
            </button>
          </div>
        </td>
      </tr>`;

      rowsHtml.push(rowHtml);
    });
  });

  tbody.innerHTML = rowsHtml.join("");
}

document.addEventListener("DOMContentLoaded", () => {
  fetchChannelHubVideos();
});
