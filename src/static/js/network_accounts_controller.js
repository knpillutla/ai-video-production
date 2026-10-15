// CineAI Studio: Network Multi-YouTube Channel Accounts Manager
let currentCrudLinkedAccounts = [];
let isAddingNewYtAccount = false;

function initCrudYouTubeAccounts(ch) {
  isAddingNewYtAccount = false;
  if (ch && Array.isArray(ch.linked_youtube_channels) && ch.linked_youtube_channels.length > 0) {
    currentCrudLinkedAccounts = JSON.parse(JSON.stringify(ch.linked_youtube_channels));
  } else if (ch) {
    const slug = ch.channel_slug || (ch.channel_name || "channel").toLowerCase().replace(/[^a-z0-9]/g, "_");
    currentCrudLinkedAccounts = [{
      id: slug,
      name: ch.channel_name || slug,
      handle: ch.channel_handle || `@${slug}`,
      slug: slug,
      type: "Primary / Long-form",
      is_default: true,
      is_authorized: false
    }];
  } else {
    currentCrudLinkedAccounts = [];
  }
  renderCrudYouTubeAccounts();
  refreshCrudAccountsAuthStatus();
}

async function refreshCrudAccountsAuthStatus() {
  if (!currentCrudLinkedAccounts || currentCrudLinkedAccounts.length === 0) return;
  let changed = false;
  for (const acc of currentCrudLinkedAccounts) {
    if (!acc.slug) continue;
    try {
      const res = await fetch(`/api/channels/${acc.slug}/youtube/auth-status`);
      if (res.ok) {
        const data = await res.json();
        const authVal = Boolean(data.authorized);
        if (acc.is_authorized !== authVal) {
          acc.is_authorized = authVal;
          changed = true;
        }
      }
    } catch (e) {}
  }
  if (changed) renderCrudYouTubeAccounts();
}

function getCrudYouTubeAccounts() {
  return [...currentCrudLinkedAccounts];
}

function promptAddNewYouTubeAccount() {
  isAddingNewYtAccount = true;
  renderCrudYouTubeAccounts();
  const input = document.getElementById("inline-yt-name-input");
  if (input) input.focus();
}

function cancelInlineNewAccount() {
  isAddingNewYtAccount = false;
  renderCrudYouTubeAccounts();
}

function submitInlineNewAccount() {
  const nameInput = document.getElementById("inline-yt-name-input");
  const handleInput = document.getElementById("inline-yt-handle-input");
  const typeSelect = document.getElementById("inline-yt-type-select");

  const name = nameInput?.value?.trim();
  if (!name) {
    alert("Please enter a YouTube Channel Name.");
    return;
  }
  const handleRaw = handleInput?.value?.trim() || name;
  const cleanHandle = handleRaw.startsWith("@") ? handleRaw : `@${handleRaw}`;
  const derivedSlug = name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 36) || `yt_${Date.now()}`;
  const accType = typeSelect?.value || "Shorts & Reels";

  // Prevent duplicate slug
  const finalSlug = currentCrudLinkedAccounts.some(a => a.slug === derivedSlug)
    ? `${derivedSlug}_${Date.now().toString().slice(-4)}`
    : derivedSlug;

  currentCrudLinkedAccounts.push({
    id: finalSlug,
    name: name,
    handle: cleanHandle,
    slug: finalSlug,
    type: accType,
    is_default: currentCrudLinkedAccounts.length === 0,
    is_authorized: false
  });

  isAddingNewYtAccount = false;
  renderCrudYouTubeAccounts();
}

function removeCrudYouTubeAccount(slug) {
  if (currentCrudLinkedAccounts.length <= 1) {
    if (!confirm("Remove this YouTube account? The network will have no linked YouTube distribution.")) return;
  }
  currentCrudLinkedAccounts = currentCrudLinkedAccounts.filter(a => a.slug !== slug);
  renderCrudYouTubeAccounts();
}

