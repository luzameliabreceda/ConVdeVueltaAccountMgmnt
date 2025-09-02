from abc import ABCMeta
from typing import Dict, Any, TypeVar
from datetime import datetime
import uuid
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

from .connections.postgresql_connection import Base, db_connection

T = TypeVar('T', bound='BaseModel')


# Custom metaclass that combines SQLAlchemy's DeclarativeMeta with ABCMeta
class BaseModelMeta(type(Base), ABCMeta):
    pass


class BaseModel(Base, metaclass=BaseModelMeta):
    """Base SQLAlchemy model class for all entities"""
    
    __abstract__ = True
    
    # Base columns for all entities
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True, index=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        result = {}
        
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Handle different data types
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, uuid.UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        """Create model instance from dictionary"""
        # Filter only the columns that exist in the model
        valid_columns = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_columns}
        
        # Parse datetime strings if needed
        for key, value in filtered_data.items():
            if isinstance(value, str) and key in ['created_at', 'updated_at']:
                try:
                    from dateutil.parser import parse
                    filtered_data[key] = parse(value)
                except (ValueError, ImportError):
                    pass
        
        return cls(**filtered_data)
    
    def update_fields(self, **kwargs) -> None:
        """Update model fields"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # SQLAlchemy will handle updated_at automatically with onupdate
    
    def soft_delete(self) -> None:
        """Soft delete this entity by setting deleted_at timestamp"""
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore a soft deleted entity by clearing deleted_at"""
        self.deleted_at = None
    
    def is_deleted(self) -> bool:
        """Check if this entity is soft deleted"""
        return self.deleted_at is not None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, BaseModel):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    # Active Record Pattern - Instance Methods Only
    
    @classmethod
    async def _get_session(cls) -> AsyncSession:
        """Get database session"""
        if not db_connection.is_connected():
            await db_connection.connect()
        return db_connection.get_session()
    
    @classmethod
    async def _ensure_tables_exist(cls) -> None:
        """Ensure tables exist"""
        try:
            if not db_connection.is_connected():
                await db_connection.connect()
            
            engine = db_connection.get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Warning: Could not ensure tables exist: {e}")
    
    async def save(self: T) -> T:
        """Save this entity to database (Active Record pattern)"""
        await self._ensure_tables_exist()
        
        session = await self._get_session()
        try:
            # Check if entity exists
            if self.id:
                existing = await session.get(self.__class__, self.id)
                if existing:
                    # Update existing
                    for column in self.__class__.__table__.columns:
                        if column.name not in ['id', 'created_at']:
                            setattr(existing, column.name, getattr(self, column.name))
                    await session.commit()
                    await session.refresh(existing)
                    return existing
            
            # Insert new
            session.add(self)
            await session.commit()
            await session.refresh(self)
            return self
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def delete(self, hard_delete: bool = False) -> bool:
        """Delete this entity from database (Active Record pattern)
        
        Args:
            hard_delete: If True, permanently delete from database. If False, soft delete.
        """
        session = await self._get_session()
        try:
            if hard_delete:
                # Hard delete - remove from database
                await session.delete(self)
            else:
                # Soft delete - set deleted_at timestamp
                self.soft_delete()
                session.add(self)
            
            await session.commit()
            return True
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    async def refresh(self: T) -> T:
        """Refresh this entity from database (Active Record pattern)"""
        session = await self._get_session()
        try:
            await session.refresh(self)
            return self
        finally:
            await session.close()


# Alias for backward compatibility
Model = BaseModel