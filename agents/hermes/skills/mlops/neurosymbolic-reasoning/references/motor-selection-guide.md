# Guía para Elegir el Motor de Razonamiento Optimizado

Utilice esta guía para determinar cómo el sistema selecciona automáticamente el motor simbólico adecuado basándose en el contexto de la tarea.

## Criterios de Selección

1. **Complejidad del Problema**
   - Problemas simples de dependencias -> NetworkX
   - Reglas lógicas claras -> PyDatalog
   - Optimizaciones con restricciones -> Z3

2. **Requisitos Específicos**
   - Detectación de ciclos -> NetworkX
   - Validación de reglas lógicas -> PyDatalog
   - Programación con restricciones SAT -> Z3

3. **Enfoque de la Tarea**
   - Análisis visual de redes -> NetworkX
   - Inferencia deductiva -> PyDatalog
   - Solución algorítmica -> Z3

## Recomendaciones Core

- Use 'combined' para problemas no estructurados
- Prefiera PyDatalog para validación de reglas de negocio
- Reserve Z3 para problemas con más de 10 variables interactuantes

## Ejemplos Prácticos

```python
# Detectar ciclos en dependencias de microservicios
if task == "Validar topología de microservicios":
    context = {
        "dependencies": {
            "service_a": ["service_b"],
            "service_b": ["service_c"],
            "service_c": []
        }
    }
    engine_preference = "networkx"

# Validar criterios de elegibilidad para científicos
if task == "Validar asistencias para investigación":
    context = {
        "facts": [("graduados", True), ("publicaciones", 15)],
        "rules": [
            {"name": "experto_basico", "head": "aprobado", "body": "(graduados & publicaciones >= 5)"}
        ]
    }
    engine_preference = "pydatalog"

# Programar asignación de equipos con restricciones horarias
if task == "Optimizar distribución de equipos":
    context = {
        "variables": ["t1", "t2", "t3"],
        "constraints": [
            "t1 + t2 <= 8",
            "t2 + t3 >= 6",
            "t1 != t3"
        ]
    }
    engine_preference = "z3"
```

## Mantenimiento

- Este archivo se actualiza automáticamente cuando evoluciona el skill.
- Mantenga los nombres de motores consistentes con el código.
- Agregue nuevas entradas de motor al integrar nuevas herramientas.