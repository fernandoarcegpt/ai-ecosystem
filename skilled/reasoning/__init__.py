"""
Reasonamiento neurosimbólico integrado en el ecosistema Hermes.

Este paquete proporciona capacidad general de razonamiento simbólico como parte transversal del ecosistema Hermes.

Componentes principales:
- NetworkX: Análisis de grafos, relaciones, dependencias, caminos, ciclos, conectividad
- PyDatalog: Hechos, reglas, consultas e inferencia lógica
- Z3 Solver: Restricciones, satisfacibilidad, incompatibilidades, planificación

Uso rápido:
    from skilled.reasoning.hermes_integration import hermes_auto_detect_and_reason

    # Detección automática y ejecución
    evidence = hermes_auto_detect_and_reason(
        "Planificar despliegue con restricciones", 
        {"dependencies": ["build", "deploy"], "constraints": ["build antes que deploy"]}
    )
    
    # Uso explícito
    from skilled.reasoning.hermes_integration import hermes_explicit_symbolic_reasoning
    
    result = hermes_explicit_symbolic_reasoning(
        "Validar reglas de negocio",
        {"facts": [("admin", "user1")], "rules": [{"name": "rule1", "head": "valid", "body": "admin"}]},
        engine_preference="combined"
    )
"""

from .neuro_symbolic_engine import (
    NeurosymbolicCoordinator,
    NeurosymbolicCoordinationResult,
    get_coordinator,
    execute_symbolic_analysis,
    analyze_need_for_reasoning,
    auto_trigger_reasoning_if_needed
)
from .hermes_integration import (
    HermesSymbolIntegration,
    get_symbolic_integration,
    hermes_auto_detect_and_reason,
    hermes_explicit_symbolic_reasoning
)

__all__ = [
    "NeurosymbolicCoordinator",
    "NeurosymbolicCoordinationResult",
    "get_coordinator",
    "execute_symbolic_analysis",
    "analyze_need_for_reasoning",
    "auto_trigger_reasoning_if_needed",
    "integrate_result_with_hermes_response",
    "HermesSymbolIntegration",
    "get_symbolic_integration",
    "hermes_auto_detect_and_reason",
    "hermes_explicit_symbolic_reasoning"
]

__version__ = "1.0.0"
__status__ = "production-ready"