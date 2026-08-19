# Índice maestro de documentación

> Fuente principal para localizar documentación sin cargarla toda. Revisado el
> 2026-08-19 contra `fix/core-verification-and-orchestration`. Las rutas son
> relativas a la raíz. Estado permitido: **Vigente**, **Parcial**,
> **Histórico**, **Reemplazado** o **Pendiente**.

## Uso contextual obligatorio

1. Identifique el área que cambiará.
2. Consulte en este índice las fuentes principales de esa área.
3. Abra solo esas fuentes y los complementos necesarios.
4. Realice y verifique el cambio.
5. Aplique el criterio «Cuándo actualizarlo» de las entradas afectadas.
6. Actualice este índice si creó, movió, reemplazó o archivó documentación.

## Documentación general y arquitectura

| Documento | Ruta | Descripción | Área relacionada | Cuándo consultarlo | Cuándo actualizarlo | Fuente principal | Estado | Sustituye o es sustituido por | Última verificación |
|---|---|---|---|---|---|---|---|---|---|
| Operación general | `README.md` | Capacidades, instalación y pruebas reales | repositorio | inicio, instalación o límites | comandos, capacidades o requisitos | Sí | Vigente | sustituye guías operativas antiguas | 2026-08-18 / tool neurosimbólica |
| Arquitectura vigente | `ARCHITECTURE.md` | Componentes reales y estados | arquitectura | diseño o cambio estructural | componentes, flujos o integraciones | Sí | Vigente | sustituye `SYSTEM_BLUEPRINT.md` | 2026-08-18 / tool neurosimbólica |
| Instrucciones centrales | `CLAUDE.md` | Reglas operativas para agentes | flujo de trabajo | antes de cualquier cambio | políticas, comandos o finalización | Sí | Vigente | sustituye instrucciones dispersas | 2026-08-18 / tool neurosimbólica |
| Entrada de documentación | `docs/README.md` | Enlaces a fuentes principales | documentación | al explorar `docs/` | altas o cambios de fuentes | No | Vigente | sustituye README de calculadora | 2026-08-19 / changelog enlazado |
| Índice maestro | `docs/DOCUMENTATION_INDEX.md` | Inventario, estado y reglas de actualización | documentación | antes y después de una tarea | cualquier documento creado, movido o archivado | Sí | Vigente | sustituye catálogos dispersos | 2026-08-19 / changelog registrado |
| Historial de cambios | `CHANGELOG.md` | Evolución funcional, arquitectura y versiones del repositorio y plugin neurosimbólico | versiones, documentación | revisar qué cambió entre versiones o preparar una nueva | cambios funcionales, contratos, motores, verificación o versión declarada | Sí | Vigente | complementa Git y manifiestos de versión | 2026-08-19 / plugin 1.3.0 |
| Blueprint auditado | `SYSTEM_BLUEPRINT.md` | Instantánea de arquitectura de 2025 | arquitectura | investigación histórica | no actualizar; crear evidencia vigente aparte | No | Reemplazado | sustituido por `ARCHITECTURE.md` | 2026-08-17 / rama de verificación |
| Árbol del repositorio | `STRUCTURE.md` | Instantánea generada y voluminosa | estructura | rastreo histórico excepcional | regenerar como artefacto nuevo, no editar como fuente | No | Histórico | sustituido por Git y este índice | 2026-08-17 / rama de verificación |
| Consolidación fase 1 | `phase1_consolidation_report.md` | Resultado puntual de inventario | razonamiento | comparar evolución inicial | no actualizar | No | Histórico | sustituido por arquitectura e informe de verificación | 2026-08-17 / rama de verificación |
| Planes Claude | `.claude/plans/` | Tres propuestas de trabajo no desplegadas | planificación | rastrear decisiones propuestas | solo al corregir su estado histórico | No | Histórico | complementa el historial | 2026-08-17 / rama de verificación |
| Especificaciones OpenSpec | `.openspec/specs/` | Especificaciones de ejemplo o legado | especificaciones | trabajar en esos prototipos | al cambiar el prototipo asociado | No | Parcial | sin sucesor demostrado | 2026-08-17 / rama de verificación |

