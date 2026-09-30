// CineAI Studio: Script, Storyboard & Screenplay JSON Drawer Controller
let activeScriptDrawerTab = "visual";

function switchScriptDrawerTab(tabKey) {
  activeScriptDrawerTab = tabKey || "visual";
  const tabs = {
    visual: { btn: "btn-script-tab-visual", view: "script-drawer-view-visual", activeColor: "bg-amber-600" },
    inputs_json: { btn: "btn-script-tab-inputs", view: "script-drawer-view-inputs", activeColor: "bg-emerald-600" },
    screenplay_json: { btn: "btn-script-tab-screenplay", view: "script-drawer-view-screenplay", activeColor: "bg-amber-600" },
    pipeline_json: { btn: "btn-script-tab-pipeline", view: "script-drawer-view-pipeline", activeColor: "bg-purple-600" },
    manifest_json: { btn: "btn-script-tab-manifest", view: "script-drawer-view-manifest", activeColor: "bg-indigo-600" },
  };

  const actBase = "flex-1 py-1 px-1.5 font-bold rounded-lg text-white shadow transition flex items-center justify-center gap-1";
  const inactCls = "flex-1 py-1 px-1.5 font-medium text-slate-600 dark:text-gray-400 hover:text-white rounded-lg transition flex items-center justify-center gap-1";

  Object.entries(tabs).forEach(([k, cfg]) => {
    const btn = document.getElementById(cfg.btn);
    const view = document.getElementById(cfg.view);
    const isAct = (k === activeScriptDrawerTab);
    if (btn) {
      btn.className = isAct ? `${actBase} ${cfg.activeColor}` : inactCls;
    }
    if (view) {
      view.classList.toggle("hidden", !isAct);
    }
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
    } else {
      copyBtn.innerHTML = '<i class="fa-solid fa-copy"></i> <span>Copy Storyboard</span>';
      copyBtn.onclick = copyScriptDrawerContent;
    }
  }
}

