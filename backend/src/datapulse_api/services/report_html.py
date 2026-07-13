from html import escape

from datapulse_api.models import (
    CleaningReportDocument,
    CleaningRuleEffect,
    ColumnProfile,
    DataQualityIssue,
    StructureWarning,
)


def render_cleaning_report_html(report: CleaningReportDocument) -> str:
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{_e(report.metadata.title)}</title>",
            f"<style>{_styles()}</style>",
            "</head>",
            "<body>",
            '<main class="report-shell">',
            _render_header(report),
            _render_executive_summary(report),
            _render_structure_summary(report),
            _render_quality_summary(report),
            _render_cleaning_summary(report),
            _render_export_summary(report),
            _render_limitations(report),
            "</main>",
            "</body>",
            "</html>",
        ]
    )


def _render_header(report: CleaningReportDocument) -> str:
    generated_at = report.metadata.generated_at.isoformat(timespec="seconds")
    sheet = (
        f"<p><strong>Selected sheet:</strong> {_e(report.metadata.selected_sheet_name)}</p>"
        if report.metadata.selected_sheet_name
        else ""
    )
    return f"""
<header class="report-header">
  <p class="eyebrow">DataPulse</p>
  <h1>{_e(report.metadata.title)}</h1>
  <div class="meta-grid">
    <p><strong>Generated:</strong> {_e(generated_at)}</p>
    <p><strong>Source file:</strong> {_e(report.metadata.source_filename)}</p>
    <p><strong>File type:</strong> {_e(report.metadata.detected_extension.upper())}</p>
    {sheet}
  </div>
</header>
"""


def _render_executive_summary(report: CleaningReportDocument) -> str:
    cards = [
        ("Sample rows", str(report.quality.sampled_row_count)),
        ("Detected columns", str(report.structure.detected_column_count)),
        ("Quality score", str(report.quality.quality_score)),
        ("Total issues", str(report.quality.total_issue_count)),
        ("Selected rules", str(len(report.metadata.selected_rules))),
        ("Rows after cleaning", str(report.cleaning.after_summary.row_count)),
        ("Columns after cleaning", str(report.cleaning.after_summary.column_count)),
    ]
    return _section("Executive Summary", f'<div class="card-grid">{_cards(cards)}</div>')


def _render_structure_summary(report: CleaningReportDocument) -> str:
    structure = report.structure
    delimiter = (
        f"{structure.delimiter.delimiter_label} ({structure.delimiter.detected_delimiter!r})"
        if structure.delimiter
        else "Not applicable"
    )
    workbook = ""
    if structure.workbook:
        workbook = (
            f"<p><strong>Workbook sheets:</strong> "
            f"{_e(', '.join(structure.workbook.sheet_names))}</p>"
        )
    content = f"""
<div class="summary-list">
  <p><strong>Structure status:</strong> {_e(structure.structure_status.value)}</p>
  <p><strong>Delimiter:</strong> {_e(delimiter)}</p>
  {workbook}
  <p><strong>Header detected:</strong> {_yes_no(structure.has_detected_header)}</p>
  <p><strong>Header row index:</strong> {_e(str(structure.header_row_index))}</p>
  <p><strong>Preview rows:</strong> {_e(str(structure.preview_row_count))}</p>
  <p><strong>Column names:</strong> {_e(', '.join(structure.column_names))}</p>
</div>
{_warnings("Structure Warnings", structure.warnings)}
"""
    return _section("Structure Summary", content)


def _render_quality_summary(report: CleaningReportDocument) -> str:
    quality = report.quality
    severity_cards = [
        ("Critical issues", str(quality.severity_counts.critical)),
        ("Warning issues", str(quality.severity_counts.warning)),
        ("Info issues", str(quality.severity_counts.info)),
    ]
    content = f"""
<div class="card-grid compact">{_cards(severity_cards)}</div>
<h3>Issue List</h3>
{_quality_issues(quality.issues)}
<h3>Column Profiles</h3>
{_column_profiles(quality.columns)}
"""
    return _section("Data Quality Summary", content)


