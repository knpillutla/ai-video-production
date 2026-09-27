// CineAI Studio: Real-Time Production Log Console Controller
let logConsoleEventSource = null;
let allConsoleLogs = [];
let activeConsoleLevelFilter = "ALL";
let isConsoleExpanded = false;
let isConsoleDrawerOpen = false;

function initLogConsole() {
  connectLogConsoleSSE();
  // Global hotkey: backtick (`) or Ctrl+` to toggle console
  document.addEventListener("keydown", (e) => {
    if (e.ctrlKey && e.key === "`") {
      e.preventDefault();
      toggleLogConsoleDrawer();
    }
  });
}

function connectLogConsoleSSE() {
  if (logConsoleEventSource) {
    try { logConsoleEventSource.close(); } catch (_) {}
  }

  const dot = document.getElementById("log-console-status-dot");
  const txt = document.getElementById("log-console-status-text");

  try {
    logConsoleEventSource = new EventSource("/api/logs/stream");

    logConsoleEventSource.onopen = () => {
      if (dot) dot.className = "w-2 h-2 rounded-full bg-emerald-500 animate-pulse";
      if (txt) { txt.textContent = "Streaming Live"; txt.className = "text-[10px] px-2 py-0.2 rounded-full bg-emerald-500/20 text-emerald-400 font-medium"; }
    };

    logConsoleEventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        appendLogToTerminal(data);
      } catch (err) {
        console.error("Error parsing SSE log event:", err);
      }
    };

    logConsoleEventSource.onerror = () => {
      if (dot) dot.className = "w-2 h-2 rounded-full bg-amber-500";
      if (txt) { txt.textContent = "Reconnecting..."; txt.className = "text-[10px] px-2 py-0.2 rounded-full bg-amber-500/20 text-amber-400 font-medium"; }
      setTimeout(connectLogConsoleSSE, 4000);
    };
  } catch (e) {
    console.error("SSE connection failed, falling back to REST poll:", e);
    fetchRecentLogsFallback();
  }
}

async function fetchRecentLogsFallback() {
  try {
    const res = await fetch("/api/logs?limit=100");
    if (res.ok) {
      const data = await res.json();
      if (data.logs) {
        data.logs.forEach(appendLogToTerminal);
      }
    }
  } catch (_) {}
}

function toggleLogConsoleDrawer(forceState) {
  const drawer = document.getElementById("studio-log-console-drawer");
  if (!drawer) return;
  isConsoleDrawerOpen = typeof forceState === "boolean" ? forceState : !isConsoleDrawerOpen;
  if (isConsoleDrawerOpen) {
    drawer.classList.remove("translate-y-full");
    scrollConsoleToBottom();
  } else {
    drawer.classList.add("translate-y-full");
  }
}

function toggleConsoleExpand() {
  const drawer = document.getElementById("studio-log-console-drawer");
  const btn = document.getElementById("btn-console-expand");
  if (!drawer) return;
  isConsoleExpanded = !isConsoleExpanded;
  if (isConsoleExpanded) {
    drawer.style.height = "75vh";
    if (btn) btn.innerHTML = '<i class="fa-solid fa-down-left-and-up-right-to-center text-[11px]"></i>';
  } else {
    drawer.style.height = "320px";
    if (btn) btn.innerHTML = '<i class="fa-solid fa-up-right-and-down-left-from-center text-[11px]"></i>';
  }
  scrollConsoleToBottom();
}

function appendLogToTerminal(entry) {
  if (!entry || !entry.message) return;
  allConsoleLogs.push(entry);
  if (allConsoleLogs.length > 2000) allConsoleLogs.shift();

  const countEl = document.getElementById("log-console-count");
  if (countEl) countEl.textContent = `${allConsoleLogs.length} logs`;

  // Check if matches active level filter
  if (!logMatchesFilter(entry)) return;

  const terminal = document.getElementById("log-console-terminal");
  const inspectorTerm = document.getElementById("inspector-console-terminal");
  const html = buildLogHtmlLine(entry);

  if (terminal) {
    const div = document.createElement("div");
    div.innerHTML = html;
    terminal.appendChild(div.firstElementChild || div);
  }
  if (inspectorTerm) {
    const div2 = document.createElement("div");
    div2.innerHTML = html;
    inspectorTerm.appendChild(div2.firstElementChild || div2);
  }

  const autoScroll = document.getElementById("log-console-autoscroll");
  if (!autoScroll || autoScroll.checked) {
    scrollConsoleToBottom();
  }
}

