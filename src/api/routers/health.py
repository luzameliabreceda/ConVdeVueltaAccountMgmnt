"""
Health check endpoints.
"""
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from ..core.config import settings


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    version: str
    environment: str
    service: str


class MessageResponse(BaseModel):
    """Generic message response model."""
    message: str
    timestamp: datetime


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the service is running and healthy"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns the current status of the service.
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment,
        service=settings.app_name
    )


@router.get(
    "/test",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Test Endpoint",
    description="Simple test endpoint to verify the API is working"
)
async def test_endpoint() -> MessageResponse:
    """
    Test endpoint.
    
    Simple endpoint for testing purposes.
    """
    return MessageResponse(
        message="Hello from Microservice Template! 🚀",
        timestamp=datetime.utcnow()
    ) 