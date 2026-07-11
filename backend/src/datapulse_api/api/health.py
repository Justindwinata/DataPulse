from fastapi import APIRouter

from datapulse_api import __version__

router = APIRouter(tags=["system"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "datapulse-api",
        "version": __version__,
    }