def _render_cleaning_summary(report: CleaningReportDocument) -> str:
    cleaning = report.cleaning
    selected_rules = (
        ", ".join(rule.value for rule in report.metadata.selected_rules)
        if report.metadata.selected_rules
        else "No rules selected"
    )
    cards = [
        ("Rows before", str(cleaning.before_summary.row_count)),
        ("Rows after", str(cleaning.after_summary.row_count)),
        ("Columns before", str(cleaning.before_summary.column_count)),
        ("Columns after", str(cleaning.after_summary.column_count)),
        ("Removed empty rows", str(cleaning.after_summary.removed_empty_rows_count)),
        ("Removed duplicates", str(cleaning.after_summary.removed_duplicate_rows_count)),
        ("Dropped empty columns", str(cleaning.after_summary.dropped_empty_columns_count)),
        ("Renamed columns", str(cleaning.after_summary.renamed_columns_count)),
    ]
    preview = cleaning.cleaned_preview
    content = f"""
<p><strong>Selected rules:</strong> {_e(selected_rules)}</p>
<div class="card-grid compact">{_cards(cards)}</div>
<h3>Rule Effects</h3>
{_rule_effects(cleaning.rule_effects)}
{_cleaning_warnings(cleaning.warnings)}
<h3>Cleaned Preview</h3>
{_table(preview.columns, preview.rows) if preview else "<p>No cleaned preview was generated.</p>"}
"""
    return _section("Cleaning Summary", content)


def _render_export_summary(report: CleaningReportDocument) -> str:
    excel_note = ""
    if report.metadata.detected_extension in {"xls", "xlsx"}:
        excel_note = (
            "<p>Excel values are exported only as CSV. Formatting, formulas, charts, "
            "and merged cell behavior are not preserved.</p>"
        )
    content = f"""
<div class="summary-list">
  <p><strong>Export format:</strong> {_e(report.export.export_format)}</p>
  <p><strong>Generated filename:</strong> {_e(report.export.filename)}</p>
  <p><strong>Content type:</strong> {_e(report.export.content_type)}</p>
  <p><strong>CSV-first strategy:</strong> {_yes_no(report.export.csv_first_strategy)}</p>
  <p><strong>Original file modified:</strong> {_yes_no(report.export.original_file_modified)}</p>
  {excel_note}
</div>
"""
    return _section("Export Summary", content)


def _render_limitations(report: CleaningReportDocument) -> str:
    items = "".join(f"<li>{_e(item)}</li>" for item in report.limitations)
    return _section("Limitations", f"<ul>{items}</ul>")


def _cards(cards: list[tuple[str, str]]) -> str:
    return "".join(
        f'<article class="summary-card"><span>{_e(label)}</span><strong>{_e(value)}</strong></article>'
        for label, value in cards
    )


def _quality_issues(issues: list[DataQualityIssue]) -> str:
    if not issues:
        return "<p>No quality issues were detected in the sampled data.</p>"
    return "".join(
        f"""
<article class="issue-card severity-{_e(issue.severity.value)}">
  <h4>{_e(issue.title)}</h4>
  <p>{_e(issue.message)}</p>
  <p><strong>Severity:</strong> {_e(issue.severity.value)}</p>
  <p><strong>Affected columns:</strong> {_e(_list_or_none(issue.affected_columns))}</p>
  <p><strong>Affected rows:</strong> {_e(str(issue.affected_row_count or 0))}</p>
  <p><strong>Suggested future rule:</strong> {_e(issue.suggested_cleaning_rule or "None")}</p>
</article>
"""
        for issue in issues
    )


def _column_profiles(columns: list[ColumnProfile]) -> str:
    headers = ["Column", "Type", "Missing", "Missing %", "Unique", "Issues"]
    rows = [
        [
            column.column_name,
            column.inferred_type.value,
            str(column.missing_count),
            f"{column.missing_percentage:.2f}",
            str(column.unique_count),
            _list_or_none(column.issues),
        ]
        for column in columns
    ]
    return _table(headers, rows)


def _rule_effects(effects: list[CleaningRuleEffect]) -> str:
    if not effects:
        return "<p>No cleaning rules were applied.</p>"
    headers = ["Rule", "Status", "Message", "Affected rows", "Affected columns"]
    rows = [
        [
            effect.rule.value,
            effect.status.value,
            effect.message,
            str(effect.affected_rows),
            str(effect.affected_columns),
        ]
        for effect in effects
    ]
    return _table(headers, rows)


