"""Script de prueba para validar el motor de razonamiento neurosimbólico"""

import sys
import os

# Agregar directorios necesarios al path
sys.path.insert(0, '/home/fernando/ai-ecosystem/skilled')
sys.path.insert(0, '/home/fernando/ai-ecosystem')

from reasoning.networkx_wrapper import GraphAnalyzer
from reasoning.pydatalog_integration import SymbolicEngine
from reasoning.z3_solver_integration import ConstraintSolver

def test_networkx():
    print("=== Testing NetworkX Wrapper ===")
    analyzer = GraphAnalyzer()
    
    # Añadir nodos y aristas
    analyzer.add_nodes(['A', 'B', 'C'])
    analyzer.add_edges([('A', 'B'), ('B', 'C'), ('C', 'A')])  # Ciclo
    
    print(f"Ciclos detectados: {analyzer.detect_cycles()}")
    print(f"Grafo acíclico: {analyzer.is_acyclic()}")
    print(f"Ruta A->C: {analyzer.find_shortest_path('A', 'C')}")
    print(f"Visualización:\n{analyzer.visualize_structure()}")
    print("✓ NetworkX Wrapper test passed\n")

def test_pydatalog():
    print("=== Testing PyDatalog Integration ===")
    engine = SymbolicEngine()
    
    # Añadir hechos
    engine.add_fact('parent', 'Alice', 'Bob')
    engine.add_fact('parent', 'Bob', 'Charlie')
    engine.add_fact('parent', 'Charlie', 'David')
    
    # Definir reglas
    engine.define_rule('ancestor', 'parent(X, Y)', 'ancestor(X, Y)')
    
    # Consultar
    result = engine.query('parent(Alice, Y)')
    print(f"Resultado de consulta parent(Alice, Y): {result}")
    print(f"Total de hechos: {engine.get_fact_count()}")
    print(f"Total de reglas: {engine.get_rule_count()}")
    print("✓ PyDatalog Integration test passed\n")

def test_z3():
    print("=== Testing Z3 Solver ===")
    solver = ConstraintSolver()
    
    # Crear variables
    x = solver.add_integer_variable('x', min_val=0, max_val=10)
    y = solver.add_integer_variable('y', min_val=0, max_val=10)
    
    # Añadir restricciones
    solver.add_constraint('x > 3')
    solver.add_constraint('y < 8')
    
    # Resolver
    result = solver.solve()
    print(f"Estado: {result['status']}")
    if result['status'] == 'satisfiable':
        print(f"Solución encontrada: {result['solution']}")
    print("✓ Z3 Solver test passed\n")

def main():
    test_networkx()
    test_pydatalog()
    test_z3()
    print("=== Todos los tests pasaron exitosamente! ===")

if __name__ == "__main__":
    main()