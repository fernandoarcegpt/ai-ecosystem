# Informe de verificación integral (sin seguridad)

Fecha de corte: 2026-08-18.

## Resultado ejecutivo

El núcleo reproducible pasó **87 pruebas** e integra razonamiento neurosimbólico, tareas persistentes,
agentes por rol, ejecución mediante Claude Code, memoria versionable, mejora
continua, dataset y evaluación de materiales extensos. Las pruebas reales ya
aportadas en el host verificaron la integración anterior de Hermes CLI con
NetworkX/Z3/PyDatalog y Claude Code mediante `TaskRouter`. Tras migrar a una
tool call oficial, la suite local está verificada y la nueva prueba CLI real
queda pendiente en el host. La ejecución conjunta histórica
`npm run verify:all-live` terminó correctamente antes de esta migración.

La seguridad permanece fuera de alcance por indicación del propietario. Los
componentes externos que no existen en el árbol se registran como `not_present`;
no se inventa una evaluación sin URL o paquete inequívoco.

## Matriz consolidada

| Parte | Estado y evidencia |
|---|---|
| NetworkX, PyDatalog y Z3 | Verificado por suite; revalidación de tool call en Hermes CLI pendiente |
| Composición NetworkX → PyDatalog → Z3/Optimize | Verificada con transferencia explícita de hechos y restricciones |
| Plan de Transferencias Documentales 2027 | Regresión E2E permanente; extracción, tres motores, alcance y soporte de afirmaciones |
| Ciclos, contradicciones, SAT/UNSAT e inferencia transitiva | Verificado |
| Activación y no activación del razonador | Verificado |
| Persistencia y dependencias de tareas | Verificado |
| Bloqueo por falta de ejecutor | Verificado |
| Continuación de trabajo independiente | Verificado |
| Reanudación manual y automática | Verificado |
| Persistencia de decisiones humanas | Verificado |
| Captura y recuperación de resultados en memoria | Verificado |
| `npm test` y GitHub Actions | Verificado localmente: 87 pruebas aprobadas; CI se valida en el PR |
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

NetworkX, Z3 y PyDatalog se seleccionan y ejecutan automáticamente desde la
herramienta oficial `neurosymbolic_reasoning`. `pre_llm_call` solo detecta y
requiere la llamada; no ejecuta motores ocultos. En modo
`combined`, NetworkX aporta relaciones alcanzables a PyDatalog; sus hechos
derivados se convierten en restricciones para Z3/Optimize y la coordinación
solo se declara exitosa si pasan todos los motores requeridos. La regresión
del Plan de Transferencias 2027 verifica `blocked(RRHH)`,
`requires_correction(Contabilidad)`, capacidad, objetivo institucional e
inyección anidada. El contrato fundamentado limita el alcance, declara el
supuesto de elegibilidad, resuelve el soporte de cada afirmación y reemplaza
la redacción libre. La nueva prueba real `test:hermes-cli` exige tool calls
contabilizadas; su revalidación en el host queda pendiente.

### 11. Mejora continua

Cada ejecución añade su informe al historial. Fallos o bloqueos repetidos
generan propuestas con evidencia, métrica y riesgo. Las regresiones de guardas
impiden aceptar una mejora.

### 12. Dataset

`datasets/evaluation` contiene 72 casos sintéticos: 62 de entrenamiento, 6 de
validación y 4 de evaluación. No contiene datos de usuario ni autoriza
fine-tuning. Su reconstrucción exacta forma parte de `verify:all`.

### 13. Pruebas

`npm test` cubre 87 pruebas de motores, herramienta y hooks del plugin, tareas, bloqueo, memoria, Claude Code,
decisiones, agentes, mejora, dataset, materiales y auditoría. GitHub Actions
ejecuta `npm run verify:all`.

### 14. Pruebas reales de host

- `npm run test:hermes-cli`: la versión anterior fue aprobada con 3/3 motores;
  la versión actual exige una tool call oficial y está pendiente de revalidar
  en el host con Hermes.
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

## Revisión documental integral

La revisión del 2026-08-17 localizó 355 archivos documentales relevantes. El
índice maestro los representa mediante 63 entradas exactas o colecciones
delimitadas y define una fuente principal por área. El catálogo registra ocho
parches, migraciones o colecciones de respaldo con evidencia, estado y riesgo.

Se actualizaron las fuentes operativas de arquitectura, instalación,
instrucciones de agentes, validación, memoria e ingestión. Los manuales de CBM,
los informes de consolidación y las bitácoras antiguas quedaron identificados
como parciales, históricos o reemplazados. Las instrucciones centrales y los
skills pertinentes remiten al índice y cargan documentación de forma
contextual.

La validación comprueba rutas inventariadas, cobertura de documentos nuevos,
duplicados, campos obligatorios, enlaces internos de fuentes vigentes,
catálogo de parches, comandos npm documentados y rutas absolutas en componentes
críticos. Se ejecuta desde `npm test`, `npm run verify:all` y GitHub Actions.

No se hizo una evaluación semántica individual de cada archivo dentro de
`patches/backups/history/` ni de `patches/2026-08-17_auto_copied_files/`: son
copias masivas y duplicadas, inventariadas como colecciones de respaldo. Los
archivos históricos que contienen ejemplos de credenciales o detalles privados
del host se conservaron sin reescritura y se clasificaron desde el índice. Las
pruebas reales de seguridad permanecen fuera de alcance por indicación del
propietario.
