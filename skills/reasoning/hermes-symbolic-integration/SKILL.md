---
name: hermes-symbolic-integration
description: Integration of neuro-symbolic reasoning router with Hermes chat pipeline
version: 1.0.0
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

This skill provides automatic neuro-symbolic reasoning integration with the Hermes chat pipeline. It intercepts user queries and routes them to appropriate symbolic engines (Z3, NetworkX, PyDatalog) based on semantic analysis.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Chat Pipeline                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              semantic_router.classify_task_structure        │
│                                                             │
│  Analyzes query strings → mode + engine + confidence        │
└─────────────────────────────────────────────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           ▼                  ▼                  ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │   LLM    │      │  Z3/SMT  │      │NetworkX  │
    │(llm_only)│      │(constraints│      │  (graph) │
    │          │      │ / rules) │      │          │
    └──────────┘      └──────────┘      └──────────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Result Integration + Final Response          │
└─────────────────────────────────────────────────────────────┘
```

## Modes

| Mode | Engine | Description | Tests |
|------|--------|-------------|-------|
| `llm_only` | none | Simple queries, no symbolic reasoning | test_a.py |
| `rules` | z3 | Logical rule validation, permission checks | test_b.py |
| `constraints` | z3 | Assignment, budget, resource allocation | test_c.py |
| `graph` | networkx | Dependency cycles, path analysis | test_d.py |
| `human_review` | none | Missing critical information | test_e.py |

## Installation

```bash
# Install dependencies
pip install networkx z3-solver pydatalog

# Copy skill to Hermes profile
cp ~/.hermes/skills/hermes-symbolic-integration /home/fernando/.hermes/skills/reasoning/
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

The skill integrates via two main entry points:

1. `hermes_auto_detect_and_reason()` - Auto-triggering for contextual analysis
2. `hermes_explicit_symbolic_reasoning()` - Explicit symbolic reasoning requests

Both functions are exposed through `hermes_integration.py` and called automatically during chat processing.

## Output Format

When symbolic reasoning activates, output includes trace markers:

```
[reasoning-router]
mode=<mode_name>
engine=<engine_name|none>
executed=<true|false>
result=<result_token>
evidence=<brief_explanation>
```

## Testing

Run the built-in tests:

```bash
python test_symbolic_integration.py
```

All 5 tests should pass with expected modes and engines.