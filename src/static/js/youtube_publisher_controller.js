// CineAI Studio: YouTube Credentials & Background Idempotent Publishing Controller
let currentYtChannelSlug = "", currentYtEpisodeId = "", selectedSecretFile = null, ytPollTimer = null;

// ==========================================
// 1. YouTube OAuth Credentials Management
// ==========================================

async function openYouTubeCredentialsModal(channelSlug, channelName = "") {
  currentYtChannelSlug = channelSlug || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  const nameEl = document.getElementById("yt-cred-channel-name"), slugEl = document.getElementById("yt-cred-channel-slug");
  if (nameEl) nameEl.textContent = channelName || currentYtChannelSlug.replace(/_/g, " ").toUpperCase();
  if (slugEl) slugEl.textContent = currentYtChannelSlug;
  document.getElementById("yt-cred-upload-msg")?.classList.add("hidden");
  document.getElementById("yt-cred-auth-msg")?.classList.add("hidden");
  openModal("youtube-credentials-modal");
  await refreshChannelAuthStatus(currentYtChannelSlug);
}

async function refreshChannelAuthStatus(slug) {
  const badge = document.getElementById("yt-cred-status-badge"), authBtn = document.getElementById("yt-cred-auth-btn"), discBtn = document.getElementById("yt-cred-disconnect-btn");
  if (badge) {
    badge.className = "px-2.5 py-1 rounded-full text-[10px] font-bold border flex items-center gap-1.5 bg-gray-500/10 text-gray-400 border-gray-500/30";
    badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-gray-400"></span><span>Checking...</span>`;
  }
  try {
    const res = await fetch(`/api/channels/${slug}/youtube/auth-status`), data = await res.json();
    if (data.authorized) {
      if (badge) {
        badge.className = "px-2.5 py-1 rounded-full text-[10px] font-bold border flex items-center gap-1.5 bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/40";
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span><span>Authorized: ${data.channel_title || 'YouTube Channel'}</span>`;
      }
      if (authBtn) authBtn.innerHTML = `<i class="fa-solid fa-arrows-rotate text-xs"></i><span>Re-Authorize Account</span>`;
      discBtn?.classList.remove("hidden");
    } else {
      if (badge) {
        badge.className = "px-2.5 py-1 rounded-full text-[10px] font-bold border flex items-center gap-1.5 bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/40";
        badge.innerHTML = `<span class="w-2 h-2 rounded-full bg-amber-500"></span><span>${data.has_client_secret ? 'Ready for Authorization' : 'Credentials Missing'}</span>`;
      }
      if (authBtn) {
        authBtn.innerHTML = `<i class="fa-brands fa-google text-xs"></i><span>Authorize with Google</span>`;
        authBtn.disabled = !data.has_client_secret;
      }
      discBtn?.classList.add("hidden");
    }
    return data;
  } catch (err) { console.error("Error refreshing channel auth status:", err); }
}

function handleSecretFileSelected(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  selectedSecretFile = file;
  const label = document.getElementById("yt-cred-file-label"), uploadBtn = document.getElementById("yt-cred-upload-btn");
  if (label) label.textContent = file.name;
  if (uploadBtn) uploadBtn.disabled = false;
}

async function uploadClientSecretFile() {
  if (!selectedSecretFile || !currentYtChannelSlug) return;
  const uploadBtn = document.getElementById("yt-cred-upload-btn"), msgEl = document.getElementById("yt-cred-upload-msg");
  if (uploadBtn) { uploadBtn.disabled = true; uploadBtn.textContent = "Uploading..."; }
  const formData = new FormData();
  formData.append("file", selectedSecretFile);
  try {
    const res = await fetch(`/api/channels/${currentYtChannelSlug}/youtube/credentials`, { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Upload failed");
    if (msgEl) { msgEl.className = "text-[10px] font-mono text-emerald-500 block"; msgEl.textContent = `✅ ${data.message}`; }
    await refreshChannelAuthStatus(currentYtChannelSlug);
  } catch (err) {
    if (msgEl) { msgEl.className = "text-[10px] font-mono text-red-500 block"; msgEl.textContent = `❌ ${err.message}`; }
  } finally {
    if (uploadBtn) { uploadBtn.disabled = false; uploadBtn.textContent = "Upload & Register"; }
  }
}

async function triggerGoogleOAuthAuthorization() {
  if (!currentYtChannelSlug) return;
  const authBtn = document.getElementById("yt-cred-auth-btn"), authMsg = document.getElementById("yt-cred-auth-msg");
  if (authBtn) { authBtn.disabled = true; authBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs"></i><span>Connecting...</span>`; }
  if (authMsg) { authMsg.className = "text-[10px] font-mono text-indigo-400 block"; authMsg.textContent = "👉 A browser window is opening for Google OAuth consent. Please approve access..."; }
  try {
    const res = await fetch(`/api/channels/${currentYtChannelSlug}/youtube/authorize`, { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Authorization failed");
    if (authMsg) { authMsg.className = "text-[10px] font-mono text-emerald-500 block"; authMsg.textContent = `✅ Successfully linked to: ${data.channel_title || 'YouTube'}`; }
    await refreshChannelAuthStatus(currentYtChannelSlug);
    if (typeof fetchAndCacheChannelProfiles === "function") fetchAndCacheChannelProfiles();
  } catch (err) {
    if (authMsg) { authMsg.className = "text-[10px] font-mono text-red-500 block"; authMsg.textContent = `❌ ${err.message}`; }
  } finally {
    if (authBtn) authBtn.disabled = false;
  }
}

async function disconnectYouTubeAuth() {
  if (!currentYtChannelSlug || !confirm(`Disconnect YouTube account for ${currentYtChannelSlug}?`)) return;
  try {
    await fetch(`/api/channels/${currentYtChannelSlug}/youtube/disconnect`, { method: "DELETE" });
    await refreshChannelAuthStatus(currentYtChannelSlug);
  } catch (err) { console.error("Failed to disconnect YouTube:", err); }
}

// ==========================================
// 2. Background Resilient Publishing
// ==========================================

let currentPublishAccountsList = [];

async function openPublishModal(episodeId, channelSlug, episodeTitle = "") {
  currentYtEpisodeId = episodeId;
  currentYtChannelSlug = channelSlug || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  const liveTitle = document.getElementById("dist-yt-title")?.value || episodeTitle || "4K Master Experience";
  const epIdEl = document.getElementById("yt-pub-episode-id"), epTitleEl = document.getElementById("yt-pub-episode-title");
  const chSlugEl = document.getElementById("yt-pub-channel-slug"), chTitleEl = document.getElementById("yt-pub-channel-title");
  const resultBox = document.getElementById("yt-pub-result-box"), submitBtn = document.getElementById("yt-pub-submit-btn");

  if (epIdEl) epIdEl.textContent = episodeId;
  if (epTitleEl) epTitleEl.textContent = liveTitle;
  if (chSlugEl) chSlugEl.textContent = currentYtChannelSlug;
  if (resultBox) { resultBox.classList.add("hidden"); resultBox.innerHTML = ""; }
  if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = `<i class="fa-brands fa-youtube"></i><span>Upload & Publish</span>`; }

  const distB = document.getElementById("dist-check-broadcast"), distN = document.getElementById("dist-check-nature"), distS = document.getElementById("dist-check-short");
  const modB = document.getElementById("yt-pub-check-broadcast"), modN = document.getElementById("yt-pub-check-nature"), modS = document.getElementById("yt-pub-check-short");
  if (modB && distB) modB.checked = distB.checked;
  if (modN && distN) modN.checked = distN.checked;
  if (modS && distS) modS.checked = distS.checked;

  try {
    const accRes = await fetch(`/api/channels/${currentYtChannelSlug}/youtube/accounts`).catch(() => null);
    if (accRes && accRes.ok) {
      const accData = await accRes.json();
      currentPublishAccountsList = accData.accounts || [];
      const accSel = document.getElementById("yt-pub-account-select");
      if (accSel && currentPublishAccountsList.length > 0) {
        const firstAuth = currentPublishAccountsList.find(a => a.is_authorized);
        accSel.innerHTML = currentPublishAccountsList.map(a => {
          const isSelected = firstAuth ? a.slug === firstAuth.slug : a.is_default;
          return `<option value="${a.slug}" ${isSelected ? 'selected' : ''}>
            ${a.name} (${a.type || (a.is_default ? 'Primary' : 'Shorts')}) ${a.is_authorized ? '✓' : '⚠️'}
          </option>`;
        }).join("");
        onPublishAccountSelectChange(accSel.value);
      }
    }
  } catch (e) {}

  try {
    const activeAccSlug = document.getElementById("yt-pub-account-select")?.value || currentYtChannelSlug;
    const res = await fetch(`/api/channels/${currentYtChannelSlug}/episodes/${episodeId}/publish-status?target_slug=${activeAccSlug}`);
    const data = await res.json();
    if (chTitleEl) chTitleEl.textContent = data.channel_title || currentYtChannelSlug.replace(/_/g, " ").toUpperCase();
    if (data.upload_in_progress) startPublishStatusPolling(data.upload_state);
    else if (data.published) renderPublishedResult(data);
    openModal("youtube-publish-modal");
  } catch (err) {
    openModal("youtube-publish-modal");
  }
}

function onPublishAccountSelectChange(selectedSlug) {
  const acc = currentPublishAccountsList.find(a => a.slug === selectedSlug);
  const authBadge = document.getElementById("yt-pub-auth-badge"), authText = document.getElementById("yt-pub-auth-text");
  const isAuth = Boolean(acc ? acc.is_authorized : false);
  if (authBadge) {
    authBadge.className = isAuth
      ? "px-2 py-0.5 rounded-full text-[9px] font-bold border flex items-center gap-1 bg-emerald-500/15 text-emerald-500 border-emerald-500/30"
      : "px-2 py-0.5 rounded-full text-[9px] font-bold border flex items-center gap-1 bg-amber-500/15 text-amber-500 border-amber-500/30";
  }
  if (authText) authText.textContent = isAuth ? `Authorized (${acc?.name || selectedSlug})` : "Awaiting OAuth Link";
}

function renderPublishedResult(data) {
  const resultBox = document.getElementById("yt-pub-result-box"), submitBtn = document.getElementById("yt-pub-submit-btn");
  if (resultBox) {
    resultBox.classList.remove("hidden");
    resultBox.innerHTML = `<div class="flex items-center gap-2 text-emerald-500 font-bold text-xs"><i class="fa-solid fa-circle-check"></i><span>Published to YouTube (Idempotent Safe)</span></div>
      <div class="space-y-1 text-[11px] pt-1 border-t border-[var(--border)]">
        ${data.short?.url ? `<div>📱 <strong>Short:</strong> <a href="${data.short.url}" target="_blank" class="text-indigo-400 hover:underline font-mono">${data.short.url}</a></div>` : ''}
        ${data.broadcast?.url ? `<div>🎬 <strong>Music Edition:</strong> <a href="${data.broadcast.url}" target="_blank" class="text-indigo-400 hover:underline font-mono">${data.broadcast.url}</a></div>` : ''}
        ${data.nature?.url ? `<div>🌿 <strong>Nature ASMR:</strong> <a href="${data.nature.url}" target="_blank" class="text-indigo-400 hover:underline font-mono">${data.nature.url}</a></div>` : ''}
      </div>`;
  }
  if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = `<i class="fa-solid fa-check"></i><span>Already Published</span>`; }
}

function startPublishStatusPolling(initialState) {
  const resultBox = document.getElementById("yt-pub-result-box"), submitBtn = document.getElementById("yt-pub-submit-btn");
  if (ytPollTimer) clearInterval(ytPollTimer);

  const updateUI = (state) => {
    if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs"></i><span>Uploading (${state?.progress_pct || 0}%)...</span>`; }
    if (resultBox) {
      resultBox.classList.remove("hidden");
      resultBox.innerHTML = `<div class="flex items-center gap-2 text-indigo-400 font-semibold text-xs"><i class="fa-solid fa-spinner fa-spin"></i><span>${state?.step || 'Uploading in background...'} (${state?.progress_pct || 0}%)</span></div>
        <p class="text-[10px] text-[var(--text-muted)] mt-1">✓ You can safely close or refresh the browser. Backend continues uploading.</p>`;
    }
  };

  updateUI(initialState);

  ytPollTimer = setInterval(async () => {
    try {
      const res = await fetch(`/api/channels/${currentYtChannelSlug}/episodes/${currentYtEpisodeId}/publish-status`);
      const data = await res.json();
      if (data.published) {
        clearInterval(ytPollTimer);
        renderPublishedResult(data);
        const sb = document.getElementById("top-ep-status-badge");
        if (sb) { sb.className = "px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-600 text-white shadow-sm flex items-center gap-1"; sb.innerHTML = '<i class="fa-brands fa-youtube text-[10px]"></i><span>Published</span>'; }
      } else if (data.upload_in_progress) {
        updateUI(data.upload_state);
      } else if (data.upload_state?.status === "failed") {
        clearInterval(ytPollTimer);
        if (resultBox) { resultBox.innerHTML = `<div class="text-red-500 font-bold text-xs"><i class="fa-solid fa-circle-xmark"></i> Upload Failed: ${data.upload_state.error || 'Unknown error'}</div>`; }
        if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = `<i class="fa-brands fa-youtube"></i><span>Retry Upload</span>`; }
      }
    } catch (e) { console.debug("Publish status poll error:", e); }
  }, 3000);
}

async function executeYouTubePublication() {
  if (!currentYtChannelSlug || !currentYtEpisodeId) return;

  const submitBtn = document.getElementById("yt-pub-submit-btn");
  const privacy = document.querySelector('input[name="yt_privacy"]:checked')?.value || "public";
  const forceReupload = document.getElementById("yt-pub-force-reupload")?.checked || false;

  // Custom metadata & checkboxes from UI
  const bTitle = document.getElementById("dist-yt-title")?.value || "";
  const bDesc = document.getElementById("dist-yt-desc")?.value || "";
  const nTitle = document.getElementById("dist-yt-title-nature")?.value || "";
  const nDesc = document.getElementById("dist-yt-desc-nature")?.value || "";
  const sTitle = document.getElementById("dist-short-title")?.value || "";
  const sDesc = document.getElementById("dist-short-desc")?.value || "";
  const uploadShort = document.getElementById("yt-pub-check-short")?.checked ?? true;
  const uploadBroadcast = document.getElementById("yt-pub-check-broadcast")?.checked ?? true;
  const uploadNature = document.getElementById("yt-pub-check-nature")?.checked ?? false;
  const targetAccSlug = document.getElementById("yt-pub-account-select")?.value || currentYtChannelSlug;

  if (!uploadShort && !uploadBroadcast && !uploadNature) {
    alert("Please select at least one format to upload (Short, Broadcast, or Nature ASMR).");
    return;
  }

  if (submitBtn) { submitBtn.disabled = true; submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin text-xs"></i><span>Initiating Upload...</span>`; }

  try {
    const res = await fetch(`/api/channels/${currentYtChannelSlug}/episodes/${currentYtEpisodeId}/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        privacy_status: privacy,
        force_reupload: forceReupload,
        title: bTitle,
        description: bDesc,
        nature_title: nTitle,
        nature_description: nDesc,
        short_title: sTitle,
        short_description: sDesc,
        upload_short: uploadShort,
        upload_broadcast: uploadBroadcast,
        upload_nature: uploadNature,
        target_channel_slug: targetAccSlug,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Publication failed");

    startPublishStatusPolling({ step: "Started background upload...", progress_pct: 5 });
  } catch (err) {
    const resultBox = document.getElementById("yt-pub-result-box");
    if (resultBox) {
      resultBox.classList.remove("hidden");
      resultBox.innerHTML = `<div class="text-red-500 font-bold text-xs"><i class="fa-solid fa-circle-xmark"></i> ${err.message}</div>`;
    }
    if (submitBtn) { submitBtn.disabled = false; submitBtn.innerHTML = `<i class="fa-brands fa-youtube"></i><span>Retry Upload</span>`; }
  }
}

function onCredentialsModalClosed() {
  if (typeof refreshCrudAccountsAuthStatus === "function") refreshCrudAccountsAuthStatus();
  if (typeof loadNetworkDistributionAccounts === "function" && typeof selectedStudioChannel !== "undefined") {
    loadNetworkDistributionAccounts(selectedStudioChannel);
  }
}
