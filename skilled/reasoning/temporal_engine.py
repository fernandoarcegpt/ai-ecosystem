"""Razonamiento temporal verificable sobre intervalos usando Z3."""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence

from z3 import Int, Or, Solver, sat

from .engine_contracts import EngineResult, ReasoningCapability, ReasoningProfile


class TemporalEngineAdapter:
    name = "z3_temporal"
    capabilities: Sequence[ReasoningCapability] = (ReasoningCapability.TEMPORAL,)
    priority = 50

    def _spec(self, problem: Any) -> Dict[str, Any]:
        indicators = dict(getattr(problem, "structural_indicators", {}) or {})
        return dict(indicators.get("temporal_spec") or {})

    def can_handle(self, problem: Any, profile: ReasoningProfile) -> bool:
        return profile.requires(ReasoningCapability.TEMPORAL) and bool(
            self._spec(problem).get("tasks")
        )

    def execute(self, problem: Any, context: Optional[Dict[str, Any]] = None) -> EngineResult:
        spec = self._spec(problem)
        try:
            tasks = dict(spec.get("tasks") or {})
            if not tasks:
                raise ValueError("temporal_spec.tasks is required")

            solver = Solver()
            starts = {}
            ends = {}
            durations = {}
            for name, raw in tasks.items():
                name = str(name)
                duration = int((raw or {}).get("duration", 0))
                if duration <= 0:
                    raise ValueError(f"Task duration must be positive: {name}")
                start = Int(f"start_{name}")
                end = Int(f"end_{name}")
                starts[name], ends[name], durations[name] = start, end, duration
                solver.add(start >= 0)
                solver.add(end == start + duration)

            for before in spec.get("before", []):
                left, right = map(str, before)
                if left not in tasks or right not in tasks:
                    raise ValueError(f"Unknown task in precedence: {before}")
                solver.add(ends[left] <= starts[right])

            for pair in spec.get("non_overlap", []):
                left, right = map(str, pair)
                if left not in tasks or right not in tasks:
                    raise ValueError(f"Unknown task in non_overlap: {pair}")
                solver.add(Or(ends[left] <= starts[right], ends[right] <= starts[left]))

            for name, deadline in dict(spec.get("deadlines") or {}).items():
                name = str(name)
                if name not in tasks:
                    raise ValueError(f"Unknown task deadline: {name}")
                solver.add(ends[name] <= int(deadline))

            for name, release in dict(spec.get("release_times") or {}).items():
                name = str(name)
                if name not in tasks:
                    raise ValueError(f"Unknown task release time: {name}")
                solver.add(starts[name] >= int(release))

            status = solver.check()
            satisfiable = status == sat
            schedule = {}
            if satisfiable:
                model = solver.model()
                for name in tasks:
                    schedule[name] = {
                        "start": model.eval(starts[name]).as_long(),
                        "end": model.eval(ends[name]).as_long(),
                        "duration": durations[name],
                    }

            return EngineResult(
                engine=self.name,
                capabilities=tuple(self.capabilities),
                status="success",
                data={
                    "solution_status": "satisfiable" if satisfiable else "unsatisfiable",
                    "schedule": schedule,
                },
                evidence={"schedule": schedule},
                validation={"valid": True, "satisfiable": satisfiable},
                transfer_payload={"schedule": schedule},
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
