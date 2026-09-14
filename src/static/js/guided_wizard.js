// CineAI Studio: Guided Wizard & Multi-Step Video Production Controller
let currentWizardStep = 1;
let wizardSelectedTier = "balanced";

function openCreateVideoWizardModal() {
  currentWizardStep = 1;
  const heroPrompt = (document.getElementById("youtube-prompt-input")?.value || "").trim();
  const heroUrl = (document.getElementById("youtube-url-input")?.value || "").trim();
  const wizardPrompt = document.getElementById("wizard-prompt-input");
  const wizardUrl = document.getElementById("wizard-youtube-url");
  if (wizardPrompt && heroPrompt && !wizardPrompt.value) wizardPrompt.value = heroPrompt;
  if (wizardUrl && heroUrl && !wizardUrl.value) wizardUrl.value = heroUrl;
  wizardGoToStep(1);
  openModal("create-video-wizard-modal");
}

function closeCreateVideoWizardModal() {
  closeModal("create-video-wizard-modal");
}

function wizardGoToStep(step) {
  currentWizardStep = step;
  for (let s = 1; s <= 3; s++) {
    const container = document.getElementById(`wizard-step-${s}-container`);
    const tabBtn = document.getElementById(`wizard-tab-${s}`);
    if (container) container.classList.toggle("hidden", s !== step);
    if (tabBtn) {
      tabBtn.className = s === step
        ? "px-4 py-2 font-bold text-white bg-indigo-600 rounded-lg shadow"
        : "px-4 py-2 font-medium text-gray-400 rounded-lg";
    }
  }
}

function wizardAnalyzeConcept() {
  const promptInput = document.getElementById("wizard-prompt-input");
  const distillerCard = document.getElementById("wizard-distiller-card");
  const premiseText = document.getElementById("wizard-premise-text");
  const concept = (promptInput?.value || "").trim() || "Satirical narrative adaptation";
  if (premiseText) premiseText.textContent = `Analyzed concept: "${concept}". Storyboard keyframes aligned.`;
  if (distillerCard) distillerCard.classList.remove("hidden");
}

function wizardSelectTier(tierKey) {
  wizardSelectedTier = tierKey;
  const tiers = ["low_cost", "balanced", "cinematic"];
  tiers.forEach(t => {
    const card = document.getElementById("wizard-card-" + t);
    if (!card) return;
    card.className = t === tierKey
      ? "p-3 border-2 border-indigo-500 bg-indigo-950/40 rounded-xl cursor-pointer transition space-y-1 ring-1 ring-indigo-500/50"
      : "p-3 border border-slate-700 bg-slate-900/60 rounded-xl cursor-pointer transition space-y-1";
  });
  const tier = PRODUCTION_TIERS[tierKey] || PRODUCTION_TIERS.balanced;
  const costEl = document.getElementById("wizard-confirm-cost");
  if (costEl) costEl.textContent = tier.priceStr;
}

