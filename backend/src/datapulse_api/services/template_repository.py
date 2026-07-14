from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
import sqlite3

from datapulse_api.core.database import DEFAULT_DATABASE_PATH, connect
from datapulse_api.models import (
    WorkflowTemplateCreate,
    WorkflowTemplateDetail,
    WorkflowTemplateListResponse,
    WorkflowTemplateSummary,
    WorkflowTemplateUpdate,
)


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS workflow_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    selected_rules_json TEXT NOT NULL,
    source_session_id INTEGER,
    source_filename TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_workflow_templates_created_at
ON workflow_templates(created_at DESC);
"""


class WorkflowTemplateNotFoundError(LookupError):
    pass


class WorkflowTemplateRepository:
    def __init__(self, database_path: Path | str = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.initialize()

    def initialize(self) -> None:
        with connect(self.database_path) as connection:
            connection.executescript(SCHEMA_SQL)
            connection.commit()

    def create(self, payload: WorkflowTemplateCreate) -> WorkflowTemplateDetail:
        now = _utc_iso()
        values = {
            "name": payload.name,
            "description": payload.description,
            "selected_rules_json": _json_dumps([rule.value for rule in payload.selected_rules]),
            "source_session_id": payload.source_session_id,
            "source_filename": payload.source_filename,
            "created_at": now,
            "updated_at": now,
        }
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO workflow_templates (
                    name, description, selected_rules_json, source_session_id,
                    source_filename, created_at, updated_at
                )
                VALUES (
                    :name, :description, :selected_rules_json, :source_session_id,
                    :source_filename, :created_at, :updated_at
                )
                """,
                values,
            )
            connection.commit()
            return self.get(int(cursor.lastrowid))

    def list(self) -> WorkflowTemplateListResponse:
        with connect(self.database_path) as connection:
            rows = connection.execute(
                """
                SELECT * FROM workflow_templates
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        summaries = [_row_to_summary(row) for row in rows]
        return WorkflowTemplateListResponse(templates=summaries, total_count=len(summaries))

    def get(self, template_id: int) -> WorkflowTemplateDetail:
        with connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT * FROM workflow_templates WHERE id = ?",
                (template_id,),
            ).fetchone()
        if row is None:
            raise WorkflowTemplateNotFoundError(f"Workflow template {template_id} was not found.")
        return _row_to_detail(row)

    def update(
        self,
        template_id: int,
        payload: WorkflowTemplateUpdate,
    ) -> WorkflowTemplateDetail:
        current = self.get(template_id)
        selected_rules = (
            [rule.value for rule in payload.selected_rules]
            if payload.selected_rules is not None
            else [rule.value for rule in current.selected_rules]
        )
        values = {
            "id": template_id,
            "name": payload.name if payload.name is not None else current.name,
            "description": payload.description if "description" in payload.model_fields_set else current.description,
            "selected_rules_json": _json_dumps(selected_rules),
            "updated_at": _utc_iso(),
        }
        with connect(self.database_path) as connection:
            connection.execute(
                """
                UPDATE workflow_templates
                SET name = :name,
                    description = :description,
                    selected_rules_json = :selected_rules_json,
                    updated_at = :updated_at
                WHERE id = :id
                """,
                values,
            )
            connection.commit()
        return self.get(template_id)

    def delete(self, template_id: int) -> None:
        with connect(self.database_path) as connection:
            cursor = connection.execute(
                "DELETE FROM workflow_templates WHERE id = ?",
                (template_id,),
            )
            connection.commit()
        if cursor.rowcount == 0:
            raise WorkflowTemplateNotFoundError(f"Workflow template {template_id} was not found.")


def _row_to_summary(row: sqlite3.Row) -> WorkflowTemplateSummary:
    selected_rules = _json_loads(row["selected_rules_json"])
    return WorkflowTemplateSummary(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        selected_rules_count=len(selected_rules),
        source_session_id=row["source_session_id"],
        source_filename=row["source_filename"],
        created_at=_parse_datetime(row["created_at"]),
        updated_at=_parse_datetime(row["updated_at"]),
    )


def _row_to_detail(row: sqlite3.Row) -> WorkflowTemplateDetail:
    summary = _row_to_summary(row)
    return WorkflowTemplateDetail(
        **summary.model_dump(),
        selected_rules=_json_loads(row["selected_rules_json"]),
    )


def _json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str):
    return json.loads(value)


def _utc_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)
