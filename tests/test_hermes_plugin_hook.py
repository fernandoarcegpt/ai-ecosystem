"""Contract tests for the real Hermes pre_llm_call plugin entry point."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


PLUGIN_DIR = (
    Path(__file__).resolve().parents[1]
    / "agents/hermes/plugins/neurosymbolic-integration"
)


class FakeHermesContext:
    def __init__(self):
        self.hooks = {}

    def register_hook(self, event, callback):
        self.hooks[event] = callback


def _load_plugin():
    spec = importlib.util.spec_from_file_location(
        "neurosymbolic_integration_plugin",
        PLUGIN_DIR / "__init__.py",
        submodule_search_locations=[str(PLUGIN_DIR)],
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pre_llm_hook_executes_all_three_engines_and_skips_plain_text(
    tmp_path,
    monkeypatch,
):
    proof = tmp_path / "hook-proof.log"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)
    hook = ctx.hooks["pre_llm_call"]

    cases = {
        "networkx": "Detecta el ciclo del grafo A -> B -> C -> A",
        "z3": "Resuelve las restricciones x > 10 y x < 5",
        "pydatalog": (
            "Ana es madre de Luis y Luis es padre de Marta. "
            "¿Es Ana ancestro de Marta?"
        ),
    }
    for expected_engine, prompt in cases.items():
        result = hook(user_message=prompt, platform="cli", session_id="test")
        assert result is not None
        assert "context" in result
        assert f"Motor utilizado: {expected_engine}" in result["context"]

    assert hook(user_message="Hola, ¿cómo estás?", platform="cli") is None

    evidence = proof.read_text(encoding="utf-8")
    for engine in cases:
        assert f"ENGINE={engine} STATUS=success" in evidence
    assert evidence.count("CONTEXT_INJECTED") == 3


def test_plugin_ignores_non_cli_platform(tmp_path, monkeypatch):
    proof = tmp_path / "hook-proof.log"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    result = ctx.hooks["pre_llm_call"](
        user_message="Detecta A -> B -> A",
        platform="telegram",
    )
    assert result is None
    assert "CONTEXT_INJECTED" not in proof.read_text(encoding="utf-8")


def test_pre_llm_hook_logs_composed_transfer_pipeline(tmp_path, monkeypatch):
    proof = tmp_path / "combined-hook-proof.log"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)

    prompt = (
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
    result = ctx.hooks["pre_llm_call"](
        user_message=prompt,
        platform="cli",
        session_id="combined-test",
    )

    assert result is not None
    assert "MODO: combined" in result["context"]
    evidence = proof.read_text(encoding="utf-8")
    assert "ENGINE=combined STATUS=success" in evidence
    assert "NETWORKX=success" in evidence
    assert "PYDATALOG=success" in evidence
    assert "Z3=success" in evidence
    assert "CONTEXT_INJECTED" in evidence


def test_explicit_orchestration_command_runs_through_hermes_hook(
    tmp_path,
    monkeypatch,
):
    proof = tmp_path / "hook-proof.log"
    monkeypatch.setenv("HERMES_NEUROSYMBOLIC_PROOF_LOG", str(proof))
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
    plugin = _load_plugin()
    ctx = FakeHermesContext()
    plugin.register(ctx)
    result = ctx.hooks["pre_llm_call"](
        user_message="/orchestrate Implementar y verificar el cambio",
        platform="cli",
    )

    assert "completed=4" in result["context"]
    assert "AUTONOMY_COMPLETED=4 BLOCKED=0 FAILED=0" in proof.read_text()
