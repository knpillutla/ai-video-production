// CineAI Studio: Multi-Broadcast Distribution & Packaging Controller (Music, ASMR & Shorts)
let currentDistributionEpisode = null;
let currentBroadcastTags = [];
let currentNatureTags = [];
let currentShortTags = [];
let currentNetworkYtAccounts = [];
let selectedDistributionAccountSlug = null;

async function renderDistributionPackaging(vid) {
  if (!vid) return;
  currentDistributionEpisode = vid;

  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "nature_rhythms");
  const uEmail = (typeof currentUser !== "undefined" && currentUser?.email) ? currentUser.email : "knpillutla@gmail.com";
  const sanitizedUser = uEmail.replace(/@/g, "-").replace(/\./g, "-");
  loadNetworkDistributionAccounts(chSlug);

  // Check long-play & master editions on disk
  const isRelax = String(vid.genre || vid.format || "relaxation").toLowerCase().includes("relax");
  const eds = vid.long_play_editions || vid.editions || vid.all_editions || [];
  const has3hMusic = eds.some(e => e.edition_id === "3h_music" || (e.name && e.name.includes("3-Hour") && e.name.includes("Music")));
  const has8hMusic = eds.some(e => e.edition_id === "8h_music" || (e.name && e.name.includes("8-Hour") && e.name.includes("Music")));
  const has3hNature = eds.some(e => e.edition_id === "3h_nature" || (e.name && e.name.includes("3-Hour") && (e.name.includes("Nature") || e.name.includes("ASMR"))));
  const has8hNature = eds.some(e => e.edition_id === "8h_nature" || (e.name && e.name.includes("8-Hour") && (e.name.includes("Nature") || e.name.includes("ASMR"))));

  // Dynamic Header Titles & Badges
  const bTitleEl = document.getElementById("dist-broadcast-header-title");
  const bBadgeEl = document.getElementById("dist-broadcast-badge");
  if (bTitleEl && bBadgeEl) {
    if (has3hMusic) {
      bTitleEl.textContent = "3-Hour 4K Broadcast with Music (16:9 UHD)";
      bBadgeEl.textContent = "3h • Music + 432Hz BGM";
    } else if (has8hMusic) {
      bTitleEl.textContent = "8-Hour 4K Broadcast with Music (16:9 UHD)";
      bBadgeEl.textContent = "8h • Music + 432Hz BGM";
    } else {
      bTitleEl.textContent = isRelax ? "4K Broadcast Master with Music (16:9 UHD)" : "4K Master (Voiceover & Score)";
      bBadgeEl.textContent = "4K Master • Music";
    }
  }

  const nTitleEl = document.getElementById("dist-nature-header-title");
  const nBadgeEl = document.getElementById("dist-nature-badge");
  if (nTitleEl && nBadgeEl) {
    if (has3hNature) {
      nTitleEl.textContent = "3-Hour Pure Nature ASMR Broadcast (16:9 UHD)";
      nBadgeEl.textContent = "3h • Pure Rain/Nature ASMR";
    } else if (has8hNature) {
      nTitleEl.textContent = "8-Hour Pure Nature ASMR Broadcast (16:9 UHD)";
      nBadgeEl.textContent = "8h • Pure ASMR";
    } else if (!isRelax) {
      nTitleEl.textContent = "4K Clean Master (Instrumental / Zero Voiceover)";
      nBadgeEl.textContent = "4K Master • Clean Score";
    } else {
      nTitleEl.textContent = "4K Pure Nature ASMR Master (16:9 UHD)";
      nBadgeEl.textContent = "4K Master • Pure ASMR";
    }
  }

  // Load screenplay publishing metadata if not in memory
  let pub = vid.publishing || vid.screenplay?.publishing || vid.script?.publishing;
  if (!pub) {
    try {
      const fmtQ = encodeURIComponent(vid.format || vid.format_slug || "");
      const prodQ = encodeURIComponent(vid.production_name || "");
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&format=${fmtQ}&production_name=${prodQ}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        pub = data.screenplay?.publishing || data.script?.publishing;
      }
    } catch (e) {}
  }

  const topic = vid.story_topic || vid.concept || vid.title || "Nature Sanctuary";
  const cleanTitle = (vid.title || "Serene Nature Sanctuary").replace(/\s*-\s*4K.*$/i, "").trim();

  // 1. Resolve Thumbnails
  let thumbUrl = vid.thumbnail_url || vid.thumbnailUrl || vid.thumb_url || vid.keyframes?.[0]?.url;
  if (!thumbUrl && vid.format && vid.production_name) {
    thumbUrl = `/storage/user-${sanitizedUser}/networks/${chSlug}/${vid.format}/${vid.production_name}/${epId}/keyframe_p1.jpg?t=${Date.now()}`;
  }
  if (thumbUrl) {
    setupThumbnailDisplay("dist-broadcast-thumb-img", "dist-broadcast-thumb-placeholder", "dist-broadcast-thumb-link", thumbUrl);
    setupThumbnailDisplay("dist-nature-thumb-img", "dist-nature-thumb-placeholder", "dist-nature-thumb-link", thumbUrl);
    setupThumbnailDisplay("dist-short-thumb-img", "dist-short-thumb-placeholder", "dist-short-thumb-link", thumbUrl);
  }

  // 2. Section 1 (Music Edition) Titles
  const defaultBroadcastTitles = [
    `${cleanTitle} ⋄ 432Hz Deep Healing Soundbath - 4K UHD`,
    `3 HOURS of Deep Serenity in ${cleanTitle} ✦ Calming Sleep & Anxiety Relief`,
    `${cleanTitle} Sanctuary ⋄ 4K 60FPS Living Wallpaper & Velvet Resonance`
  ];
  const broadcastTitles = (pub?.ctr_titles && pub.ctr_titles.length > 0) ? pub.ctr_titles : defaultBroadcastTitles;
  const bTitleInput = document.getElementById("dist-yt-title");
  if (bTitleInput) {
    if (!bTitleInput.value || bTitleInput.value.includes("Master Video")) bTitleInput.value = broadcastTitles[0];
    updateCharCounter("dist-broadcast-title-chars", bTitleInput.value.length, 100);
    bTitleInput.oninput = () => updateCharCounter("dist-broadcast-title-chars", bTitleInput.value.length, 100);
  }
  renderTitleVariantPills("dist-broadcast-title-variants", broadcastTitles, (sel) => {
    if (bTitleInput) { bTitleInput.value = sel; updateCharCounter("dist-broadcast-title-chars", sel.length, 100); }
  });

  // Description & Tags (Music)
  const bDescInput = document.getElementById("dist-yt-desc");
  if (bDescInput) {
    bDescInput.value = pub?.description_with_timestamps || `Escape into the peaceful serenity of ${cleanTitle}.\n\n⏱️ Chapters:\n0:00 - Sanctuary Immersion\n30:00 - 432Hz Delta Brainwave Entrainment\n1:00:00 - Restorative Sleep & Deep Focus\n\n🌿 Production Lore:\n- Audio: 432Hz Velvet Binaural Master (-14.0 LUFS)\n- Visuals: 4K UHD Cinemagraph Master`;
  }
  currentBroadcastTags = (pub?.seo_tags && pub.seo_tags.length > 0) ? pub.seo_tags : ["4K Nature Relaxation", "432Hz Meditation Music", "Stress Relief", "Living Wallpaper 4K", "Deep Healing", "Sleep Aid", "Focus Music"];
  renderTagsPills("dist-broadcast-tags-container", "dist-broadcast-tags-count", currentBroadcastTags, "indigo");

  // 3. Section 2 (Pure Nature ASMR / Clean Edition)
  const defaultNatureTitles = [
    `${cleanTitle} ⋄ 3 HOURS Pure Rain ASMR & Nature Sounds (Zero Music)`,
    `Torrential Rain Falling on Balcony ✦ Deep Sleep ASMR & White Noise`,
    `${cleanTitle} Sanctuary ⋄ 4K Pure ASMR Living Wallpaper (No BGM)`
  ];
  const nTitleInput = document.getElementById("dist-yt-title-nature");
  if (nTitleInput) {
    if (!nTitleInput.value || nTitleInput.value.includes("Master Video")) nTitleInput.value = defaultNatureTitles[0];
    updateCharCounter("dist-nature-title-chars", nTitleInput.value.length, 100);
    nTitleInput.oninput = () => updateCharCounter("dist-nature-title-chars", nTitleInput.value.length, 100);
  }
  renderTitleVariantPills("dist-nature-title-variants", defaultNatureTitles, (sel) => {
    if (nTitleInput) { nTitleInput.value = sel; updateCharCounter("dist-nature-title-chars", sel.length, 100); }
  });

  const nDescInput = document.getElementById("dist-yt-desc-nature");
  if (nDescInput) {
    nDescInput.value = `Immerse in pure, unedited nature sounds from ${cleanTitle}. 100% Zero Music, pure environmental foley for insomnia relief and tranquil background ambience.\n\n⏱️ Chapters:\n0:00 - Pure Rain & Nature ASMR\n1:00:00 - Continuous Deep Sleep Ambience\n2:00:00 - Restorative Rain White Noise`;
  }
  currentNatureTags = ["PureRainASMR", "NatureSounds", "ZeroMusic", "WhiteNoise", "SleepAid", "4KASMR", "RainOnChalet", "RainstormSleep", "InsomniaRelief"];
  renderTagsPills("dist-nature-tags-container", "dist-nature-tags-count", currentNatureTags, "emerald");

  // 4. Section 3 (Shorts 9:16)
  const shortBase = cleanTitle.length > 32 ? cleanTitle.substring(0, 32).trim() + "..." : cleanTitle;
  const shortTitles = [`${shortBase} ✦ 432Hz Calm #Shorts`, `Feel Instant Peace ⋄ ${shortBase} #Shorts`, `Sleep in 60 Seconds ✦ ${shortBase} #Shorts`];
  const sTitleInput = document.getElementById("dist-short-title");
  if (sTitleInput) {
    sTitleInput.value = shortTitles[0];
    updateCharCounter("dist-short-title-chars", sTitleInput.value.length, 60);
    sTitleInput.oninput = () => updateCharCounter("dist-short-title-chars", sTitleInput.value.length, 60);
  }
  renderTitleVariantPills("dist-short-title-variants", shortTitles, (sel) => {
    if (sTitleInput) { sTitleInput.value = sel; updateCharCounter("dist-short-title-chars", sel.length, 60); }
  });

  const sDescInput = document.getElementById("dist-short-desc");
  if (sDescInput) sDescInput.value = `${topic.substring(0, 100)}...\n\n#Shorts #AmbientMusic #Nature #Relaxation #432Hz #Sleep #ViralShorts`;
  currentShortTags = ["#Shorts", "#ShortsFeed", "#AmbientMusic", "#Relaxation", "#4K", "#StressRelief", "#Meditation", "#Calm", "#ASMR"];
  renderTagsPills("dist-short-tags-container", "dist-short-tags-count", currentShortTags, "rose");

  syncDistributionCheckboxes();
}

