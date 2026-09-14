// wizard_ui.js: Compatibility re-export for production tier tests
function openCreateVideoWizard() {
  if (typeof openCreateVideoWizardModal === "function") {
    openCreateVideoWizardModal();
  }
}

function closeCreateVideoWizard() {
  if (typeof closeCreateVideoWizardModal === "function") {
    closeCreateVideoWizardModal();
  }
}
