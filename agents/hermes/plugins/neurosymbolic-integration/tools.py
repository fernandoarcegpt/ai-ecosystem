"""Handler de la herramienta neurosimbólica oficial."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict


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


def build_neurosymbolic_handler(
    runtime,
    *,
    proof_writer: Callable[..., None],
):
    """Crea un handler que ejecuta el pipeline una sola vez por request_id."""

    def handler(args: Dict[str, Any], **kwargs) -> str:
        args = args if isinstance(args, dict) else {}
        request_id = str(args.get("request_id", "")).strip()
        query = str(args.get("query", "")).strip()
        if not request_id or not query:
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

        # El texto guardado por el detector es autoritativo. Esto evita que el
        # modelo resuma o cambie silenciosamente el problema al llamar el tool.
        query = runtime.query_for(request_id) or query
        structured = _sanitize_structured_context(args.get("structured_context"))
        proof_writer(
            "tool_started",
            request_id=request_id,
            structured_keys=sorted(structured),
        )

        try:
            from .hermes_integration import get_symbolic_integration

            integration = get_symbolic_integration()
            context = dict(structured)
            if structured:
                context["formalization_source"] = "hermes_tool_arguments"
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
                "schema_version": 1,
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

        runtime.complete(request_id, contract, **kwargs)
        proof_writer(
            "tool_completed",
            request_id=request_id,
            run_id=contract.get("run_id"),
            status=contract.get("status"),
            engine=contract.get("engine_used"),
            engines=contract.get("engines", {}),
            result_hash=(contract.get("audit") or {}).get("result_hash"),
        )
        return json.dumps(contract, ensure_ascii=False, default=str)

    return handler
