"""Metarrazonamiento por capacidades para el pipeline neurosimbólico.

La ruta legacy (NetworkX/PyDatalog/Z3) permanece intacta. Este módulo se activa
solo cuando el problema declara capacidades adicionales y compone motores
especializados mediante ``EngineRegistry``. Cada motor recibe el mismo
``SymbolicProblem`` y un contexto acumulado con transferencias anteriores.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from .engine_contracts import ReasoningCapability, ReasoningProfile
from .extended_engine_registry import build_extended_engine_registry


_SPEC_CAPABILITIES = {
    "planning_spec": ReasoningCapability.PLANNING,
    "temporal_spec": ReasoningCapability.TEMPORAL,
    "spatial_spec": ReasoningCapability.SPATIAL,
    "probabilistic_spec": ReasoningCapability.PROBABILISTIC,
    "causal_spec": ReasoningCapability.CAUSAL,
    "abductive_spec": ReasoningCapability.ABDUCTIVE,
    "statistical_induction_spec": ReasoningCapability.STATISTICAL_INDUCTION,
}

_LEGACY_CAPABILITIES = {
    ReasoningCapability.GRAPH,
    ReasoningCapability.LOGIC,
    ReasoningCapability.CONSTRAINTS,
}

_EXTENDED_EXECUTION_ORDER = {
    "clingo_abduction": 10,
    "dowhy": 20,
    "pgmpy": 30,
    "shapely_pyproj": 40,
    "unified_planning": 50,
    "z3_temporal": 60,
    "sklearn_tree_induction": 70,
}


def profile_for_problem(problem: Any) -> ReasoningProfile:
    """Deriva capacidades actuales y las declaradas por especificaciones."""
    base = ReasoningProfile.from_problem(problem)
    capabilities = list(base.capabilities)
    indicators = dict(getattr(problem, "structural_indicators", {}) or {})

    for key, capability in _SPEC_CAPABILITIES.items():
        if indicators.get(key):
            capabilities.append(capability)

    causal_spec = dict(indicators.get("causal_spec") or {})
    if causal_spec.get("counterfactual"):
        capabilities.append(ReasoningCapability.COUNTERFACTUAL)

    return ReasoningProfile(
        capabilities=tuple(dict.fromkeys(capabilities)),
        legacy_mode=base.legacy_mode,
        human_review=base.human_review,
        review_reason=base.review_reason,
    )


def has_extended_capabilities(profile: ReasoningProfile) -> bool:
    return any(capability not in _LEGACY_CAPABILITIES for capability in profile.capabilities)


class MetaReasoner:
    """Construye y ejecuta planes de razonamiento multi-motor."""

    def __init__(self, legacy_coordinator: Any, registry=None):
        self.legacy_coordinator = legacy_coordinator
        self.registry = registry or build_extended_engine_registry()

    def _legacy_plan(self, capabilities: Sequence[ReasoningCapability]) -> List[str]:
        requested = set(capabilities) & _LEGACY_CAPABILITIES
        if not requested:
            return []
        if len(requested) > 1:
            return ["legacy_combined"]
        if ReasoningCapability.GRAPH in requested:
            return ["networkx"]
        if ReasoningCapability.LOGIC in requested:
            return ["pydatalog"]
        return ["z3"]

    def build_plan(self, problem: Any, profile: Optional[ReasoningProfile] = None) -> Tuple[str, ...]:
        profile = profile or profile_for_problem(problem)
        legacy_steps = self._legacy_plan(profile.capabilities)
        extended = tuple(
            capability
            for capability in profile.capabilities
            if capability not in _LEGACY_CAPABILITIES
        )
        extended_steps: Iterable[str] = ()
        if extended:
            extended_profile = ReasoningProfile(
                capabilities=extended,
                legacy_mode=profile.legacy_mode,
                human_review=profile.human_review,
                review_reason=profile.review_reason,
            )
            extended_steps = self.registry.build_plan(extended_profile, problem)
            extended_steps = sorted(
                extended_steps,
                key=lambda name: (_EXTENDED_EXECUTION_ORDER.get(name, 999), name),
            )
        return tuple([*legacy_steps, *extended_steps])

    @staticmethod
    def _legacy_envelope(name: str, capabilities: Sequence[ReasoningCapability], raw: Dict[str, Any]) -> Dict[str, Any]:
        status = str(raw.get("status", "error"))
        return {
            "engine": name,
            "capabilities": [capability.value for capability in capabilities],
            "status": status,
            "data": raw,
            "evidence": {},
            "validation": dict(raw.get("validation") or {}),
            "formalization_errors": list(raw.get("formalization_errors", [])),
            "warnings": [],
            "transfer_payload": {},
            "deterministic": True,
            "executed": status not in {"skipped", "formalization_error"},
        }

    def _execute_legacy(self, step: str, problem: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        if step == "networkx":
            raw = self.legacy_coordinator._run_networkx_reasoning(problem, context)
            return self._legacy_envelope(step, (ReasoningCapability.GRAPH,), raw)
        if step == "pydatalog":
            raw = self.legacy_coordinator._run_pydatalog_reasoning(problem, context)
            return self._legacy_envelope(step, (ReasoningCapability.LOGIC,), raw)
        if step == "z3":
            raw = self.legacy_coordinator._run_z3_reasoning(problem, context)
            return self._legacy_envelope(step, (ReasoningCapability.CONSTRAINTS,), raw)
        raw = self.legacy_coordinator._run_combined_reasoning(problem, context)
        capabilities = tuple(
            capability
            for capability in (
                ReasoningCapability.GRAPH,
                ReasoningCapability.LOGIC,
                ReasoningCapability.CONSTRAINTS,
            )
            if (
                (capability == ReasoningCapability.GRAPH and getattr(problem, "relations", None))
                or (capability == ReasoningCapability.LOGIC and (getattr(problem, "facts", None) or getattr(problem, "rules", None)))
                or (
                    capability == ReasoningCapability.CONSTRAINTS
                    and (
                        getattr(problem, "constraints", None)
                        or getattr(problem, "variables", None)
                        or (getattr(problem, "items", None) and getattr(problem, "people", None))
                    )
                )
            )
        )
        return self._legacy_envelope(step, capabilities, raw)

    def execute(
        self,
        task_description: str,
        problem: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        start = time.time()
        profile = profile_for_problem(problem)

        if profile.human_review:
            return self._review_result(
                problem,
                profile,
                profile.review_reason or "ambiguous_symbolic_formalization",
                start,
            )

        try:
            plan = self.build_plan(problem, profile)
        except LookupError as exc:
            return self._review_result(problem, profile, str(exc), start)

        if not plan:
            return self._review_result(problem, profile, "no_reasoning_engine_selected", start)

        engine_results: Dict[str, Dict[str, Any]] = {}
        transfers = []
        working_context = dict(context or {})
        working_context.setdefault("engine_transfers", {})
        failures = []

        for step in plan:
            if step in {"networkx", "pydatalog", "z3", "legacy_combined"}:
                envelope = self._execute_legacy(step, problem, working_context)
            else:
                adapter = self.registry.get(step)
                if adapter is None:
                    failures.append({"engine": step, "reason": "adapter_missing"})
                    break
                result = adapter.execute(problem, working_context)
                envelope = result.to_dict()

            engine_results[step] = envelope
            if envelope.get("status") != "success" or envelope.get("formalization_errors"):
                failures.append(
                    {
                        "engine": step,
                        "status": envelope.get("status"),
                        "formalization_errors": envelope.get("formalization_errors", []),
                    }
                )
                break

            payload = dict(envelope.get("transfer_payload") or {})
            if payload:
                working_context["engine_transfers"][step] = payload
                transfers.append({"from": step, "payload": payload})

        if failures:
            formalization_failure = any(
                item.get("status") == "formalization_error"
                or item.get("formalization_errors")
                for item in failures
            )
            status = "human_review" if formalization_failure else "error"
            review_reason = "insufficient_or_invalid_formalization" if formalization_failure else None
        else:
            status = "success"
            review_reason = None

        deterministic = all(
            envelope.get("deterministic") is True
            for envelope in engine_results.values()
        ) if engine_results else True

        result = {
            "status": status,
            "reasoning_applied": status == "success",
            "engine_used": plan[0] if len(plan) == 1 else "meta_combined",
            "analysis": {
                "formalized_problem": problem.to_dict(),
                "reasoning_profile": profile.to_dict(),
                "reasoning_plan": list(plan),
                "meta_reasoning": True,
                "review_reason": review_reason,
            },
            "results": {
                "status": "success" if not failures else "error",
                "required_capabilities": [capability.value for capability in profile.capabilities],
                "reasoning_plan": list(plan),
                "executed_engines": list(engine_results),
                "engine_results": engine_results,
                "knowledge_transfers": transfers,
                "failures": failures,
                "validation": {
                    "all_required_engines_succeeded": not failures and len(engine_results) == len(plan),
                    "fail_closed": True,
                },
                "deterministic": deterministic,
            },
            "evidence": {
                "engine_results": engine_results,
                "knowledge_transfers": transfers,
            },
            "execution_time": time.time() - start,
            "error": None if status in {"success", "human_review"} else "meta_reasoning_engine_failure",
            "formalization_errors": [
                error
                for failure in failures
                for error in failure.get("formalization_errors", [])
            ],
        }
        if status == "human_review":
            result["analysis"]["human_review"] = True
        return result

    @staticmethod
    def _review_result(problem: Any, profile: ReasoningProfile, reason: str, start: float) -> Dict[str, Any]:
        return {
            "status": "human_review",
            "reasoning_applied": False,
            "engine_used": "none",
            "analysis": {
                "formalized_problem": problem.to_dict(),
                "reasoning_profile": profile.to_dict(),
                "reasoning_plan": [],
                "meta_reasoning": True,
                "human_review": True,
                "review_reason": reason,
            },
            "results": {},
            "evidence": {},
            "execution_time": time.time() - start,
            "error": None,
            "formalization_errors": [],
        }
