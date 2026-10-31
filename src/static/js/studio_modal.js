// CineAI Studio: Professional Guidance & Notification Modal Controller
let studioModalCallback = null;

function showStudioModal({ title, message, nextStep, onConfirm }) {
  const titleEl = document.getElementById("popup-title");
  const messageEl = document.getElementById("popup-message");
  const nextBox = document.getElementById("popup-next-step-box");
  studioModalCallback = onConfirm || null;

  if (titleEl) titleEl.textContent = title;
  if (messageEl) messageEl.textContent = message;
  if (nextBox) {
    if (nextStep) {
      nextBox.textContent = nextStep;
      nextBox.classList.remove("hidden");
    } else {
      nextBox.classList.add("hidden");
    }
  }
  openModal("studio-popup-modal");
}

function closeStudioModal() {
  closeModal("studio-popup-modal");
  studioModalCallback = null;
}

function onStudioModalConfirm() {
  if (typeof studioModalCallback === "function") {
    studioModalCallback();
  }
  closeStudioModal();
}

// Circular Popup Progress Modal for Stage 1 Story Script Formulation
let _creationProgressInterval = null;

function showCreationProgressModal({ episodeId, title, subtitle } = {}) {
  const modal = document.getElementById("creation-progress-modal");
  if (!modal) return;
  const bEl = document.getElementById("creation-progress-badge");
  const tEl = document.getElementById("creation-progress-title");
  const sEl = document.getElementById("creation-progress-subtitle");
  const pEl = document.getElementById("creation-progress-pct");
  const cEl = document.getElementById("creation-progress-circle");

  if (bEl) bEl.textContent = (episodeId || "EP-001").toUpperCase();
  if (tEl) tEl.textContent = title || "Generating Sovereign 22-Chapter Story Script";
  if (sEl) sEl.textContent = subtitle || "Directing Gemini 2.5 Flash to evaluate trending destinations & sovereign history...";

  const circumference = 263.89; // 2 * PI * 42
  let pct = 18;
  const setPct = (val) => {
    if (pEl) pEl.textContent = `${Math.round(val)}%`;
    if (cEl) {
      const offset = circumference - (val / 100) * circumference;
      cEl.style.strokeDashoffset = offset;
    }
    const stepGeo = document.getElementById("step-check-geo");
    const stepStory = document.getElementById("step-check-story");
    const stepDisk = document.getElementById("step-check-disk");
    if (val >= 45 && stepStory) {
      stepStory.className = "flex items-center gap-2 text-indigo-600 dark:text-indigo-400 font-semibold";
      stepStory.innerHTML = '<i class="fa-solid fa-circle-check text-xs"></i><span>2. Synthesizing 22 Chapters (Prologue to Future Horizons)</span>';
    }
    if (val >= 80 && stepDisk) {
      stepDisk.className = "flex items-center gap-2 text-blue-600 dark:text-blue-400 font-semibold animate-pulse";
      stepDisk.innerHTML = '<i class="fa-solid fa-spinner fa-spin text-xs"></i><span>3. Creating Episode Folder & Traceable Artifacts</span>';
    }
  };

  setPct(pct);
  if (_creationProgressInterval) clearInterval(_creationProgressInterval);
  _creationProgressInterval = setInterval(() => {
    if (pct < 94) {
      pct += Math.max(1, (94 - pct) * 0.15);
      setPct(pct);
    }
  }, 1000);

  modal.classList.remove("hidden");
}

function updateCreationProgressModal({ progress, subtitle, title } = {}) {
  if (typeof progress === "number") {
    const circumference = 263.89;
    const pEl = document.getElementById("creation-progress-pct");
    const cEl = document.getElementById("creation-progress-circle");
    if (pEl) pEl.textContent = `${Math.round(progress)}%`;
    if (cEl) {
      const offset = circumference - (progress / 100) * circumference;
      cEl.style.strokeDashoffset = offset;
    }
  }
  if (title) {
    const tEl = document.getElementById("creation-progress-title");
    if (tEl) tEl.textContent = title;
  }
  if (subtitle) {
    const sEl = document.getElementById("creation-progress-subtitle");
    if (sEl) sEl.textContent = subtitle;
  }
}

function hideCreationProgressModal() {
  if (_creationProgressInterval) {
    clearInterval(_creationProgressInterval);
    _creationProgressInterval = null;
  }
  const modal = document.getElementById("creation-progress-modal");
  if (!modal) return;
  const pEl = document.getElementById("creation-progress-pct");
  const cEl = document.getElementById("creation-progress-circle");
  if (pEl) pEl.textContent = "100%";
  if (cEl) cEl.style.strokeDashoffset = 0;
  const stepDisk = document.getElementById("step-check-disk");
  if (stepDisk) {
    stepDisk.className = "flex items-center gap-2 text-emerald-600 dark:text-emerald-400 font-semibold";
    stepDisk.innerHTML = '<i class="fa-solid fa-circle-check text-xs"></i><span>3. Episode Folder & Artifacts Ready</span>';
  }
  setTimeout(() => {
    modal.classList.add("hidden");
  }, 500);
}
