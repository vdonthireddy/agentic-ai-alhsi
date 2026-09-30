"""Base class for all benchmarks in ALHSI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from alhsi.core.types import PresetConfig


class BaseBenchmark(ABC):
    """Abstract benchmark suite defining target file, baseline setup, and evaluator."""

    @abstractmethod
    def get_config(self) -> PresetConfig:
        """Return preset metadata configuration."""
        pass

    @abstractmethod
    def setup_workspace(self, workspace_path: Path) -> None:
        """Initialize benchmark files in the target workspace."""
        pass

    @abstractmethod
    def get_eval_script(self) -> str:
        """Return relative path to the immutable harness evaluation script."""
        pass
