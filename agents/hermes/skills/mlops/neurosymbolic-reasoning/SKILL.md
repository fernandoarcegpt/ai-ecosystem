---
name: neurosymbolic-reasoning
description: Integración de razonamiento neurosimbólico en Hermes con auto‑activación basada en detección automática de patrones.
version: 1.2.0
tags: [neurosymbolic, reasoning, hermes, networkx, pydatalog, z3, symbolic-ai, auto-detection, semantic-router]
---

# Razonamiento Neurosimbólico en Hermes

Sistema de razonamiento simbólico integrado en Hermes que se activa automáticamente mediante detección de patrones.

## Motores y casos de uso
| Motor | Uso |
|-------|-----|
| NetworkX | Análisis de grafos (dependencias, ciclos). |
| PyDatalog | Inferencia lógica (reglas, hechos). |
| Z3 | Restricciones y planificación. |

## Flujo de trabajo
```python
# Detección automática sin marcadores
from skilled.reasoning.hermes_integration import hermes_auto_detect_and_trigger
evidence = hermes_auto_detect_and_trigger(
    "Planificar despliegue con dependencias",
    {"constraints": ["A antes que B"], "relations": [("A","B")]}
)
if evidence:
    # Integrar evidencia en la respuesta de Hermes
    context["symbolic_evidence"] = evidence
```

## Patrones detectados
- **Dependencias**: `dependencias`, `dependencia`, `before`, `after`.
- **Restricciones**: `constraint`, `restricción`, `limit`, `limitación`.
- **Secuencias**: `sequence`, `orden`, `step`.
- **Reglas**: `rule`, `regla`, `if-then`.

## Integración con Hermes
- **Hooks**: `on_task_received` llama a `hermes_auto_detect_and_trigger`.
- **Interceptores**: Añadir `context["symbolic_evidence"]` si se detecta.
- **Respuesta**: `integrate_result_with_hermes_response(evidence)`.

## Pitfalls
- No asumir que la detección siempre genera evidencia; verificar que `evidence` no sea None.
- Mantener el contexto actualizado; patrones basados en datos obsoletos pueden generar falsos positivos.
- No confiar en la solución sin revisar, especialmente con Z3; validar resultados críticos.
+ Asegurarse de que el número de pruebas sea exacto y que las soluciones Z3 cumplan con las restricciones de asignación (máximo dos tareas por persona, sin conflictos entre A y B). Validar que las salidas de Z3 satisfacen todas las restricciones independientemente del motor.

## Referencias rápidas
- `references/architecture.md` – Arquitectura completa.
- `references/engine-comparison.md` – Comparativa de motores.
- `references/integration-patterns.md` – Patrones de integración.

> **Nota de estilo**: Documentación concisa y directa; evite frases extensas.