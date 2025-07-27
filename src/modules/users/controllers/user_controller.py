from typing import List
from fastapi import APIRouter, Depends, status, Query
from injector import inject

from ..services.user_service_interface import UserServiceInterface
from ..models.dto import CreateUserRequest, UpdateUserRequest


class UserController:
    
    @inject
    def __init__(self, user_service: UserServiceInterface):
        self._user_service = user_service
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        @self.router.post(
            "/",
            status_code=status.HTTP_201_CREATED,
            summary="Create User",
            description="Create a new user with email and name"
        )
        async def create_user(request: CreateUserRequest):
            return await self._user_service.create_user(request.email, request.name)
        
        @self.router.get(
            "/",
            summary="List Users",
            description="Get a list of all users with pagination"
        )
        async def get_users(
            skip: int = Query(0, ge=0, description="Number of users to skip"),
            limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return")
        ):
            return await self._user_service.get_users(skip=skip, limit=limit)
        
        @self.router.get(
            "/{user_id}",
            summary="Get User",
            description="Get a specific user by their ID"
        )
        async def get_user(user_id: str):
            return await self._user_service.get_user_by_id(user_id)
        
        @self.router.put(
            "/{user_id}",
            summary="Update User",
            description="Update user information"
        )
        async def update_user(user_id: str, request: UpdateUserRequest):
            return await self._user_service.update_user(
                user_id=user_id,
                name=request.name,
                email=request.email,
                is_active=request.is_active
            )
        
        @self.router.delete(
            "/{user_id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete User",
            description="Delete a user by their ID"
        )
        async def delete_user(user_id: str):
            return await self._user_service.delete_user(user_id)
        
        @self.router.post(
            "/{user_id}/activate",
            summary="Activate User",
            description="Activate a user by their ID"
        )
        async def activate_user(user_id: str):
            return await self._user_service.activate_user(user_id)