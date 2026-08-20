# Classification Logic

## Objetivo

Clasificar solicitudes de usuario según la estructura del problema, no solo por palabras clave.

## Modos

```text
llm_only
rules
constraints
graph
hybrid
human_review
```

## Motores recomendados

```text
none
networkx
z3
pydatalog
combined
```

## Criterios

### `llm_only`

Usar cuando la tarea es lingüística:

```text
resumir
traducir
redactar
explicar sin cálculo formal
```

### `graph`

Usar cuando hay relaciones formalizables:

```text
A -> B
A depende de B en un grafo
orden topológico
ciclo
ruta
```

Motor: `networkx`.

### `constraints`

Usar cuando hay límites simultáneos:

```text
máximo
mínimo
asignar
repartir
presupuesto
capacidad
```

Motor: `z3`.

### `rules`

Usar cuando hay hechos y reglas:

```text
si X entonces Y
hecho(...)
regla(...)
parent(A,B)
```

Motor: `pydatalog` o policy engine según contexto.

### `hybrid`

Usar cuando coexisten varias estructuras:

```text
relaciones + restricciones
reglas + dependencias
hechos + restricciones + grafo
```

Motor: `combined`.

### `human_review`

Usar cuando:

- falta información crítica;
- hay ambigüedad semántica;
- una relación puede interpretarse de varias formas;
- la formalización puede inducir una conclusión falsa.

## Confianza

`confidence` significa confianza en la clasificación, no confianza en resolver automáticamente.

Ejemplo:

```text
human_review, confidence=0.8
```

quiere decir:

```text
el router cree con alta confianza que se requiere revisión humana
```

## Negación vs incertidumbre

No confundir:

```text
No hay costos conocidos.
```

con:

```text
No hay restricciones de costos.
```

La primera puede requerir revisión; la segunda puede ser una condición válida.

## Regla operativa

La clasificación recomienda. La formalización y ejecución final corresponden a:

```text
ProblemExtractor
NeurosymbolicCoordinator
```
