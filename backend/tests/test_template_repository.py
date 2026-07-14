from pathlib import Path

import pytest

from datapulse_api.models import WorkflowTemplateCreate, WorkflowTemplateUpdate
from datapulse_api.services.session_repository import CleaningSessionRepository
from datapulse_api.services import template_repository as template_repository_module
from datapulse_api.services.template_repository import (
    WorkflowTemplateNotFoundError,
    WorkflowTemplateRepository,
)
from tests.test_session_repository import make_payload


def make_template_payload(name: str = "Sales cleanup") -> WorkflowTemplateCreate:
    return WorkflowTemplateCreate(
        name=name,
        description="Reusable import cleanup",
        selected_rules=["trim_whitespace", "remove_empty_rows"],
        source_session_id=3,
        source_filename="messy.csv",
    )


def test_template_repository_creates_schema_and_database_file(tmp_path: Path) -> None:
    database_path = tmp_path / "datapulse.sqlite3"

    WorkflowTemplateRepository(database_path)

    assert database_path.exists()


def test_template_repository_create_list_get_update_and_delete(tmp_path: Path) -> None:
    repository = WorkflowTemplateRepository(tmp_path / "templates.sqlite3")

    created = repository.create(make_template_payload())
    listed = repository.list()
    fetched = repository.get(created.id)

    assert listed.total_count == 1
    assert listed.templates[0].name == "Sales cleanup"
    assert listed.templates[0].selected_rules_count == 2
    assert fetched.selected_rules == ["trim_whitespace", "remove_empty_rows"]
    assert fetched.storage_note.startswith("Templates store cleaning rules")

    updated = repository.update(
        created.id,
        WorkflowTemplateUpdate(
            name="Updated cleanup",
            description=None,
            selected_rules=["drop_empty_columns"],
        ),
    )

    assert updated.name == "Updated cleanup"
    assert updated.description is None
    assert updated.selected_rules == ["drop_empty_columns"]

    repository.delete(created.id)

    assert repository.list().total_count == 0
    with pytest.raises(WorkflowTemplateNotFoundError):
        repository.get(created.id)


def test_template_repository_orders_newest_templates_first(tmp_path: Path) -> None:
    repository = WorkflowTemplateRepository(tmp_path / "templates.sqlite3")

    first = repository.create(make_template_payload("First"))
    second = repository.create(make_template_payload("Second"))

    listed = repository.list()

    assert [template.id for template in listed.templates] == [second.id, first.id]


def test_template_repository_orders_recently_updated_templates_first(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    timestamps = iter(
        [
            "2026-07-15T00:00:00+00:00",
            "2026-07-15T00:00:01+00:00",
            "2026-07-15T00:00:02+00:00",
        ]
    )
    monkeypatch.setattr(template_repository_module, "_utc_iso", lambda: next(timestamps))
    repository = WorkflowTemplateRepository(tmp_path / "templates.sqlite3")

    first = repository.create(make_template_payload("First"))
    second = repository.create(make_template_payload("Second"))
    repository.update(first.id, WorkflowTemplateUpdate(description="Freshly edited"))

    listed = repository.list()

    assert [template.id for template in listed.templates] == [first.id, second.id]


def test_template_repository_delete_missing_template_raises_not_found(tmp_path: Path) -> None:
    repository = WorkflowTemplateRepository(tmp_path / "templates.sqlite3")

    with pytest.raises(WorkflowTemplateNotFoundError):
        repository.delete(404)


def test_template_schema_coexists_with_saved_sessions(tmp_path: Path) -> None:
    database_path = tmp_path / "datapulse.sqlite3"
    session_repository = CleaningSessionRepository(database_path)
    template_repository = WorkflowTemplateRepository(database_path)

    session = session_repository.create(make_payload())
    template = template_repository.create(
        WorkflowTemplateCreate(
            name="From session",
            selected_rules=["trim_whitespace"],
            source_session_id=session.id,
            source_filename=session.source_filename,
        )
    )

    assert session_repository.list().total_count == 1
    assert template_repository.get(template.id).source_session_id == session.id
