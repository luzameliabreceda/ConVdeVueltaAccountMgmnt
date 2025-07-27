from fastapi import APIRouter
from injector import singleton


class HealthModule:
    
    def __init__(self, prefix: str, tags: list[str] = None):
        self.prefix = prefix
        self.tags = tags or []
        self.router = APIRouter(prefix=prefix, tags=self.tags)
        self._register_dependencies()
        self._register_routes()
    
    def _register_dependencies(self):
        from ..di_container import global_di_container
        from .controllers.health_controller import HealthController
        
        bindings = [
            (HealthController, HealthController, singleton),
        ]
        
        global_di_container.register_module_dependencies("health", bindings)
    
    def _register_routes(self):
        from ..di_container import global_di_container
        from .controllers.health_controller import HealthController
        health_controller = global_di_container.get_injector().get(HealthController)
        self.router.include_router(health_controller.router)


def create_health_module():
    return HealthModule(prefix="/v1", tags=["health"])


health_module = create_health_module() 