## Agentes, miniagentes, prompts, configuraciones y skills

| Documento | Ruta | Descripción | Área relacionada | Cuándo consultarlo | Cuándo actualizarlo | Fuente principal | Estado | Sustituye o es sustituido por | Última verificación |
|---|---|---|---|---|---|---|---|---|---|
| Instrucción Claude local | `.claude/CLAUDE.md` | Instrucciones complementarias del cliente | Claude | sesiones del cliente | cambios de reglas centrales | No | Parcial | subordinado a `CLAUDE.md` | 2026-08-17 / rama de verificación |
| Configuración Claude | `.claude/settings.json` | Hooks y preferencias sin secretos | Claude | modificar hooks o entorno | cualquier cambio de hook | Sí | Vigente | complementa `CLAUDE.md` | 2026-08-17 / rama de verificación |
| Configuración MCP local | `.claude/.mcp.json` | Servidores MCP para Claude | integraciones | cambiar servidores Claude | altas, bajas o comandos MCP | Sí | Vigente | complementa `.mcp.json` | 2026-08-17 / rama de verificación |
| Configuración MCP raíz | `.mcp.json` | Servidores MCP del repositorio | integraciones | cambiar servidores globales | altas, bajas o comandos MCP | Sí | Vigente | complementa `.claude/.mcp.json` | 2026-08-17 / rama de verificación |
| Instrucciones Hermes | `agents/hermes/SOUL.md` | Conducta central del agente Hermes | Hermes | modificar comportamiento Hermes | políticas o flujo Hermes | Sí | Vigente | complementa `CLAUDE.md` | 2026-08-18 / tool neurosimbólica |
| Configuración Hermes | `agents/hermes/config/config.yaml` | Configuración versionada de Hermes | Hermes | cambiar runtime o plugins | claves o componentes configurados | Sí | Parcial | complementa SOUL y plugin | 2026-08-17 / rama de verificación |
| Manifiesto plugin | `agents/hermes/plugins/neurosymbolic-integration/plugin.yaml` | Tool oficial, hooks y metadatos del plugin | Hermes, razonamiento | cambiar integración CLI | tools, hooks, permisos o módulo | Sí | Vigente | complementa arquitectura | 2026-08-19 / plugin 1.3.0 |
| Caveman | `.claude/skills/caveman/SKILL.md` | Guía de razonamiento simplificado | skill Claude | explicación paso a paso | conducta del skill | Sí | Vigente | independiente | 2026-08-17 / rama de verificación |
| Codebase Memory | `.claude/skills/codebase-memory/SKILL.md` | Uso de CBM desde Claude | skill Claude, memoria | búsqueda estructural | comandos CBM | Sí | Parcial | complementa guías CBM | 2026-08-17 / rama de verificación |
| Análisis cuantitativo | `agents/hermes/skills/main/advanced-quant-analysis/SKILL.md` | Instrucciones cuantitativas | skill Hermes | tareas cuantitativas | interfaz o implementación asociada | No | Parcial | sin ejecutor demostrado | 2026-08-17 / rama de verificación |
| Verificación de datos | `agents/hermes/skills/main/data-verifier/SKILL.md` | Procedimiento de verificación externa | skill Hermes | validar datos | fuentes o herramientas | No | Parcial | sin ejecutor demostrado | 2026-08-17 / rama de verificación |
| Koopman EDMD | `agents/hermes/skills/main/koopman-edmd-dynamic-modeler/SKILL.md` | Diseño de modelador EDMD | skill Hermes | modelado de series | código o dependencias EDMD | No | Parcial | sin ejecutor demostrado | 2026-08-17 / rama de verificación |
| Orchestrator main legado | `agents/hermes/skills/main/orchestrator-main/SKILL.md` | Diseño maestro anterior | orquestación | rastreo histórico | no presentar comandos como reales | No | Reemplazado | sustituido por `skilled/orchestration/` | 2026-08-17 / rama de verificación |
| Referencias del orquestador | `agents/hermes/skills/main/orchestrator-main/references/` | Siete guías de migración, CBM y parches | orquestación | investigar decisiones anteriores | solo corregir estado o sucesor | No | Histórico | sustituidas por arquitectura y catálogo | 2026-08-17 / rama de verificación |
| Categorizador | `agents/hermes/skills/main/project-categorizer/SKILL.md` | Reglas propuestas de clasificación | agentes | categorizar proyectos | reglas o almacén objetivo | No | Parcial | sin ejecutor demostrado | 2026-08-17 / rama de verificación |
| Autoauditoría | `agents/hermes/skills/main/self-audit/SKILL.md` | Criterios de auditoría | verificación | finalizar cambios | pruebas o política documental | No | Parcial | `verify:all` es fuente ejecutable | 2026-08-17 / rama de verificación |
| Directivas del sistema | `agents/hermes/skills/main/system-directives/SKILL.md` | Reglas históricas de delegación | gobernanza | revisar decisiones antiguas | cambios de política | No | Reemplazado | sustituido por `CLAUDE.md` y SOUL | 2026-08-17 / rama de verificación |
| Razonamiento neurosimbólico | `agents/hermes/skills/mlops/neurosymbolic-reasoning/SKILL.md` | Activación, tool y motores | razonamiento | cambiar detección o motores | tool, router, motores o umbrales | No | Vigente | complementa arquitectura | 2026-08-18 / tool neurosimbólica |
| Referencias neurosimbólicas | `agents/hermes/skills/mlops/neurosymbolic-reasoning/references/` | Arquitectura y patrones detallados | razonamiento | implementar o validar motores | contratos o patrones simbólicos | No | Vigente | complementa el skill | 2026-08-18 / tool neurosimbólica |
| Delegation handler | `agents/hermes/skills/orchestrator/delegation-handler/SKILL.md` | Diseño de delegación especializada | agentes | estudiar delegación | política o implementación asociada | No | Parcial | orquestador Python es vigente | 2026-08-17 / rama de verificación |
| Integrador de razonamiento | `agents/hermes/skills/reasoning/reasoning-integrator/SKILL.md` | Coordinación de motores | razonamiento | modificar integración | API de motores | No | Vigente | complementa arquitectura | 2026-08-17 / rama de verificación |
| Router actualizado | `agents/hermes/skills/reasoning/semantic-router-updated/SKILL.md` | Especificación v2 del router | razonamiento | revisar prioridad humana | clasificación o tests | No | Parcial | complementa router vigente | 2026-08-17 / rama de verificación |
| Router semántico | `agents/hermes/skills/reasoning/semantic-router/SKILL.md` | Semántica de clasificación | razonamiento | cambiar clasificación | router o umbrales | No | Vigente | fuente de skill actual | 2026-08-17 / rama de verificación |
| Referencias del router | `agents/hermes/skills/reasoning/semantic-router/references/` | Instalación y lógica detallada | razonamiento | cambiar router | interfaz o despliegue | No | Parcial | complementa el skill | 2026-08-17 / rama de verificación |
| Blueprint skill | `agents/hermes/skills/software-development/ai-ecosystem-blueprint/SKILL.md` | Método para auditar arquitectura | documentación | auditorías integrales | política documental | No | Vigente | usa este índice | 2026-08-17 / rama de verificación |
| Router simbólico Hermes | `agents/hermes/skills/symbolic-reasoning-router/SKILL.md` | Reglas compactas de activación | razonamiento | ajustar activación | umbrales o router | No | Parcial | complementa router principal | 2026-08-17 / rama de verificación |
| Integración simbólica | `skills/reasoning/hermes-symbolic-integration/SKILL.md` | Instalación y uso de la tool del plugin | Hermes, razonamiento | integrar plugin | rutas, comandos, tools o hooks | No | Vigente | complementa README | 2026-08-18 / tool neurosimbólica |
| Prompt histórico | `patches/SYSTEM_PROMPT_REFERENCE.md` | Copia de instrucciones anteriores | prompts | recuperación o comparación | no actualizar como fuente activa | No | Histórico | sustituido por `CLAUDE.md` y SOUL | 2026-08-17 / rama de verificación |

