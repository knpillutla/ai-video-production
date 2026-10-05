// CineAI Studio: YouTube Packaging & Distribution Hub Controller (Broadcast 16:9 + Short 9:16)
let currentDistributionEpisode = null;
let currentBroadcastTags = [];
let currentShortTags = [];

async function renderDistributionPackaging(vid) {
  if (!vid) return;
  currentDistributionEpisode = vid;

  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  const uEmail = (typeof currentUser !== "undefined" && currentUser?.email) ? currentUser.email : "knpillutla@gmail.com";
  const sanitizedUser = uEmail.replace(/@/g, "-").replace(/\./g, "-");

  // Load screenplay publishing metadata if not in memory
  let pub = vid.publishing || vid.screenplay?.publishing || vid.script?.publishing;
  if (!pub) {
    try {
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.screenplay?.publishing) pub = data.screenplay.publishing;
        else if (data.script?.publishing) pub = data.script.publishing;
      }
    } catch (e) {
      console.debug("Failed to poll publishing metadata:", e);
    }
  }

  const topic = vid.story_topic || vid.concept || vid.title || "Desert Sanctuary";
  const cleanTitle = (vid.title || "Serene Nature Sanctuary").replace(/\s*-\s*4K.*$/i, "").trim();

  // 1. Resolve Thumbnails
  const thumbUrl = `/storage/user-${sanitizedUser}/channels/${chSlug}/${epId}/keyframe_p1.jpg?t=${Date.now()}`;
  setupThumbnailDisplay("dist-broadcast-thumb-img", "dist-broadcast-thumb-placeholder", "dist-broadcast-thumb-link", thumbUrl);
  setupThumbnailDisplay("dist-short-thumb-img", "dist-short-thumb-placeholder", "dist-short-thumb-link", thumbUrl);

  // 2. Resolve Broadcast Trending Titles
  const defaultBroadcastTitles = [
    `${cleanTitle} ⋄ 432Hz Deep Healing Soundbath - 4K UHD`,
    `3 HOURS of Deep Serenity in ${cleanTitle} ✦ Calming Sleep & Anxiety Relief`,
    `${cleanTitle} Sanctuary ⋄ 4K 60FPS Living Wallpaper & Velvet Resonance`
  ];
  const broadcastTitles = (pub?.ctr_titles && pub.ctr_titles.length > 0) ? pub.ctr_titles : defaultBroadcastTitles;

  const bTitleInput = document.getElementById("dist-yt-title");
  if (bTitleInput) {
    if (!bTitleInput.value || bTitleInput.value.includes("Master Video")) {
      bTitleInput.value = broadcastTitles[0];
    }
    updateCharCounter("dist-broadcast-title-chars", bTitleInput.value.length, 100);
    bTitleInput.oninput = () => updateCharCounter("dist-broadcast-title-chars", bTitleInput.value.length, 100);
  }
  renderTitleVariantPills("dist-broadcast-title-variants", broadcastTitles, (sel) => {
    if (bTitleInput) {
      bTitleInput.value = sel;
      updateCharCounter("dist-broadcast-title-chars", sel.length, 100);
    }
  });

  // 3. Resolve Broadcast Description & Chapters
  const bDescInput = document.getElementById("dist-yt-desc");
  if (bDescInput) {
    if (pub?.description_with_timestamps) {
      bDescInput.value = pub.description_with_timestamps;
    } else {
      bDescInput.value = `Escape into the peaceful serenity of ${cleanTitle}.\n\n⏱️ Chapters:\n0:00 - Sanctuary Immersion\n30:00 - 432Hz Delta Brainwave Entrainment\n1:00:00 - Restorative Sleep & Deep Focus\n\n🌿 Production Lore:\n- Audio: 432Hz Velvet Binaural Master (-14.0 LUFS Broadcast Standard)\n- Visuals: 4K UHD Lossless Cinemagraph Master (24 FPS)\n- YPP Monetization: 100% Commercial Cleared & Advertiser-Friendly`;
    }
  }

  // 4. Resolve Broadcast SEO Tags
  const defaultBTags = ["4K Nature Relaxation", "432Hz Meditation Music", "Stress Relief", "Living Wallpaper 4K", "Deep Healing", "Sleep Aid", "Cinemagraph Nature", "Anti-Fatigue Soundscape", "Focus Music"];
  currentBroadcastTags = (pub?.seo_tags && pub.seo_tags.length > 0) ? pub.seo_tags : defaultBTags;
  renderTagsPills("dist-broadcast-tags-container", "dist-broadcast-tags-count", currentBroadcastTags, "indigo");

  // 5. Resolve Short (9:16) Viral Titles (<60 chars with #Shorts)
  const shortBase = cleanTitle.length > 32 ? cleanTitle.substring(0, 32).trim() + "..." : cleanTitle;
  const shortTitles = [
    `${shortBase} ✦ 432Hz Calm #Shorts`,
    `Feel Instant Peace ⋄ ${shortBase} #Shorts`,
    `Sleep in 60 Seconds ✦ ${shortBase} #Shorts`
  ];

  const sTitleInput = document.getElementById("dist-short-title");
  if (sTitleInput) {
    sTitleInput.value = shortTitles[0];
    updateCharCounter("dist-short-title-chars", sTitleInput.value.length, 60);
    sTitleInput.oninput = () => updateCharCounter("dist-short-title-chars", sTitleInput.value.length, 60);
  }
  renderTitleVariantPills("dist-short-title-variants", shortTitles, (sel) => {
    if (sTitleInput) {
      sTitleInput.value = sel;
      updateCharCounter("dist-short-title-chars", sel.length, 60);
    }
  });

  // 6. Resolve Short Description & Hashtags
  const sDescInput = document.getElementById("dist-short-desc");
  if (sDescInput) {
    sDescInput.value = `${topic.substring(0, 100)}...\n\n#Shorts #AmbientMusic #Nature #Relaxation #432Hz #Sleep #ViralShorts`;
  }

  // 7. Resolve Shorts Viral Tags
  currentShortTags = ["#Shorts", "#ShortsFeed", "#AmbientMusic", "#Relaxation", "#4K", "#StressRelief", "#Meditation", "#Calm", "#ASMR"];
  renderTagsPills("dist-short-tags-container", "dist-short-tags-count", currentShortTags, "rose");
}

