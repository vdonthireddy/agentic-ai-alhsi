# ALHSI: Agent Loop Harness Self-Improvement

> **Interactive Implementation of the Autonomous Agent Loop & Software 3.0 Workflow**  
> An autonomous research and optimization system showcasing recursive code mutation, immutable verification harnesses, and git-backed evaluation loops.

---

## 🌟 The Core Paradigm: Software 3.0 & The Autonomous Agent Loop

In modern autonomous systems and self-improving AI development, code creation has transitioned across three major eras:

| Era | How Code is Created | Role of the Human Engineer |
| :--- | :--- | :--- |
| **Software 1.0** | Humans write explicit algorithms, control flow, and syntax (C++, Python). | **Coder:** Writes lines of instructions. |
| **Software 2.0** | Neural network weights are optimized via gradient descent. | **Curator:** Writes loss functions & collects datasets. |
| **Software 3.0** | Autonomous AI agent loops write, mutate, test, and optimize software. | **Harness Engineer:** Builds the immutable verification harness, objective metrics, and sandboxes. |

```
                       ┌──────────────────────────────────────────────┐
                       │          THE AUTONOMOUS AGENT LOOP           │
                       └──────────────────────────────────────────────┘
                                               │
                        ┌──────────────────────▼─────────────────────┐
                        │              1. Hypothesize                │
                        │   Agent analyzes experiment history, logs, │
                        │        diffs, and proposes an idea         │
                        └──────────────────────┬─────────────────────┘
                                               │
                        ┌──────────────────────▼─────────────────────┐
                        │             2. Mutate Code                 │
                        │ Agent writes code change to target file    │
                        │       (e.g., train.py / kernel.py)         │
                        └──────────────────────┬─────────────────────┘
                                               │
 ┌─────────────────────────────────────────────▼────────────────────────────────────────────┐
 │                                THE IMMUTABLE HARNESS                                     │
 │                                                                                          │
 │  3. Sandbox Execution:                                                                   │
 │     Protected subprocess benchmarks execution with timeout & anti-tamper guards.         │
 │                                                                                          │
 │  4. Objective Verification:                                                              │
 │     Measures primary metric (val_loss, GFLOPS, test accuracy).                          │
 │     Runs cryptographic checks ensuring test assertions & grader were not modified.       │
 └─────────────────────────────────────────────┬────────────────────────────────────────────┘
                                               │
                        ┌──────────────────────▼─────────────────────┐
                        │             5. Decision Rule               │
                        └──────────────┬─────────────────────────────┘
                                       │
                    Improved? ─────────┴───────── Worse / Crashed / Tampered?
                       │                                    │
                       ▼                                    ▼
             [ ACCEPTED ]                               [ REJECTED ]
          git commit snapshot                        git checkout / revert
          Update golden baseline                     Restore last baseline
                       │                                    │
                       └─────────────────┬──────────────────┘
                                         │
                                         ▼
                            Repeat Loop for Next Trial
```

---

## 🔬 The Overnight Autoresearch Story

In recursive self-improvement demonstrations, an autonomous agent is pointed at a `train.py` GPT training codebase:
1. **The Setup**: The agent has write access only to `train.py`, while the evaluation harness, data loader, and test metrics are locked.
2. **The Run**: The loop runs autonomously overnight through dozens of trials.
3. **The Result**: The agent discovers genuine optimizations—including obscure bugs in the attention mechanism that human inspection missed over months of development—yielding measurable speedups in training.
4. **The Principle**: *"When the agent fails, don't just tweak the prompt. Engineer the harness."*

---

## 🚀 Features of this Application

- **Visual State Machine**: Real-time interactive display showing each stage of the loop (`Hypothesize` → `Mutate` → `Evaluate` → `Decide` → `Commit/Revert`).
- **Interactive Metric Curve**: Real-time Chart.js tracking primary metrics across trials, color-coded by outcome (🟢 Accepted, 🔴 Rejected, 🟡 Crashed, 🟣 Tamper caught).
- **Integrated Git Engine**: Every accepted trial is committed with rich metadata and SHA-1 hash; every regression or crash is cleanly reverted.
- **Harness Security & Anti-Cheat Demonstration**:
  - Cryptographic checksum verification of all non-target files.
  - Subprocess sandboxing with timeout protection.
  - One-click button to launch an **Adversarial Cheater Agent** demonstrating how the Harness intercepts reward hacking.
