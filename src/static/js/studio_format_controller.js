// CineAI Studio: Format (16:9 vs 9:16) & Audio Ambience Mode Controller
function setStudioFormat(format) {
  const hiddenInput = document.getElementById("studio-selected-format");
  const landscapeBtn = document.getElementById("format-btn-landscape");
  const portraitBtn = document.getElementById("format-btn-portrait");
  
  if (hiddenInput) hiddenInput.value = format;
  
  if (landscapeBtn) landscapeBtn.classList.toggle("active", format === "16:9");
  if (portraitBtn) portraitBtn.classList.toggle("active", format === "9:16");
}

function togglePureNatureMode(isPure) {
  const bgmToggle = document.getElementById("studio-toggle-bgm");
  const voiceToggle = document.getElementById("studio-toggle-voice-over");
  
  if (isPure) {
    if (bgmToggle) bgmToggle.checked = false;
    if (voiceToggle) voiceToggle.checked = false;
  } else {
    if (bgmToggle) bgmToggle.checked = true;
    if (voiceToggle) voiceToggle.checked = true;
  }
}
