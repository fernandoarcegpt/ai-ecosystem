# Instrucciones operativas del repositorio

Este archivo describe únicamente capacidades que existen en el árbol actual.

## Política obligatoria de no borrado

**Ningún agente, script o automatización debe eliminar definitivamente archivos o directorios del proyecto.**

Cuando un elemento deje de ser necesario en su ubicación activa, debe retirarse mediante traslado a `vault/` conforme a `docs/RETENTION_POLICY.md`, preservando cuando sea posible su ruta original y registrando el movimiento en `vault/INDEX.md`.

La eliminación definitiva dentro de `vault/` queda reservada exclusivamente al propietario del repositorio y se realiza manualmente. Los agentes no deben ejecutar `rm`, `git rm`, APIs de borrado ni purgas automáticas sobre contenido del proyecto o del baúl.

Si el elemento contiene secretos, credenciales o datos sensibles, no debe copiarse automáticamente al baúl: el flujo debe bloquearse y solicitar intervención humana.

## Flujo de trabajo

1. Identificar el área afectada y consultar `docs/DOCUMENTATION_INDEX.md`.
2. Abrir solo las fuentes que el índice asigna a esa área; no cargar todo el inventario.
3. Inspeccionar el código y el estado de Git antes de modificar.
4. Clasificar la solicitud con `reasoning.operational_decision` cuando requiera enrutamiento explícito.
5. Usar `TaskRouter` para objetivos persistentes, dependencias y bloqueos.
6. Ejecutar y verificar el cambio antes de declararlo completo.
7. Revisar en el índice qué documentos deben actualizarse por el cambio. Si se crea, mueve, reemplaza o archiva documentación, actualizar también el índice.
8. Si un archivo o directorio debe retirarse de su ubicación activa, moverlo a `vault/` y registrarlo; nunca destruirlo automáticamente.
9. Registrar en `KnowledgeBroker` solo resultados que hayan sido verificados.
10. Para autonomía iniciada por Hermes, aceptar únicamente el prefijo explícito
   `/orchestrate` y exigir `HERMES_AUTONOMY_ENABLED=1`.
11. Alimentar el ciclo de mejora con informes persistidos; una propuesta no es
   evidencia de mejora hasta superar métricas y guardas.

No se deben tratar los nombres históricos `orchestrator-main`, `general-planning` ni `@hermes/cli` como comandos instalados: en este repositorio algunos sobreviven únicamente como documentación de skills.

## Comandos reales

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
npm test
npm run verify:all
```

Prueba de integración con una instalación real de Hermes:

```bash
npm run test:hermes-cli
npm run test:claude-code-live
npm run test:hermes-autonomy-live
```

El script exige que `neurosymbolic-integration` esté descubierto y habilitado
por Hermes. Ejecuta NetworkX, Z3 y PyDatalog mediante `hermes chat -q`, exige
una llamada oficial a `neurosymbolic_reasoning` y comprueba que un mensaje
ordinario conserve cero llamadas.

## Componentes operativos

- `skilled/reasoning/task_router.py`: tareas, dependencias, ejecutores, verificación, persistencia, bloqueo y reanudación.
- `skilled/reasoning/operational_decision.py`: árbol central de decisión.
- `skilled/orchestration`: agentes, ejecución multi-etapa, puente Hermes e historial.
- `skilled/reasoning/claude_code_executor.py`: adaptador opt-in de Claude Code.
- `skilled/reasoning/neuro_symbolic_engine.py`: NetworkX, Z3 y PyDatalog.
- `agents/hermes/plugins/neurosymbolic-integration`: herramienta
  `neurosymbolic_reasoning`, detector previo, auditoría y salida fundamentada.
- `sharememory/hermes_memory/knowledge_broker.py`: memoria operativa.
- `skilled/improvement`: mejora continua y construcción de evaluaciones.
- `datasets/evaluation`: casos sintéticos versionados, sin datos de usuario.
- `vault/`: cuarentena de archivos retirados; nunca se purga automáticamente.

## Criterio de finalización

Una tarea está completa solo si existe resultado, verificación y evidencia. Si falta un ejecutor o una decisión humana, debe quedar `blocked` con causa, evidencia, alternativas, riesgos, acción requerida y reanudación definida.

Las reglas detalladas y el estado de implementación están en `docs/verification-report.md`.
