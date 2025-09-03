from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.user import User
from ..models.dto import CreateUserRequest, UpdateUserWithPasswordRequest, UpdateUserResponse


class UserService(ABC):
    
    @abstractmethod
    async def create_user(self, request: CreateUserRequest) -> User:
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update_user_with_password(self, user_id: str, request: UpdateUserWithPasswordRequest) -> UpdateUserResponse:
        pass 