import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.api.health import router as health_router
from src.api.upload import router as upload_router
from src.api.results import router as results_router
from src.api.metrics import router as metrics_router
from src.core.config import get_settings
from src.core.logger import setup_logging, trace_id_ctx_var


def create_app() -> FastAPI:
    # Set up JSON structured logging
    setup_logging()
    
    settings = get_settings()
    app = FastAPI(title=settings.app_name)
    
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
    return app


app = create_app()
