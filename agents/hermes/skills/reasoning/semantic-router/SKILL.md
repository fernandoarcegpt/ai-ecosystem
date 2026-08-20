---
name: semantic-router
description: Clasificación automática de solicitudes hacia modos de razonamiento LLM, reglas, restricciones, grafos, híbrido o revisión humana.
version: 1.1.0
author: Hermes Agent
tags: [neurosymbolic, reasoning, routing, automation, symbolic-ai, human-review]
---

# Semantic Router

El Semantic Router clasifica solicitudes de usuario para decidir si deben ir al LLM normal o a un motor simbólico.

## Modos actuales

| Modo | Motor recomendado | Uso |
|---|---|---|
| `llm_only` | `none` | resumen, traducción, redacción, conversación |
| `rules` | `pydatalog` o política externa | reglas, permisos, inferencias |
| `constraints` | `z3` | restricciones, asignaciones, límites |
| `graph` | `networkx` | dependencias, ciclos, rutas, orden topológico |
| `hybrid` | `combined` | mezcla de grafos, reglas y restricciones |
| `human_review` | `none` | ambigüedad o datos críticos faltantes |

## Relación con `ProblemExtractor`

El router clasifica la intención estructural. La formalización real ocurre en:

```text
skilled/reasoning/symbolic_problem_schema.py
```

El resultado formalizado se representa como:

```text
SymbolicProblem
```

## Principio clave

`confidence` significa confianza en la clasificación, no confianza en que el problema pueda resolverse automáticamente.

Ejemplo:

```text
mode = human_review
confidence = 0.8
```

significa:

```text
El sistema está bastante seguro de que esto requiere revisión humana.
```

No significa que pueda resolverlo con 80% de certeza.

## Ambigüedad

Debe usarse `human_review` cuando:

- faltan datos críticos;
- hay ambigüedad semántica;
- una relación puede significar varias cosas;
- la formalización no debería inyectarse como evidencia determinista.

Ejemplo:

```text
"A depende de B"
```

puede ser dependencia técnica, laboral, económica, emocional o documental. Si no hay contexto de grafo/dependencias, debe tratarse con cuidado.

## Falsos positivos a evitar

No activar `human_review` solo por frases negativas como:

```text
No hay restricciones de presupuesto.
No faltan datos.
No hay dependencias.
```

Esas frases pueden ser información válida, no incertidumbre.

## Uso programático

```python
from reasoning.semantic_router import classify_task_structure

result = classify_task_structure(
    "Organiza estas tareas respetando dependencias y detecta ciclos."
)

print(result["mode"])
print(result["recommended_engine"])
```

## Validación

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

## Relación con motores

El router no debe ejecutar motores directamente. Su función es recomendar.

La ejecución ocurre en:

```text
skilled/reasoning/neuro_symbolic_engine.py
```

## Estado actual

Implementado:

- Clasificación por patrones y estructura.
- Modos `llm_only`, `rules`, `constraints`, `graph`, `hybrid`, `human_review`.
- Priorización de incertidumbre explícita.
- Diferenciación entre incertidumbre y negación.

Pendiente:

- Aprendizaje de patrones.
- Registro persistente de decisiones de routing.
- Métricas históricas de aciertos/falsos positivos.
- Integración más profunda con una base lógica persistente.
