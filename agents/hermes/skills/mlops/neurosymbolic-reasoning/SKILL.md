---
name: neurosymbolic-reasoning
description: Integración de razonamiento neurosimbólico en Hermes con auto‑activación basada en detección automática de patrones.
version: 1.3.0
tags: [neurosymbolic, reasoning, hermes, networkx, pydatalog, z3, symbolic-ai, auto-detection, semantic-router]
---

# Razonamiento Neurosimbólico en Hermes

Sistema de razonamiento simbólico integrado en Hermes mediante una herramienta
oficial, con detección estructural, trazabilidad y salida determinista.

## Motores y casos de uso
| Motor | Uso |
|-------|-----|
| NetworkX | Análisis de grafos (dependencias, ciclos). |
| PyDatalog | Inferencia lógica (reglas, hechos). |
| Z3 | Restricciones y planificación. |

## Flujo de trabajo
```text
pre_llm_call detector
  → neurosymbolic_reasoning tool call
  → ProblemExtractor
  → NetworkX / PyDatalog / Z3
  → grounded_result
  → transform_llm_output
```

## Patrones detectados
- **Dependencias**: `dependencias`, `dependencia`, `before`, `after`.
- **Restricciones**: `constraint`, `restricción`, `limit`, `limitación`.
- **Secuencias**: `sequence`, `orden`, `step`.
- **Reglas**: `rule`, `regla`, `if-then`.

## Integración con Hermes
- **Herramienta**: `neurosymbolic_reasoning` es el único punto de ejecución.
- **Detector**: `pre_llm_call` requiere la tool call, pero no ejecuta motores.
- **Auditoría**: `post_tool_call` confirma la llamada oficial.
- **Respuesta**: `transform_llm_output` entrega el Markdown fundamentado.
- **Fallo seguro**: si la herramienta requerida no se ejecuta, se descarta la
  respuesta libre del modelo.

## Pitfalls
- No ejecutar el pipeline desde el hook ni simular el contador de herramientas.
- No omitir ni alterar el `request_id` generado para el turno.
- Mantener el contexto actualizado; patrones basados en datos obsoletos pueden generar falsos positivos.
- No afirmar plazos, responsables o autorizaciones ausentes del contrato.
- Verificar que todas las referencias `supported_by` estén resueltas.

## Referencias rápidas
- `references/architecture.md` – Arquitectura completa.
- `references/engine-comparison.md` – Comparativa de motores.
- `references/integration-patterns.md` – Patrones de integración.

> **Nota de estilo**: Documentación concisa y directa; evite frases extensas.
