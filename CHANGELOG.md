# Changelog

Este documento registra cambios funcionales y de arquitectura relevantes de `ai-ecosystem`.

## Convenciones de versión

El repositorio y el plugin neurosimbólico tienen versiones distintas:

- `ai-ecosystem`: versión declarada en `package.json` (actualmente `0.1.0`).
- `neurosymbolic-integration`: versión declarada en `agents/hermes/plugins/neurosymbolic-integration/plugin.yaml` (actualmente `1.3.0`).

Las versiones del plugin descritas aquí corresponden a estados versionados del código. No implican por sí solas que exista un Git tag o una GitHub Release con el mismo número.

## [Unreleased]

- Se añadió compatibilidad explícita con **Hermes Progressive Tool Disclosure / Tool Search**: cuando `neurosymbolic_reasoning` queda diferida, el hook debe invocarla mediante el puente `tool_call` en lugar de intentar una llamada directa inexistente.
- La instrucción de formalización exige que `structured_context.required_capabilities` sea un array JSON de strings y que, para grafos, las aristas explícitas se copien en `relations` como pares origen/destino.
- La verificación live de Hermes se endurece para aislar el toolset `neurosymbolic` y exigir también `official_tool_observed`, demostrando que el puente terminó ejecutando la herramienta subyacente real.
- Se añadió una formalización local y determinista para lógica genérica escrita con sintaxis explícita (`Hechos: predicado(...). Regla: si predicado(...) entonces predicado(...)`), de modo que PyDatalog no dependa de que el modelo copie `facts` y `rules` en `structured_context`; la ruta solo reutiliza predicados y argumentos escritos literalmente en la consulta autoritativa y registra `local_formalization_applied`.
- Se añadió una regresión que reproduce el fallo live donde Tool Search entregó solo `required_capabilities=["logic"]` y verifica que la consulta explícita termine en `pydatalog` con `status=success`.
- Estos cambios permanecen sin nueva versión declarada hasta completar la verificación live local detector → puente Tool Search → `neurosymbolic_reasoning` → motor → salida fundamentada.
- Se estableció una política obligatoria de **no borrado**: agentes, scripts y automatizaciones no eliminan definitivamente contenido del proyecto.
- Se creó `docs/RETENTION_POLICY.md` como fuente principal de conservación y `vault/` como baúl versionado de cuarentena.
- Todo elemento retirado de su ubicación activa debe moverse al baúl, conservar su ruta de origen cuando sea posible y registrarse en `vault/INDEX.md`.
- La eliminación definitiva dentro del baúl queda reservada exclusivamente al propietario y se realiza manualmente.
- Los secretos, credenciales o datos sensibles quedan fuera del mecanismo automático de baúl y requieren intervención humana.
- Usar esta sección para cambios todavía no incorporados a una nueva versión declarada.
- Todo cambio que modifique capacidades, contratos de herramienta, detección, motores, compatibilidad o procedimiento de verificación debe registrarse aquí antes de subir la versión correspondiente.

## Plugin `neurosymbolic-integration` 1.3.0 — 2026-08-19

### Detección y activación

- Se reforzó la detección de cuándo Hermes debe utilizar razonamiento neurosimbólico mediante una matriz explícita de capacidades y evidencia de detección.
- Se ampliaron los casos detectables a grafos, lógica, restricciones, planificación, temporal, espacial, probabilístico/Bayesiano, causal, contrafactual, abductivo e inducción estadística.
- Se añadieron controles negativos para evitar activaciones por palabras aisladas o consultas ordinarias.
- Se permitió formalización estructurada de lógica genérica mediante `facts`, `rules` y `queries`, sin depender únicamente de dominios especiales como parentesco.

### Integración Hermes

- Se expuso explícitamente el toolset `neurosymbolic` en `platform_toolsets` y `known_plugin_toolsets` para CLI y Telegram.
- Se reforzó el contrato `neurosymbolic_reasoning` con schemas específicos por motor, para que Hermes conozca los campos esperados de cada formalización.
- El `request_id` debe provenir del `pre_llm_call`; un identificador desconocido se rechaza.
- El texto original almacenado por el runtime es autoritativo frente a cualquier `query` alterado durante la tool call.

### Trazabilidad y diagnóstico

- Se añadieron eventos de prueba diferenciados: `detector_decision`, `tool_required`, `tool_started`, `runtime_engine_inventory`, `engine_result_observed`, `tool_completed`, `official_tool_observed` y `output_replaced`.
- El runtime registra las versiones de paquetes y los motores/adaptadores visibles desde el mismo intérprete Python que ejecuta Hermes.
- Se añadió `scripts/verify_neurosymbolic_runtime.py`, que ejecuta operaciones reales sobre los motores extendidos y no se limita a comprobar imports.
- `scripts/verify_hermes_cli.sh` ahora exige la cadena completa detector → tool → motor → salida y ejecuta smoke tests desde el Python de Hermes.

