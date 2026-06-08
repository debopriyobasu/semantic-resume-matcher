from fastapi import FastAPI

from src.api.health import router as health_router
from src.api.upload import router as upload_router
from src.api.results import router as results_router
from src.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    app.include_router(health_router)
    app.include_router(upload_router)
    app.include_router(results_router)
    return app


app = create_app()
