from __future__ import annotations

import importlib.util
import sys
import uuid
from pathlib import Path

import pytest


PLUGIN_DIR = (
    Path(__file__).resolve().parents[1]
    / "agents/hermes/plugins/neurosymbolic-integration"
)


def _load(filename: str):
    name = f"neurosymbolic_matrix_{filename}_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, PLUGIN_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CASES = [
    ("graph", "Analiza el grafo A -> B -> C y dime si existe un ciclo."),
    ("logic", "Si active(X) entonces eligible(X). Deduce si se cumple la regla."),
    ("constraints", "Asigna A y B entre Ana y Luis; máximo 1 tarea por persona."),
    (
        "planning",
        "Estado inicial ready. Hay una secuencia de acciones para alcanzar el objetivo done.",
    ),
    (
        "temporal",
        "A tarda 2 horas y B tarda 3; B solo puede empezar cuando termine A.",
    ),
    (
        "spatial",
        "El punto (1, 2) y este polígono están dados: determina si el punto está dentro de él.",
    ),
    (
        "probabilistic",
        "La prevalencia es 1%, sensibilidad 95%, especificidad 90% y la prueba salió positiva.",
    ),
    (
        "causal",
        "Estima el efecto causal del tratamiento T sobre el resultado Y controlando confusores.",
    ),
    (
        "counterfactual",
        "¿Qué habría pasado si el tratamiento T hubiera sido 0?",
    ),
    (
        "abductive",
        "¿Qué pudo causar esta observación entre las hipótesis permitidas?",
    ),
    (
        "statistical_induction",
        "Con estos ejemplos predice la clase de un caso nuevo.",
    ),
]


@pytest.mark.parametrize(("capability", "prompt"), CASES)
def test_each_implemented_capability_has_a_natural_detection_path(capability, prompt):
    detection = _load("detection.py").detect_extended_reasoning(prompt)
    assert detection["requires_tool"] is True
    assert capability in detection["capabilities"]
    assert detection["scores"][capability] >= 4
    assert detection["evidence"][capability]


def test_detector_capabilities_are_exposed_by_the_tool_schema():
    detection_module = _load("detection.py")
    schema_module = _load("schemas.py")
    enum_values = set(
        schema_module.NEUROSYMBOLIC_REASONING["parameters"]["properties"]
        ["structured_context"]["properties"]["required_capabilities"]
        ["items"]["enum"]
    )

    detected = set()
    for _, prompt in CASES:
        detected.update(
            detection_module.detect_extended_reasoning(prompt)["capabilities"]
        )

    assert detected <= enum_values
    assert {
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
    } <= enum_values
