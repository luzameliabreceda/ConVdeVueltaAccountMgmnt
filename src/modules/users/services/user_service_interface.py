from abc import ABC, abstractmethod
from typing import List, Optional

from ..models.user import User


class UserServiceInterface(ABC):
    
    @abstractmethod
    async def create_user(self, email: str, name: str) -> User:
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> User:
        pass
    
    @abstractmethod
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, name: str, email: str, is_active: bool) -> User:
        pass
    
    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def activate_user(self, user_id: str) -> User:
        pass 