# Comparación de motores neurosimbólicos

## Resumen

| Motor | Mejor para | No usar para |
|---|---|---|
| NetworkX | grafos, dependencias, ciclos, rutas, orden topológico | restricciones numéricas o reglas lógicas generales |
| Z3 | restricciones, asignaciones, SAT/UNSAT, límites | memoria persistente o inferencia por precedentes |
| PyDatalog | hechos, reglas, consultas lógicas | optimización numérica o grafos grandes |
| combined | problemas con mezcla de grafos, reglas y restricciones | planificación cognitiva profunda todavía |
| human_review | ambigüedad o falta de datos críticos | casos claramente formalizables |

## NetworkX

Uso:

```text
A depende de B
B depende de C
¿hay ciclos?
```

Capacidades:

- Construcción de grafos dirigidos.
- Detección de ciclos.
- DAG.
- Orden topológico.

Salida esperada:

```text
is_acyclic
cycles_found
topological_order
```

## Z3

Uso:

```text
Reparte A,B,C entre Ana,Luis.
Máximo una tarea por persona.
A y B no pueden estar juntas.
```

Capacidades:

- Variables enteras/booleanas.
- Restricciones.
- SAT/UNSAT.
- Validación de dominio cerrado.

Salida esperada:

```text
solution_status
solution_values
formalized_constraints
assignment
```

## PyDatalog

Uso:

```text
parent(Alice,Bob)
parent(Bob,Charlie)
ancestor(X,Y) <= parent(X,Y)
```

Capacidades:

- Hechos.
- Reglas.
- Consultas.
- Bindings.
- Hechos derivados.

Salida esperada:

```text
facts_processed
rules_applied
bindings
derived_facts
```

## Combined

Uso:

Cuando el problema trae varias estructuras a la vez:

```text
relaciones + restricciones + reglas
```

Estado actual:

- Ejecuta varios motores.
- Combina resultados básicos.
- Calcula confianza simple según motores ejecutados.

Limitación:

No es todavía un planificador híbrido profundo. El siguiente paso sería ordenar motores por dependencia lógica.

## Human review

Uso:

```text
A depende de B
```

sin contexto técnico puede ser ambiguo.

La ruta `human_review` evita inyectar evidencia determinista cuando la formalización puede ser incorrecta.

## Reglas de selección

```text
relaciones / flechas / ciclos      → NetworkX
máximo / mínimo / asignación       → Z3
hechos + reglas                    → PyDatalog
mezcla de estructuras              → combined
ambigüedad / datos faltantes       → human_review
solo lenguaje natural              → llm_only
```

## Relación con FGCS

| FGCS | ai-ecosystem |
|---|---|
| HELIOS | combined básico |
| MGTP | Z3/PyDatalog parciales |
| PIMOS | Hermes hook/orquestación |
| Quixote/Kappa | futura base lógica persistente |
