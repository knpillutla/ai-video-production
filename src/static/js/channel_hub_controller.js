// CineAI Studio: Channel Management & Video Hub Controller with full CRUD
let allChannelEpisodes = [];
let userChannels = [];
let currentHubChannel = "all";
let activeEnrichedProfile = null;

async function fetchUserChannels() {
  try {
    if (typeof fetchAndCacheChannelProfiles === "function") await fetchAndCacheChannelProfiles();
    const res = await fetch("/api/channels");
    const data = await res.json();
    if (Array.isArray(data)) {
      userChannels = data;
      if (typeof updateStudioChannelMetas === "function") updateStudioChannelMetas(userChannels);
      if (typeof renderChannelManagementShelf === "function") renderChannelManagementShelf();
      if (typeof renderChannelHubTable === "function") renderChannelHubTable();
    }
  } catch (err) {
    console.error("Error fetching channels:", err);
  }
}

function activateChannelFromHub(slug) {
  if (typeof selectStudioChannel === "function") selectStudioChannel(slug);
  selectHubChannel(slug);
}

function selectHubChannel(chId) {
  currentHubChannel = chId;
  if (typeof renderChannelManagementShelf === "function") renderChannelManagementShelf();
  if (typeof renderChannelHubTable === "function") renderChannelHubTable();
}

function openCreateChannelModal() {
  activeEnrichedProfile = null;
  document.getElementById("crud-is-edit").value = "false";
  document.getElementById("crud-channel-id").value = "";
  document.getElementById("crud-modal-title").textContent = "Create Distribution Channel";
  document.getElementById("crud-channel-slug").disabled = false;
  document.getElementById("crud-submit-btn").innerHTML = '<i class="fa-solid fa-plus text-[10px]"></i><span>Create Channel</span>';
  document.getElementById("channel-crud-form").reset();
  const preview = document.getElementById("crud-enriched-preview");
  if (preview) preview.classList.add("hidden");
  openModal("channel-crud-modal");
}

async function openEditChannelModal(channelId) {
  const ch = userChannels.find(c => String(c.id) === String(channelId) || c.channel_slug === channelId);
  if (!ch) return;
  activeEnrichedProfile = null;
  const slug = ch.channel_slug || ch.channel_name.toLowerCase().replace(/[^a-z0-9]/g, "_");
  document.getElementById("crud-is-edit").value = "true";
  document.getElementById("crud-channel-id").value = ch.id;
  document.getElementById("crud-modal-title").textContent = `Channel Strategy: ${ch.channel_name}`;
  document.getElementById("crud-channel-slug").value = slug;
  document.getElementById("crud-channel-slug").disabled = true;
  document.getElementById("crud-channel-name").value = ch.channel_name || "";
  document.getElementById("crud-channel-handle").value = (ch.channel_handle || "").replace(/^@/, "");
  document.getElementById("crud-channel-category").value = ch.category || "General";
  document.getElementById("crud-channel-lang").value = ch.primary_language || "en";
  document.getElementById("crud-channel-icon").value = ch.icon || "fa-clapperboard";
  document.getElementById("crud-channel-color").value = ch.color || "indigo";
  document.getElementById("crud-channel-desc").value = ch.description || "";
  document.getElementById("crud-channel-tag").value = ch.tag || "";
  document.getElementById("crud-channel-comments").value = ch.comments || "";
  document.getElementById("crud-channel-tags").value = (ch.default_tags || []).join(", ");
  document.getElementById("crud-submit-btn").innerHTML = '<i class="fa-solid fa-floppy-disk text-[10px]"></i><span>Save Changes</span>';

  if (cachedChannelProfiles && cachedChannelProfiles[slug]) {
    activeEnrichedProfile = cachedChannelProfiles[slug];
    const allowed = activeEnrichedProfile.allowed_genres || [];
    document.querySelectorAll('input[name="crud_genre"]').forEach(cb => {
      cb.checked = allowed.includes(cb.value);
    });
    updateEnrichedPreviewUI(activeEnrichedProfile);
  }
  openModal("channel-crud-modal");
}

function updateEnrichedPreviewUI(profile) {
  const preview = document.getElementById("crud-enriched-preview");
  if (!preview || !profile) return;
  preview.classList.remove("hidden");
  const aEl = document.getElementById("preview-audio-style");
  if (aEl) aEl.textContent = `${profile.audio_profile?.style || 'Harmonic'} (${profile.audio_profile?.bgm_enabled_by_default ? 'BGM ON' : 'Pure ASMR / BGM OFF'})`;
  const sEl = document.getElementById("preview-suno-tags");
  if (sEl) sEl.textContent = profile.audio_profile?.suno_tag_template || "";
  const lEl = document.getElementById("preview-lighting");
  if (lEl) lEl.textContent = profile.visual_lighting_guardrails?.lighting_temperature || "Natural";
  const pEl = document.getElementById("preview-purity");
  if (pEl) pEl.textContent = profile.visual_lighting_guardrails?.purity_rule || "Pure Nature";
}

function autoPopulateSlug(name) {
  if (document.getElementById("crud-is-edit").value === "true") return;
  const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 32);
  document.getElementById("crud-channel-slug").value = slug;
}

