"""Unit tests for GitExperimentManager."""

from pathlib import Path
from alhsi.core.git_manager import GitExperimentManager


def test_git_init_and_commit(tmp_path: Path):
    target = "train.py"
    target_path = tmp_path / target
    target_path.write_text("x = 10")

    git_mgr = GitExperimentManager(tmp_path)
    git_mgr._run_git("add", target)
    git_mgr._run_git("commit", "-m", "Initial commit")

    assert git_mgr.get_head_commit() is not None

    # Modify and commit improvement
    target_path.write_text("x = 20")
    commit_sha = git_mgr.commit_improvement(
        trial_num=1,
        title="Increase capacity",
        metric_name="val_loss",
        old_val=3.5,
        new_val=3.1,
        target_file=target,
    )
    assert commit_sha is not None
    commits = git_mgr.get_recent_commits()
    assert len(commits) == 2
    assert "Trial #1" in commits[0]["message"]


def test_git_revert(tmp_path: Path):
    target = "train.py"
    target_path = tmp_path / target
    target_path.write_text("original = True")

    git_mgr = GitExperimentManager(tmp_path)
    git_mgr._run_git("add", target)
    git_mgr._run_git("commit", "-m", "Baseline")

    # Modify with bad code
    target_path.write_text("bad = True")
    assert "bad = True" in target_path.read_text()

    # Revert
    git_mgr.revert_changes(target)
    assert "original = True" in target_path.read_text()
