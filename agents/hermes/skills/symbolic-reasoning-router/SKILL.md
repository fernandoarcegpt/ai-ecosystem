---
name: symbolic-reasoning-router
category: reasoning
description: Hermes semantic router for routing tasks to neuro-symbolic reasoning engine
---
# Hermes Semantic Router

This skill automates task routing to the neuro-symbolic reasoning engine when appropriate.

## Rules for Activation
- Detects semantic patterns indicating formal reasoning needs
- Triggers when keyword_score >= 3 and structural_patterns > 0
- Uses analyze_context_for_reasoning with reduced thresholds for critical tasks
- Prioritizes constraint satisfaction and cycle detection tasks

## Workflow
1. Analyze task description with keyword analysis
2. Check for structural patterns (graphs, constraints)
3. Compare with configured relevance thresholds
4. Route to Hermes if criteria met

## Configuration
thresholds: {keyword_score: 2.5, pattern_score: 1.0}
required_structural_patterns: ['constraint', 'graph', 'cycle']