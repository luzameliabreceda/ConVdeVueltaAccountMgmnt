from typing import List, Optional
from injector import inject

from ...database.repository import BaseRepository
from ..models.user import User


class UserRepository(BaseRepository[User]):
    """User repository using SQLAlchemy ORM"""
    
    def __init__(self):
        super().__init__(User)
    
    # Domain-specific methods
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        return await self.find_one_by(email=email)
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return await self.exists_by(email=email)
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        return await self.exists_by(username=username)
    
    async def exists_by_national_id(self, national_id: str) -> bool:
        """Check if user exists by national ID"""
        return await self.exists_by(national_id=national_id)
    
    async def get_users_paginated(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with pagination (alias for find_all)"""
        return await self.find_all(limit=limit, offset=skip)