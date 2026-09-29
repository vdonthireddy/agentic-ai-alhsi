// ALHSI Client Application - Real-time Agent Loop Interface & Feature Hub

let ws = null;
let currentState = null;
let metricChart = null;
let activeFilter = "all";
let searchQuery = "";

// DOM Elements
const wsBadge = document.getElementById("ws-badge");
const wsText = document.getElementById("ws-text");
const selectPreset = document.getElementById("select-preset");
const selectAgent = document.getElementById("select-agent");
const selectDelay = document.getElementById("select-delay");
const btnStart = document.getElementById("btn-start");
const btnPause = document.getElementById("btn-pause");
const btnStep = document.getElementById("btn-step");
const btnReset = document.getElementById("btn-reset");
const btnQuickCheat = document.getElementById("btn-quick-cheat");

// Modals & Triggers
const btnOpenGuide = document.getElementById("btn-open-guide");
const btnCloseGuide = document.getElementById("btn-close-guide");
const guideModal = document.getElementById("guide-modal");

const btnOpenVideo = document.getElementById("btn-open-video");
const btnCloseVideo = document.getElementById("btn-close-video");
const videoModal = document.getElementById("video-modal");

const btnOpenSecurity = document.getElementById("btn-open-security");
const btnCloseSecurity = document.getElementById("btn-close-security");
const securityModal = document.getElementById("security-modal");
const securityFeedback = document.getElementById("security-lab-feedback");

const btnOpenSettings = document.getElementById("btn-open-settings");
const btnCloseSettings = document.getElementById("btn-close-settings");
const settingsModal = document.getElementById("settings-modal");
const btnSaveSettings = document.getElementById("btn-save-settings");

const trialModal = document.getElementById("trial-modal");
const btnCloseTrial = document.getElementById("btn-close-trial");

// Editor Tab & Manual Human Mode
const editorTextarea = document.getElementById("editor-textarea");
const btnRunManual = document.getElementById("btn-run-manual");

// Phase Nodes
const nodes = {
  hypothesizing: document.getElementById("node-hypothesize"),
  modifying: document.getElementById("node-modify"),
  evaluating: document.getElementById("node-evaluate"),
  deciding: document.getElementById("node-decide"),
  committing: document.getElementById("node-commit"),
  reverting: document.getElementById("node-commit"),
};
const phaseStatusText = document.getElementById("phase-status-text");

// Tab Navigation
const tabButtons = {
  diff: document.getElementById("tab-btn-diff"),
  code: document.getElementById("tab-btn-code"),
  editor: document.getElementById("tab-btn-editor"),
  commits: document.getElementById("tab-btn-commits"),
  logs: document.getElementById("tab-btn-logs"),
};
const tabPanes = {
  diff: document.getElementById("tab-pane-diff"),
  code: document.getElementById("tab-pane-code"),
  editor: document.getElementById("tab-pane-editor"),
  commits: document.getElementById("tab-pane-commits"),
  logs: document.getElementById("tab-pane-logs"),
};

// Search & Filter
const inputSearch = document.getElementById("input-search");
const filterButtons = document.querySelectorAll(".filter-btn");

