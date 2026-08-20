# Guía de selección de motor

## Selección rápida

| Señal en la consulta | Motor |
|---|---|
| dependencias, flechas, ciclos, rutas | NetworkX |
| máximo, mínimo, límite, asignación | Z3 |
| hechos, reglas, parentesco, inferencia | PyDatalog |
| reglas + restricciones + grafos | combined |
| datos faltantes o relación ambigua | human_review |
| resumen, traducción, redacción | llm_only |

## NetworkX

Usar cuando el problema se pueda representar como grafo:

```text
A -> B
B -> C
C -> A
```

Preguntas típicas:

```text
¿hay ciclos?
¿cuál es el orden correcto?
¿qué depende de qué?
```

## Z3

Usar cuando hay restricciones simultáneas:

```text
máximo 2 tareas por persona
A y B no pueden ir juntas
x > 10
x < 5
```

Preguntas típicas:

```text
¿existe solución?
¿qué asignación cumple todo?
¿las restricciones son contradictorias?
```

## PyDatalog

Usar cuando hay hechos y reglas:

```text
parent(Alice,Bob)
parent(Bob,Charlie)
ancestor(X,Y) <= parent(X,Y)
```

Preguntas típicas:

```text
¿qué hechos se derivan?
¿qué reglas aplican?
¿qué bindings satisfacen la consulta?
```

## Combined

Usar cuando el `SymbolicProblem` contiene varios tipos:

```text
relations + constraints
facts + rules + constraints
relations + rules
```

Advertencia: `combined` todavía no es un planificador cognitivo completo; ejecuta motores y resume resultados.

## Human review

Usar cuando la formalización puede ser engañosa.

Ejemplo ambiguo:

```text
A depende de B
```

Sin contexto, puede significar varias cosas. No debe tratarse automáticamente como grafo técnico.

## Regla final

Si hay evidencia formalizable y el motor devuelve `success`, puede inyectarse al LLM.

Si hay `human_review`, `formalization_error`, `error` o `skipped`, no presentar como conclusión determinista.
