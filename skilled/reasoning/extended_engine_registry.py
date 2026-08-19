"""Registro de motores adicionales habilitados por capacidades."""

from __future__ import annotations

from .engine_contracts import EngineRegistry
from .planning_engine import PlanningEngineAdapter
from .spatial_engine import SpatialEngineAdapter
from .temporal_engine import TemporalEngineAdapter


def build_extended_engine_registry() -> EngineRegistry:
    """Construye un registro fresco con los motores incorporados en el Paso 2."""
    return EngineRegistry(
        [
            PlanningEngineAdapter(),
            TemporalEngineAdapter(),
            SpatialEngineAdapter(),
        ]
    )
