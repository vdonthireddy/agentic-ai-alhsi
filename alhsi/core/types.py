"""Data types and schemas for ALHSI (Agent-Loop-Harness-Self-Improvement).

Inspired by the Software 3.0 recursive self-improvement loop architecture.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional
import time


class TrialStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    ACCEPTED = "accepted"       # Metric improved -> git committed
    REJECTED = "rejected"       # Metric regressed -> git reverted
    CRASHED = "crashed"         # Runtime error or syntax error -> reverted
    TAMPER_DETECTED = "tamper"  # Harness caught cheating attempt -> reverted


class LoopPhase(str, Enum):
    IDLE = "idle"
    HYPOTHESIZING = "hypothesizing"  # Agent reading history and forming idea
    MODIFYING = "modifying"          # Agent emitting code change/diff
    EVALUATING = "evaluating"        # Harness running code in sandbox
    DECIDING = "deciding"            # Comparing against baseline metric
    COMMITTING = "committing"        # Better: Git commit snapshot
    REVERTING = "reverting"          # Worse/Broken: Git reset to baseline
    PAUSED = "paused"
    COMPLETED = "completed"


@dataclass
class Hypothesis:
    title: str
    description: str
    category: str  # "optimizer", "architecture", "hyperparameter", "kernel", "algorithmic"
    expected_impact: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BenchmarkResult:
    metric_name: str
    metric_value: float
    lower_is_better: bool
    secondary_metrics: Dict[str, float] = field(default_factory=dict)
    success: bool = True
    error_message: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    tamper_detected: bool = False
    tamper_reason: Optional[str] = None
    execution_time_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Trial:
    trial_num: int
    hypothesis: Hypothesis
    target_file: str
    diff: str
    code_before: str
    code_after: str
    baseline_metric: float
    trial_metric: Optional[float] = None
    metric_delta: Optional[float] = None
    status: TrialStatus = TrialStatus.PENDING
    commit_hash: Optional[str] = None
    rejection_reason: Optional[str] = None
    secondary_metrics: Dict[str, float] = field(default_factory=dict)
    logs: str = ""
    elapsed_sec: float = 0.0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class PresetConfig:
    id: str
    name: str
    description: str
    research_context: str
    target_file: str
    metric_name: str
    unit: str
    lower_is_better: bool
    baseline_metric: float
    category: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
