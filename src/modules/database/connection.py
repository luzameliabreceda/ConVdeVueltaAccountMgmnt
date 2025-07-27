from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Generic, TypeVar
from contextlib import asynccontextmanager

T = TypeVar('T')


class DatabaseConnection(ABC):
    
    @abstractmethod
    async def connect(self) -> None:
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        pass
    
    @abstractmethod
    async def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def delete_table(self, table_name: str) -> None:
        pass
    
    @abstractmethod
    async def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def insert_many(self, table_name: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def find_by_id(self, table_name: str, record_id: Any) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def find_one(self, table_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def find_many(self, table_name: str, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    async def update(self, table_name: str, record_id: Any, data: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def delete(self, table_name: str, record_id: Any) -> bool:
        pass
    
    @abstractmethod
    async def count(self, table_name: str, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        pass
    
    @abstractmethod
    async def exists(self, table_name: str, filter_dict: Dict[str, Any]) -> bool:
        pass
    
    @abstractmethod
    async def clear_table(self, table_name: str) -> None:
        pass
    
    @asynccontextmanager
    @abstractmethod
    async def transaction(self):
        yield
    
    @abstractmethod
    async def health_check(self) -> bool:
        pass 