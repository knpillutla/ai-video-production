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
