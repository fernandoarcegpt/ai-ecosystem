"""Acceptance tests for the connected autonomous orchestration flow."""

import json

from orchestration.autonomous_orchestrator import AgentRegistry, AutonomousOrchestrator
from orchestration.hermes_bridge import run_from_hermes


def _verified_executor(task):
    result = {
        "completed": True,
        "summary": f"completed {task.id}",
        "evidence": [f"role={task.assigned_agent}", f"type={task.type}"],
    }
    if task.type == "implementation":
        result["tests_passed"] = True
    if task.type == "qa":
        result["smoke_test_passed"] = True
    return result


def test_registry_runs_complete_multiagent_plan_and_persists_history(tmp_path):
    registry = AgentRegistry()
    for role, task_types in {
        "researcher": ["analysis"],
        "orchestrator": ["design"],
        "builder": ["implementation"],
        "qa": ["qa"],
    }.items():
        registry.register(role, _verified_executor, task_types=task_types)

    result = AutonomousOrchestrator(
        registry,
        state_dir=str(tmp_path),
    ).run("Implementar y verificar una mejora")

    assert result["task_report"]["total_tasks"] == 4
    assert result["task_report"]["status_distribution"]["completed"] == 4
    assert result["task_report"]["human_blocks"] == []
    history = json.loads((tmp_path / "run-history.json").read_text())
    assert len(history) == 1
    assert {agent["name"] for agent in history[0]["agents"]} >= {
        "researcher",
        "orchestrator",
        "builder",
        "qa",
    }


def test_hermes_bridge_requires_explicit_command_and_executes_all_stages(tmp_path):
    result = run_from_hermes(
        "/orchestrate Implementar y verificar el cambio",
        repository_path=str(tmp_path),
        state_dir=str(tmp_path / "state"),
        executor=_verified_executor,
    )
    assert result["task_report"]["status_distribution"]["completed"] == 4
    assert (tmp_path / "state" / "memory" / "memory.json").is_file()


def test_improvement_feedback_is_automatically_connected(tmp_path):
    registry = AgentRegistry()
    registry.register("researcher", _verified_executor, task_types=["analysis"])
    orchestrator = AutonomousOrchestrator(registry, state_dir=str(tmp_path))
    first = orchestrator.run("Analizar objetivo")
    second = orchestrator.run("Analizar objetivo")

    assert first["task_report"]["status_distribution"]["blocked"] == 2
    assert any(
        proposal["kind"] == "repeated_block"
        for proposal in second["improvement_proposals"]
    )
