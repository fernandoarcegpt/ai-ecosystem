from types import SimpleNamespace

from skilled.reasoning.abductive_engine import AbductiveEngineAdapter
from skilled.reasoning.engine_contracts import ReasoningCapability, ReasoningProfile
from skilled.reasoning.extended_engine_registry import build_extended_engine_registry
from skilled.reasoning.statistical_induction_engine import StatisticalInductionEngineAdapter


def _problem(capabilities, **specs):
    indicators = {
        "required_capabilities": [capability.value for capability in capabilities],
        **specs,
    }
    return SimpleNamespace(
        mode=SimpleNamespace(value="none"),
        relations=[],
        facts=[],
        rules=[],
        constraints=[],
        items=[],
        people=[],
        structural_indicators=indicators,
    )


def test_clingo_returns_all_minimal_abductive_explanations():
    problem = _problem(
        (ReasoningCapability.ABDUCTIVE,),
        abductive_spec={
            "observations": ["wet"],
            "assumables": ["rain", "pipe_break"],
            "rules": [
                "wet :- rain.",
                "wet :- pipe_break.",
            ],
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    adapter = AbductiveEngineAdapter()

    assert adapter.can_handle(problem, profile) is True
    result = adapter.execute(problem)

    assert result.status == "success"
    assert result.data["solution_status"] == "explained"
    assert result.data["minimum_hypothesis_count"] == 1
    assert result.data["minimal_explanations"] == [["pipe_break"], ["rain"]]
    assert result.validation["minimality_checked_by_exhaustive_models"] is True


def test_clingo_reports_no_explanation_instead_of_inventing_one():
    problem = _problem(
        (ReasoningCapability.ABDUCTIVE,),
        abductive_spec={
            "observations": ["wet"],
            "assumables": ["rain"],
            "constraints": [":- rain."],
        },
    )

    result = AbductiveEngineAdapter().execute(problem)

    assert result.status == "success"
    assert result.data["solution_status"] == "no_explanation"
    assert result.data["minimal_explanations"] == []
    assert result.validation["explanation_found"] is False


def test_statistical_induction_learns_auditable_classification_pattern():
    examples = [
        {"x": value, "label": "low" if value < 6 else "high"}
        for value in range(12)
    ]
    problem = _problem(
        (ReasoningCapability.STATISTICAL_INDUCTION,),
        statistical_induction_spec={
            "task": "classification",
            "features": ["x"],
            "target": "label",
            "examples": examples,
            "test_size": 0.25,
            "random_state": 7,
            "max_depth": 2,
            "predict": [{"x": 1}, {"x": 10}],
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    adapter = StatisticalInductionEngineAdapter()

    assert adapter.can_handle(problem, profile) is True
    result = adapter.execute(problem)

    assert result.status == "success"
    assert result.data["task"] == "classification"
    assert result.data["metrics"]["accuracy"] == 1.0
    assert "x" in result.data["rules"]
    assert result.data["predictions"][0]["prediction"] == "low"
    assert result.data["predictions"][1]["prediction"] == "high"
    assert result.validation["holdout_evaluated"] is True
    assert "not a logical proof" in result.warnings[0]
    assert result.deterministic is False


def test_statistical_induction_rejects_too_few_examples():
    problem = _problem(
        (ReasoningCapability.STATISTICAL_INDUCTION,),
        statistical_induction_spec={
            "features": ["x"],
            "target": "label",
            "examples": [
                {"x": 0, "label": "low"},
                {"x": 1, "label": "low"},
                {"x": 2, "label": "high"},
            ],
        },
    )

    result = StatisticalInductionEngineAdapter().execute(problem)

    assert result.status == "formalization_error"
    assert "At least 4 examples" in result.formalization_errors[0]


def test_registry_covers_abductive_and_statistical_inductive_capabilities():
    problem = _problem(
        (
            ReasoningCapability.ABDUCTIVE,
            ReasoningCapability.STATISTICAL_INDUCTION,
        ),
        abductive_spec={
            "observations": ["wet"],
            "assumables": ["rain"],
            "rules": ["wet :- rain."],
        },
        statistical_induction_spec={
            "features": ["x"],
            "target": "label",
            "examples": [
                {"x": 0, "label": "low"},
                {"x": 1, "label": "low"},
                {"x": 2, "label": "high"},
                {"x": 3, "label": "high"},
            ],
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    registry = build_extended_engine_registry()

    assert registry.build_plan(profile, problem) == (
        "clingo_abduction",
        "sklearn_tree_induction",
    )
