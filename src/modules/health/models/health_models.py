from datetime import datetime
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    environment: str
    service: str


class MessageResponse(BaseModel):
    message: str
    timestamp: datetime 