from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3

from datapulse_api.core.database import DEFAULT_DATABASE_PATH, connect
from datapulse_api.models import (
    SavedCleaningSessionCreate,
    SavedCleaningSessionDetail,
    SavedCleaningSessionListResponse,
    SavedCleaningSessionSummary,
)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS cleaning_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_filename TEXT NOT NULL,
    detected_extension TEXT NOT NULL,
    content_type TEXT,
    file_size_bytes INTEGER NOT NULL,
    selected_sheet_name TEXT,
    structure_summary_json TEXT NOT NULL,
    quality_summary_json TEXT NOT NULL,
    selected_rules_json TEXT NOT NULL,
    cleaning_summary_json TEXT NOT NULL,
    rule_effects_json TEXT NOT NULL,
    export_summary_json TEXT NOT NULL,
    report_summary_json TEXT NOT NULL,
    preview_snapshot_json TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_cleaning_sessions_created_at
ON cleaning_sessions(created_at DESC);
"""


class CleaningSessionNotFoundError(LookupError):
    pass


class CleaningSessionRepository:
    def __init__(self, database_path: Path | str = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.initialize()

    def initialize(self) -> None:
        with connect(self.database_path) as connection:
            connection.executescript(SCHEMA_SQL)
            connection.commit()

    def create(self, payload: SavedCleaningSessionCreate) -> SavedCleaningSessionDetail:
        now = _utc_iso()
        values = {
            "source_filename": payload.source_filename,
            "detected_extension": payload.detected_extension,
            "content_type": payload.content_type,
            "file_size_bytes": payload.file_size_bytes,
            "selected_sheet_name": payload.selected_sheet_name,
            "structure_summary_json": _json_dumps(payload.structure_summary),
            "quality_summary_json": _json_dumps(payload.quality_summary),
            "selected_rules_json": _json_dumps(payload.selected_rules),
            "cleaning_summary_json": _json_dumps(payload.cleaning_summary),
            "rule_effects_json": _json_dumps(payload.rule_effects),
            "export_summary_json": _json_dumps(payload.export_summary),
            "report_summary_json": _json_dumps(payload.report_summary),
            "preview_snapshot_json": _json_dumps(payload.preview_snapshot) if payload.preview_snapshot is not None else None,
            "created_at": now,
            "updated_at": now,
        }
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO cleaning_sessions (
                    source_filename, detected_extension, content_type, file_size_bytes,
                    selected_sheet_name, structure_summary_json, quality_summary_json,
                    selected_rules_json, cleaning_summary_json, rule_effects_json,
                    export_summary_json, report_summary_json, preview_snapshot_json,
                    created_at, updated_at
                )
                VALUES (
                    :source_filename, :detected_extension, :content_type, :file_size_bytes,
                    :selected_sheet_name, :structure_summary_json, :quality_summary_json,
                    :selected_rules_json, :cleaning_summary_json, :rule_effects_json,
                    :export_summary_json, :report_summary_json, :preview_snapshot_json,
                    :created_at, :updated_at
                )
                """,
                values,
            )
            connection.commit()
            return self.get(int(cursor.lastrowid))

    def list(self) -> SavedCleaningSessionListResponse:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT * FROM cleaning_sessions
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        summaries = [_row_to_summary(row) for row in rows]
        return SavedCleaningSessionListResponse(sessions=summaries, total_count=len(summaries))

    def get(self, session_id: int) -> SavedCleaningSessionDetail:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM cleaning_sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
        if row is None:
            raise CleaningSessionNotFoundError(f"Saved cleaning session {session_id} was not found.")
        return _row_to_detail(row)

    def delete(self, session_id: int) -> None:
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                "DELETE FROM cleaning_sessions WHERE id = ?",
                (session_id,),
            )
            connection.commit()
        if cursor.rowcount == 0:
            raise CleaningSessionNotFoundError(f"Saved cleaning session {session_id} was not found.")


def _row_to_summary(row: sqlite3.Row) -> SavedCleaningSessionSummary:
    quality_summary = _json_loads(row["quality_summary_json"])
    cleaning_summary = _json_loads(row["cleaning_summary_json"])
    selected_rules = _json_loads(row["selected_rules_json"])
    before_summary = cleaning_summary.get("before_summary", {})
    after_summary = cleaning_summary.get("after_summary", {})
    return SavedCleaningSessionSummary(
        id=row["id"],
        source_filename=row["source_filename"],
        detected_extension=row["detected_extension"],
        selected_sheet_name=row["selected_sheet_name"],
        quality_score=quality_summary.get("quality_score"),
        total_issue_count=quality_summary.get("total_issue_count", 0),
        selected_rules_count=len(selected_rules),
        rows_before=before_summary.get("row_count"),
        rows_after=after_summary.get("row_count"),
        columns_before=before_summary.get("column_count"),
        columns_after=after_summary.get("column_count"),
        created_at=_parse_datetime(row["created_at"]),
        updated_at=_parse_datetime(row["updated_at"]),
    )


def _row_to_detail(row: sqlite3.Row) -> SavedCleaningSessionDetail:
    summary = _row_to_summary(row)
    return SavedCleaningSessionDetail(
        **summary.model_dump(),
        content_type=row["content_type"],
        file_size_bytes=row["file_size_bytes"],
        structure_summary=_json_loads(row["structure_summary_json"]),
        quality_summary=_json_loads(row["quality_summary_json"]),
        selected_rules=_json_loads(row["selected_rules_json"]),
        cleaning_summary=_json_loads(row["cleaning_summary_json"]),
        rule_effects=_json_loads(row["rule_effects_json"]),
        export_summary=_json_loads(row["export_summary_json"]),
        report_summary=_json_loads(row["report_summary_json"]),
        preview_snapshot=_json_loads(row["preview_snapshot_json"]) if row["preview_snapshot_json"] else None,
    )


def _json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str):
    return json.loads(value)


def _utc_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)
