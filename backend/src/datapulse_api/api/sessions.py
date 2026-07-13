from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import HTMLResponse

from datapulse_api.models import (
    SavedCleaningSessionCreate,
    SavedCleaningSessionDetail,
    SavedCleaningSessionListResponse,
)
from datapulse_api.services.report_html import render_saved_session_report_html
from datapulse_api.services.saved_session_report import build_saved_session_report
from datapulse_api.services.session_repository import (
    CleaningSessionNotFoundError,
    CleaningSessionRepository,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_session_repository() -> CleaningSessionRepository:
    return CleaningSessionRepository()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_session(
    payload: SavedCleaningSessionCreate,
    repository: CleaningSessionRepository = Depends(get_session_repository),
) -> SavedCleaningSessionDetail:
    return repository.create(payload)


@router.get("")
async def list_sessions(
    repository: CleaningSessionRepository = Depends(get_session_repository),
) -> SavedCleaningSessionListResponse:
    return repository.list()


@router.get("/{session_id}/report.html", response_class=HTMLResponse)
async def get_saved_session_report(
    session_id: int,
    repository: CleaningSessionRepository = Depends(get_session_repository),
) -> HTMLResponse:
    try:
        session = repository.get(session_id)
    except CleaningSessionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Saved cleaning session not found.") from error
    report = build_saved_session_report(session)
    return HTMLResponse(
        content=render_saved_session_report_html(report),
        media_type="text/html; charset=utf-8",
    )


@router.get("/{session_id}")
async def get_session(
    session_id: int,
    repository: CleaningSessionRepository = Depends(get_session_repository),
) -> SavedCleaningSessionDetail:
    try:
        return repository.get(session_id)
    except CleaningSessionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Saved cleaning session not found.") from error


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    repository: CleaningSessionRepository = Depends(get_session_repository),
) -> Response:
    try:
        repository.delete(session_id)
    except CleaningSessionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Saved cleaning session not found.") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
