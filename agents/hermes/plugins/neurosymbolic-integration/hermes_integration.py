"""Integration layer between Hermes and the Neuro-Symbolic Reasoning Engine.

This module provides the bridge between Hermes' plugin system and the
validated neurosymbolic core. It contains the functions that Hermes plugins
will call to detect and execute symbolic reasoning.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Add the ecosystem to the path for imports
_EcosystemPath = "/home/fernando/ai-ecosystem/skilled"
if _EcosystemPath not in sys.path:
    sys.path.insert(0, _EcosystemPath)

# Track availability
_NEUROSYMBOLIC_AVAILABLE = False
_NURSOR_ERROR = None


def _ensure_neurosymbolic_imports():
    """Ensure neurosymbolic module is importable."""
    global _NEUROSYMBOLIC_AVAILABLE, _NURSOR_ERROR
    if _NEUROSYMBOLIC_AVAILABLE:
        return True

    try:
        # Test import
        from reasoning.neuro_symbolic_engine import (
            NeurosymbolicCoordinator,
        )
        _NEUROSYMBOLIC_AVAILABLE = True
        return True
    except ImportError as e:
        _NURSOR_ERROR = str(e)
        logger.warning(f"Neurosymbolic module not available: {e}")
        return False
    except Exception as e:
        _NURSOR_ERROR = str(e)
        logger.warning(f"Neurosymbolic module error: {e}")
        return False


def get_symbolic_integration():
    """Get the singleton symbolic integration instance."""
    from reasoning.hermes_integration import get_symbolic_integration as _get
    return _get()


def hermes_auto_detect_and_reason(
    task_description: str,
    context: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """Auto-detect and execute symbolic reasoning for a task description.

    This function:
    1. Analyzes the task description and context
    2. Determines if symbolic reasoning is needed
    3. Executes the reasoning engine if needed
    4. Returns formatted evidence text for the LLM

    Args:
        task_description: The user query or task description
        context: Additional context (entities, relations, constraints, etc.)

    Returns:
        Formatted evidence text to inject into the LLM context, or None
    """
    if not _ensure_neurosymbolic_imports():
        return None

    try:
        integration = get_symbolic_integration()
        temporal_context = integration.provide_temporal_context(context or {})

        result = integration.intercept_task(task_description, temporal_context)

        if result:
            return integration.integrate_result_with_hermes_response(result)

        return None
    except Exception as e:
        logger.warning(f"Auto-detect and reason failed: {e}")
        return None


def hermes_explicit_symbolic_reasoning(
    task_description: str,
    context: Dict[str, Any],
    engine_preference: Optional[str] = "auto"
) -> Dict[str, Any]:
    """Explicitly execute symbolic reasoning.

    Args:
        task_description: The user query or task description
        context: Structured context with entities, relations, constraints, etc.
        engine_preference: Preferred engine ("auto", "networkx", "z3", "pydatalog", "combined")

    Returns:
        Full result dictionary from the reasoning engine
    """
    if not _ensure_neurosymbolic_imports():
        return {
            "status": "symbolic_engine_unavailable",
            "error": _NURSOR_ERROR or "Unknown import error"
        }

    try:
        integration = get_symbolic_integration()
        temporal_context = integration.provide_temporal_context(context)

        return integration.intercept_task(task_description, temporal_context)
    except Exception as e:
        logger.error(f"Explicit symbolic reasoning failed: {e}")
        return {
            "status": "error",
            "error": str(e)
        }