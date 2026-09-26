// CineAI Studio: User Preference Profiles & Presets Controller
const PREFERENCES_STORAGE_KEY = "cineai_user_preferences_v1";

const STUDIO_DEFAULT_PRESETS = {
  id: "presets",
  name: "Presets (Studio Default)",
  format: "16:9",
  pureNature: false,
  bgm: true,
  voiceOver: true,
  tts: false,
  lipsync: false,
  duration: "10",
  stretchHours: "0",
  fps: "24",
  language: "en",
  tier: "balanced",
  nicheRadio: null
};

function getUserPreferencesList() {
  try {
    const raw = localStorage.getItem(PREFERENCES_STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    console.error("Error reading preferences:", e);
    return [];
  }
}

function saveUserPreferencesList(list) {
  try {
    localStorage.setItem(PREFERENCES_STORAGE_KEY, JSON.stringify(list));
  } catch (e) {
    console.error("Error saving preferences:", e);
  }
}

function captureCurrentStudioSettings() {
  const getChk = id => document.getElementById(id)?.checked || false;
  const getVal = (id, def) => document.getElementById(id)?.value || def;
  const nicheRadio = document.querySelector("input[name='niche_theme_radio']:checked")?.value || null;

  return {
    format: getVal("studio-selected-format", "16:9"),
    pureNature: getChk("studio-toggle-pure-nature"),
    bgm: getChk("studio-toggle-bgm"),
    voiceOver: getChk("studio-toggle-voice-over"),
    tts: getChk("studio-toggle-tts"),
    lipsync: getChk("studio-toggle-lipsync"),
    duration: getVal("studio-duration", "10"),
    stretchHours: getVal("studio-stretch-hours", "0"),
    fps: getVal("studio-fps", "24"),
    language: getVal("studio-language", "en"),
    tier: typeof currentTier !== "undefined" ? currentTier : "balanced",
    nicheRadio: nicheRadio
  };
}

function applySettingsToStudio(settings) {
  const setChk = (id, val) => { const el = document.getElementById(id); if (el) el.checked = !!val; };
  const setVal = (id, val) => { const el = document.getElementById(id); if (el && val !== undefined) el.value = val; };

  if (typeof setStudioFormat === "function" && settings.format) {
    setStudioFormat(settings.format);
  }

  setChk("studio-toggle-pure-nature", settings.pureNature);
  setChk("studio-toggle-bgm", settings.bgm);
  setChk("studio-toggle-voice-over", settings.voiceOver);
  setChk("studio-toggle-tts", settings.tts);
  setChk("studio-toggle-lipsync", settings.lipsync);

  setVal("studio-duration", settings.duration || "10");
  setVal("studio-stretch-hours", settings.stretchHours || "0");
  setVal("studio-fps", settings.fps || "24");
  setVal("studio-language", settings.language || "en");

  if (typeof selectProductionTier === "function" && settings.tier) {
    selectProductionTier(settings.tier);
  }

  if (settings.nicheRadio) {
    const r = document.querySelector(`input[name='niche_theme_radio'][value='${settings.nicheRadio}']`);
    if (r) r.checked = true;
  } else {
    document.querySelectorAll("input[name='niche_theme_radio']").forEach(r => r.checked = false);
  }

  if (typeof togglePureNatureMode === "function") {
    togglePureNatureMode(!!settings.pureNature);
  }
}

function populateProfileDropdown() {
  const sel = document.getElementById("studio-profile-selector");
  if (!sel) return;

  const prefs = getUserPreferencesList();
  let html = `<option value="presets">⚡ Presets (Studio Default)</option>`;

  if (prefs.length > 0) {
    html += `<optgroup label="My Preferences (${prefs.length})">`;
    prefs.forEach(p => {
      const defBadge = p.isDefault ? " ⭐ (Default on Login)" : "";
      html += `<option value="${p.id}">${p.name}${defBadge}</option>`;
    });
    html += `</optgroup>`;
  }

  sel.innerHTML = html;
}

function onProfileSelectChange(val) {
  if (val === "presets") {
    resetToStudioPresets();
  } else {
    const prefs = getUserPreferencesList();
    const p = prefs.find(x => x.id === val);
    if (p) {
      applySettingsToStudio(p);
      showProfileStatusToast(`Applied preference: "${p.name}"`);
    }
  }
}

function resetToStudioPresets() {
  applySettingsToStudio(STUDIO_DEFAULT_PRESETS);
  const sel = document.getElementById("studio-profile-selector");
  if (sel) sel.value = "presets";
  showProfileStatusToast("Reset all controls to Studio Presets.");
}

function openSavePreferenceModal() {
  const current = captureCurrentStudioSettings();
  const summaryEl = document.getElementById("pref-snapshot-summary");
  if (summaryEl) {
    summaryEl.textContent = `Format: ${current.format} • Dur: ${current.duration}s • Stretch: ${current.stretchHours}h • FPS: ${current.fps} • Lang: ${current.language} • Tier: ${current.tier} • Audio: ${current.pureNature ? 'Pure Nature' : (current.bgm ? 'BGM' : 'No BGM')}`;
  }

  const nameInput = document.getElementById("pref-profile-name");
  if (nameInput) {
    nameInput.value = "";
    nameInput.placeholder = "e.g. My 8h Nature ASMR Setup";
  }

  const chk = document.getElementById("pref-is-default");
  if (chk) chk.checked = false;

  renderSavedProfilesManagerList();
  openModal("preference-modal");
}

function handleSavePreferenceForm(e) {
  e.preventDefault();
  const nameInput = document.getElementById("pref-profile-name");
  const isDefaultChk = document.getElementById("pref-is-default");
  const name = (nameInput?.value || "").trim();
  if (!name) return;

  const current = captureCurrentStudioSettings();
  const isDefault = isDefaultChk?.checked || false;

  let list = getUserPreferencesList();
  if (isDefault) {
    list.forEach(p => p.isDefault = false);
  }

  const newProfile = {
    id: "pref_" + Date.now().toString(36) + "_" + Math.random().toString(36).slice(2, 5),
    name,
    isDefault,
    createdAt: new Date().toLocaleDateString(),
    ...current
  };

  list.unshift(newProfile);
  saveUserPreferencesList(list);
  populateProfileDropdown();

  const sel = document.getElementById("studio-profile-selector");
  if (sel) sel.value = newProfile.id;

  closeModal("preference-modal");
  showStudioModal({
    title: "Preference Saved",
    message: `Preference profile "${name}" has been saved successfully!${isDefault ? ' (Set as Default on Login)' : ''}`,
    nextStep: "You can switch between Studio Presets and your preferences anytime from the dropdown."
  });
}

function renderSavedProfilesManagerList() {
  const container = document.getElementById("pref-saved-list");
  const countEl = document.getElementById("pref-saved-count");
  if (!container) return;

  const list = getUserPreferencesList();
  if (countEl) countEl.textContent = `${list.length} Profiles`;

  if (list.length === 0) {
    container.innerHTML = `<div class="p-3 text-center text-slate-500 dark:text-gray-400 text-xs">No custom preferences saved yet.</div>`;
    return;
  }

  container.innerHTML = list.map(p => `
    <div class="flex items-center justify-between p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg text-xs">
      <div class="flex items-center gap-2">
        <span class="font-bold text-slate-900 dark:text-white">${p.name}</span>
        ${p.isDefault ? '<span class="px-1.5 py-0.2 bg-indigo-100 dark:bg-indigo-900/60 text-indigo-700 dark:text-indigo-300 rounded text-[9px] font-bold">⭐ Default on Login</span>' : ''}
      </div>
      <div class="flex items-center gap-1.5">
        ${!p.isDefault ? `<button type="button" onclick="setDefaultPreference('${p.id}')" class="px-2 py-0.5 text-[10px] bg-slate-100 dark:bg-slate-800 hover:bg-indigo-100 text-slate-700 dark:text-gray-300 rounded font-bold" title="Set as default on login">Make Default</button>` : ''}
        <button type="button" onclick="deletePreferenceProfile('${p.id}')" class="p-1 text-red-500 hover:text-red-700 text-xs" title="Delete preference"><i class="fa-solid fa-trash-can"></i></button>
      </div>
    </div>
  `).join("");
}

function setDefaultPreference(id) {
  const list = getUserPreferencesList();
  list.forEach(p => { p.isDefault = (p.id === id); });
  saveUserPreferencesList(list);
  populateProfileDropdown();
  renderSavedProfilesManagerList();
}

function deletePreferenceProfile(id) {
  let list = getUserPreferencesList();
  list = list.filter(p => p.id !== id);
  saveUserPreferencesList(list);
  populateProfileDropdown();
  renderSavedProfilesManagerList();
}

function showProfileStatusToast(msg) {
  const el = document.getElementById("studio-profile-status-toast");
  if (!el) return;
  el.textContent = msg;
  el.classList.remove("opacity-0");
  setTimeout(() => el.classList.add("opacity-0"), 2500);
}

function initUserPreferencesOnStartup() {
  populateProfileDropdown();
  const list = getUserPreferencesList();
  const defaultPref = list.find(p => p.isDefault);
  if (defaultPref) {
    applySettingsToStudio(defaultPref);
    const sel = document.getElementById("studio-profile-selector");
    if (sel) sel.value = defaultPref.id;
  } else {
    resetToStudioPresets();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  setTimeout(initUserPreferencesOnStartup, 100);
});