- **Multi-Benchmark Suites**:
  1. `nanogpt`: GPT-2 micro-transformer training scenario (optimizing `val_loss`, tokens/sec, attention scaling, cosine schedules).
  2. `matmul`: Computational kernel throughput (optimizing `gflops` and latency while enforcing mathematical matrix correctness).
  3. `reasoning`: Cognitive agent prompt & chain-of-thought optimizer against a locked puzzle test suite.
- **Multiple Cognitive Engines**:
  - **Autonomous Simulator** (instant, zero-config, out-of-the-box).
  - **Live LLM Agents** (Google Gemini, OpenAI GPT-4o, Local Ollama).
  - **Adversarial Cheater Agent** (harness defense testing).
- **Dual Interfaces**: Full-featured Web Dashboard + Terminal CLI with Rich formatting.

---

## ⚡ Quickstart

### 1. Launch with `restart.sh` (Docker by default)

```bash
# Clean restart inside Docker container (builds and runs container)
./restart.sh

# Or restart natively on the host
./restart.sh --local

# Or run the complete test suite inside the container
./restart.sh --test
```

### 2. Using Docker / Docker Compose directly

```bash
# Start with docker-compose
docker compose up -d --build

# View container logs
docker logs -f alhsi-app

# Stop container
docker compose down
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 3. Native Python Host Execution

```bash
# Using the quickstart script
./run.sh

# Or directly with python
python3 -m alhsi serve --port 8000
```

### 4. Run via Command Line Interface (CLI)

```bash
# List available benchmarks
python3 -m alhsi list

# Run autonomous loop on NanoGPT for 8 trials
python3 -m alhsi run --preset nanogpt --trials 8 --delay 0.5

# Run kernel throughput benchmark
python3 -m alhsi run --preset matmul --trials 6

# Test the Adversarial Cheater agent against the Harness
python3 -m alhsi run --preset nanogpt --agent cheat --trials 3
```

---

## 🧪 Running Automated Tests

Run the complete test suite:

```bash
pytest -v
```

All 14 tests cover types, git manager commit/revert mechanics, harness anti-tampering verification, subprocess execution, the autonomous loop orchestrator, and FastAPI API routes.

---

## 📂 Project Architecture

```
agentic-ai-alhsi/
├── alhsi/
│   ├── core/
│   │   ├── loop.py           # The Agent Loop state machine and continuous runner
│   │   ├── harness.py        # Sandbox execution, integrity checks, anti-tamper verifier
│   │   ├── git_manager.py    # Git tracking, automatic commit & rollback engine
│   │   └── types.py          # Data models: Trial, Hypothesis, BenchmarkResult, LoopPhase
│   ├── agents/
│   │   ├── base.py           # Base agent interface
│   │   ├── auto_sim.py       # Realistic Autoresearch simulator (no API key needed)
│   │   ├── llm_agent.py      # Live LLM provider (Gemini, OpenAI, Ollama)
│   │   └── cheat_agent.py    # Adversarial agent proving Harness security
│   ├── benchmarks/
│   │   ├── nanogpt/          # NanoGPT / train.py benchmark
│   │   ├── matmul/           # Matrix multiplication / attention kernel GFLOPS benchmark
│   │   └── reasoning/        # Prompt & chain-of-thought puzzle solver benchmark
│   ├── server/
│   │   ├── app.py            # FastAPI REST & WebSocket streaming server
│   │   └── static/           # Single-Page Web Dashboard (Tailwind, Lucide, Chart.js)
│   └── cli.py                # Terminal CLI with rich tables and progress logs
├── tests/                    # Pytest test suite (14 tests)
├── pyproject.toml
├── run.sh
└── README.md
```

---

## 📺 References

- **Autonomous AI Agents & Self-Improving Systems**: The emerging paradigm of Software 3.0 engineering.
- **Autoresearch**: Experimental framework for recursive self-improvement and automated code optimization.
