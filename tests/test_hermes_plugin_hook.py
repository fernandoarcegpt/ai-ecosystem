"""Contrato de la herramienta y los hooks reales del plugin Hermes."""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import uuid
from pathlib import Path

import yaml


PLUGIN_DIR = (
    Path(__file__).resolve().parents[1]
    / "agents/hermes/plugins/neurosymbolic-integration"
)


TRANSFER_PROMPT = (
    "Plan de transferencias documentales 2027. RRHH tiene 60 cajas listas. "
    "RRHH no ha remitido el inventario definitivo. Contabilidad tiene 50 "
    "cajas listas. Contabilidad presenta inventario inconsistente. "
    "Dirección tiene 35 cajas listas. OCI tiene 15 cajas listas. El flujo "
    "es organizacion -> inventario -> revision -> subsanacion -> "
    "conformidad -> transferencia. Si falta el inventario definitivo, la "
    "unidad queda bloqueada. Si el inventario es inconsistente, la unidad "
    "requiere corrección. Una unidad no puede recibirse si está bloqueada. "
    "Una unidad no puede recibirse si requiere corrección. La capacidad "
    "disponible es 120 cajas. La meta institucional es 9 transferencias."
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
    name = f"neurosymbolic_integration_plugin_{uuid.uuid4().hex}"
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


def _registered_plugin(tmp_path, monkeypatch):
    proof = tmp_path / "hook-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)
    return plugin, ctx, proof


def _required_request_id(context: str) -> str:
    match = re.search(r"`([0-9a-f]{32})`", context)
    assert match is not None
    return match.group(1)


def _events(proof: Path):
    return [
        json.loads(line)
        for line in proof.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_manifest_and_runtime_register_the_official_tool(tmp_path, monkeypatch):
    _, ctx, _ = _registered_plugin(tmp_path, monkeypatch)
    manifest = yaml.safe_load((PLUGIN_DIR / "plugin.yaml").read_text())

    assert manifest["provides_tools"] == ["neurosymbolic_reasoning"]
    assert set(manifest["provides_hooks"]) == {
        "pre_llm_call",
        "post_tool_call",
        "transform_llm_output",
    }
    registration = ctx.tools["neurosymbolic_reasoning"]
    assert registration["toolset"] == "neurosymbolic"
    assert registration["schema"]["parameters"]["required"] == [
        "query",
        "request_id",
    ]


def test_pre_llm_only_requires_tool_and_plain_text_is_ignored(
    tmp_path,
    monkeypatch,
):
    _, ctx, proof = _registered_plugin(tmp_path, monkeypatch)
    hook = ctx.hooks["pre_llm_call"]

    required = hook(
        user_message="Detecta el ciclo del grafo A -> B -> A",
        platform="cli",
        session_id="symbolic-session",
        turn_id="turn-1",
    )
    assert "REQUIERE_HERRAMIENTA_NEUROSIMBOLICA" in required["context"]
    assert "neurosymbolic_reasoning" in required["context"]

    assert hook(
        user_message="Hola, ¿cómo estás?",
        platform="cli",
        session_id="plain-session",
        turn_id="turn-2",
    ) is None

    events = _events(proof)
    assert any(item["event"] == "tool_required" for item in events)
    assert any(item["event"] == "detector_skipped" for item in events)
    assert not any(item["event"] == "tool_started" for item in events)


def test_official_tool_runs_composed_pipeline_and_replaces_free_text(
    tmp_path,
    monkeypatch,
):
    _, ctx, proof = _registered_plugin(tmp_path, monkeypatch)
    pre = ctx.hooks["pre_llm_call"]
    required = pre(
        user_message=TRANSFER_PROMPT,
        platform="cli",
        session_id="transfer-session",
        turn_id="transfer-turn",
    )
    request_id = _required_request_id(required["context"])

    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]
    result_text = handler(
        {"query": "texto alterado por el modelo", "request_id": request_id},
        session_id="transfer-session",
        turn_id="transfer-turn",
        task_id="transfer-session",
    )
    result = json.loads(result_text)
    ctx.hooks["post_tool_call"](
        tool_name="neurosymbolic_reasoning",
        args={"query": TRANSFER_PROMPT, "request_id": request_id},
        result=result_text,
        task_id="transfer-session",
        session_id="transfer-session",
        turn_id="transfer-turn",
        duration_ms=12,
    )

    assert result["status"] == "success"
    assert result["engine_used"] == "combined"
    assert result["engines"] == {
        "networkx": "success",
        "pydatalog": "success",
        "z3": "success",
    }
    assert result["summary"]["selected_units"] == ["Dirección", "OCI"]
    assert result["summary"]["selected_boxes"] == 50
    assert result["summary"]["gap_to_target"] == 7
    assert result["scope"]["entities"] == [
        "RRHH",
        "Contabilidad",
        "Dirección",
        "OCI",
    ]

    transformed = ctx.hooks["transform_llm_output"](
        response_text=(
            "Transferencia inmediata. Responsable: RRHH. Plazo sugerido: hoy."
        ),
        session_id="transfer-session",
        turn_id="transfer-turn",
        platform="cli",
    )
    assert transformed == result["rendered_markdown"]
    assert "Transferencia inmediata" not in transformed
    assert "Responsable:" not in transformed
    assert "Plazo sugerido" not in transformed
    assert "4 unidades" in transformed
    assert "no limita el universo institucional" in transformed
    assert "Supuestos explícitos" in transformed

    events = _events(proof)
    completed = next(item for item in events if item["event"] == "tool_completed")
    assert completed["engines"] == {
        "networkx": "success",
        "pydatalog": "success",
        "z3": "success",
    }
    assert any(item["event"] == "output_replaced" for item in events)
    assert any(item["event"] == "official_tool_observed" for item in events)


def test_missing_required_tool_fails_closed(tmp_path, monkeypatch):
    _, ctx, proof = _registered_plugin(tmp_path, monkeypatch)
    ctx.hooks["pre_llm_call"](
        user_message="Detecta A -> B -> A",
        platform="cli",
        session_id="missing-tool",
        turn_id="missing-turn",
    )

    transformed = ctx.hooks["transform_llm_output"](
        response_text="El grafo no tiene ciclos.",
        session_id="missing-tool",
        turn_id="missing-turn",
        platform="cli",
    )

    assert "no ejecutado" in transformed
    assert "se descartó la respuesta" in transformed
    assert any(
        item["event"] == "required_tool_missing" for item in _events(proof)
    )


def test_tool_request_is_idempotent(tmp_path, monkeypatch):
    _, ctx, proof = _registered_plugin(tmp_path, monkeypatch)
    required = ctx.hooks["pre_llm_call"](
        user_message="Detecta el ciclo A -> B -> A",
        session_id="idempotent",
        turn_id="idempotent-turn",
        platform="cli",
    )
    request_id = _required_request_id(required["context"])
    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]
    args = {
        "query": "Detecta el ciclo A -> B -> A",
        "request_id": request_id,
    }

    first = json.loads(handler(args, session_id="idempotent"))
    second = json.loads(handler(args, session_id="idempotent"))

    assert first == second
    events = _events(proof)
    assert sum(item["event"] == "tool_started" for item in events) == 1
    assert sum(item["event"] == "tool_result_reused" for item in events) == 1


