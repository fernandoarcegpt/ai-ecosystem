"""Handler de la herramienta neurosimbólica oficial."""

from __future__ import annotations

import hashlib
import json
import logging
from importlib import metadata
from typing import Any, Callable, Dict

from .detection import detect_extended_reasoning


logger = logging.getLogger(__name__)

_ALLOWED_STRUCTURED_KEYS = {
    "required_capabilities",
    "planning_spec",
    "temporal_spec",
    "spatial_spec",
    "probabilistic_spec",
    "causal_spec",
    "abductive_spec",
    "statistical_induction_spec",
}

_RUNTIME_DISTRIBUTIONS = (
    "networkx",
    "pyDatalog",
    "z3-solver",
    "unified-planning",
    "up-pyperplan",
    "shapely",
    "pyproj",
    "pgmpy",
    "dowhy",
    "clingo",
    "scikit-learn",
)


def _sanitize_structured_context(raw: Any) -> Dict[str, Any]:
    """Acepta solo el subconjunto declarado por el schema del tool."""
    if not isinstance(raw, dict):
        return {}
    sanitized = {
        key: value
        for key, value in raw.items()
        if key in _ALLOWED_STRUCTURED_KEYS
    }
    capabilities = sanitized.get("required_capabilities")
    if capabilities is not None:
        if not isinstance(capabilities, list):
            sanitized.pop("required_capabilities", None)
        else:
            sanitized["required_capabilities"] = [
                str(value) for value in capabilities if str(value).strip()
            ]
    return sanitized


def _runtime_snapshot(integration) -> Dict[str, Any]:
    """Describe qué motores ve el mismo proceso Python que ejecuta Hermes."""
    versions = {}
    for distribution in _RUNTIME_DISTRIBUTIONS:
        try:
            versions[distribution] = metadata.version(distribution)
        except metadata.PackageNotFoundError:
            versions[distribution] = None

    legacy = {}
    coordinator = getattr(integration, "coordinator", None)
    if coordinator is not None:
        try:
            legacy = dict((coordinator.get_status() or {}).get("engines") or {})
        except Exception:
            legacy = {}

    extended = []
    meta_reasoner = getattr(integration, "meta_reasoner", None)
    registry = getattr(meta_reasoner, "registry", None)
    if registry is not None:
        try:
            extended = list(registry.names())
        except Exception:
            extended = []

    return {
        "legacy_engines": legacy,
        "extended_adapters": extended,
        "package_versions": versions,
    }


def _text_review_indicators(query: str) -> Dict[str, Any]:
    """Conserva señales de revisión detectadas antes del contexto del tool.

    ProblemExtractor históricamente podía sobrescribir structural_indicators al
    fusionar contexto estructurado. Esta comprobación independiente garantiza
    que una ambigüedad detectada desde el texto no desaparezca al llegar specs.
    """
    try:
        from reasoning.symbolic_problem_schema import ProblemExtractor

        problem = ProblemExtractor.extract(query, {})
        indicators = dict(problem.structural_indicators or {})
        if indicators.get("human_review"):
            return {
                "human_review": True,
                "review_reason": indicators.get(
                    "review_reason",
                    "ambiguous_symbolic_formalization",
                ),
            }
    except Exception:
        logger.debug("Could not preflight text review indicators", exc_info=True)
    return {}


