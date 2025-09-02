from typing import List
from injector import inject

from .user_service_interface import UserServiceInterface
from ..models.user import User
from ..models.dto import CreateUserRequest, UpdateUserRequest
from ..repositories.user_repository import UserRepository
from api.exceptions.http_exceptions import (
    ConflictException,
    NotFoundException,
    BadRequestException
)


class UserService(UserServiceInterface):
    
    @inject
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def create_user(self, request: CreateUserRequest) -> User:
        # Check if email already exists
        if await self._user_repository.exists_by_email(request.email):
            raise ConflictException(f"User with email {request.email} already exists")
        
        # Check if username already exists (if provided)
        if request.username and await self._user_repository.exists_by_username(request.username):
            raise ConflictException(f"User with username {request.username} already exists")
        
        # Check if national_id already exists (if provided)
        if request.national_id and await self._user_repository.exists_by_national_id(request.national_id):
            raise ConflictException(f"User with national ID {request.national_id} already exists")
        
        # Create user with all fields from request
        user = User(
            email=request.email,
            username=request.username,
            first_name=request.first_name,
            paternal_surname=request.paternal_surname,
            maternal_surname=request.maternal_surname,
            phone=request.phone,
            date_of_birth=request.date_of_birth,
            gender=request.gender,
            national_id=request.national_id,
            password_hash=request.password_hash,
            enabled=request.enabled
        )
        return await self._user_repository.save(user)
    
    async def get_user_by_id(self, user_id: str) -> User:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self._user_repository.get_users_paginated(skip=skip, limit=limit)
    
    async def update_user(self, user_id: str, name: str = None, email: str = None, is_active: bool = None) -> User:
        user = await self.get_user_by_id(user_id)
        
        if email and email != user.email:
            if await self._user_repository.exists_by_email(email):
                raise ConflictException(f"User with email {email} already exists")
        
        if name or email:
            user.update_profile(name=name, email=email)
        
        if is_active is not None:
            if is_active:
                user.activate()
            else:
                user.deactivate()
        
        return await self._user_repository.save(user)
    
    async def delete_user(self, user_id: str) -> bool:
        deleted = await self._user_repository.delete_by_id(user_id)
        if not deleted:
            raise NotFoundException(f"User with ID {user_id} not found")
        return True
    
    async def activate_user(self, user_id: str) -> User:
        user = await self.get_user_by_id(user_id)
        
        if user.enabled:
            raise BadRequestException(f"User {user_id} is already enabled")
        
        user.enable()
        return await self._user_repository.save(user) 