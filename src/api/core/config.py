"""
Configuration settings for the microservice.
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App settings - dynamic based on environment variables
    service_name: str = "microservice-template"
    app_name: str = "Microservice Template"  # Display name
    app_version: str = "1.0.0"
    debug: bool = False
    
    # AWS settings
    aws_region: str = "us-west-2"
    
    # Environment
    environment: str = "dev"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Update app_name based on service_name if provided
        if self.service_name != "microservice-template":
            self.app_name = self.service_name.replace("-", " ").title()
        
        # Set debug mode based on environment
        if self.environment == "dev":
            self.debug = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings() 