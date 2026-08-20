# Documentación de ai-ecosystem

Este directorio contiene documentación complementaria. La documentación canónica del estado actual está en:

```text
README.md
ARCHITECTURE.md
SYSTEM_BLUEPRINT.md
CLAUDE.md
KNOWLEDGE_BROKER.md
```

## Estado actual del proyecto

`ai-ecosystem` es un workspace de Hermes Agent + Claude Code con núcleo neurosimbólico.

Componentes principales:

```text
Hermes Agent
Claude Code
Plugin neurosimbólico pre_llm_call
ProblemExtractor / SymbolicProblem
Semantic Router
NetworkX
Z3
PyDatalog
CBM / codebase-memory-mcp
Kùzu + LlamaIndex
Policy Engine
```

## Índice de documentos

| Documento | Propósito |
|---|---|
| `../README.md` | Presentación general actualizada |
| `../ARCHITECTURE.md` | Arquitectura técnica vigente |
| `../SYSTEM_BLUEPRINT.md` | Blueprint y diagnóstico del sistema |
| `../CLAUDE.md` | Instrucciones operativas para Claude/Hermes |
| `../KNOWLEDGE_BROKER.md` | Rol del broker dentro de la capa de conocimiento |
| `CBM_INTEGRATION.md` | Uso e integración de codebase-memory-mcp |
| `CBM_INTEGRATION_FULL.md` | Detalle operativo de CBM |
| `integration_summary.md` | Resumen de verificación CBM/Hermes |
| `WIKI_README.md` | Guía auxiliar de documentación/wiki |

## Criterio de vigencia

Al evaluar documentación, priorizar en este orden:

```text
1. Código actual.
2. Historial reciente de commits.
3. Tests reales.
4. requirements.txt / package.json.
5. Documentación.
```

La documentación anterior a los commits neurosimbólicos puede estar desfasada.

## Validación recomendada

### Núcleo neurosimbólico

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

### Semantic router

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

### Hermes CLI

```bash
npm run test:hermes-cli
```

### CBM

```bash
pnpm run cbm:index
QUERY="reasoning" pnpm run cbm:search
QUERY="engine" pnpm run cbm:graph
```

## Brecha principal pendiente

El proyecto ya tiene motores neurosimbólicos. Falta convertirlos en una memoria lógica persistente:

```text
Base lógica canónica
+ hechos persistentes
+ reglas persistentes
+ identidad de entidades
+ contradicciones
+ trazas históricas
+ planificador híbrido
```
