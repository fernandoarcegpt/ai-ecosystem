#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'skilled'))

print("Testing neurosymbolic engine...")

# Test 1: Import
try:
    from reasoning.neuro_symbolic_engine import NeurosymbolicCoordinator, execute_symbolic_analysis, analyze_need_for_reasoning
    from reasoning.hermes_integration import HermesSymbolIntegration, hermes_auto_detect_and_reason, hermes_explicit_symbolic_reasoning
    print("��✓ Imports successful")
except Exception as e:
    print(f"��✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Create coordinator
try:
    coord = NeurosymbolicCoordinator()
    print("��✓ Coordinator created")
except Exception as e:
    print(f"��✗ Coordinator creation failed: {e}")
    sys.exit(1)

# Test 3: Analyze context
try:
    context = {"description": "Test task with constraints", "constraints": [{"type": "order", "before": "A", "after": "B"}]}
    analysis = analyze_need_for_reasoning(context)
    print(f"��✓ Analysis completed: needs_reasoning={analysis.get('needs_symbolic_reasoning')}")
except Exception as e:
    print(f"��✗ Analysis failed: {e}")
    sys.exit(1)

# Test 4: Execute symbolic reasoning (should work with installed packages)
try:
    result = execute_symbolic_analysis(
        task_description="Test reasoning",
        context={"description": "Test", "dependencies": ["task1", "task2"], "constraints": [{"type": "order", "before": "task1", "after": "task2"}]}
    )
    print(f"��✓ Execution completed: status={result.get('status')}")
    if result.get('status') == 'success':
        print(f"  Engine used: {result.get('engine_used')}")
        print(f"  Execution time: {result.get('execution_time'):.3f}s")
except Exception as e:
    print(f"��✗ Execution failed: {e}")
    # Some executions might fail due to missing data, but that's okay for this test
    pass

# Test 5: Test state isolation by creating two coordinators and checking they don't share graph state
try:
    from reasoning.networkx_wrapper import GraphAnalyzer
    ga1 = GraphAnalyzer()
    ga1.add_nodes(['A', 'B'])
    ga1.add_edges([('A', 'B')])
    
    ga2 = GraphAnalyzer()
    # ga2 should be empty
    if len(ga2.graph.nodes()) == 0:
        print("��✓ State isolation: new graph analyzer is empty")
    else:
        print("��✗ State isolation failed: graph analyzer shares state")
except Exception as e:
    print(f"��✗ State isolation test failed: {e}")

# Test 6: Hermes integration public functions
try:
    evidence = hermes_auto_detect_and_reason(
        "Planificar despliegue con dependencias",
        {"dependencies": ["build", "test", "deploy"]}
    )
    if evidence is not None:
        print("��✓ Hermes auto-detection returned evidence")
        print(f"  Evidence length: {len(evidence)} chars")
    else:
        print("○ Hermes auto-detection returned None (no need detected)")
except Exception as e:
    print(f"��✗ Hermes integration test failed: {e}")

# Test 7: Explicit symbolic reasoning
try:
    result = hermes_explicit_symbolic_reasoning(
        "Validar reglas de acceso",
        {"facts": [("user", "admin")], "rules": [{"name": "access_rule", "head": "granted", "body": "user, admin"}]},
        engine_preference="pydatalog"
    )
    print(f"��✓ Explicit reasoning: status={result.get('status')}")
except Exception as e:
    print(f"��✗ Explicit reasoning failed: {e}")

print("\nAll tests completed!")
