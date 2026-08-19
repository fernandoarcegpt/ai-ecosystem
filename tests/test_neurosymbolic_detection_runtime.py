from __future__ import annotations

import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path

import pytest


PLUGIN_DIR = (
    Path(__file__).resolve().parents[1]
    / "agents/hermes/plugins/neurosymbolic-integration"
)


class FakeHermesContext:
    def __init__(self):
        self.hooks = {}
        self.tools = {}

    def register_hook(self, event, callback):
        self.hooks[event] = callback

    def register_tool(self, **registration):
        self.tools[registration["name"]] = registration


def _load_detection():
    name = f"neurosymbolic_detection_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(name, PLUGIN_DIR / "detection.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_plugin():
    name = f"neurosymbolic_runtime_plugin_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(
        name,
        PLUGIN_DIR / "__init__.py",
        submodule_search_locations=[str(PLUGIN_DIR)],
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _request_id(text: str) -> str:
    match = re.search(r"`([0-9a-f]{32})`", text)
    assert match is not None
    return match.group(1)


def _events(path: Path):
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


@pytest.mark.parametrize(
    ("prompt", "expected"),
    [
        (
            "Planificación clásica: estado inicial listo, acciones con precondiciones y objetivo terminado.",
            "planning",
        ),
        (
            "La tarea A dura 2 horas y debe terminar antes de B.",
            "temporal",
        ),
        (
            "¿El punto (1, 2) está dentro del polígono definido por estas coordenadas?",
            "spatial",
        ),
        (
            "¿Cuál es la probabilidad de A dado B?",
            "probabilistic",
        ),
        (
            "Estima el efecto causal de T sobre Y controlando estos confusores.",
            "causal",
        ),
        (
            "¿Qué habría pasado si el tratamiento hubiera sido 0?",
            "counterfactual",
        ),
        (
            "Busca las posibles causas que explican esta observación entre estas hipótesis.",
            "abductive",
        ),
        (
            "Entrena con estos ejemplos un modelo para clasificar los datos.",
            "statistical_induction",
        ),
    ],
)
def test_detector_covers_common_reasoning_phrasings(prompt, expected):
    detection = _load_detection().detect_extended_reasoning(prompt)
    assert detection["requires_tool"] is True
    assert expected in detection["capabilities"]
    assert detection["scores"][expected] >= 4
    assert detection["evidence"][expected]


def test_counterfactual_also_requires_causal_capability():
    detection = _load_detection().detect_extended_reasoning(
        "¿Qué hubiera pasado si X hubiese sido 0?"
    )
    assert detection["capabilities"] == ["causal", "counterfactual"]


@pytest.mark.parametrize(
    "prompt",
    [
        "Hazme un plan de viaje para el fin de semana.",
        "La palabra probabilidad aparece tres veces en este párrafo.",
        "Explícame la causa de la lluvia en términos generales.",
        "Dame una lista de acciones para ordenar mi escritorio.",
    ],
)
def test_detector_avoids_obvious_nonformal_false_positives(prompt):
    detection = _load_detection().detect_extended_reasoning(prompt)
    assert detection["requires_tool"] is False
    assert detection["capabilities"] == []


def test_ambiguous_text_review_survives_tool_context(tmp_path, monkeypatch):
    proof = tmp_path / "ambiguous-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = "A depende de B."
    required = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="ambiguous-session",
        turn_id="ambiguous-turn",
    )
    request_id = _request_id(required["context"])
    result = json.loads(
        ctx.tools["neurosymbolic_reasoning"]["handler"](
            {"query": prompt, "request_id": request_id},
            session_id="ambiguous-session",
            turn_id="ambiguous-turn",
            task_id="ambiguous-session",
        )
    )

    assert result["status"] == "human_review"
    assert result["claims"] == []
    assert result["review_reason"] == "bare_dependency_relation_is_ambiguous"


def test_proof_log_distinguishes_detection_runtime_and_engine_execution(
    tmp_path,
    monkeypatch,
):
    proof = tmp_path / "runtime-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = "Restricciones temporales: A dura 2 y B dura 3; A debe terminar antes de B."
    required = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="runtime-session",
        turn_id="runtime-turn",
    )
    request_id = _request_id(required["context"])

    result = json.loads(
        ctx.tools["neurosymbolic_reasoning"]["handler"](
            {
                "query": prompt,
                "request_id": request_id,
                "structured_context": {
                    "required_capabilities": ["temporal"],
                    "temporal_spec": {
                        "tasks": {
                            "A": {"duration": 2},
                            "B": {"duration": 3},
                        },
                        "before": [["A", "B"]],
                    },
                },
            },
            session_id="runtime-session",
            turn_id="runtime-turn",
            task_id="runtime-session",
        )
    )
    assert result["status"] == "success"
    assert result["engines"] == {"z3_temporal": "success"}

    events = _events(proof)
    detector = [item for item in events if item["event"] == "detector_decision"]
    inventory = [item for item in events if item["event"] == "runtime_engine_inventory"]
    engine = [item for item in events if item["event"] == "engine_result_observed"]
    completed = [item for item in events if item["event"] == "tool_completed"]

    assert detector and "temporal" in detector[-1]["detected_capabilities"]
    assert inventory and inventory[-1]["legacy_engines"]["z3"] is True
    assert "z3_temporal" in inventory[-1]["extended_adapters"]
    assert inventory[-1]["package_versions"]["z3-solver"] is not None
    assert engine and engine[-1]["engine"] == "z3_temporal"
    assert engine[-1]["status"] == "success"
    assert completed[-1]["engine"] == "z3_temporal"
    assert completed[-1]["status"] == "success"
