// CineAI Studio: Panel 1 Creation Hub Controller (New Production & Channel Archive)
let activeCreationTab = "new";
let channelArchiveEpisodes = [];

function switchCreationTab(tabKey) {
  activeCreationTab = tabKey;
  const btnNew = document.getElementById("btn-tab-creation-new"), btnArch = document.getElementById("btn-tab-creation-archive");
  const viewNew = document.getElementById("view-creation-new"), viewArch = document.getElementById("view-creation-archive");

  if (btnNew) btnNew.classList.toggle("active", tabKey === "new");
  if (btnArch) btnArch.classList.toggle("active", tabKey === "archive");

  if (tabKey === "new") {
    if (viewNew) viewNew.classList.remove("hidden");
    if (viewArch) viewArch.classList.add("hidden");
    if (!currentActiveInspectorEpisode && typeof renderEmptyInspectorState === "function") renderEmptyInspectorState();
    else if (currentActiveInspectorEpisode && typeof populateProductionControlsFromEpisode === "function") populateProductionControlsFromEpisode(currentActiveInspectorEpisode);
  } else {
    if (viewNew) viewNew.classList.add("hidden");
    if (viewArch) viewArch.classList.remove("hidden");
    fetchAndRenderChannelArchive();
  }
}

function openHierarchyGuideModal() {
  const modal = document.getElementById("hierarchy-guide-modal");
  if (modal) modal.classList.remove("hidden");
}

function closeHierarchyGuideModal() {
  const modal = document.getElementById("hierarchy-guide-modal");
  if (modal) modal.classList.add("hidden");
}

const STUDIO_FORMAT_DEFINITIONS = {
  relaxation: { label: "🧘 Relaxation & Ambient", icon: "fa-spa", defaultGenre: "relax/nature" },
  documentary: { label: "🦅 Documentary", icon: "fa-compass", defaultGenre: "documentary" },
  walking_tour: { label: "🚶 4K Walking Tour", icon: "fa-person-walking", defaultGenre: "travel_walking" },
  music_video: { label: "💃 Music & Dance", icon: "fa-music", defaultGenre: "dance/folk" },
  short: { label: "📱 Shorts & Reels", icon: "fa-mobile-screen", defaultGenre: "comedy/satire" },
  movie: { label: "🎬 Movie & Drama", icon: "fa-film", defaultGenre: "documentary" }
};

let activeStudioFormat = "relaxation";
let activeSeriesMode = "existing";
let cachedExistingSeries = [];

function getCuratedProductionPresets(channelSlug, formatKey) {
  const c = String(channelSlug || "").toLowerCase();
  const f = String(formatKey || "").toLowerCase();
  const g = String(document.getElementById("studio-genre-selector")?.value || "").toLowerCase();
  const sg = String(document.getElementById("studio-subgenre-selector")?.value || "").toLowerCase();

  if (c.includes("euro") || g.includes("nations") || sg.includes("europe") || c.includes("discovery")) {
    return [
      "Grand European Odyssey",
      "Chronicles of Europe",
      "European Heritage & Empires",
      "Great Cities of Europe",
      "Alpine & Nordic Sanctuaries",
      "Mediterranean Horizons",
      "Historic Nations & Dynasties",
      "Lost Empires & Castles",
      "European Countryside Walks",
      "Scenic Rail & River Journeys"
    ];
  }
  if (c.includes("skyline") || g.includes("city") || g.includes("urban") || g.includes("places")) {
    return [
      "Skyline Diaries 4K",
      "Metropolitan Marvels",
      "Monuments of Heritage",
      "Spiritual Capitals & Ghats",
      "Ancient Forts & Palaces",
      "Coastal & Riverfront Skylines"
    ];
  }
  if (f === "relaxation" || g.startsWith("relax")) {
    return [
      "Majestic Alpine Sanctuaries",
      "Velvet Forest Whispers",
      "Tranquil Ocean Horizons",
      "Cozy Fireplace & Embers",
      "Biophilic Rain Retreats",
      "Kyoto Zen Temple Serenity",
      "Cascading Waterfall Glades",
      "Sacred Lotus Ponds"
    ];
  }
  if (f === "walking_tour" || g.includes("walking") || g.includes("tour")) {
    return [
      "Historic Old Town Strolls",
      "European Countryside Walks",
      "Alpine Mountain Trails",
      "Rainy Evening City Walks",
      "Cobblestone Village Paths"
    ];
  }
  if (g.includes("comedy") || f === "short") {
    return [
      "Urban Satire Chronicles",
      "Middle Class Melodramas",
      "Weekend Chaos Stories",
      "IT Office Quirks"
    ];
  }
  if (g.includes("dance") || f === "music_video") {
    return [
      "Folk Rhythms & Festive Beats",
      "Highland Dance Melodies",
      "Heritage Musical Journeys",
      "Sunset Melodic Waves"
    ];
  }
  return [
    "Chronicles of Civilizations",
    "Nations of the World",
    "Deep History & Dynasties",
    "Earth's Untamed Frontiers",
    "Lost Empires & Architecture",
    "Wildlife Expeditions & Wonders"
  ];
}

function setSeriesMode(mode) {
  activeSeriesMode = mode;
  const existBtn = document.getElementById("series-mode-existing-btn");
  const newBtn = document.getElementById("series-mode-new-btn");
  const existCont = document.getElementById("series-existing-container");
  const newCont = document.getElementById("series-new-container");

  if (existBtn) existBtn.classList.toggle("active", mode === "existing");
  if (newBtn) newBtn.classList.toggle("active", mode === "new");
  if (existCont) existCont.classList.toggle("hidden", mode !== "existing");
  if (newCont) newCont.classList.toggle("hidden", mode !== "new");

  if (mode === "existing") {
    const sel = document.getElementById("studio-existing-series-select");
    if (sel && sel.value) {
      onExistingSeriesSelect(sel.value);
    } else {
      const epCode = document.getElementById("studio-episode-code");
      if (epCode && !epCode.value) epCode.value = "EP-001";
    }
  } else {
    const pInput = document.getElementById("studio-production-name");
    const epCode = document.getElementById("studio-episode-code");
    if (pInput) {
      pInput.focus();
    }
    if (epCode && !epCode.value) epCode.value = "EP-001";
  }
}

let newSeriesDebounceTimer = null;
function onNewSeriesNameInput(val) {
  const epCode = document.getElementById("studio-episode-code");
  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "nature_rhythms";
  const fmtKey = (typeof activeStudioFormat !== "undefined" ? activeStudioFormat : "relaxation");
  const cleanName = (val || "").trim();
  if (!cleanName) {
    if (epCode) epCode.value = "EP-001";
    return;
  }
  clearTimeout(newSeriesDebounceTimer);
  newSeriesDebounceTimer = setTimeout(async () => {
    try {
      const res = await fetch(`/api/channels/${chSlug}/next-episode?format=${encodeURIComponent(fmtKey)}&production_name=${encodeURIComponent(cleanName)}`);
      const data = await res.json();
      if (data.status === "ok" && epCode) {
        epCode.value = data.next_episode_code || "EP-001";
      }
    } catch (e) {
      if (epCode && !epCode.value.trim()) epCode.value = "EP-001";
    }
  }, 250);
}

