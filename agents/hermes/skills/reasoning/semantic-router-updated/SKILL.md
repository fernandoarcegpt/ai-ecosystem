---
name: semantic-router-updated
description: "Automatic classification and routing of user requests to appropriate reasoning modes (updated for human_review priority)"
version: 2.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
tags: [neurosymbolic, reasoning, routing, automation, symbolic-ai]
related_skills: [neurosymbolic-reasoning]
---

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

## Uncertainty Detection (Priority Logic)
The router prioritizes `human_review` mode when ALL of these conditions are met:
- Explicit uncertainty indicators present: "sin información", "no hay datos", "falta información", "desconocido", "no conocemos"
- AND the request mentions constraints or budgeting contexts (e.g., "presupuesto", "costos", "asignar", "distribuir")
- AND no complete solution pathway can be established from keywords alone

### Critical Implementation
When ANY uncertainty indicator is detected, the mode is directly set to `human_review` with `engine=none`, bypassing other scoring logic to guarantee human review for missing critical information.

## Confidence Semantics
**Critical clarification**: `confidence` represents the router's confidence in the *classification decision*, NOT the confidence that the task can be solved automatically.
- `human_review` with `confidence=0.8` means: "The router is 80% certain this request requires human review"

## Integration Guide

To integrate the Semantic Router into any agent workflow:

1. Import the classifier function:
   ```python
   from skilled.reasoning.semantic_router import classify_task_structure
   ```

2. Classify each incoming request:
   ```python
   classification = classify_task_structure(user_request)
   ```

3. Route based on returned mode:
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
PYTHONPATH=/path/to/skilled:$PYTHONPATH pytest tests/test_semantic_router/
```

## References
- [Neuro-Symbolic Reasoning in Hermes](../../../../../README.md#ejemplo-de-razonamiento)
- [Symbolic Engine Integration](../../../plugins/neurosymbolic-integration/plugin.yaml)
- [Classification Logic](../semantic-router/references/classification_logic.md)

Use the canonical references above; this compatibility skill does not maintain a duplicate `references/` tree.
