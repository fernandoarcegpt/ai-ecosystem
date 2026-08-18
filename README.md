# AI Ecosystem

Repositorio experimental para integrar Hermes con razonamiento
neurosimbólico, enrutamiento de tareas y memoria persistente.

La documentación se navega desde
[`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md), que separa las
fuentes vigentes de las referencias parciales, históricas y reemplazadas.

## Qué funciona

- Detección y análisis de grafos dirigidos con NetworkX.
- Restricciones aritméticas y de asignación con Z3, incluyendo resultados
  satisfacibles e insatisfacibles.
- Inferencia familiar directa y transitiva con PyDatalog.
- Selección automática del motor a partir de un problema formalizado.
- Enrutamiento de tareas con dependencias, persistencia, reanudación,
  verificación y bloqueos humanos accionables.
- Registro de resultados verificados en `KnowledgeBroker` y recuperación
  después de reiniciar el proceso.
- Integración de razonamiento en el flujo CLI de Hermes mediante el plugin
  `agents/hermes/plugins/neurosymbolic-integration`.
- Orquestación explícita desde Hermes mediante `/orchestrate`, con agentes por
  rol, dependencias, verificación, memoria e historial de ejecución.
- Mejora continua conectada automáticamente a los informes de tareas.
- Dataset de evaluación reproducible con 72 casos autorizados y sintéticos.
- Inventario y evaluación por fragmentos de materiales extensos de texto/PDF.

El sistema formaliza únicamente relaciones y restricciones que puede
reconocer o que recibe de forma estructurada. Una lista plana de nombres no
se transforma en dependencias implícitas.

## Instalación para desarrollo

Requiere Python 3.12.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
```

Las dependencias de indexación y LlamaIndex están en `requirements.txt` y no
son necesarias para ejecutar la suite central.

## Verificación

```bash
npm test
```

Ese comando ejecuta la suite de aceptación usada por CI. Comprueba:

- ciclos y órdenes topológicos reales;
- SAT/UNSAT y modelos aritméticos reales;
- inferencia lógica transitiva;
- aislamiento entre ejecuciones;
- activación y no activación del razonamiento;
- ejecución de tareas, bloqueos, reanudación y persistencia;
- captura y recuperación de memoria verificada.

GitHub Actions ejecuta la misma selección en cada pull request y en los
pushes a `main`.

La comprobación reproducible completa se ejecuta con:

```bash
npm run verify:all
```

Incluye tests, auditoría de prompts/skills/servicios y reconstrucción exacta
del dataset. Las integraciones que requieren los binarios y credenciales del
host se prueban conjuntamente con `npm run verify:all-live`.

### Verificación real con Hermes CLI

Hermes descubre plugins de usuario en `~/.hermes/plugins/`. En una instalación de desarrollo se puede enlazar este plugin sin duplicarlo:

```bash
mkdir -p ~/.hermes/plugins
ln -s "$PWD/agents/hermes/plugins/neurosymbolic-integration" \
  ~/.hermes/plugins/neurosymbolic-integration
hermes plugins enable neurosymbolic-integration
npm run test:hermes-cli
```

Si el destino ya existe, revísalo y no lo sobrescribas. La prueba ejecuta `hermes chat -q` tres veces y exige evidencia de NetworkX, Z3 y PyDatalog en el hook `pre_llm_call`.

## Componentes principales

| Ruta | Responsabilidad |
|---|---|
| `skilled/reasoning/symbolic_problem_schema.py` | Formalización de problemas |
| `skilled/reasoning/neuro_symbolic_engine.py` | Coordinación de motores |
| `skilled/reasoning/networkx_wrapper.py` | Grafos y dependencias |
| `skilled/reasoning/z3_solver_integration.py` | Restricciones Z3 |
| `skilled/reasoning/pydatalog_integration.py` | Hechos, reglas y consultas |
| `skilled/reasoning/task_router.py` | Plan, ejecución, verificación y reanudación |
| `skilled/reasoning/operational_decision.py` | Árbol operativo central y auditable |
| `skilled/reasoning/claude_code_executor.py` | Ejecutor opt-in de Claude Code en modo JSON |
| `skilled/orchestration/` | Registro de agentes, orquestador y puente Hermes |
| `agents/hermes/skills/human_gate/skill.py` | Libro persistente de revisiones humanas |
| `sharememory/hermes_memory/knowledge_broker.py` | Memoria persistente y búsqueda |
| `sharememory/hermes_memory/work_memory.py` | Captura de resultados verificados |
| `skilled/improvement/` | Evidencia de mejora continua y datasets de evaluación |
| `datasets/evaluation/` | Dataset sintético versionado para evaluación comparativa |

## Ejemplo de razonamiento

```python
from reasoning.neuro_symbolic_engine import execute_symbolic_analysis

result = execute_symbolic_analysis(
    "Detecta el ciclo A -> B -> C -> A",
    {},
    engine_preference="networkx",
)

assert result["status"] == "success"
assert result["results"]["is_acyclic"] is False
```

Ejecuta el ejemplo con `PYTHONPATH=.:./skilled` desde la raíz del repositorio.

## Ejemplo de tareas persistentes

```python
from reasoning.task_router import TaskRouter

router = TaskRouter(store_path="runtime/tasks.json")
tasks = router.decompose_objective("Implementar y verificar el cambio")
report = router.execute_available(
    tasks,
    {
        "researcher": lambda task: {"completed": True},
        "orchestrator": lambda task: {"completed": True},
        "builder": lambda task: {"tests_passed": True},
        "qa": lambda task: {"smoke_test_passed": True},
    },
)
```

Si no existe un ejecutor, la tarea queda en `blocked` con motivo y acción
requerida. Una aprobación guardada en `HumanGate` reanuda automáticamente la tarea en la siguiente ejecución y libera sus dependientes; el trabajo independiente continúa mientras tanto.

Claude Code puede registrarse como ejecutor explícito del agente `builder`:

```python
from reasoning.claude_code_executor import ClaudeCodeExecutor
from reasoning.task_router import TaskRouter

executor = ClaudeCodeExecutor(".")
router = TaskRouter(executors={"builder": executor})
```

El adaptador usa `claude -p --output-format json --json-schema ...` y solo declara una implementación verificada cuando Claude devuelve evidencia y `tests_passed: true`.

Hermes puede iniciar el flujo completo únicamente con una orden explícita y
la habilitación del host:

```bash
export HERMES_AUTONOMY_ENABLED=1
hermes chat -q "/orchestrate Implementar y verificar el cambio"
```

Los mensajes ordinarios nunca disparan ejecución autónoma. La prueba real usa
un repositorio temporal y se ejecuta con `npm run test:hermes-autonomy-live`.

## Dataset y materiales extensos

El dataset versionado se reconstruye de manera determinista:

```bash
PYTHONPATH=.:./skilled python3 scripts/build_evaluation_dataset.py
```

Contiene 72 casos sintéticos, sin datos de usuario, separados en entrenamiento,
validación y evaluación. No autoriza fine-tuning; primero exige una mejora
comparativa medible.

Para inventariar, fragmentar y detectar duplicados en materiales disponibles:

```bash
PYTHONPATH=.:./skilled python3 scripts/evaluate_materials.py archivo.pdf libro.txt
```

## Memoria versionable

La memoria de ejecución permanece fuera del snapshot versionado. Solo entradas marcadas como `verified`/`validated` y con confianza suficiente se exportan:

```bash
PYTHONPATH=. python -m sharememory.hermes_memory.knowledge_broker \
  export-validated docs/validated-knowledge.json
```

`BasicMemory` usa ahora `basic_memory.json`; ya no comparte el esquema incompatible de `memory.json` con `KnowledgeBroker`.

## Límites verificables

- El parser de lenguaje natural cubre patrones explícitos, no comprensión
  lingüística general.
- Los ejecutores externos requieren binario, autenticación y presupuesto del host.
- OpenClaw, Proyecto Japonés, Hermes Workspace y Scrubs no existen como
  componentes identificables en este árbol; su auditoría queda cerrada como
  `not_present` hasta recibir una fuente canónica.
- Los árboles históricos y respaldos del repositorio se conservan; la suite
  central usa las rutas enumeradas en `package.json` y en CI.

## Criterio de éxito

Una función no se considera operativa solo por existir. Debe producir una
salida verificable, fallar de forma explícita cuando no puede formalizar el
problema y tener una prueba automatizada que compruebe el objetivo observable.
