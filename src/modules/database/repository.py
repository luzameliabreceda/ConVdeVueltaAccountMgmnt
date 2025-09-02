from typing import Generic, TypeVar, List, Optional, Any, Dict, Type
from abc import ABC
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from .model import BaseModel
from .connections.postgresql_connection import db_connection, Base

T = TypeVar('T', bound=BaseModel)


class BaseRepository(Generic[T], ABC):
    """Base SQLAlchemy repository class similar to JPA Repository pattern"""
    
    def __init__(self, model_class: Type[T]):
        self.model_class = model_class
        self.connection = db_connection
    
    async def _ensure_tables_exist(self) -> None:
        """Create tables if they don't exist"""
        try:
            if not self.connection.is_connected():
                await self.connection.connect()
            
            engine = self.connection.get_engine()
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        except Exception as e:
            print(f"Warning: Could not ensure tables exist: {e}")
    
    @asynccontextmanager
    async def _get_session(self):
        """Get database session with automatic cleanup"""
        if not self.connection.is_connected():
            await self.connection.connect()
        
        session = self.connection.get_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # JPA-style methods
    
    async def save(self, entity: T) -> T:
        """Save entity (insert or update)"""
        await self._ensure_tables_exist()
        
        async with self._get_session() as session:
            # Check if entity exists
            if entity.id:
                existing = await session.get(self.model_class, entity.id)
                if existing:
                    # Update existing
                    for column in self.model_class.__table__.columns:
                        if column.name not in ['id', 'created_at']:
                            setattr(existing, column.name, getattr(entity, column.name))
                    await session.commit()
                    await session.refresh(existing)
                    return existing
            
            # Insert new
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity
    
    async def save_all(self, entities: List[T]) -> List[T]:
        """Save multiple entities"""
        await self._ensure_tables_exist()
        
        async with self._get_session() as session:
            session.add_all(entities)
            await session.commit()
            
            # Refresh all entities
            for entity in entities:
                await session.refresh(entity)
            
            return entities
    
    async def find_by_id(self, entity_id: Any, include_deleted: bool = False) -> Optional[T]:
        """Find entity by ID"""
        async with self._get_session() as session:
            stmt = select(self.model_class).where(self.model_class.id == entity_id)
            
            # Filter out soft deleted entities unless explicitly requested
            if not include_deleted:
                stmt = stmt.where(self.model_class.deleted_at.is_(None))
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
    
    async def find_all(self, limit: int = 100, offset: int = 0, include_deleted: bool = False) -> List[T]:
        """Find all entities with pagination"""
        async with self._get_session() as session:
            stmt = select(self.model_class)
            
            # Filter out soft deleted entities unless explicitly requested
            if not include_deleted:
                stmt = stmt.where(self.model_class.deleted_at.is_(None))
            
            stmt = stmt.order_by(self.model_class.created_at.desc()).limit(limit).offset(offset)
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def find_by(self, include_deleted: bool = False, **filters) -> List[T]:
        """Find entities by filters"""
        async with self._get_session() as session:
            stmt = select(self.model_class)
            
            # Filter out soft deleted entities unless explicitly requested
            if not include_deleted:
                stmt = stmt.where(self.model_class.deleted_at.is_(None))
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    stmt = stmt.where(column == value)
            
            stmt = stmt.order_by(self.model_class.created_at.desc())
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def find_one_by(self, **filters) -> Optional[T]:
        """Find one entity by filters"""
        results = await self.find_by(**filters)
        return results[0] if results else None
    
    async def exists_by_id(self, entity_id: Any) -> bool:
        """Check if entity exists by ID"""
        entity = await self.find_by_id(entity_id)
        return entity is not None
    
    async def exists_by(self, **filters) -> bool:
        """Check if entity exists by filters"""
        async with self._get_session() as session:
            stmt = select(self.model_class)
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    stmt = stmt.where(column == value)
            
            stmt = stmt.limit(1)
            result = await session.execute(stmt)
            return result.scalar_one_or_none() is not None
    
    async def count(self, **filters) -> int:
        """Count entities"""
        async with self._get_session() as session:
            stmt = select(func.count(self.model_class.id))
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    stmt = stmt.where(column == value)
            
            result = await session.execute(stmt)
            return result.scalar_one()
    
    async def delete_by_id(self, entity_id: Any, hard_delete: bool = False) -> bool:
        """Delete entity by ID"""
        async with self._get_session() as session:
            entity = await session.get(self.model_class, entity_id)
            if entity:
                if hard_delete:
                    # Hard delete - remove from database
                    await session.delete(entity)
                else:
                    # Soft delete - set deleted_at timestamp
                    entity.soft_delete()
                    session.add(entity)
                
                await session.commit()
                return True
            return False
    
    async def delete(self, entity: T, hard_delete: bool = False) -> bool:
        """Delete entity"""
        async with self._get_session() as session:
            if hard_delete:
                # Hard delete - remove from database
                await session.delete(entity)
            else:
                # Soft delete - set deleted_at timestamp
                entity.soft_delete()
                session.add(entity)
            
            await session.commit()
            return True
    
    async def delete_by(self, **filters) -> int:
        """Delete entities by filters and return count of deleted entities"""
        async with self._get_session() as session:
            stmt = delete(self.model_class)
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    stmt = stmt.where(column == value)
            
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
    
    async def delete_all(self) -> int:
        """Delete all entities and return count of deleted entities"""
        async with self._get_session() as session:
            stmt = delete(self.model_class)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
    
    async def update_by_id(self, entity_id: Any, **updates) -> Optional[T]:
        """Update entity by ID"""
        async with self._get_session() as session:
            entity = await session.get(self.model_class, entity_id)
            if entity:
                for key, value in updates.items():
                    if hasattr(entity, key):
                        setattr(entity, key, value)
                await session.commit()
                await session.refresh(entity)
                return entity
            return None
    
    async def update_by(self, filters: Dict[str, Any], updates: Dict[str, Any]) -> int:
        """Update entities by filters and return count of updated entities"""
        async with self._get_session() as session:
            stmt = update(self.model_class)
            
            # Apply filters
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    column = getattr(self.model_class, key)
                    stmt = stmt.where(column == value)
            
            # Apply updates
            stmt = stmt.values(**updates)
            
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount
    
    # Utility methods
    
    async def flush(self) -> None:
        """Flush current session"""
        async with self._get_session() as session:
            await session.flush()
    
    async def refresh(self, entity: T) -> T:
        """Refresh entity from database"""
        async with self._get_session() as session:
            await session.refresh(entity)
            return entity
    
    @asynccontextmanager
    async def transaction(self):
        """Transaction context manager"""
        async with self._get_session() as session:
            async with session.begin():
                yield session
    
    # Soft Delete specific methods
    
    async def restore_by_id(self, entity_id: Any) -> bool:
        """Restore a soft deleted entity by ID"""
        async with self._get_session() as session:
            entity = await session.get(self.model_class, entity_id)
            if entity and entity.is_deleted():
                entity.restore()
                session.add(entity)
                await session.commit()
                return True
            return False
    
    async def find_deleted(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Find only soft deleted entities"""
        async with self._get_session() as session:
            stmt = select(self.model_class).where(
                self.model_class.deleted_at.is_not(None)
            ).order_by(self.model_class.deleted_at.desc()).limit(limit).offset(offset)
            
            result = await session.execute(stmt)
            return list(result.scalars().all())
    
    async def count_deleted(self) -> int:
        """Count soft deleted entities"""
        async with self._get_session() as session:
            stmt = select(func.count(self.model_class.id)).where(
                self.model_class.deleted_at.is_not(None)
            )
            result = await session.execute(stmt)
            return result.scalar_one()