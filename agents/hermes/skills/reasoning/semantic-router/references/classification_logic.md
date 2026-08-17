# Classification Logic Reference

## Mode Priority Order

The semantic router evaluates modes in this order:

1. **UNCAUGHT EXCEPTION** - If scores dict is empty → `llm_only`
2. **UNCERTAINTY DETECTION** - If uncertainty indicators present AND human_review pattern matches → `human_review` (short-circuit)
3. **HYBRID DETECTION** - If top mode is "hybrid" OR second-highest score >= 70% of top score AND >= 2 modes have scores >= 50% of top score → `hybrid`
4. **SINGLE MODE** - Return the highest-scoring mode

## Uncertainty Indicators

These phrases trigger `human_review` when matched with `human_review` pattern:

| Indicator | Purpose |
|-----------|---------|
| "sin información" | Missing data |
| "no hay datos" | No data available |
| "falta información" | Missing information |
| "desconocido" | Unknown state |

## Scoring System

| Pattern Type | Points |
|--------------|--------|
| Keyword match | 2 per occurrence |
| Structural regex match | 5 per pattern |

## Engine Mapping

| Mode | Engine |
|------|--------|
| rules | z3 |
| constraints | z3 |
| graph | networkx |
| hybrid | combined |
| human_review | none |
| llm_only | none |

## Test Cases

```python
# Uncertainty triggers human_review despite hybrid scores
test = "Asigna diez usuarios a cinco equipos bajo presupuesto limitado, pero sin información de costos."
# Expected: human_review (constraints=9, human_review=7, but uncertainty detected)

# Hybrid when combining domains
test = "Planifica el cambio y comprueba tanto políticas como dependencias."
# Expected: hybrid (policies + dependencies)

# Pure constraints
test = "Asigna diez usuarios a cinco equipos bajo presupuesto limitado."
# Expected: constraints
```