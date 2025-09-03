from abc import ABC, abstractmethod
from datetime import timedelta
from typing import Optional, Dict, Any


class JWTService(ABC):
    """Interface for JWT token generation and validation"""
    
    @abstractmethod
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        pass
    
    @abstractmethod
    def create_user_token(self, user_id: str, email: str) -> str:
        """Create a JWT token for a user"""
        pass

