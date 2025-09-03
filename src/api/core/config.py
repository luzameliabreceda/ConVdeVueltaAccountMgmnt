import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    service_name: str = "microservice-template"
    app_name: str = "Microservice Template"
    app_version: str = "1.0.0"
    debug: bool = False
    
    aws_region: str = "us-west-2"
    aws_profile: Optional[str] = None
    
    environment: str = "dev"
    
    database_type: str = "memory"
    
    # JWT Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.service_name != "microservice-template":
            self.app_name = self.service_name.replace("-", " ").title()
        
        if self.environment == "dev":
            self.debug = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 