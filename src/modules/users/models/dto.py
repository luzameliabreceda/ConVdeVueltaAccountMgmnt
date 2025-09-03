from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    paternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    maternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    national_id: Optional[str] = Field(None, max_length=13)
    password_hash: Optional[str] = Field(None, max_length=255)
    enabled: bool = True


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    paternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    maternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    national_id: Optional[str] = Field(None, max_length=13)
    enabled: Optional[bool] = None


class UpdateProfileRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    paternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    maternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)


class UpdateContactRequest(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)


class SetPasswordRequest(BaseModel):
    password_hash: str = Field(..., max_length=255)


class UpdateUserWithPasswordRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    paternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    maternal_surname: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, max_length=10)
    national_id: Optional[str] = Field(None, max_length=13)
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="Plain text password to be hashed")
    enabled: Optional[bool] = None


class UpdateUserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    paternal_surname: Optional[str] = None
    maternal_surname: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    password_hash: Optional[str] = None
    registration_date: datetime
    enabled: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    paternal_surname: Optional[str] = None
    maternal_surname: Optional[str] = None
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    national_id: Optional[str] = None
    registration_date: datetime
    enabled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None


class UsersListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    skip: int
    limit: int 