async function fetchAndPopulateExistingSeries(channelSlug, formatKey) {
  const sel = document.getElementById("studio-existing-series-select");
  if (!sel) return;

  const curated = getCuratedProductionPresets(channelSlug, formatKey);
  let existing = [];

  if (channelSlug && channelSlug !== "all") {
    try {
      const res = await fetch(`/api/channels/${channelSlug}/productions?format=${encodeURIComponent(formatKey)}`);
      const data = await res.json();
      if (data.status === "ok" && Array.isArray(data.productions) && data.productions.length > 0) {
        existing = data.productions;
        cachedExistingSeries = existing;
      } else {
        cachedExistingSeries = [];
      }
    } catch (err) {
      cachedExistingSeries = [];
    }
  }

  let html = "";
  if (existing.length > 0) {
    html += `<optgroup label="📁 Existing Productions on Disk">`;
    html += existing.map(p => `
      <option value="${p.slug}" data-name="${p.name}" data-next="${p.next_episode_code}">
        ${p.name} (${p.episodes_count} ep${p.episodes_count === 1 ? '' : 's'} • Next: ${p.next_episode_code})
      </option>
    `).join("");
    html += `</optgroup>`;
  }

  html += `<optgroup label="⭐ Curated Production Options">`;
  html += curated.map(name => {
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
    return `<option value="${slug}" data-name="${name}">${name}</option>`;
  }).join("");
  html += `</optgroup>`;
  html += `<option value="standalone" data-name="Standalone">🌿 Standalone (Single Episode)</option>`;

  sel.innerHTML = html;

  // Preserve current value or pick first
  const pInput = document.getElementById("studio-production-name");
  const currentVal = pInput?.value?.trim();
  const matchOpt = Array.from(sel.options).find(o => (o.getAttribute("data-name") || o.textContent.trim()) === currentVal || o.value === currentVal);

  if (matchOpt) {
    sel.value = matchOpt.value;
    onExistingSeriesSelect(matchOpt.value);
  } else if (existing.length > 0) {
    sel.value = existing[0].slug;
    onExistingSeriesSelect(existing[0].slug);
  } else if (curated.length > 0) {
    const firstSlug = curated[0].toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_+|_+$/g, '');
    sel.value = firstSlug;
    onExistingSeriesSelect(firstSlug);
  }
}

function onExistingSeriesSelect(seriesSlug) {
  const sel = document.getElementById("studio-existing-series-select");
  const p = cachedExistingSeries.find(x => x.slug === seriesSlug);
  const epCode = document.getElementById("studio-episode-code");
  const pInput = document.getElementById("studio-production-name");
  if (p) {
    if (epCode) epCode.value = p.next_episode_code || "EP-001";
    if (pInput) pInput.value = p.name;
  } else {
    const opt = sel?.selectedOptions?.[0];
    const cleanName = opt?.getAttribute("data-name") || opt?.textContent?.trim() || seriesSlug;
    if (pInput) pInput.value = cleanName;
    if (epCode && !epCode.value) epCode.value = "EP-001";
    if (cleanName && cleanName !== "Standalone") {
      onNewSeriesNameInput(cleanName);
    }
  }
}

function renderFormatChipsForActiveNetwork(channelSlug) {
  const container = document.getElementById("studio-format-chips-container");
  const countBadge = document.getElementById("studio-format-count-badge");
  if (!container) return;

  const p = (typeof cachedChannelProfiles !== "undefined" ? cachedChannelProfiles[channelSlug] : null) || (typeof studioChannelMetas !== "undefined" ? studioChannelMetas[channelSlug] : null);
  const allowed = p?.allowed_formats || p?.raw?.allowed_formats || ["relaxation", "documentary", "walking_tour", "music_video", "short"];

  if (countBadge) countBadge.textContent = `${allowed.length} Licensed Format${allowed.length === 1 ? '' : 's'}`;

  // If currently active format is not allowed, switch to first allowed
  if (!allowed.includes(activeStudioFormat)) {
    activeStudioFormat = allowed[0] || "relaxation";
  }

  container.innerHTML = allowed.map(fmtKey => {
    const meta = STUDIO_FORMAT_DEFINITIONS[fmtKey] || { label: fmtKey.replace(/_/g, " ").toUpperCase(), icon: "fa-film" };
    const isActive = (fmtKey === activeStudioFormat);
    return `
      <button type="button" onclick="selectStudioFormat('${fmtKey}')" id="fmt-pill-${fmtKey}" 
        class="format-chip-btn ${isActive ? 'active' : ''}">
        <i class="fa-solid ${meta.icon} text-[10px]"></i>
        <span>${meta.label}</span>
      </button>
    `;
  }).join("");

  const hiddenInput = document.getElementById("studio-active-format-val");
  if (hiddenInput) hiddenInput.value = activeStudioFormat;

  fetchAndPopulateExistingSeries(channelSlug, activeStudioFormat);
}

function selectStudioFormat(fmtKey, preserveGenre = null) {
  activeStudioFormat = fmtKey;
  const hiddenInput = document.getElementById("studio-active-format-val");
  if (hiddenInput) hiddenInput.value = fmtKey;

  // Update pills visual state
  document.querySelectorAll("#studio-format-chips-container button").forEach(btn => {
    btn.classList.remove("active");
  });
  const activeBtn = document.getElementById(`fmt-pill-${fmtKey}`);
  if (activeBtn) {
    activeBtn.classList.add("active");
  }

  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "nature_rhythms";
  if (fmtKey === "documentary" && typeof selectProductionTier === "function") {
    selectProductionTier("balanced");
  }

  // Automatically enforce 9:16 for Reels/Shorts and 16:9 for all other formats
  if (typeof setStudioFormat === "function") {
    if (fmtKey === "short" || fmtKey === "reels" || fmtKey === "shorts") {
      setStudioFormat("9:16");
    } else {
      setStudioFormat("16:9");
    }
  }

  // Show/Hide Country & Region/Language Shelf for Music Video format
  const countryShelf = document.getElementById("studio-country-language-shelf");
  if (countryShelf) {
    const isMusic = (fmtKey === "music_video");
    countryShelf.classList.toggle("hidden", !isMusic);
    if (isMusic) {
      initMusicCountryAndLanguageFromNetwork(chSlug);
    }
  }

  const archLbl = document.getElementById("studio-archetype-label");
  const archSubLbl = document.getElementById("studio-archetype-sublabel");
  if (archLbl) archLbl.textContent = (fmtKey === "music_video") ? "6. Background & Setting:" : "6. Archetype (Setting Template):";
  if (archSubLbl) archSubLbl.textContent = (fmtKey === "music_video") ? "Environment & Location" : "Template";

  fetchAndPopulateExistingSeries(chSlug, fmtKey);
  syncGenreDropdownOnly(chSlug, preserveGenre);
}

