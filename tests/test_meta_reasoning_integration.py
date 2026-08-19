from skilled.reasoning.hermes_integration import HermesSymbolIntegration
from skilled.reasoning.meta_reasoning import profile_for_problem
from skilled.reasoning.symbolic_problem_schema import ReasoningMode, SymbolicProblem


def test_profile_infers_extended_capability_from_structured_spec():
    problem = SymbolicProblem(
        mode=ReasoningMode.NONE,
        structural_indicators={
            "temporal_spec": {
                "tasks": {"A": {"duration": 2}},
            }
        },
    )

    profile = profile_for_problem(problem)

    assert [capability.value for capability in profile.capabilities] == ["temporal"]


def test_extended_temporal_route_produces_grounded_contract():
    integration = HermesSymbolIntegration()
    context = {
        "required_capabilities": ["temporal"],
        "temporal_spec": {
            "tasks": {
                "A": {"duration": 2},
                "B": {"duration": 3},
            },
            "before": [["A", "B"]],
            "deadlines": {"B": 8},
        },
        "formalization_source": "test_fixture",
    }

    result = integration.intercept_task(
        "Resuelve estas restricciones temporales.",
        context,
    )

    assert result["status"] == "success"
    assert result["engine_used"] == "z3_temporal"
    assert result["analysis"]["meta_reasoning"] is True
    assert result["analysis"]["reasoning_plan"] == ["z3_temporal"]
    schedule = result["results"]["engine_results"]["z3_temporal"]["data"]["schedule"]
    assert schedule["A"]["end"] <= schedule["B"]["start"]
    assert schedule["B"]["end"] <= 8

    contract = integration.run_grounded_task(
        "Resuelve estas restricciones temporales.",
        context,
        run_id="temporal-meta-test",
    )
    assert contract["status"] == "success"
    assert contract["engines"] == {"z3_temporal": "success"}
    assert contract["reasoning_plan"] == ["z3_temporal"]
    assert contract["audit"]["unresolved_support"] == []
    assert "Resultado neurosimbólico verificable" in contract["rendered_markdown"]
    assert "restricciones temporales" in contract["claims"][0]["statement"].lower()


def test_extended_intent_without_spec_fails_closed_to_human_review():
    integration = HermesSymbolIntegration()
    prompt = (
        "Quiero usar Bayes y calcular la probabilidad posterior, pero todavía "
        "no tengo las probabilidades condicionales."
    )

    assert integration.should_use_symbolic_reasoning(prompt, {}) is True
    result = integration.intercept_task(prompt, {})

    assert result["status"] == "human_review"
    assert result["reasoning_applied"] is False
    assert result["analysis"]["meta_reasoning"] is True
    assert "probabilistic" in result["analysis"]["reasoning_profile"]["capabilities"]

    contract = integration.run_grounded_task(prompt, {}, run_id="incomplete-bayes")
    assert contract["status"] == "human_review"
    assert contract["claims"] == []
    assert "no concluyente" in contract["rendered_markdown"].lower()


def test_meta_reasoner_composes_spatial_then_temporal_and_records_transfers():
    integration = HermesSymbolIntegration()
    context = {
        "required_capabilities": ["spatial", "temporal"],
        "spatial_spec": {
            "geometries": {
                "area": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]],
                },
                "point": {"type": "Point", "coordinates": [5, 5]},
            },
            "queries": [
                {"op": "contains", "left": "area", "right": "point"},
            ],
        },
        "temporal_spec": {
            "tasks": {
                "inspect": {"duration": 2},
                "approve": {"duration": 1},
            },
            "before": [["inspect", "approve"]],
        },
    }

    result = integration.intercept_task(
        "Evalúa la intersección espacial y las restricciones temporales.",
        context,
    )

    assert result["status"] == "success"
    assert result["engine_used"] == "meta_combined"
    assert result["analysis"]["reasoning_plan"] == [
        "shapely_pyproj",
        "z3_temporal",
    ]
    assert result["results"]["validation"]["all_required_engines_succeeded"] is True
    assert [item["from"] for item in result["results"]["knowledge_transfers"]] == [
        "shapely_pyproj",
        "z3_temporal",
    ]
    spatial = result["results"]["engine_results"]["shapely_pyproj"]
    assert spatial["data"]["queries"][0]["value"] is True
