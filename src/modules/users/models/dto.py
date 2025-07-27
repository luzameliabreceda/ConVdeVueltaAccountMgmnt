from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)


class UpdateUserRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int 