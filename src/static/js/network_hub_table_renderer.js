// CineAI Studio: Audience Networks Strategy & Metadata Table Renderer
let cachedNetworkProfiles = {};
let cachedChannelProfiles = {}; // backward compatibility alias

async function fetchAndCacheNetworkProfiles() {
  try {
    const res = await fetch("/api/channels/profiles");
    const data = await res.json();
    if (data.status === "ok" && data.profiles) {
      cachedNetworkProfiles = data.profiles;
      cachedChannelProfiles = data.profiles;
    }
  } catch (err) {
    console.error("Error fetching network profiles:", err);
  }
}
const fetchAndCacheChannelProfiles = fetchAndCacheNetworkProfiles;

function filterNetworkManagementTable() {
  const query = (document.getElementById("channel-table-search")?.value || "").toLowerCase().trim();
  const filtered = userChannels.filter(ch => {
    if (!query) return true;
    const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    const prof = cachedNetworkProfiles[slug] || {};
    const genres = (prof.allowed_genres || []).join(" ");
    const formats = (prof.allowed_formats || ch.allowed_formats || []).join(" ");
    const tags = (ch.default_tags || []).join(" ");
    const searchString = `${ch.channel_name} ${ch.channel_handle} ${ch.tag} ${ch.category} ${ch.description} ${ch.comments} ${genres} ${formats} ${tags}`.toLowerCase();
    return searchString.includes(query);
  });
  renderNetworkHubTable(filtered);
}
const filterChannelManagementTable = filterNetworkManagementTable;

const NETWORK_GENRE_LABELS = {
  "relax/ocean": "🏖️ Ocean",
  "relax/beach_lounge": "🏖️ Beach Lounge",
  "relax/desert": "🏜️ Desert",
  "relax/mountain": "🏔️ Mountain",
  "relax/valley": "🌸 Valley",
  "relax/blizzard": "❄️ Blizzard",
  "relax/rain": "🌧️ Rain",
  "relax/forest": "🌲 Forest",
  "relax/nature": "🏔️ Nature",
  "relax/healing": "✨ 528Hz",
  "relax/zen": "🪷 Zen",
  "relax/waterfall": "🌊 Waterfall",
  "relax/hearth": "🔥 Hearth",
  "relax/cozy": "🪵 Cozy",
  "relax/ambient": "🌌 Ambient",
  "documentary": "🦅 Wildlife",
  "travel/scenic": "✈️ Travel & Nature",
  "relax/scenic": "✈️ Travel & Nature",
  "relax/art": "🎨 Living Art",
  "travel_walking": "🚶 Walking",
  "dance/folk": "💃 Folk Dance",
  "music/mass_song": "🥁 Mass Song",
  "music/static_vocal": "🎤 Static Vocal",
  "music/solo_singer": "🎸 Solo Singer",
  "music/duet_romance": "💑 Duet Romance",
  "music/concert_live": "🎆 Concert Live",
  "comedy/satire": "🎭 Comedy"
};
const GENRE_LABELS = NETWORK_GENRE_LABELS;

