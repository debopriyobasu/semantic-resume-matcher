from fastapi import APIRouter

from src.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, status_code=200)
async def health() -> HealthResponse:
    """
    Check the health status of the application.

    Returns a simple JSON response indicating that the service is running and
    able to accept requests.
    """
    return HealthResponse(status="ok")
