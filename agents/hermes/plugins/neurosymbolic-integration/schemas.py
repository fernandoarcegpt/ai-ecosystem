"""Esquemas de herramientas visibles para Hermes."""

NEUROSYMBOLIC_REASONING = {
    "name": "neurosymbolic_reasoning",
    "description": (
        "Ejecuta razonamiento determinista sobre grafos, reglas lógicas y "
        "restricciones. Debe usarse cuando el turno contiene dependencias, "
        "ciclos, inferencias si-entonces, asignaciones, capacidades u objetivos "
        "de optimización. Devuelve una respuesta fundamentada; no agregues "
        "plazos, responsables, autorizaciones ni recomendaciones ausentes."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Texto completo del problema que debe formalizarse.",
            },
            "request_id": {
                "type": "string",
                "description": (
                    "Identificador entregado por el contexto neurosimbólico del "
                    "turno. Debe copiarse sin cambios."
                ),
            },
        },
        "required": ["query", "request_id"],
        "additionalProperties": False,
    },
}