## Memoria, conocimiento, servicios y scripts

| Documento | Ruta | Descripción | Área relacionada | Cuándo consultarlo | Cuándo actualizarlo | Fuente principal | Estado | Sustituye o es sustituido por | Última verificación |
|---|---|---|---|---|---|---|---|---|---|
| Formato de memoria | `sharememory/hermes_memory/hermes_memory_format.md` | Esquema documental de memoria | memoria | cambiar serialización | esquema o validación | No | Parcial | código Python es fuente ejecutable | 2026-08-17 / rama de verificación |
| Catálogo legado de skills | `sharememory/hermes_memory/hermes_skills_catalog.md` | Inventario anterior | agentes, memoria | rastreo histórico | no actualizar | No | Reemplazado | sustituido por este índice | 2026-08-17 / rama de verificación |
| Broker Obsidian legado | `KNOWLEDGE_BROKER.md` | Manual de un broker anterior | memoria | rastreo de integración Obsidian | no actualizar | No | Reemplazado | sustituido por README y código vigente | 2026-08-17 / rama de verificación |
| Guía OKF | `docs/WIKI_README.md` | Manual de wiki y Obsidian | memoria | investigación histórica | no actualizar como operativo | No | Histórico | sin sucesor operativo equivalente | 2026-08-17 / rama de verificación |
| Guía CBM | `docs/CBM_INTEGRATION.md` | Comandos CBM y afirmaciones de host | memoria | usar scripts CBM con cautela | comandos en package.json | No | Parcial | complementada por package.json | 2026-08-17 / rama de verificación |
| CBM completa | `docs/CBM_INTEGRATION_FULL.md` | Informe de host anterior | memoria | rastreo histórico | no actualizar | No | Reemplazado | sustituido por guía CBM e índice | 2026-08-17 / rama de verificación |
| Resumen CBM | `docs/integration_summary.md` | Resultado puntual de hooks | memoria | rastreo histórico | no actualizar | No | Reemplazado | sustituido por guía CBM e índice | 2026-08-17 / rama de verificación |
| Configuración de razonamiento | `skilled/reasoning/config.yaml` | Umbrales y políticas del router | razonamiento | cambiar selección | claves o defaults | Sí | Vigente | complementa los skills | 2026-08-17 / rama de verificación |
| Políticas | `src/reasoning/policies/safety.yaml` | Reglas declarativas de seguridad | razonamiento | modificar políticas | reglas o consumidor | No | Parcial | sin cobertura integral de seguridad | 2026-08-17 / rama de verificación |
| Scripts operativos | `scripts/` | Verificación, datasets, corpus y utilidades | operación | ejecutar o modificar automatización | interfaces, flags o salidas | Sí | Vigente | documentados por README | 2026-08-18 / verificador tool calls |
| Servicio de conocimiento | `knowledge-service/` | Entrada de ingestión | conocimiento | operar ingestión | dependencias o rutas | Sí | Parcial | complementa memoria | 2026-08-17 / rama de verificación |
| Taskhero | `src/taskhero/README.md` | Manual de subproyecto Node | subproyecto | trabajar en taskhero | scripts o estructura propia | Sí | Parcial | independiente | 2026-08-17 / rama de verificación |

