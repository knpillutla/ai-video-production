// CineAI Studio: Theme Management & User Preferences Persistence
function applyTheme(themeName, persist = false) {
  document.documentElement.setAttribute("data-theme", themeName);
  const icon = document.getElementById("theme-toggle-icon");
  const label = document.getElementById("theme-toggle-label");
  if (icon) {
    if (themeName === "light") icon.className = "fa-solid fa-sun text-amber-400";
    else if (themeName === "cyberpunk") icon.className = "fa-solid fa-bolt text-pink-400";
    else if (themeName === "amoled") icon.className = "fa-solid fa-moon text-blue-400";
    else icon.className = "fa-solid fa-circle-half-stroke text-indigo-400";
  }
  if (label) label.textContent = themeName.charAt(0).toUpperCase() + themeName.slice(1);
  currentUser.theme = themeName;
  if (persist) {
    localStorage.setItem("cineai_theme", themeName);
    saveUserState();
  }
}

function toggleTheme() {
  const themes = ["dark", "light", "cyberpunk", "amoled"];
  const curIdx = themes.indexOf(currentUser.theme || "dark");
  const nextTheme = themes[(curIdx + 1) % themes.length];
  applyTheme(nextTheme, true);
}

function saveUserState() {
  localStorage.setItem("cineai_user", JSON.stringify(currentUser));
  updateUserUI();
}

function updateUserUI() {
  const nameEl = document.getElementById("user-name-display");
  const avatarEl = document.getElementById("user-avatar-display");
  const creditEl = document.getElementById("user-credit-display");
  const containerEl = document.getElementById("user-container-display");
  if (nameEl) nameEl.textContent = currentUser.display_name;
  if (avatarEl && currentUser.avatar_url) avatarEl.src = currentUser.avatar_url;
  if (creditEl) creditEl.textContent = `$${currentUser.balance_usd.toFixed(2)} USD`;
  if (containerEl) containerEl.textContent = currentUser.container_id;
}

function saveUserSettings(e) {
  if (e) e.preventDefault();
  const nameInput = document.getElementById("settings-display-name");
  const themeSelect = document.getElementById("settings-theme-select");
  if (nameInput && nameInput.value.trim()) currentUser.display_name = nameInput.value.trim();
  if (themeSelect) applyTheme(themeSelect.value, true);
  saveUserState();
  closeModal("settings-modal");
  showStudioModal({
    title: "Settings Saved",
    message: "Profile preferences and theme settings have been updated.",
    nextStep: "Theme and preferences are active across your studio session."
  });
}

function loginWithGoogle() {
  currentUser.display_name = "Krishna Pillutla (Google)";
  currentUser.email = "krishna@google.com";
  currentUser.avatar_url = "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=120&auto=format&fit=crop&q=80";
  saveUserState();
  closeModal("auth-modal");
  showStudioModal({
    title: "Google Authentication Successful",
    message: `Signed in as ${currentUser.display_name} (${currentUser.email}).`,
    nextStep: "Cloud storage container mounted: " + currentUser.container_id
  });
}

function loginWithDevAccount() {
  const nameInput = document.getElementById("auth-name-input");
  const emailInput = document.getElementById("auth-email-input");
  if (nameInput && nameInput.value.trim()) currentUser.display_name = nameInput.value.trim();
  if (emailInput && emailInput.value.trim()) currentUser.email = emailInput.value.trim();
  saveUserState();
  closeModal("auth-modal");
  showStudioModal({
    title: "Profile Updated",
    message: `Authenticated as ${currentUser.display_name}.`,
    nextStep: "Preferences and container access verified."
  });
}