// Initialize Chart.js
function initChart() {
  const ctx = document.getElementById("metricChart").getContext("2d");
  metricChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [
        {
          label: "Trial Metric",
          data: [],
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          pointBackgroundColor: [],
          pointBorderColor: "#ffffff",
          pointRadius: 6,
          pointHoverRadius: 9,
          borderWidth: 2,
          tension: 0.2,
          fill: true,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (e, elements) => {
        if (elements.length > 0 && currentState && currentState.trials) {
          const idx = elements[0].index;
          openTrialModal(currentState.trials[idx]);
        }
      },
      interaction: {
        mode: "index",
        intersect: false,
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(15, 23, 42, 0.95)",
          titleColor: "#93c5fd",
          bodyColor: "#f1f5f9",
          borderColor: "rgba(255, 255, 255, 0.1)",
          borderWidth: 1,
          padding: 10,
          callbacks: {
            title: function (items) {
              const idx = items[0].dataIndex;
              if (currentState && currentState.trials && currentState.trials[idx]) {
                return `Trial #${idx + 1}: ${currentState.trials[idx].hypothesis.title}`;
              }
              return items[0].label;
            },
            label: function (item) {
              const idx = item.dataIndex;
              if (currentState && currentState.trials && currentState.trials[idx]) {
                const t = currentState.trials[idx];
                return [
                  `Metric: ${t.trial_metric !== null ? t.trial_metric : "Crashed/Tampered"}`,
                  `Status: ${t.status.toUpperCase()}`,
                  `Category: ${t.hypothesis.category}`,
                  `Click point to inspect trial`,
                ];
              }
              return `Value: ${item.formattedValue}`;
            },
          },
        },
      },
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { size: 10 } },
        },
        y: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { size: 10 } },
        },
      },
    },
  });
}

// Update Chart with Trial Points
function updateChart(state) {
  if (!metricChart || !state.trials) return;

  const labels = [];
  const data = [];
  const pointColors = [];

  state.trials.forEach((t) => {
    labels.push(`T#${t.trial_num}`);
    data.push(t.trial_metric !== null ? t.trial_metric : t.baseline_metric);

    if (t.status === "accepted") {
      pointColors.push("#10b981"); // green
    } else if (t.status === "rejected") {
      pointColors.push("#ef4444"); // red
    } else if (t.status === "crashed") {
      pointColors.push("#f59e0b"); // amber
    } else if (t.status === "tamper") {
      pointColors.push("#8b5cf6"); // purple
    } else {
      pointColors.push("#64748b");
    }
  });

  metricChart.data.labels = labels;
  metricChart.data.datasets[0].data = data;
  metricChart.data.datasets[0].pointBackgroundColor = pointColors;
  metricChart.update();
}

// Update Phase Diagram (Visual State Machine)
function updatePhaseNodes(phase) {
  Object.values(nodes).forEach((n) => {
    if (n) n.classList.remove("active");
  });

  phaseStatusText.textContent = `Phase: ${phase.toUpperCase()}`;

  if (phase in nodes && nodes[phase]) {
    nodes[phase].classList.add("active");
  }
}

// Format unified diff to colored HTML
function formatDiff(diffText) {
  if (!diffText || !diffText.trim()) {
    return '<div class="text-slate-400 italic">No modifications in this trial.</div>';
  }

  const lines = diffText.split("\n");
  const htmlLines = lines.map((line) => {
    const esc = line
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    if (line.startsWith("+") && !line.startsWith("+++")) {
      return `<div class="diff-line-add px-2 py-0.5">${esc}</div>`;
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      return `<div class="diff-line-del px-2 py-0.5">${esc}</div>`;
    } else if (line.startsWith("@@") || line.startsWith("diff") || line.startsWith("---") || line.startsWith("+++")) {
      return `<div class="diff-line-header px-2 py-0.5">${esc}</div>`;
    }
    return `<div class="px-2 py-0.5 text-slate-400">${esc}</div>`;
  });

  return htmlLines.join("");
}

