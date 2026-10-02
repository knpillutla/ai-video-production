// CineAI Studio: Channel Management Shelf Renderer

function renderChannelManagementShelf() {
  const container = document.getElementById("channel-selector-cards");
  if (!container) return;

  if (userChannels.length === 0) {
    container.innerHTML = `
      <div onclick="openCreateChannelModal()" class="col-span-full p-4 bg-white hover:bg-slate-50 border-2 border-dashed border-indigo-300 hover:border-indigo-500 rounded-2xl cursor-pointer transition flex items-center justify-between gap-4 shadow-sm group">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 group-hover:scale-105 flex items-center justify-center text-base transition border border-indigo-100"><i class="fa-solid fa-tower-broadcast"></i></div>
          <div>
            <div class="text-xs font-bold text-slate-900 flex items-center gap-2"><span>No Channels Created Yet</span><span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-50 text-amber-800 border border-amber-300">Action Required</span></div>
            <p class="text-[11px] text-slate-600 font-medium mt-0.5">Click here to configure your YouTube channel with handle, niche, and isolated storage.</p>
          </div>
        </div>
        <button type="button" onclick="openCreateChannelModal()" class="px-3.5 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-xs flex items-center gap-1.5 shadow-sm transition shrink-0"><i class="fa-solid fa-plus text-[10px]"></i><span>Create Channel</span></button>
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
    <div onclick="selectHubChannel('all')" id="hub-channel-card-all" class="p-2.5 ${currentHubChannel === 'all' ? 'bg-indigo-950/40 border-2 border-indigo-500 ring-1 ring-indigo-500/40' : 'bg-[var(--card)] border border-[var(--border)] hover:border-indigo-500/60'} rounded-xl cursor-pointer transition space-y-1.5 shadow-sm">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-1.5"><div class="w-6 h-6 rounded-md bg-indigo-500/20 text-indigo-400 flex items-center justify-center text-xs"><i class="fa-solid fa-network-wired"></i></div><span class="font-bold text-white text-xs">All Channels</span></div>
        <span class="text-[10px] font-mono font-bold text-indigo-300 bg-indigo-900/60 px-1.5 py-0.5 rounded border border-indigo-500/30">${totalCount}</span>
      </div>
      <p class="text-[9px] text-gray-400 truncate">Network-wide overview across all series.</p>
    </div>
  `;

  const channelCards = userChannels.map(ch => {
    const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    const isSelected = currentHubChannel === slug;
    const isStudioActive = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel === slug);
    const cardBorder = isSelected
      ? "bg-indigo-950/40 border-2 border-indigo-500 ring-1 ring-indigo-500/40"
      : "bg-[var(--card)] border border-[var(--border)] hover:border-indigo-500/60";
    const epCount = counts[slug] || 0;
    const tagBadge = ch.tag ? `<span class="px-1.5 py-0.2 rounded bg-indigo-900/60 border border-indigo-500/40 text-indigo-300 text-[8px] font-bold font-mono truncate max-w-[140px]">${ch.tag}</span>` : '';

    return `
      <div onclick="selectHubChannel('${slug}')" id="hub-channel-card-${slug}" class="p-2.5 ${cardBorder} rounded-xl cursor-pointer transition space-y-2 relative group shadow-sm">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 min-w-0">
            <div class="w-6 h-6 rounded-md bg-${ch.color || 'indigo'}-500/20 text-${ch.color || 'indigo'}-400 flex items-center justify-center text-xs shrink-0"><i class="fa-solid ${ch.icon || 'fa-clapperboard'}"></i></div>
            <div class="min-w-0">
              <div class="font-bold text-white text-xs truncate flex items-center gap-1">
                <span>${ch.channel_name}</span>
              </div>
              <div class="text-[9px] text-gray-400 font-mono truncate">${ch.channel_handle || '@' + slug}</div>
            </div>
          </div>
          <span class="text-[10px] font-mono font-bold text-emerald-300 bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-500/30 shrink-0">${epCount}</span>
        </div>
        ${tagBadge ? `<div class="pt-0.5">${tagBadge}</div>` : ''}
        <div class="flex items-center justify-between pt-1 border-t border-[var(--border)]/60 text-[10px]">
          <span class="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-gray-300 font-medium">${ch.category || 'General'}</span>
          <div class="flex items-center gap-1" onclick="event.stopPropagation()">
            <button onclick="activateChannelFromHub('${slug}')" class="px-1.5 py-0.5 ${isStudioActive ? 'bg-indigo-600 text-white font-bold' : 'bg-slate-800 hover:bg-slate-700 text-gray-300'} rounded text-[9px] transition" title="Set as Active Studio Channel">${isStudioActive ? '✓ Active' : 'Activate'}</button>
            <button onclick="openEditChannelModal('${ch.id}')" class="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 hover:text-indigo-300 text-gray-300 rounded text-[9px] flex items-center gap-0.5 transition" title="Inspect & Edit Channel Strategy"><i class="fa-solid fa-sliders text-[9px]"></i><span>Details</span></button>
            <button onclick="deleteChannelConfirm('${ch.id}', '${ch.channel_name}')" class="p-1 hover:text-red-400 text-gray-400 transition" title="Delete"><i class="fa-solid fa-trash-can text-[10px]"></i></button>
          </div>
        </div>
      </div>
    `;
  }).join("");

  const addCard = `
    <div onclick="openCreateChannelModal()" class="p-2.5 bg-slate-900/30 hover:bg-slate-900/60 border-2 border-dashed border-slate-700 hover:border-indigo-500 rounded-xl cursor-pointer transition flex flex-col items-center justify-center text-center space-y-1 group shadow-sm min-h-[85px]">
      <div class="w-6 h-6 rounded-full bg-indigo-600/20 text-indigo-400 group-hover:scale-110 flex items-center justify-center text-xs transition"><i class="fa-solid fa-plus"></i></div>
      <span class="text-xs font-bold text-gray-300 group-hover:text-white transition">New Channel</span>
      <span class="text-[9px] text-gray-500">Add YouTube brand</span>
    </div>
  `;
  container.innerHTML = allCard + channelCards + addCard;
}
