"""Criterios de aceptación del razonamiento neurosimbólico."""

from reasoning.neuro_symbolic_engine import execute_symbolic_analysis, get_coordinator


def test_arrow_chain_preserves_every_edge_and_detects_cycle():
    result = execute_symbolic_analysis(
        "Detecta el ciclo del grafo A -> B -> C -> A",
        {},
        "networkx",
    )
    assert result["status"] == "success"
    graph = result["results"]
    assert set(map(tuple, graph["graph_analysis"]["edges"])) == {
        ("A", "B"), ("B", "C"), ("C", "A")
    }
    assert graph["is_acyclic"] is False
    assert any(set(cycle) == {"A", "B", "C"} for cycle in graph["cycles_found"])


def test_parent_rules_derive_transitive_ancestor():
    result = execute_symbolic_analysis(
        "Ana es madre de Luis y Luis es padre de Marta",
        {},
        "pydatalog",
    )
    assert result["status"] == "success"
    derived = {
        tuple(fact["args"])
        for fact in result["results"]["derived_facts"]
        if fact["predicate"] == "ancestor"
    }
    assert ("Ana", "Marta") in derived


def test_arithmetic_constraints_return_real_sat_model():
    result = execute_symbolic_analysis(
        "Resolver restricciones",
        {"constraints": ["x + y = 10", "x >= 1", "y >= 1"]},
        "z3",
    )
    assert result["status"] == "success"
    solved = result["results"]
    assert solved["solution_status"] == "satisfiable"
    assert solved["solution_values"]["x"] + solved["solution_values"]["y"] == 10
    assert solved["solution_values"]["x"] >= 1
    assert solved["solution_values"]["y"] >= 1


def test_contradiction_is_a_successful_unsat_result():
    result = execute_symbolic_analysis(
        "Detectar contradicción",
        {"constraints": ["x > 10", "x < 5"]},
        "z3",
    )
    assert result["status"] == "success"
    assert result["results"]["solution_status"] == "unsatisfiable"


def test_impossible_assignment_returns_unsat_without_inventing_people():
    result = execute_symbolic_analysis(
        "Reparte A,B,C entre Ana,Luis. Máximo una tarea por persona.",
        {
            "items": ["A", "B", "C"],
            "people": ["Ana", "Luis"],
            "constraints": [{"type": "max_items_per_person", "value": 1}],
        },
        "z3",
    )
    assert result["status"] == "success"
    assert result["results"]["solution_status"] == "unsatisfiable"


def test_flat_dependency_names_do_not_create_edges():
    result = execute_symbolic_analysis(
        "Analiza dependencias",
        {"dependencies": ["build", "test", "deploy"]},
        "networkx",
    )
    assert result["status"] == "formalization_error"
    assert result["reasoning_applied"] is False


def test_status_reports_each_engine():
    status = get_coordinator().get_status()
    assert status["engines"] == {
        "networkx": True,
        "z3": True,
        "pydatalog": True,
    }
