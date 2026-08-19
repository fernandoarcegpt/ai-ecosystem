"""Central operational decision tree for the agent ecosystem.

This module composes the existing semantic router with task-routing policy. It
does not execute actions; it produces an auditable decision that callers can
persist before dispatching work.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

from .semantic_router import classify_task_structure


@dataclass(frozen=True)
class OperationalDecision:
    action: str
    agent: str
    task_type: str
    tools: List[str]
    symbolic_engine: str
    use_memory: bool
    create_task: bool
    requires_human: bool
    verification: List[str]
    reasons: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def decide_operation(
    request: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Classify a request into an explicit, testable operational route."""
    context = context or {}
    lowered = request.lower()
    semantic = classify_task_structure(request)
    reasons: List[str] = []
    tools: List[str] = []

    missing_data = list(context.get("missing_required_data", []))
    conflicting_instructions = bool(context.get("conflicting_instructions"))
    requires_human = bool(missing_data or conflicting_instructions)
    if missing_data:
        reasons.append("Faltan datos requeridos: " + ", ".join(missing_data))
    if conflicting_instructions:
        reasons.append("Existen instrucciones materialmente incompatibles")

    if semantic["mode"] == "human_review":
        requires_human = True
        reasons.append("El enrutador semántico detectó incertidumbre explícita")

    if any(word in lowered for word in ("implementar", "corregir", "código", "codigo")):
        agent, task_type = "builder", "implementation"
        tools.extend(["repository", "terminal"])
        verification = ["tests", "diff_review"]
    elif any(word in lowered for word in ("probar", "verificar", "qa", "regresión", "regresion")):
        agent, task_type = "qa", "qa"
        tools.extend(["repository", "terminal"])
        verification = ["test_evidence"]
    elif any(word in lowered for word in ("investigar", "fuentes", "tendencia")):
        agent, task_type = "researcher", "research"
        tools.append("search")
        verification = ["source_traceability"]
    elif any(word in lowered for word in ("documentar", "informe", "manual")):
        agent, task_type = "km-agent", "documentation"
        tools.extend(["repository", "memory"])
        verification = ["reference_check"]
    else:
        agent, task_type = "orchestrator", "analysis"
        verification = ["result_review"]

    symbolic_engine = semantic["recommended_engine"]
    if symbolic_engine != "none":
        tools.append("neurosymbolic")
        reasons.append(
            f"Estructura {semantic['mode']} requiere {symbolic_engine}"
        )

    use_memory = bool(
        context.get("project_id")
        or context.get("continuation")
        or any(
            phrase in lowered
            for phrase in ("anterior", "previo", "continúa", "continua", "de nuevo")
        )
    )
    if use_memory and "memory" not in tools:
        tools.append("memory")

    create_task = bool(
        context.get("persist")
        or task_type in {"implementation", "qa", "research"}
        or any(word in lowered for word in ("objetivo", "tareas", "proyecto"))
    )
    action = "human_review" if requires_human else (
        "decompose_and_execute" if create_task else "execute"
    )
    if not reasons:
        reasons.append("Ruta determinada por el tipo observable de solicitud")

    return OperationalDecision(
        action=action,
        agent=agent,
        task_type=task_type,
        tools=list(dict.fromkeys(tools)),
        symbolic_engine=symbolic_engine,
        use_memory=use_memory,
        create_task=create_task,
        requires_human=requires_human,
        verification=verification,
        reasons=reasons,
    ).to_dict()


__all__ = ["OperationalDecision", "decide_operation"]