// Open Trial Detail Inspector Modal
function openTrialModal(trial) {
  if (!trial) return;

  document.getElementById("inspect-trial-badge").textContent = `TRIAL #${trial.trial_num}`;
  document.getElementById("inspect-trial-title").textContent = trial.hypothesis.title;
  document.getElementById("inspect-category").textContent = trial.hypothesis.category;

  const outcomeElem = document.getElementById("inspect-outcome");
  outcomeElem.textContent = trial.status.toUpperCase();
  if (trial.status === "accepted") {
    outcomeElem.className = "font-bold text-emerald-400";
  } else if (trial.status === "rejected") {
    outcomeElem.className = "font-bold text-rose-400";
  } else if (trial.status === "tamper") {
    outcomeElem.className = "font-bold text-purple-400";
  } else {
    outcomeElem.className = "font-bold text-amber-400";
  }

  const deltaStr = trial.metric_delta !== null ? (trial.metric_delta > 0 ? `+${trial.metric_delta.toFixed(4)}` : trial.metric_delta.toFixed(4)) : "N/A";
  document.getElementById("inspect-delta").textContent = deltaStr;
  document.getElementById("inspect-commit").textContent = trial.commit_hash || "reverted (none)";
  document.getElementById("inspect-description").textContent = trial.hypothesis.description || "No description provided.";
  document.getElementById("inspect-diff").innerHTML = formatDiff(trial.diff);
  document.getElementById("inspect-logs").textContent = trial.logs || "No subprocess console output.";

  trialModal.classList.remove("hidden");
  if (window.lucide) lucide.createIcons();
}

// Render Lab Notebook with Search & Filters
function renderLabNotebook(trials) {
  const tableBody = document.getElementById("trials-table-body");
  if (!trials || trials.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="9" class="text-center py-6 text-slate-500 font-sans">No experiments recorded yet. Start the loop above!</td></tr>';
    return;
  }

  // Apply filters and search
  const filtered = trials.filter((t) => {
    if (activeFilter === "accepted" && t.status !== "accepted") return false;
    if (activeFilter === "rejected" && t.status !== "rejected") return false;
    if (activeFilter === "tamper" && t.status !== "tamper") return false;

    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      const matchTitle = (t.hypothesis.title || "").toLowerCase().includes(q);
      const matchCat = (t.hypothesis.category || "").toLowerCase().includes(q);
      if (!matchTitle && !matchCat) return false;
    }
    return true;
  });

  if (filtered.length === 0) {
    tableBody.innerHTML = '<tr><td colspan="9" class="text-center py-6 text-slate-500 font-sans">No experiments match the filter criteria.</td></tr>';
    return;
  }

  tableBody.innerHTML = filtered
    .map((t) => {
      let statusBadge = "";
      if (t.status === "accepted") {
        statusBadge = '<span class="px-1.5 py-0.5 rounded text-[10px] bg-emerald-950 text-emerald-400 border border-emerald-800">ACCEPTED</span>';
      } else if (t.status === "rejected") {
        statusBadge = '<span class="px-1.5 py-0.5 rounded text-[10px] bg-rose-950 text-rose-400 border border-rose-800">REJECTED</span>';
      } else if (t.status === "crashed") {
        statusBadge = '<span class="px-1.5 py-0.5 rounded text-[10px] bg-amber-950 text-amber-400 border border-amber-800">CRASHED</span>';
      } else if (t.status === "tamper") {
        statusBadge = '<span class="px-1.5 py-0.5 rounded text-[10px] bg-purple-950 text-purple-400 border border-purple-800">TAMPER CAUGHT</span>';
      }

      const deltaStr = t.metric_delta !== null ? (t.metric_delta > 0 ? `+${t.metric_delta.toFixed(4)}` : t.metric_delta.toFixed(4)) : "--";
      const commitStr = t.commit_hash ? `<span class="text-purple-400 font-bold">${t.commit_hash}</span>` : '<span class="text-slate-600">reverted</span>';

      return `
        <tr class="hover:bg-slate-800/50 transition cursor-pointer" onclick="inspectTrialByNum(${t.trial_num})">
          <td class="py-2.5 px-3 text-slate-400">#${t.trial_num}</td>
          <td class="py-2.5 px-3 text-slate-200 font-sans font-medium">${t.hypothesis.title}</td>
          <td class="py-2.5 px-3 text-slate-400 font-sans">${t.hypothesis.category}</td>
          <td class="py-2.5 px-3 text-white font-bold">${t.trial_metric !== null ? t.trial_metric.toFixed(4) : "N/A"}</td>
          <td class="py-2.5 px-3 ${t.status === "accepted" ? "text-emerald-400" : "text-rose-400"}">${deltaStr}</td>
          <td class="py-2.5 px-3 font-sans">${statusBadge}</td>
          <td class="py-2.5 px-3">${commitStr}</td>
          <td class="py-2.5 px-3 text-slate-500 font-sans">${t.elapsed_sec}s</td>
          <td class="py-2.5 px-3 text-right font-sans">
            <button class="text-blue-400 hover:text-blue-300 text-xs font-semibold">Details →</button>
          </td>
        </tr>
      `;
    })
    .reverse()
    .join("");
}

