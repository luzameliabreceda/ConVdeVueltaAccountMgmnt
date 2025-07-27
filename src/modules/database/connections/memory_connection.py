from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import asyncio
from pydantic_settings import BaseSettings

from ..connection import DatabaseConnection


class MemorySettings(BaseSettings):
    pass


class MemoryConnection(DatabaseConnection):
    
    def __init__(self, settings: MemorySettings = None):
        self.settings = settings or MemorySettings()
        self._connected = False
        self._tables = {}
    
    async def connect(self) -> None:
        self._connected = True
    
    async def disconnect(self) -> None:
        self._connected = False
        self._tables.clear()
    
    async def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        if table_name not in self._tables:
            self._tables[table_name] = []
    
    async def delete_table(self, table_name: str) -> None:
        if table_name in self._tables:
            del self._tables[table_name]
    
    async def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        if table_name not in self._tables:
            self._tables[table_name] = []
        
        self._tables[table_name].append(data)
        return data
    
    async def insert_many(self, table_name: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if table_name not in self._tables:
            self._tables[table_name] = []
        
        self._tables[table_name].extend(data)
        return data
    
    async def find_by_id(self, table_name: str, record_id: Any) -> Optional[Dict[str, Any]]:
        if table_name not in self._tables:
            return None
        
        for record in self._tables[table_name]:
            if record.get('id') == record_id:
                return record
        return None
    
    async def find_one(self, table_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if table_name not in self._tables:
            return None
        
        for record in self._tables[table_name]:
            if all(record.get(key) == value for key, value in filter_dict.items()):
                return record
        return None
    
    async def find_many(self, table_name: str, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        if table_name not in self._tables:
            return []
        
        matching_records = []
        for record in self._tables[table_name]:
            if all(record.get(key) == value for key, value in filter_dict.items()):
                matching_records.append(record)
        
        return matching_records[skip:skip + limit]
    
    async def update(self, table_name: str, record_id: Any, data: Dict[str, Any]) -> bool:
        if table_name not in self._tables:
            return False
        
        for i, record in enumerate(self._tables[table_name]):
            if record.get('id') == record_id:
                self._tables[table_name][i].update(data)
                return True
        return False
    
    async def delete(self, table_name: str, record_id: Any) -> bool:
        if table_name not in self._tables:
            return False
        
        for i, record in enumerate(self._tables[table_name]):
            if record.get('id') == record_id:
                del self._tables[table_name][i]
                return True
        return False
    
    async def count(self, table_name: str, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        if table_name not in self._tables:
            return 0
        
        if not filter_dict:
            return len(self._tables[table_name])
        
        count = 0
        for record in self._tables[table_name]:
            if all(record.get(key) == value for key, value in filter_dict.items()):
                count += 1
        return count
    
    async def exists(self, table_name: str, filter_dict: Dict[str, Any]) -> bool:
        return await self.find_one(table_name, filter_dict) is not None
    
    async def clear_table(self, table_name: str) -> None:
        if table_name in self._tables:
            self._tables[table_name].clear()
    
    @asynccontextmanager
    async def transaction(self):
        yield
    
    async def health_check(self) -> bool:
        return self._connected 