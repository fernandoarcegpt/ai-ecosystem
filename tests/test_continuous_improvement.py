"""Tests for improvement evidence and dataset gating."""

import pytest

from improvement.continuous_improvement import ContinuousImprovementAgent
from improvement.dataset_builder import EvaluationDatasetBuilder
from scripts.build_evaluation_dataset import build


def test_repeated_blocks_create_evidence_backed_improvement():
    agent = ContinuousImprovementAgent(repetition_threshold=2)
    reports = [
        {
            "status_distribution": {"failed": 0},
            "human_blocks": [
                {"category": "executor", "evidence": ["builder missing"]}
            ],
        },
        {
            "status_distribution": {"failed": 0},
            "human_blocks": [
                {"category": "executor", "evidence": ["qa missing"]}
            ],
        },
    ]
    proposals = agent.analyze_task_reports(reports)
    assert len(proposals) == 1
    assert proposals[0]["subject"] == "executor"
    assert proposals[0]["occurrences"] == 2
    assert proposals[0]["evidence"] == ["builder missing", "qa missing"]


def test_change_is_rejected_when_any_guard_metric_regresses():
    result = ContinuousImprovementAgent.evaluate_change(
        {"failure_rate": 0.2, "pass_rate": 0.8},
        {"failure_rate": 0.1, "pass_rate": 0.7},
        higher_is_better=["pass_rate"],
    )
    assert result["accepted"] is False
    assert result["regressions"] == ["pass_rate"]


def _example(example_id):
    return {
        "id": example_id,
        "task": "routing",
        "input": "Detecta un ciclo",
        "expected_output": {"engine": "networkx"},
        "expected_actions": ["neurosymbolic"],
        "success_criteria": ["detect cycle"],
        "provenance": {"source": "accepted-test"},
        "authorized": True,
    }


def test_dataset_requires_authorization_and_is_deterministically_split(tmp_path):
    builder = EvaluationDatasetBuilder()
    unauthorized = _example("unauthorized")
    unauthorized["authorized"] = False
    with pytest.raises(ValueError, match="not authorized"):
        builder.add(unauthorized)

    accepted = builder.add(_example("case-1"))
    assert accepted["split"] == builder._split("case-1")
    outputs = builder.write_jsonl(str(tmp_path))
    assert set(outputs) == {"train", "validation", "evaluation"}


def test_fine_tuning_is_rejected_without_enough_evaluation_examples():
    result = EvaluationDatasetBuilder.recommend_fine_tuning(
        [{"prompt_score": 0.8, "candidate_score": 0.9}],
        minimum_examples=100,
    )
    assert result["recommended"] is False
    assert result["reason"] == "insufficient_evaluation_examples"


def test_repository_dataset_has_train_validation_and_evaluation_splits(tmp_path):
    manifest = build(str(tmp_path))
    assert manifest["quality"]["total"] == 72
    assert manifest["quality"]["ready_for_comparative_evaluation"] is True
    assert manifest["contains_user_data"] is False
    assert manifest["fine_tuning_authorized"] is False
