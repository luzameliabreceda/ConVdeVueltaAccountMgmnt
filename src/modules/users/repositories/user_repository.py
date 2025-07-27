from typing import List, Optional
from injector import inject

from ...database.repository import Repository
from ...database.connections.dynamodb_connection import DynamoDBConnection, DynamoDBSettings
from ..models.user import User


class UserRepository(Repository[User]):
    
    def __init__(self):
        settings = DynamoDBSettings()
        connection = DynamoDBConnection(settings)
        super().__init__(User, "users", connection)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.find_one(email=email)
    
    async def find_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.find_many(skip=skip, limit=limit, is_active=True)
    
    async def find_inactive_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        return await self.find_many(skip=skip, limit=limit, is_active=False)
    
    async def exists_by_email(self, email: str) -> bool:
        return await self.exists(email=email)
    
    async def activate_user(self, user_id: str) -> Optional[User]:
        return await self.update_by_id(user_id, is_active=True)
    
    async def deactivate_user(self, user_id: str) -> Optional[User]:
        return await self.update_by_id(user_id, is_active=False)
    
    async def update_profile(self, user_id: str, name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        updates = {}
        if name is not None:
            updates['name'] = name
        if email is not None:
            updates['email'] = email
        
        if updates:
            return await self.update_by_id(user_id, **updates)
        return None
    
    async def count_active_users(self) -> int:
        return await self.count(is_active=True)
    
    async def count_inactive_users(self) -> int:
        return await self.count(is_active=False) 