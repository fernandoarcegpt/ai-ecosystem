"""Enrutamiento y ejecución persistente de tareas para Hermes.

El módulo recibe ejecutores explícitos, respeta dependencias, verifica
resultados, persiste el estado y deja bloqueos accionables.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from .networkx_wrapper import GraphAnalyzer


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TaskStatus(Enum):
    PROPOSED = "proposed"
    IN_PROGRESS = "in_progress"
    PENDING_VERIFICATION = "pending_verification"
    VALIDATED = "validated"
    BLOCKED = "blocked"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass
class Task:
    id: str
    description: str
    type: str
    priority: int
    dependencies: List[str]
    assigned_agent: Optional[str]
    status: TaskStatus
    constraints: List[str]
    metadata: Dict[str, Any]
    created_at: str
    updated_at: str


@dataclass
class RouteDecision:
    agent: str
    confidence: float
    reason: str
    constraints_applied: List[str]


class TaskRouter:
    """Planifica, enruta, ejecuta y reanuda tareas verificables."""

    def __init__(self, store_path: Optional[str] = None, memory_recorder: Optional[Any] = None, human_gate: Optional[Any] = None):
        selected = store_path or os.getenv("HERMES_TASK_STORE")
        self.store_path = Path(selected).expanduser() if selected else None
        self.memory_recorder = memory_recorder
        self.human_gate = human_gate
        self.swarm_config = self._default_swarm_config()

    @staticmethod
    def _default_swarm_config() -> List[Dict[str, Any]]:
        return [
            {"id": "orchestrator", "capabilities": ["orchestration", "planning", "routing"], "preferredTaskTypes": ["orchestration", "planning", "design"]},
            {"id": "km-agent", "capabilities": ["knowledge", "documentation"], "preferredTaskTypes": ["knowledge", "documentation"]},
            {"id": "builder", "capabilities": ["implementation", "code", "tests"], "preferredTaskTypes": ["implementation", "bugfix"]},
            {"id": "researcher", "capabilities": ["research", "analysis", "synthesis"], "preferredTaskTypes": ["research", "analysis"]},
            {"id": "qa", "capabilities": ["qa", "smoke", "verification"], "preferredTaskTypes": ["qa", "verification"]},
            {"id": "reviewer", "capabilities": ["review", "regression"], "preferredTaskTypes": ["review"]},
        ]

    def decompose_objective(self, objective: str) -> List[Task]:
        """Crea un plan lineal mínimo con identificadores consistentes."""
        lower = objective.lower()
        if "verificar" in lower or "probar" in lower:
            templates = [("Verificar resultado", "qa")]
        elif "investigar" in lower:
            templates = [("Definir criterios", "analysis"), ("Investigar fuentes", "research"), ("Sintetizar hallazgos", "documentation")]
        elif "implementar" in lower or "corregir" in lower:
            templates = [("Analizar alcance", "analysis"), ("Diseñar cambio", "design"), ("Implementar cambio", "implementation"), ("Verificar cambio", "qa")]
        else:
            templates = [("Analizar objetivo", "analysis"), ("Producir resultado", "implementation"), ("Verificar resultado", "qa")]

        now = _now()
        prefix = uuid.uuid4().hex[:10]
        tasks: List[Task] = []
        previous_id: Optional[str] = None
        for index, (label, task_type) in enumerate(templates, start=1):
            task_id = f"task-{prefix}-{index}"
            tasks.append(Task(
                id=task_id,
                description=f"{label}: {objective}",
                type=task_type,
                priority=len(templates) - index + 1,
                dependencies=[previous_id] if previous_id else [],
                assigned_agent=None,
                status=TaskStatus.PROPOSED,
                constraints=[],
                metadata={"source_objective": objective},
                created_at=now,
                updated_at=now,
            ))
            previous_id = task_id
        self.save_tasks(tasks)
        return tasks

    def route_task(self, task: Task) -> RouteDecision:
        best: Dict[str, Any] = {"id": "orchestrator", "score": 0.25, "reasons": ["fallback"]}
        words = set(re.findall(r"\b\w+\b", task.description.lower()))
        for agent in self.swarm_config:
            score = 0.0
            reasons = []
            if task.type in agent.get("preferredTaskTypes", []):
                score += 0.7
                reasons.append(f"tipo {task.type}")
            overlap = words & set(agent.get("capabilities", []))
            score += min(len(overlap) * 0.1, 0.2)
            if overlap:
                reasons.append("capacidades " + ", ".join(sorted(overlap)))
            if score > best["score"]:
                best = {"id": agent["id"], "score": score, "reasons": reasons}
        return RouteDecision(str(best["id"]), min(float(best["score"]), 1.0), "; ".join(best["reasons"]), list(task.constraints))

    def verify_task_result(self, task: Task, result: Any) -> Dict[str, Any]:
        check: Dict[str, Any] = {"status": "verified", "confidence": 0.8, "details": [], "recommendations": []}
        if result is None:
            check.update(status="failed", confidence=0.0)
            check["details"].append("El ejecutor no produjo resultado")
        elif isinstance(result, dict) and result.get("success") is False:
            check.update(status="failed", confidence=0.95)
            check["details"].append("El ejecutor declaró el resultado fallido")
        elif task.type == "implementation" and not (isinstance(result, dict) and result.get("tests_passed") is True):
            check.update(status="needs_review", confidence=0.4)
            check["recommendations"].append("Adjuntar evidencia de pruebas")
        elif task.type == "qa" and not (isinstance(result, dict) and (result.get("tests_passed") is True or result.get("smoke_test_passed") is True)):
            check.update(status="needs_review", confidence=0.4)
            check["recommendations"].append("Adjuntar evidencia de QA")
        return check

    @staticmethod
    def _serialize_task(task: Task) -> Dict[str, Any]:
        data = asdict(task)
        data["status"] = task.status.value
        return data

    @staticmethod
    def _deserialize_task(data: Dict[str, Any]) -> Task:
        item = dict(data)
        item["status"] = TaskStatus(item["status"])
        return Task(**item)

    def save_tasks(self, tasks: Iterable[Task]) -> None:
        if self.store_path is None:
            return
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": 1, "updated_at": _now(), "tasks": [self._serialize_task(task) for task in tasks]}
        fd, temp_name = tempfile.mkstemp(prefix="tasks-", suffix=".tmp", dir=str(self.store_path.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2, ensure_ascii=False, default=str)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.store_path)
        except Exception:
            Path(temp_name).unlink(missing_ok=True)
            raise

    def load_tasks(self) -> List[Task]:
        if self.store_path is None or not self.store_path.exists():
            return []
        with self.store_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        return [self._deserialize_task(item) for item in payload.get("tasks", [])]

    def mark_blocked(self, task: Task, reason: str, required_action: str) -> Dict[str, Any]:
        task.status = TaskStatus.BLOCKED
        task.updated_at = _now()
        block = {"task_id": task.id, "reason": reason, "required_action": required_action, "blocked_at": task.updated_at}
        task.metadata["human_block"] = block
        if self.human_gate is not None:
            review = self.human_gate.submit_for_review(task.description, actor="task-router", metadata={"task_id": task.id, "reason": reason})
            block["review_id"] = review.review_id
        return block

    def resolve_block(self, task: Task, resolution: str) -> None:
        task.metadata["block_resolution"] = {"resolution": resolution, "resolved_at": _now()}
        task.metadata.pop("human_block", None)
        task.status = TaskStatus.PROPOSED
        task.updated_at = _now()

    def execute_available(self, tasks: List[Task], executors: Dict[str, Callable[[Task], Any]], verifier: Optional[Callable[[Task, Any], Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Ejecuta tareas listas; conserva bloqueos y permite reanudar después."""
        by_id = {task.id: task for task in tasks}
        progressed = True
        while progressed:
            progressed = False
            for task in sorted(tasks, key=lambda item: item.priority, reverse=True):
                if task.status != TaskStatus.PROPOSED:
                    continue
                missing = [dependency for dependency in task.dependencies if dependency not in by_id]
                if missing:
                    self.mark_blocked(task, f"Dependencias inexistentes: {missing}", "Corregir el plan")
                    progressed = True
                    continue
                states = [by_id[dependency].status for dependency in task.dependencies]
                if any(state in {TaskStatus.FAILED, TaskStatus.BLOCKED} for state in states):
                    self.mark_blocked(task, "Una dependencia no terminó correctamente", "Resolver la dependencia")
                    progressed = True
                    continue
                if not all(state == TaskStatus.COMPLETED for state in states):
                    continue

                decision = self.route_task(task)
                task.assigned_agent = decision.agent
                executor = executors.get(decision.agent) or executors.get(task.type)
                if executor is None:
                    self.mark_blocked(task, f"No hay ejecutor para {decision.agent}/{task.type}", "Asignar un ejecutor")
                    progressed = True
                    continue

                task.status = TaskStatus.IN_PROGRESS
                task.updated_at = _now()
                try:
                    result = executor(task)
                except Exception as exc:
                    task.status = TaskStatus.FAILED
                    task.metadata["execution_error"] = f"{type(exc).__name__}: {exc}"
                    task.updated_at = _now()
                    progressed = True
                    continue

                task.status = TaskStatus.PENDING_VERIFICATION
                check = (verifier or self.verify_task_result)(task, result)
                task.metadata["result"] = result
                task.metadata["verification"] = check
                task.status = TaskStatus.COMPLETED if check.get("status") == "verified" else TaskStatus.FAILED
                task.updated_at = _now()
                if task.status == TaskStatus.COMPLETED and self.memory_recorder is not None:
                    task.metadata["memory_entry_id"] = self.memory_recorder.record_task_result(task, result, check)["id"]
                progressed = True
            self.save_tasks(tasks)
        return self.generate_task_report(tasks)

    def generate_task_report(self, tasks: List[Task]) -> Dict[str, Any]:
        task_ids = {task.id for task in tasks}
        graph = GraphAnalyzer()
        graph.add_nodes(list(task_ids))
        for task in tasks:
            graph.add_edges([(dependency, task.id) for dependency in task.dependencies if dependency in task_ids])
        return {
            "timestamp": _now(),
            "total_tasks": len(tasks),
            "status_distribution": {status.value: sum(task.status == status for task in tasks) for status in TaskStatus},
            "cycles": graph.detect_cycles(),
            "human_blocks": [task.metadata["human_block"] for task in tasks if "human_block" in task.metadata],
        }


__all__ = ["RouteDecision", "Task", "TaskRouter", "TaskStatus"]
