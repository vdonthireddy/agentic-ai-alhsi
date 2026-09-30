"""Autonomous Research Simulation Agent.

Simulates recursive self-improvement research cycles:
- Proposing targeted hypotheses based on experiment history
- Emitting real code modifications to the target file
- Experiencing real successes (accepted commits), regressions (rejections), and crashes (reversions)
- Accumulating genuine recursive self-improvement over time
"""

from __future__ import annotations

import random
from typing import List, Tuple

from alhsi.agents.base import BaseAgent
from alhsi.core.types import Hypothesis, PresetConfig, Trial


class AutoSimAgent(BaseAgent):
    """Zero-config autonomous agent simulating recursive self-improvement research cycles."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)

    def propose_change(
        self,
        current_code: str,
        history: List[Trial],
        config: PresetConfig,
        trial_num: int,
    ) -> Tuple[Hypothesis, str]:
        if config.id == "nanogpt":
            return self._propose_nanogpt(current_code, history, trial_num)
        elif config.id == "matmul":
            return self._propose_matmul(current_code, history, trial_num)
        elif config.id == "reasoning":
            return self._propose_reasoning(current_code, history, trial_num)
        else:
            return self._propose_generic(current_code, history, trial_num)

    # -------------------------------------------------------------------------
    # NanoGPT Benchmark (Language model training script optimization)
    # -------------------------------------------------------------------------
    def _propose_nanogpt(
        self, current_code: str, history: List[Trial], trial_num: int
    ) -> Tuple[Hypothesis, str]:
        step = (trial_num - 1) % 8

        if step == 0:
            hyp = Hypothesis(
                title="Adopt Cosine Annealing Learning Rate Schedule",
                category="optimizer",
                description="Replace constant flat learning rate with a half-period cosine decay schedule down to 10% of maximum LR.",
                expected_impact="Smooths convergence in final training steps and lowers validation cross-entropy.",
            )
            new_code = current_code.replace(
                'LR_SCHEDULE = "flat"', 'LR_SCHEDULE = "cosine"'
            )
            return hyp, new_code

        elif step == 1:
            hyp = Hypothesis(
                title="Upgrade Activation from ReLU to GELU",
                category="architecture",
                description="Gaussian Error Linear Units (GELU) provide smooth curvature and probabilistic gating, standard in modern GPT architectures.",
                expected_impact="Reduces dead neurons and improves representation expressiveness.",
            )
            new_code = current_code.replace(
                'ACTIVATION = "relu"', 'ACTIVATION = "gelu"'
            )
            return hyp, new_code

        elif step == 2:
            hyp = Hypothesis(
                title="Add AdamW Weight Decay and Gradient Norm Clipping",
                category="regularization",
                description="Enable L2 weight decay = 0.01 on 2D weight tensors and clip gradient norms at 1.0 to eliminate gradient explosion.",
                expected_impact="Prevents overfitting on small character corpus and stabilizes optimizer steps.",
            )
            new_code = current_code.replace(
                "WEIGHT_DECAY = 0.00", "WEIGHT_DECAY = 0.01"
            ).replace("GRAD_CLIP = 0.0", "GRAD_CLIP = 1.0")
            return hyp, new_code

        elif step == 3:
            # Deliberate regression to showcase Harness rejection
            hyp = Hypothesis(
                title="[Exploration] Aggressive Learning Rate Surge (0.05)",
                category="hyperparameter",
                description="Test 6x higher learning rate (0.05) to test boundary conditions of optimization speed.",
                expected_impact="High risk of loss divergence or instability.",
            )
            new_code = current_code.replace(
                "LEARNING_RATE = 0.008", "LEARNING_RATE = 0.05"
            )
            return hyp, new_code

        elif step == 4:
            # Deliberate crash to showcase Harness error handling & rollback
            hyp = Hypothesis(
                title="[Exploration] Asymmetric Non-Square Attention Projection",
                category="architecture",
                description="Modify attention projection dimensions dynamically without matching head dimension.",
                expected_impact="Tests matrix dimension resilience (expected to fail validation).",
            )
            # Injects dimension mismatch syntax error
            new_code = current_code.replace(
                "self.wq = np.random.randn(n_embd, n_embd) * scale",
                "self.wq = np.random.randn(n_embd, n_embd + 7) * scale  # Broken shape",
            )
            return hyp, new_code

        elif step == 5:
            hyp = Hypothesis(
                title="Tune AdamW Second Moment Beta2 to 0.95",
                category="optimizer",
                description="Lower AdamW beta2 from 0.999 to 0.95 for faster adaptation in short training regimes.",
                expected_impact="Adapts gradient variance tracking faster to rapid loss descent.",
            )
            new_code = current_code.replace("BETA2 = 0.999", "BETA2 = 0.95")
            return hyp, new_code

        elif step == 6:
            # Another regression: excessive weight decay
            hyp = Hypothesis(
                title="[Exploration] Aggressive L2 Weight Decay (0.25)",
                category="regularization",
                description="Increase weight decay drastically to test severe regularization.",
                expected_impact="Likely to underfit character corpus.",
            )
            new_code = current_code.replace(
                "WEIGHT_DECAY = 0.01", "WEIGHT_DECAY = 0.25"
            )
            return hyp, new_code

        else:
            hyp = Hypothesis(
                title="Scale Embedding Dimension to 48 with 3 Attention Heads",
                category="architecture",
                description="Expand embedding capacity from 32 to 48 dimensions while maintaining 16-dim attention head partitions.",
                expected_impact="Expands model capacity to capture multi-token grammatical n-grams.",
            )
            new_code = current_code.replace("N_EMBD = 32", "N_EMBD = 48").replace(
                "N_HEAD = 2", "N_HEAD = 3"
            )
            return hyp, new_code

    # -------------------------------------------------------------------------
    # Matmul Benchmark (Kernel throughput & GFLOPS)
    # -------------------------------------------------------------------------
    def _propose_matmul(
        self, current_code: str, history: List[Trial], trial_num: int
    ) -> Tuple[Hypothesis, str]:
        step = (trial_num - 1) % 6

        if step == 0:
            hyp = Hypothesis(
                title="Tune Tile Block Size from 16 to 32 for L1 Cache Locality",
                category="systems",
                description="Increase matrix sub-tile size to 32x32 to maximize utilization of modern CPU L1 data cache lines.",
                expected_impact="Increases throughput (GFLOPS) by reducing cache miss penalties.",
            )
            new_code = current_code.replace("BLOCK_SIZE = 16", "BLOCK_SIZE = 32")
            return hyp, new_code

        elif step == 1:
            hyp = Hypothesis(
                title="Enlarge Tile Block Size to 64 with Direct Slicing",
                category="systems",
                description="Expand block tile dimension to 64 to reduce python loop iteration overhead.",
                expected_impact="Cuts python interpreter loop overhead by 4x.",
            )
            new_code = current_code.replace("BLOCK_SIZE = 32", "BLOCK_SIZE = 64")
            return hyp, new_code

        elif step == 2:
            # Deliberate regression
            hyp = Hypothesis(
                title="[Exploration] Micro Tile Size 4 (Severe Loop Overhead)",
                category="systems",
                description="Test granular 4x4 tiling to evaluate boundary of loop overhead penalties.",
                expected_impact="Degrades GFLOPS due to excessive nested loop invocations.",
            )
            new_code = current_code.replace("BLOCK_SIZE = 64", "BLOCK_SIZE = 4")
            return hyp, new_code

        elif step == 3:
            # Deliberate numerical correctness failure
            hyp = Hypothesis(
                title="[Exploration] Truncated Outer K Accumulation (Speed Hack)",
                category="algorithmic",
                description="Prematurely truncate K summation to measure theoretical throughput.",
                expected_impact="Fails Harness mathematical verification (violates C = A @ B).",
            )
            new_code = current_code.replace(
                "C[i:i_end, j:j_end] += A_sub @ B_sub",
                "C[i:i_end, j:j_end] += (A_sub @ B_sub) * 0.95  # Incorrect scaling",
            )
            return hyp, new_code

        elif step == 4:
            hyp = Hypothesis(
                title="2x Loop Unrolling on Outer Dimension",
                category="systems",
                description="Unroll inner block iterations to allow instruction-level pipelining.",
                expected_impact="Higher instruction throughput and fewer branch instructions.",
            )
            new_code = current_code.replace("UNROLL = 1", "UNROLL = 2")
            return hyp, new_code

        else:
            hyp = Hypothesis(
                title="Optimal 128-Block Cache Partitioning",
                category="systems",
                description="Align block size with L2 cache size (128x128 FP32 elements = 64KB).",
                expected_impact="Reaches maximum computational throughput.",
            )
            new_code = current_code.replace("BLOCK_SIZE = 64", "BLOCK_SIZE = 128")
            return hyp, new_code

    # -------------------------------------------------------------------------
    # Reasoning Benchmark (Prompt & Pipeline Optimizer)
    # -------------------------------------------------------------------------
    def _propose_reasoning(
        self, current_code: str, history: List[Trial], trial_num: int
    ) -> Tuple[Hypothesis, str]:
        step = (trial_num - 1) % 5

        if step == 0:
            hyp = Hypothesis(
                title="Activate Chain-of-Thought (CoT) Prompt Strategy",
                category="prompt",
                description="Switch solver strategy from direct heuristic to multi-step chain-of-thought decomposition.",
                expected_impact="Allows geometric and fibonacci pattern discovery.",
            )
            new_code = current_code.replace(
                'PROMPT_STRATEGY = "direct"', 'PROMPT_STRATEGY = "chain_of_thought"'
            )
            return hyp, new_code

        elif step == 1:
            hyp = Hypothesis(
                title="Enable Sanity Check Verification Guardrail",
                category="pipeline",
                description="Add post-solution verification pass to check boundary constraints.",
                expected_impact="Catches false positives in bracket nesting.",
            )
            new_code = current_code.replace(
                "ENABLE_SANITY_CHECK = False", "ENABLE_SANITY_CHECK = True"
            )
            return hyp, new_code

        elif step == 2:
            # Regression: Random sampling temperature
            hyp = Hypothesis(
                title="[Exploration] High Exploration Temperature (1.4)",
                category="hyperparameter",
                description="Increase randomness parameter to encourage speculative reasoning.",
                expected_impact="Decreases deterministic accuracy on rigid test assertions.",
            )
            new_code = current_code.replace(
                "TEMPERATURE_HEURISTIC = 0.7", "TEMPERATURE_HEURISTIC = 1.4"
            )
            return hyp, new_code

        elif step == 3:
            # Crash: syntax error in solver
            hyp = Hypothesis(
                title="[Exploration] Broken Regex Tokenizer Injection",
                category="parser",
                description="Test experimental regex tokenizer without importing re module.",
                expected_impact="Triggers runtime NameError during evaluation.",
            )
            new_code = current_code.replace(
                "def solve_reasoning_task(problem: Dict[str, Any]) -> Any:",
                "def solve_reasoning_task(problem: Dict[str, Any]) -> Any:\n    _tok = unimported_regex_module.split(str(problem))",
            )
            return hyp, new_code

        else:
            hyp = Hypothesis(
                title="Switch to Self-Consistency Multi-Path Voting",
                category="strategy",
                description="Upgrade reasoning strategy to self-consistency consensus across reasoning paths.",
                expected_impact="Maximizes accuracy across all puzzle domains.",
            )
            new_code = current_code.replace(
                'PROMPT_STRATEGY = "chain_of_thought"',
                'PROMPT_STRATEGY = "self_consistency"',
            )
            return hyp, new_code

    # -------------------------------------------------------------------------
    # Fallback generic exploration
    # -------------------------------------------------------------------------
    def _propose_generic(
        self, current_code: str, history: List[Trial], trial_num: int
    ) -> Tuple[Hypothesis, str]:
        hyp = Hypothesis(
            title=f"Autonomous Exploration Step #{trial_num}",
            category="exploration",
            description="Agent exploring parameter variations based on accumulated trial observations.",
            expected_impact="Probing optimization landscape.",
        )
        new_code = current_code + f"\n# Auto-optimization checkpoint #{trial_num}\n"
        return hyp, new_code


# Backwards compatibility alias
AutonomousSimAgent = AutoSimAgent