### Verificación y CI

- Los tests incorporados durante la expansión neurosimbólica pasaron a formar parte de `npm test` / `test:core`.
- `verify:all` incluye la verificación del runtime neurosimbólico.
- GitHub Actions se amplió para ejecutarse también en pushes a ramas `fix/**`.
- Se añadieron pruebas para configuración del toolset, binding del `request_id`, lógica genérica, matriz de capacidades y activación/no activación.

### Correcciones

- Se evitó que el contexto estructurado pudiera borrar una señal previa de `human_review` o ambigüedad detectada desde el texto.
- Se cerró la posibilidad de ejecutar una tool call neurosimbólica con un `request_id` no creado por el detector.
- Se redujo el riesgo de falsos positivos donde el plugin estuviera habilitado pero la herramienta no fuera visible al modelo.

## Plugin `neurosymbolic-integration` 1.2.0 — 2026-08-19

### Metarrazonamiento e integración multi-motor

- Se añadió `MetaReasoner` para construir planes de razonamiento a partir de capacidades requeridas.
- Se conservó la ruta legacy NetworkX/PyDatalog/Z3 y se activó una ruta extendida solo para capacidades adicionales.
- Se añadió propagación de `transfer_payload` entre motores y validación fail-closed del plan completo.
- Se creó un contrato fundamentado extensible para publicar únicamente conclusiones respaldadas por resultados de motor.
- Se incorporó soporte de `structured_context` en la herramienta oficial de Hermes.
- Los motores opcionales pasaron a cargarse de forma lazy para que una dependencia ausente no derribe la ruta legacy.
- El antiguo `neurosymbolic_integrator.py` se convirtió en shim de compatibilidad hacia la integración vigente.

## Plugin `neurosymbolic-integration` 1.1.0 — 2026-08-19

### Base auditable del plugin

- Se consolidó la herramienta oficial `neurosymbolic_reasoning` y los hooks `pre_llm_call`, `post_tool_call` y `transform_llm_output`.
- Se preservó el mensaje original del usuario durante la ejecución de la herramienta.
- Se añadió reemplazo de la respuesta libre del LLM por un resultado fundamentado cuando el turno exige razonamiento neurosimbólico.
- Se mantuvo fail-closed cuando Hermes no ejecuta la herramienta requerida.
- La integración legacy quedó centrada en `ProblemExtractor → NeurosymbolicCoordinator → NetworkX/PyDatalog/Z3`.

## Expansión de motores previa a 1.2.0 — 2026-08-19

Estos cambios prepararon las capacidades que después se integraron mediante metarrazonamiento:

- Contratos extensibles: `ReasoningCapability`, `ReasoningProfile`, `EngineResult`, `EngineAdapter` y `EngineRegistry`.
- Planificación clásica: Unified Planning + Pyperplan.
- Razonamiento temporal: Z3.
- Razonamiento espacial: Shapely + PyProj.
- Probabilístico/Bayesiano: pgmpy.
- Causal y contrafactual: DoWhy.
- Abducción: Clingo/ASP.
- Inducción estadística: scikit-learn.
- Se mantuvo `analogical` como capacidad reservada, sin afirmar soporte operativo mientras no exista un motor analógico validado.

## Base inicial del repositorio — 2026-08-17

- Commit inicial de `ai-ecosystem` (`e3a6b6e`).
- Centralización de configuración personalizada de Hermes (`79ff47f`).
- Corrección del orden de bindings de PyDatalog (`71276d8`).
- Endurecimiento del routing neurosimbólico, manejo de ambigüedad y modo combinado (`6528328`).

## Política de mantenimiento

Al modificar el sistema:

1. Registrar primero el cambio en `[Unreleased]` si altera comportamiento observable o arquitectura.
2. Al subir una versión de `plugin.yaml`, mover los cambios correspondientes a una sección con versión y fecha.
3. No declarar como operativo un motor solo porque su dependencia esté instalada; debe existir una prueba que ejecute una operación real.
4. No declarar una integración Hermes como verificada solo por imports o unit tests; la verificación live debe demostrar detector → tool call → motor → salida fundamentada.
5. Mantener separados los números de versión del repositorio y del plugin.
6. No eliminar definitivamente contenido del proyecto mediante agentes o automatizaciones; trasladarlo a `vault/` según `docs/RETENTION_POLICY.md`.