async function triggerGeminiChannelEnrichment() {
  const btn = document.getElementById("btn-ai-enrich-channel");
  const origText = btn ? btn.innerHTML : "";
  const name = document.getElementById("crud-channel-name")?.value.trim();
  const handle = document.getElementById("crud-channel-handle")?.value.trim() || name;
  const slug = document.getElementById("crud-channel-slug")?.value.trim() || autoPopulateSlug(name);
  const intent = document.getElementById("crud-channel-intent")?.value.trim() || "";

  if (!name) {
    alert("Please enter a Channel Name first.");
    return;
  }
  const selectedGenres = Array.from(document.querySelectorAll('input[name="crud_genre"]:checked')).map(cb => cb.value);

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-[9px]"></i><span>Synthesizing...</span>';
  }

  try {
    const res = await fetch("/api/channels/ai-enrich-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        channel_name: name,
        handle: handle.startsWith("@") ? handle : `@${handle}`,
        channel_slug: slug,
        allowed_genres: selectedGenres.length > 0 ? selectedGenres : ["relax/nature"],
        user_intent: intent
      })
    });
    const data = await res.json();
    if (data.status === "ok" && data.profile) {
      activeEnrichedProfile = data.profile;
      if (document.getElementById("crud-channel-desc")) document.getElementById("crud-channel-desc").value = activeEnrichedProfile.target_audience;
      if (document.getElementById("crud-channel-tag")) document.getElementById("crud-channel-tag").value = activeEnrichedProfile.tag;
      if (document.getElementById("crud-channel-comments")) document.getElementById("crud-channel-comments").value = activeEnrichedProfile.comments;
      if (document.getElementById("crud-channel-tags")) document.getElementById("crud-channel-tags").value = (activeEnrichedProfile.youtube_seo_defaults?.primary_tags || []).join(", ");
      updateEnrichedPreviewUI(activeEnrichedProfile);
    }
  } catch (err) {
    alert(`Gemini Enrichment Error: ${err.message}`);
  } finally {
    if (btn) { btn.disabled = false; btn.innerHTML = origText; }
  }
}

async function saveChannelForm(event) {
  if (event) event.preventDefault();
  const isEdit = document.getElementById("crud-is-edit").value === "true";
  const chId = document.getElementById("crud-channel-id").value;
  const tagsStr = document.getElementById("crud-channel-tags").value;
  const handleRaw = document.getElementById("crud-channel-handle").value.trim();
  const slug = document.getElementById("crud-channel-slug").value.trim();
  const selectedGenres = Array.from(document.querySelectorAll('input[name="crud_genre"]:checked')).map(cb => cb.value);

  const payload = {
    channel_name: document.getElementById("crud-channel-name").value.trim(),
    channel_slug: slug,
    channel_handle: handleRaw.startsWith("@") ? handleRaw : `@${handleRaw}`,
    category: document.getElementById("crud-channel-category").value,
    primary_language: document.getElementById("crud-channel-lang").value,
    icon: document.getElementById("crud-channel-icon").value,
    color: document.getElementById("crud-channel-color").value,
    description: document.getElementById("crud-channel-desc").value.trim(),
    tag: document.getElementById("crud-channel-tag")?.value.trim() || "",
    comments: document.getElementById("crud-channel-comments")?.value.trim() || "",
    default_tags: tagsStr ? tagsStr.split(",").map(t => t.trim()).filter(Boolean) : [],
    platform: "youtube"
  };

  try {
    const res = await fetch(isEdit ? `/api/channels/${chId}` : "/api/channels", {
      method: isEdit ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error("Failed to save channel");

    const profileToSave = activeEnrichedProfile || {
      channel_id: slug, channel_name: payload.channel_name, handle: payload.channel_handle,
      tag: payload.tag, comments: payload.comments, niche_category: payload.category,
      target_audience: payload.description, allowed_genres: selectedGenres.length > 0 ? selectedGenres : ["relax/nature"],
      audio_profile: { bgm_enabled_by_default: !slug.includes("hearth"), style: "Harmonic Soundscape", target_lufs: -14.0 },
      visual_lighting_guardrails: { lighting_temperature: "Natural (5400K)", purity_rule: "Pure Scenery" },
      youtube_seo_defaults: { primary_tags: payload.default_tags, category_id: "10" }
    };
    await fetch("/api/channels/save-profile", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profileToSave)
    });

    closeModal("channel-crud-modal");
    await fetchUserChannels();
  } catch (err) {
    alert(`Save failed: ${err.message}`);
  }
}

async function deleteChannelConfirm(chId, chName) {
  if (!confirm(`Delete channel "${chName}"?`)) return;
  try {
    await fetch(`/api/channels/${chId}`, { method: "DELETE" });
    await fetchUserChannels();
  } catch (err) {
    console.error("Delete error:", err);
  }
}

async function fetchChannelHubVideos() {
  try {
    const res = await fetch("/api/channels/episodes");
    const data = await res.json();
    if (data.status === "ok") {
      allChannelEpisodes = data.episodes || [];
      if (typeof renderChannelManagementShelf === "function") renderChannelManagementShelf();
      if (typeof renderChannelHubTable === "function") renderChannelHubTable();
    }
  } catch (err) {
    console.error("Error fetching episodes:", err);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fetchUserChannels();
  fetchChannelHubVideos();
});
