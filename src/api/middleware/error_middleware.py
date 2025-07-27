import logging
import traceback
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..exceptions.http_exceptions import (
    BaseHTTPException,
    BadRequestException,
    NotFoundException,
    ConflictException,
    UnauthorizedException,
    ForbiddenException,
    UnprocessableEntityException,
    InternalServerErrorException
)

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            
            if response.status_code >= 400:
                return await self.convert_error_response(request, response)
            
            return response
        except Exception as exc:
            return await self.handle_exception(request, exc)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        
        if isinstance(exc, BaseHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail,
                        "path": str(request.url.path)
                    }
                }
            )
        
        elif hasattr(exc, 'status_code') and hasattr(exc, 'detail'):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail,
                        "path": str(request.url.path)
                    }
                }
            )
        
        elif isinstance(exc, (BadRequestException, NotFoundException, ConflictException, 
                             UnauthorizedException, ForbiddenException, UnprocessableEntityException)):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": {
                        "code": exc.status_code,
                        "message": exc.detail,
                        "path": str(request.url.path)
                    }
                }
            )
        
        elif isinstance(exc, ValueError):
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "code": 400,
                        "message": str(exc),
                        "path": str(request.url.path)
                    }
                }
            )
        
        else:
            return await self.handle_unexpected_exception(request, exc)
    

    
    async def handle_unexpected_exception(self, request: Request, exc: Exception) -> JSONResponse:
        
        logger.error(
            f"Unexpected exception: {type(exc).__name__}: {str(exc)}",
            extra={
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "request_path": str(request.url.path),
                "request_method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        is_development = getattr(request.app.state, 'debug', False) if hasattr(request.app, 'state') else False
        
        error_response = {
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "path": str(request.url.path)
            }
        }
        
        if is_development:
            error_response["error"]["traceback"] = traceback.format_exc()
            error_response["error"]["exception_type"] = type(exc).__name__
            error_response["error"]["exception_message"] = str(exc)
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    async def convert_error_response(self, request: Request, response: Response) -> JSONResponse:
        
        response_body = b""
        async for chunk in response.body_iterator:
            response_body += chunk
        
        try:
            import json
            error_data = json.loads(response_body.decode())
            
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "error": {
                        "code": response.status_code,
                        "message": error_data.get("detail", "Unknown error"),
                        "path": str(request.url.path)
                    }
                }
            )
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JSONResponse(
                status_code=response.status_code,
                content={
                    "error": {
                        "code": response.status_code,
                        "message": "Unknown error",
                        "path": str(request.url.path)
                    }
                }
            ) 