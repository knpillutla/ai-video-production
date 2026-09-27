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
  
  const isSignedIn = currentUser && currentUser.isSignedIn !== false && Boolean(currentUser.email);

  if (nameEl) nameEl.textContent = isSignedIn ? (currentUser.display_name || "Krishna P.") : "Sign In";
  if (avatarEl) {
    if (isSignedIn) {
      if (avatarEl.tagName === "IMG" && currentUser.avatar_url) avatarEl.src = currentUser.avatar_url;
      else if (currentUser.display_name) avatarEl.textContent = currentUser.display_name.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
    } else {
      avatarEl.textContent = "👤";
    }
  }
  if (creditEl) creditEl.textContent = `$${(currentUser.balance_usd || 100.0).toFixed(2)} USD`;
  if (containerEl) containerEl.textContent = currentUser.container_id || "storage/user-knpillutla-gmail-com";
}

function openAuthOrProfileModal() {
  const isSignedIn = currentUser && currentUser.isSignedIn !== false && Boolean(currentUser.email);
  const viewSignedIn = document.getElementById("auth-view-signed-in");
  const viewSignedOut = document.getElementById("auth-view-signed-out");
  const modalTitle = document.getElementById("auth-modal-title");

  if (isSignedIn) {
    if (viewSignedIn) viewSignedIn.classList.remove("hidden");
    if (viewSignedOut) viewSignedOut.classList.add("hidden");
    if (modalTitle) modalTitle.textContent = "Google Account Profile";

    const nameInput = document.getElementById("auth-name-input");
    const emailInput = document.getElementById("auth-email-input");
    const nameText = document.getElementById("profile-display-name-text");
    const avatarLg = document.getElementById("profile-avatar-large");
    const containerBadge = document.getElementById("profile-container-badge");

    const effEmail = currentUser.email || "knpillutla@gmail.com";
    const effName = currentUser.display_name || "Krishna Pillutla";

    if (nameInput) nameInput.value = effName;
    if (emailInput) emailInput.value = effEmail;
    if (nameText) nameText.textContent = effName;
    if (avatarLg) avatarLg.textContent = effName.split(" ").map(n => n[0]).join("").slice(0, 2).toUpperCase();
    if (containerBadge) containerBadge.textContent = currentUser.container_id || "storage/user-knpillutla-gmail-com";
  } else {
    if (viewSignedIn) viewSignedIn.classList.add("hidden");
    if (viewSignedOut) viewSignedOut.classList.remove("hidden");
    if (modalTitle) modalTitle.textContent = "Sign in to CineAI Studio";
  }

  openModal("auth-modal");
}

function saveSignedProfileName() {
  const nameInput = document.getElementById("auth-name-input");
  if (nameInput && nameInput.value.trim()) {
    currentUser.display_name = nameInput.value.trim();
    saveUserState();
    closeModal("auth-modal");
    if (typeof showProfileStatusToast === "function") {
      showProfileStatusToast("Profile Updated: " + currentUser.display_name);
    }
  }
}

function signOutUser() {
  currentUser.isSignedIn = false;
  currentUser.display_name = "Guest User";
  currentUser.email = "";
  currentUser.container_id = "guest";
  saveUserState();
  
  const viewSignedIn = document.getElementById("auth-view-signed-in");
  const viewSignedOut = document.getElementById("auth-view-signed-out");
  const modalTitle = document.getElementById("auth-modal-title");
  if (viewSignedIn) viewSignedIn.classList.add("hidden");
  if (viewSignedOut) viewSignedOut.classList.remove("hidden");
  if (modalTitle) modalTitle.textContent = "Sign in to CineAI Studio";

  updateUserUI();
  if (typeof switchTab === "function") switchTab("studio");
  if (typeof showProfileStatusToast === "function") {
    showProfileStatusToast("Signed out successfully. Return to sign in.");
  }
}

