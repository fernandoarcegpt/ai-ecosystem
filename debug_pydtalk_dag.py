#!/usr/bin/env python3
"""Debug script to trace exactly what happens during PyDatalog execution"""

import sys
import os
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')

from reasoning.symbolic_problem_schema import SymbolicProblem, SymbolicConstraint
from reasoning.neuro_symbolic_engine import NeurosymbolicCoordinator
from reasoning.symbolic_problem_schema import ReasoningMode

# Reproduce the exact scenario from the failing test
coordinator = NeurosymbolicCoordinator()

context = {
    "source_query": "parent(Alice,Bob), parent(Bob,Charlie)",
    "facts": [("parent", "Alice", "Bob"), ("parent", "Bob", "Charlie")],
    "rules": [{"name": "ancestor_rule", "head": "ancestor(X, Y)", "body": "parent(X, Y)"}]
}

print("=== Debugging PyDatalog Execution ===")

try:
    print("1. Calling analyze_context_for_reasoning...")
    analysis = coordinator.analyze_context_for_reasoning(context)
    print(f"   Analysis result: {analysis}")
    
    print("2. Checking needs_symbolic_reasoning...")
    if analysis.get("needs_symbolic_reasoning"):
        print("   -> Needs symbolic reasoning")
        print("3. Calling execute_symbolic_reasoning...")
        result = coordinator.execute_symbolic_reasoning(
            "Derivar ancestros",
            context,
            engine_preference="pydatalog"
        )
        print(f"   Result: {result}")
        print(f"   Result[status]: {result.get('status')}")
        print(f"   Result[success]: {result.get('success', 'NOT SET')}")
        print(f"   Result[reasoning_applied]: {result.get('reasoning_applied')}")
    else:
        print("   -> Does NOT need symbolic reasoning")
        
except Exception as e:
    print(f"   EXCEPTION: {e}")
    import traceback
    traceback.print_exc()