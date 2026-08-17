---
name: semantic-router
description: "Automatic classification and routing of user requests to appropriate reasoning modes"
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [neurosymbolic, reasoning, routing, automation, symbolic-ai]
---


## Uncertainty Handling

When uncertainty indicators ('sin información', 'no hay datos', or 'falta información') are detected in a request, the semantic router prioritizes `human_review` mode with `NONE` engine and 80% confidence to ensure accurate execution. This takes precedence over hybrid detection when critical data is missing.

### Confidence Semantics
**Critical clarification**: `confidence` represents the router's confidence in the *classification decision*, NOT the confidence that the task can be solved automatically. 

- `human_review` with `confidence=0.8` means: "The router is 80% certain this request requires human review"
- This is semantically correct — high classification confidence for human review is desired

### Practical Example

The classification behavior addresses user preference for practical verification:

```python
test_input = "Asigna diez usuarios a cinco equipos bajo presupuesto limitado, pero sin información de costos."
result = classify_task_structure(test_input)

# Before fix: Would incorrectly classify as hybrid with reduced confidence
# After fix: Correctly classifies as human_review due to uncertainty detection

assert result["mode"] == "human_review"
assert result["confidence"] == 0.8
assert result["recommended_engine"] == "none"
```

### False Positive Prevention

The router now correctly distinguishes between:
- **Missing critical info** → `human_review`: "No hay datos de costos", "Información insuficiente", "Costos desconocidos"
- **Negative assertions** → NO `human_review`: "No hay restricciones de presupuesto", "No hay datos faltantes"
- **Contextual negation**: "Los costos son desconocidos pero no intervienen" → NO `human_review` if not needed for resolution

See `references/classification_logic.md` for detailed scoring logic and engine mapping.

## Purpose
Automatically detect the optimal reasoning mode for incoming user requests and route them to the appropriate symbolic engine without requiring manual tags (#RAZONAMIENTO, #DEPENDENCY, etc.).

## Key Concepts

### Automatic Mode Selection
Instead of relying on user-provided tags, the semantic router analyzes the **structural characteristics** of the request to determine the most appropriate reasoning approach:

1. **Linguistic Tasks** (e.g., summary, translation, casual conversation)
   → Mode: `llm_only`

2. **Policy & Permission Checks**
   → Mode: `rules` → Engine: `z3`

3. **Constraint Satisfaction Problems** (e.g., scheduling, budgeting, assignment)
   → Mode: `constraints` → Engine: `z3`

4. **Dependency & Graph Analysis** (e.g., task ordering, cycle detection)
   → Mode: `graph` → Engine: `networkx`

5. **Multi-Domain Requests** (e.g., "Planifica el cambio y comprueba tanto políticas como dependencias.")
   → Mode: `hybrid` → Engines: `networkx` + `z3` + `pydatalog`

6. **Uncertain or Insufficient Data** (e.g., missing constraints, conflicting info)
   → Mode: `human_review`

## Implementation Details

Pattern recognition uses both keyword analysis and structural indicators (e.g., "if-then", "sequence", "constraint satisfaction"). Each pattern type contributes to a confidence score which determines the mode.

Classification is performed in constant-time (~ O(n) where n is length of input) to ensure minimal performance impact.

## Integration Guide

To integrate the Semantic Router into any agent workflow:

1. **Import the classifier function**:
   ```python
   from skilled.reasoning.semantic_router import classify_task_structure
   ```

2. **Classify each incoming request**:
   ```python
   classification = classify_task_structure(user_request)
   ```

3. **Route based on returned mode**:
   ```python
   if classification["mode"] != "llm_only":
       execute_symbolic_reasoning(classification)
   else:
       normal_llm_processing()
   ```

## Testing

Unit tests for the Semantic Router are located in:
 - `tests/test_semantic_router/test_core_modes.py`

Run with:
```bash
PYTHONPATH=/path/to/skilled:$PYTHONPATH pytest tests/
```

## Verification Test Example

A minimal test validates core classification behavior:

```bash
python3 - <<'PYTEST'
from skilled.reasoning.semantic_router import classify_task_structure

# Test case: rule-based request
result = classify_task_structure("Regla: Un editor solo puede leer archivos. Ana es editora. ¿Puede modificar config.yaml?")
assert result["mode"] == "rules", f"Expected 'rules', got {result['mode']}"
assert result["recommended_engine"] == "z3", f"Expected 'z3', got {result['recommended_engine']}"
print("✅ Rule classification test passed")
PYTEST
```

This test can be executed directly without a test framework and confirms that rule-based queries are routed to the symbolic rules engine (`z3`) correctly.

## References

- [Neuro-Symbolic Reasoning in Hermes](../../../../../README.md#ejemplo-de-razonamiento)
- [Symbolic Engine Integration](../../../plugins/neurosymbolic-integration/plugin.yaml)

The local `references/` directory documents classification; runtime engine behavior is documented and tested at the canonical links above.