// Global inspect helper
window.inspectTrialByNum = function (trialNum) {
  if (currentState && currentState.trials) {
    const t = currentState.trials.find((x) => x.trial_num === trialNum);
    if (t) openTrialModal(t);
  }
};

// Render full state to UI
function renderState(state) {
  currentState = state;

  // Header & controls
  selectPreset.value = state.preset.id;
  if (state.agent_type) {
    selectAgent.value = state.agent_type;
  }
  document.getElementById("active-filename-badge").textContent = state.preset.target_file;

  // Running status & buttons
  if (state.running && !state.paused) {
    btnStart.classList.add("hidden");
    btnPause.classList.remove("hidden");
    btnStep.disabled = true;
    btnStep.classList.add("opacity-50", "cursor-not-allowed");
  } else {
    btnStart.classList.remove("hidden");
    btnPause.classList.add("hidden");
    btnStep.disabled = false;
    btnStep.classList.remove("opacity-50", "cursor-not-allowed");
  }

  // Phase diagram
  updatePhaseNodes(state.phase);

  // Top Stat Cards
  document.getElementById("stat-best-metric").textContent = state.baseline_metric.toFixed(4);
  document.getElementById("stat-unit").textContent = state.preset.unit;
  document.getElementById("stat-baseline-metric").textContent = `${state.preset.baseline_metric.toFixed(4)} ${state.preset.unit}`;
  document.getElementById("stat-total-trials").textContent = state.total_trials;
  document.getElementById("stat-accepted").textContent = `${state.accepted_count} Kept`;
  document.getElementById("stat-rejected").textContent = `${state.rejected_count} Discarded`;

  const rate = state.total_trials > 0 ? ((state.accepted_count / state.total_trials) * 100).toFixed(1) : "0.0";
  document.getElementById("stat-accept-rate").textContent = `${rate}%`;

  document.getElementById("stat-commits-count").textContent = state.recent_commits.length;
  document.getElementById("stat-latest-sha").textContent = state.recent_commits[0] ? state.recent_commits[0].hash : "--";

  // Subtitle
  document.getElementById("chart-subtitle").textContent = `Target: ${state.preset.name} (${state.preset.metric_name} - ${state.preset.lower_is_better ? "lower" : "higher"} is better)`;

  // Latest Trial Banner
  if (state.current_trial) {
    const ct = state.current_trial;
    document.getElementById("current-trial-title").textContent = ct.hypothesis.title;
    document.getElementById("current-trial-desc").textContent = ct.hypothesis.description;
    document.getElementById("current-trial-category").textContent = ct.hypothesis.category;
    document.getElementById("current-trial-impact").textContent = ct.hypothesis.expected_impact;

    const deltaElem = document.getElementById("current-trial-delta");
    if (ct.metric_delta !== null) {
      const sign = ct.metric_delta > 0 ? "+" : "";
      deltaElem.textContent = `${sign}${ct.metric_delta.toFixed(4)} ${state.preset.unit}`;
      deltaElem.className = ct.status === "accepted" ? "font-medium font-mono text-emerald-400" : "font-medium font-mono text-rose-400";
    } else {
      deltaElem.textContent = ct.status === "tamper" ? "REWARD HACK DETECTED" : "CRASH / REVERT";
      deltaElem.className = ct.status === "tamper" ? "font-medium font-mono text-purple-400" : "font-medium font-mono text-amber-400";
    }

    const badge = document.getElementById("current-trial-badge");
    badge.textContent = ct.status.toUpperCase();
    if (ct.status === "accepted") {
      badge.className = "px-2 py-0.5 text-xs font-semibold rounded bg-emerald-900/60 text-emerald-300 border border-emerald-700";
    } else if (ct.status === "rejected") {
      badge.className = "px-2 py-0.5 text-xs font-semibold rounded bg-rose-900/60 text-rose-300 border border-rose-700";
    } else if (ct.status === "crashed") {
      badge.className = "px-2 py-0.5 text-xs font-semibold rounded bg-amber-900/60 text-amber-300 border border-amber-700";
    } else if (ct.status === "tamper") {
      badge.className = "px-2 py-0.5 text-xs font-semibold rounded bg-purple-900/60 text-purple-300 border border-purple-700";
    }

    // Update diff viewer
    document.getElementById("diff-content").innerHTML = formatDiff(ct.diff);
    document.getElementById("logs-content").textContent = ct.logs || "Execution completed without console output.";
  }

  // Update Golden Code Tab
  document.getElementById("code-content").textContent = state.current_code || "No code available.";

  // Update in-browser Sandbox Editor if not currently focused by user
  if (document.activeElement !== editorTextarea) {
    editorTextarea.value = state.current_code || "";
  }

  // Update Git Commits Tab
  const commitsContainer = document.getElementById("commits-list");
  if (state.recent_commits && state.recent_commits.length > 0) {
    commitsContainer.innerHTML = state.recent_commits
      .map(
        (c) => `
      <div class="p-2.5 rounded bg-slate-900/70 border border-slate-800 flex items-start justify-between">
        <div class="space-y-0.5">
          <div class="font-mono text-purple-300 font-semibold">${c.hash} <span class="text-slate-400 font-normal font-sans">- ${c.relative_time}</span></div>
          <div class="text-slate-200">${c.message.split("\n")[0]}</div>
        </div>
        <span class="text-[10px] text-slate-500 font-mono">${c.author}</span>
      </div>
    `
      )
      .join("");
  } else {
    commitsContainer.innerHTML = '<div class="text-slate-400 italic">No commits in repository yet.</div>';
  }

  // Update Lab Notebook Table
  renderLabNotebook(state.trials);

  // Update chart
  updateChart(state);

  // Refresh lucide icons
  if (window.lucide) {
    lucide.createIcons();
  }
}

