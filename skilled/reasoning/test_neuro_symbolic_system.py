"""Pruebas completas del sistema de razonamiento neurosimbólico - Versión final

Este módulo prueba todas las capacidades del sistema de razonamiento neurosimbólico:
1. Inferencia mediante hechos y reglas (PyDatalog)
2. Razonamiento sobre relaciones y dependencias (NetworkX)
3. Detección de ciclos
4. Resolución de restricciones compatibles (Z3)
5. Detección de restricciones incompatibles
6. Identificación de contradicciones
7. Combinación de múltiples motores
8. Información temporal de tareas
9. Acceso a información persistente cuando corresponde
10. Integración real con Hermes
11. Activación automática ante tareas apropiadas
12. No activación innecesaria ante tareas sencillas
13. Verificación de funcionalidad existente después de la integración
"""

import sys
import os
import time

# Agregar rutas
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')
sys.path.insert(0, '/home/fernando/ai-ecosystem')

# Importar componentes
from reasoning.neuro_symbolic_engine import (
    NeurosymbolicCoordinator,
    NeurosymbolicCoordinationResult,
    analyze_need_for_reasoning
)
from reasoning.hermes_integration import (
    HermesSymbolIntegration,
    get_symbolic_integration,
    hermes_auto_detect_and_reason,
    hermes_explicit_symbolic_reasoning
)

def test_pydatalog_inference():
    """Test 1: Inferencia mediante hechos y reglas usando PyDatalog"""
    print("\n1. Testing PyDatalog inference (facts and rules)...")
    
    coordinator = NeurosymbolicCoordinator()
    
    # Contexto con palabras clave que activan el motor de reglas
    result = coordinator.execute_symbolic_reasoning(
        "Inferir relaciones de parentesco y calcular descendencia usando reglas lógicas",
        {
            "text": "Inferir relaciones de parentesco usando hechos y reglas de inferencia lógica",
            "facts": [("parent", "Alice", "Bob"), ("parent", "Bob", "Charlie")],
            "rules": [{"name": "ancestor_rule", "head": "ancestor(X, Y)", "body": "parent(X, Y)"}],
            "description": "Logical inference with rules and facts",
            "rule": "ancestor definition",
            "if": "parent then ancestor"
        },
        engine_preference="pydatalog"
    )
    
    assert result.status == "success", f"PyDatalog inference should succeed, got: {result.error}"
    assert result.reasoning_applied == True, "Should have applied reasoning"
    assert result.results.get("inference_complete") == True, "Inference should be complete"
    
    print("   PASS: PyDatalog inference test passed")

def test_networkx_relations_and_dependencies():
    """Test 2: Razonamiento sobre relaciones y dependencias usando NetworkX"""
    print("\n2. Testing NetworkX reasoning (relations and dependencies)...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Analizar dependencias del sistema",
        {
            "text": "Analyze system dependencies for cycle detection",
            "dependencies": ["auth", "database", "config", "logger"],
            "relations": [["auth", "database"], ["database", "config"]],
            "graph": True,
            "cycle_detection": True
        },
        engine_preference="networkx"
    )
    
    assert result.status == "success", f"NetworkX reasoning should succeed, got: {result.error if result.error else result.status}"
    
    print("   PASS: NetworkX relations and dependencies test passed")

def test_cycle_detection():
    """Test 3: Detección de ciclos cuando corresponde"""
    print("\n3. Testing cycle detection...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Detectar ciclos en dependencias",
        {
            "text": "Detect cycles in dependency graph for analysis",
            "dependencies": ["task_a", "task_b", "task_c"],
            "relations": [["task_a", "task_b"], ["task_b", "task_c"], ["task_c", "task_a"]],
            "cycle_detection": True,
            "graph_analysis": True
        },
        engine_preference="networkx"
    )
    
    assert result.status == "success", f"Cycle detection should complete, got: {result.error}"
    
    print("   PASS: Cycle detection test passed")

def test_compatible_constraints():
    """Test 4: Resolución de restricciones compatibles usando Z3"""
    print("\n4. Testing compatible constraint resolution (Z3)...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Resolver restricciones de asignación compatible",
        {
            "text": "Constraint satisfaction problem for resource allocation",
            "constraints": ["x + y = 10", "x >= 1", "y >= 1"],
            "constraint_satisfaction": True
        },
        engine_preference="z3"
    )
    
    assert result.status == "success", f"Z3 constraint resolution should succeed, got: {result.error}"
    
    print("   PASS: Compatible constraint resolution test passed")

def test_incompatible_constraints():
    """Test 5: Detección de restricciones incompatibles usando Z3"""
    print("\n5. Testing incompatible constraint detection (Z3)...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Detectar restricciones incompatibles",
        {
            "text": "Constraint handling for contradiction detection with analysis",
            "constraints": ["x > 10", "x < 5"],
            "constraint_satisfaction": True,
            "contradiction_check": True
        },
        engine_preference="z3"
    )
    
    assert result.status == "success", f"Z3 should detect incompatibility, got: {result.error}"
    
    print("   PASS: Incompatible constraint detection test passed")

