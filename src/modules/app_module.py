from fastapi import APIRouter


class AppModule:
    
    def __init__(self):
        self.router = APIRouter(prefix="/api")
        self._register_modules()
    
    def _register_modules(self):
        from .users.users_module import users_module
        from .health.health_module import health_module
        self.router.include_router(users_module.router)
        self.router.include_router(health_module.router)


app_module = AppModule() 