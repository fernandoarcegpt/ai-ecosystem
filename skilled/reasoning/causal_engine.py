"""Razonamiento causal y contrafactual verificable con DoWhy."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

import networkx as nx
import pandas as pd
from dowhy import CausalModel
import dowhy.gcm as gcm

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class CausalEngineAdapter:
    """Estima efectos causales y contrafactuales desde especificaciones explícitas."""

    name = "dowhy"
    capabilities: Sequence[ReasoningCapability] = (
        ReasoningCapability.CAUSAL,
        ReasoningCapability.COUNTERFACTUAL,
    )
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("causal_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        wants_causal = profile.requires(ReasoningCapability.CAUSAL)
        wants_counterfactual = profile.requires(ReasoningCapability.COUNTERFACTUAL)
        if not (wants_causal or wants_counterfactual):
            return False
        if not spec.get("data"):
            return False
        if wants_counterfactual:
            return bool(
                spec.get("graph_edges")
                and spec.get("counterfactual")
            )
        return bool(spec.get("treatment") and spec.get("outcome"))

    @staticmethod
    def _graph(spec: Dict[str, Any]) -> Optional[nx.DiGraph]:
        edges = [tuple(map(str, edge)) for edge in spec.get("graph_edges", [])]
        if not edges:
            return None
        graph = nx.DiGraph()
        graph.add_edges_from(edges)
        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("causal_spec.graph_edges must define a DAG")
        return graph

    @staticmethod
    def _serialize_frame(frame: pd.DataFrame) -> list[Dict[str, Any]]:
        return frame.where(pd.notnull(frame), None).to_dict(orient="records")

    def _estimate_effect(
        self,
        spec: Dict[str, Any],
        data: pd.DataFrame,
        graph: Optional[nx.DiGraph],
    ) -> Dict[str, Any]:
        treatment = str(spec.get("treatment") or "")
        outcome = str(spec.get("outcome") or "")
        if not treatment or not outcome:
            raise ValueError("causal_spec.treatment and causal_spec.outcome are required")
        missing = {treatment, outcome} - set(data.columns)
        if missing:
            raise ValueError(f"Missing causal columns: {sorted(missing)}")

        kwargs: Dict[str, Any] = {
            "data": data,
            "treatment": treatment,
            "outcome": outcome,
        }
        if graph is not None:
            kwargs["graph"] = graph
        else:
            common_causes = [str(value) for value in spec.get("common_causes", [])]
            instruments = [str(value) for value in spec.get("instruments", [])]
            if common_causes:
                kwargs["common_causes"] = common_causes
            if instruments:
                kwargs["instruments"] = instruments

        model = CausalModel(**kwargs)
        estimand = model.identify_effect(
            proceed_when_unidentifiable=bool(spec.get("proceed_when_unidentifiable", False))
        )
        method_name = str(spec.get("method_name") or "backdoor.linear_regression")
        estimate = model.estimate_effect(
            estimand,
            method_name=method_name,
            target_units=str(spec.get("target_units") or "ate"),
            test_significance=bool(spec.get("test_significance", False)),
            confidence_intervals=bool(spec.get("confidence_intervals", False)),
        )

        refutations = []
        for method in spec.get("refuters", []) or []:
            refutation = model.refute_estimate(
                estimand,
                estimate,
                method_name=str(method),
            )
            refutations.append(
                {
                    "method": str(method),
                    "result": str(refutation),
                }
            )

        value = getattr(estimate, "value", None)
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = str(value)

        return {
            "treatment": treatment,
            "outcome": outcome,
            "method_name": method_name,
            "identified_estimand": str(estimand),
            "effect_estimate": value,
            "refutations": refutations,
        }

    def _counterfactual(
        self,
        spec: Dict[str, Any],
        data: pd.DataFrame,
        graph: Optional[nx.DiGraph],
    ) -> Dict[str, Any]:
        counterfactual_spec = dict(spec.get("counterfactual") or {})
        if not counterfactual_spec:
            return {}
        if graph is None:
            raise ValueError("Counterfactual reasoning requires causal_spec.graph_edges")

        observed_records = list(counterfactual_spec.get("observed_data") or [])
        interventions_raw = dict(counterfactual_spec.get("interventions") or {})
        if not observed_records:
            raise ValueError("counterfactual.observed_data is required")
        if not interventions_raw:
            raise ValueError("counterfactual.interventions is required")

        observed_data = pd.DataFrame(observed_records)
        unknown_observed = set(graph.nodes) - set(observed_data.columns)
        if unknown_observed:
            raise ValueError(
                "Counterfactual observed_data is missing graph nodes: "
                f"{sorted(unknown_observed)}"
            )
        unknown_interventions = set(interventions_raw) - set(graph.nodes)
        if unknown_interventions:
            raise ValueError(
                f"Unknown intervention nodes: {sorted(unknown_interventions)}"
            )

        causal_model = gcm.InvertibleStructuralCausalModel(graph)
        gcm.auto.assign_causal_mechanisms(causal_model, data)
        gcm.fit(causal_model, data)
        interventions = {
            str(node): (lambda _value, fixed=value: fixed)
            for node, value in interventions_raw.items()
        }
        samples = gcm.counterfactual_samples(
            causal_model,
            interventions,
            observed_data=observed_data,
        )
        return {
            "interventions": interventions_raw,
            "observed_data": observed_records,
            "counterfactual_samples": self._serialize_frame(samples),
            "assumption_warning": (
                "Counterfactual estimates depend on the supplied causal DAG and "
                "the fitted invertible structural causal model."
            ),
        }

    def execute(
        self,
        problem: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        spec = self._spec(problem)
        try:
            data = pd.DataFrame(list(spec.get("data") or []))
            if data.empty:
                raise ValueError("causal_spec.data is required")
            graph = self._graph(spec)

            causal_result = {}
            if spec.get("treatment") or spec.get("outcome"):
                causal_result = self._estimate_effect(spec, data, graph)

            counterfactual_result = self._counterfactual(spec, data, graph)
            if not causal_result and not counterfactual_result:
                raise ValueError("No causal or counterfactual query was formalized")

            capabilities = [ReasoningCapability.CAUSAL]
            if counterfactual_result:
                capabilities.append(ReasoningCapability.COUNTERFACTUAL)

            warnings = []
            if counterfactual_result:
                warnings.append(counterfactual_result["assumption_warning"])

            data_result = {
                "causal_effect": causal_result,
                "counterfactual": counterfactual_result,
            }
            return EngineResult(
                engine=self.name,
                capabilities=tuple(capabilities),
                status="success",
                data=data_result,
                evidence=data_result,
                validation={
                    "valid": True,
                    "causal_graph_explicit": graph is not None,
                    "counterfactual_computed": bool(counterfactual_result),
                },
                warnings=warnings,
                transfer_payload={"causal_results": data_result},
                deterministic=False,
            )
        except Exception as exc:
            requested = [ReasoningCapability.CAUSAL]
            if dict(spec.get("counterfactual") or {}):
                requested.append(ReasoningCapability.COUNTERFACTUAL)
            return EngineResult(
                engine=self.name,
                capabilities=tuple(requested),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=False,
            )
