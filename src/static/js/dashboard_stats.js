// CineAI Studio: Executive Dashboard Aggregator
function renderDashboardStats() {
  const totalVideos = studioVideos.length;
  const queuedVideos = studioVideos.filter(v => v.status === "queued" || v.status === "processing").length;
  const totalCost = studioVideos.reduce((acc, v) => acc + (v.cost || 0), 0);

  const totalEl = document.getElementById("stat-total-videos");
  const queuedEl = document.getElementById("stat-queued-count");
  const costEl = document.getElementById("stat-compute-cost");

  if (totalEl) totalEl.textContent = totalVideos;
  if (queuedEl) queuedEl.textContent = queuedVideos;
  if (costEl) costEl.textContent = `$${totalCost.toFixed(2)}`;
}
