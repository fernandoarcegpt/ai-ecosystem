---
name: hermes-symbolic-integration
description: Integration of neuro-symbolic reasoning router with Hermes chat pipeline
version: 1.1.0
author: System
category: reasoning
tags:
  - reasoning
  - integration
  - semantic-router
  - z3
  - networkx
  - pydatalog
  - constraints
dependencies:
  - networkx
  - z3-solver
  - pydatalog
triggers:
  - semantic_routing
  - symbolic_reasoning
  - constraint_solving
  - graph_analysis
  - rule_validation
  - human_review
---

# Hermes Symbolic Integration

> Before changing the plugin, paths, or commands, consult the Hermes and
> reasoning section of `docs/DOCUMENTATION_INDEX.md` and apply its update criteria.

This skill provides automatic neuro-symbolic reasoning integration with the
Hermes chat pipeline. `ProblemExtractor` is the canonical formalizer. Simple
problems use one engine; `combined` problems transfer knowledge through
NetworkX → PyDatalog → Z3/Optimize. Hermes records the execution through the
official `neurosymbolic_reasoning` tool and receives deterministic Markdown.

## Architecture

`pre_llm_call detector → Hermes tool call → ProblemExtractor → SymbolicProblem → coordinator → grounded contract → transform_llm_output`

For composed problems the coordinator runs:

`NetworkX → graph facts → PyDatalog → derived constraints → Z3/Optimize → validation`

## Modes

| Mode | Engine | Description | Tests |
|------|--------|-------------|-------|
| `none` | none | No formalizable symbolic structure | acceptance suite |
| `logic` | PyDatalog | Facts, rules and explicit/inferred queries | acceptance suite |
| `constraints` | Z3/Optimize | Assignment, capacity and objectives | acceptance suite |
| `graphs` | NetworkX | Cycles, order and transitive reachability | acceptance suite |
| `combined` | NetworkX → PyDatalog → Z3 | Composed, validated reasoning | transfer-plan E2E |

## Installation

```bash
# Install dependencies
pip install networkx z3-solver pydatalog

# Copy skill to Hermes profile
cp ~/.hermes/skills/hermes-symbolic-integration $HOME/.hermes/skills/reasoning/
```

## Usage from CLI

```bash
# Simple query (LLM only)
hermes chat -q "What is Hermes Agent?"

# Rule-based query
hermes chat -q "Rule: editors can only read files. Ana is an editor. Can she modify config.yaml?"

# Constraint-based query
hermes chat -q "Assign tasks A,B,C among Ana,Luis,Marta with constraints..."

# Graph-based query
hermes chat -q "A depends on B, B depends on C, C depends on A. Valid order?"

# Human review query
hermes chat -q "Distribute 10 users among 5 teams but no budget info"
```

## Integration Points

The integration has three boundaries:

1. `pre_llm_call` detects structure but never executes an engine.
2. `neurosymbolic_reasoning` is the only execution boundary visible to Hermes.
3. `transform_llm_output` returns grounded Markdown or fails closed if the
   required tool call did not occur.

The handler is idempotent per `request_id`, so retries do not execute the
engines twice.

## Output Format

Runtime proof is JSON Lines and remains secondary to the Hermes transcript:

```json
{"schema_version":1,"event":"tool_completed","run_id":"...","status":"success","engine":"combined","engines":{"networkx":"success","pydatalog":"success","z3":"success"}}
```

## Testing

Run the built-in tests:

```bash
PYTHONPATH=.:./skilled python -m pytest -q \
  tests/test_hermes_plugin_hook.py \
  tests/test_composed_neurosymbolic_pipeline.py
```

For a real installation, run `npm run test:hermes-cli`; symbolic prompts must
show at least one official tool call and ordinary text must show zero.
