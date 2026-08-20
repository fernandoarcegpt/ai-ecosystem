# Patrón de validación Z3

## Objetivo

Usar Z3 para validar problemas de restricciones, no para generar texto ni sustituir el razonamiento del LLM.

## Flujo correcto

```text
consulta
→ ProblemExtractor
→ SymbolicProblem(mode=CONSTRAINTS)
→ variables Z3
→ restricciones formalizadas
→ solver.check()
→ SAT / UNSAT / UNKNOWN
→ validación de dominio
→ evidencia estructurada
```

## Resultado válido

Un resultado solo debe considerarse válido si:

1. Las entidades fueron extraídas sin inventar datos.
2. Las variables tienen dominio cerrado.
3. Todas las restricciones relevantes fueron formalizadas.
4. Z3 devolvió `satisfiable` o `unsatisfiable`.
5. Si hay asignación, pasa la post-validación de `SymbolicProblem`.

## Ejemplo

```text
Reparte A,B,C entre Ana,Luis.
Máximo una tarea por persona.
```

Resultado esperado:

```text
unsatisfiable
```

porque hay 3 tareas y solo 2 personas con máximo 1 tarea cada una.

## Errores que deben rechazarse

```text
restricción desconocida
entidad inventada
variable sin dominio
modelo Z3 incompleto
valor fuera del dominio
solución que no pasa post-validación
```

## Estados

| Estado | Acción |
|---|---|
| `satisfiable` | aceptar si pasa post-validación |
| `unsatisfiable` | reportar contradicción de restricciones |
| `unknown` | no presentar como conclusión fuerte |
| `formalization_error` | pedir revisión o datos adicionales |
| `error` | no inyectar evidencia determinista |

## Prueba recomendada

```bash
PYTHONPATH=.:./skilled python3 -m pytest -q tests/test_neurosymbolic_corrected.py
```

## Regla de seguridad lógica

Nunca convertir una explicación del LLM en “prueba” si Z3 no ejecutó realmente el solver y no devolvió estado verificable.