function loginWithGoogle() {
  currentUser.isSignedIn = true;
  currentUser.display_name = "Krishna Pillutla";
  currentUser.email = "knpillutla@gmail.com";
  currentUser.avatar_url = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80";
  currentUser.container_id = "user-knpillutla-gmail-com";
  currentUser.balance_usd = 100.0;
  saveUserState();
  closeModal("auth-modal");
  
  if (typeof fetchChannelHubVideos === "function") fetchChannelHubVideos();
  if (typeof syncChannelEpisodesFromBackend === "function") syncChannelEpisodesFromBackend();

  showStudioModal({
    title: "Google Authentication Successful",
    message: `Signed in as ${currentUser.display_name} (${currentUser.email}).`,
    nextStep: "Private cloud storage container mounted: " + currentUser.container_id
  });
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

let isSidebarPinned = true;

function toggleSidebarPin() {
  const sidebar = document.getElementById("app-sidebar");
  const pinIcon = document.getElementById("sidebar-pin-icon");
  const collapseIcon = document.getElementById("sidebar-collapse-icon");
  if (!sidebar) return;

  isSidebarPinned = !isSidebarPinned;
  localStorage.setItem("cineai_sidebar_pinned", isSidebarPinned ? "true" : "false");

  if (isSidebarPinned) {
    sidebar.classList.remove("unpinned", "collapsed", "hover-expanded");
    if (pinIcon) {
      pinIcon.className = "fa-solid fa-thumbtack text-[10px] text-indigo-400 rotate-0";
      pinIcon.parentElement.title = "Unpin Sidebar";
    }
    if (collapseIcon) collapseIcon.className = "fa-solid fa-angles-left text-[10px] text-indigo-400";
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Sidebar Pinned");
  } else {
    sidebar.classList.add("unpinned", "collapsed");
    if (pinIcon) {
      pinIcon.className = "fa-solid fa-thumbtack text-[10px] text-slate-400 -rotate-45";
      pinIcon.parentElement.title = "Pin Sidebar";
    }
    if (collapseIcon) collapseIcon.className = "fa-solid fa-angles-right text-[10px] text-indigo-400";
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Sidebar Unpinned");
  }
}

function toggleSidebarCollapse() {
  const sidebar = document.getElementById("app-sidebar");
  const collapseIcon = document.getElementById("sidebar-collapse-icon");
  if (!sidebar) return;
  const isCollapsed = sidebar.classList.toggle("collapsed");
  if (collapseIcon) {
    collapseIcon.className = isCollapsed ? "fa-solid fa-angles-right text-[10px] text-indigo-400" : "fa-solid fa-angles-left text-[10px] text-indigo-400";
  }
  localStorage.setItem("cineai_sidebar_collapsed", isCollapsed ? "true" : "false");
}

function setupSidebarHoverPeek() {
  const sidebar = document.getElementById("app-sidebar");
  if (!sidebar) return;
  sidebar.addEventListener("mouseenter", () => {
    if (!isSidebarPinned && sidebar.classList.contains("collapsed")) sidebar.classList.add("hover-expanded");
  });
  sidebar.addEventListener("mouseleave", () => {
    if (!isSidebarPinned) sidebar.classList.remove("hover-expanded");
  });
}

function initSidebarState() {
  const savedPin = localStorage.getItem("cineai_sidebar_pinned");
  isSidebarPinned = savedPin === null ? true : savedPin === "true";
  const savedCollapsed = localStorage.getItem("cineai_sidebar_collapsed") === "true";

  const sidebar = document.getElementById("app-sidebar");
  const pinIcon = document.getElementById("sidebar-pin-icon");
  const collapseIcon = document.getElementById("sidebar-collapse-icon");

  if (sidebar) {
    if (!isSidebarPinned) {
      sidebar.classList.add("unpinned", "collapsed");
      if (pinIcon) {
        pinIcon.className = "fa-solid fa-thumbtack text-[10px] text-slate-400 -rotate-45";
        pinIcon.parentElement.title = "Pin Sidebar";
      }
      if (collapseIcon) collapseIcon.className = "fa-solid fa-angles-right text-[10px] text-indigo-400";
    } else if (savedCollapsed) {
      sidebar.classList.add("collapsed");
      if (collapseIcon) collapseIcon.className = "fa-solid fa-angles-right text-[10px] text-indigo-400";
    }
  }

  setupSidebarHoverPeek();
}

document.addEventListener("DOMContentLoaded", () => {
  initSidebarState();
});