def _warnings(title: str, warnings: list[StructureWarning]) -> str:
    if not warnings:
        return f"<h3>{_e(title)}</h3><p>No warnings were reported.</p>"
    items = "".join(
        f"<li><strong>{_e(warning.code)}:</strong> {_e(warning.message)}</li>"
        for warning in warnings
    )
    return f"<h3>{_e(title)}</h3><ul>{items}</ul>"


def _cleaning_warnings(warnings) -> str:
    if not warnings:
        return "<h3>Cleaning Warnings</h3><p>No cleaning warnings were reported.</p>"
    items = "".join(
        f"<li><strong>{_e(warning.code)}:</strong> {_e(warning.message)}</li>"
        for warning in warnings
    )
    return f"<h3>Cleaning Warnings</h3><ul>{items}</ul>"


def _table(columns: list[str], rows: list[list[str]]) -> str:
    header_html = "".join(f"<th>{_e(column)}</th>" for column in columns)
    body_html = "".join(
        "<tr>" + "".join(f"<td>{_e(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    if not body_html:
        body_html = f'<tr><td colspan="{len(columns) or 1}">No rows to display.</td></tr>'
    return f"""
<div class="table-wrap">
  <table>
    <thead><tr>{header_html}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</div>
"""


def _section(title: str, content: str) -> str:
    return f"""
<section class="report-section">
  <h2>{_e(title)}</h2>
  {content}
</section>
"""


def _list_or_none(values: list[str]) -> str:
    return ", ".join(values) if values else "None"


def _yes_no(value: bool) -> str:
    return "Yes" if value else "No"


def _e(value: object) -> str:
    return escape("" if value is None else str(value), quote=True)


def _styles() -> str:
    return """
:root {
  color: #17202a;
  background: #f4f7f9;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
* { box-sizing: border-box; }
body { margin: 0; background: #f4f7f9; }
.report-shell { max-width: 1120px; margin: 0 auto; padding: 32px 20px 48px; }
.report-header {
  background: #12343b;
  color: #ffffff;
  padding: 32px;
  border-radius: 8px;
}
.eyebrow { margin: 0 0 8px; color: #b9e4dd; font-weight: 700; text-transform: uppercase; }
h1, h2, h3, h4, p { overflow-wrap: anywhere; }
h1 { margin: 0 0 16px; font-size: 2rem; }
h2 { margin: 0 0 18px; font-size: 1.35rem; }
h3 { margin: 24px 0 12px; font-size: 1rem; }
.meta-grid, .card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.meta-grid p, .summary-list p { margin: 0; }
.report-section {
  margin-top: 20px;
  padding: 24px;
  background: #ffffff;
  border: 1px solid #d9e2e7;
  border-radius: 8px;
}
.summary-card {
  border: 1px solid #d9e2e7;
  border-radius: 8px;
  padding: 16px;
  background: #f9fbfc;
}
.summary-card span { display: block; color: #5e6c75; font-size: 0.85rem; }
.summary-card strong { display: block; margin-top: 6px; font-size: 1.4rem; color: #12343b; }
.compact .summary-card strong { font-size: 1.1rem; }
.issue-card {
  border: 1px solid #d9e2e7;
  border-left-width: 5px;
  border-radius: 8px;
  padding: 16px;
  margin: 12px 0;
}
.severity-critical { border-left-color: #b42318; }
.severity-warning { border-left-color: #b7791f; }
.severity-info { border-left-color: #2563eb; }
.table-wrap { overflow-x: auto; border: 1px solid #d9e2e7; border-radius: 8px; }
table { width: 100%; min-width: 640px; border-collapse: collapse; }
th, td { padding: 10px 12px; border-bottom: 1px solid #e8eef2; text-align: left; vertical-align: top; }
th { background: #eef4f6; color: #12343b; font-size: 0.85rem; }
ul { padding-left: 20px; }
li { margin: 6px 0; }
@media (max-width: 520px) {
  .report-shell { padding: 16px 10px 32px; }
  .report-header, .report-section { padding: 18px; }
  h1 { font-size: 1.55rem; }
}
"""