async function openScriptDrawer(initialTab = "visual") {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  const drawer = document.getElementById("studio-script-drawer-modal");
  if (!drawer) return;

  const epId = vid.id || vid.episode_id || "EP-001";
  const chSlug = vid.channel_id || vid.channelId || (typeof selectedStudioChannel !== "undefined" ? selectedStudioChannel : "earth_serenade");

  if (!vid.screenplay || !vid.pipeline_state || !vid.user_inputs || !(vid.scenes?.length > 0)) {
    try {
      const uEmail = (typeof currentUser !== "undefined" && currentUser?.email) ? currentUser.email : "knpillutla@gmail.com";
      const res = await fetch(`/api/production/poll-artifacts?channel_id=${chSlug}&episode_id=${epId}&user_id=${encodeURIComponent(uEmail)}`);
      if (res.ok) {
        const data = await res.json();
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
  const scenes = script.scenes || vid.scenes || [];
  const pipelineState = vid.pipeline_state || { current_stage: vid.currentStage || 1, is_approved: Boolean(vid.is_approved), status: vid.status || "ready" };
  const manifest = vid.manifest || vid.script || {};
  const userInputs = vid.user_inputs || { prompt: vid.concept || vid.title, channel_id: chSlug, genre: vid.videoType || "relax/nature", episode_id: epId, duration_seconds: vid.durationSeconds || 5 };

  const setT = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setT("script-drawer-ep-id", `${epId} • Gemini 2.5 Director`);
  setT("script-drawer-title", script.title || vid.title || "Director Storyboard");
  setT("script-drawer-story", script.story_topic || vid.story_topic || vid.concept || "Master video production");
  setT("script-drawer-cluster", `Cluster: ${script.cluster || vid.cluster || vid.genre || "Ambient World"}`);
  setT("script-drawer-fps", `${script.recommended_fps || vid.recommended_fps || vid.fps || 24} FPS Cinematic`);
  setT("script-drawer-audio-tags", script.audio_tags || (script.audio_master?.suno_musical_tags) || vid.audio_tags || "ambient pad, 432hz acoustic soundscape");
  setT("script-drawer-scenes-count", `${scenes.length || 1} Scene${scenes.length > 1 ? 's' : ''}`);

  // Populate code blocks
  const inCode = document.getElementById("script-drawer-inputs-code");
  if (inCode) inCode.textContent = JSON.stringify(userInputs, null, 2);

  const spCode = document.getElementById("script-drawer-screenplay-code");
  if (spCode) spCode.textContent = JSON.stringify(vid.screenplay || script, null, 2);

  const plCode = document.getElementById("script-drawer-pipeline-code");
  if (plCode) plCode.textContent = JSON.stringify(pipelineState, null, 2);

  const mfCode = document.getElementById("script-drawer-manifest-code");
  if (mfCode) mfCode.textContent = JSON.stringify(manifest, null, 2);

  const listEl = document.getElementById("script-drawer-scenes-list");
  if (listEl) {
    if (scenes.length === 0) {
      listEl.innerHTML = `<div class="p-3 bg-slate-50 dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 text-center text-slate-500 text-[10px]">No detailed scene directives available.</div>`;
    } else {
      listEl.innerHTML = scenes.map((sc, i) => {
        const sNum = sc.scene_index || sc.scene_number || (i + 1);
        const sType = (sc.perspective_type || sc.shot_type || 'Wide Atmospheric').replace('_', ' ').toUpperCase();
        const vPrompt = sc.visual_prompt || sc.prompt || 'Scenic ambient view';
        const mPrompt = sc.motion_prompt || 'Locked tripod static camera, slow natural atmospheric motion';
        const sDur = sc.duration_seconds || vid.durationSeconds || 5;

        return `
        <div class="p-2.5 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl space-y-1.5 shadow-sm">
          <div class="flex items-center justify-between">
            <span class="text-[9px] font-bold font-mono text-amber-600 dark:text-amber-400 flex items-center gap-1">
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
              <span class="font-bold text-slate-700 dark:text-gray-300">Motion Directive (Wan 2.1 / Kling):</span>
              <p class="text-slate-600 dark:text-gray-400 leading-tight bg-white dark:bg-slate-950 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono text-[8px] select-all">${mPrompt}</p>
            </div>
          </div>
        </div>`;
      }).join("");
    }
  }

  switchScriptDrawerTab(initialTab);
  drawer.classList.remove("hidden");
}

function closeScriptDrawer() {
  document.getElementById("studio-script-drawer-modal")?.classList.add("hidden");
}

function copyScriptDrawerContent() {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  const script = vid.screenplay || vid.script || vid.manifest || {};
  const text = `Title: ${script.title || vid.title}\nStory: ${script.story_topic || vid.story_topic}\nAudio Tags: ${script.audio_tags || (script.audio_master?.suno_musical_tags) || ''}\n\nScenes:\n` +
    (script.scenes || []).map((s, i) => `Scene ${i+1} (${s.shot_type || 'Wide'}, ${s.duration_seconds || 5}s):\nVisual: ${s.visual_prompt}\nMotion: ${s.motion_prompt}`).join("\n\n");
  navigator.clipboard.writeText(text).then(() => {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast("Script copied to clipboard!");
  }).catch(() => {});
}

function copyScriptDrawerJson(type) {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  let target = null, name = "JSON";
  if (type === "user_inputs") { target = vid.user_inputs || {}; name = "user_inputs.json"; }
  else if (type === "screenplay") { target = vid.screenplay || vid.script || {}; name = "screenplay.json"; }
  else if (type === "pipeline_state") { target = vid.pipeline_state || {}; name = "pipeline_state.json"; }
  else { target = vid.manifest || vid.script || {}; name = "episode_manifest.json"; }

  const text = JSON.stringify(target, null, 2);
  navigator.clipboard.writeText(text).then(() => {
    if (typeof showProfileStatusToast === "function") showProfileStatusToast(`${name} copied to clipboard!`);
  }).catch(() => {});
}

function downloadScriptDrawerJson(type) {
  const vid = (typeof currentActiveInspectorEpisode !== "undefined") ? currentActiveInspectorEpisode : null;
  if (!vid) return;
  const epId = vid.id || vid.episode_id || "EP-001";
  let target = null, fn = `${epId}_screenplay.json`;
  if (type === "user_inputs") { target = vid.user_inputs || {}; fn = `${epId}_user_inputs.json`; }
  else if (type === "screenplay") { target = vid.screenplay || vid.script || {}; fn = `${epId}_screenplay.json`; }
  else if (type === "pipeline_state") { target = vid.pipeline_state || {}; fn = `${epId}_pipeline_state.json`; }
  else { target = vid.manifest || vid.script || {}; fn = `${epId}_manifest.json`; }

  const blob = new Blob([JSON.stringify(target, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = fn;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
