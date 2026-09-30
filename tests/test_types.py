"""Unit tests for types and data models."""

from alhsi.core.types import Hypothesis, BenchmarkResult, Trial, TrialStatus, LoopPhase


def test_hypothesis_to_dict():
    h = Hypothesis(
        title="Test Hyp",
        description="Testing",
        category="optimizer",
        expected_impact="High",
    )
    d = h.to_dict()
    assert d["title"] == "Test Hyp"
    assert d["category"] == "optimizer"


def test_benchmark_result():
    br = BenchmarkResult(
        metric_name="val_loss",
        metric_value=2.45,
        lower_is_better=True,
        secondary_metrics={"speed": 100.0},
    )
    assert br.success is True
    assert br.metric_value == 2.45
    assert br.tamper_detected is False


def test_trial_serialization():
    h = Hypothesis(title="T", description="D", category="C", expected_impact="I")
    trial = Trial(
        trial_num=1,
        hypothesis=h,
        target_file="train.py",
        diff="--- a\n+++ b",
        code_before="x = 1",
        code_after="x = 2",
        baseline_metric=3.0,
        trial_metric=2.5,
        metric_delta=-0.5,
        status=TrialStatus.ACCEPTED,
        commit_hash="abc1234",
    )
    d = trial.to_dict()
    assert d["status"] == "accepted"
    assert d["commit_hash"] == "abc1234"
    assert d["metric_delta"] == -0.5
