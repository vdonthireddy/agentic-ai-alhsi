"""Autonomous Recursive Self-Improvement Loop Orchestrator.

Implements the continuous cycle of recursive self-improvement:
  Hypothesize -> Modify -> Evaluate in Harness -> Compare -> Commit/Revert -> Repeat.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from alhsi.agents.base import BaseAgent
from alhsi.agents.auto_sim import AutoSimAgent
from alhsi.benchmarks import BaseBenchmark, get_benchmark
from alhsi.core.git_manager import GitExperimentManager
from alhsi.core.harness import Harness
from alhsi.core.types import (
    BenchmarkResult,
    Hypothesis,
    LoopPhase,
    PresetConfig,
    Trial,
    TrialStatus,
)

logger = logging.getLogger(__name__)


class AgentLoop:
    """The Autonomous Self-Improvement Loop engine."""

    def __init__(
        self,
        preset_id: str = "nanogpt",
        agent: Optional[BaseAgent] = None,
        workspace_base: Optional[Path] = None,
        on_state_change: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.preset_id = preset_id
        self.benchmark: BaseBenchmark = get_benchmark(preset_id)
        self.config: PresetConfig = self.benchmark.get_config()
        self.agent: BaseAgent = agent or AutoSimAgent()
        self.on_state_change = on_state_change

        # Setup sandbox directory
        if workspace_base:
            self.workspace_dir = Path(workspace_base).resolve() / f"sandbox_{preset_id}"
        else:
            self.workspace_dir = (
                Path.home() / ".alhsi" / f"sandbox_{preset_id}"
            ).resolve()

        self.workspace_dir.mkdir(parents=True, exist_ok=True)

        self.git_mgr = GitExperimentManager(self.workspace_dir)
        self.harness = Harness(
            workspace_dir=self.workspace_dir,
            allowed_target_file=self.config.target_file,
            metric_name=self.config.metric_name,
            lower_is_better=self.config.lower_is_better,
        )

        self.phase: LoopPhase = LoopPhase.IDLE
        self.trials: List[Trial] = []
        self.current_trial: Optional[Trial] = None
        self.baseline_metric: float = self.config.baseline_metric
        self.baseline_code: str = ""
        self.running: bool = False
        self.paused: bool = False
        self._loop_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Initialize environment and baseline
        self.reset()

    def reset(self, new_preset_id: Optional[str] = None) -> None:
        """Reset workspace and evaluate clean baseline."""
        with self._lock:
            self.running = False
            self.paused = False
            if new_preset_id and new_preset_id != self.preset_id:
                self.preset_id = new_preset_id
                self.benchmark = get_benchmark(new_preset_id)
                self.config = self.benchmark.get_config()

            # Clean workspace files (except .git)
            for item in self.workspace_dir.iterdir():
                if item.name == ".git":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()

            # Copy fresh benchmark files
            self.benchmark.setup_workspace(self.workspace_dir)
            self.harness = Harness(
                workspace_dir=self.workspace_dir,
                allowed_target_file=self.config.target_file,
                metric_name=self.config.metric_name,
                lower_is_better=self.config.lower_is_better,
            )

            # Read initial baseline code
            target_path = self.workspace_dir / self.config.target_file
            self.baseline_code = target_path.read_text(encoding="utf-8")

            # Run baseline evaluation
            eval_script = self.benchmark.get_eval_script()
            res = self.harness.execute_eval(eval_script)
            if res.success:
                self.baseline_metric = res.metric_value
            else:
                logger.warning(f"Baseline eval warning: {res.error_message}")
                self.baseline_metric = self.config.baseline_metric

            # Initial git commit
            self.git_mgr._run_git("add", ".")
            self.git_mgr._run_git(
                "commit",
                "-m",
                f"Initial Baseline for {self.config.name} [{self.config.metric_name}: {self.baseline_metric:.4f}]",
            )

            self.trials.clear()
            self.current_trial = None
            self.phase = LoopPhase.IDLE

        self._notify_state()

    def step(self) -> Trial:
        """Execute exactly one step of the autonomous loop."""
        with self._lock:
            trial_num = len(self.trials) + 1
            start_time = time.time()
            target_path = self.workspace_dir / self.config.target_file
            code_before = target_path.read_text(encoding="utf-8")

            # --- Phase 1: Hypothesize ---
            self.phase = LoopPhase.HYPOTHESIZING
            self._notify_state()

            hypothesis, candidate_code = self.agent.propose_change(
                current_code=code_before,
                history=self.trials,
                config=self.config,
                trial_num=trial_num,
            )

            # --- Phase 2: Modifying Target Code & Diff ---
            self.phase = LoopPhase.MODIFYING
            self._notify_state()

            target_path.write_text(candidate_code, encoding="utf-8")
            diff = self.git_mgr.compute_text_diff(
                code_before, candidate_code, filename=self.config.target_file
            )

            # --- Phase 3: Evaluating in Sandbox Harness ---
            self.phase = LoopPhase.EVALUATING
            self._notify_state()

            eval_res: BenchmarkResult = self.harness.execute_eval(
                self.benchmark.get_eval_script()
            )

            # --- Phase 4: Decision & Commit/Revert ---
            self.phase = LoopPhase.DECIDING
            self._notify_state()

            trial_status = TrialStatus.PENDING
            commit_hash = None
            rejection_reason = None
            trial_metric = eval_res.metric_value
            metric_delta = (
                trial_metric - self.baseline_metric
                if eval_res.success
                else None
            )

            if eval_res.tamper_detected:
                trial_status = TrialStatus.TAMPER_DETECTED
                rejection_reason = f"Security Violation: {eval_res.tamper_reason}"
                self.phase = LoopPhase.REVERTING
                self._notify_state()
                self.git_mgr.revert_changes(self.config.target_file)

            elif not eval_res.success:
                trial_status = TrialStatus.CRASHED
                rejection_reason = (
                    f"Execution Crash: {eval_res.error_message or 'Unknown error'}"
                )
                self.phase = LoopPhase.REVERTING
                self._notify_state()
                self.git_mgr.revert_changes(self.config.target_file)

            else:
                is_improved, delta = self.harness.is_improvement(
                    self.baseline_metric, trial_metric
                )
                if is_improved:
                    trial_status = TrialStatus.ACCEPTED
                    self.phase = LoopPhase.COMMITTING
                    self._notify_state()
                    commit_hash = self.git_mgr.commit_improvement(
                        trial_num=trial_num,
                        title=hypothesis.title,
                        metric_name=self.config.metric_name,
                        old_val=self.baseline_metric,
                        new_val=trial_metric,
                        target_file=self.config.target_file,
                    )
                    # Update golden state baseline
                    self.baseline_metric = trial_metric
                    self.baseline_code = candidate_code
                else:
                    trial_status = TrialStatus.REJECTED
                    rejection_reason = (
                        f"Metric regressed or stagnant (Candidate: {trial_metric:.4f} vs Baseline: {self.baseline_metric:.4f})"
                    )
                    self.phase = LoopPhase.REVERTING
                    self._notify_state()
                    self.git_mgr.revert_changes(self.config.target_file)

            elapsed = time.time() - start_time
            trial = Trial(
                trial_num=trial_num,
                hypothesis=hypothesis,
                target_file=self.config.target_file,
                diff=diff,
                code_before=code_before,
                code_after=candidate_code,
                baseline_metric=self.baseline_metric if trial_status != TrialStatus.ACCEPTED else (self.baseline_metric - (metric_delta or 0)),
                trial_metric=trial_metric if eval_res.success else None,
                metric_delta=metric_delta,
                status=trial_status,
                commit_hash=commit_hash,
                rejection_reason=rejection_reason,
                secondary_metrics=eval_res.secondary_metrics,
                logs=eval_res.stdout + ("\n" + eval_res.stderr if eval_res.stderr else ""),
                elapsed_sec=round(elapsed, 3),
            )

            self.trials.append(trial)
            self.current_trial = trial
            self.phase = LoopPhase.IDLE

        self._notify_state()
        return trial

    def start_continuous(self, max_trials: int = 15, delay_sec: float = 1.0) -> None:
        """Start autonomous continuous loop execution in background."""
        if self.running:
            return

        self.running = True
        self.paused = False
        self._notify_state()
        target_total = len(self.trials) + max_trials if max_trials > 0 else 999999

        def _worker():
            logger.info(f"Starting autonomous loop worker (current: {len(self.trials)}, target: {target_total})...")
            while self.running and len(self.trials) < target_total:
                while self.paused and self.running:
                    time.sleep(0.2)

                if not self.running:
                    break

                try:
                    self.step()
                except Exception as e:
                    logger.error(f"Error in loop step: {e}", exc_info=True)
                    break

                if delay_sec > 0:
                    time.sleep(delay_sec)

            self.running = False
            self.phase = LoopPhase.IDLE
            self._notify_state()

        self._loop_thread = threading.Thread(target=_worker, daemon=True)
        self._loop_thread.start()

    def pause(self) -> None:
        self.paused = True
        self.phase = LoopPhase.PAUSED
        self._notify_state()

    def resume(self) -> None:
        self.paused = False
        self.phase = LoopPhase.IDLE
        self._notify_state()

    def stop(self) -> None:
        self.running = False
        self.paused = False
        self.phase = LoopPhase.IDLE
        self._notify_state()

    def get_state(self) -> Dict[str, Any]:
        """Snapshot of current loop state."""
        target_path = self.workspace_dir / self.config.target_file
        current_code = target_path.read_text(encoding="utf-8") if target_path.exists() else ""
        accepted_count = sum(1 for t in self.trials if t.status == TrialStatus.ACCEPTED)
        rejected_count = sum(1 for t in self.trials if t.status == TrialStatus.REJECTED)
        crashed_count = sum(1 for t in self.trials if t.status == TrialStatus.CRASHED)
        tamper_count = sum(1 for t in self.trials if t.status == TrialStatus.TAMPER_DETECTED)

        return {
            "phase": self.phase.value,
            "running": self.running,
            "paused": self.paused,
            "preset": self.config.to_dict(),
            "baseline_metric": self.baseline_metric,
            "current_code": current_code,
            "total_trials": len(self.trials),
            "accepted_count": accepted_count,
            "rejected_count": rejected_count,
            "crashed_count": crashed_count,
            "tamper_count": tamper_count,
            "trials": [t.to_dict() for t in self.trials],
            "current_trial": self.current_trial.to_dict() if self.current_trial else None,
            "recent_commits": self.git_mgr.get_recent_commits(limit=10),
        }

    def _notify_state(self) -> None:
        if self.on_state_change:
            try:
                self.on_state_change(self.get_state())
            except Exception as e:
                logger.error(f"Error in state callback: {e}")
