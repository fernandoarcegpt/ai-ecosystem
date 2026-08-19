from types import SimpleNamespace

import pytest

from skilled.reasoning.causal_engine import CausalEngineAdapter
from skilled.reasoning.engine_contracts import ReasoningCapability, ReasoningProfile
from skilled.reasoning.extended_engine_registry import build_extended_engine_registry
from skilled.reasoning.probabilistic_engine import ProbabilisticEngineAdapter


def _problem(capabilities, **specs):
    indicators = {
        "required_capabilities": [
            capability.value if isinstance(capability, ReasoningCapability) else str(capability)
            for capability in capabilities
        ],
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


def _bayesian_problem():
    return _problem(
        [ReasoningCapability.PROBABILISTIC],
        probabilistic_spec={
            "edges": [["A", "B"]],
            "cpds": [
                {
                    "variable": "A",
                    "variable_card": 2,
                    "values": [[0.4], [0.6]],
                    "state_names": {"A": ["no", "yes"]},
                },
                {
                    "variable": "B",
                    "variable_card": 2,
                    "values": [[0.9, 0.2], [0.1, 0.8]],
                    "evidence": ["A"],
                    "evidence_card": [2],
                    "state_names": {
                        "A": ["no", "yes"],
                        "B": ["no", "yes"],
                    },
                },
            ],
            "queries": [
                {
                    "type": "posterior",
                    "variables": ["B"],
                    "evidence": {"A": "yes"},
                },
                {
                    "type": "map",
                    "variables": ["B"],
                    "evidence": {"A": "yes"},
                },
            ],
        },
    )


def test_pgmpy_returns_exact_posterior_and_map_state():
    problem = _bayesian_problem()
    profile = ReasoningProfile.from_problem(problem)
    adapter = ProbabilisticEngineAdapter()

    assert adapter.can_handle(problem, profile)
    result = adapter.execute(problem)

    assert result.status == "success"
    assert result.deterministic is False
    posterior, map_result = result.data["queries"]
    assert posterior["result"]["state_names"]["B"] == ["no", "yes"]
    assert posterior["result"]["values"] == pytest.approx([0.2, 0.8])
    assert map_result["result"] == {"B": "yes"}
    assert result.validation["model_checked"] is True


def _linear_causal_data():
    rows = []
    for confounder in range(5):
        for treatment in (0, 1):
            for repeat in range(6):
                outcome = 2.0 * treatment + 3.0 * confounder + repeat * 0.01
                rows.append(
                    {
                        "W": float(confounder),
                        "T": float(treatment),
                        "Y": float(outcome),
                    }
                )
    return rows


def test_dowhy_estimates_explicit_backdoor_effect():
    problem = _problem(
        [ReasoningCapability.CAUSAL],
        causal_spec={
            "data": _linear_causal_data(),
            "treatment": "T",
            "outcome": "Y",
            "common_causes": ["W"],
            "method_name": "backdoor.linear_regression",
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    adapter = CausalEngineAdapter()

    assert adapter.can_handle(problem, profile)
    result = adapter.execute(problem)

    assert result.status == "success"
    estimate = result.data["causal_effect"]["effect_estimate"]
    assert estimate == pytest.approx(2.0, abs=0.05)
    assert result.validation["counterfactual_computed"] is False


def test_dowhy_counterfactual_requires_explicit_graph_and_intervention():
    training = [
        {"X": float(x), "Y": float(2 * x + 1)}
        for x in range(20)
    ]
    problem = _problem(
        [ReasoningCapability.CAUSAL, ReasoningCapability.COUNTERFACTUAL],
        causal_spec={
            "data": training,
            "treatment": "X",
            "outcome": "Y",
            "graph_edges": [["X", "Y"]],
            "method_name": "backdoor.linear_regression",
            "counterfactual": {
                "observed_data": [{"X": 2.0, "Y": 5.0}],
                "interventions": {"X": 4.0},
            },
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    adapter = CausalEngineAdapter()

    assert adapter.can_handle(problem, profile)
    result = adapter.execute(problem)

    assert result.status == "success"
    counterfactual = result.data["counterfactual"]
    assert counterfactual["interventions"] == {"X": 4.0}
    assert len(counterfactual["counterfactual_samples"]) == 1
    assert counterfactual["counterfactual_samples"][0]["X"] == pytest.approx(4.0)
    assert "Y" in counterfactual["counterfactual_samples"][0]
    assert result.validation["causal_graph_explicit"] is True
    assert result.validation["counterfactual_computed"] is True
    assert result.warnings


def test_counterfactual_without_graph_fails_closed():
    problem = _problem(
        [ReasoningCapability.COUNTERFACTUAL],
        causal_spec={
            "data": [{"X": 0.0, "Y": 0.0}, {"X": 1.0, "Y": 1.0}],
            "counterfactual": {
                "observed_data": [{"X": 1.0, "Y": 1.0}],
                "interventions": {"X": 0.0},
            },
        },
    )
    adapter = CausalEngineAdapter()
    result = adapter.execute(problem)

    assert result.status == "formalization_error"
    assert any("graph_edges" in error for error in result.formalization_errors)


def test_registry_covers_probabilistic_causal_and_counterfactual_capabilities():
    registry = build_extended_engine_registry()
    profile = ReasoningProfile(
        capabilities=(
            ReasoningCapability.PROBABILISTIC,
            ReasoningCapability.CAUSAL,
            ReasoningCapability.COUNTERFACTUAL,
        ),
        legacy_mode="none",
    )

    assert registry.build_plan(profile) == ("dowhy", "pgmpy")
