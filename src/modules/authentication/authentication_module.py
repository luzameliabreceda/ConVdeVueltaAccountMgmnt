from fastapi import APIRouter
from injector import singleton
from .controllers.authentication_controller import AuthenticationController


class AuthenticationModule:
    
    def __init__(self, prefix: str, tags: list[str] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.router = APIRouter(prefix=prefix, tags=self.tags)
        self._register_dependencies()
        self._register_routes()
    
    def _register_dependencies(self):
        from ..di_container import global_di_container
        from .services.authentication_service import AuthenticationService
        from .services.impl.authentication_service_impl import AuthenticationServiceImpl
        from .services.jwt_service import JWTService
        from .services.impl.jwt_service_impl import JWTServiceImpl
        
        bindings = [
            (JWTService, JWTServiceImpl, singleton),
            (AuthenticationService, AuthenticationServiceImpl, singleton),
            (AuthenticationController, AuthenticationController, singleton),
        ]
        
        global_di_container.register_module_dependencies("authentication", bindings)
    
    def _register_routes(self):
        from ..di_container import global_di_container

        auth_controller = global_di_container.get_injector().get(AuthenticationController)
        self.router.include_router(auth_controller.router)


def create_authentication_module():
    return AuthenticationModule(prefix="/v1/auth", tags=["authentication"])


authentication_module = create_authentication_module()
