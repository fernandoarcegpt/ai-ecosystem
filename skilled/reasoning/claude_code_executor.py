"""Claude Code executor adapter for TaskRouter.

The adapter uses Claude Code's documented non-interactive JSON mode and
returns the same result contract consumed by TaskRouter's verifier.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from .task_router import Task


RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "completed": {"type": "boolean"},
        "summary": {"type": "string"},
        "tests_passed": {"type": "boolean"},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "files_changed": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["completed", "summary", "tests_passed", "evidence"],
}


class ClaudeCodeExecutor:
    """Execute an implementation task through Claude Code print mode."""

    def __init__(
        self,
        repository_path: str,
        *,
        binary: Optional[str] = None,
        timeout_seconds: int = 1800,
        max_turns: int = 30,
        max_budget_usd: Optional[float] = None,
    ):
        self.repository_path = Path(repository_path).expanduser().resolve()
        selected_binary = binary or os.getenv("CLAUDE_CODE_BIN") or "claude"
        self.binary = shutil.which(selected_binary)
        self.timeout_seconds = timeout_seconds
        self.max_turns = max_turns
        self.max_budget_usd = max_budget_usd

    @property
    def available(self) -> bool:
        return self.binary is not None and self.repository_path.is_dir()

    def _prompt(self, task: Task) -> str:
        constraints = "\n".join(f"- {item}" for item in task.constraints)
        return (
            "Trabaja de forma autónoma sobre esta tarea del repositorio. "
            "Inspecciona antes de modificar, implementa, ejecuta pruebas, "
            "corrige regresiones y documenta evidencia. No declares éxito "
            "si las pruebas necesarias no pasaron.\n\n"
            f"ID: {task.id}\n"
            f"Tipo: {task.type}\n"
            f"Objetivo: {task.description}\n"
            f"Restricciones:\n{constraints or '- Ninguna adicional'}"
        )

    def __call__(self, task: Task) -> Dict[str, Any]:
        if not self.available:
            return {
                "success": False,
                "completed": False,
                "tests_passed": False,
                "error": "claude_code_unavailable",
                "evidence": [
                    "No se encontró el binario de Claude Code o el repositorio"
                ],
            }

        command = [
            str(self.binary),
            "-p",
            self._prompt(task),
            "--output-format",
            "json",
            "--json-schema",
            json.dumps(RESULT_SCHEMA, separators=(",", ":")),
            "--permission-mode",
            "acceptEdits",
            "--max-turns",
            str(self.max_turns),
        ]
        if self.max_budget_usd is not None:
            command.extend(["--max-budget-usd", str(self.max_budget_usd)])

        try:
            completed = subprocess.run(
                command,
                cwd=self.repository_path,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "completed": False,
                "tests_passed": False,
                "error": "claude_code_timeout",
                "evidence": [
                    f"La ejecución superó {self.timeout_seconds} segundos"
                ],
            }

        if completed.returncode != 0:
            return {
                "success": False,
                "completed": False,
                "tests_passed": False,
                "error": "claude_code_failed",
                "returncode": completed.returncode,
                "evidence": [completed.stderr.strip() or completed.stdout.strip()],
            }

        try:
            envelope = json.loads(completed.stdout)
        except json.JSONDecodeError:
            return {
                "success": False,
                "completed": False,
                "tests_passed": False,
                "error": "claude_code_invalid_json",
                "evidence": [completed.stdout[:2000]],
            }

        result = envelope.get("structured_output") or {}
        if not isinstance(result, dict):
            result = {}
        permission_denials = envelope.get("permission_denials") or []
        envelope_error = bool(envelope.get("is_error"))
        response = {
            **result,
            "success": bool(result.get("completed"))
            and not envelope_error
            and not permission_denials,
            "session_id": envelope.get("session_id"),
            "cost_usd": envelope.get("total_cost_usd"),
            "permission_denials": permission_denials,
            "terminal_reason": envelope.get("terminal_reason"),
        }
        if envelope_error:
            response.update(
                success=False,
                completed=False,
                tests_passed=False,
                error="claude_code_reported_error",
                evidence=[str(envelope.get("result") or "Claude reportó un error")],
            )
        elif permission_denials:
            response.update(
                success=False,
                completed=False,
                tests_passed=False,
                error="claude_code_permission_denied",
            )
        elif not result:
            response.update(
                success=False,
                completed=False,
                tests_passed=False,
                error="claude_code_missing_structured_output",
                evidence=[str(envelope.get("result") or "Sin salida estructurada")],
            )
        return response


def create_claude_code_executor(
    repository_path: str,
    **kwargs: Any,
) -> ClaudeCodeExecutor:
    """Factory kept explicit so external execution is always opt-in."""
    return ClaudeCodeExecutor(repository_path, **kwargs)


__all__ = ["ClaudeCodeExecutor", "create_claude_code_executor"]
