# AI Ecosystem

Repositorio experimental para integrar Hermes con razonamiento
neurosimbólico, enrutamiento de tareas y memoria persistente.

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

## Componentes principales

| Ruta | Responsabilidad |
|---|---|
| `skilled/reasoning/symbolic_problem_schema.py` | Formalización de problemas |
| `skilled/reasoning/neuro_symbolic_engine.py` | Coordinación de motores |
| `skilled/reasoning/networkx_wrapper.py` | Grafos y dependencias |
| `skilled/reasoning/z3_solver_integration.py` | Restricciones Z3 |
| `skilled/reasoning/pydatalog_integration.py` | Hechos, reglas y consultas |
| `skilled/reasoning/task_router.py` | Plan, ejecución, verificación y reanudación |
| `agents/hermes/skills/human_gate/skill.py` | Libro persistente de revisiones humanas |
| `sharememory/hermes_memory/knowledge_broker.py` | Memoria persistente y búsqueda |
| `sharememory/hermes_memory/work_memory.py` | Captura de resultados verificados |

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
requerida. Al resolver el bloqueo se puede llamar otra vez a
`execute_available`; el trabajo independiente continúa mientras tanto.

## Límites actuales

- El parser de lenguaje natural cubre patrones explícitos, no comprensión
  lingüística general.
- Los ejecutores de tareas se inyectan como funciones; este módulo no crea
  procesos ni agentes externos por sí solo.
- La integración automática incluida está validada para la plataforma CLI.
- Los árboles históricos y respaldos del repositorio se conservan; la suite
  central usa las rutas enumeradas en `package.json` y en CI.

## Criterio de éxito

Una función no se considera operativa solo por existir. Debe producir una
salida verificable, fallar de forma explícita cuando no puede formalizar el
problema y tener una prueba automatizada que compruebe el objetivo observable.
