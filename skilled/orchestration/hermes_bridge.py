"""Explicit opt-in bridge from a Hermes hook to autonomous task execution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from reasoning.claude_code_executor import ClaudeCodeExecutor
from reasoning.task_router import Task
from sharememory.hermes_memory.knowledge_broker import KnowledgeBroker
from sharememory.hermes_memory.work_memory import WorkMemoryRecorder

from .autonomous_orchestrator import AgentRegistry, AutonomousOrchestrator


COMMAND_PREFIX = "/orchestrate "


def is_orchestration_request(message: str) -> bool:
    return isinstance(message, str) and message.strip().lower().startswith(
        COMMAND_PREFIX
    )


def run_from_hermes(
    message: str,
    *,
    repository_path: Optional[str] = None,
    state_dir: Optional[str] = None,
    executor: Optional[Callable[[Task], Any]] = None,
) -> Dict[str, Any]:
    """Run an explicit `/orchestrate` request; ordinary chat never executes."""
    if not is_orchestration_request(message):
        raise ValueError("Not an explicit Hermes orchestration request")
    objective = message.strip()[len(COMMAND_PREFIX) :].strip()
    if not objective:
        raise ValueError("The orchestration objective is empty")
    repository = Path(
        repository_path or os.getenv("HERMES_AUTONOMY_REPOSITORY") or "."
    ).expanduser().resolve()
    selected_state = Path(
        state_dir
        or os.getenv("HERMES_AUTONOMY_STATE_DIR")
        or (Path.home() / ".hermes" / "state" / "ai-ecosystem")
    ).expanduser().resolve()
    expected_path = os.getenv("HERMES_AUTONOMY_VERIFY_FILE")
    expected_content = os.getenv("HERMES_AUTONOMY_VERIFY_CONTENT")
    require_structured = not bool(expected_path and expected_content is not None)
    selected_executor = executor or ClaudeCodeExecutor(
        str(repository),
        require_structured_output=require_structured,
    )
    registry = AgentRegistry()
    # Claude Code is an external worker. Task-type aliases allow the same
    # worker to execute every stage while TaskRouter preserves role evidence.
    for role, task_types in {
        "researcher": ["analysis", "research"],
        "orchestrator": ["design", "planning", "orchestration"],
        "builder": ["implementation", "bugfix"],
        "qa": ["qa", "verification"],
        "km-agent": ["documentation", "knowledge"],
    }.items():
        registry.register(
            role,
            selected_executor,
            task_types=task_types,
            external=True,
        )
    memory = WorkMemoryRecorder(
        KnowledgeBroker(str(selected_state / "memory"))
    )
    verifier = None
    if expected_path and expected_content is not None:
        verification_target = (repository / expected_path).resolve()
        if repository not in verification_target.parents:
            raise ValueError("Verification file must stay inside the repository")

        def verifier(task: Task, result: Any) -> Dict[str, Any]:
            actual = (
                verification_target.read_text(encoding="utf-8")
                if verification_target.is_file()
                else None
            )
            verified = bool(result.get("success")) and actual == expected_content
            return {
                "status": "verified" if verified else "failed",
                "confidence": 1.0,
                "details": [
                    "Archivo comprobado independientemente"
                    if verified
                    else "El archivo independiente no coincide"
                ],
                "recommendations": [],
            }

    return AutonomousOrchestrator(
        registry,
        state_dir=str(selected_state),
        memory_recorder=memory,
    ).run(objective, {"persist": True}, verifier=verifier)


__all__ = ["COMMAND_PREFIX", "is_orchestration_request", "run_from_hermes"]