def test_all_single_engines_execute_only_through_the_tool(tmp_path, monkeypatch):
    _, ctx, _ = _registered_plugin(tmp_path, monkeypatch)
    cases = {
        "networkx": "Detecta el ciclo del grafo A -> B -> C -> A",
        "z3": "Resuelve las restricciones x > 10 y x < 5",
        "pydatalog": (
            "Ana es madre de Luis y Luis es padre de Marta. "
            "¿Es Ana ancestro de Marta?"
        ),
    }
    for index, (expected_engine, prompt) in enumerate(cases.items()):
        session_id = f"engine-{index}"
        required = ctx.hooks["pre_llm_call"](
            user_message=prompt,
            session_id=session_id,
            turn_id=session_id,
            platform="cli",
        )
        request_id = _required_request_id(required["context"])
        result = json.loads(
            ctx.tools["neurosymbolic_reasoning"]["handler"](
                {"query": prompt, "request_id": request_id},
                session_id=session_id,
                turn_id=session_id,
            )
        )
        assert result["engine_used"] == expected_engine
        assert result["engines"][expected_engine] == "success"


def test_explicit_orchestration_command_remains_opt_in(tmp_path, monkeypatch):
    _, ctx, proof = _registered_plugin(tmp_path, monkeypatch)
    monkeypatch.setenv("HERMES_AUTONOMY_ENABLED", "1")

    import orchestration.hermes_bridge as bridge

    monkeypatch.setattr(
        bridge,
        "run_from_hermes",
        lambda message: {
            "task_report": {
                "status_distribution": {
                    "completed": 4,
                    "blocked": 0,
                    "failed": 0,
                }
            }
        },
    )
    result = ctx.hooks["pre_llm_call"](
        user_message="/orchestrate Implementar y verificar el cambio",
        platform="cli",
        session_id="orchestration",
    )

    assert "completed=4" in result["context"]
    assert any(item["event"] == "autonomy_completed" for item in _events(proof))
