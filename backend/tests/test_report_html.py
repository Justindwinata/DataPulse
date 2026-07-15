from datapulse_api.models import CleaningRuleCode
from datapulse_api.services.cleaning_report import build_cleaning_report
from datapulse_api.services.report_html import render_cleaning_report_html


def test_html_report_renders_required_sections() -> None:
    report = build_cleaning_report(
        filename="messy.csv",
        content_type="text/csv",
        content=b"Customer Name,Amount\n Ari ,1200\n Ari ,1200\n",
        rules=[
            CleaningRuleCode.TRIM_WHITESPACE,
            CleaningRuleCode.REMOVE_DUPLICATE_ROWS,
            CleaningRuleCode.STANDARDIZE_COLUMN_NAMES,
        ],
    )

    html = render_cleaning_report_html(report)

    assert "<!doctype html>" in html
    assert "DataPulse Cleaning Report" in html
    assert "Executive Summary" in html
    assert "Structure Summary" in html
    assert "Data Quality Summary" in html
    assert "Cleaning Summary" in html
    assert "Rule Effects" in html
    assert "Export Summary" in html
    assert "Limitations" in html
    assert "Remove duplicate rows (remove_duplicate_rows)" in html
    assert "remove_duplicate_rows" in html


def test_html_report_escapes_user_provided_values() -> None:
    report = build_cleaning_report(
        filename='"><script>alert(1)</script>.csv',
        content_type="text/csv",
        content=b'name,note\n"<b>Ari</b>","<script>bad()</script>"\n',
        rules=[CleaningRuleCode.TRIM_WHITESPACE],
    )

    html = render_cleaning_report_html(report)

    assert '"><script>alert(1)</script>.csv' not in html
    assert "<b>Ari</b>" not in html
    assert "<script>bad()</script>" not in html
    assert "&lt;b&gt;Ari&lt;/b&gt;" in html
    assert "&lt;script&gt;bad()&lt;/script&gt;" in html
    assert "<script" not in html.lower()
    assert "https://" not in html
