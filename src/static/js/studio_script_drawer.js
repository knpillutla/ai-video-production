// CineAI Studio: Script, Storyboard & Screenplay JSON Drawer Controller
let activeScriptDrawerTab = "story";

function switchScriptDrawerTab(tabKey) {
  activeScriptDrawerTab = tabKey || "story";
  const tabs = {
    story: { btn: "btn-script-tab-story", view: "script-drawer-view-story", activeColor: "bg-amber-600" },
    visual: { btn: "btn-script-tab-visual", view: "script-drawer-view-visual", activeColor: "bg-purple-600" },
    inputs_json: { btn: "btn-script-tab-inputs", view: "script-drawer-view-inputs", activeColor: "bg-emerald-600" },
    screenplay_json: { btn: "btn-script-tab-screenplay", view: "script-drawer-view-screenplay", activeColor: "bg-amber-600" },
    pipeline_json: { btn: "btn-script-tab-pipeline", view: "script-drawer-view-pipeline", activeColor: "bg-purple-600" },
    manifest_json: { btn: "btn-script-tab-manifest", view: "script-drawer-view-manifest", activeColor: "bg-indigo-600" },
  };

  const actBase = "flex-1 py-1 px-1.5 font-bold rounded-lg text-white shadow transition flex items-center justify-center gap-1 whitespace-nowrap";
  const inactCls = "flex-1 py-1 px-1.5 font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center justify-center gap-1 whitespace-nowrap";

  Object.entries(tabs).forEach(([k, cfg]) => {
    const btn = document.getElementById(cfg.btn);
    const view = document.getElementById(cfg.view);
    const isAct = (k === activeScriptDrawerTab);
    if (btn) btn.className = isAct ? `${actBase} ${cfg.activeColor}` : inactCls;
    if (view) view.classList.toggle("hidden", !isAct);
  });

  const copyBtn = document.getElementById("btn-copy-storyboard-bottom");
  if (copyBtn) {
    if (activeScriptDrawerTab === "inputs_json") {
      copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy user_inputs.json</span>';
      copyBtn.onclick = () => copyScriptDrawerJson("user_inputs");
    } else if (activeScriptDrawerTab === "screenplay_json") {
      copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy screenplay.json</span>';
      copyBtn.onclick = () => copyScriptDrawerJson("screenplay");
    } else if (activeScriptDrawerTab === "pipeline_json") {
      copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy pipeline_state.json</span>';
      copyBtn.onclick = () => copyScriptDrawerJson("pipeline_state");
    } else if (activeScriptDrawerTab === "manifest_json") {
      copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i> <span>Copy manifest.json</span>';
      copyBtn.onclick = () => copyScriptDrawerJson("manifest");
    } else if (activeScriptDrawerTab === "visual") {
      copyBtn.innerHTML = '<i class="fa-solid fa-copy"></i> <span>Copy Screenplay Shots</span>';
      copyBtn.onclick = copyScriptDrawerContent;
    } else {
      copyBtn.innerHTML = '<i class="fa-solid fa-book"></i> <span>Copy Story Chapters</span>';
      copyBtn.onclick = copyStoryChaptersContent;
    }
  }
}

