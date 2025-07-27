from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
import asyncio
from pydantic_settings import BaseSettings

from pynamodb.models import Model as PynamoModel
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute
from pynamodb.exceptions import DoesNotExist, PutError, DeleteError
from pynamodb.connection import Connection

from ..connection import DatabaseConnection


class DynamoDBSettings(BaseSettings):
    
    aws_region: str = "us-west-2"
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    
    table_prefix: str = ""
    billing_mode: str = "PAY_PER_REQUEST"
    read_capacity_units: int = 5
    write_capacity_units: int = 5
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class DynamoDBConnection(DatabaseConnection):
    
    def __init__(self, settings: DynamoDBSettings):
        self.settings = settings
        self._connected = False
        self._tables = {}
        self._connection = None
    
    async def connect(self) -> None:
        try:
            self._connection = Connection(
                region=self.settings.aws_region,
                aws_access_key_id=self.settings.aws_access_key_id,
                aws_secret_access_key=self.settings.aws_secret_access_key
            )
            self._connected = True
        except Exception as e:
            print(f"Failed to connect to DynamoDB: {e}")
            self._connected = False
    
    async def disconnect(self) -> None:
        self._connected = False
        self._connection = None
    
    def _create_dynamic_model(self, table_name: str) -> type[PynamoModel]:
        
        class DynamicModel(PynamoModel):
            id = UnicodeAttribute(hash_key=True)
            created_at = UTCDateTimeAttribute(null=True)
            updated_at = UTCDateTimeAttribute(null=True)
            
            class Meta:
                table_name = f"{self.settings.table_prefix}{table_name}"
                region = self.settings.aws_region
                billing_mode = self.settings.billing_mode
                
                if self.settings.billing_mode == "PROVISIONED":
                    read_capacity_units = self.settings.read_capacity_units
                    write_capacity_units = self.settings.write_capacity_units
        
        return DynamicModel
    
    async def create_table(self, table_name: str, schema: Dict[str, Any]) -> None:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            if not model_class.exists():
                model_class.create_table(wait=True)
                print(f"Created table: {model_class.Meta.table_name}")
            else:
                print(f"Table already exists: {model_class.Meta.table_name}")
                
        except Exception as e:
            print(f"Failed to create table {table_name}: {e}")
            raise
    
    async def delete_table(self, table_name: str) -> None:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            if model_class.exists():
                model_class.delete_table()
                print(f"Deleted table: {model_class.Meta.table_name}")
            else:
                print(f"Table does not exist: {model_class.Meta.table_name}")
                
        except Exception as e:
            print(f"Failed to delete table {table_name}: {e}")
            raise
    
    async def insert(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            item = model_class(**data)
            item.save()
            
            return item.attribute_values
            
        except PutError as e:
            print(f"Failed to insert into {table_name}: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error inserting into {table_name}: {e}")
            raise
    
    async def insert_many(self, table_name: str, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            with model_class.batch_write() as batch:
                for item_data in data:
                    item = model_class(**item_data)
                    batch.save(item)
            
            return data
            
        except Exception as e:
            print(f"Failed to batch insert into {table_name}: {e}")
            raise
    
    async def find_by_id(self, table_name: str, record_id: Any) -> Optional[Dict[str, Any]]:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            item = model_class.get(str(record_id))
            return item.attribute_values
            
        except DoesNotExist:
            return None
        except Exception as e:
            print(f"Failed to find by ID in {table_name}: {e}")
            return None
    
    async def find_one(self, table_name: str, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            for item in model_class.scan():
                if all(getattr(item, key, None) == value for key, value in filter_dict.items()):
                    return item.attribute_values
            
            return None
            
        except Exception as e:
            print(f"Failed to find one in {table_name}: {e}")
            return None
    
    async def find_many(self, table_name: str, filter_dict: Dict[str, Any], skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            items = []
            count = 0
            
            for item in model_class.scan():
                if all(getattr(item, key, None) == value for key, value in filter_dict.items()):
                    if count >= skip:
                        items.append(item.attribute_values)
                        if len(items) >= limit:
                            break
                    count += 1
            
            return items
            
        except Exception as e:
            print(f"Failed to find many in {table_name}: {e}")
            return []
    
    async def update(self, table_name: str, record_id: Any, data: Dict[str, Any]) -> bool:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            item = model_class.get(str(record_id))
            
            for key, value in data.items():
                setattr(item, key, value)
            
            item.save()
            return True
            
        except DoesNotExist:
            print(f"Item with ID {record_id} not found in {table_name}")
            return False
        except Exception as e:
            print(f"Failed to update in {table_name}: {e}")
            return False
    
    async def delete(self, table_name: str, record_id: Any) -> bool:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            item = model_class.get(str(record_id))
            item.delete()
            return True
            
        except DoesNotExist:
            print(f"Item with ID {record_id} not found in {table_name}")
            return False
        except DeleteError as e:
            print(f"Failed to delete from {table_name}: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error deleting from {table_name}: {e}")
            return False
    
    async def count(self, table_name: str, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            if not filter_dict:
                return model_class.count()
            else:
                count = 0
                for item in model_class.scan():
                    if all(getattr(item, key, None) == value for key, value in filter_dict.items()):
                        count += 1
                return count
                
        except Exception as e:
            print(f"Failed to count in {table_name}: {e}")
            return 0
    
    async def exists(self, table_name: str, filter_dict: Dict[str, Any]) -> bool:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            for item in model_class.scan():
                if all(getattr(item, key, None) == value for key, value in filter_dict.items()):
                    return True
            return False
            
        except Exception as e:
            print(f"Failed to check exists in {table_name}: {e}")
            return False
    
    async def clear_table(self, table_name: str) -> None:
        try:
            model_class = self._create_dynamic_model(table_name)
            
            with model_class.batch_write() as batch:
                for item in model_class.scan():
                    batch.delete(item)
                    
        except Exception as e:
            print(f"Failed to clear table {table_name}: {e}")
            raise
    
    @asynccontextmanager
    async def transaction(self):
        try:
            yield self
        except Exception as e:
            print(f"Transaction failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        try:
            if not self._connected:
                return False
            
            return True
            
        except Exception as e:
            print(f"Health check failed: {e}")
            return False 