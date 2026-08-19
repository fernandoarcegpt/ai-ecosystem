from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from skilled.reasoning.engine_contracts import (
    EngineRegistry,
    EngineResult,
    ReasoningCapability,
    ReasoningProfile,
)


def _problem(**overrides):
    base = {
        "mode": SimpleNamespace(value="none"),
        "relations": [],
        "facts": [],
        "rules": [],
        "constraints": [],
        "items": [],
        "people": [],
        "structural_indicators": {},
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_reasoning_profile_derives_multiple_current_capabilities():
    problem = _problem(
        mode=SimpleNamespace(value="combined"),
        relations=[["A", "B"]],
        facts=[("ready", "A")],
        rules=[{"name": "rule"}],
        constraints=[object()],
    )

    profile = ReasoningProfile.from_problem(problem)

    assert profile.to_dict()["capabilities"] == ["graph", "logic", "constraints"]
    assert profile.legacy_mode == "combined"


def test_reasoning_profile_accepts_future_declared_capabilities_without_schema_change():
    problem = _problem(
        structural_indicators={
            "required_capabilities": ["causal", "probabilistic", "unknown_future"],
            "human_review": True,
            "review_reason": "causal_direction_missing",
        }
    )

    profile = ReasoningProfile.from_problem(problem)

    assert profile.requires("causal")
    assert profile.requires("probabilistic")
    assert not profile.requires("unknown_future")
    assert profile.human_review is True
    assert profile.review_reason == "causal_direction_missing"


def test_engine_result_keeps_engine_specific_data_inside_common_envelope():
    result = EngineResult(
        engine="z3",
        capabilities=(ReasoningCapability.CONSTRAINTS,),
        status="success",
        data={"solution_status": "satisfiable"},
        validation={"valid": True},
    )

    payload = result.to_dict()

    assert result.successful is True
    assert payload["engine"] == "z3"
    assert payload["capabilities"] == ["constraints"]
    assert payload["data"]["solution_status"] == "satisfiable"
    assert payload["deterministic"] is True


@dataclass
class _Adapter:
    name: str
    capabilities: tuple
    priority: int = 0
    allowed: bool = True

    def can_handle(self, problem, profile):
        return self.allowed

    def execute(self, problem, context=None):
        return EngineResult(
            engine=self.name,
            capabilities=tuple(self.capabilities),
            status="success",
        )


def test_registry_selects_minimal_coverage_plan_deterministically():
    registry = EngineRegistry(
        [
            _Adapter("networkx", (ReasoningCapability.GRAPH,), priority=10),
            _Adapter("pydatalog", (ReasoningCapability.LOGIC,), priority=10),
            _Adapter("z3", (ReasoningCapability.CONSTRAINTS,), priority=10),
            _Adapter(
                "combined-capable",
                (ReasoningCapability.GRAPH, ReasoningCapability.LOGIC),
                priority=5,
            ),
        ]
    )
    profile = ReasoningProfile(
        capabilities=(
            ReasoningCapability.GRAPH,
            ReasoningCapability.LOGIC,
            ReasoningCapability.CONSTRAINTS,
        ),
        legacy_mode="combined",
    )

    assert registry.build_plan(profile) == ("combined-capable", "z3")


def test_registry_rejects_duplicate_names_and_missing_coverage():
    adapter = _Adapter("z3", (ReasoningCapability.CONSTRAINTS,))
    registry = EngineRegistry([adapter])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(adapter)

    with pytest.raises(LookupError, match="probabilistic"):
        registry.build_plan(
            ReasoningProfile(
                capabilities=(ReasoningCapability.PROBABILISTIC,),
                legacy_mode="none",
            )
        )
