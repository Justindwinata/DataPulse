from fastapi import APIRouter, Form, UploadFile

from datapulse_api.models import (
    DataQualityResult,
    FileUploadValidationResponse,
    StructureDetectionResult,
)
from datapulse_api.services.csv_structure_detection import detect_csv_like_structure
from datapulse_api.services.data_quality import detect_data_quality
from datapulse_api.services.excel_structure_detection import (
    detect_excel_sheet_preview,
    detect_excel_workbook,
)
from datapulse_api.services.file_validation import detect_extension, sanitize_filename
from datapulse_api.services.file_validation import validate_uploaded_file_metadata

router = APIRouter(prefix="/files", tags=["files"])


@router.post("/validate-upload")
async def validate_upload(file: UploadFile) -> FileUploadValidationResponse:
    content = await file.read()
    return validate_uploaded_file_metadata(
        filename=file.filename or "uploaded_file",
        content_type=file.content_type,
        file_size_bytes=len(content),
    )


@router.post("/detect-structure")
async def detect_structure(
    file: UploadFile,
    sheet_name: str | None = Form(default=None),
) -> StructureDetectionResult:
    content = await file.read()
    filename = file.filename or "uploaded_file"
    extension = detect_extension(sanitize_filename(filename))
    if extension in {"xlsx", "xls"}:
        if sheet_name:
            return detect_excel_sheet_preview(
                filename=filename,
                content_type=file.content_type,
                content=content,
                sheet_name=sheet_name,
            )
        return detect_excel_workbook(
            filename=filename,
            content_type=file.content_type,
            content=content,
        )
    return detect_csv_like_structure(
        filename=filename,
        content_type=file.content_type,
        content=content,
    )


@router.post("/detect-quality")
async def detect_quality(
    file: UploadFile,
    sheet_name: str | None = Form(default=None),
) -> DataQualityResult:
    content = await file.read()
    return detect_data_quality(
        filename=file.filename or "uploaded_file",
        content_type=file.content_type,
        content=content,
        sheet_name=sheet_name,
    )
