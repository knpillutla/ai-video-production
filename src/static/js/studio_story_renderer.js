// CineAI Studio: Documentary Story (Stage 1) & Spoken Narration (Stage 2) Renderer
// Enforces 7-stage sequential documentary pipeline with chapter-subtitles-narration structure.

function updateFormatStageLayout(vid) {
  const isDoc = !Boolean(String(vid?.genre || "").toLowerCase().startsWith("relax"));
  const rowStory = document.getElementById("panel-stage-row-story");
  const rowNarr = document.getElementById("panel-stage-row-narration");
  const rowLp = document.getElementById("inspector-longplay-section");

  const bScript = document.getElementById("badge-script");
  const bImages = document.getElementById("badge-images");
  const bAudio = document.getElementById("badge-audio");
  const bMotion = document.getElementById("badge-motion");
  const bMaster = document.getElementById("badge-master");

  const tScript = document.getElementById("panel-script-stage-title");
  const tAudio = document.getElementById("panel-audio-stage-title");

  if (isDoc) {
    if (rowStory) rowStory.classList.remove("hidden");
    if (rowNarr) rowNarr.classList.remove("hidden");
    if (rowLp) rowLp.classList.add("hidden");

    if (bScript) bScript.textContent = "3";
    if (tScript) tScript.textContent = "Raw Gemini Screenplay";
    if (bImages) bImages.textContent = "4";
    if (bAudio) bAudio.textContent = "5";
    if (tAudio) tAudio.textContent = "BGM Soundtrack (Suno v3.5)";
    if (bMotion) bMotion.textContent = "6";
    if (bMaster) bMaster.textContent = "7";
  } else {
    if (rowStory) rowStory.classList.add("hidden");
    if (rowNarr) rowNarr.classList.add("hidden");
    if (rowLp) rowLp.classList.remove("hidden");

    if (bScript) bScript.textContent = "1";
    if (tScript) tScript.textContent = "Script & Storyboard Review";
    if (bImages) bImages.textContent = "2";
    if (bAudio) bAudio.textContent = "3";
    if (tAudio) tAudio.textContent = "Audio & BGM (48kHz)";
    if (bMotion) bMotion.textContent = "4";
    if (bMaster) bMaster.textContent = "5";
  }
}

function updateStagePillsForFormat(vid) {
  const c = document.getElementById("panel-header-stage-scroll");
  if (!c) return;
  const isDoc = !Boolean(String(vid?.genre || "").toLowerCase().startsWith("relax"));
  const curStage = vid?.currentStage || 1;
  const isProc = vid?.status === "processing";

  if (isDoc) {
    const docStages = [
      { id: "panel-stage-row-story", name: "1. Story", stage: 1 },
      { id: "panel-stage-row-narration", name: "2. Narration", stage: 2 },
      { id: "panel-stage-row-script", name: "3. Screenplay", stage: 3 },
      { id: "panel-stage-row-images", name: "4. Photos", stage: 4 },
      { id: "panel-stage-row-audio", name: "5. BGM", stage: 5 },
      { id: "panel-stage-row-motion", name: "6. Motion", stage: 6 },
      { id: "panel-stage-row-master", name: "7. Master", stage: 7 },
    ];
    c.innerHTML = docStages.map((st, i) => {
      let cls = "hover:text-[var(--accent)] font-semibold shrink-0 transition";
      let icon = "";
      if (isProc && curStage === st.stage) {
        cls += " text-purple-600 dark:text-purple-400 font-bold bg-purple-500/10 px-1.5 py-0.5 rounded border border-purple-500/20 animate-pulse";
        icon = '<i class="fa-solid fa-circle-notch fa-spin text-[8px] mr-1"></i>';
      } else if (curStage > st.stage) {
        cls += " text-emerald-600 dark:text-emerald-400 font-bold";
        icon = '✓ ';
      }
      const sep = i < docStages.length - 1 ? '<span class="text-[var(--text-muted)] opacity-40">›</span>' : '';
      return `<button type="button" onclick="scrollToStage('${st.id}')" class="${cls}">${icon}${st.name}</button>${sep}`;
    }).join("");
  } else {
    c.innerHTML = `
      <button type="button" onclick="scrollToStage('panel-stage-row-script')" class="hover:text-[var(--accent)] font-semibold shrink-0">1. Storyboard</button>
      <span>›</span>
      <button type="button" onclick="scrollToStage('panel-stage-row-images')" class="hover:text-[var(--accent)] font-semibold shrink-0">2. Photos</button>
      <span>›</span>
      <button type="button" onclick="scrollToStage('panel-stage-row-audio')" class="hover:text-[var(--accent)] font-semibold shrink-0">3. Audio &amp; BGM</button>
      <span>›</span>
      <button type="button" onclick="scrollToStage('panel-stage-row-motion')" class="hover:text-[var(--accent)] font-semibold shrink-0">4. Motion</button>
      <span>›</span>
      <button type="button" onclick="scrollToStage('panel-stage-row-master')" class="hover:text-[var(--accent)] font-semibold shrink-0">5. Master</button>
      <span>›</span>
      <button type="button" onclick="scrollToStage('inspector-longplay-section')" class="hover:text-[var(--accent)] font-semibold shrink-0">6. Long-Play</button>
    `;
  }
}

