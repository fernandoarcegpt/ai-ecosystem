#!/usr/bin/env python3
"""Verify the real TaskRouter -> Claude Code path in a temporary repository."""

from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from reasoning.claude_code_executor import ClaudeCodeExecutor
from reasoning.task_router import Task, TaskRouter, TaskStatus


EXPECTED = "CLAUDE_CODE_LIVE_OK\n"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="claude-code-live-") as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        (repository / "README.md").write_text(
            "# Repositorio temporal de verificación\n",
            encoding="utf-8",
        )
        now = datetime.now(timezone.utc).isoformat()
        task = Task(
            id="claude-code-live",
            description=(
                "Crea claude_live_probe.txt con el contenido exacto "
                "CLAUDE_CODE_LIVE_OK seguido de un salto de línea. "
                "Lee el archivo para verificarlo. No modifiques otro archivo."
            ),
            type="implementation",
            priority=1,
            dependencies=[],
            assigned_agent=None,
            status=TaskStatus.PROPOSED,
            constraints=["Trabajar únicamente en el repositorio temporal"],
            metadata={},
            created_at=now,
            updated_at=now,
        )
        executor = ClaudeCodeExecutor(
            str(repository),
            timeout_seconds=300,
            max_turns=8,
        )
        router = TaskRouter(executors={"builder": executor})

        def verify(item: Task, result: Any) -> Dict[str, Any]:
            check = router.verify_task_result(item, result)
            probe = repository / "claude_live_probe.txt"
            actual = probe.read_text(encoding="utf-8") if probe.exists() else None
            if actual != EXPECTED:
                check.update(status="failed", confidence=1.0)
                check["details"].append(
                    "La comprobación independiente del archivo no coincidió"
                )
            return check

        report = router.execute_available([task], verifier=verify)
        result = task.metadata.get("result", {})
        probe = repository / "claude_live_probe.txt"
        actual = probe.read_text(encoding="utf-8") if probe.exists() else None
        evidence = {
            "status": task.status.value,
            "assigned_agent": task.assigned_agent,
            "session_id": result.get("session_id"),
            "tests_passed": result.get("tests_passed"),
            "file_verified_independently": actual == EXPECTED,
            "permission_denials": result.get("permission_denials", []),
            "report_completed": report["status_distribution"]["completed"],
            "error": result.get("error"),
        }
        print(json.dumps(evidence, indent=2, ensure_ascii=False))
        if task.status != TaskStatus.COMPLETED or actual != EXPECTED:
            print("ERROR: integración real TaskRouter -> Claude Code no verificada")
            return 1

    print("PASS: Claude Code ejecutó una tarea real mediante TaskRouter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
