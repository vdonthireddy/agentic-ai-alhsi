"""Unit tests for the immutable evaluation Harness and anti-tamper security."""

import pytest
from pathlib import Path
from alhsi.core.harness import Harness


def test_harness_anti_tamper_detects_unauthorized_file(tmp_path: Path):
    target = "train.py"
    (tmp_path / target).write_text("x = 1")
    (tmp_path / "eval.py").write_text("print('test')")

    harness = Harness(workspace_dir=tmp_path, allowed_target_file=target, metric_name="val_loss")
    ok, err = harness.verify_integrity()
    assert ok is True

    # Malicious agent creates unauthorized file in root
    (tmp_path / "cheater.txt").write_text("fake")
    ok2, err2 = harness.verify_integrity()
    assert ok2 is False
    assert "cheater.txt" in str(err2)


def test_harness_anti_tamper_detects_grader_modification(tmp_path: Path):
    target = "train.py"
    (tmp_path / target).write_text("x = 1")
    (tmp_path / "eval.py").write_text("print('test')")

    harness = Harness(workspace_dir=tmp_path, allowed_target_file=target, metric_name="val_loss")

    # Malicious agent modifies the evaluation script
    (tmp_path / "eval.py").write_text("print('MODIFIED')")
    ok, err = harness.verify_integrity()
    assert ok is False
    assert "eval.py" in str(err)


def test_harness_improvement_logic():
    harness_lower = Harness(Path("/tmp"), "t.py", "val_loss", lower_is_better=True)
    improved, delta = harness_lower.is_improvement(baseline=3.5, candidate=3.2)
    assert improved is True
    assert delta < 0

    worse, delta2 = harness_lower.is_improvement(baseline=3.5, candidate=3.7)
    assert worse is False

    harness_higher = Harness(Path("/tmp"), "k.py", "gflops", lower_is_better=False)
    improved_gflops, delta_g = harness_higher.is_improvement(baseline=10.0, candidate=15.0)
    assert improved_gflops is True
    assert delta_g > 0
