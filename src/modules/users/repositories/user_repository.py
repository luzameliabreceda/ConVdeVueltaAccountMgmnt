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
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """Find user by username"""
        return await self.find_one_by(username=username)
    
    async def find_by_national_id(self, national_id: str) -> Optional[User]:
        """Find user by national ID"""
        return await self.find_one_by(national_id=national_id)
    
    async def find_enabled_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find enabled users with pagination"""
        return await self.find_by(enabled=True)
    
    async def find_disabled_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Find disabled users with pagination"""
        return await self.find_by(enabled=False)
    
    async def exists_by_email(self, email: str) -> bool:
        """Check if user exists by email"""
        return await self.exists_by(email=email)
    
    async def exists_by_username(self, username: str) -> bool:
        """Check if user exists by username"""
        return await self.exists_by(username=username)
    
    async def exists_by_national_id(self, national_id: str) -> bool:
        """Check if user exists by national ID"""
        return await self.exists_by(national_id=national_id)
    
    async def enable_user(self, user_id: str) -> Optional[User]:
        """Enable user by ID"""
        return await self.update_by_id(user_id, enabled=True)
    
    async def disable_user(self, user_id: str) -> Optional[User]:
        """Disable user by ID"""
        return await self.update_by_id(user_id, enabled=False)
    
    async def update_profile(self, user_id: str, first_name: Optional[str] = None, 
                           paternal_surname: Optional[str] = None, maternal_surname: Optional[str] = None,
                           phone: Optional[str] = None, date_of_birth = None, 
                           gender: Optional[str] = None) -> Optional[User]:
        """Update user profile by ID"""
        updates = {}
        if first_name is not None:
            updates['first_name'] = first_name
        if paternal_surname is not None:
            updates['paternal_surname'] = paternal_surname
        if maternal_surname is not None:
            updates['maternal_surname'] = maternal_surname
        if phone is not None:
            updates['phone'] = phone
        if date_of_birth is not None:
            updates['date_of_birth'] = date_of_birth
        if gender is not None:
            updates['gender'] = gender
        
        if updates:
            return await self.update_by_id(user_id, **updates)
        return None
    
    async def update_contact_info(self, user_id: str, email: Optional[str] = None, 
                                phone: Optional[str] = None) -> Optional[User]:
        """Update user contact information by ID"""
        updates = {}
        if email is not None:
            updates['email'] = email
        if phone is not None:
            updates['phone'] = phone
        
        if updates:
            return await self.update_by_id(user_id, **updates)
        return None
    
    async def set_password(self, user_id: str, password_hash: str) -> Optional[User]:
        """Set user password hash by ID"""
        return await self.update_by_id(user_id, password_hash=password_hash)
    
    async def count_enabled_users(self) -> int:
        """Count enabled users"""
        return await self.count(enabled=True)
    
    async def count_disabled_users(self) -> int:
        """Count disabled users"""
        return await self.count(enabled=False)
    
    async def get_users_paginated(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users with pagination (alias for find_all)"""
        return await self.find_all(limit=limit, offset=skip)