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
| Grafos | `networkx_wrapper.py` | ciclos, orden topológico y dependencias |
| Restricciones | `z3_solver_integration.py` | SAT, UNSAT y modelos |
| Reglas | `pydatalog_integration.py` | inferencia directa y transitiva |
| Coordinación simbólica | `neuro_symbolic_engine.py`, `hermes_integration.py` | selección e aislamiento de motores |
| Tareas persistentes | `task_router.py` | dependencias, bloqueo, reanudación y verificación |
| Orquestación por roles | `skilled/orchestration/` | registro de agentes, dependencias e historial |
| Memoria | `sharememory/hermes_memory/` | persistencia, búsqueda y exportación validada |
| Mejora y evaluación | `skilled/improvement/`, `datasets/evaluation/` | dataset reproducible y evaluación de corpus |
| Plugin Hermes | `agents/hermes/plugins/neurosymbolic-integration/` | hooks unitarios y prueba CLI real |

La suite reproducible se ejecuta con `npm run verify:all`. Las integraciones
que requieren binarios, credenciales o presupuesto del host se ejecutan con
`npm run verify:all-live`.

## Flujo operativo

1. Hermes recibe una consulta.
2. El plugin puede añadir evidencia de NetworkX, Z3 o PyDatalog antes de la llamada al modelo.
3. Solo una orden con prefijo `/orchestrate` y `HERMES_AUTONOMY_ENABLED=1` entra en `HermesOrchestrationBridge`.
4. `AutonomousOrchestrator` descompone y supervisa; `TaskRouter` persiste el estado y mantiene bloqueos accionables.
5. `ClaudeCodeExecutor` puede ejecutar el rol `builder` cuando se registra de forma explícita y el host está autenticado.
6. Solo resultados validados se incorporan a memoria o al ciclo de mejora.

## Integraciones externas

| Integración | Estado | Condición |
|---|---|---|
| Hermes CLI | Verificada extremo a extremo | plugin descubierto y habilitado en el host |
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
