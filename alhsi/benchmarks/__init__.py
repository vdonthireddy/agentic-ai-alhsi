"""Benchmark registry for ALHSI."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Dict, List, Type

from alhsi.benchmarks.base import BaseBenchmark
from alhsi.core.types import PresetConfig


class NanoGPTBenchmark(BaseBenchmark):
    def get_config(self) -> PresetConfig:
        return PresetConfig(
            id="nanogpt",
            name="NanoGPT Trainer (Autoresearch)",
            description="Optimize micro-Transformer training script (val_loss, tokens/s, attention scaling, AdamW schedules).",
            research_context="Autonomous agent optimization benchmark: iterating on train.py to discover hyperparameter and architecture optimizations.",
            target_file="train.py",
            metric_name="val_loss",
            unit="loss",
            lower_is_better=True,
            baseline_metric=3.65,
            category="Machine Learning / Training",
        )

    def setup_workspace(self, workspace_path: Path) -> None:
        src_dir = Path(__file__).parent / "nanogpt"
        shutil.copy2(src_dir / "train.py", workspace_path / "train.py")
        shutil.copy2(src_dir / "eval_harness.py", workspace_path / "eval_harness.py")

    def get_eval_script(self) -> str:
        return "eval_harness.py"


class MatmulBenchmark(BaseBenchmark):
    def get_config(self) -> PresetConfig:
        return PresetConfig(
            id="matmul",
            name="Computational Kernel (GFLOPS & Latency)",
            description="Optimize block matrix multiplication and attention kernels for maximum hardware throughput with strict correctness verifier.",
            research_context="Systems optimization loop: exploring memory cache locality, tiling, and vectorization within locked mathematical constraints.",
            target_file="kernel.py",
            metric_name="gflops",
            unit="GFLOPS",
            lower_is_better=False,
            baseline_metric=2.67,
            category="Systems / Performance",
        )

    def setup_workspace(self, workspace_path: Path) -> None:
        src_dir = Path(__file__).parent / "matmul"
        shutil.copy2(src_dir / "kernel.py", workspace_path / "kernel.py")
        shutil.copy2(src_dir / "eval_harness.py", workspace_path / "eval_harness.py")

    def get_eval_script(self) -> str:
        return "eval_harness.py"


class ReasoningBenchmark(BaseBenchmark):
    def get_config(self) -> PresetConfig:
        return PresetConfig(
            id="reasoning",
            name="Reasoning Pipeline (Prompt & Chain-of-Thought)",
            description="Self-improve reasoning strategy and chain-of-thought heuristics against a locked suite of multi-step puzzles.",
            research_context="Cognitive loop self-improvement: evolving reasoning prompts and algorithmic verification to raise accuracy without human tuning.",
            target_file="prompt_solver.py",
            metric_name="accuracy",
            unit="%",
            lower_is_better=False,
            baseline_metric=41.67,
            category="Reasoning / Agents",
        )

    def setup_workspace(self, workspace_path: Path) -> None:
        src_dir = Path(__file__).parent / "reasoning"
        shutil.copy2(src_dir / "prompt_solver.py", workspace_path / "prompt_solver.py")
        shutil.copy2(src_dir / "eval_harness.py", workspace_path / "eval_harness.py")

    def get_eval_script(self) -> str:
        return "eval_harness.py"


class OutboundEmailBenchmark(BaseBenchmark):
    def get_config(self) -> PresetConfig:
        return PresetConfig(
            id="outbound_email",
            name="B2B Outbound Email Campaign Optimizer",
            description="Optimize cold outbound strategy (subject lines, brevity, ROI proof, CTA friction) across 500 synthetic enterprise executives.",
            research_context="Autonomous B2B marketing loop: discovering optimal email copy and sequence cadence that maximizes demo booking rate while enforcing strict anti-spam deliverability guards.",
            target_file="campaign_strategy.py",
            metric_name="booking_rate",
            unit="%",
            lower_is_better=False,
            baseline_metric=1.10,
            category="B2B Marketing / Sales",
        )

    def setup_workspace(self, workspace_path: Path) -> None:
        src_dir = Path(__file__).parent / "outbound_email"
        shutil.copy2(src_dir / "campaign_strategy.py", workspace_path / "campaign_strategy.py")
        shutil.copy2(src_dir / "eval_harness.py", workspace_path / "eval_harness.py")

    def get_eval_script(self) -> str:
        return "eval_harness.py"


BENCHMARK_REGISTRY: Dict[str, Type[BaseBenchmark]] = {
    "nanogpt": NanoGPTBenchmark,
    "matmul": MatmulBenchmark,
    "reasoning": ReasoningBenchmark,
    "outbound_email": OutboundEmailBenchmark,
}


def get_benchmark(benchmark_id: str) -> BaseBenchmark:
    if benchmark_id not in BENCHMARK_REGISTRY:
        raise ValueError(
            f"Unknown benchmark '{benchmark_id}'. Available: {list(BENCHMARK_REGISTRY.keys())}"
        )
    return BENCHMARK_REGISTRY[benchmark_id]()


def list_benchmarks() -> List[PresetConfig]:
    return [cls().get_config() for cls in BENCHMARK_REGISTRY.values()]
