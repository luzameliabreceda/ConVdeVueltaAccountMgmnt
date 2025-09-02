import os
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool


class PostgreSQLConnection:
    """Singleton PostgreSQL connection manager using SQLAlchemy"""
    
    _instance: Optional['PostgreSQLConnection'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._connected = False
    
    def _build_database_url(self) -> str:
        """Build PostgreSQL connection URL from environment variables"""
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DATABASE', 'postgres')
        username = os.getenv('POSTGRES_USERNAME', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', 'postgres')
        
        return f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{database}"
    
    async def connect(self) -> None:
        """Initialize SQLAlchemy engine and session factory"""
        if self._engine:
            return
        
        try:
            database_url = self._build_database_url()
            
            self._engine = create_async_engine(
                database_url,
                echo=os.getenv('SQLALCHEMY_ECHO', 'false').lower() == 'true',
                pool_size=int(os.getenv('POSTGRES_MAX_POOL_SIZE', '10')),
                max_overflow=int(os.getenv('POSTGRES_MAX_OVERFLOW', '20')),
                pool_pre_ping=True,
                poolclass=NullPool if os.getenv('POSTGRES_USE_NULL_POOL', 'false').lower() == 'true' else None
            )
            
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            self._connected = True
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            self._connected = False
            raise
    
    async def disconnect(self) -> None:
        """Close SQLAlchemy engine"""
        if self._engine:
            await self._engine.dispose()
        self._connected = False
        self._engine = None
        self._session_factory = None
    
    def get_engine(self):
        """Get SQLAlchemy engine"""
        if not self._engine:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._engine
    
    def get_session_factory(self):
        """Get SQLAlchemy session factory"""
        if not self._session_factory:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._session_factory
    
    def get_session(self) -> AsyncSession:
        """Get new SQLAlchemy session"""
        session_factory = self.get_session_factory()
        return session_factory()
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self._connected and self._engine is not None
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            if not self.is_connected():
                return False
            
            async with self.get_session() as session:
                await session.execute("SELECT 1")
                return True
        except Exception as e:
            print(f"PostgreSQL health check failed: {e}")
            return False


# SQLAlchemy declarative base
Base = declarative_base()

# Global singleton instance
db_connection = PostgreSQLConnection()