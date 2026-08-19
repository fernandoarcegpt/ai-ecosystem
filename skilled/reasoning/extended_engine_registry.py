"""Registro de motores adicionales habilitados por capacidades."""

from __future__ import annotations

from .abductive_engine import AbductiveEngineAdapter
from .causal_engine import CausalEngineAdapter
from .engine_contracts import EngineRegistry
from .planning_engine import PlanningEngineAdapter
from .probabilistic_engine import ProbabilisticEngineAdapter
from .spatial_engine import SpatialEngineAdapter
from .statistical_induction_engine import StatisticalInductionEngineAdapter
from .temporal_engine import TemporalEngineAdapter


def build_extended_engine_registry() -> EngineRegistry:
    """Construye un registro fresco con los motores incorporados hasta el Paso 4."""
    return EngineRegistry(
        [
            PlanningEngineAdapter(),
            TemporalEngineAdapter(),
            SpatialEngineAdapter(),
            ProbabilisticEngineAdapter(),
            CausalEngineAdapter(),
            AbductiveEngineAdapter(),
            StatisticalInductionEngineAdapter(),
        ]
    )
