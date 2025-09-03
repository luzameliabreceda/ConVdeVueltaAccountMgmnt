import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from injector import inject
from api.core.config import settings
from ..jwt_service import JWTService


class JWTServiceImpl(JWTService):
    """Service for JWT token generation and validation"""
    
    @inject
    def __init__(self):
        pass
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Default to 30 minutes
            expire = datetime.utcnow() + timedelta(minutes=30)
        
        to_encode.update({"exp": expire})
        
        # Use a secret key from settings or environment
        secret_key = getattr(settings, 'jwt_secret_key', 'your-secret-key-change-in-production')
        algorithm = getattr(settings, 'jwt_algorithm', 'HS256')
        
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            secret_key = getattr(settings, 'jwt_secret_key', 'your-secret-key-change-in-production')
            algorithm = getattr(settings, 'jwt_algorithm', 'HS256')
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
    
    def create_user_token(self, user_id: str, email: str) -> str:
        """Create a JWT token for a user"""
        return self.create_access_token(
            data={"sub": user_id, "email": email},
            expires_delta=timedelta(hours=24)  # 24 hours expiration
        )
