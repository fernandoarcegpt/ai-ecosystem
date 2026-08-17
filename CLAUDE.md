# Instrucciones operativas del repositorio

Este archivo describe únicamente capacidades que existen en el árbol actual.

## Flujo de trabajo

1. Inspeccionar el código y el estado de Git antes de modificar.
2. Clasificar la solicitud con `reasoning.operational_decision` cuando requiera enrutamiento explícito.
3. Usar `TaskRouter` para objetivos persistentes, dependencias y bloqueos.
4. Ejecutar y verificar el cambio antes de declararlo completo.
5. Registrar en `KnowledgeBroker` solo resultados que hayan sido verificados.

No se deben tratar los nombres históricos `orchestrator-main`, `general-planning` ni `@hermes/cli` como comandos instalados: en este repositorio algunos sobreviven únicamente como documentación de skills.

## Comandos reales

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-test.txt
npm test
```

Prueba de integración con una instalación real de Hermes:

```bash
npm run test:hermes-cli
```

El script exige que `neurosymbolic-integration` esté descubierto y habilitado por Hermes. Ejecuta NetworkX, Z3 y PyDatalog mediante `hermes chat -q` y falla si el hook no inyecta evidencia.

## Componentes operativos

- `skilled/reasoning/task_router.py`: tareas, dependencias, ejecutores, verificación, persistencia, bloqueo y reanudación.
- `skilled/reasoning/operational_decision.py`: árbol central de decisión.
- `skilled/reasoning/claude_code_executor.py`: adaptador opt-in de Claude Code.
- `skilled/reasoning/neuro_symbolic_engine.py`: NetworkX, Z3 y PyDatalog.
- `agents/hermes/plugins/neurosymbolic-integration`: hook `pre_llm_call`.
- `sharememory/hermes_memory/knowledge_broker.py`: memoria operativa.
- `skilled/improvement`: mejora continua y construcción de evaluaciones.

## Criterio de finalización

Una tarea está completa solo si existe resultado, verificación y evidencia. Si falta un ejecutor o una decisión humana, debe quedar `blocked` con causa, evidencia, alternativas, riesgos, acción requerida y reanudación definida.

Las reglas detalladas y el estado de implementación están en `docs/verification-report.md`.
