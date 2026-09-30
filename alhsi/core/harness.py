"""The Harness: Execution Sandbox, Anti-Tamper Verifier, and Metric Evaluator.

In Software 3.0 autonomous systems, the Harness is the human engineer's primary artifact.
It provides:
1. Strict constraints (only allowed target file can be modified).
2. Fast, objective, low-noise measurement (< 2s - 60s).
3. Anti-reward-hacking guards (prevents fake metrics, test deletion, or metric overriding).
4. Subprocess sandboxing with timeout protection.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from alhsi.core.types import BenchmarkResult

logger = logging.getLogger(__name__)


class HarnessSecurityException(Exception):
    """Raised when an agent attempts to tamper with the evaluation harness."""
    pass


class Harness:
    """The Immutable Harness surrounding the agent loop."""

    def __init__(
        self,
        workspace_dir: Path,
        allowed_target_file: str,
        metric_name: str,
        lower_is_better: bool = True,
        min_improvement_delta: float = 0.0001,
        timeout_sec: float = 20.0,
    ):
        self.workspace_dir = Path(workspace_dir).resolve()
        self.allowed_target_file = allowed_target_file
        self.metric_name = metric_name
        self.lower_is_better = lower_is_better
        self.min_improvement_delta = min_improvement_delta
        self.timeout_sec = timeout_sec

        # Keep hash signatures of all non-target files to verify immutability
        self._immutable_file_hashes: Dict[str, str] = {}
        self._snapshot_immutable_files()

    def _snapshot_immutable_files(self) -> None:
        """Compute checksums of harness files to ensure the agent cannot alter them."""
        self._immutable_file_hashes.clear()
        for root, _, files in os.walk(self.workspace_dir):
            if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
                continue
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.workspace_dir)
                if rel_path != self.allowed_target_file:
                    file_path = os.path.join(root, f)
                    try:
                        with open(file_path, "rb") as fp:
                            self._immutable_file_hashes[rel_path] = hashlib.sha256(
                                fp.read()
                            ).hexdigest()
                    except Exception:
                        pass

    def verify_integrity(self) -> Tuple[bool, Optional[str]]:
        """Verify that the agent did not tamper with tests, benchmarks, or the harness."""
        # 1. Check if any immutable files were modified or deleted
        for rel_path, expected_hash in self._immutable_file_hashes.items():
            full_path = self.workspace_dir / rel_path
            if not full_path.exists():
                return False, f"Anti-Tamper Guard: Immutable file '{rel_path}' was deleted!"
            with open(full_path, "rb") as fp:
                current_hash = hashlib.sha256(fp.read()).hexdigest()
                if current_hash != expected_hash:
                    return False, f"Anti-Tamper Guard: Unauthorized modification detected in '{rel_path}'!"

        # 2. Check if unauthorized new files were created in root
        for root, _, files in os.walk(self.workspace_dir):
            if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
                continue
            for f in files:
                rel_path = os.path.relpath(os.path.join(root, f), self.workspace_dir)
                if (
                    rel_path != self.allowed_target_file
                    and rel_path not in self._immutable_file_hashes
                ):
                    return False, f"Anti-Tamper Guard: Unauthorized new file created: '{rel_path}'!"

        # 3. Check target file for explicit reward-hacking attempts
        target_path = self.workspace_dir / self.allowed_target_file
        if target_path.exists():
            code = target_path.read_text(encoding="utf-8")
            # Detect blatant cheating patterns
            forbidden_patterns = [
                ("__import__('os').system", "Dangerous OS execution attempt"),
                ("sys.modules['alhsi", "Attempted harness reflection hijacking"),
                ("os.environ['MOCK_METRIC']", "Attempted environment variable forgery"),
            ]
            for pat, reason in forbidden_patterns:
                if pat in code:
                    return False, f"Anti-Tamper Guard: {reason}"

        return True, None

    def execute_eval(
        self,
        eval_script_path: str,
        env_extra: Optional[Dict[str, str]] = None,
    ) -> BenchmarkResult:
        """Run the evaluation script in a protected subprocess."""
        start_time = time.time()

        # Step 1: Pre-execution integrity check
        integrity_ok, tamper_reason = self.verify_integrity()
        if not integrity_ok:
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                tamper_detected=True,
                tamper_reason=tamper_reason,
                error_message=tamper_reason,
                execution_time_sec=time.time() - start_time,
            )

        # Step 2: Prepare environment
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env["PYTHONPATH"] = str(self.workspace_dir) + os.pathsep + env.get("PYTHONPATH", "")
        if env_extra:
            env.update(env_extra)

        cmd = [sys.executable, eval_script_path]

        # Step 3: Run subprocess with timeout
        try:
            res = subprocess.run(
                cmd,
                cwd=str(self.workspace_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout_sec,
                env=env,
            )
        except subprocess.TimeoutExpired:
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                error_message=f"Harness Timeout: Execution exceeded {self.timeout_sec:.1f}s limit",
                execution_time_sec=self.timeout_sec,
            )
        except Exception as e:
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                error_message=f"Subprocess launch error: {str(e)}",
                execution_time_sec=time.time() - start_time,
            )

        elapsed = time.time() - start_time

        # Step 4: Post-execution integrity check
        integrity_ok_post, tamper_reason_post = self.verify_integrity()
        if not integrity_ok_post:
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                tamper_detected=True,
                tamper_reason=tamper_reason_post,
                error_message=tamper_reason_post,
                execution_time_sec=elapsed,
            )

        if res.returncode != 0:
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                error_message=f"Process exited with code {res.returncode}",
                stdout=res.stdout,
                stderr=res.stderr,
                execution_time_sec=elapsed,
            )

        # Step 5: Parse benchmark output (expected JSON line at the end with ALHSI_METRIC prefix)
        metric_val: Optional[float] = None
        secondary: Dict[str, float] = {}

        for line in reversed(res.stdout.splitlines()):
            line = line.strip()
            if line.startswith("__ALHSI_RESULT__"):
                payload_str = line.split("__ALHSI_RESULT__", 1)[1].strip()
                try:
                    data = json.loads(payload_str)
                    metric_val = float(data.get(self.metric_name, data.get("metric", 0.0)))
                    for k, v in data.items():
                        if k not in (self.metric_name, "metric"):
                            try:
                                secondary[k] = float(v)
                            except (ValueError, TypeError):
                                pass
                    break
                except Exception as ex:
                    logger.error(f"Failed to parse metric JSON: {ex}")

        if metric_val is None:
            # Fallback search for float in stdout
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=float("inf") if self.lower_is_better else float("-inf"),
                lower_is_better=self.lower_is_better,
                success=False,
                error_message="Harness could not locate '__ALHSI_RESULT__' JSON in stdout",
                stdout=res.stdout,
                stderr=res.stderr,
                execution_time_sec=elapsed,
            )

        # Step 6: Sanity checks on metric value
        if metric_val != metric_val:  # NaN check
            return BenchmarkResult(
                metric_name=self.metric_name,
                metric_value=metric_val,
                lower_is_better=self.lower_is_better,
                success=False,
                error_message="Metric evaluated to NaN (numerical divergence)",
                stdout=res.stdout,
                stderr=res.stderr,
                execution_time_sec=elapsed,
            )

        return BenchmarkResult(
            metric_name=self.metric_name,
            metric_value=metric_val,
            lower_is_better=self.lower_is_better,
            secondary_metrics=secondary,
            success=True,
            stdout=res.stdout,
            stderr=res.stderr,
            execution_time_sec=elapsed,
        )

    def is_improvement(self, baseline: float, candidate: float) -> Tuple[bool, float]:
        """Determine if candidate metric beats baseline beyond threshold."""
        delta = candidate - baseline
        if self.lower_is_better:
            improved = candidate < (baseline - self.min_improvement_delta)
        else:
            improved = candidate > (baseline + self.min_improvement_delta)
        return improved, delta