function syncGenreDropdownOnly(channelSlug, preserveGenre = null) {
  const gSelector = document.getElementById("studio-genre-selector");
  if (!gSelector) return;

  const genresDict = (typeof ALL_STUDIO_GENRES !== "undefined") ? ALL_STUDIO_GENRES : {};
  const channelGenres = (typeof DEFAULT_CHANNEL_GENRES !== "undefined") ? DEFAULT_CHANNEL_GENRES : {};

  const p = (typeof cachedChannelProfiles !== "undefined" ? cachedChannelProfiles[channelSlug] : null) || (typeof studioChannelMetas !== "undefined" ? studioChannelMetas[channelSlug] : null);
  const fallbackList = channelGenres[channelSlug] || [];
  const rawAllowed = p?.allowed_genres || p?.raw?.allowed_genres || [];
  const allowed = (rawAllowed.length >= fallbackList.length && rawAllowed.length > 2) ? rawAllowed : (fallbackList.length > 0 ? fallbackList : (rawAllowed.length > 0 ? rawAllowed : Object.keys(genresDict)));

  // Filter genres strictly matching the active format selected in Step 1
  let normalized = (allowed && allowed.length > 0 && channelSlug !== "all")
    ? allowed.map(g => g === "relax/scenic" ? "travel/scenic" : g).filter(g => Boolean(genresDict[g]))
    : Object.keys(genresDict);

  if (activeStudioFormat === "relaxation") {
    normalized = normalized.filter(g => g.startsWith("relax/") || g === "travel/scenic");
  } else if (activeStudioFormat === "documentary") {
    normalized = normalized.filter(g => g === "documentary" || g.includes("doc") || g === "science");
  } else if (activeStudioFormat === "walking_tour") {
    normalized = normalized.filter(g => g === "travel_walking");
  } else if (activeStudioFormat === "music_video") {
    normalized = normalized.filter(g => g.startsWith("dance/") || g.startsWith("music/"));
    if (normalized.length === 0) {
      normalized = ["music/static_vocal", "music/solo_singer", "music/duet_romance", "music/concert_live", "dance/folk", "music/mass_song"];
    }
  } else if (activeStudioFormat === "short" || activeStudioFormat === "movie") {
    normalized = normalized.filter(g => g.startsWith("comedy/") || g === "documentary" || g === "travel/scenic" || g === "science");
  }

  // Fallback if no specific format matches
  const genresToShow = normalized.length > 0 ? normalized : (activeStudioFormat === "documentary" ? ["documentary", "science"] : ["relax/nature"]);

  // Preserve user's selection if valid in the active format list
  const currentVal = preserveGenre || gSelector.value;
  const targetGenre = (currentVal && genresToShow.includes(currentVal)) ? currentVal : (genresToShow[0] || "relax/nature");

  gSelector.innerHTML = genresToShow.map(k => `<option value="${k}" ${k === targetGenre ? 'selected' : ''}>${genresDict[k] || k}</option>`).join("");
  gSelector.value = targetGenre;

  const subSelector = document.getElementById("studio-subgenre-selector");
  if (currentVal !== targetGenre || !subSelector || subSelector.options.length === 0) {
    onGenreChange(targetGenre);
  }
}

function syncGenreDropdownForChannel(channelSlug) {
  renderFormatChipsForActiveNetwork(channelSlug);
  syncGenreDropdownOnly(channelSlug);
  if (activeStudioFormat === "music_video") {
    initMusicCountryAndLanguageFromNetwork(channelSlug);
  }
}

function onStudioContinentChange(continentVal, preserveCountry = null, preserveSubRegion = null, preserveLang = null) {
  const cSelector = document.getElementById("studio-country-selector");
  if (!cSelector) return;
  const cMap = (typeof WORLD_CONTINENTS_REGIONS_MAP !== "undefined") ? WORLD_CONTINENTS_REGIONS_MAP : {};
  const list = cMap[continentVal] || cMap["Asia"] || [];

  const currentCountry = preserveCountry || cSelector.value;
  const targetCountry = (currentCountry && list.some(x => x.name === currentCountry)) ? currentCountry : (list[0]?.name || "India");

  cSelector.innerHTML = list.map(item => `
    <option value="${item.name}" ${item.name === targetCountry ? 'selected' : ''}>
      ${item.flag ? item.flag + ' ' : ''}${item.name}
    </option>
  `).join("");
  cSelector.value = targetCountry;

  onStudioCountryChange(targetCountry, preserveSubRegion, preserveLang);
}

function onStudioCountryChange(countryVal, preserveSubRegion = null, preserveLang = null) {
  const sSelector = document.getElementById("studio-subregion-selector");
  if (!sSelector) return;

  const rMap = (typeof WORLD_COUNTRY_REGIONS_MAP !== "undefined") ? WORLD_COUNTRY_REGIONS_MAP : {};
  const regions = rMap[countryVal];

  if (regions && regions.length > 0) {
    _renderSubRegions(regions, preserveSubRegion, preserveLang);
  } else {
    // Dynamic LLM curation fallback with Universal Artifact Disk Caching
    fetch(`/api/music-video/country-hierarchy?country=${encodeURIComponent(countryVal)}`)
      .then(r => r.json())
      .then(data => {
        if (data && Array.isArray(data.sub_regions) && data.sub_regions.length > 0) {
          rMap[countryVal] = data.sub_regions;
          _renderSubRegions(data.sub_regions, preserveSubRegion, preserveLang);
        } else {
          populateMusicCountryLanguages(countryVal, preserveLang);
        }
      })
      .catch(e => {
        console.warn("Country hierarchy fetch warning:", e);
        populateMusicCountryLanguages(countryVal, preserveLang);
      });
  }

  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "telugu_rhythms";
  fetchAndPopulateExistingSeries(chSlug, activeStudioFormat);
  if (activeStudioFormat === "music_video") {
    const gSelector = document.getElementById("studio-genre-selector");
    const subSelector = document.getElementById("studio-subgenre-selector");
    updateArchetypeOptions(gSelector ? gSelector.value : "music/duet_romance", subSelector ? subSelector.value : "");
  }
}

function _renderSubRegions(regions, preserveSubRegion = null, preserveLang = null) {
  const sSelector = document.getElementById("studio-subregion-selector");
  if (!sSelector) return;

  const currentSub = preserveSubRegion || sSelector.value;
  const targetSub = (currentSub && regions.some(x => x.id === currentSub)) ? currentSub : (regions[0]?.id || "");

  sSelector.innerHTML = regions.map(item => `
    <option value="${item.id}" data-culture="${item.culture || ''}" ${item.id === targetSub ? 'selected' : ''}>
      ${item.name}
    </option>
  `).join("");
  sSelector.value = targetSub;

  onStudioSubRegionChange(targetSub, preserveLang);
}

function onStudioSubRegionChange(subRegionId, preserveLang = null) {
  const cSelector = document.getElementById("studio-country-selector");
  const lSelector = document.getElementById("studio-region-language-selector");
  if (!lSelector) return;

  const countryVal = cSelector ? cSelector.value : "India";
  const rMap = (typeof WORLD_COUNTRY_REGIONS_MAP !== "undefined") ? WORLD_COUNTRY_REGIONS_MAP : {};
  const regions = rMap[countryVal] || [];
  const activeRegion = regions.find(x => x.id === subRegionId) || regions[0];

  const langs = (activeRegion && Array.isArray(activeRegion.languages) && activeRegion.languages.length > 0)
    ? activeRegion.languages
    : ((typeof STUDIO_COUNTRY_LANGUAGE_MAP !== "undefined" && STUDIO_COUNTRY_LANGUAGE_MAP[countryVal]) || []);

  const currentLang = preserveLang || lSelector.value;
  const targetLang = (currentLang && langs.some(x => x.code === currentLang)) ? currentLang : (langs[0]?.code || "te");

  lSelector.innerHTML = langs.map(item => `
    <option value="${item.code}" data-culture="${item.culture || activeRegion?.culture || 'western'}" data-script="${item.script || 'Latin'}" ${item.code === targetLang ? 'selected' : ''}>
      ${item.name}
    </option>
  `).join("");
  lSelector.value = targetLang;

  onStudioLanguageChange(targetLang);
}