// WebSocket Connection
function connectWebSocket() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${protocol}//${window.location.host}/ws`;

  ws = new WebSocket(wsUrl);

  ws.onopen = () => {
    wsBadge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-950 text-emerald-300 border border-emerald-800";
    wsBadge.firstElementChild.className = "w-2 h-2 rounded-full bg-emerald-400";
    wsText.textContent = "Live Stream Connected";
  };

  ws.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "state_update") {
        renderState(msg.data);
      }
    } catch (e) {
      console.error("Error parsing WS message:", e);
    }
  };

  ws.onclose = () => {
    wsBadge.className = "flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-800 text-slate-400 border border-slate-700";
    wsBadge.firstElementChild.className = "w-2 h-2 rounded-full bg-amber-400 animate-pulse";
    wsText.textContent = "Reconnecting...";
    setTimeout(connectWebSocket, 2000);
  };
}

// Fetch initial state via REST
async function fetchState() {
  try {
    const res = await fetch("/api/state");
    if (res.ok) {
      const data = await res.json();
      renderState(data);
    }
  } catch (e) {
    console.error("Failed to fetch state:", e);
  }
}

// Periodic State Polling (Ensures UI updates even if WS is interrupted or blocked)
setInterval(async () => {
  if (currentState && currentState.running) {
    await fetchState();
  }
}, 1000);