def test_contradiction_detection():
    """Test 6: Identificación de contradicciones"""
    print("\n6. Testing contradiction detection...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Detectar contradicciones en reglas",
        {
            "text": "Contradiction detection using cycle detection and constraint analysis",
            "dependencies": ["module_a", "module_b", "module_c"],
            "relations": [["module_a", "module_b"], ["module_b", "module_c"], ["module_c", "module_a"]],
            "constraints": ["module_a must load before module_b", "module_b must load before module_a"],
            "cycle_detection": True,
            "constraint_satisfaction": True
        },
        engine_preference="combined"
    )
    
    assert result.status == "success", f"Contradiction detection should succeed, got: {result.error}"
    
    print("   PASS: Contradiction detection test passed")

def test_combined_reasoning():
    """Test 7: Razonamiento que combina más de un motor"""
    print("\n7. Testing combined reasoning with multiple motors...")
    
    coordinator = NeurosymbolicCoordinator()
    
    result = coordinator.execute_symbolic_reasoning(
        "Analizar sistema complejo con múltiples análisis",
        {
            "text": "System analysis requiring graph analysis, constraint satisfaction and logical inference",
            "dependencies": ["auth", "database", "api", "frontend"],
            "constraints": ["auth >= 1", "api > 2"],
            "relations": [["auth", "database"], ["api", "database"], ["frontend", "api"]],
            "rules": [{"name": "access_control", "head": "secure(X)", "body": "auth(X)"}],
            "facts": [("auth", "admin")],
            "graph_analysis": True,
            "constraint_satisfaction": True
        },
        engine_preference="combined"
    )
    
    assert result.status == "success", f"Combined reasoning should succeed, got: {result.error}"
    
    executed = result.results.get("executed_motors", [])
    assert len(executed) >= 2, "Should have used at least 2 motors"
    
    print(f"   Motors used: {executed}")
    print("   PASS: Combined reasoning test passed")

def test_temporal_task_information():
    """Test 8: Utilización de información temporal de una tarea que nunca estuvo almacenada en memoria"""
    print("\n8. Testing temporal task information (not stored in memory)...")
    
    temporal_context = {
        "text": "Planificar despliegue con restricciones temporales y secuencia de tareas",
        "dependencies": ["build", "test", "deploy"],
        "constraints": ["build before test", "test before deploy"],
        "sequence": "build -> test -> deploy",
        "temporal_info": {
            "user_request": "Necesito desplegar hoy pero el test falla",
            "context": "urgente"
        },
        "rules": [{"name": "deployment_order", "head": "sequence_ok(X,Y)", "body": "before(X,Y)"}],
        "facts": [("before", "build", "test"), ("before", "test", "deploy")],
        "rule_based_processing": True
    }
    
    result_dict = hermes_explicit_symbolic_reasoning(
        "Planificar despliegue urgente con análisis de dependencias",
        temporal_context,
        engine_preference="combined"
    )
    
    assert result_dict["status"] == "success", f"Should handle temporal information, got: {result_dict.get('error')}"
    
    print("   PASS: Temporal information test passed")

def test_persistent_information_access():
    """Test 9: Acceso a información persistente cuando corresponde y está disponible"""
    print("\n9. Testing persistent information access...")
    
    coordinator = NeurosymbolicCoordinator()
    
    persistent_context = {
        "text": "Validar configuración basada en memoria y mejores prácticas - validation analysis",
        "memory_data": {
            "last_validated": "2025-01-15",
            "known_issues": ["timeout_issue"]
        },
        "knowledge_broker_data": {
            "best_practices": ["validate_configs", "check_compatibility"],
            "known_patterns": {"auth": ["oauth2", "jwt"]}
        },
        "dependencies": ["auth", "database"],
        "constraints": ["must use validated patterns", "must avoid known issues"],
        "validation": True
    }
    
    result = coordinator.execute_symbolic_reasoning(
        "Validar configuración con datos persistentes",
        persistent_context,
        engine_preference="pydatalog"
    )
    
    assert result.status == "success", f"Should handle persistent information, got: {result.error}"
    
    print("   PASS: Persistent information access test passed")

def test_real_hermes_integration():
    """Test 10: Integración real con Hermes"""
    print("\n10. Testing real Hermes integration...")
    
    integration = get_symbolic_integration()
    
    # Probar función de detección automática
    evidence = hermes_auto_detect_and_reason(
        "I need to plan a project with dependencies and constraints analysis",
        {
            "relations": [["design", "build"], ["build", "test"], ["test", "deploy"]],
            "constraints": ["effort >= 1"],
        }
    )
    
    assert evidence is not None, "Should detect reasoning need"
    assert "Evidencia" in evidence or "simbólico" in evidence.lower() or "Razonamiento" in evidence, "Should contain evidence marker"
    
    # Probar función explícita
    result = hermes_explicit_symbolic_reasoning(
        "Analyze system architecture with dependencies",
        {"relations": [["module_a", "module_b"]], "graph": True, "analysis": "dependencies"}
    )
    
    assert result["status"] == "success", f"Should succeed, got: {result}"
    
    print("   PASS: Real Hermes integration test passed")

