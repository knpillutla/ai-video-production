// CineAI Studio: Channel Management Shelf Renderer

function renderChannelManagementShelf() {
  const container = document.getElementById("channel-selector-cards");
  if (!container) return;

  if (userChannels.length === 0) {
    container.innerHTML = `
      <div onclick="openCreateChannelModal()" class="col-span-full p-4 bg-[var(--card)] hover:bg-[var(--card-hover)] border-2 border-dashed border-[var(--border)] hover:border-[var(--accent)] rounded-2xl cursor-pointer transition flex items-center justify-between gap-4 shadow-sm group">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-[var(--card-subtle)] text-[var(--accent)] flex items-center justify-center text-base transition border border-[var(--border)]"><i class="fa-solid fa-tower-broadcast"></i></div>
          <div>
            <div class="text-xs font-bold text-[var(--text)] flex items-center gap-2"><span>No Channels Created Yet</span><span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/30">Action Required</span></div>
            <p class="text-[11px] text-[var(--text-muted)] mt-0.5">Click here to configure your YouTube channel with handle, niche, and isolated storage.</p>
          </div>
        </div>
        <button type="button" onclick="openCreateChannelModal()" class="px-3.5 py-1.5 bg-[var(--accent)] hover:opacity-90 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition shrink-0"><i class="fa-solid fa-plus text-[10px]"></i><span>Create Channel</span></button>
      </div>
    `;
    return;
  }

  const totalCount = allChannelEpisodes.length;
  const counts = { all: totalCount };
  userChannels.forEach(c => {
    const slug = c.channel_slug || c.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    counts[slug] = allChannelEpisodes.filter(e => e.channel_id === slug).length;
  });

  const allCard = `
    <div onclick="selectHubChannel('all')" id="hub-channel-card-all" class="p-2.5 ${currentHubChannel === 'all' ? 'bg-[var(--card)] border-2 border-[var(--accent)] ring-1 ring-[var(--accent)]/20' : 'bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--card-hover)]'} rounded-xl cursor-pointer transition space-y-1.5 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5"><div class="w-6 h-6 rounded-md bg-[var(--card-subtle)] text-[var(--text)] flex items-center justify-center text-xs"><i class="fa-solid fa-network-wired"></i></div><span class="font-bold text-[var(--text)] text-xs">All Channels</span></div>
        <span class="text-[10px] font-mono font-bold text-[var(--text-muted)] bg-[var(--card-subtle)] px-1.5 py-0.5 rounded border border-[var(--border)]">${totalCount}</span>
      </div>
      <p class="text-[9px] text-[var(--text-muted)] truncate">Network-wide overview across all series.</p>
    </div>
  `;

  const channelCards = userChannels.map(ch => {
    const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    const isSelected = currentHubChannel === slug;
    const isStudioActive = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel === slug);
    const cardBorder = isSelected
      ? "bg-[var(--card)] border-2 border-[var(--accent)] ring-1 ring-[var(--accent)]/20"
      : "bg-[var(--card)] border border-[var(--border)] hover:bg-[var(--card-hover)]";
    const epCount = counts[slug] || 0;
    const tagBadge = ch.tag ? `<span class="px-1.5 py-0.2 rounded bg-[var(--card-subtle)] border border-[var(--border)] text-[var(--text-muted)] text-[8px] font-bold font-mono truncate max-w-[140px]">${ch.tag}</span>` : '';

    return `
      <div onclick="selectHubChannel('${slug}')" id="hub-channel-card-${slug}" class="p-2.5 ${cardBorder} rounded-xl cursor-pointer transition space-y-2 relative group shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 min-w-0">
            <div class="w-6 h-6 rounded-md bg-[var(--card-subtle)] text-[var(--text)] flex items-center justify-center text-xs shrink-0"><i class="fa-solid ${ch.icon || 'fa-clapperboard'}"></i></div>
            <div class="min-w-0">
              <div class="font-bold text-[var(--text)] text-xs truncate flex items-center gap-1">
                <span>${ch.channel_name}</span>
              </div>
              <div class="text-[9px] text-[var(--text-muted)] font-mono truncate">${ch.channel_handle || '@' + slug}</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-[var(--text)] bg-[var(--card-subtle)] px-1.5 py-0.5 rounded border border-[var(--border)] shrink-0">${epCount}</span>
        </div>
        ${tagBadge ? `<div class="pt-0.5">${tagBadge}</div>` : ''}
        <div class="flex items-center justify-between pt-1 border-t border-[var(--border)] text-[10px]">
          <span class="text-[9px] px-1.5 py-0.2 rounded bg-[var(--card-subtle)] text-[var(--text-muted)] font-medium">${ch.category || 'General'}</span>
          <div class="flex items-center gap-1" onclick="event.stopPropagation()">
            <button onclick="activateChannelFromHub('${slug}')" class="px-1.5 py-0.5 ${isStudioActive ? 'bg-[var(--accent)] text-white font-bold' : 'bg-[var(--card-subtle)] hover:bg-[var(--card-hover)] text-[var(--text)]'} rounded text-[9px] transition" title="Set as Active Studio Channel">${isStudioActive ? '✓ Active' : 'Activate'}</button>
            <button onclick="openEditChannelModal('${ch.id}')" class="px-1.5 py-0.5 bg-[var(--card-subtle)] hover:bg-[var(--card-hover)] text-[var(--text)] rounded text-[9px] flex items-center gap-0.5 transition" title="Inspect & Edit Channel Strategy"><i class="fa-solid fa-sliders text-[9px]"></i><span>Details</span></button>
            <button onclick="deleteChannelConfirm('${ch.id}', '${ch.channel_name}')" class="p-1 hover:text-red-500 text-[var(--text-muted)] transition" title="Delete"><i class="fa-solid fa-trash-can text-[10px]"></i></button>
          </div>
        </div>
      </div>
    `;
  }).join("");

  const addCard = `
    <div onclick="openCreateChannelModal()" class="p-2.5 bg-[var(--card)] hover:bg-[var(--card-hover)] border-2 border-dashed border-[var(--border)] hover:border-[var(--accent)] rounded-xl cursor-pointer transition flex flex-col items-center justify-center text-center space-y-1 group shadow-sm min-h-[85px]">
      <div class="w-6 h-6 rounded-full bg-[var(--card-subtle)] text-[var(--accent)] flex items-center justify-center text-xs transition"><i class="fa-solid fa-plus"></i></div>
      <span class="text-xs font-bold text-[var(--text)] transition">New Channel</span>
      <span class="text-[9px] text-[var(--text-muted)]">Add YouTube brand</span>
    </div>
  `;
  container.innerHTML = allCard + channelCards + addCard;
}
