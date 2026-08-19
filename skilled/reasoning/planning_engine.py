"""Planificación clásica verificable con Unified Planning + Pyperplan."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from unified_planning.engines import PlanGenerationResultStatus
from unified_planning.shortcuts import BoolType, Fluent, InstantaneousAction, Not, OneshotPlanner, Problem

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class PlanningEngineAdapter:
    name = "unified_planning"
    capabilities: Sequence[ReasoningCapability] = (ReasoningCapability.PLANNING,)
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("planning_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        spec = self._spec(problem)
        return profile.requires(ReasoningCapability.PLANNING) and bool(
            spec.get("fluents") and spec.get("actions") and spec.get("goals")
        )

    def execute(self, problem: Any, context: Optional[Dict[str, Any]] = None) -> EngineResult:
        spec = self._spec(problem)
        try:
            fluent_names = [str(name) for name in spec.get("fluents", [])]
            if not fluent_names:
                raise ValueError("planning_spec.fluents is required")
            if not spec.get("actions"):
                raise ValueError("planning_spec.actions is required")
            if not spec.get("goals"):
                raise ValueError("planning_spec.goals is required")

            up_problem = Problem(str(spec.get("name") or "formal_plan"))
            fluents = {
                name: Fluent(name, BoolType())
                for name in fluent_names
            }
            for fluent in fluents.values():
                up_problem.add_fluent(fluent, default_initial_value=False)

            initial_true = {str(name) for name in spec.get("initial_true", [])}
            unknown_initial = initial_true - set(fluents)
            if unknown_initial:
                raise ValueError(f"Unknown initial fluents: {sorted(unknown_initial)}")
            for name in initial_true:
                up_problem.set_initial_value(fluents[name], True)

            for action_spec in spec.get("actions", []):
                action = InstantaneousAction(str(action_spec["name"]))
                for name in action_spec.get("preconditions", []):
                    name = str(name)
                    if name not in fluents:
                        raise ValueError(f"Unknown precondition fluent: {name}")
                    action.add_precondition(fluents[name])
                for name in action_spec.get("negative_preconditions", []):
                    name = str(name)
                    if name not in fluents:
                        raise ValueError(f"Unknown negative precondition fluent: {name}")
                    action.add_precondition(Not(fluents[name]))
                for name in action_spec.get("add", []):
                    name = str(name)
                    if name not in fluents:
                        raise ValueError(f"Unknown add-effect fluent: {name}")
                    action.add_effect(fluents[name], True)
                for name in action_spec.get("delete", []):
                    name = str(name)
                    if name not in fluents:
                        raise ValueError(f"Unknown delete-effect fluent: {name}")
                    action.add_effect(fluents[name], False)
                up_problem.add_action(action)

            for name in spec.get("goals", []):
                name = str(name)
                if name not in fluents:
                    raise ValueError(f"Unknown goal fluent: {name}")
                up_problem.add_goal(fluents[name])

            with OneshotPlanner(name="pyperplan") as planner:
                result = planner.solve(up_problem)

            solved_statuses = {
                PlanGenerationResultStatus.SOLVED_SATISFICING,
                PlanGenerationResultStatus.SOLVED_OPTIMALLY,
            }
            solved = result.status in solved_statuses and result.plan is not None
            actions = []
            if result.plan is not None:
                actions = [
                    action_instance.action.name
                    for action_instance in result.plan.actions
                ]

            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={
                    "planner": "pyperplan",
                    "planner_status": str(result.status),
                    "plan_found": solved,
                    "actions": actions,
                    "goal_count": len(spec.get("goals", [])),
                },
                evidence={"plan": actions},
                validation={"valid": solved, "goal_reached": solved},
                transfer_payload={"ordered_actions": actions},
                deterministic=True,
            )
        except Exception as exc:
            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="formalization_error",
                formalization_errors=[str(exc)],
                validation={"valid": False},
                deterministic=True,
            )
