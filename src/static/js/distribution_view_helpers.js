// CineAI Studio: Distribution View UI Helper Utilities
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

  let badgeCls = "bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 border-indigo-500/20";
  if (color === "rose") badgeCls = "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20";
  if (color === "emerald") badgeCls = "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20";

  c.innerHTML = tags.map(t => `
    <span class="text-[9px] font-mono px-1.5 py-0.5 rounded-md border ${badgeCls} inline-flex items-center gap-0.5">
      ${t.startsWith('#') ? '' : '#'}${t}
    </span>
  `).join("");
}

function copyTextToClipboard(text, toastMsg) {
  if (!text) return;
  navigator.clipboard.writeText(text);
  if (typeof showToast === "function") showToast(toastMsg || "Copied to clipboard!", "success");
}
