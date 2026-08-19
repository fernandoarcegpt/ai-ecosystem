"""Acceptance tests for the centralized operational decision tree."""

from reasoning.operational_decision import decide_operation


def test_implementation_routes_to_builder_repository_terminal_and_tests():
    decision = decide_operation("Implementar y probar el cambio en el repositorio")
    assert decision["action"] == "decompose_and_execute"
    assert decision["agent"] == "builder"
    assert decision["task_type"] == "implementation"
    assert {"repository", "terminal"} <= set(decision["tools"])
    assert "tests" in decision["verification"]


def test_graph_request_routes_to_neurosymbolic_engine():
    decision = decide_operation(
        "Organiza las tareas respetando dependencias y detecta ciclos"
    )
    assert decision["symbolic_engine"] == "networkx"
    assert "neurosymbolic" in decision["tools"]


def test_continuation_uses_memory():
    decision = decide_operation(
        "Continúa el trabajo anterior",
        {"continuation": True, "project_id": "ecosystem"},
    )
    assert decision["use_memory"] is True
    assert "memory" in decision["tools"]


def test_missing_required_data_escalates_with_reason():
    decision = decide_operation(
        "Generar el informe",
        {"missing_required_data": ["criterio de negocio"]},
    )
    assert decision["action"] == "human_review"
    assert decision["requires_human"] is True
    assert "criterio de negocio" in decision["reasons"][0]
