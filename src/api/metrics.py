from typing import Any

from fastapi import APIRouter

from src.core.metrics import metrics_store

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_model=dict[str, Any], status_code=200)
async def get_metrics() -> dict[str, Any]:
    """Retrieve application metrics."""
    return metrics_store.get_metrics()
