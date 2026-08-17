# Informe de verificación integral (sin seguridad)

Fecha de corte: 2026-08-17.

## Resultado ejecutivo

La suite reproducible pasó **64 pruebas**. Se corrigieron la reanudación automática tras aprobación humana, los reportes incompletos de bloqueo, las rutas absolutas del plugin, la colisión de esquemas de memoria y enlaces rotos de skills. También se añadieron un árbol operativo, un adaptador opt-in de Claude Code, exportación versionable de conocimiento validado, análisis de mejora y construcción controlada de datasets de evaluación.

No se declara verificado en vivo aquello que requiere los binarios, cuentas o servicios del host. La seguridad quedó fuera por indicación del propietario.

## Estado de la matriz solicitada

| Parte | Estado con evidencia |
|---|---|
| NetworkX, PyDatalog y Z3 | Verificado por suite |
| Ciclos, contradicciones, SAT/UNSAT e inferencia transitiva | Verificado por suite |
| Activación y no activación del razonador | Verificado por suite |
| Persistencia, dependencias y continuación independiente | Verificado por suite |
| Bloqueo por falta de ejecutor y reanudación manual | Verificado por suite |
| Persistencia de decisiones humanas y resultados | Verificado por suite |
| `npm test` y GitHub Actions | Verificado previamente; selección ampliada a 64 pruebas |
| Informe con evidencia, alternativas, riesgos y siguiente paso | Corregido y verificado |
| Reanudación automática tras aprobación y de dependientes | Corregido y verificado |
| Hermes `pre_llm_call` con los tres motores | Contrato verificado; prueba CLI real preparada |
| Hermes CLI extremo a extremo | Pendiente ejecutar `npm run test:hermes-cli` en el host Hermes |
| Autonomía por tareas | Verificada dentro de `TaskRouter`; agentes externos en vivo, parcial |
| Claude Code autónomo | Adaptador integrado y probado con doble; ejecución real pendiente |
| Árbol de decisiones generales | Implementado y verificado |
| Arquitectura completa de agentes/miniagentes | Parcial; no existe un enjambre multiproceso completo en este repo |
| OpenClaw, Proyecto Japonés, Hermes Workspace y Scrubs | No existen en el árbol inspeccionado; no hubo fuente inequívoca que evaluar |
| Mejora continua | Núcleo de análisis/medición implementado; automatización externa, parcial |
| Estrategia y construcción de dataset | Constructor y barrera de fine-tuning implementados; dataset real aún vacío |
| Libros y materiales voluminosos | Inventario realizado; no hay PDF/EPUB/MOBI, no se eliminó nada |
| Memoria versionable | Exportación validada implementada; memoria runtime separada |
| Prompts, skills y servicios | Rutas críticas corregidas; revisión histórica completa aún parcial |
| Pruebas reales de seguridad | Excluidas por indicación del propietario |
| Informe con los 16 entregables | Este documento |

## Los 16 entregables

### 1. Arquitectura real encontrada

El árbol operativo contiene un agente Hermes, un plugin neurosimbólico, skills de documentación, `TaskRouter`, `HumanGate`, `KnowledgeBroker` y los tres motores simbólicos. No se encontraron procesos activos de miniagentes ni un orquestador ejecutable con el nombre histórico `orchestrator-main`.

### 2. Componentes existentes reutilizados

Se conservaron el coordinador neurosimbólico, los wrappers de NetworkX/Z3/PyDatalog, el router semántico, `HumanGate`, `KnowledgeBroker`, el plugin Hermes y el flujo de CI. No se creó una memoria ni un motor paralelo.

### 3. Componentes nuevos implementados

- Árbol auditable `operational_decision.py`.
- Adaptador `claude_code_executor.py`.
- Prueba contractual del hook y prueba Hermes CLI.
- Analizador de mejora y constructor de datasets de evaluación.
- Exportación estable de conocimiento validado.

### 4. Cambios transversales