function copyBroadcastDescription() { copyTextToClipboard(document.getElementById("dist-yt-desc")?.value, "Broadcast description copied!"); }
function copyBroadcastTags() { copyTextToClipboard(currentBroadcastTags.join(", "), "Broadcast SEO tags copied!"); }
function copyNatureDescription() { copyTextToClipboard(document.getElementById("dist-yt-desc-nature")?.value, "Nature ASMR description copied!"); }
function copyNatureTags() { copyTextToClipboard(currentNatureTags.join(", "), "Nature ASMR tags copied!"); }
function copyShortDescription() { copyTextToClipboard(document.getElementById("dist-short-desc")?.value, "Shorts description copied!"); }
function copyShortTags() { copyTextToClipboard(currentShortTags.join(", "), "Shorts viral tags copied!"); }

function syncDistributionCheckboxes() {
  const bCheck = document.getElementById("dist-check-broadcast");
  const nCheck = document.getElementById("dist-check-nature");
  const sCheck = document.getElementById("dist-check-short");
  const btn = document.getElementById("dist-publish-btn");
  const btnText = document.getElementById("dist-publish-btn-text");

  const bVal = bCheck ? bCheck.checked : true;
  const nVal = nCheck ? nCheck.checked : true;
  const sVal = sCheck ? sCheck.checked : true;

  const count = [bVal, nVal, sVal].filter(Boolean).length;
  if (btn && btnText) {
    btn.disabled = (count === 0);
    if (count === 3) btnText.textContent = "Publish All 3 Editions to YouTube";
    else if (count === 2) btnText.textContent = "Publish 2 Selected Editions to YouTube";
    else if (count === 1) {
      if (bVal) btnText.textContent = "Publish Music Broadcast to YouTube";
      else if (nVal) btnText.textContent = "Publish Nature ASMR to YouTube";
      else btnText.textContent = "Publish Short (9:16) to YouTube";
    } else btnText.textContent = "Select format to publish";
  }
}

