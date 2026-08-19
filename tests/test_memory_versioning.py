"""Tests for separated legacy memory and versionable validated knowledge."""

import json

from sharememory.hermes_memory.basic_memory import BasicMemory
from sharememory.hermes_memory.knowledge_broker import KnowledgeBroker


def test_basic_memory_no_longer_collides_with_knowledge_broker(tmp_path):
    broker = KnowledgeBroker(str(tmp_path))
    broker.store(
        "resultado verificado",
        metadata={"verification_confidence": 0.9},
        tags=["verified"],
        source="test",
    )
    basic = BasicMemory(str(tmp_path))
    basic.store("preference", "compact")

    assert basic.retrieve("preference") == "compact"
    assert broker.search("resultado verificado")
    assert (tmp_path / "memory.json").exists()
    assert (tmp_path / "basic_memory.json").exists()


def test_export_contains_only_validated_high_confidence_entries(tmp_path):
    broker = KnowledgeBroker(str(tmp_path / "runtime"))
    accepted = broker.store(
        "decisión comprobada",
        metadata={"verification_confidence": 0.95},
        tags=["verified", "architecture"],
        source="task-router",
    )
    broker.store(
        "supuesto sin validar",
        metadata={"confidence": 0.99},
        tags=["draft"],
        source="analysis",
    )
    broker.store(
        "evidencia débil",
        metadata={"verification_confidence": 0.4},
        tags=["verified"],
        source="analysis",
    )

    output = tmp_path / "repository" / "validated-knowledge.json"
    report = broker.export_validated_snapshot(str(output))
    snapshot = json.loads(output.read_text(encoding="utf-8"))

    assert report["exported_entries"] == 1
    assert snapshot["schema_version"] == 1
    assert snapshot["entries"][0]["id"] == accepted["id"]
    assert snapshot["entries"][0]["source"] == "task-router"
