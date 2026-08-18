"""Handler de la herramienta neurosimbólica oficial."""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict


logger = logging.getLogger(__name__)


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
        proof_writer("tool_started", request_id=request_id)

        try:
            from .hermes_integration import get_symbolic_integration

            integration = get_symbolic_integration()
            contract = integration.run_grounded_task(
                query,
                {},
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
                    "operativa determinista."
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
