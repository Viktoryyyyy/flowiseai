from __future__ import annotations

from pathlib import Path

from state_api.runtime.config import RuntimeConfig
from state_api.runtime.operations import StateApiOperations
from state_api.runtime.persistence import SQLiteStateRepository

from conftest import MutableClock, sample_task


def test_sqlite_local_dev_persistence_survives_repository_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "state_api.sqlite3"
    clock = MutableClock()

    repo_one = SQLiteStateRepository(str(db_path))
    operations_one = StateApiOperations(repo_one, RuntimeConfig(sqlite_path=str(db_path)), clock=clock)
    operations_one.create_task(sample_task("task-durable"), idempotency_key="idem-durable-create")
    repo_one.close()

    repo_two = SQLiteStateRepository(str(db_path))
    try:
        operations_two = StateApiOperations(repo_two, RuntimeConfig(sqlite_path=str(db_path)), clock=clock)
        read = operations_two.read_task("task-durable")
        assert read["task"]["task_id"] == "task-durable"
        replay = operations_two.create_task(sample_task("task-durable"), idempotency_key="idem-durable-create")
        assert replay["task_ref"] == "task-durable"
        assert repo_two.count_rows("tasks") == 1
    finally:
        repo_two.close()
