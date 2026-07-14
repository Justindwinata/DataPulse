from fastapi import APIRouter, Depends, HTTPException, Response, status

from datapulse_api.models import (
    WorkflowTemplateCreate,
    WorkflowTemplateDetail,
    WorkflowTemplateListResponse,
    WorkflowTemplateUpdate,
)
from datapulse_api.services.session_repository import (
    CleaningSessionNotFoundError,
    CleaningSessionRepository,
)
from datapulse_api.services.template_repository import (
    WorkflowTemplateNotFoundError,
    WorkflowTemplateRepository,
)

router = APIRouter(prefix="/templates", tags=["templates"])


def get_template_repository() -> WorkflowTemplateRepository:
    return WorkflowTemplateRepository()


def get_session_repository() -> CleaningSessionRepository:
    return CleaningSessionRepository()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_template(
    payload: WorkflowTemplateCreate,
    repository: WorkflowTemplateRepository = Depends(get_template_repository),
) -> WorkflowTemplateDetail:
    return repository.create(payload)


@router.get("")
async def list_templates(
    repository: WorkflowTemplateRepository = Depends(get_template_repository),
) -> WorkflowTemplateListResponse:
    return repository.list()


@router.post("/from-session/{session_id}", status_code=status.HTTP_201_CREATED)
async def create_template_from_session(
    session_id: int,
    payload: WorkflowTemplateCreate,
    template_repository: WorkflowTemplateRepository = Depends(get_template_repository),
    session_repository: CleaningSessionRepository = Depends(get_session_repository),
) -> WorkflowTemplateDetail:
    try:
        session = session_repository.get(session_id)
    except CleaningSessionNotFoundError as error:
        raise HTTPException(status_code=404, detail="Saved cleaning session not found.") from error
    return template_repository.create(
        WorkflowTemplateCreate(
            name=payload.name,
            description=payload.description,
            selected_rules=session.selected_rules,
            source_session_id=session.id,
            source_filename=session.source_filename,
        )
    )


@router.get("/{template_id}")
async def get_template(
    template_id: int,
    repository: WorkflowTemplateRepository = Depends(get_template_repository),
) -> WorkflowTemplateDetail:
    try:
        return repository.get(template_id)
    except WorkflowTemplateNotFoundError as error:
        raise HTTPException(status_code=404, detail="Workflow template not found.") from error


@router.patch("/{template_id}")
async def update_template(
    template_id: int,
    payload: WorkflowTemplateUpdate,
    repository: WorkflowTemplateRepository = Depends(get_template_repository),
) -> WorkflowTemplateDetail:
    try:
        return repository.update(template_id, payload)
    except WorkflowTemplateNotFoundError as error:
        raise HTTPException(status_code=404, detail="Workflow template not found.") from error


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_id: int,
    repository: WorkflowTemplateRepository = Depends(get_template_repository),
) -> Response:
    try:
        repository.delete(template_id)
    except WorkflowTemplateNotFoundError as error:
        raise HTTPException(status_code=404, detail="Workflow template not found.") from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