function populateMusicCountryLanguages(countryVal, preserveLang = null) {
  const lSelector = document.getElementById("studio-region-language-selector");
  if (!lSelector) return;
  const map = (typeof STUDIO_COUNTRY_LANGUAGE_MAP !== "undefined") ? STUDIO_COUNTRY_LANGUAGE_MAP : {};
  const list = map[countryVal] || map["India"] || [];

  const currentLang = preserveLang || lSelector.value;
  const targetLang = (currentLang && list.some(x => x.code === currentLang)) ? currentLang : (list[0]?.code || "te");

  lSelector.innerHTML = list.map(item => `
    <option value="${item.code}" data-culture="${item.culture}" data-script="${item.script}" ${item.code === targetLang ? 'selected' : ''}>
      ${item.name}
    </option>
  `).join("");
  lSelector.value = targetLang;
}

function onStudioLanguageChange(langVal) {
  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "telugu_rhythms";
  fetchAndPopulateExistingSeries(chSlug, activeStudioFormat);
  if (typeof calculateLiveCostEstimate === "function") {
    calculateLiveCostEstimate();
  }
}

function initMusicCountryAndLanguageFromNetwork(channelSlug) {
  const contSelector = document.getElementById("studio-continent-selector");
  const cSelector = document.getElementById("studio-country-selector");
  const sSelector = document.getElementById("studio-subregion-selector");
  const lSelector = document.getElementById("studio-region-language-selector");
  if (!contSelector || !cSelector || !sSelector || !lSelector) return;

  const slug = String(channelSlug || "").toLowerCase();
  let defaultContinent = "Asia";
  let defaultCountry = "India";
  let defaultSubRegion = "south_india";
  let defaultLang = "te";

  if (slug.includes("japan") || slug.includes("tokyo")) {
    defaultContinent = "Asia"; defaultCountry = "Japan"; defaultSubRegion = "kanto_tokyo"; defaultLang = "ja";
  } else if (slug.includes("france") || slug.includes("paris")) {
    defaultContinent = "Europe"; defaultCountry = "France"; defaultSubRegion = "paris_ile_de_france"; defaultLang = "fr";
  } else if (slug.includes("spain") || slug.includes("flamenco")) {
    defaultContinent = "Europe"; defaultCountry = "Spain"; defaultSubRegion = "andalusia"; defaultLang = "es";
  } else if (slug.includes("korea") || slug.includes("seoul") || slug.includes("kpop")) {
    defaultContinent = "Asia"; defaultCountry = "South Korea"; defaultSubRegion = "nationwide"; defaultLang = "ko";
  } else if (slug.includes("us") || slug.includes("america") || slug.includes("english")) {
    defaultContinent = "North America"; defaultCountry = "United States"; defaultSubRegion = "american_south"; defaultLang = "en";
  } else if (slug.includes("uk") || slug.includes("scotland") || slug.includes("celtic") || slug.includes("british")) {
    defaultContinent = "Europe"; defaultCountry = "United Kingdom"; defaultSubRegion = "scotland"; defaultLang = "gd";
  } else if (slug.includes("tamil") || slug.includes("kollywood")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "south_india"; defaultLang = "ta";
  } else if (slug.includes("kannada") || slug.includes("sandalwood")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "south_india"; defaultLang = "kn";
  } else if (slug.includes("malayalam") || slug.includes("mollywood")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "south_india"; defaultLang = "ml";
  } else if (slug.includes("hindi") || slug.includes("bollywood")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "north_india"; defaultLang = "hi";
  } else if (slug.includes("punjabi") || slug.includes("bhangra")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "north_india"; defaultLang = "pa";
  } else if (slug.includes("kashmiri")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "north_india"; defaultLang = "ks";
  } else if (slug.includes("urdu") || slug.includes("ghazal")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "north_india"; defaultLang = "ur";
  } else if (slug.includes("bengali") || slug.includes("baul")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "east_india"; defaultLang = "bn";
  } else if (slug.includes("odia") || slug.includes("odissi") || slug.includes("sambalpuri")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "east_india"; defaultLang = "or";
  } else if (slug.includes("assamese") || slug.includes("bihu")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "east_india"; defaultLang = "as";
  } else if (slug.includes("marathi") || slug.includes("lavani")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "west_india"; defaultLang = "mr";
  } else if (slug.includes("gujarati") || slug.includes("garba")) {
    defaultContinent = "Asia"; defaultCountry = "India"; defaultSubRegion = "west_india"; defaultLang = "gu";
  }

  contSelector.value = defaultContinent;
  onStudioContinentChange(defaultContinent, defaultCountry, defaultSubRegion, defaultLang);
}


function onGenreChange(genreVal, preserveSubGenre = null, preserveArch = null) {
  const subSelector = document.getElementById("studio-subgenre-selector");
  if (!subSelector) return;

  const subMap = (typeof STUDIO_SUBOPTIONS_MAP !== "undefined") ? STUDIO_SUBOPTIONS_MAP : {};
  const list = subMap[genreVal] || subMap["relax/nature"] || [];

  const currentSub = preserveSubGenre || subSelector.value;
  const targetSub = (currentSub && list.some(x => x.val === currentSub)) ? currentSub : (list[0]?.val || "");

  subSelector.innerHTML = list.map(item => `<option value="${item.val}" ${item.val === targetSub ? 'selected' : ''}>${item.label}</option>`).join("");
  subSelector.value = targetSub;
  
  updateArchetypeOptions(genreVal, targetSub, preserveArch);
  onSubGenreChange(targetSub);

  // Sync active channel audio defaults & stem modality
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  const voiceToggle = document.getElementById("studio-toggle-voice-over");
  const ttsToggle = document.getElementById("studio-toggle-tts");
  const fallbackToggle = document.getElementById("studio-toggle-fallback");
  const dualToggle = document.getElementById("studio-toggle-dual-editions");
  const dualRow = document.getElementById("studio-dual-editions-row");
  const dualLabel = document.getElementById("studio-dual-editions-label");

  const isDoc = (activeStudioFormat === "documentary" || genreVal === "documentary" || genreVal === "science" || genreVal === "doc/nations" || genreVal === "nations");
  const isRelax = (activeStudioFormat === "relaxation" || activeStudioFormat === "relax" || genreVal.startsWith("relax") || !activeStudioFormat);

  if (isDoc) {
    if (bgmToggle) { bgmToggle.checked = true; bgmToggle.disabled = false; }
    if (voiceToggle) { voiceToggle.checked = true; voiceToggle.disabled = false; }
    if (ttsToggle) { ttsToggle.disabled = false; }
    if (fallbackToggle) { fallbackToggle.disabled = false; }
    if (dualRow) dualRow.classList.remove("hidden");
    if (dualToggle) { dualToggle.checked = true; dualToggle.disabled = false; }
    if (dualLabel) dualLabel.textContent = "Dual Masters (Narration + Music)";
  } else if (isRelax) {
    // Relaxation: Dual Masters (Music Edition + Pure Nature ASMR Edition)
    if (bgmToggle) { bgmToggle.disabled = false; bgmToggle.checked = (genreVal !== "relax/hearth"); }
    if (voiceToggle) { voiceToggle.checked = false; voiceToggle.disabled = true; }
    if (ttsToggle) { ttsToggle.checked = false; ttsToggle.disabled = true; }
    if (fallbackToggle) { fallbackToggle.checked = false; fallbackToggle.disabled = true; }
    if (dualRow) dualRow.classList.remove("hidden");
    if (dualToggle) { dualToggle.checked = true; dualToggle.disabled = false; }
    if (dualLabel) dualLabel.textContent = "Dual Masters (Music + Nature)";
  } else {
    // Non-documentary, non-relaxation
    if (bgmToggle) { bgmToggle.disabled = false; bgmToggle.checked = true; }
    if (voiceToggle) { voiceToggle.checked = false; voiceToggle.disabled = true; }
    if (ttsToggle) { ttsToggle.checked = false; ttsToggle.disabled = true; }
    if (fallbackToggle) { fallbackToggle.checked = false; fallbackToggle.disabled = true; }
    if (dualRow) dualRow.classList.add("hidden");
    if (dualToggle) { dualToggle.checked = false; dualToggle.disabled = true; }
  }

  if (typeof syncTravelShotUI === "function") {
    syncTravelShotUI();
  }
  if (typeof calculateLiveCostEstimate === "function") {
    calculateLiveCostEstimate();
  }
  const chSlug = (typeof selectedStudioChannel !== "undefined" && selectedStudioChannel) ? selectedStudioChannel : "nature_rhythms";
  fetchAndPopulateExistingSeries(chSlug, activeStudioFormat);
}

