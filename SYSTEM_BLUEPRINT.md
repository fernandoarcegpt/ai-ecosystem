# System Blueprint

## Fecha de revisión

Actualizado tras revisión de documentación, estructura de repo e historial público de commits hasta `main`.

## Resumen ejecutivo

`ai-ecosystem` es un workspace de IA híbrida centrado en Hermes Agent, Claude Code, memoria estructural y razonamiento neurosimbólico.

La evolución reciente del repo muestra que el núcleo neurosimbólico dejó de ser una idea documental y pasó a estar implementado como:

```text
Hermes hook
→ extractor simbólico
→ SymbolicProblem
→ selección de motor
→ NetworkX / Z3 / PyDatalog
→ evidencia estructurada
→ contexto para LLM
```

## Hitos recientes del historial

| Commit | Impacto |
|---|---|
| `Centralize Hermes custom configuration in ai-ecosystem` | Centraliza configuración Hermes, plugin neurosimbólico y skills dentro del repo. |
| `Fix PyDatalog variable binding order` | Corrige orden de bindings en PyDatalog conservando orden de variables. |
| `Harden neurosymbolic routing, ambiguity handling and combined mode` | Mejora extracción simbólica, mezcla de modos, manejo de ambigüedad y modo combinado. |

## Componentes verificados por estructura

### 1. Hermes custom configuration

Ubicación:

```text
agents/hermes/config/config.yaml
agents/hermes/plugins/neurosymbolic-integration/
agents/hermes/skills/
```

Función:

- Configurar Hermes para el ecosistema.
- Activar plugin neurosimbólico.
- Mantener skills del proyecto.

### 2. Plugin neurosimbólico

Ubicación:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

Archivos:

```text
__init__.py
hermes_integration.py
plugin.yaml
```

Función:

- Registrar hook `pre_llm_call`.
- Ejecutar razonamiento simbólico antes del LLM.
- Inyectar evidencia solo cuando el motor devuelve éxito.

### 3. Núcleo neurosimbólico

Ubicación:

```text
skilled/reasoning/
```

Archivos principales:

```text
neuro_symbolic_engine.py
symbolic_problem_schema.py
semantic_router.py
networkx_wrapper.py
z3_solver_integration.py
pydatalog_integration.py
hermes_integration.py
```

Capacidades:

- Formalización de consultas.
- Selección automática de motor.
- Ejecución de motores reales.
- Manejo de `formalization_error`.
- `human_review` para ambigüedad.
- Aislamiento de estado por ejecución.

### 4. Motores simbólicos

| Motor | Archivo | Uso |
|---|---|---|
| NetworkX | `networkx_wrapper.py` | Grafos, ciclos, DAG, orden topológico |
| Z3 | `z3_solver_integration.py` | Restricciones, satisfacibilidad, asignaciones |
| PyDatalog | `pydatalog_integration.py` | Hechos, reglas, consultas lógicas |

### 5. Policy Engine

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

Estado:

- Contratos tipados para tareas, evidencias, decisiones y revisión humana.
- Motor de políticas YAML básico.
- Precedencia determinista: `DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW`.

### 6. Knowledge layer

Capas existentes:

```text
KùzuDB
LlamaIndex PropertyGraphIndex
codebase-memory-mcp
Knowledge Broker
Obsidian bridge
Hermes memory
```

Estado:

- Ya existe memoria estructural y grafo documental/código.
- Todavía no existe una base lógica canónica persistente con hechos, reglas, versiones, contradicciones e identidad de objetos.

## Dependencias actuales relevantes

`requirements.txt` actual contiene:

```text
python-dotenv==1.2.2
llama-index==0.14.23
llama-index-llms-openai==0.7.10
llama-index-embeddings-openai==0.6.0
llama-index-graph-stores-kuzu==0.9.1
kuzu==0.11.3
```

Además, para el núcleo neurosimbólico se requieren en el entorno correspondiente:

```text
networkx
z3-solver
pyDatalog
pytest
```

## Validación técnica recomendada

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

## Estado real del sistema

| Capacidad | Estado |
|---|---|
| Hermes como orquestador | Implementado |
| Plugin `pre_llm_call` | Implementado |
| Extracción a `SymbolicProblem` | Implementado |
| Razonamiento por restricciones | Implementado con Z3 |
| Razonamiento por reglas | Implementado con PyDatalog |
| Razonamiento por grafos | Implementado con NetworkX |
| Combined mode | Implementado básico |
| Human review por ambigüedad | Implementado básico |
| Memoria estructural del código | Implementada con CBM |
| Grafo documental | Implementado parcial con Kùzu/LlamaIndex |
| Base lógica persistente | Pendiente |
| Identidad de objetos | Pendiente |
| Truth maintenance | Pendiente |
| Razonamiento basado en casos | Pendiente |
| Debate adversarial formal | Pendiente |

## Brechas principales

### 1. Base lógica persistente

Falta una capa canónica:

```text
facts
rules
derived_facts
sources
versions
contradictions
reasoning_traces
```

### 2. Identidad de entidades

Falta resolver equivalencias:

```text
Fernando
fernandoarcegpt
autor del plugin
usuario del repo
```

### 3. Contradicciones / truth maintenance

Falta comparar hechos entre memoria, documentos, grafo y razonamiento:

```text
Hecho A contradice Hecho B
A tiene fuente X
B tiene fuente Y
A es más reciente
B queda obsoleto o requiere revisión
```

### 4. Trazas persistentes

Falta guardar por cada ejecución:

```text
pregunta
formalización
motor elegido
hechos usados
reglas aplicadas
restricciones aplicadas
resultado
validación
explicación
```

### 5. Planificación híbrida secuencial

El modo combinado existe, pero la siguiente etapa es un planificador que ordene motores según dependencia lógica:

```text
grafo → restricciones → reglas → persistencia → explicación
```

## Relación con FGCS/ICOT

| Concepto FGCS | Equivalente actual | Estado |
|---|---|---|
| PIMOS | Hermes hooks/orquestación | Parcial |
| HELIOS | Múltiples solucionadores | Parcial |
| MGTP | Z3/PyDatalog como inferencia parcial | Parcial |
| Kappa | Kùzu/CBM/Knowledge Broker | Parcial |
| Quixote | SymbolicProblem + entidades/reglas | Muy parcial |
| HELIC-II | Casos + reglas + debate | No implementado |
| Mandala | Sin equivalente claro | No implementado |

## Conclusión

El proyecto ya superó la etapa de “integrar motores”. La prioridad arquitectónica ahora es convertir los resultados simbólicos en conocimiento persistente y acumulativo.

Próximo objetivo técnico recomendado:

```text
Canonical Logical Knowledge Base
```

con:

```text
FactStore
RuleStore
EntityIdentityResolver
ContradictionEngine
ReasoningTraceStore
HybridPlanner
```