function triggerInspectorYouTubePublish() {
  syncDistributionCheckboxes();
  const vid = currentDistributionEpisode || (typeof currentActiveInspectorEpisode !== "undefined" ? currentActiveInspectorEpisode : null);
  if (!vid) return;
  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "nature_rhythms");
  const epTitle = document.getElementById("dist-yt-title")?.value || vid.title || "4K Broadcast Master";
  if (typeof openPublishModal === "function") openPublishModal(epId, chSlug, epTitle);
}

async function loadNetworkDistributionAccounts(chSlug) {
  const sel = document.getElementById("dist-target-yt-account");
  if (!sel) return;
  try {
    const res = await fetch(`/api/channels/${chSlug}/youtube/accounts`);
    if (res.ok) {
      const data = await res.json();
      currentNetworkYtAccounts = data.accounts || [];
      if (currentNetworkYtAccounts.length > 0) {
        sel.innerHTML = currentNetworkYtAccounts.map(a => `<option value="${a.slug}" ${a.is_default ? 'selected' : ''}>${a.name} (${a.type || (a.is_default ? 'Primary' : 'Shorts')})</option>`).join("");
        selectedDistributionAccountSlug = sel.value;
        updateDistributionAccountBadge(selectedDistributionAccountSlug);
        return;
      }
    }
  } catch (e) {}
  sel.innerHTML = `<option value="${chSlug}">${chSlug} (Primary)</option>`;
  selectedDistributionAccountSlug = chSlug;
  updateDistributionAccountBadge(chSlug);
}

function updateDistributionAccountBadge(slug) {
  const badge = document.getElementById("dist-target-yt-auth-badge");
  if (!badge) return;
  const acc = currentNetworkYtAccounts.find(a => a.slug === slug);
  const isAuth = Boolean(acc?.is_authorized);
  badge.className = isAuth
    ? "shrink-0 flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
    : "shrink-0 flex items-center gap-1 text-[9px] font-mono font-bold px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500 border border-amber-500/20";
  badge.innerHTML = isAuth ? `<i class="fa-solid fa-circle-check text-[8px]"></i><span>OAuth Verified</span>` : `<i class="fa-solid fa-triangle-exclamation text-[8px]"></i><span>Unlinked</span>`;
}

function onStudioDistributionAccountChange(val) {
  selectedDistributionAccountSlug = val;
  updateDistributionAccountBadge(val);
}

function openStudioTargetCredentialsModal() {
  const sel = document.getElementById("dist-target-yt-account");
  const slug = sel?.value || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "nature_rhythms");
  const name = sel?.selectedOptions?.[0]?.textContent?.trim() || slug;
  if (typeof openYouTubeCredentialsModal === "function") openYouTubeCredentialsModal(slug, name);
}