function wizardConfirmAndProduce() {
  closeCreateVideoWizardModal();
  const promptInput = document.getElementById("wizard-prompt-input");
  const urlInput = document.getElementById("wizard-youtube-url");
  const langSelect = document.getElementById("wizard-lang-select");
  const formatSelect = document.getElementById("wizard-format-select");
  const styleSelect = document.getElementById("wizard-style-select");

  const prompt = (promptInput?.value || "").trim();
  const url = (urlInput?.value || "").trim();
  const lang = langSelect?.value || "Telugu (te)";
  const fmt = formatSelect?.value || "Web Series (16:9)";
  const sty = styleSelect?.value || "Cinematic Photoreal";
  const tier = PRODUCTION_TIERS[wizardSelectedTier] || PRODUCTION_TIERS.balanced;

  let title = "";
  let concept = "";
  let prodType = "Prompt";
  const isShort = fmt.includes("Shorts") || fmt.includes("9:16");
  const formatType = isShort ? "Short (9:16)" : "Long (16:9)";
  let videoType = isShort ? "Comedy Reel" : (fmt.includes("Documentary") ? "Travel Guide & Doc" : "Web Series");

  if (url && prompt) {
    prodType = "YouTube Reference";
    title = prompt.slice(0, 36);
    concept = `${prompt} [Referencing YouTube: ${url}]`;
  } else if (url) {
    prodType = "YouTube Reference";
    const match = url.match(/(?:v=|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{6,12})/);
    title = `Adaptive Remake [${match ? match[1] : "Ref"}]`;
    concept = `Transformative adaptation referencing ${url}`;
  } else if (prompt) {
    title = prompt.slice(0, 36);
    concept = prompt;
    prodType = "Prompt";
  } else {
    title = "New AI Production";
    concept = "Guided wizard script production";
    prodType = "Script";
  }

  currentUser.balance_usd = Math.max(0, currentUser.balance_usd - tier.priceUsd);
  saveUserState();

  const newId = `EP-00${studioVideos.length + 1}`;
  const uniqueJobId = `job_${newId.toLowerCase()}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;
  const voiceGenderSelect = document.getElementById("wizard-voice-gender-select");
  const durationSelect = document.getElementById("wizard-duration-select");
  const durationSec = durationSelect ? parseInt(durationSelect.value, 10) : 10;
  const enableBgmToggle = document.getElementById("wizard-toggle-bgm");
  const enableVoiceOverToggle = document.getElementById("wizard-toggle-voice-over");
  const enableTtsToggle = document.getElementById("wizard-toggle-tts");
  const enableLipsyncToggle = document.getElementById("wizard-toggle-lipsync");

  const voiceGender = voiceGenderSelect?.value || "female";
  const enableBgm = enableBgmToggle ? enableBgmToggle.checked : true;
  const enableVoiceOver = enableVoiceOverToggle ? enableVoiceOverToggle.checked : true;
  const enableTts = enableTtsToggle ? enableTtsToggle.checked : false;
  const enableLipsync = enableLipsyncToggle ? enableLipsyncToggle.checked : false;

  const newVid = {
    id: newId,
    jobId: uniqueJobId,
    title: title,
    concept: concept,
    videoType: videoType,
    formatType: formatType,
    styleType: sty.includes("Pixar") ? "3D Animation" : (sty.includes("Anime") ? "Anime (Shonen)" : "Realistic (Photoreal)"),
    productionType: prodType,
    durationSeconds: durationSec,
    duration: `${durationSec}s`,
    status: "queued",
    youtubeStatus: "unpublished",
    youtubeChannel: null,
    youtubeUrl: null,
    youtubeReferenceUrl: url || null,
    videoUrl: "/static/videos/preview_master.mp4",
    language: lang,
    format: fmt,
    style: sty,
    tierKey: tier.key,
    tierName: tier.name + ` (${tier.priceStr})`,
    cost: tier.priceUsd,
    costStr: tier.priceStr,
    voiceGender: voiceGender,
    enableBgm: enableBgm,
    enableVoiceOver: enableVoiceOver,
    enableTts: enableTts,
    enableLipsync: enableLipsync,
    createdAt: Date.now(),
    startedAt: null,
    completedAt: null,
    publishedAt: null
  };

  studioVideos.unshift(newVid);
  if (typeof saveVideosState === "function") saveVideosState();
  switchTab("ledger");
  const mainEl = document.querySelector("main");
  if (mainEl) mainEl.scrollTop = 0;

  renderStudioVideoHistory();
  if (typeof selectLedgerVideo === "function") selectLedgerVideo(newId);

  const banner = document.getElementById("ledger-queued-banner");
  const bannerId = document.getElementById("banner-request-id");
  const bannerDetail = document.getElementById("banner-request-detail");
  if (banner) {
    if (bannerId) bannerId.textContent = uniqueJobId;
    if (bannerDetail) bannerDetail.textContent = `Episode ${newId} ("${title}") is now queued. Production Type: ${prodType} • Billed: ${tier.priceStr}. Track live progress below.`;
    banner.classList.remove("hidden");
  }

  showStudioModal({
    title: "Request Queued",
    message: `Request is queued with Request ID: ${uniqueJobId}\n\nEpisode: ${newId} — "${title}"\nProduction Type: ${prodType}\nTier: ${tier.name} (${tier.priceStr})`,
    nextStep: "Redirected to Video Ledger to monitor live synthesis."
  });

  if (typeof startLocalVideoProductionJob === "function") {
    startLocalVideoProductionJob(newVid);
  }
}

function wizardConfirmAndEnqueue() {
  return wizardConfirmAndProduce();
}
