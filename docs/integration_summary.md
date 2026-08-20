# Integration Summary

## Resumen

La integración actual de `ai-ecosystem` combina dos líneas:

1. **Memoria estructural de código** con CBM / `codebase-memory-mcp`.
2. **Razonamiento neurosimbólico** con Hermes hook + NetworkX + Z3 + PyDatalog.

Ambas son complementarias.

```text
CBM responde: ¿dónde está y cómo se relaciona el código?
Neurosymbolic engine responde: ¿qué se puede verificar lógicamente?
```

## Integración Hermes

El plugin neurosimbólico declara `pre_llm_call`.

Flujo:

```text
mensaje usuario
→ Hermes pre_llm_call
→ HermesSymbolIntegration
→ ProblemExtractor
→ SymbolicProblem
→ motor simbólico
→ evidencia
→ contexto LLM
```

## Integración CBM

Scripts disponibles:

```bash
pnpm run cbm:install
pnpm run cbm:index
QUERY="texto" pnpm run cbm:search
QUERY="nombre" pnpm run cbm:graph
```

CBM se usa para:

- indexar el repo;
- buscar código;
- navegar relaciones;
- entregar contexto estructural a Claude/Hermes.

## Integración neurosimbólica

Motores actuales:

| Motor | Uso |
|---|---|
| NetworkX | relaciones, dependencias, ciclos, orden topológico |
| Z3 | restricciones, asignaciones, satisfacibilidad |
| PyDatalog | hechos, reglas, inferencias |
| combined | ejecución básica de varios motores |
| human_review | ambigüedad o formalización incierta |

## Verificaciones recomendadas

### Núcleo neurosimbólico

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

### Semantic router

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

### Hermes plugin

```bash
npm run test:hermes-cli
```

### CBM

```bash
pnpm run cbm:index
QUERY="reasoning" pnpm run cbm:search
QUERY="engine" pnpm run cbm:graph
```

## Estado actual

| Integración | Estado |
|---|---|
| Hermes hook `pre_llm_call` | Implementado |
| Plugin neurosimbólico | Implementado |
| NetworkX | Implementado |
| Z3 | Implementado |
| PyDatalog | Implementado |
| Semantic Router | Implementado |
| Combined mode | Implementado básico |
| Human review | Implementado básico |
| CBM | Configurado |
| Kùzu/LlamaIndex | Configurado para grafo/conocimiento |
| Base lógica persistente | Pendiente |
| Contradicciones persistentes | Pendiente |
| Identidad de entidades | Pendiente |

## Limitación importante

No usar esta integración como prueba de que ya existe una memoria lógica completa.

Lo que existe:

```text
contexto estructural + razonamiento por consulta
```

Lo que falta:

```text
conocimiento lógico persistente y acumulativo
```

## Próxima integración recomendada

```text
CBM / Kùzu / Knowledge Broker
  ↓
Canonical Logical Knowledge Base
  ↓
FactStore + RuleStore + EntityIdentity + ContradictionEngine
  ↓
Neurosymbolic Engine
  ↓
ReasoningTraceStore
```
