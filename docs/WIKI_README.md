# Wiki / Documentation Guide

## Propósito

Esta guía organiza la documentación del proyecto `ai-ecosystem` y define cómo mantenerla alineada con el estado real del código.

## Estado actual del proyecto

`ai-ecosystem` es un workspace de Hermes Agent + Claude Code con núcleo neurosimbólico.

Componentes vigentes:

```text
Hermes Agent
Claude Code
pre_llm_call hook
ProblemExtractor
SymbolicProblem
Semantic Router
NetworkX
Z3
PyDatalog
CBM / codebase-memory-mcp
Kùzu + LlamaIndex
Policy Engine
```

## Documentos canónicos

| Archivo | Rol |
|---|---|
| `README.md` | Vista general del proyecto |
| `ARCHITECTURE.md` | Arquitectura técnica vigente |
| `SYSTEM_BLUEPRINT.md` | Diagnóstico y mapa del sistema |
| `CLAUDE.md` | Reglas operativas para Claude/Hermes |
| `KNOWLEDGE_BROKER.md` | Capa de broker/conocimiento |
| `docs/README.md` | Índice documental |

## Documentos auxiliares

| Archivo | Rol |
|---|---|
| `docs/CBM_INTEGRATION.md` | Integración CBM resumida |
| `docs/CBM_INTEGRATION_FULL.md` | Guía CBM extendida |
| `docs/integration_summary.md` | Resumen de integración Hermes/CBM/neurosimbólico |

## Regla de actualización

Actualizar documentación cuando cambie cualquiera de estas piezas:

```text
skilled/reasoning/
agents/hermes/plugins/
agents/hermes/config/
src/reasoning/
requirements.txt
package.json
.mcp.json
```

## Cómo evitar documentación desfasada

Antes de afirmar que algo está implementado, verificar:

```text
1. archivo real
2. test real
3. commit reciente
4. configuración activa
5. documentación existente
```

La documentación es la última fuente, no la primera.

## Estados permitidos

Usar siempre uno de estos estados:

```text
Implementado
Implementado básico
Parcial
Configurado
Pendiente
No implementado
```

No usar frases como “completo” si no hay prueba o test que lo respalde.

## Pruebas que deben aparecer en documentación técnica

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
npm run test:hermes-cli
```

Para CBM:

```bash
pnpm run cbm:index
QUERY="reasoning" pnpm run cbm:search
QUERY="engine" pnpm run cbm:graph
```

## Mapa conceptual

```text
LLM / Hermes
  ↓
Interfaz y coordinación
  ↓
ProblemExtractor / Semantic Router
  ↓
Formalización simbólica
  ↓
Motores deterministas
  ↓
Evidencia estructurada
  ↓
Respuesta trazable
```

## Próximo capítulo de documentación recomendado

Crear o ampliar documentación para:

```text
Canonical Logical Knowledge Base
FactStore
RuleStore
EntityIdentityResolver
ContradictionEngine
ReasoningTraceStore
HybridPlanner
```

Estas piezas todavía son el salto pendiente desde “razonamiento por consulta” hacia “conocimiento lógico persistente”.