function syncDualMastersVisibility() {
  const row = document.getElementById("studio-dual-editions-row");
  if (!row) return;
  const gSelector = document.getElementById("studio-genre-selector");
  const genreVal = gSelector ? gSelector.value : "";
  const isDoc = (activeStudioFormat === "documentary" || genreVal === "documentary" || genreVal === "science" || genreVal === "doc/nations" || genreVal === "nations");
  const isRelax = (activeStudioFormat === "relaxation" || activeStudioFormat === "relax" || genreVal.startsWith("relax") || !activeStudioFormat);
  row.classList.toggle("hidden", !(isDoc || isRelax));
  const dualLabel = document.getElementById("studio-dual-editions-label");
  if (dualLabel) {
    dualLabel.textContent = isDoc ? "Dual Masters (Narration + Music)" : "Dual Masters (Music + Nature)";
  }
}

function updateArchetypeOptions(genreVal, subGenreVal, preserveArch = null) {
  const archSelector = document.getElementById("studio-archetype-selector");
  if (!archSelector) return;

  const archMap = (typeof STUDIO_ARCHETYPES_MAP !== "undefined") ? STUDIO_ARCHETYPES_MAP : {};
  let list = [];

  const isMusic = (activeStudioFormat === "music_video" || (genreVal && (genreVal.startsWith("music/") || genreVal.startsWith("dance/"))));
  if (isMusic) {
    list = (typeof MUSIC_VIDEO_BACKGROUND_ARCHETYPES !== "undefined")
      ? MUSIC_VIDEO_BACKGROUND_ARCHETYPES
      : (archMap["music_video"] || archMap[genreVal] || []);
  } else if (genreVal === "documentary") {
    if (subGenreVal === "travel_itinerary_tour" || subGenreVal === "doc_places") {
      list = archMap["documentary:tour"] || [];
    } else {
      list = archMap["documentary"] || [];
    }
  } else if (genreVal === "doc/nations" || genreVal === "nations") {
    list = archMap["doc/nations"] || [];
  } else if (genreVal === "science") {
    list = archMap["science:" + subGenreVal] || archMap["science"] || [];
  } else if (archMap[genreVal + ":" + subGenreVal]) {
    list = archMap[genreVal + ":" + subGenreVal] || [];
  } else {
    list = archMap[genreVal] || archMap["relax/nature"] || [];
  }

  const countryVal = document.getElementById("studio-country-selector")?.value || "";
  const countryDef = (typeof COUNTRY_MUSIC_BACKGROUND_DEFAULTS !== "undefined") ? COUNTRY_MUSIC_BACKGROUND_DEFAULTS[countryVal] : null;

  let smartDefault = null;
  if (isMusic) {
    if (subGenreVal === "jugalbandi" || (genreVal && genreVal.includes("jugalbandi"))) {
      smartDefault = "concert_hall_stage";
    } else if (subGenreVal === "mass_beats" || (genreVal && genreVal.includes("mass"))) {
      smartDefault = "village_jathara_square";
    } else if (countryDef && list.some(x => x.val === countryDef)) {
      smartDefault = countryDef;
    }
  }

  const currentArch = preserveArch || archSelector.value;
  const targetArch = (currentArch && list.some(x => x.val === currentArch))
    ? currentArch
    : (smartDefault && list.some(x => x.val === smartDefault)
      ? smartDefault
      : (genreVal === "documentary" && subGenreVal === "doc_architecture" && list.some(x => x.val === "ancient_civilizations_history")
        ? "ancient_civilizations_history"
        : (genreVal === "documentary" && subGenreVal === "travel_itinerary_tour" && list.some(x => x.val === "itinerary_map_tour")
          ? "itinerary_map_tour"
          : (subGenreVal && (subGenreVal.includes("bedroom") || subGenreVal.includes("cabin")) && list.find(x => x.val.includes("bedroom") || x.val.includes("cabin"))?.val) || list[0]?.val || "")));

  archSelector.innerHTML = list.map(item => `<option value="${item.val}" ${item.val === targetArch ? 'selected' : ''}>${item.label}</option>`).join("");
  archSelector.value = targetArch;
  onArchetypeChange(archSelector.value);
}

function onSubGenreChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const gSelector = document.getElementById("studio-genre-selector");
  const genreVal = gSelector ? gSelector.value : "relax/nature";
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  
  const placeholders = (typeof STUDIO_SUBGENRE_PLACEHOLDERS !== "undefined") ? STUDIO_SUBGENRE_PLACEHOLDERS : {};
  if (promptInput && placeholders[val]) promptInput.placeholder = placeholders[val];

  updateArchetypeOptions(genreVal, val);

  // Audio configuration defaults based on sub-genre without overriding selected channel
  if (val === "cozy_hearth" || val === "stone_hearth") {
    if (bgmToggle && !bgmToggle.disabled) bgmToggle.checked = false;
  }
}

