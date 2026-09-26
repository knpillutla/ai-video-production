// CineAI Studio: Format (16:9 vs 9:16) & Audio Ambience Mode Controller
function setStudioFormat(format) {
  const hiddenInput = document.getElementById("studio-selected-format");
  const landscapeBtn = document.getElementById("format-btn-landscape");
  const portraitBtn = document.getElementById("format-btn-portrait");
  
  if (hiddenInput) hiddenInput.value = format;
  
  if (format === "9:16") {
    if (landscapeBtn) {
      landscapeBtn.className = "px-3 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-md transition flex items-center gap-1.5";
    }
    if (portraitBtn) {
      portraitBtn.className = "px-3 py-1 text-xs font-bold rounded-md bg-pink-600 text-white shadow transition flex items-center gap-1.5";
    }
  } else {
    // 16:9 Landscape (Default)
    if (landscapeBtn) {
      landscapeBtn.className = "px-3 py-1 text-xs font-bold rounded-md bg-indigo-600 text-white shadow transition flex items-center gap-1.5";
    }
    if (portraitBtn) {
      portraitBtn.className = "px-3 py-1 text-xs font-medium text-gray-400 hover:text-white rounded-md transition flex items-center gap-1.5";
    }
  }
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
