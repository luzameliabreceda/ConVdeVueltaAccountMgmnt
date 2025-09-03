from abc import ABC, abstractmethod


class PasswordService(ABC):
    """Interface for password hashing and verification"""
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        pass
