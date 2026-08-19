"""Integración del razonamiento neurosimbólico con Hermes.

Flujo legacy:
Hermes -> ProblemExtractor -> NeurosymbolicCoordinator -> NetworkX/Z3/PyDatalog.

Flujo extendido:
Hermes -> formalización estructurada -> ReasoningProfile -> MetaReasoner ->
motores especializados -> contrato fundamentado verificable.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .extended_grounded import build_extended_grounded_contract
from .grounded_result import build_grounded_contract
from .meta_reasoning import MetaReasoner, has_extended_capabilities, profile_for_problem

_REPOSITORY_ROOT = Path(
    os.getenv("AI_ECOSYSTEM_ROOT", Path(__file__).resolve().parents[2])
).expanduser().resolve()
_SKILLED_PATH = str(_REPOSITORY_ROOT / "skilled")
if _SKILLED_PATH not in sys.path:
    sys.path.insert(0, _SKILLED_PATH)

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


_SPEC_KEYS = (
    "planning_spec",
    "temporal_spec",
    "spatial_spec",
    "probabilistic_spec",
    "causal_spec",
    "abductive_spec",
    "statistical_induction_spec",
)

_EXTENDED_INTENT_MARKERS = {
    "planning": (
        "planificación clásica",
        "planificacion clasica",
        "precondiciones",
        "precondición",
        "precondicion",
        "estado inicial y objetivo",
        "acciones y objetivos",
    ),
    "probabilistic": (
        "bayes",
        "bayesiano",
        "bayesiana",
        "probabilidad posterior",
        "probabilidad condicional",
        "p(",
    ),
    "causal": (
        "efecto causal",
        "grafo causal",
        "variable de tratamiento",
        "confusor",
        "confusores",
    ),
    "counterfactual": (
        "contrafactual",
        "qué habría pasado si",
        "que habria pasado si",
        "qué hubiera pasado si",
        "que hubiera pasado si",
    ),
    "abductive": (
        "abducción",
        "abduccion",
        "abductiv",
        "explicaciones mínimas",
        "explicaciones minimas",
        "hipótesis permitidas",
        "hipotesis permitidas",
    ),
    "spatial": (
        "distancia geodésica",
        "distancia geodesica",
        "polígono",
        "poligono",
        "coordenadas geográficas",
        "coordenadas geograficas",
        "intersección espacial",
        "interseccion espacial",
    ),
    "temporal": (
        "restricciones temporales",
        "no se solapen",
        "sin solaparse",
        "duración de cada tarea",
        "duracion de cada tarea",
        "deadline",
        "fecha límite de la tarea",
        "fecha limite de la tarea",
    ),
    "statistical_induction": (
        "árbol de decisión",
        "arbol de decision",
        "entrena con estos ejemplos",
        "clasificación con estos datos",
        "clasificacion con estos datos",
        "regresión con estos datos",
        "regresion con estos datos",
    ),
}


class HermesSymbolIntegration:
    """Adaptador entre Hermes y los coordinadores neurosimbólicos."""

    def __init__(self):
        self.coordinator = get_coordinator() if get_coordinator else None
        self.meta_reasoner = MetaReasoner(self.coordinator) if self.coordinator else None
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def detect_extended_capabilities(task_description: str) -> List[str]:
        """Detecta intención extendida de forma conservadora.

        Esta detección solo decide si conviene solicitar la herramienta; no
        formaliza el problema ni autoriza a inventar datos faltantes.
        """
        text = str(task_description).lower()
        detected = []
        for capability, markers in _EXTENDED_INTENT_MARKERS.items():
            if any(marker in text for marker in markers):
                detected.append(capability)
        return detected

    def _prepare_context(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        incoming = dict(context or {})
        indicators = dict(incoming.get("structural_indicators") or {})

        # La API explícita y el tool de Hermes pueden entregar specs como
        # campos superiores; internamente se normalizan en structural_indicators.
        for key in _SPEC_KEYS:
            if incoming.get(key) is not None:
                indicators[key] = incoming[key]

        declared = indicators.get("required_capabilities") or incoming.get(
            "required_capabilities"
        ) or []
        if isinstance(declared, str):
            declared = [declared]
        declared = list(declared)

        detected = self.detect_extended_capabilities(task_description)
        for capability in detected:
            if capability not in declared:
                declared.append(capability)

        if declared:
            indicators["required_capabilities"] = declared
        if detected and not any(indicators.get(key) for key in _SPEC_KEYS):
            indicators["intent_detected_without_structured_spec"] = True

        if incoming.get("formalization_source"):
            indicators["formalization_source"] = incoming["formalization_source"]

        incoming["structural_indicators"] = indicators
        return {
            "description": task_description,
            **incoming,
        }

    @staticmethod
    def _human_review_result(problem, reason: str) -> Dict[str, Any]:
        return {
            "status": "human_review",
            "reasoning_applied": False,
            "engine_used": "none",
            "analysis": {
                "human_review": True,
                "review_reason": reason,
                "formalized_problem": problem.to_dict(),
            },
            "results": {},
            "evidence": {},
            "error": None,
            "formalization_errors": [],
        }

    def intercept_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Formaliza y enruta a la ruta legacy o al metarrazonador."""
        if (
            not NEUROSYMBOLIC_AVAILABLE
            or not self.coordinator
            or ProblemExtractor is None
            or ReasoningMode is None
        ):
            return None

        full_context = self._prepare_context(task_description, context)

        try:
            problem = ProblemExtractor.extract(task_description, full_context)
            profile = profile_for_problem(problem)
        except Exception as exc:
            self.logger.warning(
                "Symbolic problem extraction failed: %s",
                exc,
                exc_info=True,
            )
            return None

        extended = has_extended_capabilities(profile)
        if problem.mode == ReasoningMode.NONE and not extended:
            return None

        if problem.structural_indicators.get("human_review"):
            return self._human_review_result(
                problem,
                problem.structural_indicators.get(
                    "review_reason",
                    "ambiguous_symbolic_formalization",
                ),
            )

        self.logger.warning(
            "[neurosymbolic] formalized mode=%s capabilities=%s relations=%d "
            "constraints=%d items=%d people=%d facts=%d rules=%d",
            problem.mode.value,
            [capability.value for capability in profile.capabilities],
            len(problem.relations),
            len(problem.constraints),
            len(problem.items),
            len(problem.people),
            len(problem.facts),
            len(problem.rules),
        )

        if extended:
            if not self.meta_reasoner:
                return self._human_review_result(problem, "meta_reasoner_unavailable")
            return self.meta_reasoner.execute(
                task_description,
                problem,
                full_context,
            )

        result = self.coordinator.execute_symbolic_reasoning(
            task_description,
            full_context,
            engine_preference="auto",
        )
        return result.to_dict()

    def run_grounded_task(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        *,
        run_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Ejecutar el pipeline y devolver solo el contrato publicable."""
        result = self.intercept_task(task_description, context or {})
        if result and (result.get("analysis") or {}).get("meta_reasoning"):
            return build_extended_grounded_contract(result, run_id=run_id)
        return build_grounded_contract(result, run_id=run_id)

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
        """Convertir resultados reales en contexto consumible por Hermes."""
        if not symbolic_result:
            return ""

        if (symbolic_result.get("analysis") or {}).get("meta_reasoning"):
            contract = build_extended_grounded_contract(symbolic_result)
            return contract.get("rendered_markdown", "")

        if symbolic_result.get("status") != "success":
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

        if engine == "combined":
            lines.append("MODO: combined")

        if formalized.get("relations"):
            lines.append(f"Relaciones formalizadas: {formalized['relations']}")
        if formalized.get("constraints"):
            lines.append(f"Restricciones formalizadas: {formalized['constraints']}")
        if formalized.get("items"):
            lines.append(f"Ítems: {formalized['items']}")
        if formalized.get("people"):
            lines.append(f"Personas: {formalized['people']}")
        if formalized.get("facts"):
            lines.append(f"Hechos formalizados: {formalized['facts']}")
        if formalized.get("rules"):
            lines.append(f"Reglas formalizadas: {formalized['rules']}")
        if formalized.get("objectives"):
            lines.append(f"Objetivos: {formalized['objectives']}")
        if formalized.get("unknowns"):
            lines.append(f"HECHOS NO DETERMINADOS: {formalized['unknowns']}")

        if engine == "combined":
            required = results.get("required_engines", [])
            sections = {
                "networkx": results.get("networkx_analysis") or {},
                "pydatalog": results.get("pydatalog_analysis") or {},
                "z3": results.get("z3_analysis") or {},
            }
            lines.append("MOTORES REQUERIDOS:")
            for name in required:
                lines.append(f"- {name}: {sections.get(name, {}).get('status', 'missing')}")

            nx_result = sections["networkx"]
            if nx_result:
                lines.extend([
                    "NETWORKX:",
                    f"- acíclico: {nx_result.get('is_acyclic')}",
                    f"- orden: {nx_result.get('topological_order')}",
                    f"- alcance: {nx_result.get('transitive_relations', [])}",
                ])

            pd_result = sections["pydatalog"]
            if pd_result:
                lines.extend([
                    "PYDATALOG:",
                    f"- consultas: {pd_result.get('queries_executed', [])}",
                    f"- hechos derivados: {pd_result.get('derived_facts', [])}",
                ])

            z3_result = sections["z3"]
            if z3_result:
                lines.extend([
                    "Z3:",
                    f"- estado: {z3_result.get('solution_status')}",
                    f"- Optimize: {z3_result.get('optimizer_used', False)}",
                    f"- solución: {z3_result.get('solution_values', {})}",
                    f"- unsat core: {z3_result.get('unsat_core', [])}",
                ])

            if results.get("knowledge_transfers"):
                lines.append("TRANSFERENCIA ENTRE MOTORES: " f"{results.get('knowledge_transfers')}")
            if results.get("validation"):
                lines.append(f"VERIFICACIÓN: {results.get('validation')}")

        if results.get("is_acyclic") is not None:
            lines.append(f"Grafo acíclico: {results.get('is_acyclic')}")
        if results.get("cycles_found"):
            lines.append(f"Ciclos detectados: {results.get('cycles_found')}")
        if results.get("topological_order"):
            lines.append(f"Orden topológico: {results.get('topological_order')}")
        if results.get("solution_status") is not None:
            lines.append(f"Estado Z3: {results.get('solution_status')}")
        if results.get("solution_values"):
            lines.append(f"Solución Z3: {results.get('solution_values')}")
        if results.get("formalized_constraints"):
            lines.append("Restricciones aplicadas por Z3: " f"{results.get('formalized_constraints')}")
        if results.get("derived_facts"):
            lines.append(f"Hechos derivados: {results.get('derived_facts')}")
        if results.get("bindings"):
            lines.append(f"Bindings: {results.get('bindings')}")
        if evidence.get("conclusion"):
            lines.append(f"Conclusión estructurada: {evidence.get('conclusion')}")

        indicators = formalized.get("structural_indicators", {}) or {}
        lines.append(
            "HUMAN_REVIEW: "
            + (
                str(indicators.get("review_reason", "required"))
                if indicators.get("human_review")
                else "not_required"
            )
        )
        lines.extend([
            f"Estado: {symbolic_result.get('status')}",
            "Usa esta evidencia como resultado determinista del motor; no la contradigas salvo que señales explícitamente un error de formalización o validación.",
            "==============================================",
        ])
        return "\n".join(lines)

    def should_use_symbolic_reasoning(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Determina si existe estructura legacy o intención extendida formalizable."""
        if (
            not NEUROSYMBOLIC_AVAILABLE
            or not self.coordinator
            or ProblemExtractor is None
            or ReasoningMode is None
        ):
            return False

        full_context = self._prepare_context(task_description, context)
        try:
            problem = ProblemExtractor.extract(task_description, full_context)
            profile = profile_for_problem(problem)
        except Exception:
            return False

        return problem.mode != ReasoningMode.NONE or has_extended_capabilities(profile)


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
    result = integration.intercept_task(task_description, context or {})
    if not result:
        return None
    return integration.integrate_result_with_hermes_response(result)


def hermes_explicit_symbolic_reasoning(
    task_description: str,
    context: Dict[str, Any],
    engine_preference: Optional[str] = "auto",
) -> Dict[str, Any]:
    """Interfaz explícita para ejecución simbólica solicitada."""
    integration = get_symbolic_integration()
    if not NEUROSYMBOLIC_AVAILABLE or not integration.coordinator:
        return {
            "status": "error",
            "error": "Neurosymbolic reasoning not available",
        }

    if engine_preference in {None, "auto"}:
        return integration.intercept_task(task_description, context) or {
            "status": "skipped",
            "reasoning_applied": False,
            "engine_used": "none",
        }

    result = integration.coordinator.execute_symbolic_reasoning(
        task_description,
        context,
        engine_preference,
    )
    return result.to_dict()
