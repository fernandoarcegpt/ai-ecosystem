"""Registro de motores adicionales habilitados por capacidades."""

from __future__ import annotations

from .causal_engine import CausalEngineAdapter
from .engine_contracts import EngineRegistry
from .planning_engine import PlanningEngineAdapter
from .probabilistic_engine import ProbabilisticEngineAdapter
from .spatial_engine import SpatialEngineAdapter
from .temporal_engine import TemporalEngineAdapter


def build_extended_engine_registry() -> EngineRegistry:
    """Construye un registro fresco con los motores incorporados hasta el Paso 3."""
    return EngineRegistry(
        [
            PlanningEngineAdapter(),
            TemporalEngineAdapter(),
            SpatialEngineAdapter(),
            ProbabilisticEngineAdapter(),
            CausalEngineAdapter(),
        ]
    )
