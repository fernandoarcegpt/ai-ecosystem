"""Esquemas de herramientas visibles para Hermes.

Los specs son deliberadamente explícitos: Hermes debe saber qué estructura
formal espera cada motor y no adivinar nombres de campos.
"""

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

_PAIR_OF_STRINGS = {
    "type": "array",
    "items": {"type": "string"},
    "minItems": 2,
    "maxItems": 2,
}

_PLANNING_SPEC = {
    "type": "object",
    "description": "Planificación clásica proposicional con fluentes booleanos.",
    "properties": {
        "name": {"type": "string"},
        "fluents": {"type": "array", "items": {"type": "string"}},
        "initial_true": {"type": "array", "items": {"type": "string"}},
        "actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "preconditions": {"type": "array", "items": {"type": "string"}},
                    "negative_preconditions": {"type": "array", "items": {"type": "string"}},
                    "add": {"type": "array", "items": {"type": "string"}},
                    "delete": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        },
        "goals": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}

_TEMPORAL_SPEC = {
    "type": "object",
    "description": "Restricciones de intervalos sobre tareas con duración positiva.",
    "properties": {
        "tasks": {
            "type": "object",
            "description": "Mapa nombre_tarea -> {duration: entero positivo}.",
            "additionalProperties": {
                "type": "object",
                "properties": {"duration": {"type": "integer", "minimum": 1}},
                "required": ["duration"],
                "additionalProperties": False,
            },
        },
        "before": {"type": "array", "items": _PAIR_OF_STRINGS},
        "non_overlap": {"type": "array", "items": _PAIR_OF_STRINGS},
        "deadlines": {"type": "object", "additionalProperties": {"type": "integer"}},
        "release_times": {"type": "object", "additionalProperties": {"type": "integer"}},
    },
    "additionalProperties": False,
}

_SPATIAL_SPEC = {
    "type": "object",
    "description": "Geometrías GeoJSON nombradas y consultas espaciales explícitas.",
    "properties": {
        "geometries": {
            "type": "object",
            "description": "Mapa nombre -> geometría GeoJSON, p.ej. Point o Polygon.",
            "additionalProperties": {"type": "object", "additionalProperties": True},
        },
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "op": {
                        "type": "string",
                        "enum": [
                            "contains",
                            "within",
                            "intersects",
                            "touches",
                            "overlaps",
                            "distance",
                            "geodesic_distance_m",
                        ],
                    },
                    "left": {"type": "string"},
                    "right": {"type": "string"},
                },
                "required": ["op", "left", "right"],
                "additionalProperties": False,
            },
        },
        "ellipsoid": {"type": "string"},
    },
    "additionalProperties": False,
}

_PROBABILISTIC_SPEC = {
    "type": "object",
    "description": "Red bayesiana discreta: aristas, CPDs tabulares y consultas.",
    "properties": {
        "edges": {"type": "array", "items": _PAIR_OF_STRINGS},
        "cpds": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "variable": {"type": "string"},
                    "variable_card": {"type": "integer", "minimum": 2},
                    "values": {"type": "array"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "evidence_card": {"type": "array", "items": {"type": "integer", "minimum": 2}},
                    "state_names": {"type": "object", "additionalProperties": {"type": "array"}},
                },
                "required": ["variable", "variable_card", "values"],
                "additionalProperties": False,
            },
        },
        "queries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "enum": ["posterior", "map"]},
                    "variables": {"type": "array", "items": {"type": "string"}},
                    "evidence": {"type": "object", "additionalProperties": True},
                },
                "required": ["variables"],
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}

_CAUSAL_SPEC = {
    "type": "object",
    "description": "Modelo causal explícito para DoWhy/GCM; no inferir aristas causales desde correlación.",
    "properties": {
        "data": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "treatment": {"type": "string"},
        "outcome": {"type": "string"},
        "common_causes": {"type": "array", "items": {"type": "string"}},
        "instruments": {"type": "array", "items": {"type": "string"}},
        "graph_edges": {"type": "array", "items": _PAIR_OF_STRINGS},
        "method_name": {"type": "string"},
        "target_units": {"type": "string"},
        "proceed_when_unidentifiable": {"type": "boolean"},
        "test_significance": {"type": "boolean"},
        "confidence_intervals": {"type": "boolean"},
        "refuters": {"type": "array", "items": {"type": "string"}},
        "counterfactual": {
            "type": "object",
            "properties": {
                "observed_data": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
                "interventions": {"type": "object", "additionalProperties": True},
            },
            "additionalProperties": False,
        },
    },
    "additionalProperties": False,
}

_ABDUCTIVE_SPEC = {
    "type": "object",
    "description": "Abducción ASP: observaciones y conjunto cerrado de hipótesis permitidas.",
    "properties": {
        "observations": {"type": "array", "items": {"type": "string"}},
        "assumables": {"type": "array", "items": {"type": "string"}},
        "facts": {"type": "array", "items": {"type": "string"}},
        "rules": {"type": "array", "items": {"type": "string"}},
        "constraints": {"type": "array", "items": {"type": "string"}},
        "max_models": {"type": "integer", "minimum": 1},
    },
    "additionalProperties": False,
}

_STATISTICAL_INDUCTION_SPEC = {
    "type": "object",
    "description": "Inducción estadística tabular con árbol de decisión y validación holdout.",
    "properties": {
        "task": {"type": "string", "enum": ["classification", "regression"]},
        "features": {"type": "array", "items": {"type": "string"}},
        "target": {"type": "string"},
        "examples": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
        "test_size": {"type": "number", "exclusiveMinimum": 0, "exclusiveMaximum": 1},
        "random_state": {"type": "integer"},
        "max_depth": {"type": "integer", "minimum": 1},
        "predict": {"type": "array", "items": {"type": "object", "additionalProperties": True}},
    },
    "additionalProperties": False,
}

_SPEC_PROPERTIES = {
    "planning_spec": _PLANNING_SPEC,
    "temporal_spec": _TEMPORAL_SPEC,
    "spatial_spec": _SPATIAL_SPEC,
    "probabilistic_spec": _PROBABILISTIC_SPEC,
    "causal_spec": _CAUSAL_SPEC,
    "abductive_spec": _ABDUCTIVE_SPEC,
    "statistical_induction_spec": _STATISTICAL_INDUCTION_SPEC,
}

_LEGACY_PROPERTIES = {
    "entities": {"type": "array", "items": {"type": "string"}},
    "items": {"type": "array", "items": {"type": "string"}},
    "people": {"type": "array", "items": {"type": "string"}},
    "relations": {"type": "array", "items": _PAIR_OF_STRINGS},
    "dependencies": {"type": "array", "items": _PAIR_OF_STRINGS},
    "facts": {
        "type": "array",
        "description": "Hechos como [predicado, arg1, arg2, ...].",
    },
    "rules": {
        "type": "array",
        "description": "Reglas {name, head, body}; head/body usan sintaxis PyDatalog explícita.",
        "items": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "head": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["name", "head", "body"],
            "additionalProperties": False,
        },
    },
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
        "mensaje y sigue exactamente el schema del motor; no inventes variables, "
        "probabilidades, acciones, relaciones causales, coordenadas, hipótesis, "
        "hechos, reglas ni ejemplos faltantes."
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
                    "el *_spec cuya estructura aparece en este schema. Incluye solo "
                    "información presente en el mensaje. Si faltan datos necesarios, "
                    "indica required_capabilities y omite la estructura incompleta."
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
