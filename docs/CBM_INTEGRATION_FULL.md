# CBM Integration Full Guide

## Propósito

Esta guía describe el rol de `codebase-memory-mcp` dentro de `ai-ecosystem`.

CBM es una capa de memoria estructural del código. Sirve para navegar y consultar el repositorio, pero no reemplaza los motores neurosimbólicos ni la futura base lógica persistente.

## Arquitectura relacionada

```text
Repositorio ai-ecosystem
  ↓
codebase-memory-mcp
  ↓
Índice de código / grafo estructural
  ↓
Hermes / Claude Code
  ↓
contexto para tareas de desarrollo
```

En paralelo, el razonamiento simbólico ocurre en:

```text
skilled/reasoning/
  ├── symbolic_problem_schema.py
  ├── neuro_symbolic_engine.py
  ├── semantic_router.py
  ├── networkx_wrapper.py
  ├── z3_solver_integration.py
  └── pydatalog_integration.py
```

## Instalación

```bash
pnpm run cbm:install
```

## Indexación

```bash
pnpm run cbm:index
```

Reindexar cuando:

- se agreguen archivos relevantes;
- se muevan módulos;
- se actualicen componentes neurosimbólicos;
- una búsqueda devuelva resultados desactualizados.

## Búsqueda de código

```bash
QUERY="ProblemExtractor" pnpm run cbm:search
```

## Búsqueda de grafo

```bash
QUERY="reasoning" pnpm run cbm:graph
```

## Flujo recomendado de trabajo

Antes de editar una pieza del sistema:

```bash
QUERY="componente" pnpm run cbm:search
QUERY="componente" pnpm run cbm:graph
```

Luego revisar archivos manualmente y ejecutar pruebas específicas.

## Validación complementaria

CBM no valida comportamiento. Para validar comportamiento usar:

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_semantic_router
npm run test:hermes-cli
```

## Qué aporta CBM

- Localización rápida de archivos.
- Búsqueda de patrones.
- Navegación de relaciones de código.
- Contexto estructural para Claude Code.
- Menos riesgo de crear duplicados.

## Qué no aporta CBM

- No ejecuta Z3.
- No ejecuta PyDatalog.
- No ejecuta NetworkX como motor simbólico de usuario.
- No conserva hechos lógicos persistentes.
- No resuelve contradicciones.
- No sustituye pruebas.

## Relación con Kùzu y Knowledge Broker

| Capa | Rol |
|---|---|
| CBM | memoria estructural del código |
| Kùzu | grafo documental/conocimiento |
| LlamaIndex | ingesta/consulta sobre grafo |
| Knowledge Broker | intermediario de conocimiento |
| Núcleo neurosimbólico | razonamiento determinista |

## Próximo paso arquitectónico

La integración futura debería permitir:

```text
CBM hit
→ entidad de código
→ relación con archivo/fuente
→ hecho persistente
→ posible regla o dependencia
→ traza de razonamiento
```

Esto conectaría CBM con una futura `CanonicalLogicalKnowledgeBase`.
