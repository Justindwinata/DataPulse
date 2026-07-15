from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from datapulse_api import __version__
from datapulse_api.api.cleaning import router as cleaning_router
from datapulse_api.api.files import router as files_router
from datapulse_api.api.health import router as health_router
from datapulse_api.api.sessions import router as sessions_router
from datapulse_api.api.templates import router as templates_router

LOCAL_FRONTEND_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app() -> FastAPI:
    app = FastAPI(
        title="DataPulse API",
        summary="Deterministic CSV and Excel cleaner studio API.",
        version=__version__,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=LOCAL_FRONTEND_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    app.include_router(health_router)
    app.include_router(cleaning_router)
    app.include_router(files_router)
    app.include_router(sessions_router)
    app.include_router(templates_router)
    return app


app = create_app()