function setupThumbnailDisplay(imgId, phId, linkId, url) {
  const img = document.getElementById(imgId);
  const ph = document.getElementById(phId);
  const link = document.getElementById(linkId);
  if (!img) return;

  const testImg = new Image();
  testImg.onload = () => {
    img.src = url;
    img.classList.remove("hidden");
    if (ph) ph.classList.add("hidden");
    if (link) { link.href = url; link.classList.remove("hidden"); }
  };
  testImg.onerror = () => {
    img.classList.add("hidden");
    if (ph) ph.classList.remove("hidden");
    if (link) link.classList.add("hidden");
  };
  testImg.src = url;
}

function updateCharCounter(elId, count, max) {
  const el = document.getElementById(elId);
  if (el) {
    el.textContent = `${count}/${max}`;
    el.className = count > max ? "font-mono text-[9px] text-red-500 font-bold" : "font-mono text-[9px] text-[var(--text-muted)]";
  }
}

function renderTitleVariantPills(containerId, variants, onSelect) {
  const c = document.getElementById(containerId);
  if (!c) return;
  c.innerHTML = variants.map((v, i) => `
    <button type="button" class="text-left text-[10px] px-2 py-0.5 rounded bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] text-[var(--text)] hover:border-indigo-400 dark:hover:border-indigo-500 transition truncate flex items-center gap-1 group" title="Click to use this title">
      <span class="text-[8px] font-mono font-bold px-1 rounded bg-[var(--card-subtle)] text-[var(--text-muted)] group-hover:text-indigo-400">#${i + 1}</span>
      <span class="truncate">${v}</span>
    </button>
  `).join("");

  c.querySelectorAll("button").forEach((btn, idx) => {
    btn.onclick = () => onSelect(variants[idx]);
  });
}

function renderTagsPills(containerId, countId, tags, color = "indigo") {
  const c = document.getElementById(containerId);
  const countEl = document.getElementById(countId);
  if (!c) return;
  if (countEl) countEl.textContent = `(${tags.length})`;

  const badgeCls = color === "rose" 
    ? "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20"
    : "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20";

  c.innerHTML = tags.map(t => `
    <span class="text-[9px] font-mono px-1.5 py-0.5 rounded-md border ${badgeCls} inline-flex items-center gap-0.5">
      ${t.startsWith('#') ? '' : '#'}${t}
    </span>
  `).join("");
}

function copyBroadcastDescription() {
  const val = document.getElementById("dist-yt-desc")?.value || "";
  navigator.clipboard.writeText(val);
  if (typeof showToast === "function") showToast("Broadcast description copied to clipboard!", "success");
}

function copyBroadcastTags() {
  const text = currentBroadcastTags.join(", ");
  navigator.clipboard.writeText(text);
  if (typeof showToast === "function") showToast("All Broadcast SEO tags copied!", "success");
}

function copyShortDescription() {
  const val = document.getElementById("dist-short-desc")?.value || "";
  navigator.clipboard.writeText(val);
  if (typeof showToast === "function") showToast("Shorts description copied to clipboard!", "success");
}

function copyShortTags() {
  const text = currentShortTags.join(", ");
  navigator.clipboard.writeText(text);
  if (typeof showToast === "function") showToast("All Shorts viral tags copied!", "success");
}

function syncDistributionCheckboxes() {
  const bCheck = document.getElementById("dist-check-broadcast");
  const sCheck = document.getElementById("dist-check-short");
  const btn = document.getElementById("dist-publish-btn");
  const btnText = document.getElementById("dist-publish-btn-text");

  const bVal = bCheck ? bCheck.checked : true;
  const sVal = sCheck ? sCheck.checked : true;

  const mbCheck = document.getElementById("yt-pub-check-broadcast");
  const msCheck = document.getElementById("yt-pub-check-short");
  if (mbCheck) mbCheck.checked = bVal;
  if (msCheck) msCheck.checked = sVal;

  if (btn && btnText) {
    if (bVal && sVal) {
      btn.disabled = false;
      btnText.textContent = "Publish Both to YouTube";
    } else if (bVal) {
      btn.disabled = false;
      btnText.textContent = "Publish 4K Broadcast to YouTube";
    } else if (sVal) {
      btn.disabled = false;
      btnText.textContent = "Publish Short (9:16) to YouTube";
    } else {
      btn.disabled = true;
      btnText.textContent = "Select format to publish";
    }
  }
}

function triggerInspectorYouTubePublish() {
  syncDistributionCheckboxes();
  const vid = currentDistributionEpisode || (typeof currentActiveInspectorEpisode !== "undefined" ? currentActiveInspectorEpisode : null);
  if (!vid) return;
  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");
  const epTitle = document.getElementById("dist-yt-title")?.value || vid.title || "4K Broadcast Master";

  if (typeof openPublishModal === "function") {
    openPublishModal(epId, chSlug, epTitle);
  }
}

