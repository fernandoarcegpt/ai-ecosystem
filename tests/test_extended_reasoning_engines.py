from types import SimpleNamespace

from skilled.reasoning.engine_contracts import ReasoningCapability, ReasoningProfile
from skilled.reasoning.extended_engine_registry import build_extended_engine_registry
from skilled.reasoning.planning_engine import PlanningEngineAdapter
from skilled.reasoning.spatial_engine import SpatialEngineAdapter
from skilled.reasoning.temporal_engine import TemporalEngineAdapter


def _problem(**indicators):
    return SimpleNamespace(
        mode=SimpleNamespace(value="none"),
        relations=[],
        facts=[],
        rules=[],
        constraints=[],
        items=[],
        people=[],
        structural_indicators=indicators,
    )


def test_classical_planner_finds_real_two_step_plan():
    problem = _problem(
        required_capabilities=["planning"],
        planning_spec={
            "name": "move_between_locations",
            "fluents": ["at_a", "at_b", "at_c"],
            "initial_true": ["at_a"],
            "goals": ["at_c"],
            "actions": [
                {
                    "name": "move_a_b",
                    "preconditions": ["at_a"],
                    "add": ["at_b"],
                    "delete": ["at_a"],
                },
                {
                    "name": "move_b_c",
                    "preconditions": ["at_b"],
                    "add": ["at_c"],
                    "delete": ["at_b"],
                },
            ],
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    result = PlanningEngineAdapter().execute(problem)

    assert profile.requires("planning")
    assert result.status == "success"
    assert result.data["plan_found"] is True
    assert result.data["actions"] == ["move_a_b", "move_b_c"]
    assert result.validation["goal_reached"] is True


def test_temporal_engine_respects_precedence_deadline_and_duration():
    problem = _problem(
        required_capabilities=["temporal"],
        temporal_spec={
            "tasks": {
                "review": {"duration": 3},
                "approve": {"duration": 2},
            },
            "before": [["review", "approve"]],
            "deadlines": {"approve": 8},
        },
    )
    result = TemporalEngineAdapter().execute(problem)

    assert result.status == "success"
    assert result.data["solution_status"] == "satisfiable"
    schedule = result.data["schedule"]
    assert schedule["review"]["end"] <= schedule["approve"]["start"]
    assert schedule["approve"]["end"] <= 8
    assert schedule["review"]["end"] - schedule["review"]["start"] == 3


def test_temporal_engine_reports_unsatisfiable_model_as_valid_solver_result():
    problem = _problem(
        required_capabilities=["temporal"],
        temporal_spec={
            "tasks": {"A": {"duration": 5}},
            "release_times": {"A": 4},
            "deadlines": {"A": 7},
        },
    )
    result = TemporalEngineAdapter().execute(problem)

    assert result.status == "success"
    assert result.data["solution_status"] == "unsatisfiable"
    assert result.validation["valid"] is True
    assert result.validation["satisfiable"] is False


def test_spatial_engine_executes_topological_and_geodesic_queries():
    problem = _problem(
        required_capabilities=["spatial"],
        spatial_spec={
            "geometries": {
                "area": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]],
                },
                "inside": {"type": "Point", "coordinates": [1, 1]},
                "outside": {"type": "Point", "coordinates": [3, 3]},
                "lima_a": {"type": "Point", "coordinates": [-77.04, -12.05]},
                "lima_b": {"type": "Point", "coordinates": [-77.03, -12.05]},
            },
            "queries": [
                {"op": "contains", "left": "area", "right": "inside"},
                {"op": "contains", "left": "area", "right": "outside"},
                {"op": "geodesic_distance_m", "left": "lima_a", "right": "lima_b"},
            ],
        },
    )
    result = SpatialEngineAdapter().execute(problem)

    assert result.status == "success"
    queries = result.data["queries"]
    assert queries[0]["value"] is True
    assert queries[1]["value"] is False
    assert 1000 < queries[2]["value"] < 1200


def test_extended_registry_covers_step_two_capabilities_without_future_engines():
    problem = _problem(
        required_capabilities=["planning", "temporal", "spatial"],
        planning_spec={"fluents": ["x"], "actions": [{"name": "set_x", "add": ["x"]}], "goals": ["x"]},
        temporal_spec={"tasks": {"A": {"duration": 1}}},
        spatial_spec={
            "geometries": {
                "a": {"type": "Point", "coordinates": [0, 0]},
                "b": {"type": "Point", "coordinates": [1, 1]},
            },
            "queries": [{"op": "distance", "left": "a", "right": "b"}],
        },
    )
    profile = ReasoningProfile.from_problem(problem)
    registry = build_extended_engine_registry()

    plan = registry.build_plan(profile, problem)

    assert set(plan) == {"unified_planning", "z3_temporal", "shapely_pyproj"}
    assert registry.get("unified_planning") is not None
    assert registry.get("z3_temporal") is not None
    assert registry.get("shapely_pyproj") is not None
    assert not profile.requires(ReasoningCapability.PROBABILISTIC)
