# Arquitectura vigente de AI Ecosystem

> Fuente principal de arquitectura. Contrastada el 2026-08-17 con la rama
> `fix/core-verification-and-orchestration`. Para localizar documentación
> complementaria o histórica, consulte [`docs/DOCUMENTATION_INDEX.md`](docs/DOCUMENTATION_INDEX.md).

## Alcance real

El repositorio es un entorno Python de experimentación e integración para
Hermes. Combina razonamiento neurosimbólico, ejecución persistente de tareas,
memoria verificable, mejora continua y adaptadores opt-in para ejecutores
externos. `package.json` agrupa los comandos de prueba; no existe una
aplicación Node que requiera compilación.

## Componentes implementados y verificados

| Área | Implementación | Evidencia reproducible |
|---|---|---|
| Formalización y selección | `skilled/reasoning/symbolic_problem_schema.py`, `semantic_router.py`, `operational_decision.py` | `npm test` |
| Grafos | `networkx_wrapper.py` | ciclos, orden, alcance, ancestros/descendientes y cuellos de dependencia |
| Restricciones | `z3_solver_integration.py` | SAT/UNSAT, `Optimize`, objetivos jerárquicos y `unsat_core` trazable |
| Reglas | `pydatalog_integration.py` | hechos, reglas y consultas declaradas por `SymbolicProblem` |
| Coordinación simbólica | `neuro_symbolic_engine.py`, `hermes_integration.py` | selección aislada o composición NetworkX → PyDatalog → Z3 |
| Tareas persistentes | `task_router.py` | dependencias, bloqueo, reanudación y verificación |
| Orquestación por roles | `skilled/orchestration/` | registro de agentes, dependencias e historial |
| Memoria | `sharememory/hermes_memory/` | persistencia, búsqueda y exportación validada |
| Mejora y evaluación | `skilled/improvement/`, `datasets/evaluation/` | dataset reproducible y evaluación de corpus |
| Plugin Hermes | `agents/hermes/plugins/neurosymbolic-integration/` | herramienta oficial, hooks de control y pruebas unitarias; revalidación CLI real pendiente |

La suite reproducible se ejecuta con `npm run verify:all`. Las integraciones
que requieren binarios, credenciales o presupuesto del host se ejecutan con
`npm run verify:all-live`.

## Flujo operativo

1. Hermes recibe una consulta.
2. `ProblemExtractor` crea una IR trazable con hechos, reglas, relaciones,
   restricciones, variables, objetivos, incógnitas, consultas y procedencia.
3. Un modo simple ejecuta un motor aislado. `combined` encadena NetworkX →
   PyDatalog → Z3/Optimize y valida que todos los motores requeridos terminen.
4. `pre_llm_call` detecta estructura simbólica y requiere una llamada oficial a
   `neurosymbolic_reasoning`; el hook no ejecuta los motores.
5. La herramienta ejecuta el pipeline una sola vez, construye afirmaciones con
   soporte y produce Markdown determinista. `transform_llm_output` sustituye la
   redacción libre o falla de forma segura si faltó la tool call.
6. Solo una orden con prefijo `/orchestrate` y `HERMES_AUTONOMY_ENABLED=1` entra en `HermesOrchestrationBridge`.
7. `AutonomousOrchestrator` descompone y supervisa; `TaskRouter` persiste el estado y mantiene bloqueos accionables.
8. `ClaudeCodeExecutor` puede ejecutar el rol `builder` cuando se registra de forma explícita y el host está autenticado.
9. Solo resultados validados se incorporan a memoria o al ciclo de mejora.

## Integraciones externas

| Integración | Estado | Condición |
|---|---|---|
| Hermes CLI | Revalidación pendiente tras migración a tool oficial | plugin descubierto, habilitado y proveedor con tool calling |
| Claude Code | Verificada extremo a extremo | binario, autenticación, permisos y presupuesto |
| Codebase Memory MCP | Parcial | hay comandos y guías, pero el estado del índice y hook depende del host |
| Kùzu/LlamaIndex | Parcial | código de ingestión presente; fuera de la suite central |
| Obsidian/OKF | Histórico o no verificado | las guías conservadas no demuestran un servicio activo actual |

## Capacidades experimentales o parciales

- El reconocimiento de lenguaje natural formaliza patrones explícitos; no es comprensión general.
- Los skills cuantitativos, de categorización y delegación son instrucciones; su presencia no demuestra un comando ejecutable homónimo.
- `src/ingest.py` permite configurar `KNOWLEDGE_DB_PATH` y usa por defecto una ruta relativa al repositorio; la ingestión completa sigue fuera de la suite central.
- Los planes bajo `.claude/plans/` son propuestas, no estado desplegado.

## Pendiente o no presente

- OpenClaw, Proyecto Japonés, Hermes Workspace y Scrubs no tienen una fuente canónica identificable en este árbol.
- No hay evidencia de los comandos históricos `orchestrator-main`, `general-planning` ni `@hermes/cli`; no deben invocarse como ejecutables.
- La seguridad real quedó fuera del alcance de la verificación por decisión del propietario.

## Componentes históricos

`SYSTEM_BLUEPRINT.md`, `STRUCTURE.md`, las guías antiguas de CBM/OKF y el
catálogo legado de skills son instantáneas de etapas anteriores. Se conservan
para trazabilidad, pero no son fuentes operativas. El estado y sucesor de cada
uno constan en el índice maestro.

## Reglas de mantenimiento

- Un cambio estructural obliga a revisar este archivo y el índice maestro.
- Un cambio de comando obliga a revisar `README.md`, `CLAUDE.md`, `package.json` y las guías operativas relacionadas.
- Una integración se declara operativa solo si tiene evidencia automatizada o una prueba real registrada en `docs/verification-report.md`.
- Los parches se catalogan en `docs/PATCH_CATALOG.md`; su mera existencia no prueba que estén aplicados.
