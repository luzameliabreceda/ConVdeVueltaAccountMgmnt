from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_injector import attach_injector

from .core.config import settings
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from modules.app_module import app_module
from .middleware.error_middleware import ErrorHandlingMiddleware


def create_app() -> FastAPI:
    
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    app.add_middleware(ErrorHandlingMiddleware)
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(app_module.router)
    
    from modules.di_container import global_di_container
    attach_injector(app, global_di_container.get_injector())
    
    return app


app = create_app() 