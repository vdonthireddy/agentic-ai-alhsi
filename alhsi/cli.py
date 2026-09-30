"""Command Line Interface for ALHSI."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich import print as rprint
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from alhsi.agents.cheat_agent import CheatAgent
from alhsi.agents.auto_sim import AutoSimAgent
from alhsi.agents.llm_agent import LLMAgent
from alhsi.benchmarks import list_benchmarks
from alhsi.core.loop import AgentLoop
from alhsi.core.types import TrialStatus


def run_command(args: argparse.Namespace):
    console = Console() if HAS_RICH else None

    if HAS_RICH:
        console.print(
            Panel.fit(
                "[bold cyan]ALHSI - Autonomous Self-Improvement Engine[/bold cyan]\n"
                "[dim]Software 3.0 Agent-Loop-Harness Architecture[/dim]",
                border_style="blue",
            )
        )
    else:
        print("=== ALHSI: Autonomous Self-Improvement Engine ===")

    # Select agent
    if args.agent == "cheat":
        agent = CheatAgent()
    elif args.agent in ("gemini", "openai", "ollama"):
        agent = LLMAgent(provider=args.agent)
    else:
        agent = AutoSimAgent()

    loop = AgentLoop(preset_id=args.preset, agent=agent)

    print(f"Target Benchmark: {loop.config.name}")
    print(f"Target File: {loop.config.target_file}")
    print(f"Initial Baseline Metric: {loop.baseline_metric:.4f} {loop.config.unit}")
    print(f"Running {args.trials} autonomous trials...\n")

    for i in range(args.trials):
        trial = loop.step()

        status_style = "green" if trial.status == TrialStatus.ACCEPTED else (
            "red" if trial.status == TrialStatus.REJECTED else "yellow"
        )
        delta_str = f"{trial.metric_delta:+.4f}" if trial.metric_delta is not None else "N/A"

        if HAS_RICH:
            console.print(
                f"[bold]Trial #{trial.trial_num}[/bold]: {trial.hypothesis.title} "
                f"[{status_style}][{trial.status.value.upper()}][/{status_style}] "
                f"(Metric: {trial.trial_metric} | Delta: {delta_str})"
            )
            if trial.commit_hash:
                console.print(f"  [dim]Git Commit: {trial.commit_hash}[/dim]")
        else:
            print(
                f"Trial #{trial.trial_num}: {trial.hypothesis.title} "
                f"[{trial.status.value.upper()}] (Metric: {trial.trial_metric} | Delta: {delta_str})"
            )

        if args.delay > 0 and i < args.trials - 1:
            time.sleep(args.delay)

    print("\n" + "=" * 60)
    state = loop.get_state()
    print("Execution Summary:")
    print(f"  Total Trials: {state['total_trials']}")
    print(f"  Accepted Improvements: {state['accepted_count']}")
    print(f"  Rejected Regressions: {state['rejected_count']}")
    print(f"  Final Golden Metric: {state['baseline_metric']:.4f} {loop.config.unit}")
    print(f"  Total Git Commits: {len(state['recent_commits'])}")
    print("=" * 60)


def serve_command(args: argparse.Namespace):
    import uvicorn
    print(f"Starting ALHSI Interactive Web Dashboard on http://{args.host}:{args.port}")
    uvicorn.run("alhsi.server.app:app", host=args.host, port=args.port, reload=args.reload)


def list_command(args: argparse.Namespace):
    benchmarks = list_benchmarks()
    if HAS_RICH:
        table = Table(title="Available Benchmarks")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Target File", style="green")
        table.add_column("Metric", style="magenta")
        table.add_column("Direction", style="yellow")
        for b in benchmarks:
            table.add_row(
                b.id,
                b.name,
                b.target_file,
                b.metric_name,
                "Lower is better" if b.lower_is_better else "Higher is better",
            )
        Console().print(table)
    else:
        for b in benchmarks:
            print(f"- {b.id}: {b.name} (Target: {b.target_file}, Metric: {b.metric_name})")


def main():
    parser = argparse.ArgumentParser(
        prog="alhsi",
        description="Agent-Loop-Harness Self-Improvement Engine (Software 3.0)",
    )
    subparsers = parser.add_subparsers(dest="command")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Launch interactive Web Dashboard")
    serve_parser.add_argument("--host", default="127.0.0.1", help="Host binding")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port binding")
    serve_parser.add_argument("--reload", action="store_true", help="Enable reload")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run autonomous loop in CLI")
    run_parser.add_argument("--preset", default="nanogpt", choices=["nanogpt", "matmul", "reasoning"])
    run_parser.add_argument("--agent", default="sim", choices=["sim", "gemini", "openai", "ollama", "cheat"])
    run_parser.add_argument("--trials", type=int, default=8, help="Number of trials to execute")
    run_parser.add_argument("--delay", type=float, default=0.5, help="Delay between trials in seconds")

    # List command
    subparsers.add_parser("list", help="List available benchmarks")

    args = parser.parse_args()

    if args.command == "serve":
        serve_command(args)
    elif args.command == "run":
        run_command(args)
    elif args.command == "list":
        list_command(args)
    else:
        # Default action: launch serve
        serve_parser.print_help()


if __name__ == "__main__":
    main()
