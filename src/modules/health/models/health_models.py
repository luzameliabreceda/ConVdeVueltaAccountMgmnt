from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    service: str
    os_environment: str


class MessageResponse(BaseModel):
    message: str
    timestamp: datetime 