function renderStorySection(vid) {
  const c = document.getElementById("panel-section-story");
  const statusEl = document.getElementById("panel-story-status");
  const actionsEl = document.getElementById("panel-story-header-actions");
  if (!c) return;

  const storyObj = vid?.story || (vid?.screenplay ? {
    title: vid.screenplay.title,
    story_topic: vid.screenplay.story_topic,
    synopsis: vid.screenplay.story_topic,
    destination_entity: vid.screenplay.destination_entity || vid.production_name,
    chapters: (vid.screenplay.scenes || []).map((sc, i) => ({
      chapter_index: i + 1,
      chapter_title: sc.chapter_title || `Chapter ${i + 1}`,
      chapter_subtitle: sc.chapter_subtitle || "",
      narration: sc.narration_text || sc.narration || ""
    })),
    total_words_count: vid.screenplay.total_words_count,
    audio_master: vid.screenplay.audio_master
  } : null);

  const chapters = storyObj?.chapters || [];
  const hasStory = Boolean(storyObj && (chapters.length > 0 || storyObj.title || storyObj.story_topic));
  const isProc = vid?.status === "processing" && (vid?.currentStage === 1 || !vid?.currentStage);

  if (isProc && !hasStory) {
    if (statusEl) {
      statusEl.textContent = "Synthesizing...";
      statusEl.className = "text-amber-500 font-mono text-[9px] animate-pulse font-bold";
    }
    c.innerHTML = `
      <div class="h-9 bg-amber-50/70 dark:bg-amber-950/30 border-2 border-amber-500/80 rounded-xl flex items-center justify-between px-3 shadow-sm gap-2">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-3.5 h-3.5 rounded-full border-2 border-amber-500 border-t-transparent animate-spin shrink-0"></div>
          <span class="text-[9px] font-bold text-amber-700 dark:text-amber-400 truncate">Synthesizing Raw Gemini Story &amp; Chapters...</span>
        </div>
        <div class="w-24 bg-amber-200/60 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden shrink-0">
          <div class="h-full bg-gradient-to-r from-amber-500 to-orange-500 rounded-full animate-pulse" style="width: 30%"></div>
        </div>
      </div>`;
    return;
  }

  if (hasStory) {
    if (statusEl) {
      statusEl.textContent = `${chapters.length} Chapters Ready`;
      statusEl.className = "text-emerald-600 dark:text-emerald-400 font-mono text-[9px] font-bold";
    }
    if (actionsEl) {
      actionsEl.innerHTML = `
        <button type="button" onclick="openScriptDrawer('story')" class="btn-runway-secondary py-0.5 px-2 text-[10px] font-bold flex items-center gap-1" title="View Full Story Chapters &amp; Narration">
          <i class="fa-solid fa-book-open text-[9px]"></i>
          <span>View Story (${chapters.length} Ch)</span>
        </button>
      `;
    }

    const title = storyObj.title || vid?.title || "Documentary Story Dossier";
    const dest = storyObj.destination_entity || vid?.production_name || "";
    const synop = storyObj.synopsis || storyObj.story_topic || "";
    const firstNarr = chapters[0]?.narration || synop;

    c.innerHTML = `
      <div class="p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm flex flex-col gap-1.5">
        <div class="flex items-center justify-between gap-1.5">
          <div class="flex items-center gap-1.5 min-w-0 flex-1 cursor-pointer" onclick="openScriptDrawer('story')">
            <span class="w-4 h-4 rounded-md bg-amber-500/15 text-amber-600 dark:text-amber-400 flex items-center justify-center text-[9px] shrink-0 font-bold">
              <i class="fa-solid fa-book"></i>
            </span>
            <span class="text-[10px] font-black text-slate-900 dark:text-gray-100 truncate">${dest ? dest + ': ' : ''}${title}</span>
          </div>
          <div class="flex items-center gap-1 shrink-0">
            <span class="text-[8px] font-mono font-bold px-1.5 py-0.2 rounded bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800">${chapters.length} Chapters</span>
            <button type="button" onclick="openScriptDrawer('story')" class="w-6 h-6 rounded-lg bg-amber-50 dark:bg-amber-950 hover:bg-amber-100 text-amber-700 dark:text-amber-300 border border-amber-200 dark:border-amber-800 flex items-center justify-center text-[9px]" title="Read Story Dossier">
              <i class="fa-solid fa-up-right-from-square"></i>
            </button>
          </div>
        </div>
        <div class="text-[9px] text-slate-600 dark:text-slate-300 line-clamp-2 leading-relaxed bg-slate-50 dark:bg-slate-950/60 p-1.5 rounded-lg border border-slate-100 dark:border-slate-800/80">
          <span class="font-bold text-amber-600 dark:text-amber-400 mr-1">Ch 1:</span>${firstNarr}
        </div>
      </div>
    `;
    return;
  }

  // Empty state
  if (statusEl) {
    statusEl.textContent = "Empty";
    statusEl.className = "text-slate-400 font-mono text-[9px]";
  }
  c.innerHTML = `
    <div class="h-9 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl flex items-center justify-between px-2.5 text-slate-500 dark:text-slate-400 shadow-sm">
      <div class="flex items-center gap-1.5 min-w-0">
        <i class="fa-solid fa-book text-slate-400 text-xs shrink-0"></i>
        <span class="text-[9px] font-medium text-slate-500 dark:text-gray-400 truncate">No Raw Gemini Story Synthesized Yet</span>
      </div>
      <button type="button" onclick="advanceToScriptStage(currentActiveInspectorEpisode)" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold shrink-0 flex items-center gap-1" title="Generate Gemini Raw Story">
        <i class="fa-solid fa-sparkles text-[9px]"></i> Generate Story
      </button>
    </div>
  `;
}