async function openScriptDrawer(initialTab = "story") {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  const drawer = document.getElementById("studio-script-drawer-modal");
  if (!drawer) return;

  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "euro_discovery");

  if (!vid.screenplay || !vid.story || !vid.pipeline_state) {
    try {
      const uEmail = (typeof currentUser !== "undefined" && currentUser?.email) ? currentUser.email : "knpillutla@gmail.com";
      const fmtQ = encodeURIComponent(vid.format || vid.format_slug || "");
      const prodQ = encodeURIComponent(vid.production_name || "");
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&format=${fmtQ}&production_name=${prodQ}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
        if (data.story) vid.story = data.story;
        if (data.script) vid.script = data.script;
        if (data.screenplay) vid.screenplay = data.screenplay;
        if (data.user_inputs) vid.user_inputs = data.user_inputs;
        if (data.pipeline_state) vid.pipeline_state = data.pipeline_state;
        if (data.manifest) vid.manifest = data.manifest;
      }
    } catch (e) {
      console.debug("Script drawer poll notice:", e);
    }
  }

  const script = vid.screenplay || vid.script || vid.manifest || {};
  const story = vid.story || script;
  const docShots = (script.chapters || []).flatMap((ch, cIdx) =>
    (ch.shots || []).map((sh, sIdx) => ({
      ...sh,
      chapter_index: ch.chapter_index || (cIdx + 1),
      chapter_title: ch.chapter_title || `Chapter ${cIdx + 1}`,
      shot_index: sh.shot_index || (sIdx + 1),
    }))
  );
  const scenes = docShots.length > 0 ? docShots : (script.scenes || vid.scenes || []);
  const rawChapters = story.chapters || scenes.map((sc, i) => ({
    chapter_index: i + 1,
    chapter_title: sc.chapter_title || `Chapter ${i + 1}`,
    chapter_subtitle: sc.chapter_subtitle || "",
    chapter_stats: sc.chapter_stats || "",
    fact_badge: sc.fact_badge || "",
    narration: sc.narration_text || sc.narration || "",
  }));

  const pipelineState = vid.pipeline_state || { current_stage: vid.currentStage || 1, is_approved: Boolean(vid.is_approved), status: vid.status || "ready" };
  const manifest = vid.manifest || vid.script || {};
  const userInputs = vid.user_inputs || { prompt: vid.concept || vid.title, channel_id: chSlug, episode_id: epId, duration_seconds: vid.durationSeconds || 60 };

  const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setT("script-drawer-ep-id", `${epId} • Gemini 2.5 Director`);
  setT("script-drawer-title", story.title || script.title || vid.title || "Director Storyboard");
  setT("script-drawer-story", story.synopsis || story.story_topic || script.story_topic || vid.story_topic || "Master video production");
  setT("script-drawer-cluster", `Cluster: ${script.cluster || vid.cluster || vid.genre || "Documentary"}`);
  setT("script-drawer-fps", `${script.recommended_fps || vid.recommended_fps || vid.fps || 24} FPS Cinematic`);
  setT("script-drawer-audio-tags", script.audio_tags || (script.audio_master?.suno_musical_tags) || vid.audio_tags || "acoustic documentary score");
  setT("script-drawer-scenes-count", `${rawChapters.length || scenes.length || 1} Chapters`);

  // VIEW 1: Populate Chapters List
  const chListEl = document.getElementById("script-drawer-chapters-list");
  if (chListEl) {
    if (rawChapters.length === 0) {
      chListEl.innerHTML = `<div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500 text-[10px]">No story chapters generated yet. Click Produce Video to synthesize.</div>`;
    } else {
      chListEl.innerHTML = rawChapters.map(ch => `
        <div class="p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-1.5 shadow-sm">
          <div class="flex items-center justify-between gap-1 flex-wrap">
            <div class="flex items-center gap-1.5 min-w-0">
              <span class="w-5 h-5 rounded-md bg-amber-500/15 text-amber-600 dark:text-amber-400 font-mono font-bold text-[10px] flex items-center justify-center shrink-0">${ch.chapter_index}</span>
              <span class="text-xs font-black text-slate-900 dark:text-gray-100">${ch.chapter_title}</span>
            </div>
            <div class="flex items-center gap-1">
              ${ch.fact_badge ? `<span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-amber-100 dark:bg-amber-950 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800">${ch.fact_badge}</span>` : ''}
              ${ch.chapter_stats ? `<span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-gray-300 border border-slate-200 dark:border-slate-700">${ch.chapter_stats}</span>` : ''}
            </div>
          </div>
          ${ch.chapter_subtitle ? `<div class="text-[10px] font-bold text-amber-600 dark:text-amber-400 pl-6.5">${ch.chapter_subtitle}</div>` : ''}
          <div class="p-2 bg-slate-50 dark:bg-slate-950 rounded-lg border border-slate-200 dark:border-slate-800 text-[10px] text-slate-700 dark:text-slate-300 leading-relaxed font-sans select-all">
            <span class="text-slate-400 font-bold uppercase text-[8px] block mb-0.5">Spoken Narration:</span>
            ${ch.narration || '(No narration text specified)'}
          </div>
        </div>
      `).join("");
    }
  }

  // VIEW 2: Populate Multi-Shot Screenplay Scenes List
  const listEl = document.getElementById("script-drawer-scenes-list");
  if (listEl) {
    if (scenes.length === 0) {
      listEl.innerHTML = `<div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500 text-[10px]">No expanded multi-shot directives available yet. Click Generate Script.</div>`;
    } else {
      listEl.innerHTML = scenes.map((sc, i) => {
        const sNum = sc.scene_index || (i + 1);
        const sType = (sc.shot_type || 'Wide Vista').replace('_', ' ').toUpperCase();
        const vPrompt = sc.visual_prompt || 'Scenic ambient view';
        const mPrompt = sc.motion_prompt || 'Slow drone forward camera motion';
        const sDur = sc.duration_seconds || 12;
        return `
        <div class="p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-1.5 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-[9px] font-bold font-mono text-purple-600 dark:text-purple-400 flex items-center gap-1">
              <i class="fa-solid fa-clapperboard"></i> Scene ${sNum}: ${sType}
            </span>
            <span class="px-1.5 py-0.2 rounded bg-slate-200 dark:bg-slate-800 text-[8px] font-mono text-slate-600 dark:text-gray-400 font-bold">⏱ ${sDur}s</span>
          </div>
          <div class="space-y-1 text-[9px]">
            <div>
              <span class="font-bold text-slate-700 dark:text-gray-300">Visual Prompt (FLUX 1.1 Pro):</span>
              <p class="text-slate-600 dark:text-gray-400 leading-tight bg-white dark:bg-slate-950 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono text-[8px] select-all">${vPrompt}</p>
            </div>
            <div>
              <span class="font-bold text-slate-700 dark:text-gray-300">Motion Directive (${sc.motion_type || 'Ken Burns / Wan 2.1'}):</span>
              <p class="text-slate-600 dark:text-gray-400 leading-tight bg-white dark:bg-slate-950 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono text-[8px] select-all">${mPrompt}</p>
            </div>
          </div>
        </div>`;
      }).join("");
    }
  }

  // Populate code blocks
  const inCode = document.getElementById("script-drawer-inputs-code");
  if (inCode) inCode.textContent = JSON.stringify(userInputs, null, 2);
  const spCode = document.getElementById("script-drawer-screenplay-code");
  if (spCode) spCode.textContent = JSON.stringify(vid.screenplay || script, null, 2);
  const plCode = document.getElementById("script-drawer-pipeline-code");
  if (plCode) plCode.textContent = JSON.stringify(pipelineState, null, 2);
  const mfCode = document.getElementById("script-drawer-manifest-code");
  if (mfCode) mfCode.textContent = JSON.stringify(manifest, null, 2);

  switchScriptDrawerTab(initialTab);
  drawer.classList.remove("hidden");
}

