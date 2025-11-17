"""Health check router."""

from fastapi import APIRouter

from app.config import settings
from app.models import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status with service version and OpenMetadata configuration status
    """
    return HealthResponse(
        status="healthy",
        version=settings.service_version,
        openmetadata_configured=settings.openmetadata_configured,
    )
