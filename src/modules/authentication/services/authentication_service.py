from abc import ABC, abstractmethod
from ..models.dto import LoginRequest, SignupRequest, LoginResponse, SignupResponse


class AuthenticationService(ABC):
    
    @abstractmethod
    async def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate user with email and password"""
        pass
    
    @abstractmethod
    async def signup(self, request: SignupRequest) -> SignupResponse:
        """Register a new user with email"""
        pass
