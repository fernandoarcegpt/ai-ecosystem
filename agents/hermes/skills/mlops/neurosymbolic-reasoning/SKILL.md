---
name: neurosymbolic-reasoning
description: Razonamiento neurosimbólico en Hermes con formalización automática, motores reales y evidencia estructurada.
version: 1.3.0
tags: [neurosymbolic, reasoning, hermes, networkx, pydatalog, z3, symbolic-ai, semantic-router, human-review]
---

# Neurosymbolic Reasoning

Skill operativa para usar el núcleo neurosimbólico de `ai-ecosystem` desde Hermes.

## Estado actual

Implementado:

- Formalización mediante `SymbolicProblem`.
- Selección automática de modo/motor.
- NetworkX para grafos.
- Z3 para restricciones.
- PyDatalog para reglas.
- Modo `combined` básico.
- Ruta `human_review` para ambigüedad.
- Integración con Hermes mediante `pre_llm_call`.

Pendiente:

- Base lógica persistente.
- Identidad canónica de entidades.
- Truth maintenance.
- Trazas históricas persistentes.
- Razonamiento basado en casos.

## Archivos principales

```text
skilled/reasoning/neuro_symbolic_engine.py
skilled/reasoning/symbolic_problem_schema.py
skilled/reasoning/semantic_router.py
skilled/reasoning/networkx_wrapper.py
skilled/reasoning/z3_solver_integration.py
skilled/reasoning/pydatalog_integration.py
skilled/reasoning/hermes_integration.py
```

## Motores

| Motor | Uso |
|---|---|
| NetworkX | dependencias, ciclos, DAG, orden topológico |
| Z3 | restricciones, asignación, satisfacibilidad |
| PyDatalog | hechos, reglas, inferencia |
| combined | ejecución básica de varios motores |
| human_review | ambigüedad o información insuficiente |

## Flujo real

```text
usuario
→ Hermes pre_llm_call
→ HermesSymbolIntegration
→ ProblemExtractor
→ SymbolicProblem
→ motor recomendado
→ evidencia estructurada
→ contexto para LLM
```

## Uso programático

```python
from reasoning.hermes_integration import hermes_auto_detect_and_reason

context = hermes_auto_detect_and_reason(
    "Reparte A,B,C entre Ana y Luis. Máximo una tarea por persona.",
    {}
)

if context:
    print(context)
```

## Validación

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
npm run test:hermes-cli
```

## Reglas de uso

- No afirmar que hubo razonamiento simbólico si el resultado fue `None`, `skipped`, `human_review`, `formalization_error` o `error`.
- No contradecir evidencia determinista con una respuesta LLM salvo que se señale error de formalización.
- No tratar `combined` como planificación cognitiva completa; actualmente es ejecución combinada básica.
- No asumir persistencia de hechos/reglas si no existe un store explícito.

## Relación con FGCS

| FGCS | Equivalente actual | Estado |
|---|---|---|
| HELIOS | varios motores cooperando | Parcial |
| PIMOS | Hermes hook/orquestación | Parcial |
| MGTP | Z3/PyDatalog como inferencia parcial | Parcial |
| Kappa/Quixote | futura base lógica persistente | Pendiente |

## Próximo objetivo

Diseñar:

```text
CanonicalLogicalKnowledgeBase
  ├── FactStore
  ├── RuleStore
  ├── EntityIdentityResolver
  ├── ContradictionEngine
  └── ReasoningTraceStore
```
