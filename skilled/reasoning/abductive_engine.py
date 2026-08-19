"""Abducción verificable sobre Answer Set Programming con Clingo.

El motor no inventa hipótesis: solo puede seleccionar átomos declarados en
``abductive_spec.assumables`` y busca explicaciones mínimas que hagan verdaderas
las observaciones bajo los hechos, reglas y restricciones suministrados.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import clingo

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class AbductiveEngineAdapter:
    name = "clingo_abduction"
    capabilities: Sequence[ReasoningCapability] = (ReasoningCapability.ABDUCTIVE,)
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("abductive_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        return profile.requires(ReasoningCapability.ABDUCTIVE) and bool(
            spec.get("observations") and spec.get("assumables")
        )

    @staticmethod
    def _normalize_statement(value: Any) -> str:
        statement = str(value).strip()
        if not statement:
            raise ValueError("ASP statements cannot be empty")
        return statement if statement.endswith(".") else statement + "."

    @staticmethod
    def _normalize_atom(value: Any) -> str:
        atom = str(value).strip().rstrip(".")
        if not atom or any(token in atom for token in (":-", "{", "}", ";")):
            raise ValueError(f"Invalid abductive atom: {value}")
        return atom

    def execute(
        self,
        problem: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        spec = self._spec(problem)
        try:
            observations = [self._normalize_atom(v) for v in spec.get("observations", [])]
            assumables = [self._normalize_atom(v) for v in spec.get("assumables", [])]
            if not observations:
                raise ValueError("abductive_spec.observations is required")
            if not assumables:
                raise ValueError("abductive_spec.assumables is required")
            if len(set(assumables)) != len(assumables):
                raise ValueError("abductive_spec.assumables contains duplicates")

            program = []
            program.extend(self._normalize_statement(v) for v in spec.get("facts", []))
            program.extend(self._normalize_statement(v) for v in spec.get("rules", []))
            program.extend(self._normalize_statement(v) for v in spec.get("constraints", []))

            # Cada hipótesis declarada es opcional. Las observaciones deben ser
            # verdaderas en cualquier modelo aceptado.
            program.extend(f"{{{atom}}}." for atom in assumables)
            program.extend(f":- not {atom}." for atom in observations)

            control = clingo.Control(["0"])
            control.add("base", [], "\n".join(program))
            control.ground([("base", [])])

            assumable_set = set(assumables)
            explanations = []
            max_models = int(spec.get("max_models", 10000))
            if max_models <= 0:
                raise ValueError("abductive_spec.max_models must be positive")

            with control.solve(yield_=True) as handle:
                for index, model in enumerate(handle, start=1):
                    if index > max_models:
                        raise ValueError(
                            "Abductive search exceeded max_models; narrow the hypothesis space"
                        )
                    atoms = {str(symbol) for symbol in model.symbols(atoms=True)}
                    selected = sorted(atoms & assumable_set)
                    explanations.append(selected)
                solve_result = handle.get()

            if not solve_result.satisfiable or not explanations:
                return EngineResult(
                    engine=self.name,
                    capabilities=tuple(self.capabilities),
                    status="success",
                    data={
                        "solution_status": "no_explanation",
                        "minimal_explanations": [],
                        "models_examined": len(explanations),
                    },
                    evidence={"minimal_explanations": []},
                    validation={"valid": True, "explanation_found": False},
                    transfer_payload={"abductive_explanations": []},
                    deterministic=True,
                )

            minimum_size = min(len(item) for item in explanations)
            minimal = []
            seen = set()
            for explanation in explanations:
                if len(explanation) != minimum_size:
                    continue
                key = tuple(explanation)
                if key not in seen:
                    seen.add(key)
                    minimal.append(explanation)
            minimal.sort()

            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={
                    "solution_status": "explained",
                    "minimal_explanations": minimal,
                    "minimum_hypothesis_count": minimum_size,
                    "models_examined": len(explanations),
                    "observations": observations,
                    "assumables": assumables,
                },
                evidence={
                    "observations": observations,
                    "minimal_explanations": minimal,
                },
                validation={
                    "valid": True,
                    "explanation_found": True,
                    "minimality_checked_by_exhaustive_models": True,
                },
                transfer_payload={"abductive_explanations": minimal},
                deterministic=True,
            )
        except Exception as exc:
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=True,
            )
