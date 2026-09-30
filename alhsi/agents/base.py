"""Base Agent Interface for ALHSI."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Tuple

from alhsi.core.types import Hypothesis, PresetConfig, Trial


class BaseAgent(ABC):
    """Abstract agent that analyzes prior trials and proposes code modifications."""

    @abstractmethod
    def propose_change(
        self,
        current_code: str,
        history: List[Trial],
        config: PresetConfig,
        trial_num: int,
    ) -> Tuple[Hypothesis, str]:
        """Inspects current code and trial history to propose a hypothesis and new code.
        
        Returns:
            Tuple of (Hypothesis, modified_code_str)
        """
        pass
