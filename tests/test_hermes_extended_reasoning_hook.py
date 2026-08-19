from __future__ import annotations

import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path


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


def _load_plugin():
    name = f"neurosymbolic_extended_plugin_{uuid.uuid4().hex}"
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


def test_official_tool_executes_extended_temporal_engine(tmp_path, monkeypatch):
    proof = tmp_path / "extended-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = (
        "Resuelve estas restricciones temporales: la tarea A dura 2 y la tarea "
        "B dura 3; A debe terminar antes de B."
    )
    required = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="extended-temporal-session",
        turn_id="extended-temporal-turn",
    )
    request_id = _request_id(required["context"])
    assert "structured_context" in required["context"]

    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]
    result_text = handler(
        {
            "query": "texto alterado",
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
        session_id="extended-temporal-session",
        turn_id="extended-temporal-turn",
        task_id="extended-temporal-session",
    )
    result = json.loads(result_text)

    assert result["status"] == "success"
    assert result["engine_used"] == "z3_temporal"
    assert result["reasoning_plan"] == ["z3_temporal"]
    assert result["engines"] == {"z3_temporal": "success"}
    assert result["formalization_source"] == "hermes_tool_arguments"
    assert result["audit"]["unresolved_support"] == []

    transformed = ctx.hooks["transform_llm_output"](
        response_text="respuesta libre del modelo",
        session_id="extended-temporal-session",
        turn_id="extended-temporal-turn",
    )
    assert "Resultado neurosimbólico verificable" in transformed
    assert "z3_temporal" in transformed
    assert "respuesta libre del modelo" not in transformed

    events = [
        json.loads(line)
        for line in proof.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    completed = [item for item in events if item["event"] == "tool_completed"]
    assert completed
    assert completed[-1]["engine"] == "z3_temporal"
    assert completed[-1]["status"] == "success"


def test_official_tool_fails_closed_when_bayesian_spec_is_missing(tmp_path, monkeypatch):
    proof = tmp_path / "bayes-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = "Calcula con Bayes la probabilidad posterior, pero no tengo las CPD."
    required = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="incomplete-bayes-session",
        turn_id="incomplete-bayes-turn",
    )
    request_id = _request_id(required["context"])

    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]
    result = json.loads(
        handler(
            {
                "query": prompt,
                "request_id": request_id,
                "structured_context": {
                    "required_capabilities": ["probabilistic"],
                },
            },
            session_id="incomplete-bayes-session",
            turn_id="incomplete-bayes-turn",
            task_id="incomplete-bayes-session",
        )
    )

    assert result["status"] == "human_review"
    assert result["claims"] == []
    assert "no concluyente" in result["rendered_markdown"].lower()