function onWeatherChange(weatherVal) {
  const labels = ["normal", "rain", "snow", "fog", "sunset", "night"];
  labels.forEach(w => {
    const lbl = document.getElementById(`weather-lbl-${w}`);
    if (lbl) {
      if (w === weatherVal) {
        lbl.className = "flex items-center justify-center gap-1 py-1 px-1.5 bg-[var(--card)] rounded-md border-2 border-[var(--accent)] cursor-pointer text-[var(--text)]";
      } else {
        lbl.className = "flex items-center justify-center gap-1 py-1 px-1.5 bg-[var(--card)] rounded-md border border-[var(--border)] cursor-pointer hover:border-[var(--accent)] text-[var(--text)]";
      }
    }
  });

  const promptInput = document.getElementById("youtube-prompt-input");
  if (promptInput && !promptInput.value.trim()) {
    const weatherPhrases = {
      rain: " (with gentle cinematic rainfall, mist plumes & petrichor ASMR)",
      snow: " (with serene snowfall, frosted evergreens & winter wind)",
      fog: " (with morning valley mist, volumetric god rays & soft haze)",
      sunset: " (at golden hour sunset, warm alpenglow & long purple shadows)",
      night: " (under starlit midnight sky, brilliant Milky Way & celestial peace)",
      normal: ""
    };
    if (weatherPhrases[weatherVal]) {
      const origPlaceholder = promptInput.placeholder.replace(/ \(with.*?\)/, "").replace(/ \(at.*?\)/, "").replace(/ \(under.*?\)/, "");
      promptInput.placeholder = origPlaceholder + weatherPhrases[weatherVal];
    }
  }
}

function onArchetypeChange(val) {
  const promptInput = document.getElementById("youtube-prompt-input");
  const hints = (typeof STUDIO_ARCHETYPE_HINTS !== "undefined") ? STUDIO_ARCHETYPE_HINTS : {};
  if (promptInput && hints[val]) promptInput.placeholder = hints[val];
}

function applyGenreNichePreset() {
  const gSelector = document.getElementById("studio-genre-selector");
  if (gSelector) {
    gSelector.value = "relax/nature";
    onGenreChange("relax/nature");
  }
  const cadRadios = document.querySelectorAll("input[name='studio_shot_hold']");
  cadRadios.forEach(r => { r.checked = (r.value === "3m"); });
}

async function fetchAndRenderChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  if (!container) return;

  try {
    const res = await fetch("/api/channels/episodes");
    const data = await res.json();
    if (data.status === "ok" && Array.isArray(data.episodes)) {
      channelArchiveEpisodes = data.episodes;
    }
  } catch (e) {
    console.warn("Could not fetch channel archive:", e);
  }

  filterChannelArchive();
}

let selectedArchiveFormat = "all";

function setArchiveFormatFilter(fmt) {
  selectedArchiveFormat = fmt || "all";
  renderArchiveFormatPills();
  filterChannelArchive();
}

function renderArchiveFormatPills() {
  const container = document.getElementById("archive-format-pills");
  if (!container) return;

  const ch = typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "all";
  const rawList = [
    ...(typeof studioVideos !== "undefined" && Array.isArray(studioVideos) ? studioVideos : []),
    ...(typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes) ? channelArchiveEpisodes : [])
  ];

  const seenKeys = new Set();
  const formatCounts = { all: 0 };
  rawList.forEach(ep => {
    const cId = (ep.channel_id || ep.channelId || "earth_serenade").toLowerCase().trim();
    if (ch !== "all" && cId !== ch.toLowerCase().trim()) return;
    const rawEId = String(ep.episode_id || ep.id || "").trim().toUpperCase();
    const fmt = String(ep.format || ep.format_slug || "relaxation").toLowerCase().trim();
    const prod = String(ep.production_name || "standalone").toLowerCase().trim().replace(/\s+/g, "_");
    const key = `${cId}_${fmt}_${prod}_${rawEId}`;
    if (seenKeys.has(key)) return;
    seenKeys.add(key);

    formatCounts.all = (formatCounts.all || 0) + 1;
    formatCounts[fmt] = (formatCounts[fmt] || 0) + 1;
  });

  const formatMeta = {
    all: { label: "All", icon: "fa-border-all" },
    relaxation: { label: "🌿 Relaxation", icon: "fa-leaf" },
    documentary: { label: "🎬 Documentary", icon: "fa-film" },
    travel_walking: { label: "🚶 Walking Tour", icon: "fa-person-walking" },
    dance_musical: { label: "💃 Dance / Song", icon: "fa-music" },
    nature_retreat: { label: "🌲 Retreat", icon: "fa-tree" },
    ambient_world: { label: "🌌 Ambient", icon: "fa-moon" }
  };

  const availableFormats = ["all", ...Object.keys(formatCounts).filter(f => f !== "all" && formatCounts[f] > 0)];

  container.innerHTML = availableFormats.map(fmt => {
    const isAct = (selectedArchiveFormat === fmt);
    const meta = formatMeta[fmt] || { label: fmt.charAt(0).toUpperCase() + fmt.slice(1), icon: "fa-tag" };
    const cnt = formatCounts[fmt] || 0;
    const btnCls = isAct
      ? "bg-indigo-600 text-white font-bold shadow-sm ring-1 ring-indigo-400"
      : "bg-slate-100 dark:bg-slate-800/80 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-gray-300 font-medium";
    return `<button type="button" onclick="setArchiveFormatFilter('${fmt}')" class="px-2 py-0.5 rounded-full text-[9px] shrink-0 transition flex items-center gap-1 ${btnCls}"><span>${meta.label}</span><span class="opacity-75 font-mono text-[8px]">(${cnt})</span></button>`;
  }).join("");
}