`TaskRouter` acepta ejecutores persistentes, sincroniza aprobaciones y libera dependientes. El plugin ya no supone `/home/fernando`. Los skills apuntan a referencias reales. `run_ingest.sh` resuelve el repositorio y `.venv` de forma portable. `CLAUDE.md` dejó de presentar comandos inexistentes como operativos.

### 5. OpenClaw, Proyecto Japonés, Hermes Workspace y Scrubs

No hay rutas, módulos ni configuraciones de esos nombres. Por ello no se copió ni integró software por similitud de nombre. Evaluarlos fuera del repo requiere una URL o repositorio inequívoco.

### 6. Autonomía por tareas

El objetivo se descompone, prioriza, enruta, ejecuta, verifica y persiste. Las tareas listas siguen avanzando aunque otra quede bloqueada. Los ejecutores se registran por agente o tipo; Claude Code puede ocupar `builder` de forma opt-in.

### 7. Bloqueo humano

Cada bloqueo contiene tarea, estado alcanzado, evidencia, impedimento, alternativas, riesgos, acción humana y siguiente paso automático. `HumanGate` persiste la decisión; una aprobación repropone la tarea y una denegación la mantiene bloqueada. Los bloqueos derivados no duplican revisiones.

### 8. Controles de seguridad

No se modificaron ni verificaron en esta fase, conforme a la exclusión expresa.

### 9. Memoria

`KnowledgeBroker` conserva memoria operativa; `WorkMemoryRecorder` acepta solo resultados verificados. `BasicMemory` quedó aislada en `basic_memory.json`. `export-validated` genera un snapshot estable únicamente de conocimiento validado y con procedencia/confianza suficiente.

### 10. Capacidad neurosimbólica

`ProblemExtractor` formaliza la tarea y el coordinador selecciona NetworkX, Z3, PyDatalog o combinación. El hook inyecta solo resultados exitosos. El script E2E prueba los tres motores mediante el comando oficial `hermes chat -q`.

### 11. Mejora continua

`ContinuousImprovementAgent` convierte bloqueos o fallos repetidos en mejoras con evidencia, métrica y riesgo. `evaluate_change` rechaza una mejora si una métrica guardia retrocede. Falta conectarlo a una automatización recurrente.

### 12. Dataset y fine-tuning

El constructor exige autorización, procedencia, salida esperada y criterio de éxito; asigna splits deterministas y produce JSONL. Fine-tuning se rechaza sin un mínimo de casos y una ganancia comparativa medible sobre la alternativa de prompt/herramientas. No se entrenó ningún modelo.

### 13. Pruebas ejecutadas

La selección de `package.json` pasó 64/64 en un entorno limpio con `requirements-test.txt`. Incluye motores, integración, tareas, memoria, hook, Claude Code simulado, árbol operativo, mejora y datasets.

### 14. Pruebas pendientes

- `npm run test:hermes-cli` en el host con Hermes habilitado.
- Claude Code real con autenticación y un repositorio de prueba reversible.
- Agentes/miniagentes multiproceso y servicios externos reales.
- Seguridad, expresamente excluida.

### 15. Riesgos identificados

- Skills y respaldos históricos pueden seguir describiendo capacidades viejas.
- `patches/` ocupa ~11 MB y concentra 1271 de 1626 archivos rastreados.
- `STRUCTURE.md` ocupa ~4.5 MB y `.openspec` contiene 182 archivos generados.
- La prueba Hermes real consume una llamada de modelo por motor.

### 16. Próximas acciones priorizadas

Automáticas y reversibles:

1. Ejecutar la suite ampliada en CI.
2. Ejecutar la prueba Hermes CLI y adjuntar su salida.
3. Poblar un pequeño dataset autorizado de evaluación antes de considerar entrenamiento.
4. Conectar reportes de tarea al analizador de mejora en modo informe.

Requieren decisión humana:

1. Identificar con URL exacta OpenClaw, Proyecto Japonés, Workspace y Scrubs.
2. Autorizar una prueba real de Claude Code con presupuesto y repositorio.
3. Decidir si `patches/`, `.openspec` y `STRUCTURE.md` se archivan o conservan.
4. Abrir una fase separada para seguridad.