function buildLogHtmlLine(entry) {
  const time = entry.time_str || (entry.timestamp ? entry.timestamp.substring(11, 19) : "00:00:00");
  const msg = escapeConsoleHtml(entry.message);
  let lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-slate-800 text-slate-400">LOG</span>`;
  let textClass = "text-slate-300";

  if (msg.includes("[DECISION") || msg.includes("decision_")) {
    lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-purple-900/60 text-purple-300 border border-purple-500/30">DECISION</span>`;
    textClass = "text-purple-200 font-semibold";
  } else if (msg.includes("[STAGE") || msg.includes("starting_channel_job")) {
    lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-blue-900/60 text-blue-300 border border-blue-500/30">STAGE</span>`;
    textClass = "text-cyan-200 font-semibold";
  } else if (entry.level === "ERROR" || msg.includes("error") || msg.includes("failed")) {
    lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-red-900/60 text-red-300 border border-red-500/30">ERROR</span>`;
    textClass = "text-red-300";
  } else if (entry.level === "WARNING" || msg.includes("fallback") || msg.includes("warning")) {
    lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-amber-900/60 text-amber-300 border border-amber-500/30">WARN</span>`;
    textClass = "text-amber-200";
  } else if (entry.level === "INFO") {
    lvlBadge = `<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-500/30">INFO</span>`;
  }

  // Model tags highlighting
  let formattedMsg = msg
    .replace(/(FLUX 1\.1 Pro|FLUX Dev|FLUX\.1)/g, '<span class="text-blue-400 font-bold">$1</span>')
    .replace(/(Kling v3|Kling 4K|Wan 2\.1|Hunyuan)/g, '<span class="text-pink-400 font-bold">$1</span>')
    .replace(/(Suno v3\.5|Velvet binaural|432Hz)/g, '<span class="text-emerald-400 font-bold">$1</span>')
    .replace(/(FFmpeg|Single-Pass|CRF 22)/g, '<span class="text-yellow-400 font-bold">$1</span>');

  return `
    <div class="flex items-start gap-2 py-0.5 hover:bg-slate-900/60 px-1 rounded transition text-left font-mono">
      <span class="text-slate-500 select-none text-[10px] shrink-0">${time}</span>
      <span class="shrink-0">${lvlBadge}</span>
      <span class="${textClass} flex-1 break-words">${formattedMsg}</span>
    </div>
  `;
}

function escapeConsoleHtml(str) {
  if (!str) return "";
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function logMatchesFilter(entry) {
  const msg = (entry.message || "").toLowerCase();
  const searchInput = document.getElementById("log-console-search");
  const query = searchInput ? searchInput.value.toLowerCase().trim() : "";

  if (query && !msg.includes(query) && !(entry.level || "").toLowerCase().includes(query)) {
    return false;
  }

  if (activeConsoleLevelFilter === "ALL") return true;
  if (activeConsoleLevelFilter === "DECISION") return msg.includes("decision") || msg.includes("[decision");
  if (activeConsoleLevelFilter === "STAGE") return msg.includes("stage") || msg.includes("[stage") || msg.includes("starting_channel");
  if (activeConsoleLevelFilter === "ERROR") return entry.level === "ERROR" || msg.includes("error") || msg.includes("fail");
  return true;
}

function setConsoleLevelFilter(filter) {
  activeConsoleLevelFilter = filter;
  ["ALL", "DECISION", "STAGE", "ERROR"].forEach((lvl) => {
    const btn = document.getElementById(`filter-btn-${lvl}`);
    if (btn) {
      if (lvl === filter) {
        btn.className = "px-2 py-0.5 rounded font-bold bg-indigo-600 text-white";
      } else {
        btn.className = "px-2 py-0.5 rounded text-slate-400 hover:text-white";
      }
    }
  });
  renderFilteredConsoleLogs();
}

function filterConsoleLogs() {
  renderFilteredConsoleLogs();
}

function renderFilteredConsoleLogs() {
  const terminal = document.getElementById("log-console-terminal");
  const inspectorTerm = document.getElementById("inspector-console-terminal");
  if (!terminal && !inspectorTerm) return;

  const filtered = allConsoleLogs.filter(logMatchesFilter);
  const html = filtered.map(buildLogHtmlLine).join("");

  if (terminal) terminal.innerHTML = html || '<div class="text-slate-500 italic p-2">No matching logs found.</div>';
  if (inspectorTerm) inspectorTerm.innerHTML = html || '<div class="text-slate-500 italic p-2">No matching logs found.</div>';
  scrollConsoleToBottom();
}

function scrollConsoleToBottom() {
  const terminal = document.getElementById("log-console-terminal");
  if (terminal) terminal.scrollTop = terminal.scrollHeight;
  const inspectorTerm = document.getElementById("inspector-console-terminal");
  if (inspectorTerm) inspectorTerm.scrollTop = inspectorTerm.scrollHeight;
}

function clearConsoleLogs() {
  allConsoleLogs = [];
  const terminal = document.getElementById("log-console-terminal");
  if (terminal) terminal.innerHTML = '<div class="text-slate-500 italic">Log console cleared. Waiting for new production events...</div>';
  const inspectorTerm = document.getElementById("inspector-console-terminal");
  if (inspectorTerm) inspectorTerm.innerHTML = '<div class="text-slate-500 italic">Log console cleared.</div>';
  const countEl = document.getElementById("log-console-count");
  if (countEl) countEl.textContent = "0 logs";
  fetch("/api/logs", { method: "DELETE" }).catch(() => {});
}

function copyConsoleLogs() {
  const text = allConsoleLogs.map((l) => `[${l.timestamp || l.time_str || ''}] [${l.level || 'INFO'}] ${l.message || ''}`).join("\n");
  navigator.clipboard.writeText(text).then(() => {
    alert("Console logs copied to clipboard!");
  }).catch(() => {
    alert("Unable to copy logs to clipboard.");
  });
}

document.addEventListener("DOMContentLoaded", initLogConsole);
