import csv
from collections import Counter
from io import StringIO

from datapulse_api.models import (
    DelimiterConfidence,
    DelimiterDetection,
    RawTablePreview,
    StructureDetectionResult,
    StructureDetectionStatus,
    StructureNextStep,
    StructureWarning,
    StructureWarningSeverity,
)
from datapulse_api.services.file_validation import (
    MAX_UPLOAD_SIZE_BYTES,
    SUPPORTED_FORMATS_LABEL,
    detect_extension,
    sanitize_filename,
    validate_uploaded_file_metadata,
)

CSV_LIKE_EXTENSIONS = frozenset({"csv", "tsv", "txt"})
EXCEL_EXTENSIONS = frozenset({"xlsx", "xls"})
DELIMITER_CANDIDATES: tuple[tuple[str, str], ...] = (
    (",", "comma"),
    (";", "semicolon"),
    ("\t", "tab"),
    ("|", "pipe"),
)
MAX_SAMPLE_BYTES = 512 * 1024
MAX_SAMPLE_ROWS = 200
MAX_PREVIEW_ROWS = 20


def detect_csv_like_structure(
    *,
    filename: str,
    content_type: str | None,
    content: bytes,
) -> StructureDetectionResult:
    safe_filename = sanitize_filename(filename)
    extension = detect_extension(safe_filename) or "unknown"
    validation = validate_uploaded_file_metadata(
        filename=filename,
        content_type=content_type,
        file_size_bytes=len(content),
    )

    if extension in EXCEL_EXTENSIONS and len(content) > 0 and len(content) <= MAX_UPLOAD_SIZE_BYTES:
        return _rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=len(content),
            status=StructureDetectionStatus.NOT_IMPLEMENTED,
            next_step=StructureNextStep.WAIT_FOR_EXCEL_SUPPORT,
            message="Excel structure detection will be implemented in a later milestone.",
            code="excel_structure_detection_not_implemented",
        )

    if not validation.is_supported or extension not in CSV_LIKE_EXTENSIONS:
        messages = validation.validation_messages
        message = messages[0] if messages else f"Unsupported file extension. Supported formats are {SUPPORTED_FORMATS_LABEL}."
        return _rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=len(content),
            status=StructureDetectionStatus.REJECTED,
            next_step=StructureNextStep.UPLOAD_SUPPORTED_FILE,
            message=message,
            code="file_not_supported_for_structure_detection",
        )

    sample_text = _decode_sample(content[:MAX_SAMPLE_BYTES])
    raw_rows = _read_rows(sample_text)
    meaningful_rows = [(index, row) for index, row in enumerate(raw_rows) if _row_has_value(row)]
    warnings = _detect_sample_warnings(raw_rows, meaningful_rows)

    if not meaningful_rows:
        return _rejected_result(
            filename=filename,
            safe_filename=safe_filename,
            extension=extension,
            content_type=content_type,
            file_size_bytes=len(content),
            status=StructureDetectionStatus.REJECTED,
            next_step=StructureNextStep.UPLOAD_SUPPORTED_FILE,
            message="File is empty. Upload a non-empty tabular file.",
            code="empty_file",
        )

    delimiter = _detect_delimiter(sample_text)
    parsed_rows = _parse_rows(sample_text, delimiter.detected_delimiter or ",")
    sampled_rows = parsed_rows[:MAX_SAMPLE_ROWS]
    meaningful_parsed_rows = [
        (index, row) for index, row in enumerate(sampled_rows) if _row_has_value(row)
    ]

    header_index, has_header, leading_metadata_rows = _detect_header_row(meaningful_parsed_rows)
    if leading_metadata_rows:
        warnings.append(
            StructureWarning(
                code="leading_metadata_rows",
                message="Possible metadata rows were detected before the header.",
            )
        )

    table_rows = meaningful_parsed_rows
    if header_index is not None:
        table_rows = [(index, row) for index, row in meaningful_parsed_rows if index >= header_index]

    header_row = next((row for index, row in table_rows if index == header_index), None)
    column_count = len(header_row) if has_header and header_row is not None else _detect_column_count(table_rows)
    column_names, generated_column_names, name_warnings = _build_column_names(
        header_row=header_row if has_header else None,
        column_count=column_count,
    )
    warnings.extend(name_warnings)
    warnings.extend(_detect_width_warnings(table_rows, column_count))

    data_rows = [(index, row) for index, row in table_rows if not has_header or index != header_index]
    preview_rows = [_normalize_row(row, column_count) for _, row in data_rows[:MAX_PREVIEW_ROWS]]

    if len(meaningful_parsed_rows) < 2:
        warnings.append(
            StructureWarning(
                code="very_small_file",
                message="The sample contains fewer than two meaningful rows.",
                severity=StructureWarningSeverity.INFO,
            )
        )

    return StructureDetectionResult(
        original_filename=filename,
        safe_filename=safe_filename,
        detected_extension=extension,
        file_size_bytes=len(content),
        content_type=content_type,
        structure_status=StructureDetectionStatus.DETECTED,
        delimiter=delimiter,
        has_detected_header=has_header,
        header_row_index=header_index,
        column_names=column_names,
        generated_column_names=generated_column_names,
        detected_column_count=column_count,
        sampled_row_count=len(sampled_rows),
        preview_row_count=len(preview_rows),
        total_row_count_calculated=False,
        warnings=_deduplicate_warnings(warnings),
        preview=RawTablePreview(columns=column_names, rows=preview_rows),
        next_step=StructureNextStep.QUALITY_ISSUE_DETECTION,
    )


