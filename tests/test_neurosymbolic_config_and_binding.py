from __future__ import annotations

import importlib.util
import json
import sys
import uuid
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ROOT / "agents/hermes/plugins/neurosymbolic-integration"
CONFIG_PATH = ROOT / "agents/hermes/config/config.yaml"


class FakeHermesContext:
    def __init__(self):
        self.hooks = {}
        self.tools = {}

    def register_hook(self, event, callback):
        self.hooks[event] = callback

    def register_tool(self, **registration):
        self.tools[registration["name"]] = registration


def _load_plugin():
    name = f"neurosymbolic_binding_plugin_{uuid.uuid4().hex}"
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


def test_neurosymbolic_plugin_and_toolset_are_exposed_to_hermes():
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))

    assert "neurosymbolic-integration" in config["plugins"]["enabled"]
    for platform in ("cli", "telegram"):
        assert "neurosymbolic" in config["platform_toolsets"][platform]
        assert "neurosymbolic" in config["known_plugin_toolsets"][platform]


def test_unknown_request_id_cannot_execute_neurosymbolic_tool(tmp_path, monkeypatch):
    proof = tmp_path / "binding-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))

    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)
    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]

    result = json.loads(
        handler(
            {
                "query": "A -> B",
                "request_id": "f" * 32,
            },
            session_id="unbound-session",
            turn_id="unbound-turn",
        )
    )

    assert result == {
        "status": "error",
        "error": "unknown_neurosymbolic_request_id",
    }
    events = [
        json.loads(line)
        for line in proof.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    rejected = [item for item in events if item["event"] == "tool_rejected"]
    assert rejected
    assert rejected[-1]["reason"] == "unknown_request_id"


def test_tool_uses_detector_query_even_if_model_changes_query(tmp_path, monkeypatch):
    proof = tmp_path / "authoritative-query-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))

    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    original = "Detecta el ciclo del grafo A -> B -> A"
    required = ctx.hooks["pre_llm_call"](
        user_message=original,
        platform="cli",
        session_id="bound-session",
        turn_id="bound-turn",
    )
    import re

    match = re.search(r"`([0-9a-f]{32})`", required["context"])
    assert match is not None
    request_id = match.group(1)

    handler = ctx.tools["neurosymbolic_reasoning"]["handler"]
    result = json.loads(
        handler(
            {
                "query": "A -> B",
                "request_id": request_id,
            },
            session_id="bound-session",
            turn_id="bound-turn",
            task_id="bound-session",
        )
    )

    assert result["status"] == "success"
    assert result["engine_used"] == "networkx"
    # El original sí contiene el ciclo completo; la query alterada no.
    support = (result.get("audit") or {}).get("support_index", {})
    nx = support.get("networkx:analysis", {})
    assert nx.get("is_acyclic") is False

    events = [
        json.loads(line)
        for line in proof.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    started = [item for item in events if item["event"] == "tool_started"]
    assert started
    assert started[-1]["query_argument_matches_authoritative"] is False
