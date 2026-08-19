"""Registro lazy de motores adicionales habilitados por capacidades."""

from __future__ import annotations

import logging
from typing import List

from .engine_contracts import EngineRegistry


logger = logging.getLogger(__name__)


def _load_adapter(module_name: str, class_name: str):
    """Carga un adaptador opcional sin romper el núcleo legacy."""
    try:
        module = __import__(
            f"{__package__}.{module_name}",
            fromlist=[class_name],
        )
        return getattr(module, class_name)()
    except (ImportError, AttributeError) as exc:
        logger.warning(
            "Optional reasoning engine unavailable: %s.%s (%s)",
            module_name,
            class_name,
            exc,
        )
        return None


def build_extended_engine_registry() -> EngineRegistry:
    """Construye un registro fresco con los motores disponibles.

    La ausencia de una dependencia opcional no impide importar ni ejecutar la
    ruta legacy. Si una capacidad requerida no tiene adaptador disponible,
    ``MetaReasoner`` la deriva a ``human_review`` mediante fail-closed.
    """
    specs = [
        ("planning_engine", "PlanningEngineAdapter"),
        ("temporal_engine", "TemporalEngineAdapter"),
        ("spatial_engine", "SpatialEngineAdapter"),
        ("probabilistic_engine", "ProbabilisticEngineAdapter"),
        ("causal_engine", "CausalEngineAdapter"),
        ("abductive_engine", "AbductiveEngineAdapter"),
        ("statistical_induction_engine", "StatisticalInductionEngineAdapter"),
    ]
    adapters: List[object] = []
    for module_name, class_name in specs:
        adapter = _load_adapter(module_name, class_name)
        if adapter is not None:
            adapters.append(adapter)
    return EngineRegistry(adapters)