function renderNarrationSection(vid) {
  const c = document.getElementById("panel-section-narration");
  const statusEl = document.getElementById("panel-narration-status");
  const actionsEl = document.getElementById("panel-narration-header-actions");
  if (!c) return;

  const rawStems = vid?.audio_stems || [];
  const narrStem = rawStems.find(s => (s.filename && (s.filename.includes("spoken_narration") || s.filename.includes("narration"))) || (s.name && (s.name.toLowerCase().includes("narration") || s.name.toLowerCase().includes("voiceover"))));
  const hasNarr = Boolean(narrStem && narrStem.url);
  const isProc = vid?.status === "processing" && (vid?.currentStage === 2 || vid?.currentStage === 3);

  if (isProc && !hasNarr) {
    if (statusEl) {
      statusEl.textContent = "Synthesizing...";
      statusEl.className = "text-blue-500 font-mono text-[9px] animate-pulse font-bold";
    }
    c.innerHTML = `
      <div class="h-9 bg-blue-50/70 dark:bg-blue-950/30 border-2 border-blue-500/80 rounded-xl flex items-center justify-between px-3 shadow-sm gap-2">
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-3.5 h-3.5 rounded-full border-2 border-blue-500 border-t-transparent animate-spin shrink-0"></div>
          <span class="text-[9px] font-bold text-blue-700 dark:text-blue-400 truncate">Synthesizing Azure Speech Voiceover Narration...</span>
        </div>
        <div class="w-24 bg-blue-200/60 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden shrink-0">
          <div class="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full animate-pulse" style="width: 50%"></div>
        </div>
      </div>`;
    return;
  }

  if (hasNarr) {
    if (statusEl) {
      statusEl.textContent = "Ready";
      statusEl.className = "text-emerald-600 dark:text-emerald-400 font-mono text-[9px] font-bold";
    }
    if (actionsEl) {
      actionsEl.innerHTML = `
        <button type="button" onclick="advanceToScriptStage(currentActiveInspectorEpisode)" class="btn-runway-primary py-0.5 px-2 text-[10px] font-bold shadow-sm flex items-center gap-1" title="Advance to Stage 3: Screenplay">
          <span>Next: Screenplay</span>
          <i class="fa-solid fa-arrow-right text-[8px]"></i>
        </button>
      `;
    }

    c.innerHTML = `
      <div class="p-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-sm flex flex-col gap-1">
        <div class="flex items-center justify-between text-[9px]">
          <span class="font-mono text-indigo-600 dark:text-indigo-400 font-bold flex items-center gap-1.5">
            <i class="fa-solid fa-circle-check text-emerald-500 text-[8px]"></i>
            <span class="text-slate-900 dark:text-gray-100 font-bold">Azure Speech Neural Master (48kHz)</span>
          </span>
          <span class="text-[8px] font-mono text-slate-500 dark:text-slate-400">⏱ ${narrStem.duration || 'Ready'}</span>
        </div>
        <audio controls preload="none" src="${narrStem.url}" class="h-5 w-full mt-0.5"></audio>
      </div>
    `;
    return;
  }

  // Not generated yet: offer voiceover engine selection
  if (statusEl) {
    statusEl.textContent = "Idle";
    statusEl.className = "text-slate-400 font-mono text-[9px]";
  }
  c.innerHTML = `
    <div class="p-1.5 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950/40 dark:to-indigo-950/40 border border-blue-300 dark:border-blue-600/50 rounded-xl flex items-center justify-between gap-1.5 shadow-sm">
      <div class="flex items-center gap-1.5">
        <i class="fa-solid fa-microphone text-blue-600 dark:text-blue-400 text-xs"></i>
        <div class="flex flex-col">
          <span class="text-[9px] font-bold text-blue-950 dark:text-white">Stage 1 Story Ready</span>
          <span class="text-[7px] text-blue-700 dark:text-blue-300">Choose voiceover engine:</span>
        </div>
      </div>
      <div class="flex items-center gap-1 flex-wrap">
        <button type="button" onclick="advanceToNarrationStage(currentActiveInspectorEpisode, 'azure_speech')" class="px-2 py-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Synthesize Voiceover with Azure Speech">
          🎙️ Azure/Edge (Def)
        </button>
        <button type="button" onclick="advanceToNarrationStage(currentActiveInspectorEpisode, 'gemini')" class="px-2 py-1 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Synthesize Voiceover with Gemini 2.5 Flash Audio">
          ✨ Gemini Audio
        </button>
        <button type="button" onclick="advanceToNarrationStage(currentActiveInspectorEpisode, 'kokoro')" class="px-2 py-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 text-white rounded-lg text-[8px] font-bold transition flex items-center gap-1 shadow active:scale-95" title="Synthesize Voiceover with Kokoro CPU ($0.00)">
          ⚡ Kokoro ($0)
        </button>
      </div>
    </div>
  `;
}

window.advanceToNarrationStage = window.advanceToNarrationStage || function(vid, tts) {
  let t = (typeof resolveActiveStudioEpisode === "function") ? resolveActiveStudioEpisode(vid) : (vid || currentActiveInspectorEpisode);
  if (t && typeof startStudioLiveStageProgress === "function") startStudioLiveStageProgress(t, "manual", "narration");
};
window.renderStorySection = renderStorySection;
window.renderNarrationSection = renderNarrationSection;
window.updateFormatStageLayout = updateFormatStageLayout;
window.updateStagePillsForFormat = updateStagePillsForFormat;


