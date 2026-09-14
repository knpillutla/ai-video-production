// CineAI Studio: Bootstrapper & Lifecycle Manager
document.addEventListener("DOMContentLoaded", () => {
  try {
    const saved = localStorage.getItem("cineai_user");
    if (saved) {
      currentUser = Object.assign(currentUser, JSON.parse(saved));
    }
    const savedTheme = localStorage.getItem("cineai_theme") || currentUser.theme || "dark";
    applyTheme(savedTheme, false);
  } catch (e) {
    console.warn("Storage initialization warning:", e);
  }

  updateUserUI();
  selectProductionTier("balanced");

  if (typeof renderStudioVideoHistory === "function") {
    renderStudioVideoHistory();
  }
  if (typeof renderAppsCatalog === "function") {
    renderAppsCatalog();
  }
  if (typeof renderDashboardStats === "function") {
    renderDashboardStats();
  }

  // Default to studio tab
  switchTab("studio");
});
