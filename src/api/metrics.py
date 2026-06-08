from typing import Any, Dict
from fastapi import APIRouter

from src.core.metrics import metrics_store

router = APIRouter(tags=["metrics"])

@router.get("/metrics", response_model=Dict[str, Any], status_code=200)
async def get_metrics() -> Dict[str, Any]:
    """Retrieve application metrics."""
    return metrics_store.get_metrics()
