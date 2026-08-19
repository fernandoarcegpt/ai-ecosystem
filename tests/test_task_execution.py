"""Pruebas del ciclo tarea -> verificación -> persistencia -> memoria."""

from agents.hermes.skills.human_gate.skill import HumanGate
from reasoning.task_router import Task, TaskRouter, TaskStatus
from sharememory.hermes_memory.knowledge_broker import KnowledgeBroker
from sharememory.hermes_memory.work_memory import WorkMemoryRecorder


def _task(task_id, task_type="analysis", dependencies=None, priority=1):
    return Task(
        id=task_id,
        description=f"Ejecutar {task_id}",
        type=task_type,
        priority=priority,
        dependencies=dependencies or [],
        assigned_agent=None,
        status=TaskStatus.PROPOSED,
        constraints=[],
        metadata={},
        created_at="2026-01-01T00:00:00+00:00",
        updated_at="2026-01-01T00:00:00+00:00",
    )


def test_execution_respects_dependencies_and_survives_restart(tmp_path):
    store = tmp_path / "tasks.json"
    router = TaskRouter(store_path=str(store))
    tasks = [_task("first", priority=2), _task("second", dependencies=["first"])]
    order = []

    def execute(task):
        order.append(task.id)
        return {"completed": True}

    report = router.execute_available(tasks, {"researcher": execute})
    assert order == ["first", "second"]
    assert report["status_distribution"]["completed"] == 2
    restored = TaskRouter(store_path=str(store)).load_tasks()
    assert [task.status for task in restored] == [TaskStatus.COMPLETED, TaskStatus.COMPLETED]


def test_one_missing_executor_creates_human_block_but_independent_work_continues(tmp_path):
    gate_path = tmp_path / "reviews.json"
    gate = HumanGate(storage_path=str(gate_path))
    router = TaskRouter(store_path=str(tmp_path / "tasks.json"), human_gate=gate)
    blocked = _task("blocked", task_type="qa", priority=2)
    runnable = _task("runnable", task_type="analysis", priority=1)

    report = router.execute_available([blocked, runnable], {"researcher": lambda task: {"completed": True}})
    assert blocked.status == TaskStatus.BLOCKED
    assert runnable.status == TaskStatus.COMPLETED
    assert report["human_blocks"][0]["required_action"] == "Asignar un ejecutor"
    assert report["human_blocks"][0]["evidence"]
    assert report["human_blocks"][0]["alternatives"]
    assert report["human_blocks"][0]["risks"]
    assert report["human_blocks"][0]["automatic_next"]
    assert report["human_blocks"][0]["state_reached"] == "proposed"
    assert len(HumanGate(storage_path=str(gate_path)).check_pending_reviews()) == 1


def test_resolved_block_can_resume(tmp_path):
    router = TaskRouter(store_path=str(tmp_path / "tasks.json"))
    task = _task("qa-task", task_type="qa")
    router.execute_available([task], {})
    assert task.status == TaskStatus.BLOCKED
    router.resolve_block(task, "Se asignó QA")
    router.execute_available([task], {"qa": lambda item: {"smoke_test_passed": True}})
    assert task.status == TaskStatus.COMPLETED


def test_human_approval_automatically_resumes_task_and_dependant(tmp_path):
    gate = HumanGate(storage_path=str(tmp_path / "reviews.json"))
    router = TaskRouter(
        store_path=str(tmp_path / "tasks.json"),
        human_gate=gate,
    )
    parent = _task("qa-task", task_type="qa", priority=2)
    dependant = _task(
        "after-qa",
        dependencies=["qa-task"],
        priority=1,
    )

    router.execute_available([parent, dependant], {})
    assert parent.status == TaskStatus.BLOCKED
    assert dependant.status == TaskStatus.BLOCKED
    # El bloqueo derivado no crea una segunda revisión humana.
    reviews = gate.check_pending_reviews()
    assert len(reviews) == 1

    assert gate.process_review(reviews[0].review_id, "approve", "QA disponible")
    report = router.execute_available(
        [parent, dependant],
        {
            "qa": lambda item: {"smoke_test_passed": True},
            "researcher": lambda item: {"completed": True},
        },
    )

    assert parent.status == TaskStatus.COMPLETED
    assert dependant.status == TaskStatus.COMPLETED
    assert report["status_distribution"]["completed"] == 2


def test_rejected_human_review_does_not_auto_resume(tmp_path):
    gate = HumanGate(storage_path=str(tmp_path / "reviews.json"))
    router = TaskRouter(human_gate=gate)
    task = _task("qa-task", task_type="qa")
    router.execute_available([task], {})
    review = gate.check_pending_reviews()[0]
    assert gate.process_review(review.review_id, "reject", "Falta evidencia")

    report = router.execute_available(
        [task],
        {"qa": lambda item: {"smoke_test_passed": True}},
    )

    assert task.status == TaskStatus.BLOCKED
    assert report["human_blocks"][0]["human_decision"]["status"] == "rejected"


def test_verified_result_is_retrievable_after_memory_restart(tmp_path):
    memory_dir = tmp_path / "memory"
    recorder = WorkMemoryRecorder(KnowledgeBroker(str(memory_dir)))
    router = TaskRouter(memory_recorder=recorder)
    task = _task("remember-me")
    router.execute_available([task], {"researcher": lambda item: {"finding": "alpha evidence"}})
    assert task.status == TaskStatus.COMPLETED

    restarted = KnowledgeBroker(str(memory_dir))
    matches = restarted.search("alpha evidence", entry_type="task_outcome")
    assert len(matches) == 1
    assert matches[0]["metadata"]["task_id"] == "remember-me"


def test_human_decision_history_is_not_deleted(tmp_path):
    path = tmp_path / "reviews.json"
    gate = HumanGate(storage_path=str(path))
    review = gate.submit_for_review("Confirmar dato", metadata={"task_id": "data-1"})
    assert gate.process_review(review.review_id, "approve", "dato confirmado") is True
    restored = HumanGate(storage_path=str(path))
    assert restored.get_review_by_id(review.review_id).status == "approved"
    assert restored.get_review_stats() == {"pending": 0, "completed": 1, "total": 1}