function filterChannelArchive() {
  const container = document.getElementById("channel-archive-list-container");
  const badgeCount = document.getElementById("channel-archive-badge-count");
  if (!container) return;

  renderArchiveFormatPills();

  const search = (document.getElementById("archive-filter-search")?.value || "").toLowerCase().trim();
  const ch = typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "all";

  const allMap = new Map();
  if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
    studioVideos.forEach(v => {
      const cId = (v.channelId || v.channel_id || "earth_serenade").toLowerCase().trim();
      const rawEId = (v.id || v.episode_id || "").trim();
      const normEId = rawEId ? rawEId.toUpperCase() : "EP-001";
      const fmt = String(v.format_slug || v.format || "relaxation").toLowerCase().trim();
      const prod = String(v.production_name || "standalone").toLowerCase().trim().replace(/\s+/g, "_");
      const key = `${cId}_${fmt}_${prod}_${normEId}`;
      allMap.set(key, {
        episode_id: normEId, channel_id: cId, format: fmt, format_slug: fmt,
        production_name: v.production_name || v.user_inputs?.production_name || null,
        title: v.title, story_topic: v.concept || v.story_topic || v.title,
        cost_usd: v.cost || v.cost_usd || 0.14, status: v.status || "completed",
        is_approved: Boolean(v.is_approved || v.approved),
        progress: v.progress || (v.status === "completed" ? 100 : (v.status === "processing" ? 50 : 15)),
        videoUrl: v.videoUrl || v.video_url, keyframes: v.keyframes || [], motion_clips: v.motion_clips || [], audio_stems: v.audio_stems || [],
        created_timestamp: Number(v.created_timestamp || (v.createdAt ? v.createdAt / 1000 : 0) || 0)
      });
    });
  }

  channelArchiveEpisodes.forEach(ep => {
    const cId = (ep.channel_id || "earth_serenade").toLowerCase().trim();
    const rawEId = (ep.episode_id || ep.id || "").trim();
    const normEId = rawEId ? rawEId.toUpperCase() : "EP-001";
    const fmt = String(ep.format || ep.format_slug || "relaxation").toLowerCase().trim();
    const prod = String(ep.production_name || "standalone").toLowerCase().trim().replace(/\s+/g, "_");
    const key = `${cId}_${fmt}_${prod}_${normEId}`;
    if (!allMap.has(key)) {
      allMap.set(key, {
        ...ep, episode_id: normEId, channel_id: cId, format: fmt, format_slug: fmt,
        production_name: ep.production_name || "standalone",
        is_approved: Boolean(ep.is_approved || ep.approved), status: "completed", progress: 100,
        created_timestamp: Number(ep.created_timestamp || ep.updated_timestamp || 0)
      });
    } else {
      const ex = allMap.get(key);
      if (ep.production_name && (!ex.production_name || ex.production_name === "standalone")) ex.production_name = ep.production_name;
      if (ep.is_approved || ep.approved) ex.is_approved = true;
      if (ep.keyframes && ep.keyframes.length > 0 && (!ex.keyframes || ex.keyframes.length === 0)) ex.keyframes = ep.keyframes;
      if (ep.motion_clips && ep.motion_clips.length > 0 && (!ex.motion_clips || ex.motion_clips.length === 0)) ex.motion_clips = ep.motion_clips;
      if (ep.audio_stems && ep.audio_stems.length > 0 && (!ex.audio_stems || ex.audio_stems.length === 0)) ex.audio_stems = ep.audio_stems;
      if (ep.video_url && !ex.videoUrl) ex.videoUrl = ep.video_url;
      if (ep.created_timestamp && !ex.created_timestamp) ex.created_timestamp = Number(ep.created_timestamp);
    }
  });

  const allEpisodes = Array.from(allMap.values());
  const filtered = allEpisodes.filter(ep => {
    if (ch !== "all" && ep.channel_id !== ch) return false;
    if (selectedArchiveFormat && selectedArchiveFormat !== "all") {
      const epFmt = String(ep.format || ep.format_slug || "").toLowerCase().trim();
      if (epFmt && epFmt !== selectedArchiveFormat.toLowerCase().trim()) return false;
    }
    if (search) {
      const match = [ep.title, ep.episode_id, ep.story_topic, ep.production_name, ep.format].some(s => (s || "").toLowerCase().includes(search));
      if (!match) return false;
    }
    return true;
  });

  // Sort descending: newest created / updated on top
  filtered.sort((a, b) => {
    const tA = Number(a.created_timestamp || (a.createdAt ? a.createdAt / 1000 : 0) || 0);
    const tB = Number(b.created_timestamp || (b.createdAt ? b.createdAt / 1000 : 0) || 0);
    return tB - tA;
  });

  if (badgeCount) badgeCount.textContent = filtered.length;

  if (filtered.length === 0) {
    container.innerHTML = `<div class="p-6 text-center text-xs text-gray-500 bg-slate-50 dark:bg-slate-950/40 rounded-xl border border-dashed border-[var(--border)]">No productions found for this format filter.</div>`;
    return;
  }

  const activeEpisode = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  const activeEpId = activeEpisode ? String(activeEpisode.id || activeEpisode.episode_id || "").trim().toUpperCase() : null;
  const activeChannelId = activeEpisode ? String(activeEpisode.channelId || activeEpisode.channel_id || "").trim().toLowerCase() : null;
  const activeFmt = activeEpisode ? String(activeEpisode.format || activeEpisode.format_slug || "").trim().toLowerCase() : null;
  const activeProd = activeEpisode ? String(activeEpisode.production_name || "").trim().toLowerCase().replace(/\s+/g, "_") : null;

  container.innerHTML = filtered.map(ep => {
    const curEpId = String(ep.episode_id || ep.id || "").trim().toUpperCase();
    const curChId = String(ep.channel_id || ep.channelId || "").trim().toLowerCase();
    const curFmt = String(ep.format || ep.format_slug || "").trim().toLowerCase();
    const curProd = String(ep.production_name || "").trim().toLowerCase().replace(/\s+/g, "_");

    const isSel = Boolean(activeEpId && curEpId === activeEpId && (!activeChannelId || curChId === activeChannelId) && (!activeFmt || curFmt === activeFmt) && (!activeProd || curProd === activeProd));
    const isProc = (ep.status === "processing" || ep.status === "queued");
    const isApp = Boolean(ep.is_approved || ep.approved);
    const bCls = isSel ? "border-2 border-indigo-500 bg-indigo-50/60 dark:bg-indigo-950/40 ring-1 ring-indigo-500/30" : "border border-slate-200 dark:border-slate-800 hover:border-indigo-400 bg-slate-50 dark:bg-slate-950/80";
    const badge = isProc ? `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-blue-500/15 text-blue-700 dark:text-blue-400 border border-blue-500/30 font-bold animate-pulse"><i class="fa-solid fa-spinner fa-spin mr-0.5"></i> In Progress</span>` : (isApp ? `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-500/15 text-emerald-700 dark:text-emerald-400 border border-emerald-500/30 font-bold">✓ Approved</span>` : `<span class="text-[8px] font-mono px-1.5 py-0.2 rounded-full bg-amber-500/15 text-amber-700 dark:text-amber-400 border border-amber-500/30 font-bold">⏳ Unapproved</span>`);
    const pBar = isProc ? `<div class="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden mt-1"><div class="h-full bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full transition-all duration-300" style="width: ${ep.progress || 45}%"></div></div>` : "";
    const prodName = ep.production_name ? ep.production_name.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase()) : "Standalone";
    const geminiTitle = ep.title || ep.story_topic || "Untitled Episode";
    const storyDesc = ep.story_topic && ep.story_topic !== ep.title ? ep.story_topic : "";
    const fmtBadge = ep.format ? `<span class="px-1.5 py-0.2 rounded text-[7px] font-mono uppercase bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800">${ep.format}</span>` : "";

    return `
      <div onclick="selectArchiveEpisode('${ep.episode_id}', '${ep.channel_id}', '${ep.format || ''}', '${ep.production_name || ''}')" class="p-2.5 ${bCls} rounded-xl cursor-pointer transition space-y-1.5 group relative">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-1.5 overflow-hidden">
            <span class="font-mono font-bold text-xs text-indigo-600 dark:text-indigo-400 shrink-0">${ep.episode_id}</span>
            <span class="text-[11px] font-bold text-slate-800 dark:text-slate-200 truncate" title="${prodName}"><i class="fa-solid fa-film text-[9px] text-slate-400 mr-1"></i>${prodName}</span>
            ${fmtBadge}
          </div>
          <div class="flex items-center gap-1 shrink-0">
            ${badge}
            <button type="button" onclick="event.stopPropagation(); deleteStudioEpisode('${ep.episode_id}', event, '${ep.channel_id}', '${ep.format || ''}', '${ep.production_name || ''}', '${ep.storage_path || ''}', '${(ep.title || '').replace(/'/g, "\\'")}');" class="p-1 text-slate-400 hover:text-red-600 rounded transition" title="Delete Episode"><i class="fa-solid fa-trash-can text-[10px]"></i></button>
          </div>
        </div>
        <div>
          <div class="font-semibold text-indigo-600 dark:text-indigo-300 text-xs group-hover:underline truncate" title="${geminiTitle}">${geminiTitle}</div>
          ${storyDesc ? `<div class="text-[10px] text-slate-500 dark:text-gray-400 line-clamp-1">${storyDesc}</div>` : ''}
        </div>
        ${pBar}
      </div>`;
  }).join("");
}

