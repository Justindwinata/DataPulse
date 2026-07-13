from pathlib import Path

import pytest

from datapulse_api.models import SavedCleaningSessionCreate
from datapulse_api.services.session_repository import (
    CleaningSessionNotFoundError,
    CleaningSessionRepository,
)


def make_payload(filename: str = "messy.csv") -> SavedCleaningSessionCreate:
    return SavedCleaningSessionCreate(
        source_filename=filename,
        detected_extension="csv",
        content_type="text/csv",
        file_size_bytes=42,
        structure_summary={"detected_column_count": 2, "preview_row_count": 1},
        quality_summary={"quality_score": 91, "total_issue_count": 2},
        selected_rules=["trim_whitespace", "remove_empty_rows"],
        cleaning_summary={
            "before_summary": {"row_count": 3, "column_count": 2},
            "after_summary": {"row_count": 2, "column_count": 2},
        },
        rule_effects=[{"rule": "trim_whitespace", "status": "applied"}],
        export_summary={"format": "CSV", "filename": "messy_cleaned.csv"},
        report_summary={"format": "HTML", "generated": True},
        preview_snapshot={"columns": ["name"], "rows": [["Ari"]]},
    )


def test_repository_creates_schema_and_database_file(tmp_path: Path) -> None:
    database_path = tmp_path / "datapulse.sqlite3"

    CleaningSessionRepository(database_path)

    assert database_path.exists()


def test_repository_create_list_get_and_delete_session(tmp_path: Path) -> None:
    repository = CleaningSessionRepository(tmp_path / "history.sqlite3")

    created = repository.create(make_payload())
    listed = repository.list()
    fetched = repository.get(created.id)

    assert listed.total_count == 1
    assert listed.sessions[0].source_filename == "messy.csv"
    assert listed.sessions[0].selected_rules_count == 2
    assert listed.sessions[0].rows_before == 3
    assert fetched.preview_snapshot == {"columns": ["name"], "rows": [["Ari"]]}
    assert fetched.storage_note.startswith("Original uploaded files are not stored")

    repository.delete(created.id)

    assert repository.list().total_count == 0
    with pytest.raises(CleaningSessionNotFoundError):
        repository.get(created.id)


def test_repository_orders_newest_sessions_first(tmp_path: Path) -> None:
    repository = CleaningSessionRepository(tmp_path / "history.sqlite3")

    first = repository.create(make_payload("first.csv"))
    second = repository.create(make_payload("second.csv"))

    listed = repository.list()

    assert [session.id for session in listed.sessions] == [second.id, first.id]


def test_repository_delete_missing_session_raises_not_found(tmp_path: Path) -> None:
    repository = CleaningSessionRepository(tmp_path / "history.sqlite3")

    with pytest.raises(CleaningSessionNotFoundError):
        repository.delete(404)
