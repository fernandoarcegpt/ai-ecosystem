# Semantic Router Integration Guide

## Flujo recomendado

```text
Usuario
  ↓
Hermes / Claude Code
  ↓
pre_llm_call hook
  ↓
Semantic Router / ProblemExtractor
  ↓
SymbolicProblem
  ↓
NetworkX / Z3 / PyDatalog / combined
  ↓
Evidencia estructurada
  ↓
LLM
```

## Importación

```python
from reasoning.semantic_router import classify_task_structure
from reasoning.hermes_integration import hermes_auto_detect_and_reason
```

## Clasificación simple

```python
classification = classify_task_structure(
    "Organiza tareas respetando dependencias y detecta ciclos."
)

print(classification["mode"])
print(classification["recommended_engine"])
```

## Integración con Hermes

La ruta preferida es el plugin:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

Ese plugin registra `pre_llm_call` y evita que cada skill tenga que llamar manualmente al router.

## Uso directo

```python
result = hermes_auto_detect_and_reason(
    "Reparte A,B,C entre Ana,Luis. Máximo una tarea por persona.",
    {}
)

if result:
    print(result)
```

## Estados

| Estado | Qué hacer |
|---|---|
| `success` | usar evidencia como contexto determinista |
| `skipped` | dejar que el LLM responda normalmente |
| `human_review` | no presentar conclusión determinista |
| `formalization_error` | pedir aclaración o datos estructurados |
| `error` | no inyectar evidencia |

## Validación

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
npm run test:hermes-cli
```

## Buenas prácticas

- No usar solo keywords para decidir ejecución.
- Permitir que `ProblemExtractor` formalice antes de decidir.
- No inyectar evidencia si el resultado no es `success`.
- Usar `human_review` para ambigüedad.
- Verificar post-condiciones de Z3.
- No asumir persistencia de hechos PyDatalog.

## Pendiente

- Registrar métricas históricas de clasificación.
- Guardar trazas de routing.
- Aprender falsos positivos/negativos.
- Integrar con una base lógica persistente.
