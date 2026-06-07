from fastapi import APIRouter

from src.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
