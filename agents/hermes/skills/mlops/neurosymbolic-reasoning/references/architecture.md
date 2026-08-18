# Arquitectura neurosimbólica

## Flujo operativo

```text
mensaje de usuario
  → pre_llm_call: detección estructural, sin ejecutar motores
  → tool call oficial: neurosymbolic_reasoning
  → ProblemExtractor / SymbolicProblem
  → NetworkX → PyDatalog → Z3/Optimize
  → validación de motores y soportes
  → contrato fundamentado
  → Markdown determinista mediante transform_llm_output
```

Un turno simbólico que no llame la herramienta termina con una respuesta de
fallo seguro. El plugin no vuelve a ejecutar silenciosamente los motores desde
el hook y no altera el contador de sesión de forma artificial.

## Componentes

1. `schemas.py`: contrato que ve el modelo.
2. `tools.py`: único handler que ejecuta el pipeline.
3. `runtime.py`: correlación e idempotencia por `request_id` y turno.
4. `ProblemExtractor`: formalización con procedencia y supuestos explícitos.
5. `NeurosymbolicCoordinator`: selección o composición de motores.
6. `grounded_result.py`: afirmaciones, soporte, alcance y Markdown canónico.

## Composición

En modo `combined`, NetworkX deriva alcance, PyDatalog deriva estados y Z3
recibe las restricciones resultantes. El resultado global solo es exitoso si
todos los motores requeridos terminan y ninguna afirmación contiene una
referencia de soporte sin resolver.

## Aislamiento y trazabilidad

- Cada ejecución crea instancias nuevas de los motores.
- El handler reutiliza el resultado si Hermes repite el mismo `request_id`.
- Los logs son JSONL e incluyen `run_id`, estados y hash, sin copiar el prompt.
- La sesión oficial de Hermes es la fuente primaria para contar tool calls.

## Verificación

```bash
PYTHONPATH=.:./skilled python -m pytest -q \
  tests/test_hermes_plugin_hook.py \
  tests/test_composed_neurosymbolic_pipeline.py

npm run test:hermes-cli
```

La segunda prueba requiere una instalación real de Hermes y un proveedor con
tool calling funcional.