async function approveCurrentEpisode() {
  if (!currentActiveInspectorEpisode) return;
  const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
  if (!epId || epId === "NEW") return;
  const uEmail = (typeof currentUser !== "undefined" && currentUser.email) ? currentUser.email : "knpillutla@gmail.com";
  const chSlug = currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id || ((typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all") ? selectedStudioChannel : "earth_serenade");

  const btn = document.getElementById("btn-studio-approve");
  const btnTxt = document.getElementById("btn-studio-approve-text");
  if (btn) btn.disabled = true;
  if (btnTxt) btnTxt.textContent = "Approving...";

  try {
    const res = await fetch(`/api/production/episodes/${epId}/approve?channel_id=${chSlug}&user_id=${encodeURIComponent(uEmail)}`, { method: "POST" });
    const data = await res.json();
    if (data.success) {
      currentActiveInspectorEpisode.is_approved = true;
      currentActiveInspectorEpisode.approved = true;
      if (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) {
        const v = findStudioEpisodeById(epId, chSlug);
        if (v) { v.is_approved = true; v.approved = true; }
      }
      const archEp = channelArchiveEpisodes.find(x => x.episode_id === epId && x.channel_id === chSlug);
      if (archEp) { archEp.is_approved = true; archEp.approved = true; }
      if (typeof saveVideosState === "function") saveVideosState();
      if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(currentActiveInspectorEpisode);
      filterChannelArchive();
      if (typeof showProfileStatusToast === "function") showProfileStatusToast(`✓ Episode ${epId} approved successfully!`);
    }
  } catch (e) {
    console.error("Approve episode error:", e);
    if (btn) btn.disabled = false;
    if (btnTxt) btnTxt.textContent = "Approve Master Video";
  }
}

function selectArchiveEpisode(epId, chId, formatSlug, prodName) {
  const normEpId = String(epId || "").trim().toUpperCase();
  const ch = chId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "all");
  const normCh = String(ch || "").trim().toLowerCase();
  const normFmt = String(formatSlug || "").trim().toLowerCase();
  const normProd = String(prodName || "").trim().toLowerCase().replace(/\s+/g, "_");

  const matchFn = x => {
    if (!x) return false;
    const curId = String(x.id || x.episode_id || "").trim().toUpperCase();
    if (curId !== normEpId) return false;
    const curCh = String(x.channelId || x.channel_id || "").trim().toLowerCase();
    if (normCh !== "all" && curCh && curCh !== normCh) return false;
    if (normFmt) {
      const curFmt = String(x.format || x.format_slug || "").trim().toLowerCase();
      if (curFmt && !curFmt.includes(normFmt) && !normFmt.includes(curFmt)) return false;
    }
    if (normProd) {
      const curProd = String(x.production_name || "").trim().toLowerCase().replace(/\s+/g, "_");
      if (curProd && curProd !== normProd) return false;
    }
    return true;
  };

  let ep = (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) ? studioVideos.find(matchFn) : null;
  if (!ep && typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
    ep = channelArchiveEpisodes.find(matchFn);
  }
  if (!ep) {
    const looseMatch = x => {
      if (!x || String(x.id || x.episode_id || "").trim().toUpperCase() !== normEpId) return false;
      if (normCh !== "all" && String(x.channelId || x.channel_id || "").trim().toLowerCase() !== normCh) return false;
      if (normFmt) {
        const curFmt = String(x.format || x.format_slug || "").trim().toLowerCase();
        if (curFmt && !curFmt.includes(normFmt) && !normFmt.includes(curFmt)) return false;
      }
      return true;
    };
    ep = (typeof studioVideos !== "undefined" && Array.isArray(studioVideos)) ? studioVideos.find(looseMatch) : null;
    if (!ep && typeof channelArchiveEpisodes !== "undefined" && Array.isArray(channelArchiveEpisodes)) {
      ep = channelArchiveEpisodes.find(looseMatch);
    }
  }
  if (!ep) return;

  // Sanitize cross-format artifact bleed
  const epFmt = String(ep.format || ep.format_slug || normFmt || "").toLowerCase();
  if (epFmt && Array.isArray(ep.keyframes)) {
    ep.keyframes = ep.keyframes.filter(kf => {
      const u = String(typeof kf === "object" ? kf.url : kf || "");
      if (u.includes("/relaxation/") && epFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && epFmt.includes("relaxation")) return false;
      return true;
    });
  }
  if (epFmt && Array.isArray(ep.motion_clips)) {
    ep.motion_clips = ep.motion_clips.filter(mc => {
      const u = String(typeof mc === "object" ? mc.url : mc || "");
      if (u.includes("/relaxation/") && epFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && epFmt.includes("relaxation")) return false;
      return true;
    });
  }
  if (epFmt && Array.isArray(ep.audio_stems)) {
    ep.audio_stems = ep.audio_stems.filter(as => {
      const u = String(typeof as === "object" ? as.url : as || "");
      if (u.includes("/relaxation/") && epFmt.includes("documentary")) return false;
      if (u.includes("/documentary/") && epFmt.includes("relaxation")) return false;
      return true;
    });
  }

  // Set active inspector episode immediately
  currentActiveInspectorEpisode = ep;

  // Switch channel quietly if different without triggering destructive form resets
  const targetChannel = ep.channelId || ep.channel_id;
  if (targetChannel && typeof selectedStudioChannel !== "undefined" && selectedStudioChannel !== "all" && selectedStudioChannel !== targetChannel) {
    selectedStudioChannel = targetChannel;
    if (typeof updateStudioChannelBadge === "function") updateStudioChannelBadge();
  }

  if (typeof renderInspectorFromVideo === "function") renderInspectorFromVideo(ep);
  if (window.StudioBus) window.StudioBus.emit("episode:selected", ep);
  filterChannelArchive();
}

function deleteStudioEpisode(epId, event, channelId, formatSlug, productionName, storagePath, title) {
  if (event) event.stopPropagation();
  if (typeof promptDeleteEpisode === "function") {
    promptDeleteEpisode(epId, channelId, formatSlug, productionName, storagePath, title);
  }
}

function deleteActiveInspectorEpisode() {
  if (typeof currentActiveInspectorEpisode !== "undefined" && currentActiveInspectorEpisode) {
    const epId = currentActiveInspectorEpisode.id || currentActiveInspectorEpisode.episode_id;
    const chSlug = currentActiveInspectorEpisode.channelId || currentActiveInspectorEpisode.channel_id;
    const fmt = currentActiveInspectorEpisode.format || currentActiveInspectorEpisode.format_slug;
    const prod = currentActiveInspectorEpisode.production_name;
    const path = currentActiveInspectorEpisode.storage_path || currentActiveInspectorEpisode.storagePath;
    const ttl = currentActiveInspectorEpisode.title || currentActiveInspectorEpisode.story_topic;
    if (epId && epId !== "NEW") {
      deleteStudioEpisode(epId, null, chSlug, fmt, prod, path, ttl);
    }
  }
}

if (window.StudioBus) {
  window.StudioBus.on("channel:changed", () => {
    if (activeCreationTab === "archive") filterChannelArchive();
  });
}
