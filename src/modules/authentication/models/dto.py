from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    email: EmailStr


class LoginResponse(BaseModel):
    user_id: str
    token: str


class SignupResponse(BaseModel):
    user_id: str
    token: str