// Event Listeners for Loop Controls
btnStep.addEventListener("click", async () => {
  btnStep.disabled = true;
  const originalHtml = btnStep.innerHTML;
  btnStep.innerHTML = "<span>Running...</span>";
  try {
    const res = await fetch("/api/step", { method: "POST" });
    if (!res.ok) {
      const err = await res.json();
      console.warn("Step request:", err.detail);
    }
    await fetchState();
  } catch (e) {
    console.error("Step execution error:", e);
  } finally {
    btnStep.disabled = false;
    btnStep.innerHTML = originalHtml;
    if (window.lucide) lucide.createIcons();
  }
});

btnStart.addEventListener("click", async () => {
  const delay = parseFloat(selectDelay.value) || 1.0;
  btnStart.classList.add("hidden");
  btnPause.classList.remove("hidden");
  phaseStatusText.textContent = "Phase: STARTING...";
  try {
    await fetch("/api/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ max_trials: 30, delay_sec: delay }),
    });
    await fetchState();
  } catch (err) {
    console.error("Failed to start loop:", err);
  }
});

btnPause.addEventListener("click", async () => {
  btnPause.classList.add("hidden");
  btnStart.classList.remove("hidden");
  try {
    await fetch("/api/pause", { method: "POST" });
    await fetchState();
  } catch (err) {
    console.error("Failed to pause loop:", err);
  }
});

btnReset.addEventListener("click", async () => {
  btnReset.disabled = true;
  const presetId = selectPreset.value;
  const agentType = selectAgent.value;
  try {
    await fetch("/api/reset", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ preset_id: presetId, agent_type: agentType }),
    });
    await fetchState();
  } catch (err) {
    console.error("Failed to reset:", err);
  } finally {
    btnReset.disabled = false;
  }
});

selectPreset.addEventListener("change", async () => {
  await fetch("/api/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset_id: selectPreset.value, agent_type: selectAgent.value }),
  });
  await fetchState();
});

selectAgent.addEventListener("change", async () => {
  await fetch("/api/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset_id: selectPreset.value, agent_type: selectAgent.value }),
  });
  await fetchState();
});

// Manual Human Sandbox Execution (Software 1.0 vs 3.0)
btnRunManual.addEventListener("click", async () => {
  const userCode = editorTextarea.value;
  btnRunManual.disabled = true;
  btnRunManual.innerHTML = "<span>Benchmarking in Harness...</span>";
  try {
    const res = await fetch("/api/custom-trial", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        code: userCode,
        title: "Manual Human Optimization",
        description: "User modified code in in-browser editor to test hypothesis against the harness.",
        category: "software_1.0_human",
      }),
    });
    const trial = await res.json();
    await fetchState();
    openTrialModal(trial);
  } catch (e) {
    console.error("Error executing manual trial:", e);
  } finally {
    btnRunManual.disabled = false;
    btnRunManual.innerHTML = '<i data-lucide="play" class="w-3.5 h-3.5"></i><span>Run My Code in Harness</span>';
    if (window.lucide) lucide.createIcons();
  }
});

// Quick Cheat Button
btnQuickCheat.addEventListener("click", async () => {
  selectAgent.value = "cheat";
  await fetch("/api/reset", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ preset_id: selectPreset.value, agent_type: "cheat" }),
  });
  await fetchState();
  setTimeout(async () => {
    const res = await fetch("/api/step", { method: "POST" });
    const trial = await res.json();
    await fetchState();
    openTrialModal(trial);
  }, 200);
});

// Attack Simulator Lab Launchers
document.querySelectorAll(".btn-launch-attack").forEach((btn) => {
  btn.addEventListener("click", async (e) => {
    const attackType = e.target.getAttribute("data-attack");
    btn.disabled = true;
    btn.textContent = "Attacking...";
    try {
      const res = await fetch("/api/cheat-test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ attack_type: attackType }),
      });
      const trial = await res.json();
      await fetchState();
      securityFeedback.classList.remove("hidden");
      securityFeedback.innerHTML = `
        <div class="text-rose-400 font-bold">⚠️ ATTACK INTERCEPTED BY HARNESS</div>
        <div><b>Target Attack:</b> ${attackType}</div>
        <div><b>Outcome:</b> ${trial.status.toUpperCase()}</div>
        <div><b>Reason:</b> ${trial.rejection_reason || "Anti-tamper violation"}</div>
        <div class="text-slate-400 mt-1">Harness automatically restored golden baseline via git.</div>
      `;
    } catch (err) {
      console.error(err);
    } finally {
      btn.disabled = false;
      btn.textContent = "Launch";
    }
  });
});

