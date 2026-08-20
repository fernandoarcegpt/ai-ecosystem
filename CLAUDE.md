# Claude / Hermes Operating Guide

## Reglas base

- Haz exactamente lo solicitado: nada más, nada menos.
- Lee un archivo antes de editarlo.
- Prefiere editar documentación existente antes de crear archivos nuevos.
- No guardes archivos temporales en la raíz; usa `/src`, `/tests`, `/docs`, `/config` o `/scripts`.
- Mantén archivos razonablemente pequeños y claros.
- Valida entradas en límites del sistema.
- No agregues `Co-Authored-By` salvo que el proyecto lo configure explícitamente.
- Para operaciones críticas, usar revisión humana o checkpoint antes de ejecutar cambios destructivos.

## Arquitectura actual del proyecto

`ai-ecosystem` integra:

```text
Hermes Agent
Claude Code
Neurosymbolic Integration Plugin
ProblemExtractor / SymbolicProblem
NetworkX
Z3
PyDatalog
CBM / codebase-memory-mcp
Kùzu + LlamaIndex
Policy Engine
```

El flujo principal de razonamiento es:

```text
usuario
→ Hermes / Claude Code
→ pre_llm_call hook
→ ProblemExtractor
→ SymbolicProblem
→ motor simbólico
→ evidencia estructurada
→ respuesta LLM
```

## Componentes neurosimbólicos

Ubicación:

```text
skilled/reasoning/
```

Archivos clave:

```text
neuro_symbolic_engine.py
symbolic_problem_schema.py
semantic_router.py
z3_solver_integration.py
pydatalog_integration.py
networkx_wrapper.py
hermes_integration.py
```

### Motores

| Motor | Uso |
|---|---|
| NetworkX | grafos, dependencias, ciclos, DAG, orden topológico |
| Z3 | restricciones, satisfacibilidad, asignaciones |
| PyDatalog | hechos, reglas, inferencia lógica |
| combined | ejecución combinada básica |
| human_review | ambigüedad, información insuficiente o formalización dudosa |

## Plugin Hermes

Ubicación:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

El plugin registra:

```text
pre_llm_call
```

Regla operativa:

- Si el resultado simbólico es `success`, se inyecta evidencia al LLM.
- Si es `human_review`, `formalization_error` o `error`, no se debe presentar como conclusión determinista.

## Memoria y conocimiento

Capas actuales:

```text
Hermes memory
CBM / codebase-memory-mcp
KùzuDB
LlamaIndex PropertyGraphIndex
Knowledge Broker
Obsidian bridge
```

Estado:

- La memoria estructural existe.
- La base lógica persistente todavía está pendiente.
- No asumir que PyDatalog conserva hechos entre sesiones si no existe persistencia explícita.

## Validación correcta

No confiar únicamente en `npm test` si está definido como placeholder.

### Núcleo neurosimbólico

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

### Semantic router

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

### Hermes plugin CLI

```bash
npm run test:hermes-cli
```

### CBM

```bash
pnpm run cbm:index
QUERY="reasoning" pnpm run cbm:search
QUERY="engine" pnpm run cbm:graph
```

## Comandos CBM

```bash
pnpm run cbm:install
pnpm run cbm:index
QUERY="texto" pnpm run cbm:search
QUERY="nombre" pnpm run cbm:graph
```

## Policy Engine

Ubicación:

```text
src/reasoning/
```

Archivos:

```text
contracts.py
policy_engine.py
policies/safety.yaml
```

Principio:

```text
DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW
```

## Qué no asumir

No asumir que ya existe:

- base lógica persistente completa;
- identidad canónica de entidades;
- truth maintenance general;
- razonamiento basado en casos;
- debate adversarial formal;
- theorem prover general tipo Lean/Coq/Vampire;
- planificación híbrida profunda más allá del modo combinado básico.

## Próximo objetivo arquitectónico

Construir una capa superior:

```text
Canonical Logical Knowledge Base
```

con:

```text
FactStore
RuleStore
DerivedFactStore
ReasoningTraceStore
EntityIdentityResolver
ContradictionEngine
HybridPlanner
```

## Criterio de respuesta técnica

Cuando describas el proyecto:

- Distingue entre implementado, parcial y pendiente.
- Cita archivos concretos si estás justificando una afirmación.
- No presentes documentación antigua como estado actual si contradice `requirements.txt`, commits recientes o pruebas reales.
- Prioriza los motores neurosimbólicos y la integración Hermes como núcleo actual del proyecto.
