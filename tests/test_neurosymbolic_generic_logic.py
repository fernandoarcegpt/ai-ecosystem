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
    name = f"neurosymbolic_generic_logic_{uuid.uuid4().hex}"
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


def test_generic_if_then_rule_is_detected_and_executes_pydatalog(tmp_path, monkeypatch):
    proof = tmp_path / "generic-logic-proof.jsonl"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = (
        "Hechos: activo(alice). Regla: si alguien está activo entonces es "
        "elegible. Deduce si alice es elegible."
    )
    required = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="generic-logic-session",
        turn_id="generic-logic-turn",
    )
    assert required is not None
    assert "logic" in required["context"]

    match = re.search(r"`([0-9a-f]{32})`", required["context"])
    assert match is not None
    request_id = match.group(1)

    result = json.loads(
        ctx.tools["neurosymbolic_reasoning"]["handler"](
            {
                "query": prompt,
                "request_id": request_id,
                "structured_context": {
                    "required_capabilities": ["logic"],
                    "facts": [["active", "alice"]],
                    "rules": [
                        {
                            "name": "eligible_from_active",
                            "head": "eligible(X)",
                            "body": "active(X)",
                        }
                    ],
                    "queries": ["eligible(X)"],
                },
            },
            session_id="generic-logic-session",
            turn_id="generic-logic-turn",
            task_id="generic-logic-session",
        )
    )

    assert result["status"] == "success"
    assert result["engine_used"] == "pydatalog"
    assert result["engines"] == {"pydatalog": "success"}
    assert any(
        claim.get("kind") == "derived_fact"
        and "eligible" in claim.get("statement", "")
        and "alice" in claim.get("statement", "")
        for claim in result["claims"]
    )

    events = [
        json.loads(line)
        for line in proof.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    decisions = [item for item in events if item["event"] == "detector_decision"]
    engines = [item for item in events if item["event"] == "engine_result_observed"]
    assert decisions and "logic" in decisions[-1]["detected_capabilities"]
    assert engines and engines[-1]["engine"] == "pydatalog"
    assert engines[-1]["status"] == "success"
