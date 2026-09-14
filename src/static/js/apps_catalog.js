// CineAI Studio: Runway Apps Gallery Controller
const APPS_CATALOG = [
  {
    id: "app-edit-studio",
    title: "Edit Studio",
    badge: "NEW",
    category: "social",
    desc: "Use Aleph 2.0 to edit videos with natural language. Preview before you generate.",
    img: "https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=400&auto=format&fit=crop&q=80",
    format: "Shorts (9:16)",
    style: "Cinematic Photoreal"
  },
  {
    id: "app-ad-localization",
    title: "Ad Localization",
    badge: null,
    category: "marketing",
    desc: "Content localization. Upload an ad image, type in language, get a new video ad.",
    img: "https://images.unsplash.com/photo-1533750516457-a7f992034fec?w=400&auto=format&fit=crop&q=80",
    format: "Shorts (9:16)",
    style: "Commercial Polish"
  },
  {
    id: "app-expand-image",
    title: "Expand Image",
    badge: null,
    category: "social",
    desc: "Change your image's aspect ratio dynamically for 9:16 vertical reels.",
    img: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=400&auto=format&fit=crop&q=80",
    format: "Shorts (9:16)",
    style: "Photoreal 4K"
  },
  {
    id: "app-lip-sync",
    title: "Multilingual Lip Sync",
    badge: null,
    category: "social",
    desc: "Azure Neural TTS voice alignment with realistic facial movement in Telugu & Hindi.",
    img: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&auto=format&fit=crop&q=80",
    format: "Web Series (16:9)",
    style: "Cinematic Photoreal"
  },
  {
    id: "app-film-scenes",
    title: "Narrative Scenes",
    badge: "HOT",
    category: "film",
    desc: "Generate multi-character dramatic dialog scenes with cinematic lighting.",
    img: "https://images.unsplash.com/photo-1485846234645-a62644f84728?w=400&auto=format&fit=crop&q=80",
    format: "Web Series (16:9)",
    style: "Cinematic Photoreal"
  },
  {
    id: "app-animation-story",
    title: "Story Explainer",
    badge: null,
    category: "educational",
    desc: "Engaging educational narratives with 3D Pixar animation and isometric diagrams.",
    img: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=400&auto=format&fit=crop&q=80",
    format: "Documentary (16:9)",
    style: "3D Pixar Animation"
  }
];

let selectedCategory = "social";

function selectAppCategory(catKey) {
  selectedCategory = catKey;
  const categories = ["film", "marketing", "social", "educational", "experimental"];
  categories.forEach(c => {
    const card = document.getElementById("cat-card-" + c);
    if (!card) return;
    if (c === catKey) {
      card.className = "p-3 bg-indigo-600/20 border-2 border-indigo-500 rounded-xl cursor-pointer transition flex items-center gap-3";
    } else {
      card.className = "p-3 bg-slate-900/60 hover:bg-slate-800/80 border border-[var(--border)] rounded-xl cursor-pointer transition flex items-center gap-3";
    }
  });
  const titles = {
    film: "Film or shorts",
    marketing: "Marketing",
    social: "Social",
    educational: "Educational content",
    experimental: "Experimental art"
  };
  const titleEl = document.getElementById("apps-category-title");
  if (titleEl) titleEl.textContent = titles[catKey] || catKey;
  renderAppsCatalog();
}

function filterAppsCatalog() {
  renderAppsCatalog();
}

function renderAppsCatalog() {
  const container = document.getElementById("apps-grid-container");
  if (!container) return;
  const query = (document.getElementById("apps-search-input")?.value || "").toLowerCase();
  const items = APPS_CATALOG.filter(app => {
    const matchCat = (selectedCategory === "all" || app.category === selectedCategory || query.length > 0);
    const matchQuery = !query || app.title.toLowerCase().includes(query) || app.desc.toLowerCase().includes(query);
    return matchCat && matchQuery;
  });

  if (items.length === 0) {
    container.innerHTML = '<div class="col-span-3 text-center py-12 text-gray-500 text-xs">No apps found matching your query.</div>';
    return;
  }

  container.innerHTML = items.map(app => `
    <div onclick="launchApp('${app.id}')" class="group bg-slate-900/90 border border-[var(--border)] hover:border-indigo-500/80 rounded-2xl overflow-hidden cursor-pointer transition shadow-md hover:shadow-indigo-500/10 flex flex-col">
      <div class="h-36 overflow-hidden relative bg-slate-950">
        <img src="${app.img}" alt="${app.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-300">
        ${app.badge ? `<span class="absolute top-2.5 left-2.5 px-2 py-0.5 bg-blue-600 text-white font-bold text-[9px] rounded-md shadow">${app.badge}</span>` : ''}
        <div class="absolute bottom-2 right-2 w-7 h-7 rounded-lg bg-black/60 backdrop-blur flex items-center justify-center text-white text-xs">
          <i class="fa-solid fa-play"></i>
        </div>
      </div>
      <div class="p-4 space-y-1.5 flex-1 flex flex-col justify-between">
        <div>
          <div class="font-bold text-white text-xs group-hover:text-indigo-400 transition flex items-center justify-between">
            <span>${app.title}</span>
            <i class="fa-solid fa-arrow-up-right-from-square text-[10px] opacity-0 group-hover:opacity-100 transition"></i>
          </div>
          <p class="text-[11px] text-gray-400 leading-relaxed mt-1 line-clamp-2">${app.desc}</p>
        </div>
        <div class="pt-2 text-[10px] text-indigo-300 font-semibold flex items-center gap-1">
          <i class="fa-solid fa-wand-magic-sparkles text-[9px]"></i>
          <span>Launch App</span>
        </div>
      </div>
    </div>
  `).join("");
}

function launchApp(appId) {
  const app = APPS_CATALOG.find(a => a.id === appId);
  if (!app) return;
  openCreateVideoWizardModal();
  setTimeout(() => {
    const promptInput = document.getElementById("wizard-prompt-input");
    const formatSelect = document.getElementById("wizard-format-select");
    const styleSelect = document.getElementById("wizard-style-select");
    if (promptInput) promptInput.value = `Create ${app.title}: ${app.desc}`;
    if (formatSelect) formatSelect.value = app.format;
    if (styleSelect) styleSelect.value = app.style;
  }, 100);
}
