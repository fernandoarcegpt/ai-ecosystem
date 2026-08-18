# Informe de verificación integral (sin seguridad)

Fecha de corte: 2026-08-17.

## Resultado ejecutivo

El núcleo reproducible pasó **75 pruebas** e integra razonamiento neurosimbólico, tareas persistentes,
agentes por rol, ejecución mediante Claude Code, memoria versionable, mejora
continua, dataset y evaluación de materiales extensos. Las pruebas reales ya
aportadas en el host verificaron Hermes CLI con NetworkX/Z3/PyDatalog y Claude
Code mediante `TaskRouter`. La ejecución conjunta `npm run verify:all-live`
también terminó correctamente, incluida la ruta Hermes → orquestador → Claude
Code con verificación independiente.

La seguridad permanece fuera de alcance por indicación del propietario. Los
componentes externos que no existen en el árbol se registran como `not_present`;
no se inventa una evaluación sin URL o paquete inequívoco.

## Matriz consolidada

| Parte | Estado y evidencia |
|---|---|
| NetworkX, PyDatalog y Z3 | Verificado por suite y Hermes CLI real |
| Ciclos, contradicciones, SAT/UNSAT e inferencia transitiva | Verificado |
| Activación y no activación del razonador | Verificado |
| Persistencia y dependencias de tareas | Verificado |
| Bloqueo por falta de ejecutor | Verificado |
| Continuación de trabajo independiente | Verificado |
| Reanudación manual y automática | Verificado |
| Persistencia de decisiones humanas | Verificado |
| Captura y recuperación de resultados en memoria | Verificado |
| `npm test` y GitHub Actions | Verificado: 75 pruebas aprobadas |
| Autonomía real dentro de Hermes | Verificada extremo a extremo con `/orchestrate` y Claude Code real |
| Hermes CLI con los tres motores | Verificado extremo a extremo, 3/3 |
| Informe de bloqueo completo | Verificado: evidencia, alternativas, riesgos y siguiente acción |
| Arquitectura de agentes y miniagentes | Implementada mediante registro de roles, ejecutores y plan multi-etapa |
| Claude Code autónomo integrado | Verificado extremo a extremo mediante `TaskRouter` |
| Árboles de decisión generales | Implementado y verificado |
| OpenClaw, Proyecto Japonés, Hermes Workspace y Scrubs | Evaluación del árbol cerrada: `not_present`; integración externa no aplicable sin fuente |
| Mejora continua | Conectada automáticamente a los informes e historial |
| Estrategia y construcción de dataset | Implementada; 72 casos sintéticos reproducibles, con 3 splits |
| Libros y materiales voluminosos | Evaluador implementado: inventario, fragmentación, hash y duplicados |
| Memoria versionable | Snapshot validado implementado y verificado |
| Prompts, skills y servicios | Activos críticos actualizados y auditados automáticamente |
| Pruebas reales de seguridad | Excluidas por indicación del propietario |
| Informe final con 16 entregables | Este documento, actualizado |

## Los 16 entregables

### 1. Arquitectura real

Hermes usa un plugin de entrada, un árbol operativo, `TaskRouter`, registro de
agentes, ejecutores externos, `HumanGate`, `KnowledgeBroker`, tres motores
simbólicos y un ciclo de mejora. Las dependencias y estados se persisten.

### 2. Reutilización

Se reutilizaron el coordinador neurosimbólico, wrappers, router semántico,
memoria, puerta humana y plugin. No se duplicaron motores ni almacenes.

### 3. Componentes implementados

- `skilled/orchestration`: agentes, orquestador y puente Hermes.
- `skilled/improvement`: mejora, dataset y materiales extensos.
- Ejecutor real de Claude Code y pruebas de integración.
- Dataset versionado y auditoría operativa.

### 4. Integración transversal

Una solicitud explícita de Hermes puede producir un plan, asignar roles,
ejecutar, verificar, persistir, memorizar y generar propuestas de mejora. Los
mensajes normales no disparan ejecución autónoma.

### 5. Proyectos externos

La inspección del árbol no encontró OpenClaw, Proyecto Japonés, Hermes
Workspace ni Scrubs como fuentes identificables. El resultado y el dato
necesario para ampliar la evaluación están en
`docs/audits/external-components.json`.

### 6. Autonomía

`AgentRegistry` vincula roles con ejecutores. `AutonomousOrchestrator` ejecuta
planes multi-etapa y guarda `tasks.json` y `run-history.json`. El puente Hermes
solo acepta `/orchestrate` con habilitación explícita.

### 7. Bloqueo humano

Los bloqueos contienen estado, evidencia, impedimento, alternativas, riesgos,
acción humana y reanudación. Las decisiones se conservan y liberan dependientes.

### 8. Seguridad

No se modificó ni probó en esta fase.

### 9. Memoria

Solo resultados verificados llegan a `WorkMemoryRecorder`. La memoria de
ejecución permanece separada del snapshot versionable validado.

### 10. Capacidad neurosimbólica

NetworkX, Z3 y PyDatalog se seleccionan y ejecutan automáticamente. La prueba
real `test:hermes-cli` verificó ejecución e inyección de los tres motores.

### 11. Mejora continua

Cada ejecución añade su informe al historial. Fallos o bloqueos repetidos
generan propuestas con evidencia, métrica y riesgo. Las regresiones de guardas
impiden aceptar una mejora.

### 12. Dataset

`datasets/evaluation` contiene 72 casos sintéticos: 62 de entrenamiento, 6 de
validación y 4 de evaluación. No contiene datos de usuario ni autoriza
fine-tuning. Su reconstrucción exacta forma parte de `verify:all`.

### 13. Pruebas

`npm test` cubre motores, plugin, tareas, bloqueo, memoria, Claude Code,
decisiones, agentes, mejora, dataset, materiales y auditoría. GitHub Actions
ejecuta `npm run verify:all`.

### 14. Pruebas reales de host

- `npm run test:hermes-cli`: aprobada, 3/3 motores.
- `npm run test:claude-code-live`: aprobada, archivo verificado de forma independiente.
- `npm run test:hermes-autonomy-live`: aprobada; Hermes originó y supervisó una tarea real de Claude Code.
- `npm run verify:all-live`: aprobada de principio a fin.

Los verificadores permitieron hasta dos intentos. En la ejecución final,
Claude Code completó su tarea en el segundo intento después de una denegación
del comando auxiliar `xxd`; Hermes también completó la prueba autónoma en el
segundo intento. En ambos casos el éxito dependió del archivo comprobado por
el proceso verificador, no del texto declarado por el modelo.

### 15. Riesgos y límites

- Los ejecutores externos consumen llamadas reales y dependen del host.
- Un componente ausente no puede evaluarse externamente sin una fuente.
- La evaluación de materiales mide integridad estructural; la evaluación
  semántica exige criterios específicos del dominio.
- La seguridad sigue excluida.

### 16. Criterio final

Una capacidad solo se declara operativa con resultado observable, verificación
y evidencia persistible. `npm run verify:all` es la puerta reproducible;
`npm run verify:all-live` añade las integraciones reales del host.
