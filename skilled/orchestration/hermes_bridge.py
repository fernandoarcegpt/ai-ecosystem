"""Explicit opt-in bridge from a Hermes hook to autonomous task execution."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from reasoning.claude_code_executor import ClaudeCodeExecutor
from reasoning.task_router import Task

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
    selected_executor = executor or ClaudeCodeExecutor(str(repository))
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
    return AutonomousOrchestrator(
        registry,
        state_dir=state_dir or os.getenv("HERMES_AUTONOMY_STATE_DIR"),
    ).run(objective, {"persist": True})


__all__ = ["COMMAND_PREFIX", "is_orchestration_request", "run_from_hermes"]
