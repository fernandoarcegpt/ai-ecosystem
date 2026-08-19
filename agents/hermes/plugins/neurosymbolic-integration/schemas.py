"""Esquemas de herramientas visibles para Hermes."""

_CAPABILITIES = [
    "graph",
    "logic",
    "constraints",
    "planning",
    "temporal",
    "spatial",
    "probabilistic",
    "causal",
    "counterfactual",
    "abductive",
    "statistical_induction",
]

_SPEC_PROPERTIES = {
    "planning_spec": {"type": "object", "additionalProperties": True},
    "temporal_spec": {"type": "object", "additionalProperties": True},
    "spatial_spec": {"type": "object", "additionalProperties": True},
    "probabilistic_spec": {"type": "object", "additionalProperties": True},
    "causal_spec": {"type": "object", "additionalProperties": True},
    "abductive_spec": {"type": "object", "additionalProperties": True},
    "statistical_induction_spec": {"type": "object", "additionalProperties": True},
}

_LEGACY_PROPERTIES = {
    "entities": {"type": "array", "items": {"type": "string"}},
    "items": {"type": "array", "items": {"type": "string"}},
    "people": {"type": "array", "items": {"type": "string"}},
    "relations": {
        "type": "array",
        "items": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
            "maxItems": 2,
        },
    },
    "facts": {"type": "array"},
    "rules": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    "constraints": {"type": "array"},
    "variables": {"type": "object", "additionalProperties": True},
    "objectives": {"type": "array"},
    "queries": {"type": "array"},
}

NEUROSYMBOLIC_REASONING = {
    "name": "neurosymbolic_reasoning",
    "description": (
        "Ejecuta razonamiento formal, verificable y auditable sobre grafos, "
        "reglas, restricciones, planificación, tiempo, espacio, probabilidad, "
        "causalidad, contrafactuales, abducción e inducción estadística. "
        "Cuando uses structured_context, copia únicamente datos explícitos del "
        "mensaje; no inventes variables, probabilidades, acciones, relaciones "
        "causales, coordenadas, hipótesis, hechos, reglas ni ejemplos faltantes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto completo y sin resumir del problema.",
            },
            "request_id": {
                "type": "string",
                "description": (
                    "Identificador entregado por el contexto neurosimbólico del "
                    "turno. Debe copiarse sin cambios."
                ),
            },
            "structured_context": {
                "type": "object",
                "description": (
                    "Formalización opcional. Para graph/logic/constraints usa los "
                    "campos estructurados explícitos; para motores extendidos usa "
                    "su *_spec. Incluye solo información presente en el mensaje. "
                    "Si faltan datos necesarios, indica required_capabilities y "
                    "omite la estructura incompleta para que el sistema falle cerrado."
                ),
                "properties": {
                    "required_capabilities": {
                        "type": "array",
                        "items": {"type": "string", "enum": _CAPABILITIES},
                        "uniqueItems": True,
                    },
                    **_LEGACY_PROPERTIES,
                    **_SPEC_PROPERTIES,
                },
                "additionalProperties": False,
            },
        },
        "required": ["query", "request_id"],
        "additionalProperties": False,
    },
}
