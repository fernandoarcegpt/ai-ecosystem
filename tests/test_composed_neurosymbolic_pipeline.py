"""Regresiones del pipeline neurosimbólico compuesto extremo a extremo."""

from skilled.reasoning.hermes_integration import HermesSymbolIntegration
from skilled.reasoning.grounded_result import build_grounded_contract
from skilled.reasoning.neuro_symbolic_engine import NeurosymbolicCoordinator
from skilled.reasoning.symbolic_problem_schema import ProblemExtractor
from skilled.reasoning.z3_solver_integration import ConstraintSolver


TRANSFER_PLAN_2027 = """
Plan de transferencias documentales 2027. RRHH tiene 60 cajas listas.
RRHH todavía no ha remitido el inventario definitivo. Contabilidad tiene 50
cajas listas. Contabilidad presenta inventario inconsistente. Dirección tiene
35 cajas listas. OCI tiene 15 cajas listas. El flujo es organizacion ->
inventario -> revision -> subsanacion -> conformidad -> transferencia ->
ocupacion_espacio. Si falta el inventario definitivo, la unidad queda
bloqueada. Si el inventario es inconsistente, la unidad requiere corrección.
Una unidad no puede recibirse si está bloqueada. Una unidad no puede recibirse
si requiere corrección. La capacidad disponible es 120 cajas. La
reorganización aumenta la capacidad en 80 cajas. La meta institucional es 9
transferencias. Se desconoce la duración de cada revisión.
"""


def test_transfer_plan_is_grounded_in_general_symbolic_problem():
    problem = ProblemExtractor.extract(TRANSFER_PLAN_2027)
    serialized = problem.to_dict()

    assert serialized["mode"] == "combined"
    assert serialized["relations"]
    assert serialized["facts"]
    assert serialized["rules"]
    assert serialized["constraints"]
    assert serialized["variables"]
    assert serialized["objectives"]
    assert serialized["assumptions"]
    assert serialized["unknowns"]
    assert serialized["queries"]
    assert serialized["provenance"]

    rendered = repr(serialized)
    for hallucinated in ("Hacienda", "Reconocimiento", "Tecnología"):
        assert hallucinated not in rendered

    assert ("missing_final_inventory", "RRHH") in problem.facts
    assert ("inventory_inconsistent", "Contabilidad") in problem.facts
    assert problem.objectives[0]["target"] == 9
    assert problem.assumptions[0]["id"] == (
        "listed_impediments_complete_for_scope"
    )
    assert all("source_text" in item for item in problem.provenance)


def test_combined_pipeline_transfers_knowledge_between_all_engines():
    result = NeurosymbolicCoordinator().execute_symbolic_reasoning(
        TRANSFER_PLAN_2027,
        {},
    ).to_dict()

    assert result["status"] == "success"
    assert result["engine_used"] == "combined"
    combined = result["results"]
    assert combined["required_engines"] == ["networkx", "pydatalog", "z3"]
    assert combined["executed_motors"] == ["networkx", "pydatalog", "z3"]
    assert combined["validation"]["required_engines_succeeded"] is True

    transfers = combined["knowledge_transfers"]
    assert [(item["from"], item["to"]) for item in transfers] == [
        ("networkx", "pydatalog"),
        ("pydatalog", "z3"),
    ]

    derived = combined["pydatalog_analysis"]["derived_facts"]
    assert {tuple([item["predicate"], *item["args"]]) for item in derived} >= {
        ("blocked", "RRHH"),
        ("requires_correction", "Contabilidad"),
        ("cannot_receive", "RRHH"),
        ("cannot_receive", "Contabilidad"),
    }

    z3_result = combined["z3_analysis"]
    assert z3_result["optimizer_used"] is True
    assert z3_result["solution_values"]["receive_RRHH"] is False
    assert z3_result["solution_values"]["receive_Contabilidad"] is False
    assert z3_result["solution_values"]["receive_Direccion"] is True
    assert z3_result["solution_values"]["receive_OCI"] is True
    assert z3_result["solution_values"]["reorganize"] is False


def test_combined_evidence_exposes_nested_engine_results():
    integration = HermesSymbolIntegration()
    result = integration.intercept_task(TRANSFER_PLAN_2027, {})
    evidence = integration.integrate_result_with_hermes_response(result)

    assert "MODO: combined" in evidence
    assert "- networkx: success" in evidence
    assert "- pydatalog: success" in evidence
    assert "- z3: success" in evidence
    assert "NETWORKX:" in evidence
    assert "PYDATALOG:" in evidence
    assert "Z3:" in evidence
    assert "TRANSFERENCIA ENTRE MOTORES:" in evidence
    assert "HECHOS NO DETERMINADOS:" in evidence
    assert "HUMAN_REVIEW: not_required" in evidence


def test_constraint_solver_returns_real_unsat_core():
    solver = ConstraintSolver()
    value = solver.add_integer_variable("capacity")
    assert solver.add_tracked_constraint(value >= 10, "minimum_capacity")
    assert solver.add_tracked_constraint(value <= 5, "maximum_capacity")

    result = solver.solve()

    assert result["status"] == "unsatisfiable"
    assert set(result["unsat_core"]) == {
        "minimum_capacity",
        "maximum_capacity",
    }


def test_grounded_transfer_contract_scopes_and_limits_every_claim():
    integration = HermesSymbolIntegration()
    result = integration.intercept_task(TRANSFER_PLAN_2027, {})
    contract = build_grounded_contract(result, run_id="grounded-test")

    assert contract["status"] == "success"
    assert contract["scope"]["entities"] == [
        "RRHH",
        "Contabilidad",
        "Dirección",
        "OCI",
    ]
    assert contract["summary"]["selected_units"] == ["Dirección", "OCI"]
    assert contract["summary"]["reorganization_used"] is False
    assert contract["summary"]["gap_to_target"] == 7
    assert all(claim["supported_by"] for claim in contract["claims"])
    assert contract["audit"]["unresolved_support"] == []
    support_index = contract["audit"]["support_index"]
    assert all(
        support_id in support_index
        for claim in contract["claims"]
        for support_id in claim["supported_by"]
    )

    rendered = contract["rendered_markdown"]
    assert "no limita el universo institucional" in rendered
    assert "Transferencia inmediata" not in rendered
    assert "Responsable:" not in rendered
    assert "Plazo sugerido" not in rendered


def test_grounded_contract_fails_closed_for_ambiguous_formalization():
    contract = HermesSymbolIntegration().run_grounded_task(
        "Ana depende de Luis",
        {},
        run_id="human-review-test",
    )

    assert contract["status"] == "human_review"
    assert contract["claims"] == []
    assert "no concluyente" in contract["rendered_markdown"]
    assert "No se emitió una conclusión operativa determinista" in (
        contract["rendered_markdown"]
    )


def test_combined_engine_failure_is_not_published_as_success(monkeypatch):
    coordinator = NeurosymbolicCoordinator()
    monkeypatch.setattr(
        coordinator,
        "_run_z3_reasoning",
        lambda problem, context: {
            "status": "error",
            "error": "simulated_z3_failure",
        },
    )

    result = coordinator.execute_symbolic_reasoning(
        TRANSFER_PLAN_2027,
        {},
    ).to_dict()
    contract = build_grounded_contract(result, run_id="partial-failure-test")

    assert result["status"] == "error"
    assert result["results"]["validation"]["required_engines_succeeded"] is False
    assert contract["status"] == "error"
    assert contract["claims"] == []
    assert "no concluyente" in contract["rendered_markdown"]
