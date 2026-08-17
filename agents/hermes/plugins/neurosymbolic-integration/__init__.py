"""Neurosymbolic Integration Plugin for Hermes.

Integra automáticamente el núcleo neurosimbólico con Hermes mediante
el hook pre_llm_call.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

_registered = False


def _write_proof(message: str) -> None:
    """Append machine-readable evidence when a proof log is configured."""
    selected = os.getenv(
        "HERMES_NEUROSYMBOLIC_PROOF_LOG",
        "/tmp/neuro_hook_proof.log",
    )
    proof_path = Path(selected).expanduser()
    proof_path.parent.mkdir(parents=True, exist_ok=True)
    with proof_path.open("a", encoding="utf-8") as handle:
        handle.write(message.rstrip("\n") + "\n")


def register(ctx):
    """Registrar el hook neurosimbólico pre_llm_call en Hermes."""
    global _registered

    logger.warning("[neurosymbolic-plugin] register(ctx) invoked")
    logger.warning("  ctx type: %s", type(ctx))
    logger.warning(
        "  ctx.manifest.name: %s",
        getattr(getattr(ctx, "manifest", None), "name", None),
    )

    if _registered:
        logger.warning(
            "[neurosymbolic-plugin] Already registered, returning early"
        )
        return

    try:
        from .hermes_integration import get_symbolic_integration

        def pre_llm_call_hook(**kwargs) -> Optional[Dict[str, str]]:
            """Ejecutar razonamiento simbólico antes de la llamada al LLM."""
            try:
                logger.warning(
                    "[neurosymbolic-plugin] pre_llm_call_hook invoked"
                )
                _write_proof("HOOK_INVOKED")
                logger.warning(
                    "  kwargs keys: %s",
                    list(kwargs.keys()),
                )

                user_message = kwargs.get("user_message") or ""
                platform = kwargs.get("platform", "cli") or "cli"

                if not isinstance(user_message, str) or not user_message.strip():
                    logger.warning(
                        "[neurosymbolic-plugin] Empty user message, returning None"
                    )
                    return None

                # Durante esta fase de validación se mantiene CLI.
                if platform != "cli":
                    logger.warning(
                        "[neurosymbolic-plugin] Not CLI platform (%s), returning None",
                        platform,
                    )
                    return None

                integration = get_symbolic_integration()

                # Delegar detección, formalización, selección de motor y ejecución
                # al coordinador central. No filtrar aquí por keywords.
                result = integration.intercept_task(
                    user_message,
                    {},
                )

                if not result:
                    logger.warning(
                        "[neurosymbolic-plugin] No symbolic reasoning required"
                    )
                    return None

                status = result.get("status")
                engine = result.get("engine_used")

                logger.warning(
                    "[neurosymbolic-plugin] reasoning executed: "
                    "status=%s engine=%s",
                    status,
                    engine,
                )
                _write_proof(f"ENGINE={engine} STATUS={status}")

                if status != "success":
                    logger.warning(
                        "[neurosymbolic-plugin] Symbolic result not successful; "
                        "context will not be injected"
                    )
                    return None

                evidence_text = (
                    integration.integrate_result_with_hermes_response(result)
                )

                if not evidence_text:
                    logger.warning(
                        "[neurosymbolic-plugin] Empty evidence text, returning None"
                    )
                    return None

                logger.warning(
                    "[neurosymbolic-plugin] injecting symbolic context engine=%s",
                    engine,
                )

                _write_proof("CONTEXT_INJECTED")

                return {"context": str(evidence_text)}

            except Exception as exc:
                logger.warning(
                    "[neurosymbolic-plugin] pre_llm_call hook failed: %s",
                    exc,
                    exc_info=True,
                )
                return None

        logger.warning(
            "[neurosymbolic-plugin] Registering pre_llm_call hook..."
        )
        ctx.register_hook("pre_llm_call", pre_llm_call_hook)
        logger.warning(
            "[neurosymbolic-plugin] pre_llm_call hook registered successfully"
        )

        _registered = True
        logger.info(
            "Neurosymbolic integration plugin registered successfully"
        )

    except Exception as exc:
        logger.error(
            "[neurosymbolic-plugin] Failed to register plugin: %s",
            exc,
            exc_info=True,
        )
        raise
