from datetime import datetime
from fastapi import APIRouter, status

from ..models.health_models import HealthResponse
from api.core.config import settings


class HealthController:
    
    def __init__(self):
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        @self.router.get(
            "/health",
            response_model=HealthResponse,
            status_code=status.HTTP_200_OK,
            summary="Health Check",
            description="Check if the service is running and healthy"
        )
        async def health_check() -> HealthResponse:
            return HealthResponse(
                status="healthy",
                timestamp=datetime.utcnow(),
                version=settings.app_version,
                environment=settings.environment,
                service=settings.app_name,
            )