function closeScriptDrawer() {
  document.getElementById("studio-script-drawer-modal")?.classList.add("hidden");
  document.getElementById("episode-script-modal")?.classList.add("hidden");
}

function copyStoryChaptersContent() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  const story = vid.story || vid.screenplay || {};
  const chapters = story.chapters || [];
  const text = `Title: ${story.title || vid.title}\nDestination: ${story.destination_entity || ''}\n\n` +
    chapters.map(c => `Chapter ${c.chapter_index}: ${c.chapter_title}\n${c.chapter_subtitle || ''}\nNarration: ${c.narration}`).join("\n\n");
  navigator.clipboard.writeText(text).then(() => {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Story chapters copied!");
  }).catch(() => {});
}

function copyScriptDrawerContent() {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  const script = vid.screenplay || vid.script || vid.manifest || {};
  const text = `Title: ${script.title || vid.title}\nStory: ${script.story_topic || vid.story_topic}\n\nScenes:\n` +
    (script.scenes || []).map((s, i) => `Scene ${i+1} (${s.shot_type || 'Wide'}, ${s.duration_seconds || 12}s):\nVisual: ${s.visual_prompt}\nMotion: ${s.motion_prompt}`).join("\n\n");
  navigator.clipboard.writeText(text).then(() => {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Screenplay shots copied!");
  }).catch(() => {});
}

function copyScriptDrawerJson(type) {
  const vid = currentActiveInspectorEpisode;
  if (!vid) return;
  let target = (type === "user_inputs") ? vid.user_inputs : ((type === "screenplay") ? (vid.screenplay || vid.script) : ((type === "pipeline_state") ? vid.pipeline_state : vid.manifest));
  navigator.clipboard.writeText(JSON.stringify(target || {}, null, 2)).then(() => {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast(`Copied ${type}.json!`);
  }).catch(() => {});
}

window.openScriptDrawer = openScriptDrawer;
window.closeScriptDrawer = closeScriptDrawer;
window.switchScriptDrawerTab = switchScriptDrawerTab;
