"""Auditable multi-agent orchestration with memory and improvement feedback."""

from __future__ import annotations

import json
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from improvement.continuous_improvement import ContinuousImprovementAgent
from reasoning.operational_decision import decide_operation
from reasoning.task_router import Task, TaskRouter


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AgentRegistration:
    name: str
    task_types: List[str]
    external: bool = False


class AgentRegistry:
    """Keep agent metadata and executable implementations in one registry."""

    def __init__(self) -> None:
        self._agents: Dict[str, AgentRegistration] = {}
        self._executors: Dict[str, Callable[[Task], Any]] = {}

    def register(
        self,
        name: str,
        executor: Callable[[Task], Any],
        *,
        task_types: Iterable[str] = (),
        external: bool = False,
    ) -> None:
        if not name.strip() or not callable(executor):
            raise ValueError("An agent needs a name and a callable executor")
        self._agents[name] = AgentRegistration(
            name=name,
            task_types=list(dict.fromkeys(task_types)),
            external=external,
        )
        self._executors[name] = executor

    def executors(self) -> Dict[str, Callable[[Task], Any]]:
        result = dict(self._executors)
        for name, registration in self._agents.items():
            for task_type in registration.task_types:
                result.setdefault(task_type, self._executors[name])
        return result

    def describe(self) -> List[Dict[str, Any]]:
        return [asdict(self._agents[name]) for name in sorted(self._agents)]


class AutonomousOrchestrator:
    """Connect decision, task execution, memory and bounded self-improvement."""

    def __init__(
        self,
        registry: AgentRegistry,
        *,
        state_dir: Optional[str] = None,
        memory_recorder: Optional[Any] = None,
        human_gate: Optional[Any] = None,
        improvement_agent: Optional[ContinuousImprovementAgent] = None,
    ) -> None:
        selected = Path(state_dir).expanduser() if state_dir else Path(
            tempfile.mkdtemp(prefix="hermes-orchestration-")
        )
        self.state_dir = selected.resolve()
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.registry = registry
        self.improvement_agent = improvement_agent or ContinuousImprovementAgent()
        self.router = TaskRouter(
            store_path=str(self.state_dir / "tasks.json"),
            memory_recorder=memory_recorder,
            human_gate=human_gate,
            executors=registry.executors(),
        )
        self.history_path = self.state_dir / "run-history.json"

    def _history(self) -> List[Dict[str, Any]]:
        if not self.history_path.exists():
            return []
        try:
            payload = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        return payload if isinstance(payload, list) else []

    def _save_history(self, history: List[Dict[str, Any]]) -> None:
        target = self.history_path
        temporary = target.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(history, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        temporary.replace(target)

    def run(self, objective: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        decision = decide_operation(objective, context)
        tasks = self.router.decompose_objective(objective)
        report = self.router.execute_available(tasks)
        history = self._history()
        improvement_inputs = [item["task_report"] for item in history]
        improvement_inputs.append(report)
        proposals = self.improvement_agent.analyze_task_reports(improvement_inputs)
        record = {
            "timestamp": _now(),
            "objective": objective,
            "decision": decision,
            "agents": self.registry.describe(),
            "task_report": report,
            "improvement_proposals": proposals,
        }
        history.append(record)
        self._save_history(history)
        return record


__all__ = ["AgentRegistry", "AgentRegistration", "AutonomousOrchestrator"]