## Pruebas, parches, migraciones e historia

| Documento | Ruta | Descripción | Área relacionada | Cuándo consultarlo | Cuándo actualizarlo | Fuente principal | Estado | Sustituye o es sustituido por | Última verificación |
|---|---|---|---|---|---|---|---|---|---|
| Informe de verificación | `docs/verification-report.md` | Evidencia reproducible y real | pruebas | evaluar estado comprobado | cambios de suite o ejecución real | Sí | Vigente | sustituye tablas de estado manuales | 2026-08-18 / 87 pruebas |
| Auditoría externa | `docs/audits/external-components.json` | Resultado sobre componentes externos | auditoría | cambiar inventario externo | aparece fuente canónica | Sí | Vigente | complementa informe | 2026-08-17 / rama de verificación |
| Catálogo de parches | `docs/PATCH_CATALOG.md` | Estado, evidencia y riesgos de parches | parches | aplicar, revisar o crear parche | cualquier artefacto bajo `patches/` | Sí | Vigente | sustituye índices antiguos | 2026-08-17 / rama de verificación |
| Índice anterior de parches | `patches/PATCHES_INDEX.md` | Bitácora original | parches | rastreo histórico | no actualizar | No | Reemplazado | sustituido por catálogo vigente | 2026-08-17 / rama de verificación |
| Parte general anterior | `patches/PARTE_GENERAL.md` | Guía original de estructura | parches | rastreo histórico | no actualizar | No | Reemplazado | sustituido por catálogo vigente | 2026-08-17 / rama de verificación |
| Parche Notex | `patches/2026-08-02_notex_audio_only_imports/` | Informe y diff cuyo objetivo falta | parches | investigación histórica | si reaparece una fuente canónica | No | Histórico | catalogado como obsoleto | 2026-08-17 / rama de verificación |
| Parche Kùzu | `patches/2026-08-04_knowledge_broker_db_path/` | Informe, decisiones, diff y prueba | parches | revisar ingestión Kùzu | ruta o comportamiento de ingestión | No | Vigente | complementa catálogo | 2026-08-17 / rama de verificación |
| Plantilla de parches | `patches/plantillas/` | Plantilla documental | parches | crear registro futuro | campos o criterio de evidencia | No | Parcial | complementa catálogo | 2026-08-17 / rama de verificación |
| Respaldo importado | `patches/2026-08-17_auto_copied_files/` | Copia automática masiva | respaldo | recuperación excepcional | no actualizar | No | Histórico | solo respaldo | 2026-08-17 / rama de verificación |
| Historial de respaldos | `patches/backups/history/` | Instantáneas anteriores | respaldo | recuperación excepcional | no actualizar | No | Histórico | solo respaldo | 2026-08-17 / rama de verificación |
| Tutorial simbólico | `documentation/tutorial_instalacion_hermes_simbolico.md` | Instalación antigua | Hermes | rastreo histórico | no actualizar como operativo | No | Reemplazado | sustituido por README | 2026-08-17 / rama de verificación |
| Procedimientos de dominio | `procedures/` | Guías médicas, pruebas y resúmenes antiguos | procedimientos | solo si una tarea cita uno | al verificar individualmente contra una fuente | No | Histórico | no son manual operativo central | 2026-08-17 / rama de verificación |
| Staging documental | `staging/` | Ejemplos y entradas no promovidas | ingestión | probar procesamiento | al cambiar fixtures | No | Pendiente | no es documentación publicada | 2026-08-17 / rama de verificación |

## Jerarquía de fuentes

- Arquitectura: `ARCHITECTURE.md`.
- Operación y comandos: `README.md`, `package.json` y scripts reales.
- Historial y versiones: `CHANGELOG.md`.
- Conducta de agentes: `CLAUDE.md` y `agents/hermes/SOUL.md`.
- Estado probado: `docs/verification-report.md` y la suite.
- Parches: `docs/PATCH_CATALOG.md`.
- Detalle de una skill: su `SKILL.md`, limitado por el estado que figura aquí.

Una fuente complementaria nunca debe elevar por sí sola una capacidad parcial
o histórica a operativa.