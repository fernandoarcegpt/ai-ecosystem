---
name: reasoning-integrator
description: "Neuro-symbolic reasoning engine integration and coordination with LLM workflows"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [neurosymbolic, reasoning, z3, networkx, pydatalog, policy-engine, integration]
---

# Reasoning Integrator

> Before changing engines, routing, or integration, consult the reasoning
> sources selected by `docs/DOCUMENTATION_INDEX.md` and apply their update criteria.

## Overview
The Reasoning Integrator provides neuro-symbolic reasoning capabilities that operate transparently alongside standard LLM processing. It integrates symbolic engines (Datalog, Z3, NetworkX) into the decision loop while maintaining full auditability.

## System Architecture

### Core Components

1. **Semantic Router** (`skilled/reasoning/semantic_router.py`)
   - Classifies requests automatically based on structural analysis
   - Routes to appropriate symbolic engine without manual tags
   - Returns structured mode/engine recommendations

2. **NeuroSymbolicCoordinator** (`skilled/reasoning/neuro_symbolic_engine.py`)
   - Central hub managing multiple symbolic engines
   - Coordinates inference across networkx, z3, and pydatalog
   - Produces structured results with evidence for LLM consumption

3. **Engine Integrations**
   - **NetworkX Wrapper**: Graph analysis, dependency resolution, cycle detection
   - **Z3 Solver**: Constraint satisfaction, policy validation, resource allocation
   - **PyDatalog Engine**: Logical inference, rule-based reasoning, fact derivation

### Operational Cycle

Every relevant request passes through this cycle:

1. **Interpretar** (LLM interprets natural language)
2. **Extraer** (Structured extraction of facts, rules, variables, constraints)
3. **Validar estructura** (Ensure extracted elements conform to expected schema)
4. **Ejecutar motor** (Run symbolic engine(s) based on router classification)
5. **Devolver al LLM** (Feed symbolic result back as evidence)
6. **Contrastar** (Cross-check LLM answer with symbolic result)
7. **Corregir** (Auto-modify contradictory responses)
8. **Escalar** (Route to human review when necessary)

## API Usage

### Programmatic Access

```python
# Import router and classifier
from skilled.reasoning.semantic_router import classify_task_structure
from skilled.reasoning.neuro_symbolic_engine import execute_symbolic_analysis

# Step 1: Classify the request
classification = classify_task_structure("Asigna cinco tareas a tres personas sin cruzar horarios y sin superar el presupuesto.")

# Step 2: Execute symbolic reasoning if needed
if classification["mode"] != "llm_only":
    result = execute_symbolic_analysis(
        task_description="Asigna cinco tareas a tres personas sin cruzar horarios y sin superar el presupuesto.",
        context={
            "variables": ["empleado1", "empleado2", "empleado3", "tarea1", ..., "tarea5"],
            "constraints": [
                "No overlapping schedules",
                "Total cost <= budget_limit"
            ]
        },
        engine_preference=classification["recommended_engine"]
    )
    
    # Use result.evidence_for_hermes in final response
    print(result["evidence_for_hermes"])
```

### CLI Integration Example

```python
# In Hermes main processing loop
classification = classify_task_structure(task_description)
log_audit_entry(
    mode=classification["mode"],
    engine=classification["recommended_engine"],
    reason="structural_analysis"
)

if classification["mode"] != "llm_only":
    symbolic_result = execute_symbolic_analysis(
        task_description,
        context_with_entities_and_constraints,
        classification["recommended_engine"]
    )
    # Inject evidence into LLM context before final response
```

## Policy Enforcement Points

Mandatory checkpoints before executing sensitive operations:

- **Pre-execution**: Validate policies, check constraints, review dependencies
- **Post-plan**: Verify ordering validity, check for cycles, satisfy constraints
- **Result validation**: Compare LLM proposal with symbolic result

### Hook Integration

```python
# Pre-action checkpoint
def pre_execute_hook(action: str, context: dict) -> bool:
    classification = classify_task_structure(action)
    
    # Block actions requiring symbolic validation
    if classification["mode"] in ["rules", "constraints"]:
        symbolic_result = execute_symbolic_analysis(action, context)
        
        # Block if symbolic engine detects violation
        if symbolic_result.get("solution_status") == "unsat":
            return False
            
        # Escalate if confidence is low
        if symbolic_result.get("confidence", 1.0) < 0.8:
            escalate_to_human_review(action, symbolic_result)
            return False  # Wait for approval
            
    return True

# Post-execution trace logging
def post_execute_hook(result: Any, context: dict) -> None:
    log_audit_trail(context, result, symbolic_results_used=True)
```

## Audit Trail Requirements

Auditable records must include (but never internal LLM chains):

- Selected reasoning mode
- Symbol engine invoked
- Operational reason summary
- Extracted facts/constraints sent to engine
- Structured result from engine
- Final decision taken
- Human intervention required (boolean)

## Testing

### Unit Tests
Located in `tests/`:
- `test_neuro_symbolic_system.py`
- `test_semantic_router/test_core_modes.py`
- `test_integration.py`

Run with:
```bash
PYTHONPATH=$HOME/ai-ecosystem/skilled:$PYTHONPATH pytest tests/
```

### Integration Scenarios

| Scenario | Trigger Text | Expected Mode | Engine |
|----------|--------------|---------------|--------|
| Rule-based policy | "¿El operador puede eliminar un archivo protegido según estas reglas?" | `rules` | `z3` |
| Dependency analysis | "Organiza estas tareas respetando sus dependencias y detecta ciclos." | `graph` | `networkx` |
| Constraint satisfaction | "Asigna cinco tareas a tres personas sin cruzar horarios y sin superar el presupuesto." | `constraints` | `z3` |
| Hybrid planning | "Planifica el cambio y comprueba tanto políticas como dependencias." | `hybrid` | `combined` |
| Simple summary | "Resume este documento." | `llm_only` | `none` |
| Uncertain request | "Asigna diez usuarios a cinco equipos bajo presupuesto limitado, pero sin información de costos." | `human_review` | `none` |

## Limitations

1. Engine availability depends on installed packages (networkx, z3-solver, pydatalog)
2. Very high uncertainty requests are escalated to human review rather than auto-processed
3. Some edge cases may require explicit engine selection via fallback mechanisms

## References

- [Semantic Router Documentation](../semantic-router/SKILL.md)
- [Validated engine integration](../../../../../README.md#componentes-principales)
- [Operational decision tree](../../../../../skilled/reasoning/operational_decision.py)
