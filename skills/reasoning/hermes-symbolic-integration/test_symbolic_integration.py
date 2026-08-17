#!/usr/bin/env python3
"""
Test script for hermes-symbolic-integration skill
Tests the 5 required test cases with expected results
"""

import sys
import os

def test_symbolic_integration():
    """Test all 5 modes with expected results"""
    from skilled.reasoning.semantic_router import classify_task_structure
    
    # Test cases from user requirements
    test_cases = {
        "A": {
            "query": "Resume en dos líneas qué es Hermes Agent.",
            "expected_mode": "llm_only",
            "expected_engine": "none",
            "expected_executed": False
        },
        "B": {
            "query": "Regla: los editores solo pueden leer archivos. Ana es editora. ¿Puede Ana modificar config.yaml?",
            "expected_mode": "rules",
            "expected_engine": "z3",
            "expected_executed": True
        },
        "C": {
            "query": "Asigna las tareas A,B,C,D,E,F entre Ana,Luis,Marta. Nadie puede recibir más de dos tareas y A y B no pueden asignarse a la misma persona.",
            "expected_mode": "constraints",
            "expected_engine": "z3",
            "expected_executed": True
        },
        "D": {
            "query": "A depende de B, B depende de C y C depende de A. Dame un orden válido de ejecución.",
            "expected_mode": "graph",
            "expected_engine": "networkx",
            "expected_executed": True
        },
        "E": {
            "query": "Distribuye diez usuarios entre cinco equipos sin superar un presupuesto total, pero no conocemos los costos de asignación.",
            "expected_mode": "human_review",
            "expected_engine": "none",
            "expected_executed": False  # human_review doesn't execute a symbolic engine
        }
    }
    
    print("🧪 Testing Hermes Symbolic Integration")
    print("=" * 50)
    
    passed = 0
    total = len(test_cases)
    
    # Modes that execute symbolic reasoning (not human_review or llm_only)
    symbolic_modes = ['constraints', 'rules', 'graph', 'hybrid']
    
    for label, case in test_cases.items():
        print(f"\n📝 TEST {label}: {case['query'][:50]}...")
        
        result = classify_task_structure(case['query'])
        mode = result['mode']
        engine = result['recommended_engine']
        # Only modes with symbolic engines execute
        executed = mode in symbolic_modes
        
        # Check results
        mode_ok = mode == case['expected_mode']
        engine_ok = engine == case['expected_engine']
        executed_ok = executed == case['expected_executed']
        
        if mode_ok and engine_ok and executed_ok:
            print(f"   ✅ PASS - mode={mode}, engine={engine}, executed={executed}")
            passed += 1
        else:
            print(f"   ❌ FAIL")
            print(f"      Expected: mode={case['expected_mode']}, engine={case['expected_engine']}, executed={case['expected_executed']}")
            print(f"      Got:      mode={mode}, engine={engine}, executed={executed}")
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration is working correctly.")
        return True
    else:
        print("❌⚠  Some tests failed. Check configuration.")
        return False

if __name__ == "__main__":
    success = test_symbolic_integration()
    sys.exit(0 if success else 1)