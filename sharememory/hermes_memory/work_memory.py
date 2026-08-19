"""Captura de resultados de trabajo validados en la memoria persistente."""

from __future__ import annotations

import json
from typing import Any, Dict

from .knowledge_broker import KnowledgeBroker


class WorkMemoryRecorder:
    """Registra únicamente resultados que ya pasaron una verificación."""

    def __init__(self, broker: KnowledgeBroker):
        self.broker = broker

    def record_task_result(self, task: Any, result: Any, verification: Dict[str, Any]) -> Dict[str, Any]:
        if verification.get("status") != "verified":
            raise ValueError("Only verified task results can be stored")
        content = json.dumps(
            {"task_id": task.id, "description": task.description, "result": result, "verification": verification},
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
        return self.broker.store(
            content=content,
            entry_type="task_outcome",
            metadata={
                "task_id": task.id,
                "task_type": task.type,
                "assigned_agent": task.assigned_agent,
                "verification_confidence": verification.get("confidence"),
            },
            tags=["work", "verified", task.type],
            source="task-router",
            identity_key=f"task:{task.id}",
        )


__all__ = ["WorkMemoryRecorder"]
