"""Unit tests for the autonomous Agent Loop and adversarial agent defense."""

from pathlib import Path
from alhsi.agents.cheat_agent import CheatAgent
from alhsi.agents.auto_sim import AutoSimAgent
from alhsi.core.loop import AgentLoop
from alhsi.core.types import TrialStatus


def test_loop_execution_nanogpt(tmp_path: Path):
    loop = AgentLoop(
        preset_id="nanogpt",
        agent=AutoSimAgent(),
        workspace_base=tmp_path,
    )
    assert loop.baseline_metric > 0.0

    trial = loop.step()
    assert trial.trial_num == 1
    assert trial.status in (TrialStatus.ACCEPTED, TrialStatus.REJECTED)
    assert trial.diff != ""

    state = loop.get_state()
    assert state["total_trials"] == 1
    assert len(state["recent_commits"]) >= 1


def test_loop_catches_cheater_agent(tmp_path: Path):
    loop = AgentLoop(
        preset_id="nanogpt",
        agent=CheatAgent(),
        workspace_base=tmp_path,
    )
    trial = loop.step()
    assert trial.status == TrialStatus.TAMPER_DETECTED
    assert trial.commit_hash is None
    assert "Security Violation" in str(trial.rejection_reason)
