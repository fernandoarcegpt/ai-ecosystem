"""Integración del razonamiento neurosimbólico con Hermes.

Flujo:
Hermes pre_llm_call -> ProblemExtractor -> SymbolicProblem -> coordinador
-> motor real (NetworkX/Z3/PyDatalog) -> evidencia -> contexto del LLM.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional

sys.path.insert(0, "/home/fernando/ai-ecosystem/skilled")

logger = logging.getLogger(__name__)

try:
    from reasoning.neuro_symbolic_engine import (
        NeurosymbolicCoordinator,
        NeurosymbolicCoordinationResult,
        get_coordinator,
        execute_symbolic_analysis,
        analyze_need_for_reasoning,
        auto_trigger_reasoning_if_needed,
    )
    from reasoning.symbolic_problem_schema import (
        ProblemExtractor,
        ReasoningMode,
    )
    NEUROSYMBOLIC_AVAILABLE = True
except ImportError as exc:
    logger.warning("Neuro-symbolic integration module import failed: %s", exc)
    NEUROSYMBOLIC_AVAILABLE = False
    NeurosymbolicCoordinator = None
    NeurosymbolicCoordinationResult = None
    get_coordinator = None
    execute_symbolic_analysis = None
    analyze_need_for_reasoning = None
    auto_trigger_reasoning_if_needed = None
    ProblemExtractor = None
    ReasoningMode = None


class HermesSymbolIntegration:
    """Adaptador fino entre Hermes y el coordinador neurosimbólico."""

    def __init__(self):
        self.coordinator = get_coordinator() if get_coordinator else None
        self.logger = logging.getLogger(__name__)

    def intercept_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Formalizar primero y, si existe un problema simbólico real,
        delegar selección de motor y ejecución al coordinador.

        No utiliza un prefiltro de keywords que pueda impedir que
        ProblemExtractor vea la consulta.
        """
        if (
            not NEUROSYMBOLIC_AVAILABLE
            or not self.coordinator
            or ProblemExtractor is None
            or ReasoningMode is None
        ):
            return None

        full_context = {
            "description": task_description,
            **(context or {}),
        }

        try:
            problem = ProblemExtractor.extract(
                task_description,
                full_context,
            )
        except Exception as exc:
            self.logger.warning(
                "Symbolic problem extraction failed: %s",
                exc,
                exc_info=True,
            )
            return None

        # Si el extractor no encontró estructura simbólica verificable,
        # dejar la consulta al LLM normal.
        if problem.mode == ReasoningMode.NONE:
            return None

        # Una estructura formalizable puede seguir siendo semánticamente
        # ambigua. En ese caso NO inyectar evidencia determinista.
        if problem.structural_indicators.get("human_review"):
            return {
                "status": "human_review",
                "reasoning_applied": False,
                "engine_used": "none",
                "analysis": {
                    "human_review": True,
                    "review_reason": problem.structural_indicators.get(
                        "review_reason",
                        "ambiguous_symbolic_formalization",
                    ),
                    "formalized_problem": problem.to_dict(),
                },
                "results": {},
                "evidence": {},
                "error": None,
                "formalization_errors": [],
            }

        self.logger.warning(
            "[neurosymbolic] formalized mode=%s relations=%d "
            "constraints=%d items=%d people=%d facts=%d rules=%d",
            problem.mode.value,
            len(problem.relations),
            len(problem.constraints),
            len(problem.items),
            len(problem.people),
            len(problem.facts),
            len(problem.rules),
        )

        result = self.coordinator.execute_symbolic_reasoning(
            task_description,
            full_context,
            engine_preference="auto",
        )
        return result.to_dict()

    def provide_temporal_context(
        self,
        conversation_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Conservar contexto estructurado ya disponible en el turno."""
        temporal_context = {
            "timestamp": datetime.now().isoformat(),
            "entities": [],
            "relations": [],
            "constraints": [],
            "dependencies": [],
            "rules": [],
            "assumptions": [],
            "facts": [],
            "source_types": set(),
        }

        mappings = (
            ("entities", "entities_from_conversation"),
            ("relations", "relations_from_conversation"),
            ("constraints", "constraints_from_conversation"),
            ("dependencies", "dependencies_from_conversation"),
            ("rules", "rules_from_conversation"),
            ("facts", "facts_from_conversation"),
        )

        for key, source_type in mappings:
            value = conversation_context.get(key, [])
            if value:
                temporal_context[key] = value
                temporal_context["source_types"].add(source_type)

        memory_data = conversation_context.get("memory_data", {})
        if memory_data:
            temporal_context["memory_context"] = memory_data
            temporal_context["source_types"].add("persistent_memory")

        kb_data = conversation_context.get("knowledge_broker_data", {})
        if kb_data:
            temporal_context["knowledge_broker_context"] = kb_data
            temporal_context["source_types"].add("knowledge_broker")

        temporal_context["source_types"] = list(
            temporal_context["source_types"]
        )
        return temporal_context

    def integrate_result_with_hermes_response(
        self,
        symbolic_result: Dict[str, Any],
    ) -> str:
        """Convertir únicamente resultados simbólicos reales en contexto para Hermes."""
        if not symbolic_result or symbolic_result.get("status") != "success":
            return ""

        engine = symbolic_result.get("engine_used", "none")
        analysis = symbolic_result.get("analysis", {}) or {}
        results = symbolic_result.get("results", {}) or {}
        evidence = symbolic_result.get("evidence", {}) or {}
        formalized = analysis.get("formalized_problem", {}) or {}

        lines = [
            "=== Evidencia de razonamiento neurosimbólico ===",
            f"Motor utilizado: {engine}",
            f"Modo formalizado: {formalized.get('mode', 'unknown')}",
        ]

        if formalized.get("relations"):
            lines.append(
                f"Relaciones formalizadas: {formalized['relations']}"
            )
        if formalized.get("constraints"):
            lines.append(
                f"Restricciones formalizadas: {formalized['constraints']}"
            )
        if formalized.get("items"):
            lines.append(f"Ítems: {formalized['items']}")
        if formalized.get("people"):
            lines.append(f"Personas: {formalized['people']}")

        # NetworkX
        if results.get("is_acyclic") is not None:
            lines.append(
                f"Grafo acíclico: {results.get('is_acyclic')}"
            )
        if results.get("cycles_found"):
            lines.append(
                f"Ciclos detectados: {results.get('cycles_found')}"
            )
        if results.get("topological_order"):
            lines.append(
                f"Orden topológico: {results.get('topological_order')}"
            )

        # Z3
        if results.get("solution_status") is not None:
            lines.append(
                f"Estado Z3: {results.get('solution_status')}"
            )
        if results.get("solution_values"):
            lines.append(
                f"Solución Z3: {results.get('solution_values')}"
            )
        if results.get("formalized_constraints"):
            lines.append(
                "Restricciones aplicadas por Z3: "
                f"{results.get('formalized_constraints')}"
            )

        # PyDatalog
        if results.get("derived_facts"):
            lines.append(
                f"Hechos derivados: {results.get('derived_facts')}"
            )
        if results.get("bindings"):
            lines.append(
                f"Bindings: {results.get('bindings')}"
            )

        if evidence.get("conclusion"):
            lines.append(
                f"Conclusión estructurada: {evidence.get('conclusion')}"
            )

        lines.extend(
            [
                f"Estado: {symbolic_result.get('status')}",
                "Usa esta evidencia como resultado determinista del motor; "
                "no la contradigas salvo que señales explícitamente un error "
                "de formalización o validación.",
                "==============================================",
            ]
        )

        return "\n".join(lines)

    def should_use_symbolic_reasoning(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Determinar mediante ProblemExtractor si existe estructura simbólica real.
        """
        if (
            not NEUROSYMBOLIC_AVAILABLE
            or not self.coordinator
            or ProblemExtractor is None
            or ReasoningMode is None
        ):
            return False

        full_context = {
            "description": task_description,
            **(context or {}),
        }

        try:
            problem = ProblemExtractor.extract(
                task_description,
                full_context,
            )
        except Exception:
            return False

        return problem.mode != ReasoningMode.NONE


_symbolic_integration = None


def get_symbolic_integration() -> HermesSymbolIntegration:
    """Obtener instancia singleton de integración simbólica."""
    global _symbolic_integration
    if _symbolic_integration is None:
        _symbolic_integration = HermesSymbolIntegration()
    return _symbolic_integration


def hermes_auto_detect_and_reason(
    task_description: str,
    context: Optional[Dict[str, Any]] = None,
) -> Optional[str]:
    """Detección, ejecución y formateo automático para hooks de Hermes."""
    integration = get_symbolic_integration()

    if not integration.coordinator:
        return None

    result = integration.intercept_task(
        task_description,
        context or {},
    )
    if not result:
        return None

    return integration.integrate_result_with_hermes_response(result)


def hermes_explicit_symbolic_reasoning(
    task_description: str,
    context: Dict[str, Any],
    engine_preference: Optional[str] = "auto",
) -> Dict[str, Any]:
    """Interfaz explícita para ejecución simbólica solicitada."""
    if not NEUROSYMBOLIC_AVAILABLE or not get_coordinator():
        return {
            "status": "error",
            "error": "Neurosymbolic reasoning not available",
        }

    coordinator = get_coordinator()
    result = coordinator.execute_symbolic_reasoning(
        task_description,
        context,
        engine_preference or "auto",
    )
    return result.to_dict()