def build_neurosymbolic_handler(
    runtime,
    *,
    proof_writer: Callable[..., None],
):
    """Crea un handler que ejecuta el pipeline una sola vez por request_id."""

    def handler(args: Dict[str, Any], **kwargs) -> str:
        args = args if isinstance(args, dict) else {}
        request_id = str(args.get("request_id", "")).strip()
        provided_query = str(args.get("query", "")).strip()
        if not request_id or not provided_query:
            return json.dumps(
                {
                    "status": "error",
                    "error": "query and request_id are required",
                },
                ensure_ascii=False,
            )

        cached = runtime.completed_contract(request_id)
        if cached is not None:
            proof_writer(
                "tool_result_reused",
                request_id=request_id,
                status=cached.get("status"),
            )
            return json.dumps(cached, ensure_ascii=False, default=str)

        # La herramienta solo puede ejecutar requests creados por el detector.
        # Esto evita que un request_id inventado por el modelo cambie la cadena
        # detector -> tool -> motor o permita sustituir el texto original.
        authoritative_query = runtime.query_for(request_id)
        if authoritative_query is None:
            proof_writer(
                "tool_rejected",
                request_id=request_id,
                reason="unknown_request_id",
            )
            return json.dumps(
                {
                    "status": "error",
                    "error": "unknown_neurosymbolic_request_id",
                },
                ensure_ascii=False,
            )

        query = authoritative_query
        query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
        detection = detect_extended_reasoning(query)
        structured = _sanitize_structured_context(args.get("structured_context"))

        # Las capacidades detectadas localmente no dependen de que el LLM las
        # recuerde al construir la llamada. Si falta su spec, el sistema falla
        # cerrado con human_review en vez de ejecutar otro motor por accidente.
        declared = list(structured.get("required_capabilities") or [])
        for capability in detection.get("capabilities", []):
            if capability not in declared:
                declared.append(capability)
        if declared:
            structured["required_capabilities"] = declared

        proof_writer(
            "tool_started",
            request_id=request_id,
            query_hash=query_hash,
            query_argument_matches_authoritative=(provided_query == query),
            structured_keys=sorted(structured),
            detected_capabilities=detection.get("capabilities", []),
            declared_capabilities=declared,
        )

        try:
            from .hermes_integration import get_symbolic_integration

            integration = get_symbolic_integration()
            snapshot = _runtime_snapshot(integration)
            proof_writer(
                "runtime_engine_inventory",
                request_id=request_id,
                query_hash=query_hash,
                **snapshot,
            )

            context = dict(structured)
            if structured:
                context["formalization_source"] = "hermes_tool_arguments"

            review_indicators = _text_review_indicators(query)
            if review_indicators:
                context["structural_indicators"] = {
                    **dict(context.get("structural_indicators") or {}),
                    **review_indicators,
                }

            contract = integration.run_grounded_task(
                query,
                context,
                run_id=request_id,
            )
        except Exception as exc:
            logger.warning(
                "Neurosymbolic tool execution failed: %s",
                type(exc).__name__,
                exc_info=True,
            )
            contract = {
                "schema_version": 2,
                "run_id": request_id,
                "status": "error",
                "engine_used": "none",
                "engines": {},
                "claims": [],
                "error": "internal_neurosymbolic_error",
                "rendered_markdown": (
                    "## Resultado neurosimbólico no concluyente\n\n"
                    "La herramienta falló y no se emitió una conclusión "
                    "verificable."
                ),
            }

        # Un evento por motor permite distinguir con precisión: detector sí,
        # herramienta sí, motor X sí/no. El mapa ``engines`` solo se construye
        # a partir de resultados que llegaron al contrato fundamentado.
        for engine, status in dict(contract.get("engines") or {}).items():
            proof_writer(
                "engine_result_observed",
                request_id=request_id,
                query_hash=query_hash,
                engine=engine,
                status=status,
                reasoning_plan=contract.get("reasoning_plan", []),
            )

        runtime.complete(request_id, contract, **kwargs)
        proof_writer(
            "tool_completed",
            request_id=request_id,
            query_hash=query_hash,
            run_id=contract.get("run_id"),
            status=contract.get("status"),
            engine=contract.get("engine_used"),
            engines=contract.get("engines", {}),
            reasoning_plan=contract.get("reasoning_plan", []),
            required_capabilities=contract.get("required_capabilities", []),
            review_reason=contract.get("review_reason"),
            result_hash=(contract.get("audit") or {}).get("result_hash"),
        )
        return json.dumps(contract, ensure_ascii=False, default=str)

    return handler
