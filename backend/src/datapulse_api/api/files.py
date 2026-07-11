from fastapi import APIRouter, UploadFile

from datapulse_api.models import FileUploadValidationResponse, StructureDetectionResult
from datapulse_api.services.csv_structure_detection import detect_csv_like_structure
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
async def detect_structure(file: UploadFile) -> StructureDetectionResult:
    content = await file.read()
    return detect_csv_like_structure(
        filename=file.filename or "uploaded_file",
        content_type=file.content_type,
        content=content,
    )