// Save Settings Modal
btnSaveSettings.addEventListener("click", async () => {
  const geminiKey = document.getElementById("input-gemini-key").value;
  const openaiKey = document.getElementById("input-openai-key").value;
  const ollamaHost = document.getElementById("input-ollama-host").value;
  await fetch("/api/settings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      gemini_api_key: geminiKey || null,
      openai_api_key: openaiKey || null,
      ollama_host: ollamaHost || null,
    }),
  });
  settingsModal.classList.add("hidden");
  alert("Settings saved successfully!");
});

// Tab Switching
Object.keys(tabButtons).forEach((tabKey) => {
  tabButtons[tabKey].addEventListener("click", () => {
    Object.keys(tabButtons).forEach((k) => {
      tabButtons[k].classList.remove("active", "bg-blue-600", "text-white");
      tabButtons[k].classList.add("bg-slate-800", "text-slate-300");
      tabPanes[k].classList.add("hidden");
    });
    tabButtons[tabKey].classList.add("active", "bg-blue-600", "text-white");
    tabButtons[tabKey].classList.remove("bg-slate-800", "text-slate-300");
    tabPanes[tabKey].classList.remove("hidden");
  });
});

// Search & Filter Listeners
inputSearch.addEventListener("input", (e) => {
  searchQuery = e.target.value.trim();
  if (currentState && currentState.trials) {
    renderLabNotebook(currentState.trials);
  }
});

filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => {
      b.classList.remove("active", "bg-blue-600", "text-white");
      b.classList.add("text-slate-400");
    });
    btn.classList.add("active", "bg-blue-600", "text-white");
    btn.classList.remove("text-slate-400");
    activeFilter = btn.getAttribute("data-filter");
    if (currentState && currentState.trials) {
      renderLabNotebook(currentState.trials);
    }
  });
});

// Modal Show/Hide
btnOpenGuide.addEventListener("click", () => guideModal.classList.remove("hidden"));
btnCloseGuide.addEventListener("click", () => guideModal.classList.add("hidden"));
guideModal.addEventListener("click", (e) => {
  if (e.target === guideModal) guideModal.classList.add("hidden");
});

btnOpenVideo.addEventListener("click", () => videoModal.classList.remove("hidden"));
btnCloseVideo.addEventListener("click", () => videoModal.classList.add("hidden"));
videoModal.addEventListener("click", (e) => {
  if (e.target === videoModal) videoModal.classList.add("hidden");
});

btnOpenSecurity.addEventListener("click", () => securityModal.classList.remove("hidden"));
btnCloseSecurity.addEventListener("click", () => securityModal.classList.add("hidden"));
securityModal.addEventListener("click", (e) => {
  if (e.target === securityModal) securityModal.classList.add("hidden");
});

btnOpenSettings.addEventListener("click", () => settingsModal.classList.remove("hidden"));
btnCloseSettings.addEventListener("click", () => settingsModal.classList.add("hidden"));
settingsModal.addEventListener("click", (e) => {
  if (e.target === settingsModal) settingsModal.classList.add("hidden");
});

btnCloseTrial.addEventListener("click", () => trialModal.classList.add("hidden"));
trialModal.addEventListener("click", (e) => {
  if (e.target === trialModal) trialModal.classList.add("hidden");
});

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  initChart();
  fetchState();
  connectWebSocket();
  if (window.lucide) {
    lucide.createIcons();
  }
});
