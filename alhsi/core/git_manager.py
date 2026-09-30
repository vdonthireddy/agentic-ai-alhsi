"""Git manager for tracking experiments, commits, and rollbacks in the autonomous self-improvement loop.

Every accepted change becomes a real commit. Every failed change is cleanly reverted.
"""

from __future__ import annotations

import difflib
import logging
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


class GitExperimentManager:
    """Manages git lifecycle for the autonomous self-improvement loop."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = Path(workspace_path).resolve()
        self._ensure_repo()

    def _run_git(self, *args: str) -> subprocess.CompletedProcess[str]:
        cmd = ["git"] + list(args)
        return subprocess.run(
            cmd,
            cwd=str(self.workspace_path),
            capture_output=True,
            text=True,
            check=False,
        )

    def _ensure_repo(self) -> None:
        """Initialize git repo if not present and configure local user."""
        git_dir = self.workspace_path / ".git"
        if not git_dir.exists():
            res = self._run_git("init")
            if res.returncode != 0:
                logger.error(f"Failed to init git: {res.stderr}")

        # Set local git user for clean commit logs
        self._run_git("config", "user.name", "Autonomous Loop Agent")
        self._run_git("config", "user.email", "agent@autoresearch.local")

    def get_head_commit(self) -> Optional[str]:
        res = self._run_git("rev-parse", "--short", "HEAD")
        if res.returncode == 0:
            return res.stdout.strip()
        return None

    def commit_improvement(
        self,
        trial_num: int,
        title: str,
        metric_name: str,
        old_val: float,
        new_val: float,
        target_file: str,
    ) -> Optional[str]:
        """Commit an accepted improvement to the repository."""
        self._run_git("add", target_file)
        delta = new_val - old_val
        delta_str = f"{delta:+.4f}"
        msg = (
            f"Trial #{trial_num}: {title}\n\n"
            f"{metric_name}: {old_val:.4f} -> {new_val:.4f} ({delta_str})\n"
            f"Autonomous improvement accepted by Harness."
        )
        res = self._run_git("commit", "-m", msg)
        if res.returncode == 0:
            commit_hash = self.get_head_commit()
            logger.info(f"Committed Trial #{trial_num} as {commit_hash}")
            return commit_hash
        else:
            logger.warning(f"Git commit failed: {res.stderr}")
            return self.get_head_commit()

    def revert_changes(self, target_file: str) -> None:
        """Discard modifications and restore target file to last accepted commit."""
        # Check out the target file from HEAD
        res = self._run_git("checkout", "HEAD", "--", target_file)
        if res.returncode != 0:
            # If no HEAD exists yet, remove file or clean
            self._run_git("checkout", "--", target_file)
        # Clean any untracked artifacts
        self._run_git("clean", "-fd")

    def get_diff(self, target_file: str) -> str:
        """Get git diff for the target file."""
        res = self._run_git("diff", "HEAD", "--", target_file)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout
        # Fallback to plain diff
        res2 = self._run_git("diff", "--", target_file)
        return res2.stdout if res2.returncode == 0 else ""

    @staticmethod
    def compute_text_diff(
        before: str, after: str, filename: str = "target.py"
    ) -> str:
        """Compute unified diff between two strings."""
        lines_before = before.splitlines(keepends=True)
        lines_after = after.splitlines(keepends=True)
        diff_lines = list(
            difflib.unified_diff(
                lines_before,
                lines_after,
                fromfile=f"a/{filename}",
                tofile=f"b/{filename}",
                lineterm="",
            )
        )
        return "\n".join(diff_lines)

    def get_recent_commits(self, limit: int = 15) -> List[dict]:
        """Fetch list of recent commits."""
        res = self._run_git(
            "log",
            f"-n{limit}",
            "--pretty=format:%h|%an|%ar|%s",
        )
        commits = []
        if res.returncode == 0 and res.stdout.strip():
            for line in res.stdout.strip().split("\n"):
                parts = line.split("|", 3)
                if len(parts) == 4:
                    commits.append(
                        {
                            "hash": parts[0],
                            "author": parts[1],
                            "relative_time": parts[2],
                            "message": parts[3],
                        }
                    )
        return commits
