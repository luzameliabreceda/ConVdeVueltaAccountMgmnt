from passlib.context import CryptContext
from injector import inject
from ..password_service import PasswordService

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordServiceImpl(PasswordService):
    """Service for password hashing and verification"""
    
    @inject
    def __init__(self):
        pass
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