def _decode_sample(sample: bytes) -> str:
    return sample.decode("utf-8-sig", errors="replace")


def _read_rows(text: str) -> list[list[str]]:
    return [[line] for line in text.splitlines()]


def _detect_delimiter(sample_text: str) -> DelimiterDetection:
    scored: list[tuple[int, int, str, str]] = []
    for delimiter, label in DELIMITER_CANDIDATES:
        rows = _parse_rows(sample_text, delimiter)
        meaningful = [row for row in rows[:MAX_SAMPLE_ROWS] if _row_has_value(row)]
        widths = [len(row) for row in meaningful if len(row) > 1]
        if not widths:
            scored.append((0, 0, delimiter, label))
            continue
        common_width, common_count = Counter(widths).most_common(1)[0]
        scored.append((common_width, common_count, delimiter, label))

    best_width, best_count, best_delimiter, best_label = max(scored, key=lambda item: (item[1], item[0]))
    if best_count >= 2 and best_width > 1:
        confidence = DelimiterConfidence.HIGH
    elif best_count == 1 and best_width > 1:
        confidence = DelimiterConfidence.MEDIUM
    else:
        confidence = DelimiterConfidence.LOW

    return DelimiterDetection(
        detected_delimiter=best_delimiter,
        delimiter_label=best_label,
        delimiter_confidence=confidence,
        detection_reason=f"{best_label.title()} produced the most consistent sampled row widths.",
    )


def _parse_rows(text: str, delimiter: str) -> list[list[str]]:
    reader = csv.reader(StringIO(text), delimiter=delimiter)
    return [[cell.strip() for cell in row] for row in reader][:MAX_SAMPLE_ROWS]


def _row_has_value(row: list[str]) -> bool:
    return any(cell.strip() for cell in row)


def _detect_sample_warnings(
    raw_rows: list[list[str]],
    meaningful_rows: list[tuple[int, list[str]]],
) -> list[StructureWarning]:
    warnings: list[StructureWarning] = []
    if len(raw_rows) != len(meaningful_rows):
        warnings.append(
            StructureWarning(
                code="empty_rows_in_sample",
                message="Empty rows were detected in the sampled file.",
            )
        )
    if len(raw_rows) >= MAX_SAMPLE_ROWS:
        warnings.append(
            StructureWarning(
                code="sample_row_limit_reached",
                message="Only the first bounded sample of rows was inspected.",
                severity=StructureWarningSeverity.INFO,
            )
        )
    return warnings


def _detect_header_row(rows: list[tuple[int, list[str]]]) -> tuple[int | None, bool, bool]:
    if not rows:
        return None, False, False

    for position, (row_index, row) in enumerate(rows[:5]):
        next_row = rows[position + 1][1] if position + 1 < len(rows) else []
        if _looks_like_header(row, next_row):
            return row_index, True, position > 0

    return rows[0][0], False, False


