# Comparativa de Motores y Cuándo Usar Cada Uno

Esta guía explica cuándo usar cada motor de razonamiento simbólico y cómo aprovechar al máximo para diferentes tipos de tareas.

## Comparativa General

| Característica | NetworkX | PyDatalog | Z3 Solver |
|--------------|----------|-----------|-----------|
| Paradigma | Grafos y relaciones | Lógica de predicados | Lógica de primer orden (SMT) |
| Complejidad | Media | Media-Alta | Alta |
| Tiempo de ejecución | Rápido | Rápido | Variable (PUEDE ser lento) |
| Memoria | Eficiente | Eficiente | Puede ser intensivo |
| Escalabilidad | Alta | Media-Alta | Media-Baja |
| Facilidad de uso | Media | Alta | Media-Baja |
| Interpretación de resultados | Intuitiva (grafos) | Lógica deductiva | Técnica (modelos) |

## Cuándo Usar NetworkX

### Casos de Uso Típicos

- **Planificación de tareas/construcción de pipelines**
  - Detectar ciclos en dependencias antes de ejecutar
  - Determinar orden topológico de ejecución

- **Análisis de arquitectura de software**
  - Validar que no hay ciclos en dependencias de paquetes
  - Analizar conectividad entre componentes

- **Diagnóstico de sistemas**
  - Identificar puntos de fallo críticos
  - Analizar redes de dependencias

### Ejemplo

```python
# Analizar dependencias de microservicios
context = {
    "dependencies": {
        "service_a": ["service_b"],
        "service_b": ["service_c"],
        "service_c": []
    }
}

result = hermes_explicit_symbolic_reasoning(
    "Validar topología de microservicios",
    context,
    engine_preference="networkx"
)
```

## Cuándo Usar PyDatalog

### Casos de Uso Típicos

- **Validación de reglas de negocio**
  - Determinar elegibilidad de clientes para préstamos
  - Validar políticas de seguros

- **Sistemas expertos**
  - Motor de recomendaciones basado en hechos y reglas
  - Diagnóstico médico con protocolos clínicos

- **Análisis de cumplimiento normativo**
  - Verificar que transacciones cumplen con regulaciones
  - Validar acceso basado en roles

### Ejemplo

```python
# Validar elegibilidad para préstamo
context = {
    "facts": [
        ("edad", 25),
        ("ingresos_anuales", 50000),
        ("puntaje_credito", 720)
    ],
    "rules": [
        {"name": "edad_minima", "head": "elegible_edad", "body": "edad >= 18"},
        {"name": "ingreso_minimo", "head": "elegible_ingreso", "body": "ingresos_anuales >= 30000"},
        {"name": "credito_minimo", "head": "elegible_credito", "body": "puntaje_credito >= 650"},
        {"name": "aprobacion", "head": "aprobado", "body": "elegible_edad & elegible_ingreso & elegible_credito"}
    ]
}

result = hermes_explicit_symbolic_reasoning(
    "Verificar elegibilidad para préstamo",
    context,
    engine_preference="pydatalog"
)
```

## Cuándo Usar Z3 Solver

### Casos de Uso Típicos

- **Planificación y programación**
  - Asignación de recursos con restricciones
  - Planificación de horarios (examenes, trabajos)

- **Verificación de software**
  - Encontrar violaciones de invariantes
  - Comprobar cobertura de casos de prueba

- **Optimización de sistemas**
  - Configuración óptima de parámetros
  - Resolución de problemas combinados

### Consideraciones de Rendimiento

- Z3 puede ser **lento** con problemas muy complejos
- Es ideal para problemas con **muchas variables interdependientes**
- Para problemas simples, PyDatalog suele ser suficiente

### Ejemplo

```python
# Planificar horarios de exámenes
context = {
    "variables": {
        "hora_examen_matematicas": "int",
        "hora_examen_fisica": "int",
        "hora_examen_quimica": "int"
    },
    "constraints": [
        "hora_examen_matematicas >= 9",
        "hora_examen_matematicas <= 17",
        "hora_examen_fisica >= 9",
        "hora_examen_fisica <= 17",
        "hora_examen_quimica >= 9",
        "hora_examen_quimica <= 17",
        "hora_examen_matematicas != hora_examen_fisica",
        "hora_examen_matematicas != hora_examen_quimica",
        "hora_examen_fisica != hora_examen_quimica"
    ],
    "objectives": {
        "minimize": "hora_examen_quimica"  # Preferir química lo más temprano posible
    }
}

result = hermes_explicit_symbolic_reasoning(
    "Planificar horarios de exámenes sin solapamiento",
    context,
    engine_preference="z3"
)
```

## Motor 'combined'

Cuando `engine_preference="combined"`:

1. Se ejecutan todos los motores disponibles
2. Cada motor analiza su aspecto correspondiente
3. Los resultados se consolidan en una conclusión final
4. La confianza se calcula como promedio de confianzas individuales

### Ventajas

- **Cobertura máxima**: Captura problemas complejos que cada motor por separado podría no resolver
- **Robustez**: Si un motor falla, otros pueden proporcionar resultados

### Desventajas

- **Mayor costo computacional**: Ejecuta tres motores en lugar de uno
- **Complejidad de integración**: Puede ser difícil consolidar resultados divergentes

## Recomendaciones para Elección Manual

| Escenario | Motor Sugerido |
|-----------|----------------|
| Simple estructura de dependencias | NetworkX |
| Reglas de negocio claras | PyDatalog |
| Restricciones complejas con optimización | Z3 |
| Tarea mixta o desconocida | 'combined' |
| Priorizar velocidad sobre exhaustividad | NetworkX o PyDatalog |
| Priorizar exhaustividad sobre velocidad | Z3 o 'combined' |