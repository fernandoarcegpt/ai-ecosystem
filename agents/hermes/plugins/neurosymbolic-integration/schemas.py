"""Esquemas de herramientas visibles para Hermes."""

_EXTENDED_CAPABILITIES = [
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

NEUROSYMBOLIC_REASONING = {
    "name": "neurosymbolic_reasoning",
    "description": (
        "Ejecuta razonamiento formal, verificable y auditable sobre grafos, "
        "reglas, restricciones, planificación, tiempo, espacio, probabilidad, "
        "causalidad, contrafactuales, abducción e inducción estadística. "
        "Cuando uses structured_context, copia únicamente datos explícitos del "
        "mensaje; no inventes variables, probabilidades, acciones, relaciones "
        "causales, coordenadas, hipótesis ni ejemplos faltantes."
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
                    "Formalización opcional para motores extendidos. Incluye solo "
                    "información explícita del usuario. Si faltan datos necesarios, "
                    "indica required_capabilities y omite el spec incompleto para "
                    "que el sistema falle cerrado con human_review."
                ),
                "properties": {
                    "required_capabilities": {
                        "type": "array",
                        "items": {"type": "string", "enum": _EXTENDED_CAPABILITIES},
                        "uniqueItems": True,
                    },
                    **_SPEC_PROPERTIES,
                },
                "additionalProperties": False,
            },
        },
        "required": ["query", "request_id"],
        "additionalProperties": False,
    },
}
