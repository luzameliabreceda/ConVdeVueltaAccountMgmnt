from typing import List, Optional
from injector import inject

from ..user_service import UserService
from ..password_service import PasswordService
from ...models.user import User
from ...models.dto import CreateUserRequest, UpdateUserWithPasswordRequest, UpdateUserResponse
from ...repositories.user_repository import UserRepository
from api.exceptions.http_exceptions import (
    ConflictException,
    NotFoundException,
    BadRequestException
)


class UserServiceImpl(UserService):
    
    @inject
    def __init__(self, user_repository: UserRepository, password_service: PasswordService):
        self._user_repository = user_repository
        self._password_service = password_service
    
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
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        return await self._user_repository.find_by_email(email)
    
    async def update_user_with_password(self, user_id: str, request: UpdateUserWithPasswordRequest) -> UpdateUserResponse:
        # Get user by ID
        user = await self._user_repository.find_by_id(user_id)
        
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        
        # Update fields if provided
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.paternal_surname is not None:
            user.paternal_surname = request.paternal_surname
        if request.maternal_surname is not None:
            user.maternal_surname = request.maternal_surname
        if request.phone is not None:
            user.phone = request.phone
        if request.date_of_birth is not None:
            user.date_of_birth = request.date_of_birth
        if request.gender is not None:
            user.gender = request.gender
        if request.national_id is not None:
            user.national_id = request.national_id
        if request.email is not None:
            user.email = request.email
        if request.username is not None:
            user.username = request.username
        if request.enabled is not None:
            if request.enabled:
                user.enable()
            else:
                user.disable()
        
        # Hash password if provided
        if request.password:
            user.password_hash = self._password_service.hash_password(request.password)
        
        # Save the updated user
        updated_user = await self._user_repository.save(user)
        
        # Return the response DTO
        return UpdateUserResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            username=updated_user.username,
            first_name=updated_user.first_name,
            paternal_surname=updated_user.paternal_surname,
            maternal_surname=updated_user.maternal_surname,
            phone=updated_user.phone,
            date_of_birth=updated_user.date_of_birth,
            gender=updated_user.gender,
            national_id=updated_user.national_id,
            password_hash=updated_user.password_hash,
            registration_date=updated_user.registration_date,
            enabled=updated_user.enabled,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at,
            deleted_at=updated_user.deleted_at
        ) 