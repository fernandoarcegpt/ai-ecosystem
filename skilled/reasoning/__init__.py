"""Reasonamiento neurosimbólico integrado en el ecosistema Hermes.

Pipeline canónico:
- ProblemExtractor / SymbolicProblem: representación formal y procedencia.
- NeurosymbolicCoordinator: ruta legacy estable para NetworkX, PyDatalog y Z3.
- MetaReasoner / EngineRegistry: selección y composición por capacidades.
- Motores extendidos: planificación clásica, temporal, espacial, probabilístico,
  causal/contrafactual, abductivo e inducción estadística.
- Grounded contracts: publicación de conclusiones con soporte auditable.

Los motores especializados no reinterpretan lenguaje natural. Hermes puede
proponer una formalización estructurada a través de la herramienta oficial,
pero el sistema falla cerrado cuando faltan datos necesarios.
"""

from .engine_contracts import (
    EngineRegistry,
    EngineResult,
    ReasoningCapability,
    ReasoningProfile,
)
from .meta_reasoning import MetaReasoner, profile_for_problem
from .neuro_symbolic_engine import (
    NeurosymbolicCoordinator,
    NeurosymbolicCoordinationResult,
    get_coordinator,
    execute_symbolic_analysis,
    analyze_need_for_reasoning,
    auto_trigger_reasoning_if_needed,
)
from .hermes_integration import (
    HermesSymbolIntegration,
    get_symbolic_integration,
    hermes_auto_detect_and_reason,
    hermes_explicit_symbolic_reasoning,
)

__all__ = [
    "EngineRegistry",
    "EngineResult",
    "ReasoningCapability",
    "ReasoningProfile",
    "MetaReasoner",
    "profile_for_problem",
    "NeurosymbolicCoordinator",
    "NeurosymbolicCoordinationResult",
    "get_coordinator",
    "execute_symbolic_analysis",
    "analyze_need_for_reasoning",
    "auto_trigger_reasoning_if_needed",
    "HermesSymbolIntegration",
    "get_symbolic_integration",
    "hermes_auto_detect_and_reason",
    "hermes_explicit_symbolic_reasoning",
]

__version__ = "1.1.0"
__status__ = "integrated"