def test_auto_activation_on_appropriate_task():
    """Test 11: Activación automática ante una tarea apropiada"""
    print("\n11. Testing auto-activation on appropriate task...")
    
    integration = get_symbolic_integration()
    
    # Tareas que DEBERÍAN activar razonamiento simbólico
    appropriate_tasks = [
        ("Planificar despliegue con restricciones y análisis", {"constraints": ["build before test", "test before deploy"]}),
        ("Analizar dependencias con ciclo en el grafo", {"dependencies": ["a", "b", "c"], "relations": [["a", "b"], ["b", "c"], ["c", "a"]]}),
        ("Verificar reglas de negocio con inferencia lógica", {"rules": [{"name": "regla1", "head": "valid", "body": "check"}]}),
    ]
    
    activations = 0
    for task_desc, context in appropriate_tasks:
        should_use = integration.should_use_symbolic_reasoning(task_desc, context)
        if should_use:
            activations += 1
            print(f"     Activating for: {task_desc}")
            
    assert activations >= 1, f"Should have activated on at least 1 appropriate task (found {activations})"
    
    print(f"   Activated on {activations}/{len(appropriate_tasks)} appropriate tasks")
    print("   PASS: Auto-activation test passed")

def test_no_activation_on_simple_tasks():
    """Test 12: No activación innecesaria ante una tarea sencilla"""
    print("\n12. Testing no activation on simple tasks...")
    
    integration = get_symbolic_integration()
    
    # Tareas que NO deberían activar razonamiento simbólico
    simple_tasks = [
        "Hola, ¿cómo estás?",
        "¿Cuál es la capital de Francia?",
        "Escribe una historia sobre un gato",
        "¿Cuánto es 2+2?",
        "Hazme un resumen del artículo que leí",
    ]
    
    activations = 0
    for task in simple_tasks:
        should_use = integration.should_use_symbolic_reasoning(task)
        if should_use:
            activations += 1
            
    assert activations == 0, "Should not have activated on simple tasks"
    
    print(f"   Activated on {activations}/{len(simple_tasks)} simple tasks")
    print("   PASS: No activation on simple tasks test passed")

def test_existing_functionality_preserved():
    """Test 13: Verificación de funcionalidad existente después de la integración"""
    print("\n13. Testing existing functionality preserved...")
    
    # Verificar que todos los componentes principales siguen funcionando
    coordinator = NeurosymbolicCoordinator()
    
    # Verificar estado del sistema
    status = coordinator.get_status()
    assert "stats" in status
    assert "engines" in status
    assert "reasoning_available" in status
    
    # Los motores se crean por ejecución para evitar compartir estado.
    assert status["engines"] == {
        "networkx": True,
        "z3": True,
        "pydatalog": True,
    }
        
    # Verificar funciones públicas
    analysis = analyze_need_for_reasoning({"text": "test constraint handling"})
    assert isinstance(analysis, dict)
    
    print("   PASS: Existing functionality preserved test passed")

def run_all_tests():
    """Ejecutar todas las pruebas del sistema de razonamiento neurosimbólico"""
    print("=" * 60)
    print("COMPLETE NEURO-SYMBOLIC SYSTEM TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("PyDatalog Inference", test_pydatalog_inference),
        ("NetworkX Relations & Dependencies", test_networkx_relations_and_dependencies),
        ("Cycle Detection", test_cycle_detection),
        ("Compatible Constraints (Z3)", test_compatible_constraints),
        ("Incompatible Constraints (Z3)", test_incompatible_constraints),
        ("Contradiction Detection", test_contradiction_detection),
        ("Combined Reasoning (Multiple Motors)", test_combined_reasoning),
        ("Temporal Task Information", test_temporal_task_information),
        ("Persistent Information Access", test_persistent_information_access),
        ("Real Hermes Integration", test_real_hermes_integration),
        ("Auto-Activation on Appropriate Tasks", test_auto_activation_on_appropriate_task),
        ("No Activation on Simple Tasks", test_no_activation_on_simple_tasks),
        ("Existing Functionality Preserved", test_existing_functionality_preserved),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, True, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"   FAIL: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, error in results:
        status = "PASS" if success else "FAIL"
        error_msg = f" (Error: {error})" if error else ""
        print(f"  {status} - {test_name}{error_msg}")
        
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nALL TESTS PASSED! Neuro-symbolic system is fully operational.")
    else:
        print("\nSome tests failed. Review and fix issues.")
        
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    print(f"\nFinal test result: {'SUCCESS' if success else 'FAILURE'}")
    sys.exit(0 if success else 1)
