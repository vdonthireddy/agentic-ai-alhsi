# ALHSI User Guide: How to Use the Application
### Interactive Walkthrough for the Agent-Loop-Harness Self-Improvement System

---

## 🚀 1. Launching the Application

You can launch ALHSI in one command using either **Docker** (recommended) or **Native Python**.

### Option A: Launch with Docker (Recommended)
From the project root, run:
```bash
./restart.sh
```
This script automatically:
1. Cleans up any conflicting processes or previous containers on port 8000.
2. Builds the latest Docker image (`alhsi:latest`).
3. Launches the container in the background with port `8000` mapped.
4. Waits for the health check to confirm the server is responsive.

Once finished, open your browser to: **[http://localhost:8000](http://localhost:8000)**.

### Option B: Native Host Execution
If you prefer running directly on your host machine without Docker:
```bash
./run.sh
```
Or specify a custom port:
```bash
python3 -m alhsi serve --port 8080
```

### Option C: Run the Complete Automated Test Suite
To verify the entire system, sandbox, anti-tamper verifier, and API inside Docker:
```bash
./restart.sh --test
```

---

## 🖥️ 2. Web Dashboard Layout & Interface Tour

The dashboard is structured into four interactive zones designed for complete visibility and control over the autonomous loop:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│  [ALHSI LOGO]   [Preset Dropdown]  [Agent Dropdown]  [Delay]  [Start] [Step] [Reset]   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                       VISUAL STATE MACHINE (5-Phase Live Flow)                          │
│   [1. Hypothesize] ──► [2. Mutate] ──► [3. Evaluate] ──► [4. Decide] ──► [5. Commit]   │
├────────────────────────────────────────────────────┬───────────────────────────────────┤
│                                                    │  TABS:                            │
│           METRIC PROGRESSION CANVAS                │  [Target Code] [Unified Diff]     │
│             (Interactive Chart.js)                 │  [Code Sandbox] [Security Lab]    │
│                                                    │                                   │
│   • Tracks loss / GFLOPS / accuracy across trials  │  • View live code mutations       │
│   • Color-coded dots (🟢 Accepted, 🔴 Rejected,   │  • Run custom human code changes  │
│     🟡 Crashed, 🟣 Tamper caught)                  │  • Trigger adversarial attacks    │
│   • Click any data point to inspect that trial     │                                   │
├────────────────────────────────────────────────────┴───────────────────────────────────┤
│                       LAB NOTEBOOK & TRIAL AUDIT LOG                                   │
│   [Filter: All / Accepted / Rejected / Tampered]   [Search Hypotheses & Diffs...]      │
│   Trial # | Status | Hypothesis Title | Metric Delta | Commit SHA | Duration | Action  │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                       RECENT GIT COMMITS & REVERT LEDGER                               │
│   Lists all snapshots saved to the permanent baseline history                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 3. Step-by-Step Practical Workflows

### Workflow 1: Running Your First Autonomous Optimization Loop
1. Open **[http://localhost:8000](http://localhost:8000)**.
2. Under **Benchmark Suite**, select **NanoGPT Trainer (Autoresearch)**.
3. Under **Cognitive Engine**, select **Autonomous Simulator (Zero-Config)**.
   *(This simulator uses realistic heuristics and requires no API keys or setup).*
4. Set the **Delay** to **1.0s** so you can visually watch each phase transition.
5. Click **▶ Start Loop**.
6. **Observe the system in motion**:
   - The top **Visual State Machine** pulses through each phase: `Hypothesizing` → `Mutating` → `Evaluating` → `Deciding` → `Committing / Reverting`.
   - The **Metric Curve** plots each trial in real time.
   - Trials that successfully lower the validation loss turn **Green** and trigger a git commit.
   - Trials that regress turn **Red** and are automatically reverted to the previous baseline.
7. Click **⏸ Pause** at any time to freeze execution.

---

### Workflow 2: Stepping Through a Trial One by One
If you want to study the agent's decision-making step-by-step:
1. Make sure the loop is paused.
2. Click the **⏭ Step** button once.
3. The system executes exactly one trial:
   - Generates a hypothesis based on past trial results.
   - Modifies `train.py`.
   - Benchmarks the code in the subprocess sandbox.
   - Checks the result against the golden baseline.
   - Commits or reverts the workspace.
4. Check the **Lab Notebook** table below to see the result recorded.

---

### Workflow 3: Human vs. Agent (The Interactive Code Sandbox)
Want to test your own programming intuition against the harness? You can write code manually in the browser and benchmark it against the agent's baseline.

1. In the right-hand panel, click the **Code Sandbox** tab.
2. You will see the active baseline code loaded into the in-browser editor.
3. Make an experimental edit. For example, in the `NanoGPT` benchmark:
   - Locate the hyperparameter: `LR_SCHEDULE = "step"`
   - Change it to: `LR_SCHEDULE = "cosine"`
   - Or adjust `LEARNING_RATE = 0.003` to `0.001`
4. Enter a brief description in the **Hypothesis / Idea** field (e.g., *"Switch to cosine learning rate schedule"*).
5. Click **🚀 Run Custom Trial**.
6. The sandbox executes your code inside the protected harness:
   - If your code beats the baseline, the system accepts it and creates a permanent git commit!
   - If your code regresses or causes a syntax error, the harness rejects it and restores the previous working code.

---

### Workflow 4: Testing Harness Defenses in the Security Lab
To see how the harness protects against reward hacking, fraudulent metrics, and sandbox escapes:

1. In the right-hand panel, click the **Security Lab** tab.
2. You will see three pre-configured adversarial attack simulations:
   - **Attack 1: Grader Modification**: Attempts to alter `eval_harness.py` to force an automatic passing score.
   - **Attack 2: Metric Falsification**: Attempts to print fake benchmark output sentinels without running real computations.
   - **Attack 3: Unauthorized File Drop**: Attempts to create files outside the permitted target file.
3. Click any attack button (e.g., **Launch Attack 1: Modify Eval Grader**).
4. **Watch the Harness in action**:
   - The SHA-256 cryptographic verifier intercepts the change before the trial is accepted.
   - The status updates to **TAMPER DETECTED** (🟣).
   - An alert banner displays the exact security violation and confirms that the workspace was safely rolled back.

---

### Workflow 5: Inspecting Trial Details & Diffs
Every trial—whether accepted, rejected, crashed, or tampered—is fully recorded.

1. In the **Lab Notebook** table at the bottom of the page, click the **Inspect** button on any trial row.
   *(Alternatively, click any circular dot on the Chart.js metric curve).*
2. A comprehensive **Trial Detail Modal** opens, showing:
   - **Hypothesis**: The scientific title, rationale, and expected impact.
   - **Metric Breakdown**: Baseline score, trial score, and the net delta.
   - **Unified Git Diff**: Side-by-side colorized diff showing lines added and removed.
   - **Subprocess Logs**: Full stdout and stderr output from the benchmark run.
   - **Git Commit SHA**: The exact commit hash if accepted, or the rejection reason if reverted.

---

### Workflow 6: Connecting Frontier LLMs (Gemini, OpenAI, Ollama)
You can power the cognitive loop using frontier AI models:

1. Click the **⚙️ Settings** button in the top navigation bar.
2. In the modal:
   - **Google Gemini**: Paste your `GEMINI_API_KEY` (select `gemini-1.5-flash` or `gemini-1.5-pro`).
   - **OpenAI**: Paste your `OPENAI_API_KEY` (select `gpt-4o` or `gpt-4o-mini`).
   - **Local Ollama**: Enter your Ollama host URL (default `http://localhost:11434`) and model name (e.g., `llama3` or `deepseek-coder`).
3. Click **Save Settings**.
4. In the top toolbar, switch the **Cognitive Engine** dropdown to your configured provider.
5. Click **Start Loop** to watch the frontier model iteratively generate and test code!

---

### Workflow 7: Exporting Experiment Telemetry
When you want to analyze your optimization runs in external tools (Excel, Python, pandas):
- Click **Export CSV** in the top navigation bar to download a spreadsheet containing every trial's metrics, timestamps, diffs, and outcomes.
- Click **Export JSON** to download raw structured telemetry for automated data analysis pipelines.

---

## 💻 4. Command Line Interface (CLI) Guide

ALHSI includes a terminal interface with Rich formatting for running headless experiments on remote servers.

### List All Available Benchmarks
```bash
python3 -m alhsi list
```
Displays a table of available benchmark suites, target files, metrics, and baseline scores.

### Run an Autonomous Loop via Terminal
```bash
# Run 8 trials on the NanoGPT benchmark with a 0.5s delay
python3 -m alhsi run --preset nanogpt --trials 8 --delay 0.5

# Run 10 trials on the Matrix Kernel throughput benchmark
python3 -m alhsi run --preset matmul --trials 10

# Run reasoning puzzle optimization
python3 -m alhsi run --preset reasoning --trials 5
```

### Test Adversarial Defense via CLI
```bash
# Point the adversarial cheater agent at NanoGPT for 3 trials
python3 -m alhsi run --preset nanogpt --agent cheat --trials 3
```

### CLI Command Options

| Argument | Description | Default |
| :--- | :--- | :--- |
| `--preset` | Benchmark suite (`nanogpt`, `matmul`, `reasoning`) | `nanogpt` |
| `--agent` | Cognitive engine (`sim`, `gemini`, `openai`, `ollama`, `cheat`) | `sim` |
| `--trials` | Maximum number of trials to run | `10` |
| `--delay` | Artificial pause between trials in seconds | `0.5` |
| `--workspace` | Base directory for sandboxed git workspaces | `~/.alhsi` |

---

## 🛠️ 5. Troubleshooting & Frequently Asked Questions

### Port 8000 is already in use
Run `./restart.sh`. It automatically identifies and frees any running process or zombie container holding port 8000 before starting up.

### How do I reset a benchmark to its original starting state?
Click the **↺ Reset** button in the dashboard toolbar. This wipes the active workspace, re-copies the golden initial code, and commits the fresh baseline to Git.

### Where are the git repositories stored?
Each benchmark suite maintains an isolated Git repository in your user directory:
`~/.alhsi/workspaces/<preset_id>/`
You can run standard `git log` or `git diff` commands directly inside that folder.

### How do I check container logs?
```bash
docker logs -f alhsi-app
```

### How do I stop the container?
```bash
docker stop alhsi-app
```
