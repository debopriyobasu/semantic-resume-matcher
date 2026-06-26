import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.api.health import router as health_router
from src.api.jobs import router as jobs_router
from src.api.metrics import router as metrics_router
from src.api.results import router as results_router
from src.api.upload import router as upload_router
from src.core.config import get_settings
from src.core.logger import setup_logging, trace_id_ctx_var


def create_app() -> FastAPI:
    # Set up JSON structured logging
    setup_logging()

    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    # Enable CORS for local development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def trace_id_middleware(request: Request, call_next):
        trace_id = str(uuid.uuid4())
        trace_id_ctx_var.set(trace_id)
        response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        return response

    app.include_router(health_router)
    app.include_router(upload_router)
    app.include_router(results_router)
    app.include_router(metrics_router)
    app.include_router(jobs_router)
    return app


app = create_app()
