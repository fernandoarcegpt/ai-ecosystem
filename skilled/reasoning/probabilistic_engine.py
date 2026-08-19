"""Inferencia probabilística/Bayesiana verificable con pgmpy."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
from pgmpy.models import DiscreteBayesianNetwork

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class ProbabilisticEngineAdapter:
    """Ejecuta redes bayesianas discretas formalizadas explícitamente."""

    name = "pgmpy"
    capabilities: Sequence[ReasoningCapability] = (
        ReasoningCapability.PROBABILISTIC,
    )
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("probabilistic_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        return profile.requires(ReasoningCapability.PROBABILISTIC) and bool(
            spec.get("cpds") and spec.get("queries")
        )

    @staticmethod
    def _serialize_factor(factor: Any) -> Dict[str, Any]:
        variables = [str(value) for value in getattr(factor, "variables", [])]
        state_names = {
            str(key): list(value)
            for key, value in dict(getattr(factor, "state_names", {}) or {}).items()
        }
        values = getattr(factor, "values", None)
        if hasattr(values, "tolist"):
            values = values.tolist()
        return {
            "variables": variables,
            "state_names": state_names,
            "values": values,
        }

    def execute(
        self,
        problem: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> EngineResult:
        spec = self._spec(problem)
        try:
            raw_cpds = list(spec.get("cpds") or [])
            queries = list(spec.get("queries") or [])
            if not raw_cpds:
                raise ValueError("probabilistic_spec.cpds is required")
            if not queries:
                raise ValueError("probabilistic_spec.queries is required")

            edges = [tuple(map(str, edge)) for edge in spec.get("edges", [])]
            model = DiscreteBayesianNetwork(edges)

            cpds = []
            all_variables = set()
            for raw in raw_cpds:
                variable = str(raw["variable"])
                evidence = [str(value) for value in raw.get("evidence", [])]
                all_variables.add(variable)
                all_variables.update(evidence)
                cpd = TabularCPD(
                    variable=variable,
                    variable_card=int(raw["variable_card"]),
                    values=raw["values"],
                    evidence=evidence or None,
                    evidence_card=[int(value) for value in raw.get("evidence_card", [])] or None,
                    state_names={
                        str(key): list(value)
                        for key, value in dict(raw.get("state_names") or {}).items()
                    },
                )
                cpds.append(cpd)

            for variable in sorted(all_variables):
                if variable not in model.nodes:
                    model.add_node(variable)
            model.add_cpds(*cpds)
            if not model.check_model():
                raise ValueError("pgmpy rejected the Bayesian network model")

            inference = VariableElimination(model)
            query_results = []
            for raw_query in queries:
                variables = [str(value) for value in raw_query.get("variables", [])]
                evidence = {
                    str(key): value
                    for key, value in dict(raw_query.get("evidence") or {}).items()
                }
                if not variables:
                    raise ValueError("Every probabilistic query requires variables")
                unknown = (set(variables) | set(evidence)) - set(model.nodes)
                if unknown:
                    raise ValueError(f"Unknown variables in probabilistic query: {sorted(unknown)}")

                if raw_query.get("type", "posterior") == "map":
                    value = inference.map_query(
                        variables=variables,
                        evidence=evidence or None,
                        show_progress=False,
                    )
                    query_results.append(
                        {
                            "type": "map",
                            "variables": variables,
                            "evidence": evidence,
                            "result": dict(value),
                        }
                    )
                else:
                    factor = inference.query(
                        variables=variables,
                        evidence=evidence or None,
                        joint=True,
                        show_progress=False,
                    )
                    query_results.append(
                        {
                            "type": "posterior",
                            "variables": variables,
                            "evidence": evidence,
                            "result": self._serialize_factor(factor),
                        }
                    )

            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={
                    "model_valid": True,
                    "nodes": [str(node) for node in model.nodes],
                    "edges": [[str(a), str(b)] for a, b in model.edges],
                    "queries": query_results,
                },
                evidence={"posterior_queries": query_results},
                validation={
                    "valid": True,
                    "model_checked": True,
                    "query_count": len(query_results),
                },
                transfer_payload={"probabilistic_results": query_results},
                deterministic=False,
            )
        except Exception as exc:
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=False,
            )
