from fastapi import APIRouter
from injector import singleton
from .repositories.user_repository_memory import UserRepositoryMemory


class UsersModule:
    
    def __init__(self, prefix: str, tags: list[str] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.router = APIRouter(prefix=prefix, tags=self.tags)
        self._register_dependencies()
        self._register_routes()
    
    def _register_dependencies(self):
        from ..di_container import global_di_container
        from .repositories.user_repository import UserRepository
        from .services.user_service_interface import UserServiceInterface
        from .services.user_service import UserService
        from .controllers.user_controller import UserController
        
        bindings = [
            (UserRepository, UserRepositoryMemory, singleton),
            (UserServiceInterface, UserService, singleton),
            (UserController, UserController, singleton),
        ]
        
        global_di_container.register_module_dependencies("users", bindings)
    
    def _register_routes(self):
        from ..di_container import global_di_container
        from .controllers.user_controller import UserController

        user_controller = global_di_container.get_injector().get(UserController)
        self.router.include_router(user_controller.router)


def create_users_module():
    return UsersModule(prefix="/v1/users", tags=["users"])


users_module = create_users_module() 