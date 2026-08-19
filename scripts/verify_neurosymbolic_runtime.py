#!/usr/bin/env python3
"""Smoke test ejecutable de todos los motores extendidos en el Python actual.

No usa pytest. Su objetivo es detectar el problema clásico de entornos: que las
dependencias estén instaladas en un venv, pero Hermes se ejecute con otro.
Ejecuta una operación mínima real en cada motor y sale con código 1 si alguno
no está disponible o no produce un resultado válido.
"""

from __future__ import annotations

import json
import sys
from importlib import metadata
from types import SimpleNamespace

from skilled.reasoning.engine_contracts import ReasoningCapability, ReasoningProfile
from skilled.reasoning.extended_engine_registry import build_extended_engine_registry


DISTRIBUTIONS = (
    "unified-planning",
    "up-pyperplan",
    "z3-solver",
    "shapely",
    "pyproj",
    "pgmpy",
    "dowhy",
    "clingo",
    "scikit-learn",
)


def problem_for(capability: str, spec_key: str, spec: dict):
    return SimpleNamespace(
        mode=SimpleNamespace(value="none"),
        relations=[],
        facts=[],
        rules=[],
        constraints=[],
        items=[],
        people=[],
        variables={},
        structural_indicators={
            "required_capabilities": [capability],
            spec_key: spec,
        },
    )


def main() -> int:
    registry = build_extended_engine_registry()
    versions = {}
    for name in DISTRIBUTIONS:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = None

    cases = [
        (
            "unified_planning",
            ReasoningCapability.PLANNING,
            "planning_spec",
            {
                "fluents": ["ready", "done"],
                "initial_true": ["ready"],
                "actions": [
                    {
                        "name": "finish",
                        "preconditions": ["ready"],
                        "add": ["done"],
                    }
                ],
                "goals": ["done"],
            },
        ),
        (
            "z3_temporal",
            ReasoningCapability.TEMPORAL,
            "temporal_spec",
            {
                "tasks": {"A": {"duration": 2}, "B": {"duration": 3}},
                "before": [["A", "B"]],
            },
        ),
        (
            "shapely_pyproj",
            ReasoningCapability.SPATIAL,
            "spatial_spec",
            {
                "geometries": {
                    "area": {
                        "type": "Polygon",
                        "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]],
                    },
                    "point": {"type": "Point", "coordinates": [1, 1]},
                },
                "queries": [{"op": "contains", "left": "area", "right": "point"}],
            },
        ),
        (
            "pgmpy",
            ReasoningCapability.PROBABILISTIC,
            "probabilistic_spec",
            {
                "edges": [],
                "cpds": [
                    {
                        "variable": "A",
                        "variable_card": 2,
                        "values": [[0.7], [0.3]],
                        "state_names": {"A": ["no", "yes"]},
                    }
                ],
                "queries": [{"type": "posterior", "variables": ["A"]}],
            },
        ),
        (
            "dowhy",
            ReasoningCapability.CAUSAL,
            "causal_spec",
            {
                "data": [
                    {"W": 0, "T": 0, "Y": 0},
                    {"W": 0, "T": 1, "Y": 2},
                    {"W": 1, "T": 0, "Y": 1},
                    {"W": 1, "T": 1, "Y": 3},
                    {"W": 2, "T": 0, "Y": 2},
                    {"W": 2, "T": 1, "Y": 4},
                    {"W": 3, "T": 0, "Y": 3},
                    {"W": 3, "T": 1, "Y": 5},
                ],
                "treatment": "T",
                "outcome": "Y",
                "common_causes": ["W"],
            },
        ),
        (
            "clingo_abduction",
            ReasoningCapability.ABDUCTIVE,
            "abductive_spec",
            {
                "observations": ["wet"],
                "assumables": ["rain", "pipe_break"],
                "rules": ["wet :- rain.", "wet :- pipe_break."],
            },
        ),
        (
            "sklearn_tree_induction",
            ReasoningCapability.STATISTICAL_INDUCTION,
            "statistical_induction_spec",
            {
                "task": "classification",
                "features": ["x"],
                "target": "label",
                "examples": [
                    {"x": 0, "label": "low"},
                    {"x": 1, "label": "low"},
                    {"x": 2, "label": "low"},
                    {"x": 3, "label": "low"},
                    {"x": 6, "label": "high"},
                    {"x": 7, "label": "high"},
                    {"x": 8, "label": "high"},
                    {"x": 9, "label": "high"},
                ],
                "test_size": 0.25,
                "random_state": 42,
                "predict": [{"x": 8}],
            },
        ),
    ]

    report = {
        "python_executable": sys.executable,
        "python_version": sys.version.split()[0],
        "package_versions": versions,
        "registered_adapters": list(registry.names()),
        "engines": {},
    }
    failures = []

    for engine_name, capability, spec_key, spec in cases:
        adapter = registry.get(engine_name)
        if adapter is None:
            report["engines"][engine_name] = {
                "status": "missing",
                "valid": False,
            }
            failures.append(engine_name)
            continue

        problem = problem_for(capability.value, spec_key, spec)
        profile = ReasoningProfile(
            capabilities=(capability,),
            legacy_mode="none",
        )
        try:
            can_handle = bool(adapter.can_handle(problem, profile))
            result = adapter.execute(problem, {}) if can_handle else None
            valid = bool(
                result is not None
                and result.status == "success"
                and not result.formalization_errors
                and (result.validation or {}).get("valid") is True
            )
            report["engines"][engine_name] = {
                "status": result.status if result is not None else "cannot_handle",
                "can_handle": can_handle,
                "valid": valid,
                "validation": result.validation if result is not None else {},
                "formalization_errors": (
                    list(result.formalization_errors) if result is not None else []
                ),
            }
            if not valid:
                failures.append(engine_name)
        except Exception as exc:
            report["engines"][engine_name] = {
                "status": "exception",
                "valid": False,
                "error": f"{type(exc).__name__}: {exc}",
            }
            failures.append(engine_name)

    report["overall"] = "pass" if not failures else "fail"
    report["failed_engines"] = failures
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
