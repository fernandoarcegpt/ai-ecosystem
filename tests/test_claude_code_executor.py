"""Tests for the opt-in Claude Code TaskRouter executor."""

import json

from reasoning.claude_code_executor import ClaudeCodeExecutor
from reasoning.task_router import TaskRouter, TaskStatus

from tests.test_task_execution import _task


def test_claude_code_executor_completes_implementation_task(tmp_path):
    fake_claude = tmp_path / "claude"
    payload = {
        "session_id": "session-1",
        "total_cost_usd": 0.12,
        "structured_output": {
            "completed": True,
            "summary": "Cambio implementado",
            "tests_passed": True,
            "evidence": ["pytest: 3 passed"],
            "files_changed": ["module.py"],
        },
    }
    fake_claude.write_text(
        "#!/usr/bin/env python3\n"
        f"print({json.dumps(json.dumps(payload))})\n",
        encoding="utf-8",
    )
    fake_claude.chmod(0o755)

    executor = ClaudeCodeExecutor(
        str(tmp_path),
        binary=str(fake_claude),
        timeout_seconds=5,
    )
    task = _task("implementation", task_type="implementation")
    router = TaskRouter(executors={"builder": executor})
    report = router.execute_available([task])

    assert task.status == TaskStatus.COMPLETED
    assert task.metadata["result"]["session_id"] == "session-1"
    assert task.metadata["result"]["tests_passed"] is True
    assert report["status_distribution"]["completed"] == 1


def test_claude_code_executor_fails_explicitly_when_binary_is_missing(tmp_path):
    executor = ClaudeCodeExecutor(
        str(tmp_path),
        binary="definitely-not-a-real-claude-binary",
    )
    result = executor(_task("implementation", task_type="implementation"))
    assert result["success"] is False
    assert result["error"] == "claude_code_unavailable"
