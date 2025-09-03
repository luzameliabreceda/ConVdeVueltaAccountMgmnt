from fastapi import APIRouter, status
from injector import inject
from ..services.authentication_service import AuthenticationService
from ..models.dto import LoginRequest, SignupRequest, LoginResponse, SignupResponse


class AuthenticationController:
    
    @inject
    def __init__(self, auth_service: AuthenticationService):
        self._auth_service = auth_service
        self.router = APIRouter()
        self._register_routes()
    
    def _register_routes(self):
        @self.router.post(
            "/login",
            response_model=LoginResponse,
            status_code=status.HTTP_200_OK,
            summary="User Login",
            description="Authenticate user with email and password"
        )
        async def login(request: LoginRequest) -> LoginResponse:
            return await self._auth_service.login(request)
        
        @self.router.post(
            "/signup",
            response_model=SignupResponse,
            status_code=status.HTTP_201_CREATED,
            summary="User Registration",
            description="Register a new user with email"
        )
        async def signup(request: SignupRequest) -> SignupResponse:
            return await self._auth_service.signup(request)
