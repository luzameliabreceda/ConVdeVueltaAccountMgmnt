from typing import Generic, TypeVar, List, Optional, Any, Dict
from abc import ABC

from .model import Model
from .connection import DatabaseConnection

T = TypeVar('T', bound=Model)


class Repository(Generic[T]):
    
    def __init__(self, model_class: type[T], table_name: str, connection: DatabaseConnection):
        self.model_class = model_class
        self.table_name = table_name
        self.connection = connection
    
    async def create(self, entity: T) -> T:
        data = entity.to_dict()
        created_data = await self.connection.insert(self.table_name, data)
        return self.model_class.from_dict(created_data)
    
    async def create_many(self, entities: List[T]) -> List[T]:
        data_list = [entity.to_dict() for entity in entities]
        created_data_list = await self.connection.insert_many(self.table_name, data_list)
        return [self.model_class.from_dict(data) for data in created_data_list]
    
    async def find_by_id(self, entity_id: Any) -> Optional[T]:
        data = await self.connection.find_by_id(self.table_name, entity_id)
        if data:
            return self.model_class.from_dict(data)
        return None
    
    async def find_one(self, **filters) -> Optional[T]:
        data = await self.connection.find_one(self.table_name, filters)
        if data:
            return self.model_class.from_dict(data)
        return None
    
    async def find_many(self, skip: int = 0, limit: int = 100, **filters) -> List[T]:
        data_list = await self.connection.find_many(self.table_name, filters, skip=skip, limit=limit)
        return [self.model_class.from_dict(data) for data in data_list]
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return await self.find_many(skip=skip, limit=limit)
    
    async def update(self, entity: T) -> T:
        data = entity.to_dict()
        success = await self.connection.update(self.table_name, entity.id, data)
        if success:
            return entity
        raise Exception("Failed to update entity")
    
    async def update_by_id(self, entity_id: Any, **updates) -> Optional[T]:
        entity = await self.find_by_id(entity_id)
        if entity:
            entity.update(**updates)
            return await self.update(entity)
        return None
    
    async def delete(self, entity_id: Any) -> bool:
        return await self.connection.delete(self.table_name, entity_id)
    
    async def delete_entity(self, entity: T) -> bool:
        return await self.delete(entity.id)
    
    async def exists(self, **filters) -> bool:
        return await self.connection.exists(self.table_name, filters)
    
    async def exists_by_id(self, entity_id: Any) -> bool:
        return await self.connection.exists(self.table_name, {"id": entity_id})
    
    async def count(self, **filters) -> int:
        return await self.connection.count(self.table_name, filters if filters else None)
    
    async def count_all(self) -> int:
        return await self.count()
    
    async def clear(self) -> None:
        await self.connection.clear_table(self.table_name)
    
    async def health_check(self) -> bool:
        return await self.connection.health_check() 