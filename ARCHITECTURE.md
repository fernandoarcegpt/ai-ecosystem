# Architecture

## Estado vigente

`ai-ecosystem` es un workspace de **Hermes Agent + Claude Code** con integración neurosimbólica. El proyecto combina:

- Orquestación con Hermes Agent.
- Configuración y flujo de trabajo con Claude Code.
- Razonamiento simbólico con NetworkX, Z3 y PyDatalog.
- Enrutamiento semántico y formalización mediante `SymbolicProblem`.
- Memoria estructural de código con `codebase-memory-mcp`.
- Grafo documental con Kùzu + LlamaIndex.
- Políticas deterministas y revisión humana.

El foco arquitectónico actual es pasar de un LLM con herramientas a un sistema híbrido donde el LLM coordina, pero los motores externos verifican.

## Vista de alto nivel

```text
Usuario
  │
  ▼
Hermes Agent / Claude Code
  │
  ▼
Hooks / pre_llm_call
  │
  ▼
HermesSymbolIntegration
  │
  ▼
ProblemExtractor
  │
  ▼
SymbolicProblem
  │
  ├── graph       → NetworkX
  ├── constraints → Z3
  ├── logic       → PyDatalog
  └── combined    → NetworkX + Z3 + PyDatalog
  │
  ▼
Evidencia estructurada
  │
  ▼
Respuesta del LLM con contexto determinista
```

## Directorios principales

```text
.
├── agents/hermes/
│   ├── config/
│   ├── plugins/neurosymbolic-integration/
│   └── skills/
├── skilled/reasoning/
│   ├── neuro_symbolic_engine.py
│   ├── symbolic_problem_schema.py
│   ├── semantic_router.py
│   ├── z3_solver_integration.py
│   ├── pydatalog_integration.py
│   ├── networkx_wrapper.py
│   └── hermes_integration.py
├── src/
│   ├── ingest.py
│   ├── query.py
│   └── reasoning/
│       ├── contracts.py
│       ├── policy_engine.py
│       └── policies/
├── docs/
├── tests/
├── .claude/
├── .openspec/
├── README.md
├── CLAUDE.md
├── SYSTEM_BLUEPRINT.md
├── KNOWLEDGE_BROKER.md
├── package.json
└── requirements.txt
```

## Núcleo neurosimbólico

### `skilled/reasoning/symbolic_problem_schema.py`

Define el modelo intermedio `SymbolicProblem` y el extractor central.

Responsabilidades:

- Extraer entidades, relaciones, restricciones, hechos y reglas.
- Fusionar estructuras simbólicas explícitas.
- Inferir modo de razonamiento.
- Evitar entidades inventadas.
- Marcar ambigüedad mediante `human_review`.

Modos relevantes:

```text
NONE
GRAPHS
CONSTRAINTS
LOGIC
COMBINED
```

### `skilled/reasoning/neuro_symbolic_engine.py`

Coordinador principal.

Responsabilidades:

- Crear instancias frescas de cada motor para evitar estado compartido.
- Elegir motor automáticamente según `SymbolicProblem`.
- Ejecutar NetworkX, Z3, PyDatalog o modo combinado.
- Validar formalización y resultados.
- Preparar evidencia estructurada.

### `skilled/reasoning/networkx_wrapper.py`

Razonamiento sobre grafos.

Capacidades actuales:

- Grafo dirigido por ejecución.
- Inserción de nodos y relaciones.
- Detección de ciclos.
- Verificación DAG.
- Orden topológico.

### `skilled/reasoning/z3_solver_integration.py`

Resolución de restricciones.

Capacidades actuales:

- Variables enteras y booleanas.
- Restricciones simples: `>`, `<`, `=`, suma, igualdad.
- Resultado `satisfiable`, `unsatisfiable`, `unknown`, `error`.
- Aislamiento de solver por instancia.

### `skilled/reasoning/pydatalog_integration.py`

Razonamiento basado en reglas.

Capacidades actuales:

- Hechos en PyDatalog.
- Reglas con cabeza/cuerpo.
- Consultas con bindings.
- Corrección de orden de variables con `dict.fromkeys(...)`.
- Limpieza de estado global por instancia.

### `skilled/reasoning/semantic_router.py`

Clasificador de tareas.

Modos:

```text
llm_only
rules
constraints
graph
hybrid
human_review
```

Motores recomendados:

```text
none
networkx
z3
pydatalog
combined
```

## Integración con Hermes

### Plugin

Ubicación:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

Archivos:

```text
plugin.yaml
__init__.py
hermes_integration.py
```

`plugin.yaml` declara:

```yaml
provides_hooks:
  - pre_llm_call
```

El hook:

1. Recibe el mensaje del usuario.
2. Llama a la integración simbólica.
3. Ejecuta razonamiento si hay estructura formalizable.
4. Inyecta contexto solo si el resultado es `success`.
5. No inyecta evidencia determinista en caso de `human_review` o error.

## Memoria estructural y conocimiento

### CBM / codebase-memory-mcp

Uso:

```bash
pnpm run cbm:install
pnpm run cbm:index
QUERY="pattern" pnpm run cbm:search
QUERY="name" pnpm run cbm:graph
```

Rol:

- Índice estructural del código.
- Búsqueda semántica o por patrones.
- Grafo de dependencias/código.

### Kùzu + LlamaIndex

Dependencias actuales:

```text
llama-index==0.14.23
llama-index-graph-stores-kuzu==0.9.1
kuzu==0.11.3
```

Rol:

- Grafo documental.
- Ingesta y consulta semántica.
- Base para una futura capa tipo Kappa/Quixote.

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

Responsabilidades:

- Modelar tareas, actores, evidencias, decisiones y revisión humana.
- Cargar políticas YAML.
- Aplicar precedencia determinista:

```text
DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW
```

Estado: funcional como motor de políticas básico, pero todavía no está plenamente fusionado con PyDatalog/Z3 para políticas complejas.

## Pruebas y verificación

### Pruebas neurosimbólicas

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

Cubren:

- Inferencia PyDatalog real.
- Z3 satisfiable.
- Z3 unsatisfiable.
- Ciclos NetworkX.
- DAG y orden topológico.
- Asignación con dominio cerrado.
- Aislamiento entre tareas.
- Rechazo de entidades inventadas.
- Rechazo de restricciones no formalizables.
- Combined mode con outputs reales.

### Semantic router

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

### Hermes CLI / plugin

```bash
npm run test:hermes-cli
```

### Nota sobre `npm test`

El script raíz `npm test` puede estar definido como placeholder. Para validar el sistema real se deben usar los comandos explícitos de `pytest` y verificación de Hermes.

## Estado frente al FGCS japonés

| FGCS/ICOT | ai-ecosystem | Estado |
|---|---|---|
| PIMOS | Hermes Agent + hooks | Parcial |
| HELIOS | Modo combinado con varios motores | Parcial |
| MGTP | Z3/PyDatalog como motores parciales | Parcial |
| Kappa | Kùzu/CBM/Knowledge Broker | Parcial |
| Quixote | SymbolicProblem + entidades + reglas | Muy parcial |
| HELIC-II | Casos + reglas + debate | Pendiente |
| KL1/KL2 | Python + Hermes, no lenguaje lógico concurrente | No implementado |

## Brechas arquitectónicas

El sistema ya tiene motores. Lo pendiente es la capa de conocimiento persistente:

1. Base lógica canónica.
2. Persistencia de hechos y reglas.
3. Identidad de entidades/objetos.
4. Motor de contradicciones/truth maintenance.
5. Trazas históricas de razonamiento.
6. Planificación híbrida secuencial, no solo ejecución combinada.
7. Razonamiento basado en casos.
8. Debate adversarial entre agentes.
9. Theorem prover general opcional.

## Principio rector

El LLM no debe ser la única fuente de verdad. Debe actuar como interfaz y coordinador, mientras que los motores simbólicos y la memoria estructural validan lo que pueda validarse determinísticamente.