function renderCrudYouTubeAccounts() {
  const container = document.getElementById("crud-yt-accounts-container");
  if (!container) return;

  let html = "";

  // 1. Inline New Account Form (when user clicks "+ Attach YouTube Channel")
  if (isAddingNewYtAccount) {
    html += `
      <div class="p-2.5 rounded-xl border border-red-500/40 bg-[var(--card)] space-y-2 shadow-sm animate-fadeIn">
        <div class="flex items-center justify-between">
          <span class="text-[11px] font-bold text-[var(--text)] flex items-center gap-1.5">
            <i class="fa-brands fa-youtube text-red-500 text-xs"></i>
            <span>Attach New YouTube Channel</span>
          </span>
          <span class="text-[9px] font-mono text-[var(--text-muted)]">OAuth Syndication</span>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
          <div>
            <label class="text-[9px] font-bold text-[var(--text-muted)] block mb-0.5">Account / Channel Name *</label>
            <input type="text" id="inline-yt-name-input" placeholder="e.g. Nature Rhythms Shorts" class="w-full px-2 py-1 bg-[var(--card-subtle)] border border-[var(--border)] rounded-md text-[var(--text)] text-xs focus:border-red-500 outline-none">
          </div>
          <div>
            <label class="text-[9px] font-bold text-[var(--text-muted)] block mb-0.5">Handle (@tag)</label>
            <input type="text" id="inline-yt-handle-input" placeholder="e.g. @NatureRhythmsShorts" class="w-full px-2 py-1 bg-[var(--card-subtle)] border border-[var(--border)] rounded-md text-[var(--text)] text-xs focus:border-red-500 outline-none">
          </div>
        </div>
        <div class="flex items-center justify-between gap-2 pt-0.5">
          <div class="flex-1">
            <label class="text-[9px] font-bold text-[var(--text-muted)] block mb-0.5">Channel Role / Content Type</label>
            <select id="inline-yt-type-select" class="w-full px-2 py-1 bg-[var(--card-subtle)] border border-[var(--border)] rounded-md text-[var(--text)] text-xs focus:border-red-500 outline-none font-semibold">
              <option value="9:16 Shorts &amp; Reels">📱 9:16 Shorts &amp; Reels</option>
              <option value="Primary / Long-form 4K">🎬 Primary / Long-form 4K</option>
              <option value="Ambient &amp; 24/7 Sleep Live">🌙 Ambient &amp; 24/7 Sleep Live</option>
              <option value="Regional / Multi-Language">🌐 Regional / Multi-Language</option>
              <option value="Secondary Outlet">⚡ Secondary Outlet</option>
            </select>
          </div>
          <div class="flex items-center gap-1.5 pt-3">
            <button type="button" onclick="cancelInlineNewAccount()" class="px-2.5 py-1 rounded-md border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text)] text-[10px] font-bold transition">Cancel</button>
            <button type="button" onclick="submitInlineNewAccount()" class="px-2.5 py-1 rounded-md bg-red-600 hover:bg-red-500 text-white text-[10px] font-bold transition shadow flex items-center gap-1">
              <i class="fa-solid fa-check text-[9px]"></i><span>Add Channel</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // 2. Empty State
  if (currentCrudLinkedAccounts.length === 0 && !isAddingNewYtAccount) {
    html += `
      <div class="p-3 rounded-lg border border-dashed border-[var(--border)] text-center text-[var(--text-muted)] text-[10px] space-y-1">
        <i class="fa-brands fa-youtube text-slate-400 text-base block"></i>
        <span>No YouTube channels attached yet. Click <strong>+ Attach YouTube Channel</strong> above to add long-form or shorts distribution channels.</span>
      </div>
    `;
  }

  // 3. Render List of Linked YouTube Accounts
  currentCrudLinkedAccounts.forEach((acc, idx) => {
    const isDef = acc.is_default || idx === 0;
    const typeLabel = acc.type || (isDef ? "Primary / Long-form" : "Shorts & Reels");
    const isAuth = Boolean(acc.is_authorized);

    html += `
      <div class="flex items-center justify-between p-2 rounded-lg bg-[var(--card)] border border-[var(--border)] gap-2 hover:border-red-500/40 transition shadow-sm">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-7 h-7 rounded-lg bg-red-600/10 text-red-500 flex items-center justify-center shrink-0 text-xs font-bold border border-red-500/20">
            <i class="fa-brands fa-youtube"></i>
          </div>
          <div class="min-w-0">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="font-bold text-[var(--text)] text-[11px] truncate">${acc.name}</span>
              <span class="text-[9px] font-mono text-[var(--text-muted)] truncate">${acc.handle || ('@' + acc.slug)}</span>
              <span class="px-1.5 py-0.2 rounded text-[8px] font-mono bg-red-500/10 text-red-400 font-bold border border-red-500/20">${typeLabel}</span>
              ${isDef ? '<span class="px-1.5 py-0.2 rounded text-[8px] font-mono bg-indigo-500/15 text-indigo-400 font-bold border border-indigo-500/30">Default</span>' : ''}
            </div>
            <div class="text-[9px] text-[var(--text-muted)] flex items-center gap-2 mt-0.5">
              <span class="font-mono flex items-center gap-1 ${isAuth ? 'text-emerald-400' : 'text-amber-400'}">
                <span class="w-1.5 h-1.5 rounded-full ${isAuth ? 'bg-emerald-400' : 'bg-amber-400'}"></span>
                ${isAuth ? 'OAuth Verified' : 'Awaiting Authorization'}
              </span>
              <span class="text-[8px] font-mono text-[var(--text-muted)]">slug: ${acc.slug}</span>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-1.5 shrink-0">
          <button type="button" onclick="openYouTubeCredentialsModal('${acc.slug}', '${(acc.name || '').replace(/'/g, "\\'")}')" class="px-2 py-0.5 rounded text-[9px] font-bold border transition flex items-center gap-1 ${isAuth ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20' : 'bg-red-600/10 text-red-500 border-red-500/30 hover:bg-red-600/20'}" title="Upload client_secret.json & Authorize OAuth">
            <i class="fa-solid ${isAuth ? 'fa-check' : 'fa-key'} text-[8px]"></i>
            <span>${isAuth ? 'Re-Auth' : 'Authorize'}</span>
          </button>
          <button type="button" onclick="removeCrudYouTubeAccount('${acc.slug}')" class="w-6 h-6 rounded flex items-center justify-center text-[var(--text-muted)] hover:text-red-500 hover:bg-red-500/10 transition" title="Detach channel">
            <i class="fa-solid fa-trash-can text-[10px]"></i>
          </button>
        </div>
      </div>
    `;
  });

  container.innerHTML = html;
}
