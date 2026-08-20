# Arquitectura neurosimbólica

## Flujo actual

```text
Usuario
  ↓
Hermes Agent / Claude Code
  ↓
pre_llm_call hook
  ↓
HermesSymbolIntegration
  ↓
ProblemExtractor
  ↓
SymbolicProblem
  ↓
NetworkX / Z3 / PyDatalog / combined
  ↓
Evidencia estructurada
  ↓
Respuesta del LLM
```

## Componentes

| Componente | Archivo | Función |
|---|---|---|
| Integración Hermes | `skilled/reasoning/hermes_integration.py` | Adaptador entre Hermes y motor simbólico |
| Coordinador | `skilled/reasoning/neuro_symbolic_engine.py` | Selección y ejecución de motores |
| Formalización | `skilled/reasoning/symbolic_problem_schema.py` | Construye `SymbolicProblem` |
| Router | `skilled/reasoning/semantic_router.py` | Clasifica intención estructural |
| Grafos | `skilled/reasoning/networkx_wrapper.py` | Ciclos, DAG, orden topológico |
| Restricciones | `skilled/reasoning/z3_solver_integration.py` | SAT/UNSAT, asignaciones |
| Reglas | `skilled/reasoning/pydatalog_integration.py` | Hechos, reglas, bindings |

## Plugin Hermes

```text
agents/hermes/plugins/neurosymbolic-integration/
```

Declara:

```yaml
provides_hooks:
  - pre_llm_call
```

## Estados de resultado

```text
success
skipped
error
formalization_error
human_review
```

Solo `success` debe inyectarse como evidencia determinista al LLM.

## Brechas

Todavía falta:

```text
FactStore
RuleStore
EntityIdentityResolver
ContradictionEngine
ReasoningTraceStore
HybridPlanner
```

Esas piezas convertirían el razonamiento por consulta en conocimiento lógico persistente.
