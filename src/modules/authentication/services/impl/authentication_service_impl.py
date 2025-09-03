from injector import inject
from ...models.dto import LoginRequest, SignupRequest, LoginResponse, SignupResponse
from ..authentication_service import AuthenticationService
from ..jwt_service import JWTService
from ....users.services.user_service import UserService
from ....users.services.password_service import PasswordService
from ....users.models.dto import CreateUserRequest
from api.exceptions.http_exceptions import (
    UnauthorizedException,
    ConflictException,
    NotFoundException
)
import uuid


class AuthenticationServiceImpl(AuthenticationService):
    
    @inject
    def __init__(self, user_service: UserService, password_service: PasswordService, jwt_service: JWTService):
        self._user_service = user_service
        self._password_service = password_service
        self._jwt_service = jwt_service
    
    async def login(self, request: LoginRequest) -> LoginResponse:
        """Authenticate user with email and password"""
        # Get user by email
        user = await self._user_service.get_user_by_email(request.email)
        
        if not user:
            raise UnauthorizedException("Invalid email or password")
        
        # Check if user has a password hash
        if not user.password_hash:
            raise UnauthorizedException("User has no password set")
        
        # Verify password
        if not self._password_service.verify_password(request.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        
        # Generate JWT token
        token = self._jwt_service.create_user_token(str(user.id), user.email)
        
        return LoginResponse(
            user_id=str(user.id),
            token=token
        )
    
    async def signup(self, request: SignupRequest) -> SignupResponse:
        
        # Check if user already exists
        existing_user = await self._user_service.get_user_by_email(request.email)
        
        if existing_user:
            raise ConflictException("User with this email already exists")
        
        # Create user with minimal data
        create_user_request = CreateUserRequest(
            email=request.email,
            username=None,  # Will be auto-generated
            first_name=None,
            paternal_surname=None,
            maternal_surname=None,
            phone=None,
            date_of_birth=None,
            gender=None,
            national_id=None,
            password_hash=None,
            enabled=True
        )
        
        user = await self._user_service.create_user(create_user_request)
        
        # Generate JWT token
        token = self._jwt_service.create_user_token(str(user.id), user.email)
        
        return SignupResponse(
            user_id=str(user.id),
            token=token
        )
