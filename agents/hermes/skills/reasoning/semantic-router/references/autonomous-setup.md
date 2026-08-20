# Autonomous Setup

## Objetivo

Permitir que Hermes use razonamiento neurosimbólico automáticamente cuando exista estructura formalizable en la consulta.

## Activación principal

La activación recomendada ocurre mediante:

```text
pre_llm_call
```

en:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

## Flujo

```text
mensaje del usuario
→ hook pre_llm_call
→ integración simbólica
→ ProblemExtractor
→ SymbolicProblem
→ motor recomendado
→ evidencia
→ contexto para LLM
```

## Condición de inyección

Solo inyectar contexto si:

```text
status == success
```

No inyectar si:

```text
human_review
formalization_error
error
skipped
```

## Motores automáticos

```text
NetworkX  → graph
Z3        → constraints
PyDatalog → logic
combined  → hybrid
none      → llm_only / human_review
```

## Validación

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
npm run test:hermes-cli
```

## Límite actual

La autonomía actual es por consulta. Todavía falta memoria lógica persistente para que el sistema aprenda hechos/reglas de forma acumulativa.

Próxima capa recomendada:

```text
CanonicalLogicalKnowledgeBase
```
