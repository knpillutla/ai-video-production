// CineAI Studio: Bootstrapper & Lifecycle Manager
document.addEventListener("DOMContentLoaded", () => {
  try {
    const saved = localStorage.getItem("cineai_user");
    if (saved) {
      currentUser = Object.assign(currentUser, JSON.parse(saved));
      if (!currentUser.email || currentUser.email.includes("creator@")) {
        currentUser.email = "knpillutla@gmail.com";
        currentUser.display_name = "Krishna Pillutla";
        currentUser.container_id = "user-knpillutla-gmail-com";
        currentUser.isSignedIn = true;
        localStorage.setItem("cineai_user", JSON.stringify(currentUser));
      }
    }
    const savedTheme = localStorage.getItem("cineai_theme") || currentUser.theme || "dark";
    applyTheme(savedTheme, false);
  } catch (e) {
    console.warn("Storage initialization warning:", e);
  }

  updateUserUI();
  selectProductionTier("cinematic");
  if (typeof setExecutionMode === "function") {
    setExecutionMode("test");
  }

  if (typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  }
  if (typeof renderAppsCatalog === "function") {
    renderAppsCatalog();
  }
  if (typeof renderDashboardStats === "function") {
    renderDashboardStats();
  }
  if (typeof renderEmptyInspectorState === "function") {
    renderEmptyInspectorState();
  }

  if (typeof fetchUserChannels === "function") {
    fetchUserChannels();
  }

  if (typeof syncChannelEpisodesFromBackend === "function") {
    syncChannelEpisodesFromBackend();
  }

  if (typeof updateDurationOptionsForNiche === "function") {
    updateDurationOptionsForNiche("relaxation");
  }

  // Default to studio tab
  switchTab("studio");
});
