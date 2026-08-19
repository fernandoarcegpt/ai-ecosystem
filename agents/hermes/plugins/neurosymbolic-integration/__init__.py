"""Plugin Hermes para razonamiento neurosimbólico auditable.

El hook ``pre_llm_call`` detecta la necesidad de razonamiento y solicita la
herramienta oficial. La ejecución real ocurre en ``neurosymbolic_reasoning`` y
``transform_llm_output`` publica únicamente Markdown fundamentado por motores.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from .detection import detect_extended_reasoning
from .runtime import NeurosymbolicRuntime
from .schemas import NEUROSYMBOLIC_REASONING
from .tools import build_neurosymbolic_handler

logger = logging.getLogger(__name__)

_registered = False


def _write_proof(event: str, **fields: Any) -> None:
    """Añade un evento JSONL acotado; el historial Hermes sigue siendo fuente."""
    selected = os.getenv(
        "HERMES_NEUROSYMBOLIC_PROOF_LOG",
        "/tmp/neuro_hook_proof.log",
    )
    proof_path = Path(selected).expanduser()
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    with proof_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, default=str) + "\n")


def _required_tool_context(
    request_id: str,
    capability_hints: Sequence[str] = (),
) -> str:
    hint_text = ""
    if capability_hints:
        hint_text = (
            " El detector local encontró estas capacidades: "
            f"{', '.join(capability_hints)}. Inclúyelas en "
            "`structured_context.required_capabilities`. Para `graph`, usa "
            "`relations`; para `logic`, usa `facts`, `rules` y `queries`; para "
            "`constraints`, usa `items`/`people`/`constraints` según corresponda. "
            "Para las demás capacidades usa el `*_spec` exacto descrito en el "
            "schema de la herramienta. Solo crea una estructura cuando todos "
            "sus datos estén explícitos en el mensaje."
        )
    return (
        "REQUIERE_HERRAMIENTA_NEUROSIMBOLICA\n"
        "Antes de responder debes llamar exactamente una vez a la herramienta "
        "`neurosymbolic_reasoning`. Copia el mensaje completo del usuario en "
        "`query` y usa este `request_id` sin modificarlo: "
        f"`{request_id}`. No calcules el resultado por tu cuenta."
        f"{hint_text} "
        "Completa `structured_context` SOLO con hechos, números, relaciones, "
        "reglas, restricciones y ejemplos explícitos en el mensaje. No inventes "
        "datos faltantes ni completes supuestos implícitos. Si reconoces el tipo "
        "de razonamiento pero faltan datos para formalizarlo, incluye solo "
        "`required_capabilities` y omite la estructura incompleta; el sistema "
        "debe fallar cerrado. Después de la llamada no agregues plazos, "
        "responsables, autorizaciones, urgencia ni recomendaciones que no "
        "aparezcan en `rendered_markdown`."
    )


def register(ctx):
    """Registra una herramienta oficial y los hooks de control del turno."""
    global _registered
    if _registered:
        return

    runtime = NeurosymbolicRuntime()

    def pre_llm_call_hook(**kwargs) -> Optional[Dict[str, str]]:
        user_message = kwargs.get("user_message") or ""
        if not isinstance(user_message, str) or not user_message.strip():
            runtime.clear_turn(**kwargs)
            return None

        # La orquestación autónoma existente conserva su opt-in explícito y no
        # se presenta como razonamiento neurosimbólico.
        if user_message.strip().lower().startswith("/orchestrate "):
            runtime.clear_turn(**kwargs)
            if os.getenv("HERMES_AUTONOMY_ENABLED") != "1":
                return {
                    "context": (
                        "Ejecución autónoma no habilitada. Configure "
                        "HERMES_AUTONOMY_ENABLED=1 para usar /orchestrate."
                    )
                }
            from orchestration.hermes_bridge import run_from_hermes

            orchestration = run_from_hermes(user_message)
            distribution = orchestration["task_report"]["status_distribution"]
            completed = int(distribution.get("completed", 0))
            blocked = int(distribution.get("blocked", 0))
            failed = int(distribution.get("failed", 0))
            _write_proof(
                "autonomy_completed",
                completed=completed,
                blocked=blocked,
                failed=failed,
            )
            return {
                "context": (
                    "Resultado autónomo verificable: "
                    f"completed={completed}, blocked={blocked}, failed={failed}."
                )
            }

        detection = detect_extended_reasoning(user_message)
        try:
            from .hermes_integration import get_symbolic_integration

            integration = get_symbolic_integration()
            core_detector_required = integration.should_use_symbolic_reasoning(
                user_message,
                {},
            )
            requires_tool = bool(
                core_detector_required or detection.get("requires_tool")
            )
            _write_proof(
                "detector_decision",
                decision="require_tool" if requires_tool else "skip",
                detected_capabilities=detection.get("capabilities", []),
                detection_scores=detection.get("scores", {}),
                detection_evidence=detection.get("evidence", {}),
                core_detector_required=core_detector_required,
                session_id=kwargs.get("session_id"),
                turn_id=kwargs.get("turn_id"),
            )
            if not requires_tool:
                runtime.clear_turn(**kwargs)
                _write_proof(
                    "detector_skipped",
                    session_id=kwargs.get("session_id"),
                    turn_id=kwargs.get("turn_id"),
                )
                return None

            request_id = runtime.begin(user_message, **kwargs)
            _write_proof(
                "tool_required",
                request_id=request_id,
                detected_capabilities=detection.get("capabilities", []),
                session_id=kwargs.get("session_id"),
                turn_id=kwargs.get("turn_id"),
                platform=kwargs.get("platform"),
            )
            return {
                "context": _required_tool_context(
                    request_id,
                    detection.get("capabilities", []),
                )
            }
        except Exception as exc:
            request_id = runtime.begin(user_message, **kwargs)
            logger.warning(
                "[neurosymbolic-plugin] detector failed: %s",
                exc,
                exc_info=True,
            )
            _write_proof(
                "detector_error",
                request_id=request_id,
                error=type(exc).__name__,
                detected_capabilities=detection.get("capabilities", []),
            )
            return {
                "context": _required_tool_context(
                    request_id,
                    detection.get("capabilities", []),
                )
            }

    tool_handler = build_neurosymbolic_handler(
        runtime,
        proof_writer=_write_proof,
    )

    def post_tool_call_hook(
        tool_name: str = "",
        args: Optional[Dict[str, Any]] = None,
        result: str = "",
        task_id: str = "",
        duration_ms: int = 0,
        **kwargs,
    ) -> None:
        if tool_name != "neurosymbolic_reasoning":
            return
        _write_proof(
            "official_tool_observed",
            tool=tool_name,
            request_id=(args or {}).get("request_id"),
            task_id=task_id,
            session_id=kwargs.get("session_id"),
            turn_id=kwargs.get("turn_id"),
            duration_ms=duration_ms,
        )

    def transform_llm_output_hook(
        response_text: str = "",
        session_id: str = "",
        **kwargs,
    ) -> Optional[str]:
        record = runtime.consume_turn(session_id=session_id, **kwargs)
        if record is None:
            return None
        contract = record.get("contract")
        if isinstance(contract, dict) and contract.get("rendered_markdown"):
            _write_proof(
                "output_replaced",
                run_id=contract.get("run_id"),
                status=contract.get("status"),
                engine=contract.get("engine_used"),
                engines=contract.get("engines", {}),
            )
            return str(contract["rendered_markdown"])

        _write_proof(
            "required_tool_missing",
            session_id=session_id,
        )
        return (
            "## Razonamiento neurosimbólico no ejecutado\n\n"
            "El turno requería la herramienta `neurosymbolic_reasoning`, pero "
            "Hermes no registró su ejecución. Para evitar una conclusión no "
            "verificada, se descartó la respuesta generada por el modelo."
        )

    ctx.register_tool(
        name="neurosymbolic_reasoning",
        toolset="neurosymbolic",
        schema=NEUROSYMBOLIC_REASONING,
        handler=tool_handler,
        description=NEUROSYMBOLIC_REASONING["description"],
        emoji="🧠",
    )
    ctx.register_hook("pre_llm_call", pre_llm_call_hook)
    ctx.register_hook("post_tool_call", post_tool_call_hook)
    ctx.register_hook("transform_llm_output", transform_llm_output_hook)

    _registered = True
    logger.info("Neurosymbolic tool and grounding hooks registered successfully")
