from typing import List
from fastapi import APIRouter, Depends, status, Query
from injector import inject

from ..services.user_service import UserService
from ..models.dto import CreateUserRequest, UpdateUserRequest, UpdateUserWithPasswordRequest, UpdateUserResponse


class UserController:
    
    @inject
    def __init__(self, user_service: UserService):
        self._user_service = user_service
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        @self.router.put(
            "/{user_id}",
            response_model=UpdateUserResponse,
            status_code=status.HTTP_200_OK,
            summary="Update User with Password",
            description="Update user information including password (will be hashed)"
        )
        async def update_user_with_password(user_id: str, request: UpdateUserWithPasswordRequest) -> UpdateUserResponse:
            return await self._user_service.update_user_with_password(user_id, request)
