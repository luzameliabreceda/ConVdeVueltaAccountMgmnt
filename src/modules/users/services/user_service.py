from typing import List
from injector import inject

from .user_service_interface import UserServiceInterface
from ..models.user import User
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
    
    async def create_user(self, email: str, name: str) -> User:
        if await self._user_repository.exists_by_email(email):
            raise ConflictException(f"User with email {email} already exists")
        
        user = User(email=email, name=name)
        return await self._user_repository.create(user)
    
    async def get_user_by_id(self, user_id: str) -> User:
        user = await self._user_repository.find_by_id(user_id)
        if not user:
            raise NotFoundException(f"User with ID {user_id} not found")
        return user
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self._user_repository.find_all(skip=skip, limit=limit)
    
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
        
        return await self._user_repository.update(user)
    
    async def delete_user(self, user_id: str) -> bool:
        deleted = await self._user_repository.delete(user_id)
        if not deleted:
            raise NotFoundException(f"User with ID {user_id} not found")
        return True
    
    async def activate_user(self, user_id: str) -> User:
        user = await self.get_user_by_id(user_id)
        
        if user.is_active:
            raise BadRequestException(f"User {user_id} is already active")
        
        user.activate()
        return await self._user_repository.update(user) 