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
MAX_ATTEMPTS = 2


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="claude-code-live-") as directory:
        repository = Path(directory)
        subprocess.run(["git", "init", "-q"], cwd=repository, check=True)
        (repository / "README.md").write_text(
            "# Repositorio temporal de verificación\n",
            encoding="utf-8",
        )
        now = datetime.now(timezone.utc).isoformat()
        executor = ClaudeCodeExecutor(
            str(repository),
            timeout_seconds=300,
            max_turns=8,
            require_structured_output=False,
        )
        probe = repository / "claude_live_probe.txt"
        attempts = []
        passed = False

        for attempt in range(1, MAX_ATTEMPTS + 1):
            correction = (
                " Un intento anterior declaró éxito, pero la comprobación "
                "independiente no encontró el contenido requerido; corrígelo "
                "realmente con una herramienta de escritura."
                if attempt > 1
                else ""
            )
            task = Task(
                id=f"claude-code-live-{attempt}",
                description=(
                    f"En el directorio absoluto {repository}, crea realmente "
                    "claude_live_probe.txt con el contenido exacto "
                    "CLAUDE_CODE_LIVE_OK seguido de un único salto de línea. "
                    "Después lee el archivo y comprueba sus bytes. No basta "
                    "con describir la acción ni declarar éxito."
                    + correction
                ),
                type="implementation",
                priority=1,
                dependencies=[],
                assigned_agent=None,
                status=TaskStatus.PROPOSED,
                constraints=[
                    f"Trabajar únicamente en {repository}",
                    "No declarar completed si el archivo no existe",
                ],
                metadata={},
                created_at=now,
                updated_at=now,
            )
            router = TaskRouter(executors={"builder": executor})

            def verify(item: Task, result: Any) -> Dict[str, Any]:
                actual = (
                    probe.read_text(encoding="utf-8") if probe.exists() else None
                )
                verified = bool(result.get("success")) and actual == EXPECTED
                return {
                    "status": "verified" if verified else "failed",
                    "confidence": 1.0,
                    "details": [
                        "Archivo comprobado independientemente"
                        if verified
                        else "La comprobación independiente no coincidió"
                    ],
                    "recommendations": [],
                }

            report = router.execute_available([task], verifier=verify)
            result = task.metadata.get("result", {})
            actual = probe.read_text(encoding="utf-8") if probe.exists() else None
            attempt_evidence = {
                "attempt": attempt,
                "status": task.status.value,
                "assigned_agent": task.assigned_agent,
                "session_id": result.get("session_id"),
                "tests_passed": result.get("tests_passed"),
                "file_verified_independently": actual == EXPECTED,
                "permission_denials": result.get("permission_denials", []),
                "report_completed": report["status_distribution"]["completed"],
                "error": result.get("error"),
                "summary": result.get("summary"),
                "files_changed": result.get("files_changed", []),
            }
            attempts.append(attempt_evidence)
            if task.status == TaskStatus.COMPLETED and actual == EXPECTED:
                passed = True
                break

        evidence = {"passed": passed, "attempts": attempts}
        print(json.dumps(evidence, indent=2, ensure_ascii=False))
        if not passed:
            print("ERROR: integración real TaskRouter -> Claude Code no verificada")
            return 1

    print("PASS: Claude Code ejecutó una tarea real mediante TaskRouter")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
