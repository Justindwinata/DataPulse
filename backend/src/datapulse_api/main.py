from fastapi import FastAPI

from datapulse_api import __version__
from datapulse_api.api.cleaning import router as cleaning_router
from datapulse_api.api.files import router as files_router
from datapulse_api.api.health import router as health_router
from datapulse_api.api.sessions import router as sessions_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="DataPulse API",
        summary="Deterministic CSV and Excel cleaner studio API.",
        version=__version__,
    )
    app.include_router(health_router)
    app.include_router(cleaning_router)
    app.include_router(files_router)
    app.include_router(sessions_router)
    return app


app = create_app()
