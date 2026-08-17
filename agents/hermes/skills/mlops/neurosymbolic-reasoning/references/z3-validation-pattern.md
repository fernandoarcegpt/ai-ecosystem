# Patrón de Validación para Soluciones Z3

Para asegurar que las soluciones Z3 satisfacen todas las restricciones, utilizar este patrón de validación independiente del motor:

```python
from collections import Counter

def validate_z3_solution(solution):
    """
    Valida que una solución Z3 cumple con:
    - Máximo 2 tareas por persona
    - A y B no asignados a la misma persona
    - Dominio cerrado de personas
    - Todas las tareas asignadas
    """
    # Verificar máximo 2 tareas por persona
    counts = Counter(solution.values())
    assert all(v <= 2 for v in counts.values()), f"Algunas personas tienen más de 2 tareas: {counts}"
    
    # Verificar que A y B no están en la misma persona
    assert solution["A"] != solution["B"], f"A y B asignados a la misma persona: {solution['A']}"
    
    # Verificar dominio cerrado de personas
    assert set(solution.values()).issubset({"Ana", "Luis", "Marta"}), f"Personas fuera del dominio: {set(solution.values())}"
    
    # Verificar que todas las tareas están asignadas
    assert set(solution.keys()) == {"A","B","C","D","E","F"}, f"Tareas faltantes o extra: {set(solution.keys())}"
    
    return True
```

## Uso en Tests

En lugar de confiar únicamente en `status=sat`, siempre validar la solución:

```python
result = execute_symbolic_analysis(task, context, engine_preference="z3")
if result["status"] == "success":
    z3_data = result["results"].get("z3_analysis", {})
    if "solution_values" in z3_data:
        validate_z3_solution(z3_data["solution_values"])
```