function renderNetworkHubTable(networks = userChannels) {
  const tbody = document.getElementById("channel-hub-tbody");
  const countEl = document.getElementById("channel-table-count");
  if (countEl) countEl.textContent = `${networks.length} network${networks.length === 1 ? '' : 's'} configured`;
  if (!tbody) return;

  if (networks.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" class="p-8 text-center text-gray-400 text-xs font-medium">No audience networks found. Click "+ Create Network" above to configure your first audience brand.</td></tr>`;
    return;
  }

  const rowsHtml = networks.map((ch, idx) => {
    const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    const prof = cachedNetworkProfiles[slug] || {};
    const allowedGenres = prof.allowed_genres || [ch.primary_genre || "relax/nature"];
    const allowedFormats = prof.allowed_formats || ch.allowed_formats || ["ambient_soundscape", "ultra_slow_walk"];
    const epCount = allChannelEpisodes.filter(e => e.channel_id === slug).length;
    const isStudioActive = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel === slug);

    // Genre badges
    const genreBadges = allowedGenres.map(g => {
      const label = NETWORK_GENRE_LABELS[g] || g;
      return `<span class="px-1.5 py-0.5 rounded bg-[var(--card-subtle)] border border-[var(--border)] text-[var(--text-muted)] font-mono text-[9px] whitespace-nowrap">${label}</span>`;
    }).join(" ");

    // Formats badges
    const formatBadges = allowedFormats.slice(0, 3).map(fmt => {
      const cleanFmt = fmt.replace(/_/g, " ");
      return `<span class="px-1.5 py-0.2 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 font-mono text-[8px] whitespace-nowrap uppercase">${cleanFmt}</span>`;
    }).join(" ");

    // Audio policy string
    const audioStyle = prof.audio_profile?.style || (ch.channel_slug?.includes("hearth") ? "Pure ASMR" : "Harmonic Soundscape");
    const bgmOn = prof.audio_profile?.bgm_enabled_by_default ?? (!slug.includes("hearth"));
    const lufs = prof.audio_profile?.target_lufs ?? -14.0;
    const audioBadge = `<div class="space-y-0.5"><div class="font-bold text-[var(--text)] text-[10px] flex items-center gap-1"><span class="w-1.5 h-1.5 rounded-full ${bgmOn ? 'bg-emerald-500' : 'bg-amber-500'}"></span><span>${audioStyle}</span></div><div class="text-[9px] text-[var(--text-muted)] font-mono">${bgmOn ? 'BGM ON' : 'Pure ASMR'} • ${lufs} LUFS</div></div>`;

    // Lighting & Purity
    const lighting = prof.visual_lighting_guardrails?.lighting_temperature || "Natural Daylight (5400K)";
    const purity = prof.visual_lighting_guardrails?.purity_rule || "Pure pristine nature";
    const visualInfo = `<div class="space-y-0.5 max-w-[160px]"><div class="font-bold text-[var(--text)] text-[10px] truncate" title="${lighting}">💡 ${lighting}</div><div class="text-[9px] text-[var(--text-muted)] truncate" title="${purity}">🛡️ ${purity}</div></div>`;

    // Tag badge
    const tagBadge = ch.tag ? `<span class="px-2 py-0.5 rounded-lg bg-[var(--card-subtle)] border border-[var(--border)] text-[var(--text)] font-bold font-mono text-[10px] whitespace-nowrap shadow-sm">${ch.tag}</span>` : `<span class="text-[10px] text-[var(--text-muted)] italic">—</span>`;

    // Comments
    const commentsText = ch.comments ? `<div class="text-[10px] text-[var(--text-muted)] line-clamp-2 max-w-[180px]" title="${ch.comments}"><i class="fa-solid fa-comment-dots text-[var(--accent)] text-[9px] mr-1"></i>${ch.comments}</div>` : `<span class="text-[10px] text-[var(--text-muted)] italic">—</span>`;

    return `
      <tr class="hover:bg-[var(--card-hover)] transition border-b border-[var(--border)]">
        <td class="px-3 py-2.5 align-middle">
          <div class="flex items-center gap-2">
            <div class="w-7 h-7 rounded-lg bg-[var(--card-subtle)] text-[var(--text)] flex items-center justify-center text-xs shrink-0 border border-[var(--border)]">
              <i class="fa-solid ${ch.icon || 'fa-tower-broadcast'}"></i>
            </div>
            <div>
              <div class="font-bold text-[var(--text)] text-xs flex items-center gap-1.5">
                <span>${ch.channel_name}</span>
                ${isStudioActive ? '<span class="px-1.5 py-0.2 rounded bg-[var(--accent)] text-white text-[8px] font-bold">Active</span>' : ''}
              </div>
              <div class="text-[10px] text-[var(--text-muted)] font-mono">${ch.channel_handle || '@' + slug}</div>
            </div>
          </div>
        </td>
        <td class="px-3 py-2.5 align-middle">${tagBadge}</td>
        <td class="px-3 py-2.5 align-middle max-w-[150px]">
          <div class="font-bold text-[var(--text)] text-[10px]">${ch.category || 'Audience Brand'}</div>
          <div class="text-[9px] text-[var(--text-muted)] line-clamp-1 mt-0.5" title="${ch.description || ''}">${ch.description || 'Target Audience'}</div>
          <div class="flex items-center gap-1 flex-wrap mt-1">${formatBadges}</div>
        </td>
        <td class="px-3 py-2.5 align-middle max-w-[180px]">
          <div class="flex items-center gap-1 flex-wrap">${genreBadges}</div>
        </td>
        <td class="px-3 py-2.5 align-middle">${audioBadge}</td>
        <td class="px-3 py-2.5 align-middle">${visualInfo}</td>
        <td class="px-3 py-2.5 align-middle">${commentsText}</td>
        <td class="px-2.5 py-2.5 align-middle text-center font-mono font-bold text-[var(--text)] text-xs">${epCount}</td>
        <td class="px-3 py-2.5 align-middle text-center">
          <div class="flex items-center justify-center gap-1">
            <button onclick="openYouTubeCredentialsModal('${slug}', '${ch.channel_name}')" class="px-2 py-1 bg-red-600/10 hover:bg-red-600/20 text-red-500 rounded-lg text-[10px] font-bold flex items-center gap-1 transition shadow-sm border border-red-500/20" title="Distribution Outlets (YouTube / Social OAuth)">
              <i class="fa-brands fa-youtube text-[9px]"></i>
              <span>Outlets</span>
            </button>
            <button onclick="openEditChannelModal('${ch.id}')" class="px-2 py-1 bg-[var(--card-subtle)] hover:bg-[var(--card-hover)] text-[var(--text)] rounded-lg text-[10px] font-semibold flex items-center gap-1 transition shadow-sm border border-[var(--border)]" title="Network Strategy & Guardrails">
              <i class="fa-solid fa-sliders text-[9px]"></i>
              <span>Details</span>
            </button>
            <button onclick="activateChannelFromHub('${slug}'); switchTab('studio');" class="px-2 py-1 bg-[var(--accent)] hover:opacity-90 text-white rounded-lg text-[10px] font-bold flex items-center gap-1 transition shadow-sm" title="Produce in Studio">
              <i class="fa-solid fa-wand-magic-sparkles text-[9px]"></i>
              <span>Studio</span>
            </button>
            <button onclick="deleteChannelConfirm('${ch.id}', '${ch.channel_name}')" class="p-1 text-[var(--text-muted)] hover:text-red-500 transition" title="Delete Network">
              <i class="fa-solid fa-trash-can text-[10px]"></i>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join("");

  tbody.innerHTML = rowsHtml;
}
const renderChannelHubTable = renderNetworkHubTable;