def _looks_like_header(row: list[str], next_row: list[str]) -> bool:
    non_empty = [cell for cell in row if cell.strip()]
    if len(non_empty) < 2:
        return False
    row_text_ratio = sum(not _is_numeric(cell) for cell in non_empty) / len(non_empty)
    next_non_empty = [cell for cell in next_row if cell.strip()]
    if not next_non_empty:
        return row_text_ratio >= 0.8
    next_numeric_count = sum(_is_numeric(cell) for cell in next_non_empty)
    return row_text_ratio >= 0.8 and (
        next_numeric_count >= 1 or _looks_like_column_labels(non_empty)
    )


def _looks_like_column_labels(cells: list[str]) -> bool:
    label_like_count = sum(
        bool(cell.strip()) and not any(character.isdigit() for character in cell)
        for cell in cells
    )
    return label_like_count == len(cells)


def _is_numeric(value: str) -> bool:
    normalized = value.strip().replace(",", "")
    if not normalized:
        return False
    try:
        float(normalized)
    except ValueError:
        return False
    return True


def _detect_column_count(rows: list[tuple[int, list[str]]]) -> int:
    widths = [len(row) for _, row in rows if _row_has_value(row)]
    if not widths:
        return 1
    return Counter(widths).most_common(1)[0][0]


def _build_column_names(
    *,
    header_row: list[str] | None,
    column_count: int,
) -> tuple[list[str], bool, list[StructureWarning]]:
    warnings: list[StructureWarning] = []
    generated = header_row is None
    if header_row is None:
        return [f"column_{index}" for index in range(1, column_count + 1)], True, warnings

    normalized_header = _normalize_row(header_row, column_count)
    missing_indexes = [index for index, name in enumerate(normalized_header) if not name.strip()]
    names = [
        _normalize_column_name(name) if name.strip() else f"column_{index + 1}"
        for index, name in enumerate(normalized_header)
    ]
    if missing_indexes:
        generated = True
        warnings.append(
            StructureWarning(
                code="missing_column_names",
                message="Missing column names were replaced with generated names.",
            )
        )

    duplicates = [name for name, count in Counter(names).items() if count > 1]
    if duplicates:
        warnings.append(
            StructureWarning(
                code="duplicate_column_names",
                message="Duplicate column names were detected in the header row.",
            )
        )

    return names, generated, warnings


def _normalize_column_name(name: str) -> str:
    normalized = "_".join(name.strip().lower().split())
    return normalized or "column"


def _detect_width_warnings(
    rows: list[tuple[int, list[str]]],
    column_count: int,
) -> list[StructureWarning]:
    if any(len(row) != column_count for _, row in rows if _row_has_value(row)):
        return [
            StructureWarning(
                code="inconsistent_row_widths",
                message="Rows with different column counts were detected in the sample.",
            )
        ]
    return []


def _normalize_row(row: list[str], column_count: int) -> list[str]:
    normalized = row[:column_count]
    if len(normalized) < column_count:
        normalized.extend([""] * (column_count - len(normalized)))
    return normalized


def _deduplicate_warnings(warnings: list[StructureWarning]) -> list[StructureWarning]:
    seen: set[str] = set()
    unique: list[StructureWarning] = []
    for warning in warnings:
        if warning.code in seen:
            continue
        seen.add(warning.code)
        unique.append(warning)
    return unique


def _rejected_result(
    *,
    filename: str,
    safe_filename: str,
    extension: str,
    content_type: str | None,
    file_size_bytes: int,
    status: StructureDetectionStatus,
    next_step: StructureNextStep,
    message: str,
    code: str,
) -> StructureDetectionResult:
    return StructureDetectionResult(
        original_filename=filename,
        safe_filename=safe_filename,
        detected_extension=extension,
        file_size_bytes=max(file_size_bytes, 0),
        content_type=content_type,
        structure_status=status,
        warnings=[
            StructureWarning(
                code=code,
                message=message,
                severity=StructureWarningSeverity.ERROR
                if status == StructureDetectionStatus.REJECTED
                else StructureWarningSeverity.INFO,
            )
        ],
        next_step=next_step,
    )
