# ai-ecosystem

Workspace experimental de **Hermes Agent + Claude Code** orientado a agentes, memoria estructural y razonamiento neurosimbólico.

El estado actual del proyecto ya no es solo una colección de scripts: incluye un núcleo funcional que puede detectar problemas simbólicos, formalizarlos y enrutar la consulta hacia motores reales de razonamiento antes de que responda el LLM.

## Estado actual

| Área | Estado |
|---|---|
| Hermes Agent | Integrado como runtime/orquestador principal |
| Claude Code | Configuración y hooks de apoyo para trabajo sobre el repo |
| Plugin neurosimbólico Hermes | Implementado mediante `pre_llm_call` |
| Z3 | Implementado para restricciones y satisfacibilidad |
| PyDatalog | Implementado para reglas e inferencia lógica |
| NetworkX | Implementado para grafos, ciclos y orden topológico |
| Semantic Router / ProblemExtractor | Implementado para seleccionar modo/motor |
| Combined mode | Implementado de forma básica para combinar motores |
| Human review | Implementado para ambigüedad o falta de certeza simbólica |
| CBM / codebase-memory-mcp | Integrado como memoria estructural del código |
| Kùzu + LlamaIndex | Integrado como grafo/document knowledge layer |
| Base lógica persistente tipo Quixote/Kappa | Pendiente |
| Identidad persistente de objetos | Pendiente |
| Truth maintenance / contradicciones persistentes | Pendiente |
| Trazas históricas de razonamiento | Pendiente |

## Arquitectura resumida

```text
Usuario
  ↓
Hermes Agent / Claude Code
  ↓
pre_llm_call hook
  ↓
ProblemExtractor / Semantic Router
  ↓
SymbolicProblem
  ↓
┌──────────────┬──────────────┬──────────────┐
│ NetworkX     │ Z3           │ PyDatalog    │
│ grafos       │ restricciones│ reglas       │
└──────────────┴──────────────┴──────────────┘
  ↓
Evidencia estructurada
  ↓
LLM responde con contexto simbólico
```

## Componentes principales

### 1. Núcleo neurosimbólico

Ubicación principal:

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

Funciones principales:

- Formalizar consultas en `SymbolicProblem`.
- Elegir modo: `constraints`, `graphs`, `logic`, `combined` o `none`.
- Ejecutar motores reales.
- Rechazar formalizaciones ambiguas o no verificables.
- Generar evidencia estructurada para Hermes/LLM.

### 2. Plugin Hermes

Ubicación:

```text
agents/hermes/plugins/neurosymbolic-integration/
```

Función:

- Registra un hook `pre_llm_call`.
- Intercepta consultas del usuario.
- Ejecuta razonamiento simbólico cuando corresponde.
- Inyecta evidencia antes de la llamada al LLM.

### 3. Memoria y grafo de conocimiento

Capas disponibles:

```text
CBM / codebase-memory-mcp
KùzuDB
LlamaIndex PropertyGraphIndex
Knowledge Broker
Obsidian bridge
Hermes memory
```

Estado: hay varias piezas de memoria estructural, pero todavía falta una **base lógica canónica** que unifique hechos, reglas, fuentes, versiones, contradicciones e identidad de entidades.

### 4. Política y control humano

Ubicación:

```text
src/reasoning/
```

Incluye:

```text
contracts.py
policy_engine.py
policies/safety.yaml
```

Función:

- Definir contratos para tareas, decisiones, evidencias, revisión humana y auditoría.
- Evaluar políticas YAML con precedencia: `DENY > REQUIRE_HUMAN > UNKNOWN > ALLOW`.

## Instalación básica

```bash
cd ~/ai-ecosystem
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Dependencias principales actuales:

```text
python-dotenv==1.2.2
llama-index==0.14.23
llama-index-llms-openai==0.7.10
llama-index-embeddings-openai==0.6.0
llama-index-graph-stores-kuzu==0.9.1
kuzu==0.11.3
```

Además, el entorno Hermes debe tener disponibles los paquetes de razonamiento:

```text
networkx
z3-solver
pyDatalog
```

## Comandos útiles

### Pruebas neurosimbólicas reales

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

### Pruebas del semantic router

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
```

### Verificar plugin Hermes neurosimbólico

```bash
npm run test:hermes-cli
```

### CBM

```bash
pnpm run cbm:install
pnpm run cbm:index
QUERY="neuro_symbolic" pnpm run cbm:search
QUERY="reasoning" pnpm run cbm:graph
```

Nota: el script raíz `npm test` puede no representar toda la suite real. Para validación técnica, usar los comandos explícitos de `pytest` y los scripts de verificación correspondientes.

## Qué falta para el siguiente salto

El proyecto ya tiene motores neurosimbólicos básicos. El siguiente salto no es agregar otro solver, sino construir una capa superior:

```text
Base lógica persistente
+ hechos versionados
+ reglas persistentes
+ identidad de entidades
+ contradicciones
+ trazas históricas de razonamiento
+ planificación híbrida real
```

Equivalente conceptual con el proyecto japonés FGCS:

| FGCS/ICOT | Equivalente actual en ai-ecosystem | Estado |
|---|---|---|
| PIMOS | Hermes + hooks | Parcial |
| HELIOS | combined mode + varios motores | Parcial |
| MGTP | Z3/PyDatalog como motores parciales | Parcial |
| Kappa | Kùzu/CBM/Knowledge Broker | Parcial |
| Quixote | SymbolicProblem + grafo + reglas | Muy parcial |
| HELIC-II | Casos + debate + reglas | Pendiente |

## Documentación principal

```text
ARCHITECTURE.md          Arquitectura técnica vigente
SYSTEM_BLUEPRINT.md      Auditoría/blueprint del sistema
CLAUDE.md                Reglas operativas para Claude Code/Hermes
docs/README.md           Índice documental
docs/CBM_INTEGRATION.md  Integración CBM
docs/integration_summary.md  Resumen de verificación CBM/Hermes
KNOWLEDGE_BROKER.md      Capa de broker de conocimiento
```

## Principio de diseño

Este proyecto busca avanzar desde un asistente LLM con herramientas hacia un sistema híbrido donde:

- el LLM interpreta lenguaje y coordina;
- los motores simbólicos verifican restricciones, reglas y grafos;
- la memoria estructural recupera contexto;
- y las futuras capas persistentes convierten resultados en conocimiento reutilizable.
