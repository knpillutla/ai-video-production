// CineAI Studio: Prompt Creation Modes, Placeholders & Template Card Interactions
const MODE_CONFIG = {
  theme: {
    labelHtml: '<i class="fa-solid fa-compass text-[var(--text-muted)] text-xs"></i> <span>Theme / Topic Description (Optional):</span>',
    sublabel: "World Cities, Nature, Mountains, Oceans & Architecture",
    ph: "Optional example: A quiet rainforest stream beneath an old-growth canopy...",
    hint: "Theme active • World Cities, Villages, Mountains, Oceans & Architecture"
  },
  idea: {
    labelHtml: '<i class="fa-solid fa-lightbulb text-[var(--text-muted)] text-xs"></i> <span>Story Idea / Concept (Optional):</span>',
    sublabel: "Character arcs, satirical situations, narrative premise",
    ph: "Optional: Describe story concept, characters, comedic angle, or leave empty...",
    hint: "Idea active • Narrative concepts, characters & comedy"
  },
  script: {
    labelHtml: '<i class="fa-solid fa-scroll text-[var(--text-muted)] text-xs"></i> <span>Script / Screenplay (Optional):</span>',
    sublabel: "Full scene screenplay, voiceover narration, dialogue beats",
    ph: "Optional: Paste screenplay, dialogue lines, or leave empty...",
    hint: "Script active • Full screenplay, scene beats or dialogue stems"
  },
  youtube: {
    labelHtml: '<i class="fa-brands fa-youtube text-red-500 text-xs"></i> <span>Reference Adaptation Styling (Optional):</span>',
    sublabel: "Styling directions, camera motion, cinematic treatment",
    ph: "Optional: Enter styling directions to apply from reference video...",
    hint: "YouTube Reference active • Paste video link & prompt to apply reference styling"
  }
};

function clearTemplateCardHighlights() {
  document.querySelectorAll("[id^='creative-card-']").forEach(c => c.classList.remove("ring-2", "ring-indigo-500"));
}

function renderTemplatesForMode(mode) {
  const container = document.getElementById("creative-templates-container");
  if (!container) return;
  const templates = (typeof TEMPLATES_BY_MODE !== "undefined" && TEMPLATES_BY_MODE[mode]) ? TEMPLATES_BY_MODE[mode] : [];
  const titleEl = document.getElementById("creative-presets-title");
  if (titleEl) titleEl.textContent = mode === "theme" ? "Theme Presets (Nature, Wildlife, Heritage, Travel)" : "Creative Templates";

  container.innerHTML = templates.map((t, idx) => `
    <div id="creative-card-${t.id}" onclick="applyTemplate('${mode}', ${idx})" class="p-3 bg-[var(--card)] hover:bg-[var(--card-hover)] border border-[var(--border)] rounded-xl cursor-pointer transition space-y-1 group active:scale-95 shadow-sm">
      <div class="flex items-center justify-between">
        <span class="text-xs font-bold px-2 py-0.5 rounded bg-[var(--card-subtle)] text-[var(--text)] border border-[var(--border)]">${t.badge}</span>
        <i class="fa-solid fa-arrow-up-right-from-square text-[10px] text-[var(--text-muted)] group-hover:text-[var(--text)]"></i>
      </div>
      <div class="font-bold text-[var(--text)] text-xs">${t.title}</div>
      <div class="text-xs text-[var(--text-muted)] leading-tight">${t.desc}</div>
    </div>`).join("");
}

function applyTemplate(mode, idxOrObj) {
  const list = (typeof TEMPLATES_BY_MODE !== "undefined" && TEMPLATES_BY_MODE[mode]) ? TEMPLATES_BY_MODE[mode] : [];
  const t = typeof idxOrObj === "number" ? list[idxOrObj] : idxOrObj;
  if (!t) return;
  const pInput = document.getElementById("youtube-prompt-input"), uInput = document.getElementById("youtube-url-input");
  if (mode === "youtube") { if (uInput) { uInput.value = t.url || ""; flashPromptInput(uInput); } } else if (uInput) { uInput.value = ""; }
  if (pInput) { pInput.value = t.prompt; flashPromptInput(pInput); }
  clearTemplateCardHighlights();
  document.getElementById("creative-card-" + t.id)?.classList.add("ring-2", "ring-[var(--accent)]");
}

function setCreationMode(mode, autoPopulate = false) {
  currentCreationMode = mode;
  ["theme", "idea", "script", "youtube"].forEach(m => {
    const btn = document.getElementById("mode-pill-" + m);
    if (btn) btn.classList.toggle("active", m === mode);
  });

  const textarea = document.getElementById("youtube-prompt-input"), urlInput = document.getElementById("youtube-url-input");
  const urlContainer = document.getElementById("youtube-url-container"), genreShelf = document.getElementById("theme-genre-shelf");
  const hint = document.getElementById("creation-mode-hint"), labelEl = document.getElementById("prompt-input-label"), sublabelEl = document.getElementById("prompt-input-sublabel");
  const cfg = MODE_CONFIG[mode] || MODE_CONFIG.theme;

  if (labelEl && cfg.labelHtml) labelEl.innerHTML = cfg.labelHtml;
  if (sublabelEl && cfg.sublabel) sublabelEl.textContent = cfg.sublabel;
  if (textarea) { textarea.placeholder = cfg.ph; if (hint) hint.textContent = cfg.hint; }
  if (genreShelf) genreShelf.classList.toggle("hidden", mode !== "theme");
  if (urlContainer) {
    urlContainer.classList.toggle("hidden", mode !== "youtube");
    if (mode !== "youtube" && urlInput) urlInput.value = "";
  }
  renderTemplatesForMode(mode);
}

function flashPromptInput(el) {
  if (!el) return;
  el.classList.add("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40");
  setTimeout(() => el.classList.remove("ring-2", "ring-indigo-500", "border-indigo-400", "bg-indigo-950/40"), 1000);
}

